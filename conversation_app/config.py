#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 30 17:13:11 2026

@author: hounsousamuel
"""

import os

IP = "0.0.0.0"
PORT = 8000
ROUNDS = 100
EXPIRE_TIME = 160
NBF = 1
LIMIT = 5
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))

CacheDIR = os.path.join(DIR, "var", "cache")

FastApiDir = os.path.join(DIR, "fastapi_mount", "files")

FastApiDirProfile = os.path.join(DIR, "fastapi_mount", "profile_img")

INDEX_PATH = os.path.join(DIR, "chat_nexus", "index")

EBD_PATH = os.path.join(DIR, "chat_nexus", "EMBEDDING")

DOCS_PATH = os.path.join(DIR, "chat_nexus", "DOCS_IFRI")

text_dir = os.path.join(DIR, "fastapi_mount", "nexus_files")

HubDIR = os.path.join(DIR, "fastapi_mount", "hub")

REACT_PATH = os.path.join(DIR, "..", "frontend", "REACT", "build", "static")
BUILD_PATH = os.path.join(DIR, "..", "frontend", "REACT", "build")
REACT_URL = "/static"
BUILD_URL = "/build"
INDEX_HTML = os.path.join(DIR, "..", "frontend", "REACT", "build", "index.html")
REACT_EXIST = os.path.exists(REACT_PATH)

LIST_DIR = [
    DIR,
    CacheDIR, 
    FastApiDir, 
    FastApiDirProfile, 
    INDEX_PATH, 
    EBD_PATH, 
    DOCS_PATH, 
    text_dir, 
    HubDIR, 
    os.path.join(HubDIR, "imgs_profile")
]

CacheTime = None

IMG_EXTENSIONS = (".jpg", ".jpeg", ".png", ".ppm", ".bmp", ".pgm", ".tif", ".tiff", ".webp")

MODEL_PATH = os.path.join(DIR, "chat_nexus", "MODEL", "qwen2-5", "Qwen2.5-7B-Instruct-Q6_K.gguf")

# TinyPath = os.path.join(DIR, "chat_nexus", "MODEL_DEMO", "tiny", "qwen2.5-0.5b-instruct-fp16.gguf")

DemoPath = os.path.join(DIR, "chat_nexus", "MODEL_DEMO", "tiny", "gemma-3-1b-it-Q4_K_M.gguf")

if DEMO_MODE:
    
    print("🐳 DEMO MODE: Utilisation du modèle de DEMO")
    MODEL_CONFIG = {
        "qwen": DemoPath,
        "phi": DemoPath,
        "gemma": DemoPath,
        "demo": DemoPath,
    }
    
else:
    
    print("🚀 PRODUCTION MODE: Utilisation de tout les modèles")
    MODEL_CONFIG = {
        "qwen": os.path.join(DIR, "chat_nexus", "MODEL", "qwen", "Qwen2.5-3B-Instruct-Q5_K_S.gguf"),
        "phi": os.path.join(DIR, "chat_nexus", "MODEL", "phi", "Phi-3.5-mini-instruct-Q4_K_M.gguf"),
        "gemma": os.path.join(DIR, "chat_nexus", "MODEL", "gemma", "gemma-2-2b-it-Q6_K.gguf"),
        "demo": DemoPath,
        }

# print(EBD_PATH)

CONTEXT_GETTER_CONFIG = {
    "embed_path_or_name" : EBD_PATH,
    "chunk_size": 500, 
    "overlap" : 50,
    "seps" : ["\n\n", "\n", ".","?", "!", " "],
    "top_k":  3,
    "path": INDEX_PATH,
    "docs_path": DOCS_PATH
    }


REFUSED_EXT = [
    ".csv", ".rar", ".zip", ".xls"
    ]


SYS_INSTRUCTION = """ """
SYS_INSTRUCTION_CAR = """ """

PATH = os.path.join(DIR, "chat_nexus", "PROMPTS", "brain_sys_prompt", "system12.md")

with open(PATH, "r") as f:
    SYS_INSTRUCTION = f.read()

PATH_CARE = os.path.join(DIR, "chat_nexus", "PROMPTS", "care_sys_prompt", "system_prompt_care.md")
with open(PATH_CARE, "r") as f:
    SYS_INSTRUCTION_CARE = f.read()

# print(SYS_INSTRUCTION_CARE)
# print(len(SYS_INSTRUCTION))
def _create_dirs():
    for path in LIST_DIR:
        os.makedirs(path, exist_ok=True)
        
_create_dirs()
