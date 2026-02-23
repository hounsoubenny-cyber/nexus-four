#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 21 16:24:41 2026

@author: hounsousamuel
"""


import os
import sys
import asyncio
import copy

sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.join(__file__, "..", ".."))))
from conversation_app.websocket_class import _ensure_cache, CACHE
from conversation_app.config import CacheTime

_ensure_cache()

class HubManager:
    def __init__(self):
        self.meta_key = "hub_metadata"
        self.hub_skills_key = "hub_skills"
        self.hub_marketplace_key = "hub_maketplace"
        self.keys =  [self.meta_key, self.hub_marketplace_key, self.hub_skills_key]
        self.async_lock = asyncio.Lock()
        
    async def add_skills(self, skills:dict, username:str, erase:bool=False):
        try:
            # Portfolio ex: {"projet_de_antispam": {"nom": "pan", "description": "", "meta": {git_lien:"", "gmail":"", "drive":""}}}
            await self.put_user_in_cache(username=username)
            async with self.async_lock:
                cache = CACHE.get(self.hub_skills_key)
                print(cache)
                if erase:
                    cache[username] = {}
                    to_set = {}
                    to_set["skills"] = list(dict.fromkeys(skills["skills"])) #Important, si absent ça va planter et c'est le comportement voulu
                    to_set["descr"] = skills.get('descr', "")
                    portfolio = skills.get("portfolio", {})
                    portfolio_to_set = {}
                    if portfolio:
                        for k, v in portfolio.items():
                            if v:
                                portfolio_to_set[k] = v
                                
                    to_set["portfolio"] = portfolio_to_set
                    cache[username] = to_set
                    
                else:
                    data = cache[username]
                    if not "skills" in data:
                        data["skills"] = skills["skills"]
                    else:
                        d_skills = data["skills"]
                        new_skills = list(dict.fromkeys(d_skills + skills["skills"]))
                        data["skills"] = new_skills
                        
                        
                    if skills.get('descr', "") and not data.get("skills", ""):
                        data["descr"] = skills["descr"]
                    
                    portfolio = skills.get("portfolio", {})
                    
                    if not 'portfolio' in data or not data.get("portfolio", {}):
                        data["portfolio"] = portfolio
                    
                    else:
                        if portfolio:
                            d_portfolio = data["portfolio"]
                            for k, v in list(portfolio.items()):
                                if k not in d_portfolio:
                                    d_portfolio[k] = v
                                if "meta" not in v:
                                    v_cop = copy.deepcopy(v)
                                    v_cop["meta"] = {}
                                    d_portfolio[k] = v
                                else:
                                    for i, j in v.items():
                                        if i != "meta":
                                            if i not in d_portfolio[k]:
                                                d_portfolio[k][i] = j
                                            else:
                                                if str(d_portfolio[k][i].lower()) != str(j).lower():
                                                    d_portfolio[k][i] = j
                                        else:
                                            for p, q in j.items():  # j serait un dictionnaire
                                                if p not in d_portfolio[k][i]["meta"]:
                                                    d_portfolio[k][i]["meta"][p] = q
                                                else:
                                                    if d_portfolio[k][i]["meta"][p] != q:
                                                        d_portfolio[k][i]["meta"][p] = q
                    cache[username] = data
            CACHE.set(self.hub_skills_key, cache, CacheTime)
            return True                                                        
                    
        except Exception as e:
            print("Erreur hubManager.add_skills : ", str(e))
            raise
            # return False
    
    async def get_skills(self, username:str):
        try:
            await self.put_user_in_cache(username)
            async with self.async_lock:
                cache = CACHE.get(self.hub_skills_key, {}).get(username, {})
                # print(cache, CACHE.get(self.hub_skills_key))
                return cache
        except Exception as e:
            print("Erreur dans get skills : ", str(e))
            return {}
        
    async def put_user_in_cache(self, username:str):
        async with self.async_lock:
            for k in self.keys:
                if username not in CACHE.get(k, {}):
                    c = CACHE.get(k, {})
                    c[username] = {}
                    CACHE.set(k, c, CacheTime)
            
    async def get_hub_img_profile(self, username:str):
        try:
            await self.put_user_in_cache(username)
            async with self.async_lock:
                cache = CACHE.get(self.meta_key, {}).get(username, {})
                return [cache.get("img_profile_path", ""), cache.get("slogan", "")]
        except Exception as e:
            print("Erreur hubManager.get_hub_img_profile : ", str(e))
            return ""
    
    async def set_hub_img_profile(self, username:str, path:str, mot:str=""):
        try:
            await self.put_user_in_cache(username)
            async with self.async_lock:
                c = CACHE.get(self.meta_key, {})
                c[username]["img_profile_path"] = path
                c[username]["slogan"] = mot
                CACHE.set(self.meta_key, c, CacheTime)
                return True
            
        except Exception as e:
            print("Erreur hubManager.set_hub_img_profile : ", str(e))
            return False
    
    async def set_metadata(self, metadata:dict, username:str):
        try:
            keys = [
                "git_lien", "gmail", "lnkd_lien"
                ]
            await self.put_user_in_cache(username)
            async with self.async_lock:
                c = CACHE.get(self.meta_key, {})
                m = c[username]
                for k in keys:
                    v = metadata[k]
                    if v:
                        m[k] = v
                c[username] = m
                CACHE.set(self.meta_key, c, CacheTime)
                return True
            
            return False
        except Exception as e:
            print("Erreur hubManager.set_metadata : ", str(e))
            return False
    
    
    async def add_product(self, product:dict, username:str):
        try:
            await self.put_user_in_cache(username)
            async with self.async_lock:
                c = CACHE.get(self.hub_marketplace_key, {})
                m = c[username]
                m[len(m) + 1] = product
                c[username] = m
                CACHE.set(self.hub_marketplace_key, c, CacheTime)
                return True
            return False
        except Exception as e:
            print("Erreur hubManager.add_product : ", str(e))
            return False
    
    async def get_products(self, username:str):
        try:
            await self.put_user_in_cache(username)
            async with self.async_lock:
                c = CACHE.get(self.hub_marketplace_key, {}).get(username, {})
                return list(c.values())
                return []
            return []
        except Exception as e:
            print("Erreur hubManager.get_products : ", str(e))
            return []
        
    async def search_skills(self, skill:list=[]):
        ...
        
    async def del_product(self, username:str, number:int):
        try:
            await self.put_user_in_cache(username)
            async with self.async_lock:
                c = CACHE.get(self.hub_marketplace_key, {})
                m = c[username]
                m = {k:v for k, v in m.items() if int(k) != number}
                c[username] = m
                CACHE.set(self.hub_marketplace_key, c, CacheTime)
                return True
            return False
        except Exception as e:
            print("Erreur hubManager.del_product : ", str(e))
            return False
        