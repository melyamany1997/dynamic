#!/usr/bin/env python

# WS server example

import asyncio
import websockets
import json

async def on_message(websocket, path):
    message = await websocket.recv()
    print(f"message ===> {json.loads(str(message))}")
    # print(f"path ===> {path}")
    client_message = {"status":"success"}
    await websocket.send(json.dumps(client_message))

start_server = websockets.serve(on_message, 'localhost', 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()