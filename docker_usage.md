# 📖 Guide d'utilisation — Nexus-Four

Nexus-Four est un assistant intelligent qui vous aide à étudier et prend soin de votre bien-être. Il fonctionne entièrement **hors ligne**, sans connexion internet.

---

## ✅ Prérequis

Vous avez besoin de **Docker** sur votre machine. Deux options selon votre niveau :

| Option | Pour qui | Lien |
|--------|----------|------|
| **Docker Desktop** | Débutants — interface graphique simple | [Télécharger](https://www.docker.com/products/docker-desktop/) |
| **Docker CLI** | Utilisateurs avancés — ligne de commande uniquement | [Installer](https://docs.docker.com/engine/install/) |

> Les deux options fonctionnent parfaitement avec ce guide. Toutes les commandes sont identiques.

---

## 📥 Télécharger l'image Docker

Avant de commencer, vous devez récupérer l'image de Nexus-Four. Deux méthodes selon votre choix :

### 🖥️ **Option A — Avec Docker Desktop (interface graphique)**

1. Ouvrez **Docker Desktop**
2. Allez dans l'onglet **"Images"**
3. Cliquez sur **"Pull"** en haut à droite
4. Dans la fenêtre qui s'ouvre, tapez : `hounsoubenny/nexus-four:v-1.0`
5. Cliquez sur **"Pull"** et attendez le téléchargement (environ 1,2 Go)

### ⌨️ **Option B — Avec Docker CLI (ligne de commande)**

Ouvrez un terminal et tapez simplement :

```bash
docker pull hounsoubenny/nexus-four:v-1.0
```

Vous verrez la progression du téléchargement. Une fois terminé, l'image est prête à être utilisée.

> ℹ️ L'image fait environ **1,2 Go à télécharger** (compressée) et prendra **1,7 Go** sur votre disque après extraction. Prévoir une connexion stable.

## 🚀 Première utilisation

### 1. Récupérer les fichiers nécessaires

Vous avez deux façons de faire :

**Option A — Téléchargement simple** *(recommandé si vous n'utilisez pas Git)*

Créez un dossier `~/nexus/` sur votre machine et téléchargez-y directement les fichiers suivants depuis le dépôt GitHub :

- **Linux / macOS** → téléchargez `docker-compose.yml`
- **Windows** → téléchargez `docker-compose.windows.yml`

Placez le fichier téléchargé dans `~/nexus/`.

**Option B — Cloner le dépôt** *(si vous utilisez Git)*

```bash
git clone https://github.com/hounsoubenny-cyber/nexus-four.git
cd nexus-four
```

### 2. Ouvrir un terminal dans le dossier

Si vous avez choisi l'option A, ouvrez un terminal dans `~/nexus/`.
Si vous avez choisi l'option B, vous êtes déjà dans le bon dossier.

### 3. Créer le fichier de configuration

Copiez-collez cette commande **une seule fois** :

**Linux / macOS :**
```bash
echo "HOST_UID=$(id -u)" > .env && echo "HOST_GID=$(id -g)" >> .env
```

**Windows (PowerShell) :**
```powershell
"HOST_UID=1000`nHOST_GID=1000" | Out-File -Encoding utf8 .env
```

### 4. Lancer l'application

**Linux / macOS :**
```bash
docker compose up -d
```

**Windows :**
```powershell
docker compose -f docker-compose.windows.yml up -d
```

Attendez environ **1 à 2 minutes**, puis ouvrez votre navigateur et accédez à :

👉 **http://localhost:8000**

---

## 📚 Base de connaissances — L'index

L'index est la base de connaissances que Nexus consulte pour répondre à vos questions. Il est construit à partir de vos documents PDF.

### 🎓 Vous êtes en L1 ? Bonne nouvelle !

Un index préconfiguré avec les cours de L1 est déjà inclus dans l'application. Vous n'avez rien à faire — Nexus est prêt à répondre à vos questions dès le premier lancement.

### Vous voulez ajouter vos propres documents ?

Si vous souhaitez enrichir la base avec vos propres PDFs :

**Étape 1 — Copiez vos PDFs dans le dossier docs :**
```bash
cp -r /chemin/vers/vos/cours/* ~/nexus/docs/
```

**Étape 2 — Construisez l'index :**
```bash
docker compose --profile index up index-builder
```

> ⏳ Attendez que la commande se termine avant d'utiliser l'application. Ne fermez pas le terminal pendant ce processus.

---

## 🔄 Passer en année supérieure — Mettre à jour la base de connaissances

Quand vous souhaitez remplacer les cours de l'année en cours par ceux de l'année suivante :

**1. Arrêter l'application**
```bash
docker compose down
```

**2. Sauvegarder l'ancien index** *(recommandé)*
```bash
cp -r ~/nexus/index ~/nexus/index_sauvegarde_L1
```

**3. Supprimer l'ancien index**
```bash
rm -rf ~/nexus/index/*
```

**4. Remplacer les anciens cours par les nouveaux**
```bash
rm -rf ~/nexus/docs/*
cp -r /chemin/vers/nouveaux/cours/* ~/nexus/docs/
```

**5. Reconstruire l'index**
```bash
docker compose --profile index up index-builder
```

**6. Relancer l'application**
```bash
docker compose up -d
```

> 💡 Pour revenir à l'ancien index, supprimez `~/nexus/index/` et remplacez-le par votre sauvegarde.

---

## 🛑 Arrêter l'application

```bash
docker compose down
```

## ▶️ Redémarrer l'application

```bash
docker compose up -d
```

---

## 🔍 Voir les logs

Les logs vous permettent de voir ce qui se passe à l'intérieur de l'application, utile en cas de problème.

**Voir les logs en direct :**
```bash
docker compose logs -f nexus
```

**Voir les logs de l'initialisation :**
```bash
docker compose logs init-dirs
```

Appuyez sur `Ctrl + C` pour quitter l'affichage des logs.

---

## 🤖 Utiliser un modèle plus puissant (optionnel)

Par défaut, Nexus embarque un modèle léger et rapide. Si vous souhaitez de meilleures réponses, vous pouvez utiliser un modèle plus puissant.

Les modèles disponibles sont hébergés sur Google Drive — **consultez le lien dans le README du projet**.

Une fois le modèle téléchargé (fichier `.gguf`) :

```bash
# Placez le fichier dans le dossier model
mv /chemin/vers/le/fichier.gguf ~/nexus/model/

# Puis redémarrez l'application
docker compose down && docker compose up -d
```

Nexus détectera automatiquement le nouveau modèle au démarrage.

> 💡 Vous pouvez télécharger un seul modèle ou plusieurs selon vos besoins. Chaque modèle offre un compromis entre vitesse et qualité des réponses — les détails sont précisés dans le README.

---

## ❓ Problèmes fréquents

**L'interface ne s'affiche pas sur http://localhost:8000**
Attendez 1 à 2 minutes après le lancement puis rafraîchissez la page. Vérifiez que Docker est bien démarré.

**Le container ne démarre pas**
Consultez les logs pour identifier le problème :
```bash
docker compose logs nexus
```

**L'index ne se construit pas**
Vérifiez que vous avez bien des fichiers PDF dans `~/nexus/docs/` avant de lancer la commande de construction.

**Problème de permissions sur Fedora / RHEL**
Le fichier `.env` gère cela automatiquement. Si le problème persiste :
```bash
sudo setsebool -P container_manage_cgroup true
```

**Le port 8000 est déjà utilisé**
Ouvrez le fichier `docker-compose.yml` et remplacez `"8000:8000"` par `"8080:8000"`. L'application sera alors accessible sur http://localhost:8080.

---

## 📁 Où sont stockées vos données ?

Toutes vos données sont dans le dossier `~/nexus/` sur votre machine. Elles vous appartiennent et ne sont jamais envoyées sur internet.

| Dossier | Contenu |
|---------|---------|
| `~/nexus/model/` | Modèles IA supplémentaires (optionnel) |
| `~/nexus/docs/` | Vos cours en PDF |
| `~/nexus/index/` | La base de connaissances |
| `~/nexus/uploads/` | Les fichiers envoyés via l'interface |
| `~/nexus/cache/` | Historique des conversations |
