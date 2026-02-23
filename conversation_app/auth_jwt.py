#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 30 21:58:27 2026

@author: hounsousamuel
"""

import os, sys
from jose import jwt, JWTError
from fastapi import HTTPException, status
from config import EXPIRE_TIME, NBF
from datetime import datetime, timedelta

def create_token(data:dict, key:bytes=b""):
    username = data.get("username", None)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Username absent pour la création du token"
            )
    try:
        iat = datetime.utcnow()
        exp = iat + timedelta(minutes=EXPIRE_TIME)
        nbf = iat + timedelta(seconds=NBF)
        cop = {"sub": username, "exp": exp, "nbf": nbf, "iat": iat}
        token = jwt.encode(cop, key=key, algorithm="HS256")
        return token
    
    except Exception as e:
        print("Erreur de création du token : ", str(e))
    

def verify_token(token:str, key:bytes=b""):
    try:
        decoded = jwt.decode(token, key, algorithms=["HS256"])
        if not "sub" in decoded:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Token invalide !"
                ) 
        return decoded["sub"]
    except JWTError as e:
        print('Erreur jwt: ', type(e).__name__, ": ", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide !",
            headers={"WWW-Authenticate": "Baerer"}
            )
    
    except Exception as e:
        print('Erreur : ', type(e).__name__, ": ", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erreur générale !",
            headers={"WWW-Authenticate": "Baerer"}
            )