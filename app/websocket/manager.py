from typing import Dict, List

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # Stores all active websocket connections
        # {
        #     chat_request_id: [
        #         websocket1,
        #         websocket2,
        #         ...
        #     ]
        # }
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(
        self,
        chat_request_id: int,
        websocket: WebSocket,
    ):
        await websocket.accept()

        if chat_request_id not in self.active_connections:
            self.active_connections[chat_request_id] = []

        self.active_connections[chat_request_id].append(websocket)

        print(
            f"CONNECTED -> room={chat_request_id} total={len(self.active_connections[chat_request_id])}"
        )

    def disconnect(
        self,
        chat_request_id: int,
        websocket: WebSocket,
    ):
        if chat_request_id not in self.active_connections:
            return

        connections = self.active_connections[chat_request_id]

        if websocket in connections:
            connections.remove(websocket)

        # Remove room if empty
        if not connections:
            del self.active_connections[chat_request_id]

        print(f"Client disconnected from chat room {chat_request_id}")

    async def broadcast(
        self,
        chat_request_id: int,
        message: dict,
    ):
        connections = self.active_connections.get(
            chat_request_id,
            [],
        )

        disconnected = []

        for websocket in connections:
            try:
                await websocket.send_json(message)

            except Exception:
                # Save broken sockets for cleanup
                disconnected.append(websocket)

        # Remove broken connections
        for websocket in disconnected:
            self.disconnect(
                chat_request_id,
                websocket,
            )
        print(f"BROADCAST room={chat_request_id} users={len(connections)}")


manager = ConnectionManager()
