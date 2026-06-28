# 🎓 Plateforme d'Apprentissage Adaptative — EdTech SaaS IA

> **Projet de Fin d'Études (PFE) 2025–2026**  
> Plateforme SaaS intelligente pour l'apprentissage personnalisé du développement web (HTML, CSS, JavaScript) propulsée par l'Intelligence Artificielle.

---

## 📋 Table des Matières

1. [Présentation du Projet](#-présentation-du-projet)
2. [Architecture Technique](#-architecture-technique)
3. [Prérequis Système](#-prérequis-système)
4. [Installation — Backend](#-installation--backend)
5. [Installation — Frontend](#-installation--frontend)
6. [Configuration de la Base de Données](#-configuration-de-la-base-de-données)
7. [Lancement du Projet](#-lancement-du-projet)
8. [Structure des Dossiers](#-structure-des-dossiers)
9. [Base de Données](#-base-de-données)
10. [Endpoints API](#-endpoints-api)
11. [Modèles IA](#-modèles-ia)
12. [Dépannage](#-dépannage)
13. [Commandes Utiles](#-commandes-utiles)

---

## 🎯 Présentation du Projet

### Contexte

Plateforme EdTech innovante utilisant l'Intelligence Artificielle pour personnaliser l'apprentissage du développement web (HTML, CSS, JavaScript) à travers des modalités multimodales (texte, audio, vidéo).

### Fonctionnalités Principales

| Fonctionnalité | Technologie IA |
|---|---|
| Recommandation du mode d'apprentissage optimal | Random Forest |
| Génération de quiz adaptatifs | BERT / paraphrase-multilingual-MiniLM-L12-v2  |
| Recherche vocale intelligente | OpenAI Whisper + NLP |
| Prédiction et prévention du décrochage | Sequential Pattern Mining |
| Apprentissage multimodal | Texte, Audio, Vidéo |

### Stack Technologique

| Couche | Technologies |
|---|---|
| **Frontend** | ReactJS 19, TypeScript, TailwindCSS 3, Vite 8 |
| **Backend** | FastAPI, Python 3.11, SQLAlchemy 2, Alembic |
| **Base de Données** | PostgreSQL 15 |
| **IA / ML** | PyTorch 2.1, Transformers 4.36, Scikit-learn 1.3, Sentence-Transformers |
| **Reconnaissance Vocale** | OpenAI Whisper |
| **LLM** | BERT / paraphrase-multilingual-MiniLM-L12-v2 |

---

## 🏗️ Architecture Technique

```
┌─────────────────────────────────────────────────────────────────┐
│                         UTILISATEUR                             │
│               Web / Mobile / Audio / Texte / Vidéo              │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼─────────────────────────────────┐
│                      FRONTEND — ReactJS 19                      │
│               Interface Adaptative / TailwindCSS 3              │
└─────────────────────────────┬─────────────────────────────────┘
                              │ HTTP / REST
┌─────────────────────────────▼─────────────────────────────────┐
│                      BACKEND — FastAPI                          │
│              API RESTful / WebSockets / JWT Auth                │
└──────────────┬────────────────────┬───────────────┬───────────┘
               │                    │               │
┌──────────────▼──────┐ ┌───────────▼──────┐ ┌─────▼────────────┐
│  Random Forest      │ │  Whisper + NLP    │ │   BERT LLM        │
│  Style d'appr.      │ │  Recherche Vocale │ │   Tuteur IA       │
└─────────────────────┘ └──────────────────┘ └──────────────────┘
                              │
┌─────────────────────────────▼─────────────────────────────────┐
│                  PostgreSQL 15 — Base de Données                │
│             15 Tables (Cours, Quiz, Erreurs, Logs, …)           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ Prérequis Système

| Outil | Version minimale |
|---|---|
| Python | 3.11+ |
| Node.js | 20.x+ |
| npm | 10.x+ |
| PostgreSQL | 15.x+ |
| RAM | 8 GB (16 GB recommandé) |
| Espace disque | 5 GB minimum |

```bash
# Vérifier les versions installées
python --version    # Python 3.11+
node --version      # Node.js 20+
npm --version       # npm 10+
psql --version      # PostgreSQL 15+
```

---

## ⚙️ Installation — Backend

### 1. Cloner le dépôt

```bash
git clone https://github.com/daaoudi/EdTech_Web_SAAS.git
cd edtech-app
```

### 2. Créer et activer l'environnement virtuel

```bash
cd backend

# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Installer les dépendances Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Contenu de `requirements.txt` :**

```
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
asyncpg>=0.29.0
python-dotenv>=1.0.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
bcrypt>=4.1.2
pydantic>=2.5.0
psycopg2-binary==2.9.9
scikit-learn==1.3.2
joblib==1.3.2
requests==2.31.0
python-multipart==0.0.6
python-dotenv==1.0.0
sqlalchemy==2.0.23
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
email-validator==2.1.0
pandas==2.1.3
numpy==1.26.2
accelerate==0.25.0
huggingface-hub==0.20.3
torch==2.1.0
transformers==4.36.2
sentence-transformers==2.2.2
openpyxl==3.1.2
```

### 4. Configurer les variables d'environnement

Créez le fichier `backend/.env` :

```env
# ──── Base de Données PostgreSQL ────
DB_HOST=localhost
DB_PORT=5432
DB_NAME=plateforme_elearning
DB_USER=postgres
DB_PASSWORD=root

# ──── Authentification JWT ────
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ──── CORS ────
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# ──── OpenAI Whisper (Optionnel) ────
OPENAI_API_KEY=your-openai-api-key

# ──── Modèles IA ────
TUTOR_MODEL_PATH=./tutor_ia_model/
BERT_MODEL_NAME=paraphrase-multilingual-MiniLM-L12-v2
```

> ⚠️ Ne commitez jamais ce fichier `.env` dans git.

---

## 💻 Installation — Frontend

### 1. Installer les dépendances Node.js

```bash
cd frontend
npm install
```

**Dépendances principales (`package.json`) :**

```json
{
  "dependencies": {
    "@headlessui/react": "^2.2.10",
    "@heroicons/react": "^2.2.0",
    "@tailwindcss/vite": "^4.2.2",
    "axios": "^1.15.0",
    "chart.js": "^4.5.1",
    "react": "^19.2.4",
    "react-audio-player": "^0.17.0",
    "react-chartjs-2": "^5.3.1",
    "react-dom": "^19.2.4",
    "react-hot-toast": "^2.6.0",
    "react-router-dom": "^7.14.1"
  },
  "devDependencies": {
    "typescript": "~6.0.2",
    "vite": "^8.0.4",
    "tailwindcss": "^3.4.17",
    "@vitejs/plugin-react": "^6.0.1"
  }
}
```

### 2. Configurer les variables d'environnement

Créez le fichier `frontend/.env` :

```env
VITE_API_URL=http://localhost:8001
VITE_AUDIO_BASE_URL=http://localhost:8001/static/audio
VITE_WHISPER_API_URL=http://localhost:8001/api/voice/search
```

---

## 🗄️ Configuration de la Base de Données

### 1. Créer la base de données

```bash
# Se connecter à PostgreSQL
psql -U postgres

# Dans le shell PostgreSQL
CREATE DATABASE plateforme_elearning;
\q
```

### 2. Initialiser les tables

**Option A — via Python :**

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python -c "
import asyncio
from database import init_db
asyncio.run(init_db())
"
```

**Option B — via script SQL :**

```bash
psql -U postgres -d plateforme_elearning -f database_schema.sql
```

### 3. Appliquer les migrations Alembic (si configuré)

```bash
cd backend
alembic upgrade head
```

---

## ▶️ Lancement du Projet

### Terminal 1 — Démarrer le Backend

```bash
cd backend
source venv/bin/activate     # Windows: venv\Scripts\activate
uvicorn mainApp:app --reload --port 8001 --host 0.0.0.0
```

- **API disponible sur :** `http://localhost:8001`
- **Documentation Swagger :** `http://localhost:8001/docs`
- **Documentation ReDoc :** `http://localhost:8001/redoc`

### Terminal 2 — Démarrer le Frontend

```bash
cd frontend
npm run dev
```

- **Application disponible sur :** `http://localhost:5173`

---

## 📁 Structure des Dossiers

```
edtech-app/
├── backend/
│   ├── api/
│   │   └── recommendation.py          # Endpoints de recommandation
│   ├── ml/
│   │   ├── bert_tutor.py              # Tuteur IA BERT
│   │   ├── recommender.py             # Random Forest
│   │   └── sequential_miner.py        # Analyse comportementale
│   ├── models/
│   │   ├── course.py                  # Modèle Cours
│   │   ├── question.py                # Modèle Questions
│   │   ├── result.py                  # Modèle Résultats
│   │   └── users.py                   # Modèle Utilisateurs
│   ├── services/
│   │   └── voice_search.py            # Whisper + NLP
│   ├── static/                        # Fichiers statiques (audio, vidéo)
│   ├── tutor_ia_model/                # Modèles IA pré-entraînés
│   ├── models_pkl/                    # Modèles Random Forest sérialisés
│   ├── auth.py                        # Authentification JWT
│   ├── config.py                      # Configuration
│   ├── database.py                    # Connexion PostgreSQL
│   ├── mainApp.py                     # Point d'entrée FastAPI
│   ├── schemas.py                     # Pydantic schemas
│   ├── requirements.txt               # Dépendances Python
│   └── .env                           # Variables d'environnement (non versionné)
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── BehaviorRiskAnalysis.tsx
│   │   │   ├── DropoutPrediction.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── Layout.tsx
│   │   │   ├── PrivateRoute.tsx
│   │   │   ├── ProtectedRoute.tsx
│   │   │   └── Searchbar.tsx
│   │   ├── pages/
│   │   │   ├── AdminPage.tsx
│   │   │   ├── AudioLearningPage.tsx
│   │   │   ├── CourseDetailPage.tsx
│   │   │   ├── CoursesPage.tsx
│   │   │   ├── HomePage.tsx
│   │   │   ├── LevelTestPage.tsx
│   │   │   ├── LoginPage.tsx
│   │   │   ├── ProfilePage.tsx
│   │   │   ├── ProgressPage.tsx
│   │   │   ├── QuizPage.tsx
│   │   │   ├── RecommendationPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   ├── RiskMonitorPage.tsx
│   │   │   ├── TextLearningPage.tsx
│   │   │   └── VideoLearningPage.tsx
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── bertService.ts
│   │   │   ├── CourseService.ts
│   │   │   ├── MistakeService.ts
│   │   │   ├── SequentialMinerService.ts
│   │   │   └── VoiceSearchService.ts
│   │   ├── app.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── .env                           # Variables d'environnement (non versionné)
│
├── .gitignore
└── README.md
```

---

## 🗃️ Base de Données

### Schéma — 15 Tables

| Table | Description |
|---|---|
| `utilisateurs` | Comptes et profils utilisateurs |
| `roles` | Gestion des permissions |
| `cours_html` | Contenu des cours (texte, audio, vidéo) |
| `chapitres` | Organisation des chapitres |
| `medias` | Ressources multimédias |
| `questions_quiz` | Banque de questions |
| `reponses_quiz` | Réponses des utilisateurs |
| `resultats_apprentissage` | Suivi des performances |
| `erreurs_utilisateurs` | Historique des erreurs |
| `preferences_apprentissage` | Scores par mode d'apprentissage |
| `recherches_vocales` | Logs de recherche vocale |
| `embeddings_cours` | Vecteurs sémantiques BERT |
| `modeles_ia` | Métadonnées des modèles IA |
| `logs_interaction` | Analytics utilisateur |
| `logs_admin` | Audit administrateur |

### Commandes Utiles

```bash
# Connexion interactive
psql -U postgres -d plateforme_elearning

# Lister les tables
\dt

# Inspecter une table
SELECT * FROM cours_html LIMIT 10;

# Backup
pg_dump -U postgres plateforme_elearning > backup.sql

# Restore
psql -U postgres -d plateforme_elearning < backup.sql
```

---

## 🔗 Endpoints API

### Authentification

| Méthode | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Inscription utilisateur |
| POST | `/auth/login` | Authentification JWT |
| GET | `/auth/me` | Profil utilisateur connecté |

### Cours

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/cours/list` | Liste des cours disponibles |
| GET | `/cours/{id}` | Détail d'un cours |
| GET | `/cours/{id}/questions` | Questions associées à un cours |

### Recommandation — Random Forest

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/recommend/learning-mode` | Mode d'apprentissage optimal |

### Quiz — BERT

| Méthode | Endpoint | Description |
|---|---|---|
| POST | `/quiz/generate` | Générer un quiz |
| POST | `/quiz/submit` | Soumettre les réponses |
| POST | `/bert/quiz/{course_id}` | Quiz personnalisé BERT |

### Recherche Vocale — Whisper

| Méthode | Endpoint | Description |
|---|---|---|
| POST | `/voice/search` | Recherche vocale complète |
| POST | `/voice/transcribe` | Transcription audio |

### Tuteur IA — BERT

| Méthode | Endpoint | Description |
|---|---|---|
| POST | `/tutor/reformulate` | Reformulation de concept |
| GET | `/tutor/recommend` | Recommandations personnalisées |

---

## 🤖 Modèles IA

### 1. Random Forest — Prédiction du Style d'Apprentissage

```python
from ml.recommender import LearningRecommender

recommender = LearningRecommender()
user_features = {
    'text': 88.0,
    'audio': 79.3,
    'video': 95.6
}
mode, confidence = recommender.predict(user_features)
# → ('video', 0.97)
```

### 2. BERT — Tuteur IA Adaptatif

```python
from ml.bert_tutor import BertTutor

tutor = BertTutor()
tutor.load_embeddings()

quiz = tutor.generate_quiz_from_concepts(
    concepts=["titre principal HTML"],
    course_id="6",
    num_questions=5
)
```

### 3. Whisper — Recherche Vocale

```python
from services.voice_search import VoiceSearchEngine

engine = VoiceSearchEngine()
result = engine.process_voice_query("audio.wav")
# → { transcription, intent, cours_trouvés }
```

### Fichiers de modèles attendus

```
backend/tutor_ia_model/
├── cours_embeddings.pkl
├── cours_ids.pkl
├── questions_embeddings.pkl
└── ...

backend/models_pkl/
└── random_forest_model.pkl
```

---

## 🛠️ Dépannage

### `ModuleNotFoundError: No module named '...'`

```bash
cd backend
pip install -r requirements.txt --upgrade
```

### `psycopg2.OperationalError: could not connect to server`

```bash
# Vérifier le statut PostgreSQL (Linux)
sudo systemctl status postgresql
sudo systemctl restart postgresql

# Vérifier la connectivité
pg_isready -U postgres
```

### `npm ERR! code ENOENT`

```bash
cd frontend
rm -rf node_modules
rm package-lock.json
npm install
```

### Erreur CORS

Vérifiez `backend/.env` :

```env
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

### Modèle BERT non chargé

```bash
ls backend/tutor_ia_model/
# Doit contenir : cours_embeddings.pkl, cours_ids.pkl, questions_embeddings.pkl, etc.
```

### Torch ou Transformers trop lents à charger

Assurez-vous d'avoir au moins 8 GB de RAM disponibles. Les modèles pré-entraînés sont chargés en mémoire au démarrage.

---

## 📚 Commandes Utiles

### Backend

```bash
# Démarrer le serveur (développement)
uvicorn mainApp:app --reload --port 8001
#ou
python mainApp.py

# Démarrer avec logs détaillés
uvicorn mainApp:app --reload --port 8001 --log-level debug

# Appliquer les migrations
alembic upgrade head

# Créer une nouvelle migration
alembic revision --autogenerate -m "description"
```

### Frontend

```bash
# Démarrer en mode développement
npm run dev

# Compiler pour la production
npm run build

# Prévisualiser la version compilée
npm run preview

# Linter TypeScript + ESLint
npm run lint
```

---

## 👥 Contributions

Ce projet est réalisé dans le cadre d'un Projet de Fin d'Études (PFE) 2025–2026.

---

*Plateforme EdTech SaaS IA — PFE 2025-2026*
