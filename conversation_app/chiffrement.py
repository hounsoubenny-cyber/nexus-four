#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 29 18:54:09 2026

@author: hounsousamuel
"""

import bcrypt
import base64
from config import ROUNDS
from cryptography.fernet import Fernet

class FernetManager:
    def __init__(self, password:str, salt:bytes=None):
        if salt:
            if isinstance(salt, str):
                self.salt = salt.encode()
            
            else:
                self.salt = salt
        else:
            self.salt = self._gen_salt()
        print("Voila votre salt, ne le PERDEZ PAS : ", self.salt)
        self.key = self._gen_key(password, self.salt)
        self.fernet = Fernet(self.key)
    
    def _gen_key(self, password:str, salt:bytes):
        if not password:
            raise ValueError("Password requis pour générer la clé !!")
        return base64.urlsafe_b64encode(bcrypt.kdf(password.encode(), salt, desired_key_bytes=32, rounds=ROUNDS))
    
    def _gen_salt(self):
        return bcrypt.gensalt()
    
    def _update_key(self, key):
        self.key = key
    
    def _update_fernet(self):
        self.fernet = Fernet(self.key)
    
    def encrypt(self, data:str):
        if isinstance(data, bytes):
            return self.fernet.encrypt(data)
        if isinstance(data, (int, float)):
            data = str(data)
        return self.fernet.encrypt(data.encode())
    
    def decrypt(self, data:bytes):
        if isinstance(data, str):
            return self.fernet.decrypt(data.encode())
        return self.fernet.decrypt(data).decode()
    
    def encrypt_file(self, path:str, to:str, inplace:bool=False, mode:str=""):
        try:
            data = None
            with open(path, "r"+str(mode)) as f:
                data = f.read()
            
            if data:
                if isinstance(data, str):
                    data = data.encode()
                encoded = self.encrypt(data)
                if inplace:
                    to_open = path
                
                else:
                    to_open = to
                
                with open(to_open, "wb") as f:
                    f.write(encoded)
                
                return True
            
            else:
                print('Fichier vide ou invalide !')
        except Exception as e:
            print('Erreur lors du cryptage de ', path, " erreur : ", str(e))
            return False
    
    def decrypt_file(self, path:str, to:str, inplace:bool=False, mode:str=""):
        try:
            data = None
            with open(path, "r"+str(mode)) as f:
                data = f.read()
            
            if data:
                if isinstance(data, str):
                    data = data.encode()
                decoded = self.fernet.decrypt(data)
                if inplace:
                    to_open = path
                
                else:
                    to_open = to
                
                with open(to_open, "w" + str(mode)) as f:
                    if mode.lower().strip() == "b":
                        f.write(decoded)
                    
                    else:
                        f.write(decoded.decode())
                
                return True
            
            else:
                print('Fichier vide ou invalide !')
        except Exception as e:
            print('Erreur lors du décryptage de ', path, " erreur : ", str(e))
            import traceback
            traceback.print_exc()
            return False

def hashpw(password:str):
    if isinstance(password, str):
        password = password.encode()
    
    return bcrypt.hashpw(password, bcrypt.gensalt())

def checkpw(password:str, hashed:bytes):
    if isinstance(password, str):
        password = password.encode()
    
    return bcrypt.checkpw(password=password, hashed_password=hashed)


if __name__ == "__main__":
    fm1 = FernetManager("Samuel")
    fm2 = FernetManager("samuel", bcrypt.gensalt().decode())
    fm1._update_key(fm1._gen_key("Sam", fm1.salt))
    fm1._update_fernet()
    fm1.encrypt("Samuel est trop beau et aime Mike même si il veut pas le reconnaître")
    fm2.encrypt(0)
    path = "/home/hounsousamuel/Images/Copies d'écran/Copie d'écran_20260106_231402.png"
    to = "/home/hounsousamuel/Images/Copies d'écran/Copie d'écran_20260106_231402.png.fernet"
    print(fm1.encrypt_file(inplace=False, path=path, to=to, mode='b'))
    print(fm1.decrypt_file(inplace=False, path=to, to=path.replace(".png", "_&_.png"), mode="b"))
    
    
    