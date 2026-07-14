from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import jwt
from jose.exceptions import JWTError

from app.config import SECRET_KEY, JWT_ALGORITHM
from app.database import SessionLocal
from app.models.ChatRequest import ChatRequest
from app.models.ChatMessage import ChatMessage
from app.websocket.manager import manager

router = APIRouter()


@router.websocket("/ws/chat/{chat_request_id}")
async def websocket_chat(
    websocket: WebSocket,
    chat_request_id: int,
):
    print("\n================ NEW WEBSOCKET CONNECTION ================")

    db = SessionLocal()

    token = websocket.cookies.get("access_token")

    print("Token Found:", token is not None)

    if not token:
        print("No access token found.")
        await websocket.close(code=1008)
        db.close()
        return

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )

        user_id = payload["user_id"]
        role = payload["role"]

        print(f"Decoded JWT")
        print(f"Role      : {role}")
        print(f"User ID   : {user_id}")

    except JWTError as e:
        print("JWT ERROR:", e)
        await websocket.close(code=1008)
        db.close()
        return

    print(f"Looking for ChatRequest #{chat_request_id}")

    chat_request = (
        db.query(ChatRequest)
        .filter(
            ChatRequest.id == chat_request_id,
            ChatRequest.status == "approved",
        )
        .first()
    )

    if not chat_request:
        print("Chat request NOT FOUND")
        await websocket.close(code=1008)
        db.close()
        return

    print("Chat request found")
    print("--------------------------------")
    print("ChatRequest ID :", chat_request.id)
    print("User ID        :", chat_request.user_id)
    print("Admin ID       :", chat_request.admin_id)
    print("Status         :", chat_request.status)
    print("--------------------------------")

    print("Starting permission check...")

    if role == "user":
        print("User validation")

        print(f"Expected user_id={chat_request.user_id}, Current user_id={user_id}")

        if chat_request.user_id != user_id:
            print("USER VALIDATION FAILED")
            await websocket.close(code=1008)
            db.close()
            return

        print("USER VALIDATION PASSED")

    elif role == "admin":
        print("Admin validation")

        print(f"Expected admin_id={chat_request.admin_id}, Current user_id={user_id}")

        if chat_request.admin_id != user_id:
            print("ADMIN VALIDATION FAILED")
            await websocket.close(code=1008)
            db.close()
            return

        print("ADMIN VALIDATION PASSED")

    else:
        print("Unknown role:", role)

        await websocket.close(code=1008)
        db.close()
        return

    print("Calling manager.connect()")

    await manager.connect(
        chat_request_id,
        websocket,
    )

    print(f"Successfully connected to room {chat_request_id}")

    try:
        while True:
            data = await websocket.receive_text()

            print("------------------------------------------------")
            print(f"Message received in room {chat_request_id}")
            print(f"Sender ID : {user_id}")
            print(f"Role      : {role}")
            print(f"Message   : {data}")
            print("------------------------------------------------")

            if role == "admin":
                receiver_id = chat_request.user_id
            else:
                receiver_id = chat_request.admin_id

            print(f"Receiver ID = {receiver_id}")

            chat_message = ChatMessage(
                chat_request_id=chat_request.id,
                sender_id=user_id,
                receiver_id=receiver_id,
                message=data,
            )

            db.add(chat_message)
            db.commit()
            db.refresh(chat_message)

            print("Saved message successfully")
            print("Message ID :", chat_message.id)

            message_data = {
                "id": chat_message.id,
                "sender_id": chat_message.sender_id,
                "receiver_id": chat_message.receiver_id,
                "sender_role": role,
                "message": chat_message.message,
                "created_at": chat_message.created_at.isoformat(),
            }

            print("Broadcasting message...")

            await manager.broadcast(
                chat_request_id,
                message_data,
            )

            print("Broadcast complete")

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for room {chat_request_id}")

    except Exception as e:
        print("UNEXPECTED ERROR")
        print(type(e))
        print(e)

    finally:
        print("Disconnecting socket...")

        manager.disconnect(
            chat_request_id,
            websocket,
        )

        db.close()

        print("Database session closed")
        print("================ END CONNECTION ================\n")
