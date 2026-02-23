#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 30 23:39:40 2026

@author: hounsousamuel
"""

import os
import sys
import asyncio
import uuid
import json
import time
import aiofiles
from random import choice
from fastapi import (
    status, HTTPException, Depends,
    APIRouter, WebSocket, WebSocketDisconnect,
    Request, Query, Form, File, UploadFile,
    WebSocketException
    )
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from auth_jwt import create_token, verify_token
from websocket_class import WebsocketManager
from utils_cnv import checksalt, extract_text, rm, _get_file_name_mode
from cryptography.fernet import InvalidSignature, InvalidToken
from chiffrement import FernetManager, hashpw, checkpw
from limiter import LIMITER, LIMITE_STR, LIMITE_MSG_STR
from config import FastApiDir, FastApiDirProfile, IMG_EXTENSIONS, text_dir, HubDIR
from chat_nexus.chat import ChatNexus, handle_chat
from hub_manager.hub_manager import HubManager

WSInstance = None
Nexus = None
Hub = None
NEXUS_NAME = "Nexus"

def get_ws_instance() -> WebsocketManager:
    global WSInstance
    if WSInstance:
        return WSInstance
    else:
        WSInstance = WebsocketManager()
        return WSInstance

def get_nexus():
    global Nexus
    if Nexus:
        return Nexus
    Nexus = ChatNexus()
    return Nexus

def get_hub_manager():
    global Hub
    if Hub:
        return Hub
    else:
        Hub = HubManager()
        return Hub
    
class UserModel(BaseModel):
    username: str
    age: int 
    email: str
    salt: bytes | str
    password: str

class ChatMessage(BaseModel):
    question:str
    token:str
    salt:bytes|str
    username:str
    rag:bool|None=True
    
router = APIRouter()

def verify_email(email:str):
    return "@" in email

async def verify_user(token:str, username:str, wsinstance:WebsocketManager, salt:str=None):
    # Ici, j'joute salt car certaines routes doivent envoyer salt, mais d'autre nécessitent que l'user soit connecté 
    #d'ou wsinstance.active_connection, d'autres comme la route de chat ws
    try:
        if wsinstance._verify_user("login", username=username):
            if salt:
                key = salt
            else:
                if wsinstance._verify_user("connected", username=username):
                    if username in wsinstance.active_connections:
                        key = wsinstance.active_connections[username]["salt"]
                    else:
                        if username in wsinstance.temp_salt:
                            key = wsinstance.temp_salt[username]
                        else:
                            raise HTTPException(
                                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail="User non connecté, salt absent !"
                                )
    
            sub = verify_token(token=token, key=key)
            if sub == username:
                return True
        return False
    
    except Exception as e:
        print("Erreur dans la vérification d'identité : ", str(e))
        return False

async def handle_one_file(file:UploadFile = File(...)):
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    path = os.path.join(FastApiDir, filename)
    filename1 = filename.removesuffix(ext) + "_" + str(uuid.uuid4()) + ext
    path = os.path.join(FastApiDir, filename1)
    async with aiofiles.open(path, "wb") as f:
        await f.write(await file.read())
    
    return filename1, filename

async def handle_nexus_file(file:UploadFile = File(...)):
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    filename1 = filename.removesuffix(ext) + "_" + str(uuid.uuid4()) + ext
    path = os.path.join(text_dir, filename1)
    async with aiofiles.open(path, "wb") as f:
        await f.write(await file.read())
    
    return path


async def handle_imgs(file:UploadFile = File(...), username:str=""):
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    listdir = os.listdir(FastApiDirProfile)
    can = not any("_" + username + "." in a for a in listdir)
    filename = filename.removesuffix(ext) + "_" + str(username) + ext
    if can:
        path = os.path.join(FastApiDirProfile, filename)
        async with aiofiles.open(path, "wb") as f:
            await f.write(await file.read())
    
    return filename

async def handle_hub_img(file:UploadFile = File(...), username:str=""):
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    p = os.path.join(HubDIR, "imgs_profile")
    os.makedirs(p, exist_ok=True)
    listdir = os.listdir(p)
    can = not any("_" + username + "." in a for a in listdir)
    filename = filename.removesuffix(ext) + "_" + str(username) + ext
    if can:
        path = os.path.join(p, filename)
        async with aiofiles.open(path, "wb") as f:
            await f.write(await file.read())
    
    return filename
        
async def handle_marketplace_img(file:UploadFile = File(...)):
    filename = file.filename
    p = os.path.join(HubDIR, "products_img")
    os.makedirs(p, exist_ok=True)
    ext = os.path.splitext(filename)[1].lower()
    filename1 = filename.removesuffix(ext) + "_" + str(uuid.uuid4()) + ext
    path = os.path.join(p, filename1)
    async with aiofiles.open(path, "wb") as f:
        await f.write(await file.read())

    return filename, filename1

async def stream_generator(data:dict, nexus_model:ChatMessage):
    stream = await handle_chat(data, nexus_model=nexus_model, stream=True, terminal=False)
    for chunk in stream:
        text = chunk["choices"][0]["text"]
        data1 = json.dumps({"message": text, "done":False}, indent=2, ensure_ascii=False)
        nexus_model.his += chunk["choices"][0]["text"]
        yield f"""data: {data1}\n\n"""
        await asyncio.sleep(0.05)
        
    await nexus_model.update_cache(
        username=data["from"], 
        who="nexus", 
        prompt_or_response=nexus_model.his, 
        terminal=False
    )
    data1 = json.dumps({"message": "", "done":True}, indent=2, ensure_ascii=False)
    yield f"""data: {data1}\n\n"""
    
#==============================================================================================
# Routes générales
#==============================================================================================

@router.post("/login")
@LIMITER.limit(LIMITE_STR)
async def _login(request:Request, user_data:UserModel):
    try:
        age = int(user_data.age)
        salt = str(user_data.salt).encode()
        username = user_data.username
        password = user_data.password[:72]
        email = user_data.email
        if age and age > 0 and username and checksalt(salt) and verify_email(email):
            wsinstance = get_ws_instance()
            token = create_token(data={"username": username}, key=salt)
            user_info = await wsinstance.get_user_info(username)
            if wsinstance._verify_user("login", username) and user_info:
                if checkpw(password=password, hashed=user_info["password_h"]):
                    try:
                        fernet = FernetManager(password=password, salt=salt)
                        key = choice(["salt", "username", "age", "email", "password_e"])
                        fernet.decrypt(user_info[key])
                    except (InvalidSignature, InvalidToken):
                        raise HTTPException(
                            status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail="Salt incorrect !"
                            )
                    
                    success = await wsinstance._set_salt_temp(salt, username)
                    return {  
                        "success": success,
                        "salt": salt,
                        "token": token,
                        "state": "old",
                        "username": username
                        }
                else:
                    raise HTTPException(
                        status_code=status.HTTP_406_NOT_ACCEPTABLE,
                        detail="mot de passe incorrect !"
                        )
            else:
                if wsinstance.validate_username(username):
                    fernet = FernetManager(password=password, salt=salt)
                    data = {
                        "username": fernet.encrypt(username),
                        "age": fernet.encrypt(age),
                        "email": fernet.encrypt(email),
                        "salt": fernet.encrypt(salt)
                        }
                    data["password_e"] = fernet.encrypt(password)
                    data["password_h"] = hashpw(password)
                    s1 = await wsinstance._set_salt_temp(salt, username)
                    s2 = await wsinstance.put_user_in_cache(username, data_user=data)
                    success = s1 and s2
                    return {  
                        "success": success,
                        "salt": salt,
                        "token": token,
                        "state": "new",
                        "username": username
                        }
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail="username non authorisé"
                    )
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Info user invalide !"
            )
    except Exception as e:
        print("Erreur de login d'un user : ", str(e))
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=f"Erreur de login d'un user : {str(e)}"
            )

#==============================================================================================
# Routes websocket
#==============================================================================================

@router.post("/disconnect")   
@LIMITER.limit(LIMITE_STR)   
async def _disconnect(request:Request, username:str=Query(...), token:str=Query(...)):
    wsinstance = get_ws_instance()
    try:
        if await verify_user(token, username, wsinstance):
            await wsinstance.disconnect(username)
            return JSONResponse({"success": True})  
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user non authorisé"
                )
    except Exception as e:
        print("Erreur disconnect ", str(e))
        raise

@router.post("/upload_file")
@LIMITER.limit(LIMITE_STR)
async def _upload(
        request:Request, 
        # username:str=Form(...), 
        # token:str=Form(...), 
        # salt:str=Form(...),
        files:list[UploadFile]=File(...),
        json_data:str=Form(...),
    ):
    
    try:
        # if await verify_user(token, username, wsinstance):
        print("Upload file : ", json_data)
        json_data = json.loads(json_data)
        print("Upload file loaded : ", json_data)
        if all(c in json_data for c in ("from", "to")):
            tasks = [
                asyncio.create_task(handle_one_file(file=file))
                for file in files
                ]
            r = list(await asyncio.gather(*tasks))
            print("rr : ", r)
            str_ = ""
            for i, p in enumerate(r):    
                str_ += p[0] + "#__#" + p[1] 
                if (i != len(r) -1):
                    str_ += "####_####"
            
            print("str_", str_)
            wsinstance = get_ws_instance()
            await wsinstance.send_message(
                who=json_data["from"],
                to=json_data["to"],
                msg=str_,
                _type="file_send",
                )
            return JSONResponse({  
                "success": all(not isinstance(a, Exception) for a in r)
                })
        
        return JSONResponse({  
            "success": False,
            })
    except Exception as e:
        raise HTTPException(
            detail="Struture de donnée invalide !",
            status_code=status.HTTP_406_NOT_ACCEPTABLE
            )
        print("Erreur upload_file : ", str(e))

@router.post("/set_profile_img")
@LIMITER.limit(LIMITE_STR)
async def _set_profile_img(
        request:Request, 
        username:str=Form(...), 
        token:str=Form(...), 
        salt:str=Form(...),
        file:UploadFile=File(...),
    ):
    
    try:
        wsinstance = get_ws_instance()
        can = await verify_user(token, username, wsinstance, salt=salt)
        ext = os.path.splitext(file.filename)[-1]
        img_valide = ext in IMG_EXTENSIONS
        if can and img_valide:
            filename = await handle_imgs(file, username=username)
            success = await wsinstance.set_profile_img(filename, username)
            return JSONResponse({  
                "success": success,
                "path" : filename
                })
        if not can:
            reason = "username non authorisé !"
        if not img_valide:
            reason = f"Fichier image requis , pas un fichier {ext} !"
        elif not (can or img_valide):
            reason = "username non authorisé et image requis, pas un fichier {ext} !"
        else:
            reason = ""
            
        return JSONResponse({  
            "success": False,
            "reaseon": reason
            })
    except Exception as e:
        raise HTTPException(
            detail="Erreur fatale !",
            status_code=status.HTTP_406_NOT_ACCEPTABLE
            )
        print("Erreur _set_profile_img : ", str(e))

@router.post("/get_profile_img")
@LIMITER.limit(LIMITE_STR)
async def _get_profile_img(
        request:Request, 
        username:str=Form(...), 
        token:str=Form(...), 
        salt:str=Form(...),
    ):
    
    try:
        wsinstance = get_ws_instance()
        can = await verify_user(token, username, wsinstance, salt=salt)
        if can:
            filename = await wsinstance.get_profile_img(username)
            return JSONResponse({  
                "success": True if filename else False,
                "path" : filename
                })
        if not can:
            reason = "username non authorisé !"
        else:
            reason = ""
            
        return JSONResponse({  
            "success": False,
            "reaseon": reason
            })
    except Exception as e:
        raise HTTPException(
            detail="Erreur fatale !",
            status_code=status.HTTP_406_NOT_ACCEPTABLE
            )
        print("Erreur _get_profile_img : ", str(e))
        
@router.post("/user_message")
#@LIMITER.limit(LIMITE_STR)
async def _get_messages(request:Request, username:str=Form(...), with_:str=Form(...), token:str=Form(...), salt:str=Form(...)):
    wsinstance = get_ws_instance()
    try:
        if await verify_user(token, username, wsinstance, salt):
            msgs = await wsinstance.get_messages(username, with_)
            return JSONResponse({"messages": msgs})  
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user non authorisé"
                )
    except Exception as e:
        print("Erreur user_message ", str(e))
        raise

@router.post("/get_friends")
#@LIMITER.limit(LIMITE_STR)
async def _get_firends(request:Request, username:str=Form(...), token:str=Form(...), salt:str=Form(...)):
    wsinstance = get_ws_instance()
    try:
        if await verify_user(token, username, wsinstance, salt):
            friends = await wsinstance.get_friends(username)
            return JSONResponse({"friends": friends})  
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user non authorisé"
                )
    except Exception as e:
        print("Erreur get_friends ", str(e))
        raise

@router.post("/user_exist")
# @LIMITER.limit(LIMITE_STR)
async def _user_exist(request:Request, username:str=Form(...), who:str=Form(...), token:str=Form(...), salt:str=Form(...)):
    wsinstance = get_ws_instance()
    try:
        if await verify_user(token, username, wsinstance, salt):
            return JSONResponse({  
                "login":  wsinstance._verify_user("login", who),
                "connected":  wsinstance._verify_user("connected", who)
                })
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user non authorisé"
                )
    except Exception as e:
        print("Erreur get_friends ", str(e))
        raise

@router.post("/add_friend")
@LIMITER.limit(LIMITE_STR)
async def _add_friend(request:Request, username:str=Form(...), with_:str=Form(...), token:str=Form(...), salt:str=Form(...)):
    wsinstance = get_ws_instance()
    try:
        if await verify_user(token, username, wsinstance, salt):
            s = await wsinstance.add_friend(username, with_)
            return JSONResponse({"success": s})  
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user non authorisé"
                )
    except Exception as e:
        print("Erreur get_friends ", str(e))
        raise

#==============================================================================================
# Routes chat Nexus Brain et Care
#==============================================================================================

@router.post("/chat/get_history")
async def _get_chat_history(request:Request, username:str=Form(...), token:str=Form(...), salt:str=Form(...), care:bool=Form(False)):
    try:
        print(f"🔍 REQUÊTE REÇUE POUR  GET_HSITORY  {username}")
        # print(f"  - Token: {token[:20]}...")
        # print(f"  - Salt: {salt[:10]}...")
        # print(f"  - Headers: {dict(request.headers)}")
        nexus_model = get_nexus()
        # wsinstance = get_ws_instance()
        # if await verify_user(token, username, wsinstance, salt):
        if True:
            msgs = await nexus_model.get_history(username=username, terminal=False, care=care)
            # print(msgs)
            return {  
               "messages":  msgs
                }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user non authorisé"
                )
    except Exception as e:
        print("Erreur _get_chat_history ", str(e))
        raise

@router.post("/chat/get_history_conv_k")
async def _get_chat_history_conv_k(request:Request, username:str=Form(...), token:str=Form(...), salt:str=Form(...), conv_k:str=Form(...), care:bool=Form(False)):
    try:
        print(f"🔍 REQUÊTE REÇUE POUR GET_HSITORY_conv_k {username}")
        # print(f"  - Token: {token[:20]}...")
        # print(f"  - Salt: {salt[:10]}...")
        # print(f"  - Headers: {dict(request.headers)}")
        nexus_model = get_nexus()
        # wsinstance = get_ws_instance()
        # if await verify_user(token, username, wsinstance, salt):
        if True:
            print("Conv k ", conv_k, care)
            msgs = await nexus_model.get_history_conv(username=username, conv_k=conv_k, terminal=False, care=care)
            # print(msgs)
            return JSONResponse({  
               "messages":  msgs
                })
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user non authorisé"
                )
    except Exception as e:
        print("Erreur _get_chat_history ", str(e))
        raise
        
@router.post("/chat/stream")  # Pas utiliser, remplacer pas WebSocket
async def stream(request:Request, message:ChatMessage):
    username = message.username
    salt = message.salt
    token = message.token
    nexus_model = get_nexus()
    wsinstance = get_ws_instance()
    try:
        if await verify_user(token, username, wsinstance, salt):
            data = {"from": username, "rag": message.rag, "question": message.question}
            return StreamingResponse(
                stream_generator(data, nexus_model),
                media_type="text/event-stream"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user non authorisé"
                )
    except Exception as e:
        print("Erreur stream ", str(e))
        raise

@router.post("/extract_text")
async def _extract_text(
        request:Request, 
        files:list[UploadFile]=File(...),
    ):
    
    try:
        tasks = [
            asyncio.create_task(handle_nexus_file(file=file))
            for file in files
            ]
        
        r = list(await asyncio.gather(*tasks))
        
        tasks1 = [
            asyncio.create_task(extract_text(filename))
            for filename in r if not isinstance(filename, Exception)
            ]
        r1 = list(await asyncio.gather(*tasks1))
        await asyncio.gather(*[
            asyncio.to_thread(rm, filename)
            for filename in r if not isinstance(filename, Exception)
            ])
        return JSONResponse({  
            "success": all(not isinstance(a, Exception) for a in r) and all(isinstance(p, str) for p in r1),
            "text": [txt for txt in r1 if isinstance(txt, str)]
            })
        
        return JSONResponse({  
            "success": False,
            })
    except Exception as e:
        raise HTTPException(
            detail="Struture de donnée invalide !",
            status_code=status.HTTP_406_NOT_ACCEPTABLE
            )
        print("Erreur extract_text : ", str(e))
        
@router.websocket("/ws_nexus")
async def _websocket_nexus(websocket:WebSocket, username:str=Query(...), token:str=Query(...), salt:str=Query(...), care:bool=Query(False)):
    print(f"Fonction _websocket_nexus appelée pour {username}")
    print(f"Token: {token[:20]}...")
    
    # wsinstance = get_ws_instance()
    nexus_model = get_nexus()
    try:
        if not await nexus_model.connect(websocket, username, salt=salt, care=care):
            print("Connect() a retourné False")
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Erreur, username non login !"
                )
        else:
            try:
                while True:
                    # if await verify_user(token, username, wsinstance):
                    if True:
                        data = await websocket.receive_json()
                        print(data)
                        if all(c in data for c in ("rag", "from", "question", "name", "conv_k")):
                            print("OK")
                            await nexus_model.send_message(data)
                        
            except WebSocketDisconnect:
                await nexus_model.disconnect(username, care=care)
                print("Deconnexion de l'user : ", username)
                
            except Exception as e:
                print("Erreur dans la route websocket : ", str(e))
            
            finally:
                if username:
                    await nexus_model.disconnect(username, care=care)
                    
    except Exception as e:
        print("Erreur dans ws/chat/nexus : ", str(e))
        raise            

@router.websocket("/ws") # /{username}, toujour route websocket pour chat entre user
async def _websocket(websocket:WebSocket, username:str=Query(...), token:str=Query(...)):

    print(f"Fonction _websocket appelée pour {username}")
    print(f"Token: {token[:20]}...")
    
    wsinstance = get_ws_instance()
    try:
        if not await wsinstance.connect(websocket, username):
            print("Connect() a retourné False")
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Erreur, username non login !"
                )
            
        else:
            try:
                while True:
                    if await verify_user(token, username, wsinstance):
                        data = await websocket.receive_json()   
                        print("Reçu : ", json.dumps(data, indent=2, ensure_ascii=False))
                        if all(c in data for c in ("from", "to", "message", "type")):
                            if data["from"] == username:
                                _type = data["type"]
                                if _type == "for_user" or _type == "file_send":
                                    await wsinstance.send_message(
                                        who=data["from"],
                                        to=data["to"],
                                        msg=data["message"]
                                        )
                                
                                elif _type == "for_group":
                                    pass
                                
                                elif _type == "for_all":
                                    await wsinstance.send_all(msg=data["message"], who=data["who"])
                        else:
                            s_data = {
                                "from": "serveur",
                                "to": data["from"],
                                "message": "Structure de données invalide, certaines clé non retrouvé !",
                                "type": "mgs_error"
                                }
                            
                            await wsinstance.send_message(
                                who=s_data["from"],
                                to=s_data["to"],
                                msg=s_data["message"],
                                _type=s_data["type"]
                                )
                            # await websocket.send_json(s_data)
                            raise WebSocketException(
                                code=status.WS_1008_POLICY_VIOLATION,
                                reason="Structure de données invalide !"
                                )
                    else:
                        s_data = {
                            "from": "serveur",
                            "to": username,
                            "message": "username non authorisé !",
                            "type": "mgs_error"
                            }
                        
                        await wsinstance.send_message(
                            who=s_data["from"],
                            to=s_data["to"],
                            msg=s_data["message"],
                            _type=s_data["type"]
                            )
                        # await websocket.send_json(s_data)
                        raise WebSocketException(
                            code=status.WS_1008_POLICY_VIOLATION,
                            reason="username non authorisé !"
                            )
                        
            except WebSocketDisconnect:
                await wsinstance.disconnect(username, total=False)
                print("Deconnexion de l'user : ", username)
                
            except Exception as e:
                print("Erreur dans la route websocket : ", str(e))
            
            finally:
                if username:
                    await wsinstance.disconnect(username, total=False)
                    
    except Exception as e:
        print("Erreur dans ws : ", str(e))
        raise
        
class InfoUser(BaseModel):
    username:str
    token:str
    password: str
    salt: str = None
    
@router.post("/user_info")
@LIMITER.limit(LIMITE_STR)
async def _info_user(request:Request, info_user:InfoUser):
    try:
        wsinstance = get_ws_instance()
        token = info_user.token
        username = info_user.username
        password = info_user.password
        salt = info_user.salt
        salt = str(salt).encode() if salt else None
        if salt is None:
            if username in wsinstance.active_connections:
                key = wsinstance.active_connections[username]["salt"]
            else:
                key = wsinstance.temp_salt[username]
                
            salt = key
            
            
        if await verify_user(token, username, wsinstance):
            info = await wsinstance.get_user_info(username=username)
            if wsinstance._verify_user("login", username) and info:
                if checkpw(password=password, hashed=info["password_h"]):
            
                    fernet = FernetManager(password=password, salt=salt)
                    decoded = {
                        "username": fernet.decrypt(info["username"]),
                        "email": fernet.decrypt(info["email"]),
                        "password": fernet.decrypt(info["password_e"]),
                        "age": fernet.decrypt(info["age"]),
                        "salt": fernet.decrypt(info["salt"]),
                        }
                    return JSONResponse(decoded)  
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="mot de passe invalide"
                        )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user non enrégistré ou hors ligne !"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user non authorisé"
                )
    except Exception as e:
        print("Erreur dans la route d'obtention d'info : ", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user non authorisé ou salt invalide !"
            )


#==============================================================================================
# Routes Hub
#==============================================================================================

class Skills(BaseModel):
    skills:list
    descr: str = ""
    portefolio:dict[str, dict]     # Ex: {"projet_de_antispam": {"nom": "pan", "description": "", "meta": {git_lien:"", "gmail":"", "drive":""}}}
    salt:str
    username:str
    token:str
    erase:bool=False
    
class MetaData(BaseModel):
    git_lien:str = ""
    gmail:str = ""
    lnkd_lien:str = ""
    salt:str
    username:str
    token:str

class Product(BaseModel):
    name_user:str  # vrai nom si dispo
    user_descr:str = ""
    categorie:str
    name_product:str
    price:int
    device:str
    product_descr:str = ""
    path_image:str = ""
    mail:str=""
    
@router.post("/hub/set_metadata")
async def _set_hub_metadata(request:Request, meta:MetaData):
    try:
        token, salt, username = meta.token, meta.salt, meta.username
        wsinstance = get_ws_instance()
        if await verify_user(token, username, wsinstance, salt=salt):
            hub = get_hub_manager()
            success = await hub.set_metadata(meta.model_dump(), username=username)
            return {
                "success": success
                }
        
    except Exception as e:
        print("Erreur dans set_metadata : ", str(e))
        raise HTTPException(
            detail="Erreur dans set_metadata , user non authorisé ou salt invalide ou données invalides " + str(e),
            status_code=status.HTTP_406_NOT_ACCEPTABLE
            )
        
@router.post("/hub/set_img_profile")
@LIMITER.limit(LIMITE_STR)
async def _set_profile_hub_img(
        request:Request, 
        username:str=Form(...), 
        token:str=Form(...), 
        salt:str=Form(...),
        file:UploadFile=File(...),
        slogan:str=Form("")
    ):
    
    try:
        wsinstance = get_ws_instance()
        can = await verify_user(token, username, wsinstance, salt=salt)
        ext = os.path.splitext(file.filename)[-1]
        img_valide = ext in IMG_EXTENSIONS
        hub = get_hub_manager()
        if can and img_valide:
            filename = await handle_hub_img(file, username=username)
            success = await hub.set_hub_img_profile(username=username, path=filename, mot=slogan)
            return JSONResponse({  
                "success": success,
                "path" : filename
                })
        if not can:
            reason = "username non authorisé !"
        if not img_valide:
            reason = f"Fichier image requis , pas un fichier {ext} !"
        elif not (can or img_valide):
            reason = "username non authorisé et image requis, pas un fichier {ext} !"
        else:
            reason = ""
            
        return JSONResponse({  
            "success": False,
            "reaseon": reason
            })
    except Exception as e:
        print("Erreur _set_profile_hub_img : ", str(e))
        raise HTTPException(
            detail="Erreur fatale !",
            status_code=status.HTTP_406_NOT_ACCEPTABLE
            )
        

@router.post("/hub/get_profile_img")
@LIMITER.limit(LIMITE_STR)
async def _get_profile_hub_img(
        request:Request, 
        username:str=Form(...), 
        token:str=Form(...), 
        salt:str=Form(...),
    ):
    
    try:
        wsinstance = get_ws_instance()
        hub = get_hub_manager()
        can = await verify_user(token, username, wsinstance, salt=salt)
        if can:
            data = await hub.get_hub_img_profile(username)
            return JSONResponse({  
                "success": True if data else False,
                "path" : data[0],
                "slogan": data[1],
                })
        if not can:
            reason = "username non authorisé !"
        else:
            reason = ""
            
        return JSONResponse({  
            "success": False,
            "reaseon": reason
            })
    except Exception as e:
        print("Erreur _get_profile_img : ", str(e))
        raise HTTPException(
            detail="Erreur fatale !",
            status_code=status.HTTP_406_NOT_ACCEPTABLE
            )
      
    
@router.post("/hub/add_skills")
async def _add_skills(request:Request, skills:Skills):
    try:
        token, salt, username = skills.token, skills.salt, skills.username
        wsinstance = get_ws_instance()
        if await verify_user(token, username, wsinstance, salt=salt):
            hub = get_hub_manager()
            erase = skills.erase
            success = await hub.add_skills(skills.model_dump(), username, erase=erase)
            return {
                "success": success,
                }
        return {
            "success": False,
            }
    except Exception as e:
        print("Erreur _add_skills : ", str(e))
        raise HTTPException(
            detail="Erreur fatale !",
            status_code=status.HTTP_406_NOT_ACCEPTABLE
            )

@router.post("/hub/get_skills")
async def _get_skills(
    request:Request, 
    username:str=Form(...), 
    token:str=Form(...), 
    salt:str=Form(...),
):
    try:
        wsinstance = get_ws_instance()
        if await verify_user(token, username, wsinstance, salt=salt):
            hub = get_hub_manager()
            skills = await hub.get_skills(username)
            return {
                "skills": skills,
                }
        return {
            "skills": {},
            }
    except Exception as e:
        print("Erreur _add_skills : ", str(e))
        raise HTTPException(
            detail="Erreur fatale !",
            status_code=status.HTTP_406_NOT_ACCEPTABLE
            )
        
        
# ============================================
# MARKETPLACE ROUTES
# ============================================

@router.post("/mp/add_product")
async def _add_product(
    request: Request,
    username: str = Form(...),
    salt: str = Form(...),
    token: str = Form(...),
    file: UploadFile = File(None),
    name_user: str = Form(""),
    user_descr: str = Form(""),
    categorie: str = Form(...),
    name_product: str = Form(...),
    price: int = Form(...),
    device: str = Form(...),
    product_descr: str = Form(""),
    mail: str = Form(""),
):
    try:
        wsinstance = get_ws_instance()
        if await verify_user(token, username, wsinstance, salt=salt):
            path = ""
            if file:
                ext = os.path.splitext(file.filename)[-1].lower()
                img_valide = ext in IMG_EXTENSIONS
                if img_valide:
                    _, path = await handle_marketplace_img(file)
            
            hub = get_hub_manager()
            
            product = {
                "name_user": name_user,
                "user_descr": user_descr,
                "categorie": categorie,
                "name_product": name_product,
                "price": abs(int(price)),
                "device": device,
                "product_descr": product_descr,
                "path_image": path,
                "timestamp": str(time.ctime()),
                "mail": mail
            }
            
            success = await hub.add_product(product, username=username)
            
            return {
                "success": success,
                "message": "Produit ajouté avec succès" if success else "Échec ajout",
                "product": product if success else None
            }
        else:
            return {
                "success": False,
                "message": "Authentification échouée"
            }
            
    except Exception as e:
        print(f"Erreur _add_product : {str(e)}")
        raise HTTPException(
            detail="Erreur serveur",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/mp/get_products")
async def _get_products(
    request: Request, 
    username: str = Form(...), 
    token: str = Form(...), 
    salt: str = Form(...),
):
    try:
        wsinstance = get_ws_instance()
        if await verify_user(token, username, wsinstance, salt=salt):
            hub = get_hub_manager()
            products = await hub.get_products(username)
            return {
                "success": True,
                "products": products,
            }
        return {
            "success": False,
            "products": [],
        }
    except Exception as e:
        print(f"Erreur _get_products : {str(e)}")
        raise HTTPException(
            detail="Erreur serveur",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/mp/del_product")
async def _del_product(
    request: Request, 
    username: str = Form(...), 
    token: str = Form(...), 
    salt: str = Form(...),
    number: int = Form(...)
):
    try:
        wsinstance = get_ws_instance()
        if await verify_user(token, username, wsinstance, salt=salt):
            hub = get_hub_manager()
            success = await hub.del_product(username, number)
            return {
                "success": success,
                "message": "Produit supprimé" if success else "Échec suppression"
            }
        return {
            "success": False,
            "message": "Non authentifié"
        }
    except Exception as e:
        print(f"Erreur _del_product : {str(e)}")
        raise HTTPException(
            detail="Erreur serveur",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )        