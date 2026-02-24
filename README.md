# 🧠 NEXUS-FOUR
### L'Assistant IA Tout-en-Un pour Étudiants IFRI

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://hub.docker.com/r/hounsoubenny/nexus-four)
[![Version](https://img.shields.io/badge/Version-1.0-00C853?style=for-the-badge)]()
[![HackByIFRI](https://img.shields.io/badge/HackByIFRI-2026-FF6F00?style=for-the-badge)]()
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

> 🎓 **Transforme les défis académiques en succès estudiantin**  
> 100% hors ligne • 100% gratuit • 100% pour IFRI
> Fait par IFRI pour tout les étudiants
---

## 📑 Table des matières

- [💡 Le Problème](#-le-problème)
- [✨ Notre Solution](#-notre-solution)
- [🚀 Démarrage Rapide](#-démarrage-rapide)
- [📖 Fonctionnalités](#-fonctionnalités-détaillées)
- [🤖 Modèles IA](#-modèles-ia-disponibles)
- [💻 Utilisation](#-guide-dutilisation)
- [🏗️ Architecture](#-architecture-technique)
- [🔧 Dépannage](#-dépannage)
- [📡 API](#-api-endpoints)
- [🗺️ Roadmap](#-roadmap)
- [👥 Équipe](#-team-four--hackbyifri-2026)
- [🔗 Liens et demo ](#-liens-utiles)

---

## 💡 Le Problème

Les étudiants IFRI rencontrent quotidiennement ces défis :

### 📖 Manque d'aide personnalisée 24/7
Profs parfois occupés, pas toujours de connexion internet, besoin d'un assistant intelligent disponible à tout moment pour répondre aux questions sur les cours.

### 😰 Stress académique sans support
Pression des examens, charge de travail intense, mais aucun espace dédié au bien-être mental et à l'écoute empathique.

### 🎓 Pas de vitrine professionnelle
Difficile de valoriser ses compétences, projets et certificats auprès des recruteurs pour décrocher stages et emplois.

### 🤝 Manque d'espace d'échange
Aucune plateforme sécurisée pour vendre/acheter du matériel informatique (PC, souris, claviers...) entre étudiants de confiance.

---

## ✨ Notre Solution

**NEXUS-FOUR** regroupe 5 modules intelligents en une seule plateforme :

<table>
<tr>
<td width="20%" align="center">🧠<br><b>Brain</b></td>
<td width="80%">
<b>Assistant IA avec mémoire de tes cours</b><br>
Pose n'importe quelle question, l'IA répond avec les sources exactes de tes PDFs. Index L1 complet inclus. Génération de code Python/C/JS/SQL. 100% hors ligne.
</td>
</tr>
<tr>
<td align="center">💚<br><b>Care</b></td>
<td>
<b>Ton espace bien-être personnel</b><br>
Chatbot empathique pour parler de ton stress sans jugement. Tracker d'humeur rapide avec émojis. Confidentialité totale (données locales).
</td>
</tr>
<tr>
<td align="center">👤<br><b>Hub Skills</b></td>
<td>
<b>Portfolio professionnel en ligne</b><br>
Crée ton profil avec compétences, projets GitHub, certificats. URL unique partageable sur LinkedIn/CV. Export PDF automatique (bientôt).
</td>
</tr>
<tr>
<td align="center">💬<br><b>Messages</b></td>
<td>
<b>Communication temps réel</b><br>
Échange instantané avec d'autres étudiants (<100ms latence). Partage de fichiers. Notifications desktop.
</td>
</tr>
<tr>
<td align="center">🛍️<br><b>Marketplace</b></td>
<td>
<b>Vente de matériel informatique</b><br>
Achète/vends PC, souris, claviers, écrans entre étudiants IFRI. Photos, notation vendeurs, paiement Mobile Money.
<br>⚠️ <i>Vente de cours/exercices interdite (moralement incorrect)</i>
</td>
</tr>
</table>

---

## 🚀 Démarrage Rapide

### Prérequis

- **Docker 20.10+** ([Télécharger Docker Desktop](https://www.docker.com/products/docker-desktop/))
- **4 GB RAM** minimum
- **8 GB disque** libre
- Système : Windows, macOS ou Linux

### Installation en 3 étapes

#### **Étape 1 — Télécharger l'image Docker**

```bash
docker pull hounsoubenny/nexus-four:v-1.0
```

*⏳ Environ 1,2 Go à télécharger (connexion stable recommandée)*

#### **Étape 2 — Récupérer les fichiers de configuration**

**Option A** — Téléchargement direct (recommandé pour débutants)

1. Crée un dossier `~/nexus/` sur ta machine
2. Télécharge depuis [GitHub - nexus-four](https://github.com/hounsoubenny-cyber/nexus-four) :
   - **Linux/macOS** → `docker-compose.yml`
   - **Windows** → `docker-compose.windows.yml`
3. Place le fichier dans `~/nexus/`

**Option B** — Clone Git (pour développeurs)

```bash
git clone https://github.com/hounsoubenny-cyber/nexus-four.git
cd nexus-four
```

#### **Étape 3 — Lancer l'application**

**Linux / macOS :**

```bash
echo "HOST_UID=$(id -u)" > .env && echo "HOST_GID=$(id -g)" >> .env
docker compose up -d
```

**Windows (PowerShell) :**

```powershell
"HOST_UID=1000`nHOST_GID=1000" | Out-File -Encoding utf8 .env
docker compose -f docker-compose.windows.yml up -d
```

⏳ **Attends 1 à 2 minutes**, puis ouvre ton navigateur :

### ➡️ **http://localhost:8000**

---

### 📖 Besoin de plus de détails ?

Consulte le guide complet [`docker_usage.md`](./docker_usage.md) pour :
- Instructions détaillées pas à pas
- Ajouter tes propres cours PDF
- Utiliser des modèles IA plus puissants
- Résoudre les problèmes courants

---

## 📖 Fonctionnalités Détaillées

### 🧠 Brain — Assistant IA Intelligent

**Qu'est-ce que c'est ?**  
Un assistant qui connaît tous tes cours par cœur. Pose-lui une question, il trouve la réponse dans tes PDFs et te cite la source exacte.

**Fonctionnalités :**
- ✅ **Index L1 pré-construit** — Tous les cours de première année déjà indexés (rien à configurer !)
- ✅ **IA 100% hors ligne** — Fonctionne sans connexion internet
- ✅ **Recherche vectorielle FAISS** — Trouve les passages pertinents en millisecondes
- ✅ **Génération de code** — Python, C, JavaScript, SQL avec explications détaillées
- ✅ **Citations automatiques** — Chaque réponse indique le PDF source et le numéro de page
- ✅ **Mémoire conversationnelle** — Se souvient du contexte de la discussion
- 🔜 **Index L2/L3** — Bientôt disponibles pour les années supérieures (voir [`docker_usage.md`](./docker_usage.md) pour créer soit même)

**Exemple d'utilisation :**
```
Toi : Explique-moi les pointeurs en C avec un exemple

Brain : Les pointeurs en C sont des variables qui stockent 
l'adresse mémoire d'une autre variable...

[Code exemple fourni]

📚 Source : Cours_C_Avance.pdf (page 42)
```

---

### 💚 Care — Espace Bien-être

**Qu'est-ce que c'est ?**  
Un espace sûr pour parler de ton stress académique avec une IA empathique, sans jugement.

**Fonctionnalités :**
- ✅ **Chatbot bienveillant** — Parle librement de tes préoccupations, anxiété, surcharge
- ✅ **Tracker d'humeur rapide** — Note ton état en un clic avec des émojis (😊 😐 😢 😰 😡)
- ✅ **IA empathique** — Réponses adaptées à ton ressenti émotionnel
- ✅ **Confidentialité absolue** — Tes conversations restent sur ta machine, jamais envoyées sur internet
- ✅ **Disponible 24/7** — Parle quand tu en as besoin, même à 3h du matin

**Cas d'usage :**
- Gérer le stress des examens
- Parler de la charge de travail
- Trouver des techniques de relaxation
- Obtenir du soutien en période difficile

---

### 👤 Hub Skills — Portfolio Professionnel

**Qu'est-ce que c'est ?**  
Ta vitrine en ligne pour impressionner recruteurs et entreprises avec tes compétences et projets.

**Fonctionnalités :**
- ✅ **Profil complet** — Photo, bio, compétences techniques (langages, frameworks...)
- ✅ **Gestion de certificats** — Upload tes certifications avec images/PDFs
- ✅ **Portfolio projets** — Ajoute liens GitHub, démo live, screenshots, descriptions
- ✅ **URL partageable unique** — `http://nexus.local/hub/tonpseudo` à mettre sur LinkedIn/CV
- ✅ **Design professionnel** — Interface moderne qui met en valeur ton profil
- 🔜 **Export CV PDF** — Génération automatique de CV depuis ton profil

**Pourquoi c'est important ?**  
Les recruteurs veulent voir tes réalisations concrètes, pas juste une liste de compétences. Avec Hub Skills, tu prouves ce que tu sais faire ! Et tes amis puvent te demander des services

---

### 💬 Messages — Communication Temps Réel

**Qu'est-ce que c'est ?**  
Un système de messagerie instantanée entre étudiants, rapide et fiable.

**Fonctionnalités :**
- ✅ **Chat WebSocket** — Latence ultra-faible (<100ms), messages instantanés
- ✅ **Partage de fichiers** — Envoie PDFs, images, code directement dans la conversation
- ✅ **Notifications desktop** — Reçois des alertes quand quelqu'un t'écrit
- ✅ **Historique complet** — Retrouve toutes tes conversations passées
- ✅ **Recherche utilisateurs** — Trouve facilement tes camarades de promo

**Cas d'usage :**
- Entraide sur un exercice difficile
- Partage de ressources de cours
- Organisation de groupes de travail
- Demander des conseils à des L2/L3
- Commmuniquer avec des client potentiels sur Marketplace
- Commniquer avec tes amis qui demandent tes services sur Hub Skills

---

### 🛍️ Marketplace — Matériel Informatique

**Qu'est-ce que c'est ?**  
Une plateforme d'achat/vente de matériel informatique entre étudiants IFRI de confiance.

**Fonctionnalités :**
- ✅ **Listings détaillés** — Crée des annonces avec titre, description, prix, état
- ✅ **Upload photos** — Jusqu'à 5 images par produit
- ✅ **Catégories** — PC portables, souris, claviers, écrans, composants...
- ✅ **Système de notation** — Rate les vendeurs pour garantir la qualité
- ✅ **Paiement Mobile Money** — Intégration simulée (MTN, Moov, Flooz...)
- ✅ **Dashboard vendeur** — Gère toutes tes annonces en un seul endroit
- 🚧 **Recherche avancée** — Filtres par prix, état, catégorie (en développement)

**⚠️ Règle importante :**  
La vente de **cours, exercices corrigés, examens** est interdite sur la plateforme. C'est moralement incorrect et contraire à l'esprit d'entraide académique.

**Ce que tu peux vendre :**
- ✅ Ordinateurs portables
- ✅ Souris, claviers, écouteurs
- ✅ Écrans, webcams
- ✅ Composants (RAM, SSD, cartes graphiques...)
- ✅ Livres techniques (physiques)

---

## 🤖 Modèles IA Disponibles

Par défaut, Nexus embarque **Tiny** (un modèle Gemma léger de 700 MB) pour fonctionner immédiatement.

Pour des **réponses plus intelligentes et précises**, tu peux télécharger des modèles plus puissants :

| Modèle | Taille | Meilleur pour | Performance | Recommandé |
|--------|--------|---------------|-------------|------------|
| **Tiny** *(inclus par défaut)* | 700 MB | Tests rapides, démos | ⭐⭐⭐ | Débutants |
| **Qwen 2.5 Instruct (3B)** | 2.1 GB | Conversations naturelles, explications claires | ⭐⭐⭐⭐⭐ | **Recommandé pour tous, tâche standard** |
| **Phi-3.5 Mini Instruct** | 2.4 GB | Analyse technique, génération de code | ⭐⭐⭐⭐⭐ | **Recommandé pour tous, tâche ou reflexion complexe** |
| **Gemma 2 Instruct (2B)** | 1.6 GB | Réponses créatives, Care empathique | ⭐⭐⭐⭐ | Bien-être et réponses rapides |

### 📥 Télécharger les modèles

**Lien Google Drive :** [https://drive.google.com/drive/folders/1dMfF8h54zyKeSEQLq4mNDjvkMn-8H8CF](https://drive.google.com/drive/folders/1dMfF8h54zyKeSEQLq4mNDjvkMn-8H8CF)

### 🔧 Comment installer un modèle

1. Télécharge le fichier `.gguf` depuis le Drive
2. Suis les instructions dans [`docker_usage.md`](./docker_usage.md) section **"Utiliser un modèle plus puissant"**

### 💡 À savoir

- **Nexus a été conçu** avec les modèles **Qwen**, **Phi** et **Gemma** 
- **Tiny** est juste un modèle par défaut pour démarrage rapide
- Pour utiliser d'autres modèles, consulte [`docker_usage.md`](./docker_usage.md)

### ⚠️ Limitation technique

**Seuls les modèles du Google Drive** sont garantis compatibles avec Nexus. 

Ajouter d'autres modèles (depuis Hugging Face par exemple) nécessite de **modifier le code source Python backend** — c'est complexe pour quelqu'un qui ne maîtrise pas Python et l'architecture de l'app.

---

## 💻 Guide d'Utilisation

### 🎓 Configuration selon ton niveau

#### **Tu es en L1 ?** ✅ Prêt à l'emploi !

L'index des cours de L1 est **déjà inclus dans sur le repôt, télécharger juste c'est dans [`ici`](./conversation_app/chat_nexus/index)**. Tu n'as rien à configurer !

✅ Tous les cours de première année sont indexés  
✅ Pose tes questions dès le premier lancement  
✅ Aucune manipulation technique requise

#### **Tu es en L2/L3, plus ou même dans une autre filière  ?** 📚 Personnalise ton index

Tu peux construire un index avec **tes propres cours PDF** :

📖 Consulte [`docker_usage.md`](./docker_usage.md) section **"Vous voulez ajouter vos propres documents ?"**

Tu pourras :
- Ajouter les PDFs de ta promo
- Reconstruire l'index automatiquement
- Avoir un Brain adapté à ton niveau

---

### 🧠 Utiliser Brain

**1. Crée ton compte**
- Va sur http://localhost:8000
- Clique "S'inscrire"
- Remplis le formulaire

**2. Pose une question**
- Accède à l'onglet **Brain**
- Tape ta question (ex: *"Comment fonctionnent les listes chaînées en C ?"*)
- Appuie sur Entrée

**3. Reçois la réponse**
- L'IA analyse tes cours
- Te donne une réponse complète avec explications
- Cite les sources exactes (PDF + numéro de page)

**Exemples de questions :**
```
💡 Explique-moi la différence entre malloc et calloc
💡 Donne-moi un exemple de fonction récursive en C
💡 Comment créer une base de données SQL ?
💡 Écris un programme Python pour trier une liste
💡 Quelle est la complexité de l'algorithme de tri rapide ?
```

---

### 💚 Utiliser Care

**1. Accède à Care**
- Clique sur l'onglet **Care**

**2. Note ton humeur (optionnel)**
- Clique sur un émoji : 😊 😐 😢 😰 😡
- Ça prend 2 secondes !

**3. Parle au chatbot**
- Tape ce qui te tracasse
- L'IA répond avec empathie
- Pas de jugement, confidentialité garantie

**Exemples de discussions :**
```
💬 Je stresse pour mes examens de demain
💬 J'ai trop de travail, je ne sais pas par où commencer
💬 Je me sens seul(e) et dépassé(e)
💬 Comment gérer la pression académique ?
```

---

### 👤 Créer ton Hub Skills

**1. Configure ton profil**
- Va dans **Hub Skills**
- Upload une photo pro
- Écris une bio accrocheuse (2-3 phrases)

**2. Ajoute tes compétences**
- Liste tes langages : Python, C, JavaScript...
- Tes frameworks : React, Django, Flask...
- Tes outils : Git, Docker, VS Code...

**3. Ajoute tes projets**
- Titre du projet
- Description claire (problème résolu, technologies)
- Lien GitHub / démo live
- Screenshots

**4. Upload tes certificats**
- Formations suivies (Udemy, Coursera...)
- Hackathons gagnés
- Certifications officielles

**5. Partage ton profil**
- Ton URL unique : `http://nexus.local/hub/tonpseudo`
- Ajoute-la sur ton CV
- Partage-la sur LinkedIn

---

### 💬 Échanger via Messages

**1. Trouve un étudiant**
- Va dans **Messages**
- Utilise la barre de recherche
- Tape le nom ou pseudo

**2. Lance une conversation**
- Clique sur le contact
- Tape ton message
- Envoie des fichiers si besoin

**3. Reçois des notifications**
- Active les notifications desktop (navigateur)
- Sois alerté instantanément des nouveaux messages

---

### 🛍️ Vendre sur Marketplace

**1. Crée une annonce**
- Va dans **Marketplace**
- Clique "Vendre un article"

**2. Remplis les infos**
- Titre accrocheur
- Description honnête (état, défauts éventuels)
- Prix en FCFA
- Catégorie (PC, Souris, Clavier...)

**3. Upload des photos**
- Ajoute une photo claire de ton produit (optionnel)

**4. Publie**
- Clique "Ajouter" et ajoute le produit

**Tips pour vendre vite :**
- Prix honnête (compare avec le marché)
- Photos de qualité
- Description complète et transparente
- Réponds vite aux messages

---

## 🏗️ Architecture Technique

### Stack Frontend

- **React 18.3** — Bibliothèque UI moderne
- **WebSocket** — Communication temps réel
- **CSS Glassmorphism** — Design moderne et élégant
- **Responsive mobile-first** — Fonctionne sur tous écrans

### Stack Backend

- **FastAPI** — Framework Python performant
- **Python 3.11** — Langage backend
- **llama.cpp** — Inférence IA optimisée CPU
- **JWT + bcrypt** — Authentification sécurisée

### IA & Données

- **FAISS** — Recherche vectorielle ultra-rapide
- **Sentence-Transformers** — Embeddings de qualité
- **Modèles GGUF** — Format optimisé pour CPU
- **DiskCache** — Cache persistant des conversations

### Infrastructure

- **Docker multi-stage** — Builds optimisés
- **Volumes persistants** — Données sauvegardées
- **Init containers** — Configuration automatique

### Schéma d'architecture

```
┌─────────────────────────────────────────────────────┐
│                   UTILISATEUR                        │
│              (Navigateur Web)                        │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP / WebSocket
                       ↓
┌─────────────────────────────────────────────────────┐
│                  FRONTEND (React)                    │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌──────────┐  │
│  │ Brain  │  │  Care  │  │  Hub   │  │ Messages │  │
│  └────────┘  └────────┘  └────────┘  └──────────┘  │
└──────────────────────┬──────────────────────────────┘
                       │ API REST / WebSocket
                       ↓
┌─────────────────────────────────────────────────────┐
│               BACKEND (FastAPI)                      │
│  ┌──────────────────────────────────────────────┐   │
│  │           RAG Engine (Brain)                 │   │
│  │  ┌──────────┐  ┌──────────┐  ┌───────────┐  │   │
│  │  │  FAISS   │→ │   LLM    │→ │ Response  │  │   │
│  │  │ Vectoriel│  │ Manager  │  │ Generator │  │   │
│  │  └──────────┘  └──────────┘  └───────────┘  │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ Care Chat  │  │   Hub API   │  │  Messages   │  │
│  └────────────┘  └─────────────┘  └─────────────┘  │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │        Marketplace API                         │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────┐
│              STOCKAGE (Volumes)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │  Model   │  │  Index   │  │  Cache   │          │
│  │  (GGUF)  │  │ (FAISS)  │  │  (Disk)  │          │
│  └──────────┘  └──────────┘  └──────────┘          │
│                                                      │
│  ┌──────────┐  ┌──────────┐                         │
│  │  Uploads │  │   Docs   │                         │
│  │ (Files)  │  │  (PDFs)  │                         │
│  └──────────┘  └──────────┘                         │
└─────────────────────────────────────────────────────┘
```

---

## 📡 API Endpoints

Documentation interactive complète : **http://localhost:8000/docs** (Swagger UI)

### Authentification

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/signup` | Créer un compte utilisateur |
| `POST` | `/login` | Se connecter ou créer un compte (reçoit token JWT) |
| `GET` | `/get_salt` | Obtenir un `salt` utiliser pour le chiffrelent de vos données et pour le token JWT|

### Brain (RAG)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/chat` | Poser une question au RAG |


### Care (Bien-être)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/care` | Discuter avec l'IA empathique |

### Hub Skills (Portfolio)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/hub` | Ajouter une compétence, un projet ou dss infos, voir ses compétences|

### Messages (Chat)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `WS` | `/ws` | WebSocket connexion chat |

### Marketplace

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/marketplace` | Ajouter ou voir ses produits |

---

## 📁 Structure du Projet

```
nexus-four/
│
├── 📂 frontend/                          # Interface utilisateur React
│   └── 📂 REACT/
│       └── 📂 build/                     # Build de production (généré automatiquement)
│           ├── 📄 asset-manifest.json  
│           ├── 📄 favicon.ico             # Icône du site
│           ├── 📄 index.html              # Page HTML principale
│           ├── 📄 logo192.png             
│           ├── 📄 logo512.png             
│           ├── 📄 manifest.json           
│           ├── 📄 robots.txt              # Règles pour les robots
│           └── 📂 static/                 
│               ├── 📂 css/                  # Styles CSS
│               │   ├── 📄 main.e7613c46.css
│               │   └── 📄 main.e7613c46.css.map
│               └── 📂 js/                   # JavaScript compilé
│                   ├── 📄 453.231d97de.chunk.js
│                   ├── 📄 453.231d97de.chunk.js.map
│                   ├── 📄 main.6a705f10.js
│                   ├── 📄 main.6a705f10.js.LICENSE.txt
│                   └── 📄 main.6a705f10.js.map
│
├── 📂 conversation_app/                   # Application backend principale
│   ├── 📄 auth_jwt.py                     # Authentification JWT
│   ├── 📄 chiffrement.py                   # Utilitaires de chiffrement
│   ├── 📄 config.py                        # Configuration globale
│   ├── 📄 limiter.py                       # Rate limiting
│   ├── 📄 llm_test.py                      # Tests pour les modèles LLM
│   ├── 📄 main.py                          # Point d'entrée FastAPI
│   ├── 📄 requirements.txt                  # Dépendances Python principales
│   ├── 📄 requirements2.txt                 # Dépendances secondaires
│   ├── 📄 router.py                         # Routes API
│   ├── 📄 run_api.py                        # Script de lancement
│   ├── 📄 test_ws.py                        # Tests WebSocket
│   ├── 📄 utils_cnv.py                      # Utilitaires divers
│   ├── 📄 websocket_class.py                # Gestion WebSocket
│   ├── 📄 websocket_router.py               # Routes WebSocket
│   │
│   ├── 📂 chat_nexus/                       # Moteur de chat intelligent
│   │   ├── 📄 chat.py                        # Logique principale du chat
│   │   ├── 📄 context_getter.py               # Récupération de contexte RAG
│   │   │
│   │   ├── 📂 Bash/                           # Scripts utilitaires bash
│   │   │   ├── 📄 classer_documents.sh         # Organisation documents
│   │   │   ├── 📄 detecter_doublons.sh         # Détection de doublons
│   │   │   ├── 📄 show_files.sh                 # Affichage fichiers
│   │   │   └── 📄 supprimer_doublons.sh        # Nettoyage doublons
│   │   │
│   │   ├── 📂 index/                           # Index FAISS vectoriel
│   │   │   ├── 📄 index.faiss                  # Vecteurs FAISS
│   │   │   └── 📄 index.pkl                     # Métadonnées index
│   │   │
│   │   └── 📂 PROMPTS/                         # Prompts système
│   │       ├── 📄 promp.txt                     # Prompt générique
│   │       │
│   │       ├── 📂 brain_sys_prompt/             # Prompts pour le mode Brain (RAG)
│   │       │   ├── 📄 system12.md                # Version compacte
│   │       │   ├── 📄 system12_.md               # Variante
│   │       │   ├── 📄 system13.md                # Version détaillée
│   │       │   ├── 📄 system_full1.md            # Version complète
│   │       │   └── 📄 system.md                   # Prompt principal
│   │       │
│   │       └── 📂 care_sys_prompt/              # Prompts pour le mode Care (bien-être)
│   │           ├── 📄 system_prompt_care.md      # Prompt bien-être
│   │           └── 📄 system_prompt_care_.md     # Variante
│   │
│   └── 📂 hub_manager/                          # Gestionnaire Hub Skills
│       └── 📄 hub_manager.py                     # Logique du portfolio
│
├── 📄 docker-compose.yml                         # Orchestration Linux/macOS
├── 📄 docker-compose.windows.yml                 # Orchestration Windows
├── 📄 Dockerfile                                 # Build multi-stage
├── 📄 docker_usage.md                            # Guide Docker détaillé
├── 📄 README.md                                   # Présentation projet
├── 📄 LICENSE                                     # Licence (MIT)
└── 📄 .gitignore                                  # Fichiers ignorés Git
```

---

## 🔧 Dépannage

Pour **tous les problèmes techniques**, consulte d'abord le guide [`docker_usage.md`](./docker_usage.md) section **"Problèmes fréquents"**.

### ⚡ Solutions rapides

#### ❌ L'interface ne charge pas sur http://localhost:8000

**Solution :**
1. Attends **1 à 2 minutes** après `docker compose up -d`
2. Rafraîchis la page (`Ctrl + R` ou `Cmd + R`)
3. Vérifie que Docker est bien démarré

**Toujours pas ?** Vérifie les logs :
```bash
docker compose logs -f nexus
```

---

#### ❌ Le port 8000 est déjà utilisé

**Solution :**
1. Ouvre `docker-compose.yml`
2. Change la ligne `"8000:8000"` en `"8080:8000"`
3. Relance : `docker compose down && docker compose up -d`
4. Accède à http://localhost:8080

---

#### ❌ Le container ne démarre pas

**Solution :**
```bash
# Voir les logs d'erreur
docker compose logs nexus

# Voir tous les logs
docker compose logs
```

Souvent lié à :
- Ports déjà utilisés
- Problèmes de permissions (Linux)
- Volumes corrompus

---

#### ❌ L'index ne se construit pas

**Vérifie que :**
1. Tu as bien des PDFs dans `~/nexus/docs/`
2. Tu as lancé la bonne commande :
```bash
docker compose --profile index up index-builder
```

**Voir la progression :**
```bash
docker compose logs -f index-builder
```

---

#### ❌ Problème de permissions (Linux/Fedora/RHEL)

Le fichier `.env` gère normalement ça automatiquement.

**Si ça persiste :**
```bash
sudo setsebool -P container_manage_cgroup true
```

---

### 🆘 Besoin d'aide ?

Si ton problème n'est pas listé ici :

1. 📖 Consulte [`docker_usage.md`](./docker_usage.md)
2. 📋 Copie les logs : `docker compose logs nexus > logs.txt`
3. 📧 Contacte l'équipe avec les logs (voir section [Liens](#-liens-utiles))

---

## 🗺️ Roadmap

### ✅ Version 1.0 (Actuelle — Février 2026)

**Brain**
- ✅ RAG avec index L1 pré-construit
- ✅ 4 modèles IA disponibles
- ✅ Génération de code
- ✅ Citations sources automatiques

**Care**
- ✅ Chatbot empathique
- ✅ Tracker d'humeur avec émojis

**Hub Skills**
- ✅ Profil complet
- ✅ Portfolio projets
- ✅ Upload certificats
- ✅ URL publique partageable

**Messages**
- ✅ Chat temps réel WebSocket
- ✅ Partage fichiers
- ✅ Notifications desktop

**Marketplace**
- ✅ Annonces avec photos
- ✅ Système de notation
- ✅ Dashboard vendeur
- ✅ Paiement Mobile Money (mock)

---

### 🚧 Version 1.1 (En cours)

**Marketplace**
- 🚧 Route de recherche avancée
- 🚧 Filtres par prix/catégorie/état
- 🚧 Système de favoris

**Brain**
- 🚧 Index L2 (cours deuxième année)
- 🚧 Index L3 (cours troisième année)
- 
**Hub Skills**
- 🚧 Export CV PDF automatique
- 🚧 Thèmes de profil personnalisables
- 🚧 Intégration LinkedIn pour import profil

**Messages**
- 🚧 Appels audio/vidéo
- 🚧 Groupes de discussion
- 🚧 Partage d'écran pour pair programming

---

### 🔮 Version 2.0 (Futur)

**Mobile**
- 📱 Application mobile (React Native)
- 📱 Notifications push
- 📱 Mode offline complet

**Intégrations**
- 🔗 Calendrier IFRI (emplois du temps)
- 🔗 Système de notes IFRI
- 🔗 Bibliothèque numérique IFRI

**Collaboration**
- 👥 Notes de cours partagées (mode collaboratif)
- 👥 Groupes d'étude virtuels
- 👥 Tuteurs étudiants (L3 aide L1)

**IA Avancée**
- 🤖 Modèles spécialisés par matière
- 🤖 Génération d'exercices personnalisés
- 🤖 Correction automatique de code
- 🤖 Détection de plagiat dans projets

**Analytics**
- 📊 Statistiques d'apprentissage personnelles
- 📊 Prédiction de notes basée sur progression
- 📊 Recommandations de révisions ciblées

---

## 👥 Team FOUR — HackByIFRI 2026

<table>
<tr>
<td align="center">
<img src="https://github.com/identicons/user1.png" width="100px;" alt="Samuel HOUNSOU"/><br />
<sub><b>Samuel HOUNSOU</b></sub><br />
<a href="https://github.com/hounsoubenny-cyber">GitHub</a> • <a href="mailto:hounsoutchegnon@gmail.com">Email</a>
</td>
<td align="center">
<img src="https://github.com/identicons/user2.png" width="100px;" alt="Léoncelle GBESSEMEEHLAN"/><br />
<sub><b>Léoncelle GBESSEMEEHLAN</b></sub><br />
<a href="#">GitHub</a> • <a href="mailto:leoncelle.gb@gmail.com">Email</a>
</td>
<td align="center">
<img src="https://github.com/identicons/user3.png" width="100px;" alt="ADEBOYE-SENAN Christ-Emile"/><br />
<sub><b>ADEBOYE-SENAN Christ-Emile</b></sub><br />
<a href="#">GitHub</a> • <a href="mailto:emileadeboye2@gmail.com">Email</a>
</td>
<td align="center">
<img src="https://github.com/identicons/user4.png" width="100px;" alt="HOUNSOUNNOU Ruth"/><br />
<sub><b>HOUNSOUNNOU Ruth</b></sub><br />
<a href="#">GitHub</a> • <a href="mailto:hounsounnouruth@gmail.com">Email</a>
</td>
</tr>
</table>

---

### 💖 Remerciements

Un grand merci à :
- **L'IFRI** pour nous avoir formés et accueilli ce hackathon
- **Nos profs** qui nous ont donné les bases techniques
- **La communauté étudiante** qui a inspiré ce projet
- **Les testeurs bêta** qui nous ont aidés à améliorer l'app

> 🎓 **Fait avec passion pour la communauté étudiante IFRI**

---


## 🔗 Liens Utiles

### 📦 Téléchargements

- 🐳 **Docker Hub** : [hounsoubenny/nexus-four](https://hub.docker.com/r/hounsoubenny/nexus-four)
- 💾 **Modèles IA** : [Google Drive](https://drive.google.com/drive/folders/1dMfF8h54zyKeSEQLq4mNDjvkMn-8H8CF?usp=sharing)
- 📂 **Code Source** : [GitHub - nexus-four](https://github.com/hounsoubenny-cyber/nexus-four)

### 📖 Documentation

- 📘 **Guide Docker** : [`docker_usage.md`](./docker_usage.md)
- 📗 **API Documentation** : http://localhost:8000/docs (après installation)
- 📕 **Vidéo de DÉMO** : [ici, sur you tube](https://youtube) 

### 💬 Contact & Support

- 📧 **Email** : Un des email ci-dessus
- 🐛 **Bugs** : [GitHub Issues](https://github.com/hounsoubenny-cyber/nexus-four/issues)
- 💡 **Suggestions** : [GitHub Discussions](https://github.com/hounsoubenny-cyber/nexus-four/discussions)

---

<div align="center">

### ⭐ Si ce projet t'aide, laisse une étoile sur GitHub !

### 🚀 Propulsé par la passion de la communauté étudiante IFRI

---

**Nexus-Four** • Version 1.0 • HackByIFRI 2026  
*Made with ❤️ in Cotonou, Benin 🇧🇯*

</div>
