#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 16 10:06:13 2026
@author: hounsousamuel
"""
import os, sys
os.environ['LLAMA_CPP_LOG_LEVEL'] = 'ERROR'
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
import logging
logging.getLogger('sentence_transformers').setLevel(logging.ERROR)
logging.getLogger('transformers').setLevel(logging.ERROR)
logging.getLogger('huggingface_hub').setLevel(logging.ERROR)

sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.join(__file__, "..", ".."))))
import joblib, asyncio, nest_asyncio, gc
from datetime import datetime
from uuid import uuid4
from llama_cpp import Llama
from conversation_app.config import (
    CacheTime, 
    MODEL_CONFIG, 
    CONTEXT_GETTER_CONFIG, 
    SYS_INSTRUCTION, 
    SYS_INSTRUCTION_CARE
   )
from conversation_app.websocket_class import _ensure_cache, CACHE
from conversation_app.chat_nexus.context_getter import ContextGetter
from fastapi import WebSocket, WebSocketDisconnect, WebSocketException

nest_asyncio.apply()

default_path = "./MODELS_LLM_EBD_DOCS/MODEL/qwen2-5/Qwen2.5-7B-Instruct-Q6_K.gguf"
default_name = "qwen"
os.environ['LLAMA_CPP_LOG_LEVEL'] = 'ERROR'
logging.getLogger('sentence_transformers').setLevel(logging.ERROR)
logging.getLogger('transformers').setLevel(logging.ERROR)


_ensure_cache()


class ChatNexus:
    def __init__(self, verbose: bool = False, echo: bool = False):
        self.models_configs = MODEL_CONFIG
        self.n_thread = int(joblib.cpu_count() * 0.9)
        self.n_ctx = 512 * 8  # 512 = 1page # *24
        self.n_batch = 512 * 1
        self.v = verbose
        self.echo = echo
        self.models: dict[str: Llama] = {}
        self.context_getter = None
        self.n_last = 5
        self.async_lock = asyncio.Lock()
        self.sys_instruction = SYS_INSTRUCTION
        self.stops_words = {
            "phi": ["<|end|>", "<|assistant|>"],
            "qwen": ["<|im_end|>", "<|im_start|>"],
            "mistral": ["</s>", "[/INST]"],
            "gemma": ["<end_of_turn>", "<start_of_turn>"],
            "demo": ["<end_of_turn>", "<start_of_turn>"]
        }
        self.top_k = 30
        self.top_p = 0.95
        self.temp = 0.8
        self.stream = True
        self.his = ""
        self.login_user = list(CACHE.get('login_user', default=[]))
        self.active_connections = {}
        self.active_connections_care = {}
        self.model_usage = {
            "phi": 0,
            "qwen": 0,
            "gemma": 0
        }
        self.seuil = -10

    def create_model(self, name: str = "qwen"):
        if not name in self.models:
            model = Llama(
                model_path=self.models_configs[name],
                n_ctx=self.n_ctx,
                n_batch=self.n_batch,
                n_gpu_layers=0,
                n_threads=self.n_thread,
                use_mmap=True,
                use_mlock=False,
                verbose=self.v,
                seed=42,
                f16_kv=True,
                logits_all=False,
            )
            self.models[name] = model
        if not self.context_getter:
            self.context_getter = ContextGetter(**CONTEXT_GETTER_CONFIG)

    def get_model(self, name):
        print("get_model", name)
        self.create_model(name)
        return self.models[name]

    async def delete(self, name: str):
        if name in self.models:
            del self.models[name]
            gc.collect()
            print(f"✅ {name} déchargé de la RAM")
            return True
        print(f"⚠️ {name} pas en mémoire")

    def adapt_params(self, prompt: str) -> dict:
        p = prompt.lower()
        code_kw = [
            "code", "programme", "fonction", "class", "def",
            "python", "java", "javascript", "c++", "bug",
            "erreur", "debug", "algorithme", "implémenter"
        ]
        explain_kw = [
            "explique", "qu'est-ce", "c'est quoi", "comment",
            "pourquoi", "définition", "principe", "concept",
            "décris", "parle-moi", "dis-moi"
        ]
        exercise_kw = [
            "exercice", "qcm", "question", "quiz",
            "teste", "évalue", "génère des questions"
        ]
        summary_kw = [
            "résume", "synthèse", "récapitule",
            "points clés", "en bref", "résumé"
        ]
        creative_kw = [
            "écris", "rédige", "compose", "invente",
            "crée", "histoire", "poème"
        ]
        if any(kw.lower() in p.lower() for kw in code_kw):
            return {
                "temperature": 0.2,
                "top_k": 40,
                "top_p": 0.9,
                "max_tokens": 1500,
                "repeat_penalty": 1.0
            }
        elif any(kw.lower() in p.lower() for kw in explain_kw):
            return {
                "temperature": 0.5,
                "top_k": 50,
                "top_p": 0.9,
                "max_tokens": 1000,
                "repeat_penalty": 1.1
            }
        elif any(kw.lower() in p.lower() for kw in exercise_kw):
            return {
                "temperature": 0.7,
                "top_k": 50,
                "top_p": 0.9,
                "max_tokens": 700,
                "repeat_penalty": 1.2
            }
        elif any(kw.lower() in p.lower() for kw in summary_kw):
            return {
                "temperature": 0.3,
                "top_k": 40,
                "top_p": 0.85,
                "max_tokens": 400,
                "repeat_penalty": 1.0
            }
        elif any(kw.lower() in p.lower() for kw in creative_kw):
            return {
                "temperature": 0.9,
                "top_k": 80,
                "top_p": 0.95,
                "max_tokens": 800,
                "repeat_penalty": 1.05
            }
        return {
            "temperature": 0.7,
            "top_k": self.top_k,
            "top_p": self.top_p,
            "max_tokens": 800,
            "repeat_penalty": 1.1
        }

    async def create_new_chat(self, username: str, prompt: str, care: bool = False, terminal: bool = False):
        key, meta_key, _ = await self.handle_keys(terminal=terminal, care=care)
        title = prompt[:50] + ("..." if len(prompt) > 50 else "")
        cd = str(datetime.now().strftime("%Y%m%d_%H%M%S"))
        ud = str(uuid4())
        conv_k = f"_{ud}_{cd}".replace(" ", "_")
        print(key, meta_key)
        await self.put_user_in_cache(username, terminal=terminal, care=care)
        cache = CACHE.get(key, {})
        print(cache)
        if username not in cache:
            cache[username] = {}
        cache[username][conv_k] = {}
        CACHE.set(key, cache, CacheTime)
        # await self.update_cache(username, "user", prompt, conv_k=conv_k, terminal=terminal, care=care)
        meta = CACHE.get(meta_key, {})
        if username not in meta:
            meta[username] = {}
        meta[username][conv_k] = {
            "title": title,
            "id": ud,
            "cd": cd,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        CACHE.set(meta_key, meta, CacheTime)
        return conv_k

    async def handle_history_and_prompt(self, username: str, prompt: str, ctx: str = "PAS DE CONTEXT, FAIS COMME TU VEUX", name: str = "qwen", conv_k: str | None = None, care: bool = False, terminal: bool = False):
        if not conv_k:
            raise ValueError
        ctx = "PAS DE CONTEXT, FAIS COMME TU VEUX" if not ctx else ctx
        # prompt += "\nNOTE TRÈS IMPORTANTE: RÉPOND DANS LA LANGUE DE L'ÉTUDIANT!"
        key, _, sys_instruction = await self.handle_keys(terminal=terminal, care=care)
        try:
            async with self.async_lock:
                caches = CACHE.get(key, {}).get(username, {}).get(conv_k, {})
            if caches:
                to_take = list(caches.keys())[-self.n_last * 2:]
                to_return = ""
                if "phi" in name:
                    to_return += f"<|system|>{sys_instruction}\nCONTEXT: {ctx} <|end|>\n"
                    for k in to_take:
                        if "user" in k:
                            to_return += f"<|user|>{caches[k]}<|end|>\n"
                        else:
                            to_return += f"<|assistant|>{caches[k]}<|end|>\n"
                    to_return += f"<|user|>{prompt}<|end|>\n<|assistant|>"
                    
                elif "qwen" in name:
                    to_return += f"<|im_start|>system\n{sys_instruction}\nCONTEXT: {ctx} <|im_end|>\n"
                    for k in to_take:
                        if "user" in k:
                            to_return += f"<|im_start|>user\n{caches[k]}<|im_end|>\n"
                        else:
                            to_return += f"<|im_start|>assistant\n{caches[k]}<|im_end|>\n"
                    to_return += f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant"
                    
                elif "gemma" in name or name =="demo":
                    to_return += f"<start_of_turn>user\n{sys_instruction}\nCONTEXT: {ctx}\n<end_of_turn>\n"
                    for k in to_take:
                        if "user" in k:
                            to_return += f"<start_of_turn>user\n{caches[k]}<end_of_turn>\n<start_of_turn>model\n<end_of_turn>\n"
                        else:
                            to_return += f"<start_of_turn>model\n{caches[k]}<end_of_turn>\n"
                    to_return += f"<start_of_turn>user\n{prompt}<end_of_turn>\n<start_of_turn>model\n"
                    
                else:
                    to_return += f"<s>[INST]\n{sys_instruction}\nCONTEXT: {ctx} [/INST]\n"
                    for k in to_take:
                        if "user" in k:
                            to_return += f"<s>[INST]\n{caches[k]}[/INST]\n"
                        else:
                            to_return += f"\n{caches[k]}</s>\n"
                    to_return += f"<s>[INST]{prompt}[/INST]"
                return to_return, self.stops_words.get(name, self.stops_words["mistral"])
            
            else:
                to_return = ""
                if "phi" in name:
                    to_return += f"<|system|>{sys_instruction}\nCONTEXT: {ctx} <|end|>\n"
                    to_return += f"<|user|>{prompt}<|end|>\n<|assistant|>"
                    
                elif "qwen" in name:
                    to_return += f"<|im_start|>system\n{sys_instruction}\nCONTEXT: {ctx} <|im_end|>\n"
                    to_return += f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant"
                    
                elif "gemma" in name or name =="demo" :
                    to_return += f"<start_of_turn>user\n{sys_instruction}\nCONTEXT: {ctx}\n<end_of_turn>\n"
                    to_return += f"<start_of_turn>user\n{prompt}<end_of_turn>\n<start_of_turn>model\n"
                    
                else:
                    to_return += f"<s>[INST]\n{sys_instruction}\nCONTEXT: {ctx} [/INST]\n"
                    to_return += f"<s>[INST]{prompt}[/INST]"
                return to_return, self.stops_words.get(name, self.stops_words["mistral"])
        except Exception as e:
            print("Erreur dans Caht.handle_history : ", str(e))
            import traceback
            traceback.print_exc()
            return None, None

    async def update_cache(self, username: str, who: str = "user", prompt_or_response: str = "", conv_k: str | None = None, care: bool = False, terminal: bool = False):
        if conv_k is None:
            raise ValueError("conv_k requis")
        key, _, _ = await self.handle_keys(terminal=terminal, care=care)
        async with self.async_lock:
            try:
                caches = CACHE.get(key, {})
                if username not in caches:
                    caches[username] = {}
                if conv_k not in caches[username]:
                    caches[username][conv_k] = {}
                conv_messages = caches[username][conv_k]
                if conv_messages:
                    keys = list(conv_messages.keys())
                    last = int(keys[-1].split("__")[-1]) + 1
                else:
                    last = 0
                caches[username][conv_k][f"{who}__{last}"] = prompt_or_response
                CACHE.set(key, caches, expire=CacheTime)
                return True
            except Exception as e:
                print(f"❌ update_cache: {str(e)}")
                import traceback
                traceback.print_exc()
                return False

    async def put_user_in_cache(self, username: str, care: bool = False, terminal: bool = False):
        key, _, _ = await self.handle_keys(terminal=terminal, care=care)
        # print(key, "\n", CACHE)
        # async with self.async_lock:
        try:
            caches = CACHE.get(key, {})
            # print("put_user_in_cache")
            # print(caches)
            if not (username in caches):
                caches[username] = {}
                CACHE.set(key, caches, expire=CacheTime)
            return True
        except Exception as e:
            print("Erreur dans Cache.put_in_cache : ", str(e))
            return False

    async def get_history(self, username: str, care: bool = False, terminal: bool = False):
        key, meta_key, _ = await self.handle_keys(terminal=terminal, care=care)
        # async with self.async_lock:
        try:
            caches = CACHE.get(key, {})
            if not (username in caches):
                await self.put_user_in_cache(username, terminal=terminal, care=care)
                return {
                    "keys": [],
                    "meta": []
                }
            else:
                return {
                    "keys": list(caches[username].keys())[::-1],
                    "meta": list(CACHE.get(meta_key, {}).get(username, {}).values())[::-1]
                }
        except Exception as e:
            print("Erreur dans get history : ", str(e))
            return {
                "keys": [],
                "meta": []
            }

    async def get_history_conv(self, username: str, conv_k: str, care: bool = False, terminal: bool = False):
        key, _, _ = await self.handle_keys(terminal=terminal, care=care)
        # async with self.async_lock:
        try:
            caches = CACHE.get(key, {})
            if not (username in caches):
                await self.put_user_in_cache(username, terminal=terminal, care=care)
                return []
            else:
                return list(CACHE.get(key, {}).get(username, {}).get(conv_k, {}).items())
        except Exception as e:
            print("Erreur dans get history : ", str(e))
            return []


    async def handle_keys(self, terminal: bool = False, care: bool = False):
        if care:
            key = "chat_nexus_care_terminal" if terminal else "chat_nexus_care"
            meta_key = "chat_nexus_care_metadata"
            sys_instruction = SYS_INSTRUCTION_CARE
        else:
            key = "chat_nexus_terminal" if terminal else "chat_nexus"
            meta_key = "chat_nexus_metadata"
            sys_instruction = SYS_INSTRUCTION
        return key, meta_key, sys_instruction

    async def chat(self, username: str, question: str, rag: bool | None = True, terminal: bool = True, stream: bool = True, name: str = "qwen", conv_k: str | None = None, care: bool = False):
        if not conv_k:
            raise ValueError
        try:
            if care:
                name = "gemma"
            
            self.stream = stream
            self.create_model(name)
            if not os.path.exists(self.models_configs[name]):
                for k, v in self.models_configs.items():
                    # print(k, v)
                    if os.path.exists(v):
                        name = k
                        print("Avertissement, modèle inexistant, switch vers", k)
                        break
            await self.put_user_in_cache(username, terminal=terminal, care=care)
            
            print("\nNOTE : Model chargé !")
            if rag is None:
                q = f"""Analyse cette question et réponds UNIQUEMENT par OUI ou NON (rien d'autre).
                La question nécessite-t-elle des documents ou du contenu spécifique du cours pour une réponse précise et utile ?
                Question : {question}
                Réponds seulement OUI ou NON."""
                answer = self.get_model(name)(prompt=q, max_tokens=20, temperature=0.1)
                answer_text = answer["choices"][0]["text"].lower()
                # print("Answer : ", answer)
                if "oui" in answer_text:
                    ctx, source = self.context_getter.get_context(question)
                else:
                    ctx, source = None, None
            else:
                if rag:
                    ctx, source = self.context_getter.get_context(question)
                else:
                    ctx, source = None, None
            full_prompt, stop_words = await self.handle_history_and_prompt(username, question, ctx=ctx, name=name, conv_k=conv_k, care=care, terminal=terminal)
            full_prompt = full_prompt[-int(self.n_ctx * 0.6):]
            print("Full prompt : ", len(full_prompt))
            params = self.adapt_params(full_prompt)
            if self.stream:
                self.source = ""
                self.his = ""
                stream = self.get_model(name)(
                    prompt=full_prompt,
                    max_tokens=params["max_tokens"],
                    temperature=params["temperature"],
                    top_k=params["top_k"],
                    top_p=params["top_p"],
                    repeat_penalty=params["repeat_penalty"],
                    stream=True,
                    stop=stop_words
                )
                await self.update_cache(username, who="user", prompt_or_response=question, conv_k=conv_k, terminal=terminal, care=care)
                if terminal:
                    for chunk in stream:
                        self.his += chunk["choices"][0]["text"] + " "
                        print(chunk["choices"][0]["text"], end="", flush=True)
                    if source:
                        self.source = "\n".join(source)
                        print("\nSources : ", self.source)
                    await self.update_cache(username, who="nexus", prompt_or_response=self.his, conv_k=conv_k, terminal=terminal, care=care)
                    
                else:
                    if source:
                        self.source = "\n".join(source)
                    print(stream)
                    return stream
            else:
                self.source = ""
                response = self.get_model(name)(
                    prompt=full_prompt,
                    max_tokens=params["max_tokens"],
                    temperature=params["temperature"],
                    top_k=params["top_k"],
                    top_p=params["top_p"],
                    repeat_penalty=params["repeat_penalty"],
                    stream=False,
                    stop=stop_words
                )
                if terminal:
                    print(response["choices"][0]["text"])
                    if source:
                        self.source = "\n".join(source)
                        print("Sources : ", self.source)
                    await self.update_cache(username, who="user", prompt_or_response=question, conv_k=conv_k, terminal=terminal, care=care)
                    await self.update_cache(username, who="nexus", prompt_or_response=response, conv_k=conv_k, terminal=terminal, care=care)
                else:
                    await self.update_cache(username, who="user", prompt_or_response=question, conv_k=conv_k, terminal=terminal, care=care)
                    await self.update_cache(username, who="nexus", prompt_or_response=response, conv_k=conv_k, terminal=terminal, care=care)
                    if source:
                        self.source = "\n".join(source)
                return response["choices"][0]["text"]
        except Exception as e:
            print("Erreur dans Chat.chat : ", str(e))
            import traceback
            traceback.print_exc()
            return "Désolé, une erreur est survenue."

    async def connect(self, ws: WebSocket, username: str, salt: str = None, care:bool=False):
        if not salt:
            return False
        if username in self.login_user:
            await ws.accept()
            if not care:
                if username in self.active_connections:
                    return True
                self.active_connections[username] = {}
                self.active_connections[username]['websocket'] = ws
                self.active_connections[username]["salt"] = salt
            else:
                if username in self.active_connections_care:
                    return True
                self.active_connections_care[username] = {}
                self.active_connections_care[username]['websocket'] = ws
                self.active_connections_care[username]["salt"] = salt
            return True
        return False

    async def disconnect(self, username: str, care:bool=False):
        if not care:
            if username in self.active_connections:
                del self.active_connections[username]
        else:
            if username in self.active_connections_care:
                del self.active_connections_care[username]
        return True

    async def send_message(self, data: dict):
        try:
            username = data["from"]
            question = data["question"]
            rag = data["rag"]
            conv_k = data["conv_k"]
            care = data["care"]
            name = data["name"]
            if not care:
                ws: WebSocket = self.active_connections[username]["websocket"]
            else:
                ws: WebSocket = self.active_connections_care[username]["websocket"]
            print("WS : ", ws, self.active_connections)
            if ws:
                key, meta_key, _ = await self.handle_keys(terminal=False, care=care)
                
                print(data, key, meta_key)
                if conv_k == "##new_conv##":
                    await self.put_user_in_cache(username, terminal=False, care=care)
                    conv_k = await self.create_new_chat(username, question, care=care, terminal=False)
                    print("Nouvelle conversation créer : ", conv_k)
                if not conv_k.startswith("_"):
                    conv_k = "_" + conv_k
                stream = await self.chat(username, question, rag=rag, terminal=False, stream=True, name=name, conv_k=conv_k, care=care)
                title = CACHE.get(meta_key, {}).get(username, {}).get(conv_k, {}).get("title", "")
                self.his = ""
                for chunk in stream:
                    txt = chunk["choices"][0]["text"]
                    self.his += txt
                    to_send = {
                        "message": txt,
                        "done": False,
                        "type": "answer",
                        'conv_k': conv_k,
                        "title": title,
                    }
                    await ws.send_json(to_send)
                    await asyncio.sleep(0.0001)
                if self.source:
                    await ws.send_json(
                        {
                            "message": self.source,
                            "done": False,
                            "type": "source",
                            'conv_k': conv_k,
                            "title": title,
                        }
                    )
                    await asyncio.sleep(0.0001)
                await ws.send_json({
                    "message": "EOM",
                    "done": True,
                    "type": "eom",
                    'conv_k': conv_k,
                    "title": title,
                })
                await self.update_cache(username, who="nexus", prompt_or_response=self.his, conv_k=conv_k, terminal=False, care=care)
                cop = list(self.model_usage.items())
                for k, v in cop:
                    if k != name:
                        self.model_usage[k] -= 1
                return True
            for k, v in self.model_usage.items():
                if v > self.seuil:
                    await self.delete(k)
            return False
        except Exception as e:
            print("Erreur dans l'envoie de message : ", str(e))
            return False

async def handle_chat(data: dict, nexus_model: ChatNexus, terminal: bool = False, stream: bool = True, name: str = "qwen"):
    try:
        username = data["from"]
        question = data["question"]
        rag = data["rag"]
        care = data.get("care", False)
        terminal = data.get("terminal", terminal)
        success = await nexus_model.put_user_in_cache(username=username)
        print("Succès de la mise en cahe de l'user ", username, success)
        return await nexus_model.chat(username, question, rag=rag, terminal=terminal, stream=stream, name=name, care=care)
    except Exception as e:
        print("Erreur du chat : ", str(e))

if __name__ == "__main__":
    nexus = ChatNexus()
    try:
        # print(CACHE.get("chat_nexus").get("user1234"))
        # for k in CACHE:
        #     print(k)
        #     print(CACHE.get(k))
        #     input()
        while True:
            user = input("\n👤 Vous: ").strip()
            if user.lower() == 'quit':
                print("👋 Au revoir !")
                break
            print("🤖 Qwen: ", end="", flush=True)
            asyncio.run(nexus.chat("samuel", user, rag=False, terminal=True, name="gemma", conv_k="##new_conv##"))
            print()
    except Exception as e:
        print("Erreur : ", str(e))
        import traceback
        traceback.print_exc()