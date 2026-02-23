#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 29 18:53:39 2026

@author: hounsousamuel
"""

import os, sys
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import threading, uvicorn
import signal, asyncio
import atexit, aiohttp
import bcrypt, time
from datetime import datetime
from router import router
from slowapi.errors import RateLimitExceeded
from config import (
    FastApiDir, 
    IP, PORT,
    FastApiDirProfile,
    HubDIR, text_dir, 
    REACT_EXIST, REACT_PATH,
    REACT_URL, BUILD_PATH, 
    BUILD_URL, INDEX_HTML
)
from limiter import LIMITER, LIMITE_STR

serveur = None

app = FastAPI(
    version="1.0",
    docs_url='/api/docs',
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    on_startup=[lambda: print("API lancée !")],
    on_shutdown=[lambda: print("API fermée !")],
    )

app.include_router(router=router, prefix="/api")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],#["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    #expose_headers=True
    )

app.mount("/api/static/upload_data", StaticFiles(directory=FastApiDir), name="static_upload_data")
app.mount("/api/static/profile_imgs", StaticFiles(directory=FastApiDirProfile), name="static_profile_img")
app.mount("/api/static/text_dir", StaticFiles(directory=text_dir), name="static_text_data")
app.mount("/api/static/HubDir", StaticFiles(directory=HubDIR), name="static_hub_data")
app.mount("/api/static/HubDir", StaticFiles(directory=HubDIR), name="static_hub_data")

if REACT_EXIST:
    app.mount(REACT_URL, StaticFiles(directory=REACT_PATH), name="static")
    app.mount(BUILD_URL, StaticFiles(directory=BUILD_PATH), name="build")
    
def start(app, host, port):
    global serveur
    conf = uvicorn.Config(app=app, workers=10, host=host, port=port, loop='uvloop', use_colors=True,)
    serveur = uvicorn.Server(config=conf)
    th = threading.Thread(target=serveur.run, daemon=True)
    return th, serveur

def signal_manager(CLOSE_TARGET, thread):
    def signal_handler(sig, frame):
        print('Signal envoyé : ', sig)
        asyncio.run(close_api(CLOSE_TARGET))
        thread.join(2)
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)  
    signal.signal(signal.SIGQUIT, signal_handler)

def __close_api():
    global serveur
    serveur.should_exit = True

async def close_api(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print('Statut : ', response.status)

def close_api_atexit(url):
    def _close():
        asyncio.run(close_api(url))
    atexit.register(_close)
    
@app.exception_handler(RateLimitExceeded)
async def _handler(request: Request, exc:RateLimitExceeded):
    return JSONResponse(
          content= {
            "status_code": 400,
            "message": "Trop de requêtes, veuillez patientez !"
            },
          status_code=429
        )


@app.get('/api/close')
def _close_api():
    global serveur
    if serveur is None:
        print('Serveur non lancé !', serveur)
        return {
            "message ": "Serveur non lancé !"
            }
    else:
        __close_api()
        print('Serveur fermé.')
        return {
            "message ": 'Serveur fermé.'
            }
    
@app.get("/api/test")
def _test():
    return {
        "message": "Test de l'api !"
        }

@app.get("/health")
def _health():
    return {
        "message": "Ok!"
        }


@app.get("/api/salt")
@LIMITER.limit(LIMITE_STR)
def _get_salt(request: Request):
    return {
        "salt": bcrypt.gensalt().decode(),
        "datetime": time.ctime()
        }


@app.get("/api/")
async def _home():
    # if REACT_EXISTS:
    #    return FileResponse(INDEX_HTML)
    # else:
    return {
        "api_docs": "/api/docs",
        "endpoints": {
            "GET /api/login": "Connection ou création de compte",
            "wWS /api/ws/...": "Communication socket",
            "GET /api/salt": "Obtenir un salt",
            "GET /api/close": "Fermeture de l'api",
            "POST /api/upload": "Upload de fichiers",
            "POST /api/disconnect": "Déconnexion utilisateur !",
            "POST /api/user_info": "Info utilisateur",
        },
        "rate_limit": f"{LIMITE_STR}"
    }

@app.get("/")
async def _home1():
    if REACT_EXIST:
        print("REACT_EXIST")
        return FileResponse(INDEX_HTML)
   
    else:
        return {
            "api_docs": "/api/docs",
            "endpoints": {
                "GET /api/login": "Connection ou création de compte",
                "wWS /api/ws/...": "Communication socket",
                "GET /api/salt": "Obtenir un salt",
                "GET /api/close": "Fermeture de l'api",
                "POST /api/upload": "Upload de fichiers",
                "POST /api/disconnect": "Déconnexion utilisateur !",
                "POST /api/user_info": "Info utilisateur",
            },
            "rate_limit": f"{LIMITE_STR}"
        }
    

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    """Capture toutes les routes pour React Router"""
    # excluded_prefixes = ["docs", "redoc", "openapi.json"]
    
    print(full_path)
    
    if REACT_EXIST:
        return FileResponse(INDEX_HTML)
    
    raise HTTPException(status_code=404, detail="Route non trouvée")
  
    # raise HTTPException(status_code=404, detail="Route non trouvée")
if __name__ == "__main__":
    th, serveur = start(app, IP, PORT)
    th.start()
    time.sleep(2)
    URL = f"http://{IP}:{PORT}/api/"
    URL1 = f"http://{IP}:{PORT}/"
    async def test():
        async with aiohttp.ClientSession() as session:
            async with session.get(URL+"test") as response:
                return {
                    "status_code": response.status,
                    "text": await response.text(),
                    "json": await response.json(),
                    "headers": dict(response.headers)
                    }
    
    async def test1():
        async with aiohttp.ClientSession() as session:
            async with session.get(URL1) as response:
                return {
                    "status_code": response.status,
                    "text": await response.text(),
                    "json": await response.json(),
                    "headers": dict(response.headers)
                    }
            
    async def test_login():
        login_url = URL+"login"
        data = {
            "username": "samuelhounsou",
            "password":"Kimetsu no yaiba",
            "age": 17,
            "email": "samuel@gmail.com",
            "salt": "$2b$12$2N7upivC0cR4rzOd6adgiu"
            }
        async with aiohttp.ClientSession() as session:
            async with session.post(login_url, json=data) as response:
                return await response.json()
    # print(asyncio.run(test()))
    # print(asyncio.run(test1()))
    print(asyncio.run(test_login()))
    time.sleep(4)
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            asyncio.run(close_api(URL+"close"))                
            break
        
    # asyncio.run(close_api(URL+"close"))