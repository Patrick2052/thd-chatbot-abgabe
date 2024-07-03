
import os
import asyncio
import websockets
import uuid
from typing import Any, List, Dict
# def handle_message(msg):
from chatbot import Chatbot
from dotenv import load

load("./env")

HOST = os.environ.get("HOST")
PORT = os.environ.get("PORT")


class Session():
    def __init__(self, websocket):
        self.chat_id = uuid.uuid4()
        self.chatbot = Chatbot(websocket=websocket)


sessions: Dict[Any, Session] = {}


async def handler(websocket):
    if websocket not in sessions:
        print(f"new session {websocket}")
        sess = Session(websocket=websocket)
        await sess.chatbot.initialize()
        sessions[websocket] = sess

    session = sessions[websocket]

    try:

        async for message in websocket:
            await session.chatbot.handle_message(message)

            # await websocket.send(message)

    except websockets.exceptions.ConnectionClosedError:
        # Handle client error
        # del sessions[websocket]
        print("Client error occurred:", sessions[websocket])

    finally:
        # Remove the client from the connected clients set when they disconnect
        print("disconnect: ", sessions[websocket])
        del sessions[websocket]


start_server = websockets.serve(handler, HOST, PORT)
print(f"running on {HOST}:{PORT}")

# Run the server indefinitely
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
