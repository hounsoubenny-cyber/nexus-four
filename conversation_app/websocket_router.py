#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 30 15:36:41 2026

@author: hounsousamuel
"""

import os, sys
from fastapi import APIRouter, status, HTTPException, Query, File, UploadFile, Form, WebSocket, WebSocketDisconnect
from websocket_class import WebsocketManager

ws_router = APIRouter()
