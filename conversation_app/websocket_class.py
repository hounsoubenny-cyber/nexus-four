#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 30 15:36:32 2026

@author: hounsousamuel
"""

import os, sys
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.join(__file__, ".."))))
import threading
import asyncio, nest_asyncio
from diskcache import Cache
from conversation_app.config import CacheDIR, CacheTime
from fastapi import WebSocket, WebSocketDisconnect, status

nest_asyncio.apply()

CACHE = Cache(CacheDIR)

def _ensure_cache():
    required_keys = {
        "groups": [],
        "login_user": [],
        "user_data": {},
        "profiles_imgs": {},
        "chat_nexus": {},
        "chat_nexus_terminal": {},
        "chat_nexus_metadata": {},
        "chat_nexus_care_metadata": {},
        "chat_nexus_care": {},
        "chat_nexus_care_terminal": {},
        "hub_skills": {},
        "hub_maketplace": {},
        "hub_metadata": {},
        }
    for k in required_keys:
        if k not in CACHE:
            print(k)
            CACHE.set(k, value=required_keys[k], expire=CacheTime)

LOCK = threading.Lock()
_ensure_cache()

class WebsocketManager:
    def __init__(self):
        self.active_connections = {}
        self.login_user = list(CACHE.get('login_user', default=[]))
        self.temp_salt = {}
        self.async_lock = asyncio.Lock()
        self.NOT_ALLOWED_NAMES = ['login_user', "user_data", "groups", "nexus"]
    
    def _update_active_connections(self, socket:WebSocket, who:str):
        if not who:
            raise ValueError("WHO requis pour ajouté l'user à la liste des users connectés !")
        with LOCK:
            if who not in self.active_connections:
                self.active_connections[who] = socket
                msg = f"User ({who}) ajouté avec succès à la liste des user connecté"
            else:
                msg = f"User ({who}) déja présent"
        
        print("MESSAGE : ", msg)
        return True
    
    def _verify_user(self, what:str="all", username:str=None):
        if not username:
            raise ValueError("USERNAME requis pour vérification !")
        if username in ("serveur", "nexus"):
            return True
        
        what =  what.lower() if what else "all"
        if what == "login":
            return username in self.login_user
        
        elif what == "connected":
            return username in self.active_connections or username in self.temp_salt
        
        else:
            return username in self.active_connections and username in self.login_user
    
    async def _set_salt_temp(self, salt:str, username:str):
        if not username or not salt:
            raise ValueError("USERNAME ET SALT requis pour connection !!!")
        
        self.temp_salt[username] = salt
        return username in self.temp_salt
    
    async def update_login_user(self, users:str|list = ""):
        async with self.async_lock:
            val = list(CACHE.get('login_user', default=[]))
            val.extend([users] if isinstance(users, str) else users)
            self.login_user = val
            CACHE.set("login_user", val, expire=CacheTime)
    
    def validate_username(self, username:str):
        return username not in self.NOT_ALLOWED_NAMES and username not in CACHE
    
    async def set_profile_img(self, path:str, username:str):
        try:
            profiles_imgs = CACHE.get("profiles_imgs", default={})
            profiles_imgs[username] = path
            CACHE.set("profiles_imgs", profiles_imgs, expire=CacheTime)
            return True
        except Exception as e:
            print("Erreur d'ajout de photo de profile : ", str(e))
            return False
    
    async def get_profile_img(self, username:str):
        try:
            profiles_imgs = CACHE.get("profiles_imgs", default={})
            name = profiles_imgs.get(username, "")
            return name
        except Exception as e:
            print("Erreur de l'obtention de photo de profile : ", str(e))
            return ""
        
    async def put_user_in_cache(self, username:str, data_user:dict):
        try:
            if any(c not in data_user for c in ("password_h", "password_e", "email", "username", "age")):
                raise ValueError("Data_user incomplet !")
                
            # async with self.async_lock:
            CACHE.set(username, {}, expire=CacheTime)
            data = CACHE.get("user_data")
            data[username] = data_user
            CACHE.set("user_data", data, expire=CacheTime)
                
            await self.update_login_user(username)
            return True
        
        except Exception as e:
            print("Erreur de sauvegarde de l'user dans le cache : ", str(e))
            return False
        
    async def get_user_info(self, username:str):
        async with self.async_lock:
            if username in CACHE:
                user_info = CACHE.get("user_data", default={})
                return user_info.get(username, None)
        return None
        
    async def delete_user(self, username:str):
        async with self.async_lock:
            val = list(CACHE.get('login_user', default=[]))
            if username in val:
                val.remove(username)
            CACHE.set("login_user", val, expire=CacheTime)
            
            if username in CACHE:
                CACHE.delete(username)
            
    async def get_messages(self, who:str, _with:str):
        async with self.async_lock:
            if self._verify_user("login", who):
                data = CACHE.get(who, default={})
                if data:
                    if _with in data:
                        return list(data[_with].items())
                    else:
                        return []
                else:
                    data = {_with: {}}
                    CACHE.set(who, value=data, expire=CacheTime)
                    return []
            return []
            
    async def get_friends(self, username:str):
        async with self.async_lock:
            if self._verify_user("login", username):
                data = CACHE.get(username, default={})
                imgs = CACHE.get("profiles_img", default={})
                if data and len(data) != 0: 
                    # print("Data : ", data)
                    to_return = []
                    for k in data:
                        img = imgs.get(k, "")
                        if data[k] and len(data[k]) != 0:
                            to_return.append([k, len(list(data[k].keys())) or 0, img])
                        else:
                            to_return.append([k, 0, img])
                            
                    return to_return
                
                CACHE.set(username, value={}, expire=CacheTime)
                return []
            return []
    
    async def add_friend(self, username:str, with_:str):
        async with self.async_lock:
            async with self.async_lock:
                if self._verify_user("login", username):
                    data = CACHE.get(username, default={})
                    data[with_] = {}
                    CACHE.set(username, value=data, expire=CacheTime)
                    return True
                return False
            
            
    async def update_messages(self, who:str, _with:str, msg:dict, send:str):
        if any(c in ("null", "undefined", "0") for c in (who, _with)):
            raise ValueError("Nom invalide !")
            
        async with self.async_lock:
            data = CACHE.get(who, default={})
            if data:
                if _with in data:
                    _data = data[_with]
                    if _data:
                        last_idx = int(str(list(_data.keys())[-1]).split("__")[-1]) + 1
                    else:
                        last_idx = 0
                    
                    key = f"{send}__{last_idx}"
                    
                    _data[key] = msg
                    data[_with] = _data
                    CACHE.set(who, value=data, expire=CacheTime)
                    return  
            
            
            key = f"{send}__0"
            
                
            data[_with] = {
                key: msg
                }
            CACHE.set(who, value=data, expire=CacheTime)
            return 
    
    async def update_messages_for_two(self, who:str, _with:str, msg:dict, send:str):
        await self.update_messages(who=who, _with=_with, msg=msg, send=send)
        await self.update_messages(who=_with, _with=who, msg=msg, send=send)
        
    async def connect(self, websocket:WebSocket, username:str):
        if not websocket or not username :
            raise ValueError("WEBSOCKET ET USERNAME requis pour connection !!!")
            
        connected = self._verify_user("connected", username)
        print("Connnect  ", connected)
        if connected:
            if username in self.active_connections:
                await websocket.accept()
                return username in self.active_connections
            
            elif username in self.temp_salt:
                salt = self.temp_salt[username]
                # del self.temp_salt[username]
                if not username in self.active_connections:
                    self.active_connections[username] = {}
                    
                self.active_connections[username]["websocket"] = websocket
                self.active_connections[username]["salt"] = salt
                
        else:
            print(f"Connexion refusée: {username} ne s'est pas login", connected)
            # await websocket.close(code=1008, reason="Username non authentifié")
            return False
        
        await websocket.accept()
        return username in self.active_connections
    
    async def disconnect(self, username:str="", total=False):
        if username in self.active_connections:
            del self.active_connections[username]
            
        if total:
            if username in self.temp_salt:
                del self.temp_salt[username]
        
            
        return not username in self.active_connections
    
    async def send_message(self, who:str, to:str, msg:str="", _type:str=None, cache:bool=True):
        """ who : Qui envoie le message, to: À qui """
        if not to or not who:
            raise ValueError("WHO et TO requis pour envoyer le message !")
        try:
            print("send message : ", msg)
            
            if self._verify_user(what="login", username=to) and self._verify_user(what="all", username=who):
                data = {
                    "from": who,
                    "to": to,
                    "type": _type if _type else "message",
                    "message": msg
                    }
                if to in self.active_connections:
                    websocket = self.active_connections[to]["websocket"]
                    await websocket.send_json(data)
                s_ws = self.active_connections[who]["websocket"]
                to_online = self._verify_user("connected", to)
                s_msg = "online" if to_online else "offline"
                if to != "serveur":
                    s_data = {
                        "from": "serveur",
                        "to": who,
                        "type": "message",
                        "message": f"Succès, {s_msg}"
                        }
                    await s_ws.send_json(s_data)
                    if cache:
                        await self.update_messages_for_two(who, to, data, send=who)
                return True
        
            else:
                s_data = {
                    "from": "serveur",
                    "to": who,
                    "type": "message",
                    "message": "Échec, destinataire non enrégistré !"
                    }
                s_ws = self.active_connections[who]["websocket"]
                await s_ws.send_json(s_data)
                if cache:
                    await self.update_messages(who="serveur", _with=who, msg=s_data, send="serveur")
                return False
        except Exception as e:
            print("Erreur lors de l'envoie du message : ", str(e))
            return False
    
    async def send_all(self, msg:str, who:str="serveur"):
        if not who:
            raise ValueError("WHO requis pour envoyer le message !")
        try:
            if self._verify_user(what="login", username=who):
                tasks = []
                data = {
                    "from": who,
                    "to": "all",
                    "type": "message",
                    "message": msg
                    }
                for k, v in self.active_connections.items():
                    ws = v['websocket']
                    ws.send_json(data)
                    tasks.append(asyncio.create_task(self.update_messages_for_two(k, who, data)))
                await asyncio.gather(*tasks)
                return True
            return False
        except Exception as e:
            print("Erreur lors de l'envoie du message à tous les user connectés : ", str(e))
            return False

if __name__ == "__main__":
    test_socket = WebsocketManager()
    # print(asyncio.run(test_socket.get_messages("sam", "sam")))
    # print(asyncio.run(test_socket.update_login_user("sam")))
    # print(CACHE.stats())
    # print(asyncio.run(test_socket.delete_user("sam")))
    # print(test_socket.login_user)
    # print(CACHE.get("samueltest"))
    print(CACHE.get("new_user"))
    
