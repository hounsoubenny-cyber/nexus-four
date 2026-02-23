#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 13:01:39 2026

@author: hounsousamuel
"""

import os, sys, asyncio, nest_asyncio
sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.join(__file__, "..", ".."))))
from conversation_app.config import CONTEXT_GETTER_CONFIG, IMG_EXTENSIONS
from langchain_community.document_loaders import (
    PyPDFLoader, 
    DirectoryLoader, 
    CSVLoader, 
    TextLoader, 
    BSHTMLLoader,
    Docx2txtLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS, DistanceStrategy


class ContextGetter:
    def __init__(
            self,
            path:str,
            embed_path_or_name:str,
            docs_path:str|None="",
            chunk_size:int=500, 
            overlap:int=50,
            seps:list=["\n\n", "\n", ".","?", "!", " "],
            top_k:int=3
        ):
        self.path = path
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.seps = seps
        self.vector_database = None
        self.docs_path = docs_path
        self.embed_path_or_name = embed_path_or_name
        self.embed = HuggingFaceEmbeddings(
            model_name=self.embed_path_or_name,
            model_kwargs={
                "device": "cpu",
                "trust_remote_code": True, 
            },
            encode_kwargs={
                "normalize_embeddings": True,
                "batch_size": 128,
            }
        )
        self.text_spliter = None
        self.top_k = top_k
        self.directory_loader = DirectoryLoader(
            path=self.docs_path,
            glob="**/*",
            loader_cls=self._get_loader,
            recursive=True,
            silent_errors=True,
            use_multithreading=True,
            show_progress=True,
            max_concurrency=8,
            exclude=['.pka', '.pkt', '.exe', '.bin', '.zip', ".mp3", ".eml", ".pptx", *IMG_EXTENSIONS, *[p.upper() for p in IMG_EXTENSIONS]]
            )
        if path:
            try:
                self.vector_database = FAISS.load_local(
                    self.path, 
                    self.embed, 
                    allow_dangerous_deserialization=True
                )
                print(f"✅ Base chargée depuis {path}")
            except Exception as e:
                print(f"⚠️ Erreur chargement: {e}")
                self.prepare_database()
        else:
            print("🔄 Création nouvelle base...")
            raise ValueError("Arguments invalides !")
    
    def _get_loader(self, file_path:str, **kwargs):
        # print("FILE : ", file_path)
        if not file_path:
            return 
        ext = os.path.splitext(file_path)[-1].lower() 
        try:
           if ext == ".pdf":
               return PyPDFLoader(file_path=file_path)
           elif ext in (".md", ".txt", ".text", ".py", ".java", ".cpp", ".h"):
               return TextLoader(file_path=file_path, encoding="utf-8")
           elif ext == ".docx":
               return Docx2txtLoader(file_path=file_path)
           elif ext == ".csv":
               return CSVLoader(file_path=file_path)
           elif ext == ".html":
               return BSHTMLLoader(file_path=file_path)
           elif ext in (".jpg", ".jpeg", ".png", ".gif"):
               return None  
           return None
        except Exception as e:
            print(f"⚠️ Erreur avec {file_path}: {e}")
            return None
    
    def _chunk(self, do:bool=False):
        if not self.text_spliter:
            self.text_spliter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.overlap,
                separators=self.seps
                )
        if do:
            if self.docs_path and os.path.exists(self.docs_path):
                docs = self.directory_loader.load()
                if docs:
                    return self.text_spliter.split_documents(docs)
                else:
                    raise ValueError("Aucun document trouvé !")
            raise ValueError("Chemin docs requis ou invalide !")
        return []
    
    
    def prepare_database(self):
        print("🔄 Création de la base...")
        chunks = self._chunk(True)
        chunk_size = 200
        total_chunks = len(chunks)
        total = total_chunks // chunk_size + bool(len(chunks) % chunk_size)
        num = 0
                
        for i in range(0, total_chunks, chunk_size):
            chunk = chunks[i : i + chunk_size]
            print(f"📦 Batch {num}/{total} ({total_chunks} chunks au total, chunk_size={len(chunk)})")
            if i == 0:
                if self.vector_database is None:
                    self.vector_database = FAISS.from_documents(chunk, self.embed)
            else:
                self.vector_database.add_documents(chunk)
            
            if num % 5 == 0:
                print("   💾 Sauvegarde...")
                os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
                self.vector_database.save_local(self.path)
                print("   ✅ Sauvegardé")
                
            num += 1
        
        print("✅ Index créé en mémoire, taille =", len(self.vector_database.docstore._dict), "docs")
        print("Sauvegarde en cours vers :", self.path)
        self.vector_database.save_local(self.path)      
    
    def get_context(self, text:str):
        self.vector_database.distance_strategy = DistanceStrategy.COSINE
        output = self.vector_database.similarity_search(text, k=self.top_k, )
        context = ""
        sources = set()
        spliter = "\\" if os.name == "nt"  else "/"
        for doc in output:
            context += f"\n{'=' * 50}"
            context += f"\n{doc.page_content}"
            source = str(doc.metadata.get("source", "Source Inconnue")).split(spliter)[-1]
            sources.add(source)
            context += f"\n##### Source : {source} ######"
            
        return context, list(sources)
    
    async def add_docs(self, path:str, add=True):
        try:
            cop = self.docs_path
            if os.path.exists(path):
                self.docs_path = path
                if not add:
                    self.vector_database = None
                await self.prepare_database()
                self.docs_path = cop
                return True
            return False
        except Exception as e:
            print("Erreur add : ", str(e))
            return False
        
if __name__ == "__main__":
    def test_context_getter():
        print("="*60)
        print("🔍 TEST DU CONTEXTGETTER")
        print("="*60)
        
        # 1. Initialisation
        print("\n1️⃣  Initialisation du ContextGetter...")
        cg = ContextGetter(**CONTEXT_GETTER_CONFIG)
        
        # 2. Test de recherche
        print("\n2️⃣  Test de recherche avec 'réseau informatique'...")
        queries = [
            "réseau informatique",
            "programmation Python",
            "intelligence artificielle",
            "sécurité réseau",
            "base de donné SQL"
        ]
        
        for query in queries:
            print(f"\n📝 Requête: '{query}'")
            context, sources = cg.get_context(query)
            
            print(f"📄 Contexte trouvé: {len(context)} caractères")
            print(f"📁 Sources: {sources if sources else 'Aucune'}")
            
            # Affiche un extrait du premier résultat
            if context and len(context) > 0:
                preview = context[:] #+ "..." if len(context) > 200 else context
                print(f"📋 Extrait: {preview}")
        
        # 3. Statistiques
        print("\n" + "="*60)
        print("✅ TEST TERMINÉ")
        print("="*60)
    
    test_context_getter()
