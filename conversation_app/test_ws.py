#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  8 07:06:49 2026

@author: hounsousamuel
"""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from nest_asyncio import apply
apply()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            text = await websocket.receive_text()
            print("Recu : ", text)
            await websocket.send_text(f"Echo: {text}")
    except Exception as e:
        print(f"WebSocket error: {e}")


from uvicorn import Config, Server

try:
    serv = Server(Config(port=9000, host="0.0.0.0", app=app))
    serv.run()

    import time

    time.sleep(60)
    serv.should_exit = True
except KeyboardInterrupt:
    serv.should_exit = True