from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connection = {}