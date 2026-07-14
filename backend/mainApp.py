
from fastapi import FastAPI, Depends, HTTPException, status, Query, Path, Body, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
import logging
from datetime import timedelta, datetime
import json
import uvicorn
import os
import traceback
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from services.voice_search import voice_search_service
from ml.sequential_miner import SequentialPatternMiner, generate_sample_logs
from schemas import CertificateGenerateRequest, CertificateResponse, CertificateVerifyResponse
from PIL import Image, ImageDraw, ImageFont
from fastapi import FastAPI, Depends, HTTPException, status, Query, Path, Body, Header, UploadFile, File

import whisper
import tempfile
from ml.bert_tutor import bert_tutor
from ml.sequential_miner import SequentialPatternMiner
from collections import defaultdict
import pandas as pd

import re
import base64
from io import BytesIO
import uuid

from config import config
from models.database import db
from auth import auth_service, get_current_user, require_admin, require_permission
from models.users import UserCreate, UserInDB, UserUpdate, Token, UserLogin, UserResponse
from models.course import CourseCreate, CourseUpdate, CourseResponse, generate_slug
from models.question import QuestionCreate, QuestionUpdate, QuestionResponse
from models.result import LearningResultCreate, LearningResultResponse
from ml.recommender import recommender


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VoiceSearchService:
    def __init__(self):
        self.model = None
        self.intent_map = self.create_intent_map()
        
    def load_model(self):
        
        if self.model is None:
            try:
                
                self.model = whisper.load_model("base")
                logger.info("✅ Modèle Whisper chargé avec succès")
            except Exception as e:
                logger.error(f"❌ Erreur chargement modèle Whisper: {e}")
                raise
    
    def create_intent_map(self) -> Dict[str, Any]:
        
        return {
            "topics": {
                "html": {
                    "keywords": ["html", "balise", "structure", "page web", "hypertexte", "html5"],
                    "course_ids": [6, 7, 11]
                },
                "css": {
                    "keywords": ["css", "style", "design", "mise en page", "couleur", "flexbox", "grid"],
                    "course_ids": [10]
                },
                "formulaire": {
                    "keywords": ["formulaire", "form", "input", "champ", "saisie", "validation"],
                    "course_ids": [8]
                },
                "lien": {
                    "keywords": ["lien", "hyperlien", "anchor", "href", "navigation", "url"],
                    "course_ids": [7, 11]
                },
                "image": {
                    "keywords": ["image", "img", "photo", "illustration", "visuel"],
                    "course_ids": [7]
                },
                "texte": {
                    "keywords": ["texte", "paragraphe", "titre", "formatage", "heading"],
                    "course_ids": [6]
                },
                "semantique": {
                    "keywords": ["sémantique", "semantique", "html5", "structure", "header", "footer", "nav", "article"],
                    "course_ids": [9]
                }
            },
            "difficulty": {
                "debutant": ["débutant", "facile", "base", "introduction", "premier pas", "découvrir", "apprendre"],
                "intermediaire": ["intermédiaire", "moyen", "approfondi", "pratique"],
                "avance": ["avancé", "expert", "difficile", "complexe", "maîtriser", "perfectionnement"]
            },
            "actions": {
                "chercher": ["cherche", "trouver", "recherche", "afficher", "montrer", "donner"],
                "apprendre": ["apprendre", "étudier", "comprendre", "maîtriser", "découvrir"],
                "pratiquer": ["pratiquer", "exercice", "entraînement", "travailler"]
            }
        }
    
    def analyze_intent(self, text: str) -> Dict[str, Any]:
        
        text_lower = text.lower()
        
        intent = {
            "original_query": text,
            "processed_query": text_lower,
            "topics": [],
            "difficulty": None,
            "actions": [],
            "keywords": [],
            "course_ids": set(),
            "confidence": 0.0
        }
        
        
        for topic, data in self.intent_map["topics"].items():
            for keyword in data["keywords"]:
                if keyword in text_lower:
                    intent["topics"].append(topic)
                    intent["course_ids"].update(data["course_ids"])
                    intent["keywords"].append(keyword)
                    break
        
        
        for level, keywords in self.intent_map["difficulty"].items():
            for keyword in keywords:
                if keyword in text_lower:
                    intent["difficulty"] = level
                    intent["keywords"].append(keyword)
                    break
        
        
        for action, keywords in self.intent_map["actions"].items():
            for keyword in keywords:
                if keyword in text_lower:
                    intent["actions"].append(action)
                    intent["keywords"].append(keyword)
                    break
        
        
        stop_words = ["je", "tu", "il", "elle", "nous", "vous", "ils", "elles", 
                      "le", "la", "les", "un", "une", "des", "pour", "par", "sur", 
                      "dans", "avec", "sans", "et", "ou", "donc", "or", "ni", "car",
                      "veux", "cherche", "trouver", "apprendre", "cours", "moi", "toi",
                      "lui", "elle", "eux", "elles", "ce", "cet", "cette", "ces",
                      "du", "de", "au", "aux", "en", "vers", "pendant", "depuis"]
        
        words = re.findall(r'\b\w+\b', text_lower)
        for word in words:
            if len(word) > 2 and word not in stop_words and word not in intent["keywords"]:
                intent["keywords"].append(word)
        
        
        confidence = 0.0
        if intent["topics"]:
            confidence += 0.4
        if intent["difficulty"]:
            confidence += 0.3
        if intent["actions"]:
            confidence += 0.2
        if len(intent["keywords"]) > 0:
            confidence += 0.1
        
        intent["confidence"] = min(confidence, 1.0)
        
        return intent
    
    def transcribe_audio(self, audio_file_path: str) -> Dict[str, Any]:
        
        try:
            self.load_model()
            
            
            result = self.model.transcribe(
                audio_file_path,
                language="fr",
                task="transcribe",
                fp16=False
            )
            
            transcript = result["text"].strip()
            confidence = 1.0 - result.get("no_speech_prob", 0.0)
            
            
            intent = self.analyze_intent(transcript)
            
            return {
                "success": True,
                "transcript": transcript,
                "confidence": confidence,
                "intent": intent
            }
            
        except Exception as e:
            logger.error(f"Erreur transcription: {e}")
            return {
                "success": False,
                "error": str(e),
                "transcript": "",
                "confidence": 0.0,
                "intent": None
            }


voice_search_service = VoiceSearchService()


def get_db_connection_recommendation():
    
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'plateforme_elearning'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'root'),
            port=os.getenv('DB_PORT', 5432),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def get_user_metrics_direct(user_id: int):
    
    conn = get_db_connection_recommendation()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        
        
        query = """
        SELECT 
            mode,
            COALESCE(AVG(score_quiz), 0) as avg_score,
            COUNT(*) as sessions,
            COALESCE(AVG(taux_completion), 0) as avg_completion,
            COALESCE(SUM(CASE WHEN est_reussi THEN 1 ELSE 0 END)::float / NULLIF(COUNT(*), 0), 0) as success_rate
        FROM resultats_apprentissage
        WHERE utilisateur_id = %s
        GROUP BY mode
        """
        
        cur.execute(query, (user_id,))
        results = cur.fetchall()
        
        cur.close()
        conn.close()
        
        
        metrics = {
            'text': {'avg_score': 0, 'sessions': 0, 'avg_completion': 0, 'success_rate': 0},
            'audio': {'avg_score': 0, 'sessions': 0, 'avg_completion': 0, 'success_rate': 0},
            'video': {'avg_score': 0, 'sessions': 0, 'avg_completion': 0, 'success_rate': 0}
        }
        
        for row in results:
            mode = row['mode']
            if mode in metrics:
                metrics[mode] = {
                    'avg_score': float(row['avg_score']) if row['avg_score'] else 0,
                    'sessions': row['sessions'] or 0,
                    'avg_completion': float(row['avg_completion']) if row['avg_completion'] else 0,
                    'success_rate': float(row['success_rate']) if row['success_rate'] else 0
                }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting user metrics: {e}")
        return None

def get_default_recommendation_direct():
    
    return {
        'recommended_mode': 'video',
        'recommended_title': '🎬 Commencez avec la Vidéo',
        'confidence': 0.5,
        'confidence_text': 'Moyenne',
        'confidence_color': '#F59E0B',
        'probabilities_dict': {'text': 0.3, 'audio': 0.3, 'video': 0.4},
        'description': 'Pour débuter, nous recommandons le mode vidéo qui offre une introduction visuelle complète.',
        'details': [
            "Aucune donnée d'apprentissage disponible",
            "Basé sur les statistiques des nouveaux apprenants"
        ],
        'strengths': [
            "Découverte progressive des concepts",
            "Exemples visuels concrets",
            "Démonstrations pas à pas"
        ],
        'next_steps': [
            "Commencez par regarder une vidéo d'introduction",
            "Pratiquez avec les exercices associés",
            "Passez le quiz de validation"
        ],
        'metrics': {
            'text': {'score': 0, 'sessions': 0, 'success_rate': 0, 'completion': 0},
            'audio': {'score': 0, 'sessions': 0, 'success_rate': 0, 'completion': 0},
            'video': {'score': 0, 'sessions': 0, 'success_rate': 0, 'completion': 0}
        },
        'timestamp': datetime.now().isoformat()
    }


def generate_certificate_image(user_name: str, course_name: str, score: float, date: str, code: str):
    """
    Génère une image de certificat
    """
    # Dimensions du certificat
    width = 1200
    height = 848
    
    # Créer l'image
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Couleurs
    gold = (201, 168, 76)
    dark_gold = (180, 150, 60)
    dark_blue = (26, 26, 46)
    medium_blue = (74, 74, 106)
    light_blue = (45, 45, 68)
    
    # Bordures
    draw.rectangle([40, 40, width-40, height-40], outline=gold, width=20)
    draw.rectangle([60, 60, width-60, height-60], outline=dark_gold, width=4)
    
    # Charger les polices
    try:
        title_font = ImageFont.truetype("arial.ttf", 60)
        name_font = ImageFont.truetype("arial.ttf", 48)
        subtitle_font = ImageFont.truetype("arial.ttf", 24)
        text_font = ImageFont.truetype("arial.ttf", 22)
        course_font = ImageFont.truetype("arial.ttf", 32)
        small_font = ImageFont.truetype("arial.ttf", 18)
        logo_font = ImageFont.truetype("arial.ttf", 80)
    except:
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
            name_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
            subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
            course_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
            logo_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 80)
        except:
            title_font = ImageFont.load_default()
            name_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            course_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
            logo_font = ImageFont.load_default()
    
    # Titre
    draw.text((width//2, 150), "🎓 CERTIFICAT DE RÉUSSITE", 
              fill=dark_blue, font=title_font, anchor="mt")
    
    # Sous-titre
    draw.text((width//2, 220), "Ce certificat atteste que", 
              fill=medium_blue, font=subtitle_font, anchor="mt")
    
    # Nom de l'utilisateur
    draw.text((width//2, 320), user_name, 
              fill=gold, font=name_font, anchor="mt")
    
    # Texte de réussite
    draw.text((width//2, 390), "a réussi l'examen final du cours :", 
              fill=light_blue, font=text_font, anchor="mt")
    
    # Nom du cours
    draw.text((width//2, 450), course_name, 
              fill=dark_blue, font=course_font, anchor="mt")
    
    # Score
    draw.text((width//2, 520), f"avec un score de {score:.1f}%", 
              fill=light_blue, font=text_font, anchor="mt")
    
    # Date
    draw.text((width//2, 580), f"Délivré le {date}", 
              fill=medium_blue, font=small_font, anchor="mt")
    
    # Ligne de signature
    draw.line([300, 680, 500, 680], fill=dark_blue, width=2)
    draw.text((400, 710), "Signature du responsable", 
              fill=medium_blue, font=small_font, anchor="mt")
    
    # Code du certificat
    draw.text((width//2, 780), f"Code: {code}", 
              fill=medium_blue, font=small_font, anchor="mt")
    
    # Logo
    draw.text((width//2, 820), "🎓", 
              fill=gold, font=logo_font, anchor="mt")
    
    # Sauvegarder l'image
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return img_byte_arr

def generate_global_certificate_image(
    user_name: str, 
    courses_completed: list, 
    total_courses: int,
    score: float, 
    date: str, 
    code: str,
    completion_percentage: float
):
    """
    Génère une image de certificat global pour la formation complète
    """
    # Dimensions du certificat
    width = 1200
    height = 1000
    
    # Créer l'image
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Couleurs
    gold = (201, 168, 76)
    dark_gold = (180, 150, 60)
    dark_blue = (26, 26, 46)
    medium_blue = (74, 74, 106)
    light_blue = (45, 45, 68)
    light_gray = (240, 240, 245)
    
    # Bordures
    # Bordure extérieure dorée
    draw.rectangle([40, 40, width-40, height-40], outline=gold, width=20)
    # Bordure intérieure
    draw.rectangle([60, 60, width-60, height-60], outline=dark_gold, width=4)
    # Fond intérieur légèrement coloré
    draw.rectangle([70, 70, width-70, height-70], outline=light_gray, width=1)
    
    # Charger les polices
    try:
        title_font = ImageFont.truetype("arial.ttf", 52)
        subtitle_font = ImageFont.truetype("arial.ttf", 26)
        name_font = ImageFont.truetype("arial.ttf", 48)
        text_font = ImageFont.truetype("arial.ttf", 20)
        course_font = ImageFont.truetype("arial.ttf", 16)
        small_font = ImageFont.truetype("arial.ttf", 14)
        logo_font = ImageFont.truetype("arial.ttf", 60)
    except:
        try:
            # Pour Linux/Mac
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 52)
            subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
            name_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
            text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
            course_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            logo_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            name_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            course_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
            logo_font = ImageFont.load_default()
    
    # Titre principal
    draw.text((width//2, 120), "🎓 CERTIFICAT DE RÉUSSITE", 
              fill=dark_blue, font=title_font, anchor="mt")
    
    # Sous-titre
    draw.text((width//2, 180), "Formation Complète en Développement Web", 
              fill=medium_blue, font=subtitle_font, anchor="mt")
    
    # Ligne de séparation
    draw.line([300, 210, 900, 210], fill=gold, width=2)
    
    # "Ce certificat atteste que"
    draw.text((width//2, 250), "Ce certificat atteste que", 
              fill=medium_blue, font=text_font, anchor="mt")
    
    # Nom de l'utilisateur
    draw.text((width//2, 310), user_name, 
              fill=gold, font=name_font, anchor="mt")
    
    # Texte de réussite
    draw.text((width//2, 380), "a complété avec succès l'ensemble des cours suivants :", 
              fill=light_blue, font=text_font, anchor="mt")
    
    # Boîte des cours
    box_y = 420
    box_height = 200
    box_margin = 80
    
    # Fond de la boîte
    draw.rectangle([box_margin, box_y, width-box_margin, box_y + box_height], 
                   fill=light_gray, outline=gold, width=1)
    
    # Titre de la boîte
    draw.text((width//2, box_y + 15), "📚 Modules validés", 
              fill=dark_blue, font=course_font, anchor="mt")
    
    # Ligne sous le titre
    draw.line([box_margin + 50, box_y + 35, width - box_margin - 50, box_y + 35], 
              fill=dark_gold, width=1)
    
    # Afficher les cours en grille
    max_courses = min(len(courses_completed), 16)
    courses_to_show = courses_completed[:max_courses]
    
    # Calculer le nombre de colonnes
    cols = 2 if len(courses_to_show) <= 8 else 3
    rows = (len(courses_to_show) + cols - 1) // cols
    
    col_width = (width - 2 * box_margin - 60) // cols
    row_height = 28
    
    start_x = box_margin + 40
    start_y = box_y + 55
    
    draw.text_anchor = "lt"
    
    for idx, course in enumerate(courses_to_show):
        col = idx % cols
        row = idx // cols
        x = start_x + col * col_width
        y = start_y + row * row_height
        
        # Limiter la longueur du titre
        title = course['titre']
        if len(title) > 30:
            title = title[:28] + "..."
        
        # Ajouter une petite puce
        draw.text((x, y), "●", fill=gold, font=small_font)
        draw.text((x + 20, y), title, fill=dark_blue, font=small_font)
    
    # Score final
    draw.text((width//2, 660), f"Score final : {score:.1f}%", 
              fill=light_blue, font=text_font, anchor="mt")
    
    # Taux de complétion
    draw.text((width//2, 700), f"Taux de complétion : {completion_percentage:.0f}%", 
              fill=medium_blue, font=small_font, anchor="mt")
    
    # Date
    draw.text((width//2, 760), f"Délivré le {date}", 
              fill=medium_blue, font=small_font, anchor="mt")
    
    # Ligne de signature
    draw.line([350, 800, 550, 800], fill=dark_blue, width=2)
    draw.text((450, 830), "Signature du responsable pédagogique", 
              fill=medium_blue, font=small_font, anchor="mt")
    
    # Code du certificat
    draw.text((width//2, 880), f"Code: {code}", 
              fill=medium_blue, font=small_font, anchor="mt")
    
    # Logo final
    draw.text((width//2, 930), "🎓", 
              fill=gold, font=logo_font, anchor="mt")
    
    # Sauvegarder l'image
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return img_byte_arr

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    
    logger.info("🚀 Démarrage de l'application...")
    await db.connect()
    
    
    try:
        async with db.get_connection() as conn:
            version = await conn.fetchval("SELECT version()")
            logger.info(f"✅ Connecté à PostgreSQL: {version[:50]}...")
    except Exception as e:
        logger.error(f"❌ Erreur de connexion à la base: {e}")
        raise
    
    yield
    
    
    logger.info("🛑 Arrêt de l'application...")
    await db.disconnect()


app = FastAPI(
    title=config.APP_TITLE,
    version=config.APP_VERSION,
    description="API Backend pour la Plateforme Éducative Intelligente",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





try:
    
    if os.path.exists(config.TUTOR_MODEL_PATH):
        logger.info(f"📁 Chargement du modèle depuis: {config.TUTOR_MODEL_PATH}")
        
        
        bert_tutor.load_model()
        
        
        if bert_tutor.load_embeddings():
            logger.info(f"✅ Tuteur BERT initialisé avec succès")
            bert_tutor.debug_questions()
            bert_tutor.test_parse_options()
            logger.info(f"   - {len(bert_tutor.cours_ids)} cours disponibles")
            logger.info(f"   - {len(bert_tutor.questions_texts)} questions disponibles")
        else:
            logger.warning("⚠️ Tuteur BERT: impossible de charger les embeddings")
    else:
        logger.warning(f"⚠️ Dossier du modèle non trouvé: {config.TUTOR_MODEL_PATH}")
        logger.warning("   Le tuteur BERT fonctionnera en mode dégradé")
except Exception as e:
    logger.error(f"❌ Erreur initialisation BERT: {e}")
    logger.warning("   L'API continuera de fonctionner sans les fonctionnalités BERT")


sequential_miner = SequentialPatternMiner(
    min_support=config.SEQUENTIAL_MIN_SUPPORT,
    min_confidence=config.SEQUENTIAL_MIN_CONFIDENCE
)
try:
    if os.path.exists(config.SEQUENTIAL_MINER_PATH):
        if sequential_miner.load(config.SEQUENTIAL_MINER_PATH):
            logger.info("✅ Sequential Pattern Miner chargé avec succès")
        else:
            logger.info("ℹ️ Sequential Pattern Miner: nouveau modèle créé")
    else:
        logger.info("ℹ️ Sequential Pattern Miner: aucun modèle pré-entraîné trouvé")
except Exception as e:
    logger.warning(f"⚠️ Sequential Pattern Miner non chargé: {e}")


@app.post("/certificates/generate")
async def generate_certificate(
    request: CertificateGenerateRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Génère un certificat pour un utilisateur après réussite d'un examen
    """
    try:
        # Vérifier que l'utilisateur est le même
        if current_user.id != request.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez générer un certificat que pour vous-même"
            )
        
        # Vérifier si l'utilisateur existe
        user = await db.get_user_by_id(request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Vérifier si le cours existe
        course = await db.read_one("cours_html", {"id": request.course_id})
        if not course:
            raise HTTPException(status_code=404, detail="Cours non trouvé")
        
        # Vérifier si un certificat existe déjà
        exists = await db.certificate_exists(request.user_id, request.course_id, request.mode)
        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Un certificat existe déjà pour ce cours et ce mode"
            )
        
        # Générer un code unique
        certificate_code = f"CERT-{uuid.uuid4().hex[:8].upper()}-{datetime.now().strftime('%Y%m%d')}"
        
        # Formater la date
        if request.date:
            try:
                date_obj = datetime.fromisoformat(request.date.replace('Z', '+00:00'))
            except:
                date_obj = datetime.now()
        else:
            date_obj = datetime.now()
        date_str = date_obj.strftime("%d/%m/%Y")
        
        # Nom complet de l'utilisateur
        user_name = f"{user.get('prenom', '')} {user.get('nom', '')}".strip()
        if not user_name:
            user_name = user.get('email', 'Utilisateur')
        
        # Générer l'image du certificat
        img_bytes = generate_certificate_image(
            user_name=user_name,
            course_name=request.course_name,
            score=request.score,
            date=date_str,
            code=certificate_code
        )
        
        # Convertir en base64
        img_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
        certificate_url = f"data:image/png;base64,{img_base64}"
        
        # Sauvegarder dans la base de données
        certificate_id = await db.save_certificate(
            user_id=request.user_id,
            course_id=request.course_id,
            mode=request.mode,
            score=request.score,
            certificate_url=certificate_url,
            certificate_code=certificate_code
        )
        
        # Logger l'action
        await log_admin_action(
            admin_id=current_user.id,
            action="GENERATE_CERTIFICATE",
            table="certificats",
            record_id=certificate_id,
            details={
                "course_id": request.course_id,
                "score": request.score,
                "code": certificate_code
            }
        )
        
        return {
            "success": True,
            "certificate_id": certificate_id,
            "certificate_code": certificate_code,
            "certificate_url": certificate_url,
            "message": "Certificat généré avec succès"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur génération certificat: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération du certificat: {str(e)}"
        )

@app.get("/certificates/user")
async def get_my_certificates(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Récupère tous les certificats de l'utilisateur connecté
    """
    try:
        certificates = await db.get_user_certificates(current_user.id)
        return certificates
    except Exception as e:
        logger.error(f"Erreur récupération certificats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des certificats"
        )

@app.get("/certificates/verify/{code}")
async def verify_certificate(
    code: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Vérifie la validité d'un certificat
    """
    try:
        certificate = await db.get_certificate_by_code(code)
        
        if not certificate:
            return {
                "valid": False,
                "message": "Certificat non trouvé"
            }
        
        return {
            "valid": True,
            "certificate": {
                "code": certificate['certificate_code'],
                "user_name": f"{certificate.get('user_prenom', '')} {certificate.get('user_nom', '')}".strip() or certificate.get('user_email'),
                "user_email": certificate.get('user_email'),
                "course_name": certificate.get('course_title'),
                "score": float(certificate.get('score', 0)),
                "mode": certificate.get('mode'),
                "date": certificate.get('date_created').strftime("%d/%m/%Y") if certificate.get('date_created') else None
            }
        }
    except Exception as e:
        logger.error(f"Erreur vérification certificat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la vérification du certificat"
        )

@app.post("/certificates/generate-global")
async def generate_global_certificate(
    request: CertificateGenerateRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Génère un certificat global pour la formation complète
    """
    try:
        # Vérifier que l'utilisateur est le même
        if current_user.id != request.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez générer un certificat que pour vous-même"
            )
        
        # Vérifier si l'utilisateur existe
        user = await db.get_user_by_id(request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Récupérer tous les cours complétés
        async with db.get_connection() as conn:
            # Nombre total de cours
            total_courses = await conn.fetchval("""
                SELECT COUNT(*) FROM cours_html WHERE est_actif = true
            """)
            
            # Liste des cours complétés
            courses_rows = await conn.fetch("""
                SELECT DISTINCT c.id, c.titre, c.difficulte
                FROM cours_html c
                JOIN resultats_apprentissage r ON c.id = r.cours_id
                WHERE r.utilisateur_id = $1 AND r.est_reussi = true
                ORDER BY c.id
            """, request.user_id)
            
            courses_completed = [dict(row) for row in courses_rows]
            completed_count = len(courses_completed)
            
            # Calculer le pourcentage de complétion
            completion_percentage = (completed_count / total_courses) * 100 if total_courses > 0 else 0
            
            # Vérifier que l'utilisateur a complété au moins 50% des cours
            min_required = 50
            if completion_percentage < min_required:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Vous devez compléter au moins {min_required}% des cours pour obtenir le certificat global. "
                           f"Vous avez complété {completion_percentage:.0f}% ({completed_count}/{total_courses})"
                )
            
            # Si l'utilisateur demande un certificat pour un cours spécifique mais a complété tous les cours
            # on peut proposer le certificat global
            is_global = request.course_name == "Formation Complète HTML, CSS & JavaScript"
            
            # Générer un code unique pour le certificat
            certificate_code = f"GLOBAL-{uuid.uuid4().hex[:8].upper()}-{datetime.now().strftime('%Y%m%d')}"
            
            # Formater la date
            date_obj = datetime.now()
            date_str = date_obj.strftime("%d/%m/%Y")
            
            # Nom complet de l'utilisateur
            user_name = f"{user.get('prenom', '')} {user.get('nom', '')}".strip()
            if not user_name:
                user_name = user.get('email', 'Utilisateur')
            
            # Générer l'image du certificat global
            img_bytes = generate_global_certificate_image(
                user_name=user_name,
                courses_completed=courses_completed,
                total_courses=total_courses,
                score=request.score,
                date=date_str,
                code=certificate_code,
                completion_percentage=completion_percentage
            )
            
            # Convertir en base64
            img_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
            certificate_url = f"data:image/png;base64,{img_base64}"
            
            # Sauvegarder dans la base de données
            try:
                async with db.get_connection() as conn:
                    # Vérifier si la table certificats existe
                    table_exists = await conn.fetchval("""
                        SELECT EXISTS (
                            SELECT 1 FROM information_schema.tables 
                            WHERE table_name = 'certificats'
                        )
                    """)
                    
                    if not table_exists:
                        await db.create_certificates_table()
                    
                    # Insérer le certificat
                    row = await conn.fetchrow("""
                        INSERT INTO certificats 
                        (user_id, course_id, mode, score, certificate_url, certificate_code, date_created)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        RETURNING id
                    """, 
                        request.user_id,
                        0,  # course_id = 0 pour global
                        request.mode,
                        request.score,
                        certificate_url,
                        certificate_code,
                        datetime.now()
                    )
                    
                    certificate_id = row['id']
                    
                    # Logger l'action
                    await conn.execute("""
                        INSERT INTO logs_admin (admin_id, action, table_affectee, id_ligne, details)
                        VALUES ($1, $2, $3, $4, $5)
                    """,
                        current_user.id,
                        "GENERATE_GLOBAL_CERTIFICATE",
                        "certificats",
                        certificate_id,
                        f"Certificat global généré avec {completed_count}/{total_courses} cours complétés, score: {request.score}%"
                    )
            except Exception as db_error:
                logger.warning(f"Erreur sauvegarde certificat en DB: {db_error}")
                certificate_id = None
            
            return {
                "success": True,
                "certificate_id": certificate_id,
                "certificate_code": certificate_code,
                "certificate_url": certificate_url,
                "is_global": True,
                "courses_completed": completed_count,
                "total_courses": total_courses,
                "completion_percentage": completion_percentage,
                "message": f"Certificat global généré avec succès ! {completed_count}/{total_courses} cours complétés."
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur génération certificat global: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération du certificat global: {str(e)}"
        )


@app.get("/certificates/global/status")
async def get_global_certificate_status(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Vérifie si l'utilisateur peut obtenir un certificat global
    """
    try:
        async with db.get_connection() as conn:
            
            total_courses = await conn.fetchval("""
                SELECT COUNT(*) FROM cours_html WHERE est_actif = true
            """)
            
            
            completed_count = await conn.fetchval("""
                SELECT COUNT(DISTINCT cours_id) 
                FROM resultats_apprentissage 
                WHERE utilisateur_id = $1 AND est_reussi = true
            """, current_user.id)
            
            completed_count = completed_count or 0
            
            
            cert_exists = await conn.fetchval("""
                SELECT COUNT(*) FROM certificats 
                WHERE user_id = $1 AND course_id = 0
            """, current_user.id)
            
            completion_percentage = (completed_count / total_courses) * 100 if total_courses > 0 else 0
            can_generate = completion_percentage >= 50
            
            return {
                "total_courses": total_courses,
                "completed_courses": completed_count,
                "completion_percentage": round(completion_percentage, 1),
                "can_generate": can_generate,
                "certificate_exists": cert_exists > 0,
                "message": "Vous pouvez générer votre certificat global !" if can_generate else 
                          f"Complétez au moins 50% des cours ({int(total_courses * 0.5)}/{total_courses})"
            }
    except Exception as e:
        logger.error(f"Erreur vérification certificat global: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la vérification"
        )

@app.get("/certificates/download/{code}")
async def download_certificate(
    code: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Télécharge un certificat en tant que fichier image
    """
    try:
        certificate = await db.get_certificate_by_code(code)
        
        if not certificate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certificat non trouvé"
            )
        
        if certificate['user_id'] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous n'avez pas accès à ce certificat"
            )
        
        cert_url = certificate.get('certificate_url')
        if cert_url and cert_url.startswith('data:image/png;base64,'):
            base64_data = cert_url.replace('data:image/png;base64,', '')
            img_data = base64.b64decode(base64_data)
            
            from fastapi.responses import Response
            return Response(
                content=img_data,
                media_type="image/png",
                headers={
                    "Content-Disposition": f"attachment; filename=certificat_{code}.png"
                }
            )
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image du certificat non disponible"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur téléchargement certificat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du téléchargement du certificat"
        )

@app.get("/certificates/check/{course_id}")
async def check_certificate_exists(
    course_id: int,
    mode: str = Query(..., description="Mode d'apprentissage: texte, audio, video"),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Vérifie si un certificat existe déjà pour un cours et un mode
    """
    try:
        exists = await db.certificate_exists(current_user.id, course_id, mode)
        return {
            "exists": exists,
            "user_id": current_user.id,
            "course_id": course_id,
            "mode": mode
        }
    except Exception as e:
        logger.error(f"Erreur vérification certificat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la vérification"
        )


@app.post("/mistakes/save")
async def save_mistake(
    mistake_data: Dict[str, Any] = Body(...),
    current_user: UserInDB = Depends(get_current_user)
):
    
    try:
        async with db.get_connection() as conn:
            mistake_id = await db.save_user_mistake(
                conn,
                utilisateur_id=current_user.id,
                cours_id=mistake_data.get('cours_id'),
                question_id=mistake_data.get('question_id'),
                question_texte=mistake_data.get('question_texte'),
                reponse_utilisateur=mistake_data.get('reponse_utilisateur'),
                reponse_correcte=mistake_data.get('reponse_correcte'),
                mode_apprentissage=mistake_data.get('mode_apprentissage', 'audio'),
                score_obtenu=mistake_data.get('score_obtenu', 0),
                points_possibles=mistake_data.get('points_possibles', 10)
            )
            
            return {
                "status": "success",
                "mistake_id": mistake_id,
                "message": "Erreur enregistrée avec succès"
            }
    except Exception as e:
        logger.error(f"Erreur sauvegarde mistake: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mistakes/batch-save")
async def save_batch_mistakes(
    request: Dict[str, Any] = Body(...),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        mistakes = request.get('mistakes', [])
        saved_count = 0
        
        async with db.get_connection() as conn:
            for mistake in mistakes:
                result = await db.save_user_mistake(
                    conn=conn,
                    utilisateur_id=current_user.id,
                    cours_id=mistake.get('cours_id'),
                    question_id=mistake.get('question_id'),
                    question_texte=mistake.get('question_texte'),
                    reponse_utilisateur=mistake.get('reponse_utilisateur'),
                    reponse_correcte=mistake.get('reponse_correcte'),
                    mode_apprentissage=mistake.get('mode_apprentissage', 'audio'),
                    score_obtenu=mistake.get('score_obtenu', 0),
                    points_possibles=mistake.get('points_possibles', 10)
                )
                if result:
                    saved_count += 1
        
        return {
            "status": "success",
            "saved_count": saved_count,
            "message": f"{saved_count} erreur(s) enregistrée(s)"
        }
    except Exception as e:
        logger.error(f"Erreur batch sauvegarde: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mistakes/my-mistakes")
async def get_my_mistakes(
    cours_id: Optional[int] = None,
    mode: Optional[str] = None,
    limit: int = 30,
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        async with db.get_connection() as conn:
            mistakes = await db.get_user_mistakes(
                conn=conn,
                utilisateur_id=current_user.id,
                cours_id=cours_id,
                mode=mode,
                limit=limit
            )
            
            return {
                "status": "success",
                "mistakes": mistakes,
                "count": len(mistakes)
            }
    except Exception as e:
        logger.error(f"Erreur récupération mistakes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mistakes/my-stats")
async def get_my_mistakes_stats(
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        async with db.get_connection() as conn:
            stats = await db.get_user_mistakes_stats(
                conn=conn,
                utilisateur_id=current_user.id
            )
            
            return {
                "status": "success",
                "stats": stats
            }
    except Exception as e:
        logger.error(f"Erreur récupération stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mistakes/mark-revised")
async def mark_mistake_revised(
    data: dict,
    current_user: UserInDB = Depends(get_current_user)
):
    
    try:
        erreur_id = data.get('erreur_id')
        if not erreur_id:
            raise HTTPException(status_code=400, detail="erreur_id requis")
        
        async with db.get_connection() as conn:
            success = await db.mark_mistake_as_revised(
                conn, erreur_id, current_user.id
            )
            
            return {
                "status": "success",
                "revised": success,
                "message": "Erreur marquée comme révisée" if success else "Erreur non trouvée"
            }
    except Exception as e:
        logger.error(f"Erreur marquage révision: {e}")
        raise HTTPException(status_code=500, detail=str(e))




@app.post("/bert/quiz-from-mistakes")
async def bert_generate_quiz_from_mistakes(
    request: Dict[str, Any] = Body(...),
    current_user: UserInDB = Depends(get_current_user)
):
    
    
    
    course_id = request.get('course_id')
    mode = request.get('mode', 'audio')
    num_questions = request.get('num_questions', 5)
    
    if not bert_tutor.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Le tuteur BERT n'est pas encore initialisé"
        )
    
    
    async with db.get_connection() as conn:
        mistakes_data = await db.get_user_mistakes(
            conn=conn,
            utilisateur_id=current_user.id,
            cours_id=int(course_id) if course_id else None,
            mode=mode,
            limit=20
        )
    
    if not mistakes_data:
        
        quiz = bert_tutor.generate_quiz(course_id, min(num_questions, 10))
        return {
            "status": "success",
            "course_id": course_id,
            "mistakes_count": 0,
            "mode": mode,
            "questions_count": len(quiz.get('questions', [])),
            "quiz": quiz
        }
    
    
    mistakes = [m['question_texte'] for m in mistakes_data]
    
    
    concepts = []
    for mistake in mistakes:
        concept = mistake.replace("Quelle", "").replace("Comment", "").replace("?", "").strip()
        concepts.append(concept[:100])
    
    
    quiz = bert_tutor.generate_quiz_from_concepts(concepts, course_id, num_questions, mode)
    
    if not quiz:
        quiz = bert_tutor.generate_quiz(course_id, min(num_questions, 10))
    
    return {
        "status": "success",
        "course_id": course_id,
        "mistakes_count": len(mistakes),
        "mode": mode,
        "questions_count": len(quiz.get('questions', [])),
        "quiz": quiz
    }

@app.get("/bert/test/{course_id}")
async def bert_test_quiz(
    course_id: str,
    n: int = Query(3, ge=1, le=5),
    current_user: UserInDB = Depends(get_current_user)
):
    
    try:
        quiz = bert_tutor.generate_quiz(course_id, n)
        if not quiz:
            return {"error": f"Cours {course_id} non trouvé", "status": "error"}
        return {
            "status": "success",
            "course_id": course_id,
            "questions_count": len(quiz.get('questions', [])),
            "quiz": quiz
        }
    except Exception as e:
        logger.error(f"Erreur test BERT: {e}")
        return {"error": str(e), "status": "error"}

@app.get("/bert/status")
async def bert_status():
    
    return {
        "loaded": bert_tutor.is_ready(),
        "cours_count": len(bert_tutor.cours_ids) if bert_tutor.cours_ids else 0,
        "questions_count": len(bert_tutor.questions_texts) if bert_tutor.questions_texts else 0,
        "model": config.BERT_MODEL_NAME
    }


@app.post("/bert/recommend")
async def bert_recommend(
    request: Dict[str, Any] = Body(...),
    current_user: UserInDB = Depends(get_current_user)
):
    
    
    
    
    questions_echouees = request.get('questions_echouees', [])
    seuil = request.get('seuil', 0.50)
    top_n = request.get('top_n', 5)
    
    if not bert_tutor.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Le tuteur BERT n'est pas encore initialisé"
        )
    
    if not questions_echouees:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La liste des questions échouées est vide"
        )
    
    recommendations = bert_tutor.recommend_courses(questions_echouees, seuil, top_n)
    
    return {
        'user_id': current_user.id,
        'questions_count': len(questions_echouees),
        'seuil': seuil,
        'recommendations': recommendations,
        'generated_by': 'BERT'
    }


@app.get("/bert/quiz/{course_id}")
async def bert_generate_quiz(
    course_id: str,
    n: int = Query(5, ge=1, le=20, description="Nombre de questions (max 20)"),  
    difficulte: Optional[str] = Query(None, pattern="^(facile|moyen|difficile)$", description="Filtre par difficulté"),
    current_user: UserInDB = Depends(get_current_user)
):
    
    if not bert_tutor.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Le tuteur BERT n'est pas encore initialisé"
        )
    
    
    n = min(n, 20)
    
    quiz = bert_tutor.generate_quiz(course_id, n, difficulte)
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cours {course_id} non trouvé ou aucune question disponible"
        )
    
    return quiz


@app.get("/bert/analyze")
async def bert_analyze_my_learning(
    current_user: UserInDB = Depends(get_current_user)
):
    
    if not bert_tutor.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Le tuteur BERT n'est pas encore initialisé"
        )
    
    
    results = await db.get_user_learning_results(current_user.id)
    
    analysis = bert_tutor.analyze_learning_patterns(results)
    
    return {
        'user_id': current_user.id,
        'analysis': analysis,
        'generated_by': 'BERT'
    }


@app.post("/bert/analyze/{user_id}")
async def bert_analyze_user(
    user_id: int,
    current_user: UserInDB = Depends(require_admin)
):
    
    if not bert_tutor.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Le tuteur BERT n'est pas encore initialisé"
        )
    
    results = await db.get_user_learning_results(user_id)
    analysis = bert_tutor.analyze_learning_patterns(results)
    
    return {
        'user_id': user_id,
        'analysis': analysis,
        'generated_by': 'BERT'
    }


@app.post("/bert/reload")
async def bert_reload_embeddings(
    current_user: UserInDB = Depends(require_admin)
):
    
    try:
        success = bert_tutor.load_embeddings()
        if success:
            return {"message": "Embeddings BERT rechargés avec succès", "status": "ok"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors du rechargement des embeddings"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )

@app.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    current_user: UserInDB = Depends(require_admin)
):
    
    try:
        
        users = await db.get_users_with_stats(limit, skip)
        
        if active_only:
            users = [u for u in users if u.get('est_actif', True)]
        
        
        formatted_users = []
        for user in users:
            formatted_users.append({
                "id": user.get('id'),
                "email": user.get('email', ''),
                "nom": user.get('nom', ''),
                "prenom": user.get('prenom', ''),
                "role_name": user.get('role_name', 'utilisateur'),
                "role_id": user.get('role_id', 2),
                "total_results": user.get('total_results', 0),
                "avg_score": float(user.get('avg_score', 0)) if user.get('avg_score') else 0,
                "est_actif": user.get('est_actif', True),
                "date_inscription": user.get('date_inscription'),
                "derniere_connexion": user.get('derniere_connexion')
            })
        
        return formatted_users
        
    except Exception as e:
        logger.error(f"Erreur récupération utilisateurs: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des utilisateurs: {str(e)}"
        )
    



@app.get("/behavior/sequential-analysis")
async def get_sequential_analysis(current_user: UserInDB = Depends(get_current_user)):
    
    
    
    
    try:
        async with db.get_connection() as conn:
            
            query = """
            SELECT 
                utilisateur_id as user_id,
                mode as action,
                date_completion as timestamp
            FROM resultats_apprentissage
            WHERE utilisateur_id = $1
            ORDER BY date_completion
            LIMIT 100
            """
            rows = await conn.fetch(query, current_user.id)
            
            if not rows or len(rows) < 5:
                return {
                    'status': 'insufficient_data',
                    'message': 'Pas assez de données pour analyser les patterns',
                    'dropout_risk': {'level': 'Inconnu', 'score': 0, 'factors': []},
                    'total_sessions': 0,
                    'total_actions': 0,
                    'engagement_level': 'Normal',
                    'risk_patterns': [],
                    'recommendations': [
                        "📚 Complétez plus de cours pour une analyse précise",
                        "🎯 Passez des quiz pour améliorer votre progression"
                    ]
                }
            
            
            import pandas as pd
            logs_df = pd.DataFrame([dict(row) for row in rows])
            
            
            
            action_mapping = {
                'texte': 'read_content',
                'audio': 'listen_audio',
                'video': 'watch_video'
            }
            
            
            logs_df['action'] = logs_df['action'].map(action_mapping).fillna('study')
            
            
            sequences = sequential_miner.extract_sequences(logs_df)
            
            
            all_actions = []
            for session in sequences:
                all_actions.extend(session)
            
            risk = sequential_miner.predict_dropout_risk(all_actions)
            
            
            patterns = sequential_miner.mine_sequential_patterns(sequences)
            
            
            risk_patterns = []
            for pattern in patterns[:5]:
                for item in pattern.keys():
                    if isinstance(item, tuple):
                        actions = list(item)
                        risk_patterns.append({
                            'pattern': actions,
                            'support': list(pattern.values())[0]
                        })
            
            
            total_actions = len(all_actions)
            if total_actions < 10:
                engagement_level = "Faible"
            elif total_actions < 30:
                engagement_level = "Modéré"
            else:
                engagement_level = "Bon"
            
            return {
                'status': 'success',
                'user_id': current_user.id,
                'total_sessions': len(sequences),
                'total_actions': total_actions,
                'dropout_risk': {
                    'score': risk['risk_score'],
                    'level': risk['risk_level'],
                    'factors': risk['risk_factors']
                },
                'engagement_level': engagement_level,
                'risk_patterns': risk_patterns[:3],
                'recommendations': _get_behavior_sequential_recommendations(risk['risk_level'])
            }
        
    except Exception as e:
        logger.error(f"Erreur analyse séquentielle: {e}")
        logger.error(traceback.format_exc())
        return {
            'status': 'error',
            'message': 'Service temporairement indisponible',
            'dropout_risk': {'level': 'Inconnu', 'score': 0, 'factors': []},
            'total_sessions': 0,
            'total_actions': 0,
            'engagement_level': 'Normal',
            'risk_patterns': [],
            'recommendations': [
                '🔄 Réessayez plus tard',
                '📧 Contactez le support si le problème persiste'
            ]
        }

@app.get("/behavior/my-analysis")
async def get_my_behavior_analysis(current_user: UserInDB = Depends(get_current_user)):
    
    
    
    try:
        async with db.get_connection() as conn:
            
            query = """
            SELECT 
                mode,
                COUNT(*) as count,
                AVG(score_quiz) as avg_score,
                AVG(taux_completion) as avg_completion,
                SUM(CASE WHEN est_reussi THEN 1 ELSE 0 END) as success_count
            FROM resultats_apprentissage
            WHERE utilisateur_id = $1
            GROUP BY mode
            """
            rows = await conn.fetch(query, current_user.id)
            
            if not rows:
                return {
                    'status': 'no_data',
                    'message': 'Aucune donnée disponible',
                    'preferred_content': 'inconnu',
                    'dropout_risk': {'level': 'Faible', 'score': 0, 'factors': []}
                }
            
            
            mode_stats = {}
            best_mode = None
            best_score = -1
            
            for row in rows:
                mode = row['mode']
                count = row['count']
                avg_score = float(row['avg_score']) if row['avg_score'] else 0
                avg_completion = float(row['avg_completion']) if row['avg_completion'] else 0
                success_rate = (row['success_count'] / count) * 100 if count > 0 else 0
                
                combined_score = avg_score * 0.6 + success_rate * 0.3 + avg_completion * 0.1
                
                mode_stats[mode] = {
                    'count': count,
                    'avg_score': round(avg_score, 1),
                    'avg_completion': round(avg_completion, 1),
                    'success_rate': round(success_rate, 1),
                    'combined_score': round(combined_score, 2)
                }
                
                if avg_score > best_score:
                    best_score = avg_score
                    best_mode = mode
                elif avg_score == best_score and best_mode:
                    current_count = count
                    best_count = mode_stats.get(best_mode, {}).get('count', 0)
                    if current_count > best_count:
                        best_mode = mode
            
            
            total_results = sum(s['count'] for s in mode_stats.values())
            success_count = sum(r['success_count'] for r in rows)
            success_rate = (success_count / total_results) * 100 if total_results > 0 else 0
            
            risk_score = 0
            risk_factors = []
            
            if success_rate < 50:
                risk_score += 0.4
                risk_factors.append("📉 Taux de réussite faible")
            elif success_rate < 70:
                risk_score += 0.2
                risk_factors.append("📈 Taux de réussite moyen")
            else:
                risk_factors.append("🌟 Bon taux de réussite")
            
            if total_results < 5:
                risk_score += 0.2
                risk_factors.append("📚 Peu de modules complétés")
            
            if risk_score >= 0.7:
                risk_level = "Élevé"
            elif risk_score >= 0.4:
                risk_level = "Modéré"
            else:
                risk_level = "Faible"
            
            
            mode_to_learner_type = {
                'video': 'visuel',
                'audio': 'auditif',
                'texte': 'lecture'
            }
            
            detected_type = mode_to_learner_type.get(best_mode, 'mixte')
            preferred_mode = best_mode
            
            return {
                'status': 'success',
                'user_id': current_user.id,
                'total_actions': total_results,
                'preferred_content': preferred_mode,
                'detected_learner_type': detected_type,
                'mode_stats': mode_stats,
                'dropout_risk': {
                    'score': round(risk_score, 2),
                    'level': risk_level,
                    'factors': risk_factors
                },
                'engagement_score': round((1 - risk_score) * 100, 1),
                'recommendations': _get_recommendations(best_mode, risk_level, success_rate)  # ✅ Utilise la bonne fonction
            }
        
    except Exception as e:
        logger.error(f"Erreur: {e}")
        return {
            'status': 'error',
            'preferred_content': 'inconnu',
            'dropout_risk': {'level': 'Faible', 'score': 0, 'factors': []}
        }




def _get_recommendations(preferred_mode: str, risk_level: str, success_rate: float) -> list:
    """Génère des recommandations basées sur les données réelles"""
    
    mode_names = {'video': 'vidéo', 'audio': 'audio', 'texte': 'texte'}
    mode_emoji = {'video': '🎬', 'audio': '🎧', 'texte': '📖'}
    
    recommendations = []
    
    
    if preferred_mode in mode_names:
        recommendations.append(
            f"{mode_emoji[preferred_mode]} Vous excellez dans le mode {mode_names[preferred_mode]} ! "
            f"Continuez avec les cours en {mode_names[preferred_mode]} pour maximiser votre apprentissage."
        )
    
    
    if risk_level == 'Élevé':
        recommendations.append("⚠️ Votre progression ralentit. Fixez-vous des objectifs quotidiens.")
        recommendations.append("📅 Planifiez des sessions d'étude courtes mais régulières")
        recommendations.append("💬 N'hésitez pas à demander de l'aide sur les forums")
    elif risk_level == 'Modéré':
        recommendations.append("📈 Bonne progression ! Essayez d'alterner les formats d'apprentissage.")
        recommendations.append("✅ Vous êtes sur la bonne voie, continuez vos efforts")
        recommendations.append("📝 Prenez des notes pour mieux mémoriser")
    else:
        recommendations.append("🌟 Excellent travail ! Les cours avancés vous permettront d'approfondir.")
        recommendations.append("🚀 Passez aux exercices avancés")
        recommendations.append("🏆 Relevez de nouveaux défis")
    
    
    if success_rate > 85:
        recommendations.append("🎯 Vous maîtrisez bien les bases. Passez aux exercices avancés !")
    elif success_rate < 60:
        recommendations.append("📚 Revoyez les fondamentaux avant de passer aux chapitres suivants.")
    
    return recommendations[:5]  

def _get_behavior_sequential_recommendations(risk_level: str) -> list:
    
    if risk_level == 'Élevé':
        return [
            "📅 Planifiez des sessions d'étude courtes mais régulières",
            "🎯 Fixez-vous des objectifs quotidiens réalisables",
            "💬 N'hésitez pas à demander de l'aide sur les forums",
            "📚 Revenez sur les concepts de base avant de continuer"
        ]
    elif risk_level == 'Modéré':
        return [
            "✅ Vous êtes sur la bonne voie, continuez vos efforts",
            "🎮 Alternez entre différents types de contenu",
            "📝 Prenez des notes pour mieux mémoriser"
        ]
    else:
        return [
            "🌟 Excellent rythme d'apprentissage !",
            "🚀 Passez aux exercices avancés",
            "🏆 Relevez de nouveaux défis"
        ]



async def _get_user_metrics(user_id: int) -> Dict:
    
    try:
        async with db.get_connection() as conn:
            query = """
            SELECT 
                mode,
                COALESCE(AVG(score_quiz), 0) as avg_score,
                COUNT(*) as sessions,
                COALESCE(AVG(taux_completion), 0) as avg_completion,
                COALESCE(SUM(CASE WHEN est_reussi THEN 1 ELSE 0 END)::float / NULLIF(COUNT(*), 0), 0) as success_rate
            FROM resultats_apprentissage
            WHERE utilisateur_id = $1
            GROUP BY mode
            """
            rows = await conn.fetch(query, user_id)
            
            metrics = {
                'text': {'avg_score': 0, 'sessions': 0, 'avg_completion': 0, 'success_rate': 0},
                'audio': {'avg_score': 0, 'sessions': 0, 'avg_completion': 0, 'success_rate': 0},
                'video': {'avg_score': 0, 'sessions': 0, 'avg_completion': 0, 'success_rate': 0}
            }
            
            for row in rows:
                mode = row['mode']
                if mode == 'texte':
                    metrics['text'] = {
                        'avg_score': float(row['avg_score']) if row['avg_score'] else 0,
                        'sessions': row['sessions'] or 0,
                        'avg_completion': float(row['avg_completion']) if row['avg_completion'] else 0,
                        'success_rate': float(row['success_rate']) if row['success_rate'] else 0
                    }
                elif mode == 'audio':
                    metrics['audio'] = {
                        'avg_score': float(row['avg_score']) if row['avg_score'] else 0,
                        'sessions': row['sessions'] or 0,
                        'avg_completion': float(row['avg_completion']) if row['avg_completion'] else 0,
                        'success_rate': float(row['success_rate']) if row['success_rate'] else 0
                    }
                elif mode == 'video':
                    metrics['video'] = {
                        'avg_score': float(row['avg_score']) if row['avg_score'] else 0,
                        'sessions': row['sessions'] or 0,
                        'avg_completion': float(row['avg_completion']) if row['avg_completion'] else 0,
                        'success_rate': float(row['success_rate']) if row['success_rate'] else 0
                    }
            
            
            logger.info(f"Métriques pour user {user_id}: texte={metrics['text']['avg_score']:.1f}%, audio={metrics['audio']['avg_score']:.1f}%, video={metrics['video']['avg_score']:.1f}%")
            
            return metrics
    except Exception as e:
        logger.error(f"Erreur récupération métriques: {e}")
        return {
            'text': {'avg_score': 0, 'sessions': 0, 'avg_completion': 0, 'success_rate': 0},
            'audio': {'avg_score': 0, 'sessions': 0, 'avg_completion': 0, 'success_rate': 0},
            'video': {'avg_score': 0, 'sessions': 0, 'avg_completion': 0, 'success_rate': 0}
        }

@app.get("/recommend/sync-profile")
async def sync_learning_profile(current_user: UserInDB = Depends(get_current_user)):
    
    
    
    try:
        
        metrics = await _get_user_metrics(current_user.id)
        
        
        async with db.get_connection() as conn:
            query = """
            SELECT mode, COUNT(*) as count, AVG(score_quiz) as avg_score
            FROM resultats_apprentissage
            WHERE utilisateur_id = $1
            GROUP BY mode
            ORDER BY count DESC
            LIMIT 1
            """
            best_mode_row = await conn.fetchrow(query, current_user.id)
            
            actual_preferred = best_mode_row['mode'] if best_mode_row else 'mixte'
            actual_score = best_mode_row['avg_score'] if best_mode_row else 0
        
        
        type_mapping = {
            'video': 'visuel',
            'audio': 'auditif',
            'texte': 'lecture'
        }
        
        new_type = type_mapping.get(actual_preferred, 'mixte')
        
        if current_user.type_apprenant != new_type:
            await db.update("utilisateurs", current_user.id, {"type_apprenant": new_type})
            logger.info(f"✅ Type d'apprenant mis à jour: {current_user.type_apprenant} → {new_type}")
        
        return {
            'status': 'success',
            'previous_type': current_user.type_apprenant,
            'new_type': new_type,
            'preferred_mode': actual_preferred,
            'avg_score': round(actual_score, 1),
            'message': f"Profil mis à jour: {new_type} (basé sur {actual_preferred})"
        }
        
    except Exception as e:
        logger.error(f"Erreur synchronisation profil: {e}")
        return {'status': 'error', 'message': str(e)}

@app.post("/sequential/analyze")
async def sequential_analyze_user(
    user_actions: List[str] = Body(..., embed=True),
    threshold: float = Body(0.60, embed=True),
    current_user: UserInDB = Depends(get_current_user)
):
    
    
    
    
    risk = sequential_miner.predict_dropout_risk(user_actions, threshold)
    
    
    await db.execute("""
        INSERT INTO logs_comportement (utilisateur_id, actions, risque_score, risque_niveau, date_analyse)
        VALUES ($1, $2, $3, $4, CURRENT_TIMESTAMP)
    """, current_user.id, user_actions, risk['risk_score'], risk['risk_level'])
    
    return {
        'user_id': current_user.id,
        **risk,
        'timestamp': datetime.now().isoformat()
    }


@app.post("/sequential/train")
async def sequential_train(
    logs_data: List[Dict[str, Any]] = Body(...),
    current_user: UserInDB = Depends(require_admin)
):
    
    
    
    
    try:
        df = pd.DataFrame(logs_data)
        
        
        sequences = sequential_miner.extract_sequences(df)
        
        
        sequential_miner.mine_sequential_patterns(sequences)
        
        
        sequential_miner.generate_rules(sequences)
        
        
        sequential_miner.save('./tutor_ia_model/sequential_miner.pkl')
        
        return {
            'message': 'Modèle Sequential Pattern Miner entraîné avec succès',
            'sequences_count': len(sequences),
            'patterns_count': len(sequential_miner.patterns),
            'rules_count': len(sequential_miner.rules)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'entraînement: {str(e)}"
        )


@app.post("/sequential/simulate")
async def sequential_simulate(
    n_users: int = Body(10, embed=True),
    n_actions: int = Body(30, embed=True),
    current_user: UserInDB = Depends(require_admin)
):
    
    from ml.sequential_miner import generate_sample_logs
    
    logs = generate_sample_logs(n_users, n_actions)
    logs_dict = logs.to_dict('records')
    
    sequences = sequential_miner.extract_sequences(logs)
    sequential_miner.mine_sequential_patterns(sequences)
    sequential_miner.generate_rules(sequences)
    
    
    results = []
    for uid, group in logs.groupby('user_id'):
        user_seq = group.sort_values('timestamp')['action'].tolist()
        risk = sequential_miner.predict_dropout_risk(user_seq)
        results.append({
            'user_id': int(uid),
            'risk_level': risk['risk_level'],
            'risk_score': risk['risk_score'],
            'risk_factors': risk['risk_factors'][:3]
        })
    
    return {
        'simulation': {
            'n_users': n_users,
            'n_actions': n_actions,
            'total_logs': len(logs),
            'sequences_count': len(sequences),
            'patterns_count': len(sequential_miner.patterns),
            'rules_count': len(sequential_miner.rules)
        },
        'dropout_analysis': results
    }

@app.get("/sequential/user/{user_id}/risk")
async def sequential_get_user_risk(
    user_id: int,
    current_user: UserInDB = Depends(get_current_user)
):
    
    
    
    
    if current_user.id != user_id and current_user.role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à ces données"
        )
    
    try:
        async with db.get_connection() as conn:
            rows = await conn.fetch("""
                SELECT id, risque_score, risque_niveau, facteurs, date_analyse
                FROM analyses_comportement
                WHERE utilisateur_id = $1
                ORDER BY date_analyse DESC
                LIMIT 20
            """, user_id)
            
            history = []
            for row in rows:
                history.append({
                    'id': row['id'],
                    'risk_score': float(row['risque_score']),
                    'risk_level': row['risque_niveau'],
                    'risk_factors': row['facteurs'],
                    'date': row['date_analyse'].isoformat()
                })
            
            
            trend = 'stable'
            if len(history) >= 2:
                if history[0]['risk_score'] > history[1]['risk_score']:
                    trend = 'increasing'
                elif history[0]['risk_score'] < history[1]['risk_score']:
                    trend = 'decreasing'
            
            return {
                'user_id': user_id,
                'current_risk': history[0] if history else None,
                'history': history,
                'trend': trend,
                'total_analyses': len(history)
            }
    except Exception as e:
        logger.error(f"Erreur récupération historique: {e}")
        return {
            'user_id': user_id,
            'current_risk': None,
            'history': [],
            'trend': 'unknown',
            'total_analyses': 0
        }

@app.get("/sequential/patterns")
async def sequential_get_patterns(
    limit: int = Query(50, ge=1, le=200),
    current_user: UserInDB = Depends(require_admin)
):
    
    patterns = sequential_miner.patterns[:limit]
    return {
        'total_patterns': len(sequential_miner.patterns),
        'patterns': patterns
    }

@app.get("/sequential/status")
async def sequential_status(current_user: UserInDB = Depends(get_current_user)):
    
    return {
        'loaded': len(sequential_miner.rules) > 0 or len(sequential_miner.patterns) > 0,
        'patterns_count': len(sequential_miner.patterns),
        'rules_count': len(sequential_miner.rules),
        'min_support': sequential_miner.min_support,
        'min_confidence': sequential_miner.min_confidence
    }

@app.get("/sequential/rules")
async def sequential_get_rules(
    limit: int = Query(20, ge=1, le=100),
    current_user: UserInDB = Depends(require_admin)
):
    
    return {
        'total_rules': len(sequential_miner.rules),
        'rules': sequential_miner.rules[:limit],
        'min_support': sequential_miner.min_support,
        'min_confidence': sequential_miner.min_confidence
    }

@app.post("/sequential/save")
async def sequential_save_model(
    current_user: UserInDB = Depends(require_admin)
):
    
    success = sequential_miner.save('./tutor_ia_model/sequential_miner.pkl')
    if success:
        return {
            'status': 'success',
            'message': 'Modèle sauvegardé avec succès',
            'patterns_count': len(sequential_miner.patterns),
            'rules_count': len(sequential_miner.rules)
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la sauvegarde du modèle"
        )



@app.get("/recommend/test")
async def recommend_test():
    
    return {
        'message': 'API de recommandation fonctionne',
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    }

@app.get("/recommend/learning-mode")
async def recommend_learning_mode_direct(current_user: UserInDB = Depends(get_current_user)):
    
    
    
    try:
        
        metrics = await _get_user_metrics(current_user.id)
        
        logger.info(f"Métriques pour {current_user.email}: texte={metrics['text']['avg_score']:.1f}%, audio={metrics['audio']['avg_score']:.1f}%, video={metrics['video']['avg_score']:.1f}%")
        
        
        has_data = any(m['sessions'] > 0 for m in metrics.values())
        
        if not has_data:
            return _get_default_recommendation()
        
        
        recommendation = recommender.predict_best_mode(metrics, None)
        
        
        recommendation['user_id'] = current_user.id
        recommendation['user_name'] = f"{current_user.prenom} {current_user.nom}"
        recommendation['timestamp'] = datetime.now().isoformat()
        
        
        mode_scores = {
            'texte': metrics.get('text', {}).get('avg_score', 0),
            'audio': metrics.get('audio', {}).get('avg_score', 0),
            'video': metrics.get('video', {}).get('avg_score', 0)
        }
        
        
        best_score_value = max(mode_scores.values())
        best_modes = [m for m, s in mode_scores.items() if s == best_score_value]
        
        
        if len(best_modes) > 1:
            sessions = {mode: metrics.get(mode, {}).get('sessions', 0) for mode in best_modes}
            best_real_mode = max(sessions, key=sessions.get)
        else:
            best_real_mode = best_modes[0]
        
        
        mode_to_learner = {
            'texte': 'lecture',
            'audio': 'auditif',
            'video': 'visuel'
        }
        
        detected_type = mode_to_learner.get(best_real_mode, 'mixte')
        
        
        if current_user.type_apprenant != detected_type:
            await db.update("utilisateurs", current_user.id, {"type_apprenant": detected_type})
            logger.info(f"✅ Type apprenant mis à jour: {current_user.type_apprenant} → {detected_type}")
        
        logger.info(f"✅ Recommandation générée: mode={recommendation.get('recommended_mode')} (score: {mode_scores[best_real_mode]:.1f}%)")
        
        return recommendation
        
    except Exception as e:
        logger.error(f"❌ Erreur dans recommend_learning_mode: {e}")
        logger.error(traceback.format_exc())
        return _get_default_recommendation()



def _get_default_recommendation() -> Dict:
    
    return {
        'recommended_mode': 'video',
        'learner_type': 'visuel',
        'recommended_title': '🎬 Commencez avec la Vidéo',
        'confidence': 0.5,
        'confidence_text': 'Moyenne',
        'message': 'Commencez votre apprentissage avec les vidéos pour une introduction visuelle.',
        'scores': {'text': 33.3, 'audio': 33.3, 'video': 33.4},
        'metrics': {'text': 0, 'audio': 0, 'video': 0}
    }

@app.get("/recommend/debug/{user_id}")
async def recommend_debug(user_id: int, current_user: UserInDB = Depends(require_admin)):
    
    try:
        metrics = get_user_metrics_direct(user_id)
        
        return {
            'user_id': user_id,
            'metrics': metrics,
            'has_data': any(m['sessions'] > 0 for m in metrics.values()) if metrics else False,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {'error': str(e)}


@app.get("/static/list")
async def list_static_files():
    
    try:
        files = []
        static_dir = "static"
        
        
        audio_dir = os.path.join(static_dir, "audio")
        if os.path.exists(audio_dir):
            for filename in os.listdir(audio_dir):
                if filename.endswith('.mp3'):
                    file_path = os.path.join(audio_dir, filename)
                    files.append({
                        "name": filename,
                        "path": f"audio/{filename}",
                        "type": "audio",
                        "size": os.path.getsize(file_path),
                        "url": f"/static/audio/{filename}"
                    })
        
        
        if os.path.exists(static_dir):
            for filename in os.listdir(static_dir):
                if filename.endswith('.mp3') and filename not in [f["name"] for f in files]:
                    file_path = os.path.join(static_dir, filename)
                    files.append({
                        "name": filename,
                        "path": filename,
                        "type": "audio",
                        "size": os.path.getsize(file_path),
                        "url": f"/static/{filename}"
                    })
        
        files.sort(key=lambda x: x['name'])
        
        return {
            "directory": static_dir,
            "total_files": len(files),
            "files": files
        }
    except Exception as e:
        logger.error(f"Erreur: {e}")
        return {"directory": "static", "total_files": 0, "files": []}

@app.get("/static/audio/list")
async def list_audio_files():
    
    try:
        audio_dir = os.path.join("static", "audio")
        audio_files = []
        
        if os.path.exists(audio_dir):
            for filename in os.listdir(audio_dir):
                if filename.endswith('.mp3'):
                    file_path = os.path.join(audio_dir, filename)
                    audio_files.append({
                        "name": filename,
                        "path": f"audio/{filename}",
                        "size": os.path.getsize(file_path),
                        "url": f"/static/audio/{filename}",
                        "type": "audio"
                    })
        else:
            
            os.makedirs(audio_dir, exist_ok=True)
        
        audio_files.sort(key=lambda x: x['name'])
        
        return {
            "total": len(audio_files),
            "files": audio_files
        }
    except Exception as e:
        logger.error(f"Erreur: {e}")
        return {"total": 0, "files": []}



STATIC_DIR = "static"
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    logger.info(f"✅ Fichiers statiques montés sur /static depuis '{STATIC_DIR}'")
else:
    logger.warning(f"⚠️  Dossier '{STATIC_DIR}' non trouvé - Création...")
    os.makedirs(STATIC_DIR, exist_ok=True)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    logger.info(f"📁 Dossier '{STATIC_DIR}' créé et fichiers statiques montés")


security = HTTPBearer()



async def log_admin_action(
    admin_id: int, 
    action: str, 
    table: str, 
    record_id: Optional[int] = None,
    details: Optional[Dict] = None
):
    
    try:
        async with db.get_connection() as conn:
            await conn.execute(
                """
                INSERT INTO logs_admin (admin_id, action, table_affectee, id_ligne, details)
                VALUES ($1, $2, $3, $4, $5)
                """,
                admin_id, action, table, record_id, json.dumps(details) if details else None
            )
    except Exception as e:
        logger.error(f"Erreur lors du logging: {e}")

@app.get("/debug/token")
async def debug_token(authorization: Optional[str] = Header(None)):
    
    if not authorization:
        return {"error": "Pas d'en-tête Authorization"}
    
    
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    
    return {
        "authorization_header": authorization,
        "token_received": token,
        "token_length": len(token),
        "segments": len(token.split('.')),
        "is_jwt_format": len(token.split('.')) == 3,
        "raw_segments": token.split('.')
    }



@app.post("/auth/public-register", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def register_public_user(user_data: UserCreate):
    
    
    
    try:
        logger.info("=" * 50)
        logger.info("📝 DÉBUT INSCRIPTION PUBLIQUE")
        logger.info("=" * 50)
        
        
        logger.info(f"1. Données reçues:")
        logger.info(f"   Email: {user_data.email}")
        logger.info(f"   Nom: {user_data.nom}")
        logger.info(f"   Prénom: {user_data.prenom}")
        logger.info(f"   Type apprenant: {user_data.type_apprenant}")
        logger.info(f"   Niveau global: {user_data.niveau_global}")
        logger.info(f"   Préférences: {user_data.preferences}")
        
        
        logger.info("2. Validation du mot de passe...")
        password = user_data.mot_de_passe
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le mot de passe doit contenir au moins 8 caractères"
            )
        
        
        logger.info("3. Vérification de l'email...")
        existing_user = await db.get_user_by_email(user_data.email)
        if existing_user:
            logger.error(f"❌ Email déjà utilisé: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email déjà utilisé"
            )
        logger.info(f"✅ Email disponible")
        
        
        logger.info("4. Hashage du mot de passe...")
        hashed_password = auth_service.hash_password(password)
        
        
        logger.info("5. Gestion du rôle...")
        role_id = 2  
        
        
        logger.info("6. Préparation des données...")
        
        
        preferences = user_data.preferences or {}
        
        
        logger.info("7. Création de l'utilisateur...")
        user_id = await db.create_user(
            email=user_data.email,
            password_hash=hashed_password,
            nom=user_data.nom,
            prenom=user_data.prenom,
            role_id=role_id,
            type_apprenant=user_data.type_apprenant,
            niveau_global=user_data.niveau_global,
            preferences=preferences
        )
        
        logger.info(f"✅ Utilisateur créé avec ID: {user_id}")
        
        
        logger.info("8. Création du token JWT...")
        access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            data={
                "sub": str(user_id),
                "email": user_data.email,
                "role": "utilisateur",
                "role_id": role_id
            },
            expires_delta=access_token_expires
        )
        
        logger.info("=" * 50)
        logger.info(f"🎉 INSCRIPTION RÉUSSIE POUR: {user_data.email}")
        logger.info("=" * 50)
        
        return {
            "message": "Compte créé avec succès",
            "user_id": user_id,
            "email": user_data.email,
            "role": "utilisateur",
            "role_id": role_id,
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": config.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Erreur: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur technique: {str(e)}"
        )

@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    
    
    
    try:
        user = await auth_service.authenticate_user(form_data.username, form_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        
        await db.update_user_last_login(user.id)
        
        
        access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "role": user.role_name,
                "role_id": user.role_id
            },
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            email=user.email,
            role=user.role_name,
            role_id=user.role_id,
            expires_in=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la connexion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )

@app.post("/auth/register", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def register_user_admin(
    user_data: UserCreate, 
    current_user: UserInDB = Depends(require_admin)
):
    
    
    
    try:
        
        existing_user = await db.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email déjà utilisé"
            )
        
        
        hashed_password = auth_service.hash_password(user_data.mot_de_passe)
        
        
        role_id = user_data.role_id if user_data.role_id else 2
        
        
        async with db.get_connection() as conn:
            role_exists = await conn.fetchval(
                "SELECT nom_role FROM roles WHERE id = $1",
                role_id
            )
            
            if not role_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Rôle avec ID {role_id} n'existe pas"
                )
        
        
        user_id = await db.create_user(
            email=user_data.email,
            password_hash=hashed_password,
            nom=user_data.nom,
            prenom=user_data.prenom,
            role_id=role_id,
            type_apprenant=user_data.type_apprenant,
            niveau_global=user_data.niveau_global,
            preferences=user_data.preferences
        )
        
        
        await log_admin_action(
            admin_id=current_user.id,
            action="CREATE_USER",
            table="utilisateurs",
            record_id=user_id,
            details={
                "email": user_data.email,
                "role_id": role_id,
                "created_by": current_user.id
            }
        )
        
        return {
            "message": "Utilisateur créé avec succès",
            "user_id": user_id,
            "email": user_data.email,
            "role_id": role_id,
            "created_by": current_user.id,
            "created_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur création utilisateur admin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création de l'utilisateur"
        )



@app.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_user)):
    
    return current_user

@app.put("/users/me", response_model=UserResponse)
async def update_current_user(
    update_data: Dict[str, Any] = Body(...),
    current_user: UserInDB = Depends(get_current_user)
):
    
    try:
        
        allowed_fields = {'nom', 'prenom', 'email', 'type_apprenant', 'niveau_global', 'preferences'}
        
        
        filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields and v is not None}
        
        if not filtered_data:
            return current_user
        
        
        if 'niveau_global' in filtered_data:
            valid_levels = ['débutant', 'intermédiaire', 'avancé']
            if filtered_data['niveau_global'] not in valid_levels:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Niveau global invalide. Doit être parmi: {', '.join(valid_levels)}"
                )
        
        
        if 'type_apprenant' in filtered_data:
            valid_types = ['visuel', 'auditif', 'lecture', 'mixte']
            if filtered_data['type_apprenant'] not in valid_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Type d'apprenant invalide. Doit être parmi: {', '.join(valid_types)}"
                )
        
        
        if 'email' in filtered_data and filtered_data['email'] != current_user.email:
            existing = await db.get_user_by_email(filtered_data['email'])
            if existing and existing['id'] != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email déjà utilisé"
                )
        
        
        success = await db.update("utilisateurs", current_user.id, filtered_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        
        updated_user = await db.get_user_by_id(current_user.id)
        
        
        updated_user['type_apprenant'] = updated_user.get('type_apprenant')
        updated_user['niveau_global'] = updated_user.get('niveau_global', 'débutant')
        
        return UserResponse(**updated_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur mise à jour profil: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour du profil: {str(e)}"
        )

@app.post("/users/me/change-password")
async def change_password(
    old_password: str = Body(..., embed=True),
    new_password: str = Body(..., embed=True),
    current_user: UserInDB = Depends(get_current_user)
):
    
    try:
        async with db.get_connection() as conn:
            
            stored_hash = await conn.fetchval(
                "SELECT mot_de_passe_hash FROM utilisateurs WHERE id = $1",
                current_user.id
            )
            
            if not auth_service.verify_password(old_password, stored_hash):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ancien mot de passe incorrect"
                )
            
            
            if len(new_password) < 8:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Le mot de passe doit contenir au moins 8 caractères"
                )
            
            
            new_hashed_password = auth_service.hash_password(new_password)
            
            await conn.execute(
                "UPDATE utilisateurs SET mot_de_passe_hash = $1, date_maj = CURRENT_TIMESTAMP WHERE id = $2",
                new_hashed_password, current_user.id
            )
            
            return {"message": "Mot de passe changé avec succès"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur changement mot de passe: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du changement de mot de passe"
        )



@app.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    current_user: UserInDB = Depends(require_admin)
):
    
    try:
        users = await db.get_users_with_stats(limit, skip)
        
        if active_only:
            users = [u for u in users if u.get('est_actif', True)]
        
        return [UserResponse(**user) for user in users]
        
    except Exception as e:
        logger.error(f"Erreur récupération utilisateurs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des utilisateurs"
        )

@app.get("/admin/users/{user_id}", response_model=UserResponse)
async def get_user_by_id_admin(
    user_id: int = Path(..., gt=0),
    current_user: UserInDB = Depends(require_admin)
):
    
    try:
        user = await db.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        return UserResponse(**user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération utilisateur: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération de l'utilisateur"
        )

@app.put("/admin/users/{user_id}", response_model=UserResponse)
async def update_user_admin(
    user_id: int = Path(..., gt=0),
    user_update: UserUpdate = Body(...),
    current_user: UserInDB = Depends(require_admin)
):
    
    try:
        
        existing_user = await db.get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        
        if user_id == current_user.id and 'role_id' in user_update.dict(exclude_unset=True):
            if user_update.role_id != 1:  
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Vous ne pouvez pas vous retirer les droits d'administrateur"
                )
        
        
        update_data = user_update.dict(exclude_unset=True)
        if 'email' in update_data and update_data['email'] != existing_user['email']:
            user_with_email = await db.get_user_by_email(update_data['email'])
            if user_with_email and user_with_email['id'] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email déjà utilisé"
                )
        
        
        success = await db.update("utilisateurs", user_id, update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        
        await log_admin_action(
            admin_id=current_user.id,
            action="UPDATE_USER",
            table="utilisateurs",
            record_id=user_id,
            details=update_data
        )
        
        
        updated_user = await db.get_user_by_id(user_id)
        return UserResponse(**updated_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur mise à jour utilisateur admin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour de l'utilisateur"
        )

@app.delete("/admin/users/{user_id}")
async def delete_user_admin(
    user_id: int = Path(..., gt=0),
    current_user: UserInDB = Depends(require_admin)
):
    
    try:
        
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vous ne pouvez pas supprimer votre propre compte"
            )
        
        
        existing_user = await db.get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        
        success = await db.update("utilisateurs", user_id, {"est_actif": False})
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        
        await log_admin_action(
            admin_id=current_user.id,
            action="DELETE_USER",
            table="utilisateurs",
            record_id=user_id
        )
        
        return {"message": "Utilisateur désactivé avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur suppression utilisateur: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression de l'utilisateur"
        )

@app.put("/admin/users/{user_id}/activate")
async def activate_user_admin(
    user_id: int = Path(..., gt=0),
    activate: bool = Body(True, embed=True),
    current_user: UserInDB = Depends(require_admin)
):
    
    try:
        
        if user_id == current_user.id and not activate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vous ne pouvez pas désactiver votre propre compte"
            )
        
        
        existing_user = await db.get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        
        success = await db.update("utilisateurs", user_id, {"est_actif": activate})
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        
        action = "ACTIVATE_USER" if activate else "DEACTIVATE_USER"
        await log_admin_action(
            admin_id=current_user.id,
            action=action,
            table="utilisateurs",
            record_id=user_id
        )
        
        status_msg = "activé" if activate else "désactivé"
        return {"message": f"Utilisateur {status_msg} avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur activation/désactivation utilisateur: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'activation/désactivation"
        )



@app.get("/auth/me", response_model=UserResponse)
async def get_current_auth_user(current_user: UserInDB = Depends(get_current_user)):
    
    
    
    
    return current_user


@app.post("/reponses", status_code=status.HTTP_201_CREATED)
async def save_quiz_response(
    response_data: dict,
    current_user: UserInDB = Depends(get_current_user)
):
    
    try:
        async with db.get_connection() as conn:
            await conn.execute("""
                INSERT INTO reponses_quiz 
                (resultat_id, question_id, reponse_utilisateur, est_correcte, temps_reponse, date_reponse)
                VALUES ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP)
            """, 
                response_data['resultat_id'],
                response_data['question_id'],
                response_data['reponse_utilisateur'],
                response_data['est_correcte'],
                response_data.get('temps_reponse', 30)
            )
            
        return {"message": "Réponse enregistrée avec succès"}
    except Exception as e:
        logger.error(f"Erreur sauvegarde réponse: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la sauvegarde de la réponse: {str(e)}"
        )


@app.post("/voice/search")
async def voice_search(
    audio: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user)
):
   
    start_time = datetime.now()
    tmp_path = None
    
    try:
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_file:
            content = await audio.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        
        transcribe_start = datetime.now()
        
        
        transcription_result = voice_search_service.transcribe_audio(tmp_path)
        
        transcribe_time = (datetime.now() - transcribe_start).total_seconds()
        
        
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        
        if not transcription_result["success"]:
            
            async with db.get_connection() as conn:
                await conn.execute("""
                    INSERT INTO recherches_vocales 
                    (utilisateur_id, requete_transcrite, confiance_transcription, 
                     resultats_trouves, temps_reponse, succes, date_recherche)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, 
                    current_user.id, 
                    transcription_result.get("transcript", ""), 
                    transcription_result.get("confidence", 0.0),
                    0,
                    int(transcribe_time * 1000),  
                    False,
                    datetime.now()
                )
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur de transcription: {transcription_result.get('error', 'Inconnue')}"
            )
        
        transcript = transcription_result["transcript"]
        intent = transcription_result["intent"]
        
        
        search_start = datetime.now()
        search_results = await search_courses_by_intent(intent, db)
        search_time = (datetime.now() - search_start).total_seconds()
        
        nb_results = len(search_results)
        
        
        async with db.get_connection() as conn:
            await conn.execute("""
                INSERT INTO recherches_vocales 
                (utilisateur_id, requete_transcrite, confiance_transcription, 
                 resultats_trouves, temps_reponse, succes, date_recherche)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, 
                current_user.id, 
                transcript, 
                transcription_result["confidence"],
                nb_results,
                int((datetime.now() - start_time).total_seconds() * 1000), 
                True,
                datetime.now()
            )
        
        logger.info(f"🎤 Recherche vocale: '{transcript}' -> {nb_results} résultats (confiance: {transcription_result['confidence']:.2f})")
        
        return {
            "transcript": transcript,
            "confidence": transcription_result["confidence"],
            "intent": intent,
            "results": search_results,
            "suggestions": generate_suggestions(intent),
            "stats": {
                "transcribe_time_ms": int(transcribe_time * 1000),
                "search_time_ms": int(search_time * 1000),
                "total_time_ms": int((datetime.now() - start_time).total_seconds() * 1000),
                "results_count": nb_results
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur recherche vocale: {e}")
        
        
        try:
            async with db.get_connection() as conn:
                await conn.execute("""
                    INSERT INTO recherches_vocales 
                    (utilisateur_id, requete_transcrite, confiance_transcription, 
                     resultats_trouves, succes, date_recherche)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, 
                    current_user.id, 
                    "Erreur de transcription", 
                    0.0,
                    0,
                    False,
                    datetime.now()
                )
        except:
            pass
        
        
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la recherche vocale: {str(e)}"
        )


@app.get("/voice/history")
async def get_voice_search_history(
    limit: int = Query(50, ge=1, le=200),
    current_user: UserInDB = Depends(get_current_user)
):
    
    try:
        async with db.get_connection() as conn:
            rows = await conn.fetch("""
                SELECT id, requete_transcrite, confiance_transcription, 
                       resultats_trouves, temps_reponse, succes, date_recherche
                FROM recherches_vocales
                WHERE utilisateur_id = $1
                ORDER BY date_recherche DESC
                LIMIT $2
            """, current_user.id, limit)
            
            history = []
            for row in rows:
                history.append({
                    "id": row['id'],
                    "query": row['requete_transcrite'],
                    "confidence": float(row['confiance_transcription']) if row['confiance_transcription'] else 0.0,
                    "results_count": row['resultats_trouves'] or 0,
                    "response_time_ms": row['temps_reponse'] or 0,
                    "success": row['succes'],
                    "date": row['date_recherche'].isoformat() if row['date_recherche'] else None
                })
            
            return history
    except Exception as e:
        logger.error(f"Erreur récupération historique: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération de l'historique"
        )

async def search_courses_by_intent(intent: Dict, db) -> List[Dict]:
    
    try:
        async with db.get_connection() as conn:
            
            conditions = []
            params = []
            param_index = 1
            
            
            if intent.get("course_ids"):
                placeholders = ','.join([f'${param_index + i}' for i in range(len(intent["course_ids"]))])
                conditions.append(f"id IN ({placeholders})")
                params.extend(list(intent["course_ids"]))
                param_index += len(intent["course_ids"])
            
            
            if intent.get("difficulty"):
                conditions.append(f"difficulte = ${param_index}")
                params.append(intent["difficulty"])
                param_index += 1
            
            
            if intent.get("keywords"):
                keyword_conditions = []
                for keyword in intent["keywords"][:5]:
                    keyword_conditions.append(f"(titre ILIKE ${param_index} OR description ILIKE ${param_index} OR array_to_string(tags, ' ') ILIKE ${param_index})")
                    params.append(f'%{keyword}%')
                    param_index += 1
                if keyword_conditions:
                    conditions.append(f"({' OR '.join(keyword_conditions)})")
            
            
            query = """
                SELECT id, titre, description, difficulte, tags, duree_estimee as duree
                FROM cours_html
                WHERE est_actif = true
            """
            
            if conditions:
                query += " AND " + " AND ".join(conditions)
            
            query += " ORDER BY ordre_affichage LIMIT 20"
            
            rows = await conn.fetch(query, *params)
            
            results = []
            for row in rows:
                results.append({
                    "id": row['id'],
                    "titre": row['titre'],
                    "description": row['description'] or '',
                    "difficulte": row['difficulte'] or 'débutant',
                    "tags": row['tags'] or [],
                    "duree": row['duree'] or 0,
                    "score": calculate_score(row, intent)
                })
            
            
            results.sort(key=lambda x: x['score'], reverse=True)
            return results
            
    except Exception as e:
        logger.error(f"Erreur recherche par intention: {e}")
        return []

def calculate_score(course: Dict, intent: Dict) -> float:
    
    score = 0.0
    
    
    if intent.get("difficulty") and course.get("difficulte") == intent["difficulty"]:
        score += 30
    
    
    title_lower = course.get("titre", "").lower()
    desc_lower = course.get("description", "").lower()
    tags_lower = [t.lower() for t in course.get("tags", [])]
    
    for keyword in intent.get("keywords", []):
        if keyword in title_lower:
            score += 20
        if keyword in desc_lower:
            score += 10
        if any(keyword in tag for tag in tags_lower):
            score += 15
    
    
    score += intent.get("confidence", 0) * 20
    
    return min(score, 100)

def generate_suggestions(intent: Dict) -> List[str]:
    
    suggestions = []
    
    if not intent.get("topics") and not intent.get("difficulty"):
        suggestions.append("Essayez de préciser le sujet (HTML, CSS, formulaires...)")
        suggestions.append("Indiquez votre niveau (débutant, intermédiaire, avancé)")
    
    if intent.get("topics"):
        suggestions.append(f"Nous avons trouvé des cours sur {', '.join(intent['topics'][:3])}")
    
    if not intent.get("course_ids"):
        suggestions.append("Essayez des mots-clés comme 'HTML débutant' ou 'formulaires'")
    
    return suggestions

@app.get("/courses/search")
async def search_courses_endpoint(
    q: str = Query(..., min_length=1, description="Terme de recherche"),
    limit: int = Query(20, ge=1, le=100, description="Nombre maximum de résultats")
):
    
    try:
        async with db.get_connection() as conn:
            
            query = """
                SELECT 
                    id, 
                    titre, 
                    description, 
                    difficulte, 
                    tags, 
                    duree_estimee as duree,
                    -- Calcul du score de pertinence
                    (
                        -- Score pour le titre (poids 3)
                        (CASE WHEN titre ILIKE $2 THEN 30 ELSE 0 END) +
                        (CASE WHEN titre ILIKE $3 THEN 20 ELSE 0 END) +
                        -- Score pour la description (poids 1)
                        (CASE WHEN description ILIKE $2 THEN 10 ELSE 0 END) +
                        (CASE WHEN description ILIKE $3 THEN 5 ELSE 0 END) +
                        -- Score pour les tags (poids 2)
                        (CASE WHEN array_to_string(tags, ' ') ILIKE $2 THEN 20 ELSE 0 END) +
                        (CASE WHEN array_to_string(tags, ' ') ILIKE $3 THEN 10 ELSE 0 END) +
                        -- Score pour la correspondance exacte des mots
                        (SELECT COALESCE(SUM(
                            CASE WHEN position(word in titre) > 0 THEN 5
                                 WHEN position(word in description) > 0 THEN 3
                                 WHEN position(word in array_to_string(tags, ' ')) > 0 THEN 4
                            ELSE 0 END
                        ), 0) FROM unnest(string_to_array($1, ' ')) as word)
                    ) as score
                FROM cours_html
                WHERE est_actif = true
                AND (
                    titre ILIKE $2 
                    OR titre ILIKE $3
                    OR description ILIKE $2 
                    OR description ILIKE $3
                    OR array_to_string(tags, ' ') ILIKE $2
                    OR array_to_string(tags, ' ') ILIKE $3
                )
                ORDER BY score DESC, titre
                LIMIT $4
            """
            
            
            search_pattern_exact = f'%{q}%'
            
            words = q.split()
            search_pattern_words = '%' + '%'.join(words) + '%'
            
            rows = await conn.fetch(query, q, search_pattern_exact, search_pattern_words, limit)
            
            results = []
            for row in rows:
                results.append({
                    "id": row['id'],
                    "titre": row['titre'],
                    "description": row['description'] or '',
                    "difficulte": row['difficulte'] or 'débutant',
                    "tags": row['tags'] or [],
                    "duree": row['duree'] or 0,
                    "score": float(row['score']) if row['score'] else 0
                })
            
            
            if len(results) == 0:
                
                broad_query = """
                    SELECT id, titre, description, difficulte, tags, duree_estimee as duree,
                           10 as score
                    FROM cours_html
                    WHERE est_actif = true
                    ORDER BY ordre_affichage
                    LIMIT $1
                """
                broad_rows = await conn.fetch(broad_query, limit)
                for row in broad_rows:
                    results.append({
                        "id": row['id'],
                        "titre": row['titre'],
                        "description": row['description'] or '',
                        "difficulte": row['difficulte'] or 'débutant',
                        "tags": row['tags'] or [],
                        "duree": row['duree'] or 0,
                        "score": 0
                    })
            
            return results
    except Exception as e:
        logger.error(f"Erreur recherche cours: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la recherche"
        )

@app.get("/courses", response_model=List[CourseResponse])
async def get_all_courses(
    active_only: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200)
):
    
    try:
        courses = await db.get_all_courses(active_only, limit)
        return [CourseResponse(**course) for course in courses]
    except Exception as e:
        logger.error(f"Erreur récupération cours: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des cours"
        )

@app.get("/courses/{course_id}", response_model=CourseResponse)
async def get_course_by_id(course_id: int = Path(..., gt=0)):
    
    try:
        course = await db.read_one("cours_html", {"id": course_id})
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cours non trouvé"
            )
        
        return CourseResponse(**course)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération cours: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération du cours"
        )

@app.get("/courses/slug/{slug}", response_model=CourseResponse)
async def get_course_by_slug(slug: str = Path(...)):
    
    try:
        course = await db.get_course_by_slug(slug)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cours non trouvé"
            )
        
        return CourseResponse(**course)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération cours par slug: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération du cours"
        )

@app.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    current_user: UserInDB = Depends(require_admin)
):
    
    try:
        
        if not hasattr(course_data, 'slug') or not course_data.slug:
            slug = generate_slug(course_data.titre)
            course_data_dict = course_data.dict()
            course_data_dict['slug'] = slug
        else:
            course_data_dict = course_data.dict()
            slug = course_data_dict['slug']
        
        
        existing_course = await db.get_course_by_slug(slug)
        if existing_course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce slug est déjà utilisé"
            )
        
        
        course_data_dict["created_by"] = current_user.id
        course_data_dict["last_modified_by"] = current_user.id
        course_data_dict["date_creation"] = datetime.now()
        course_data_dict["date_maj"] = datetime.now()
        
        
        if 'tags' in course_data_dict and isinstance(course_data_dict['tags'], list):
            course_data_dict['tags'] = course_data_dict['tags']
        
        
        course_id = await db.create("cours_html", course_data_dict)
        
        
        await log_admin_action(
            admin_id=current_user.id,
            action="CREATE_COURSE",
            table="cours_html",
            record_id=course_id,
            details={"titre": course_data.titre, "slug": slug}
        )
        
        
        course = await db.read_one("cours_html", {"id": course_id})
        return CourseResponse(**course)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur création cours: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du cours: {str(e)}"
        )

@app.put("/courses/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int = Path(..., gt=0),
    course_data: CourseUpdate = Body(...),
    current_user: UserInDB = Depends(require_admin)
):
    
    try:
        
        existing_course = await db.read_one("cours_html", {"id": course_id})
        if not existing_course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cours non trouvé"
            )
        
        
        update_data = course_data.dict(exclude_unset=True)
        update_data["last_modified_by"] = current_user.id
        update_data["date_maj"] = datetime.now()
        
        
        if 'slug' in update_data and update_data['slug'] != existing_course['slug']:
            existing_slug = await db.get_course_by_slug(update_data['slug'])
            if existing_slug:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ce slug est déjà utilisé"
                )
        
        
        success = await db.update("cours_html", course_id, update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cours non trouvé"
            )
        
        
        await log_admin_action(
            admin_id=current_user.id,
            action="UPDATE_COURSE",
            table="cours_html",
            record_id=course_id,
            details=update_data
        )
        
        
        updated_course = await db.read_one("cours_html", {"id": course_id})
        return CourseResponse(**updated_course)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur mise à jour cours: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour du cours"
        )

@app.delete("/courses/{course_id}")
async def delete_course(
    course_id: int = Path(..., gt=0),
    current_user: UserInDB = Depends(require_admin)
):
    
    try:
        
        existing_course = await db.read_one("cours_html", {"id": course_id})
        if not existing_course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cours non trouvé"
            )
        
        
        success = await db.update("cours_html", course_id, {"est_actif": False})
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cours non trouvé"
            )
        
        
        await log_admin_action(
            admin_id=current_user.id,
            action="DELETE_COURSE",
            table="cours_html",
            record_id=course_id
        )
        
        return {"message": "Cours désactivé avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur suppression cours: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression du cours"
        )

@app.get("/courses/{course_id}/questions", response_model=List[QuestionResponse])
async def get_course_questions(
    course_id: int = Path(..., gt=0),
    mode: Optional[str] = Query(None)  
):
    
    try:
        
        if mode:
            questions = await db.get_questions_by_course(course_id, mode)
        else:
            questions = await db.get_questions_by_course(course_id, None)
        
        print(f"🔍 Cours {course_id}: {len(questions)} questions trouvées")
        return [QuestionResponse(**q) for q in questions]
    except Exception as e:
        logger.error(f"Erreur récupération questions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des questions: {str(e)}"
        )




@app.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question_by_id(question_id: int = Path(..., gt=0)):
    
    try:
        question = await db.read_one("questions_quiz", {"id": question_id})
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question non trouvée"
            )
        
        return QuestionResponse(**question)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération de la question"
        )

@app.post("/questions", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    question_data: QuestionCreate,
    current_user: UserInDB = Depends(require_admin)
):
    
    try:
        
        course = await db.read_one("cours_html", {"id": question_data.cours_id})
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cours non trouvé"
            )
        
        
        question_dict = question_data.dict()
        question_dict["created_by"] = current_user.id
        question_dict["date_creation"] = datetime.now()
        
        
        if question_dict.get("options") and isinstance(question_dict["options"], dict):
            question_dict["options"] = json.dumps(question_dict["options"])
        
        
        question_id = await db.create("questions_quiz", question_dict)
        
        
        await log_admin_action(
            admin_id=current_user.id,
            action="CREATE_QUESTION",
            table="questions_quiz",
            record_id=question_id,
            details={
                "cours_id": question_data.cours_id,
                "type_question": question_data.type_question
            }
        )
        
        
        question = await db.read_one("questions_quiz", {"id": question_id})
        return QuestionResponse(**question)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur création question: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création de la question: {str(e)}"
        )

@app.put("/questions/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int = Path(..., gt=0),
    question_data: QuestionUpdate = Body(...),
    current_user: UserInDB = Depends(require_admin)
):
    
    try:
        
        existing_question = await db.read_one("questions_quiz", {"id": question_id})
        if not existing_question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question non trouvée"
            )
        
        
        update_data = question_data.dict(exclude_unset=True)
        
        
        if 'options' in update_data and isinstance(update_data['options'], dict):
            update_data['options'] = json.dumps(update_data['options'])
        
        
        success = await db.update("questions_quiz", question_id, update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question non trouvée"
            )
        
        
        await log_admin_action(
            admin_id=current_user.id,
            action="UPDATE_QUESTION",
            table="questions_quiz",
            record_id=question_id,
            details=update_data
        )
        
        
        updated_question = await db.read_one("questions_quiz", {"id": question_id})
        return QuestionResponse(**updated_question)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur mise à jour question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour de la question"
        )

@app.delete("/questions/{question_id}")
async def delete_question(
    question_id: int = Path(..., gt=0),
    current_user: UserInDB = Depends(require_admin)
):
    
    try:
        
        existing_question = await db.read_one("questions_quiz", {"id": question_id})
        if not existing_question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question non trouvée"
            )
        
        
        async with db.get_connection() as conn:
            await conn.execute(
                "DELETE FROM reponses_quiz WHERE question_id = $1",
                question_id
            )
        
        
        success = await db.delete("questions_quiz", question_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question non trouvée"
            )
        
        
        await log_admin_action(
            admin_id=current_user.id,
            action="DELETE_QUESTION",
            table="questions_quiz",
            record_id=question_id
        )
        
        return {"message": "Question supprimée avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur suppression question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression de la question"
        )



@app.post("/results", response_model=LearningResultResponse, status_code=status.HTTP_201_CREATED)
async def save_learning_result(
    result_data: LearningResultCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    
    try:
        
        course = await db.read_one("cours_html", {"id": result_data.cours_id})
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cours non trouvé"
            )
        
        
        taux_completion = result_data.taux_completion
        if taux_completion is None:
            taux_completion = 100.0 if result_data.est_reussi else 50.0
        
        
        result_id = await db.save_learning_result(
            user_id=current_user.id,
            course_id=result_data.cours_id,
            mode=result_data.mode,
            score=result_data.score_quiz,
            time_spent=result_data.temps_passe,
            completion_rate=taux_completion,
            is_success=result_data.est_reussi,
            feedback=result_data.feedback
        )
        
        
        await db.calculate_learner_type(current_user.id)
        
        
        result = await db.read_one("resultats_apprentissage", {"id": result_id})
        return LearningResultResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur sauvegarde résultat: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la sauvegarde du résultat: {str(e)}"
        )



@app.get("/users/me/preferences")
async def get_user_preferences(current_user: UserInDB = Depends(get_current_user)):
    
    try:
        async with db.get_connection() as conn:
            
            query = """
            SELECT score_texte, score_audio, score_video, confiance, 
                   date_calcul, date_maj, historique
            FROM preferences_apprentissage
            WHERE utilisateur_id = $1
            ORDER BY date_calcul DESC
            LIMIT 1
            """
            
            row = await conn.fetchrow(query, current_user.id)
            
            if not row:
                
                return {
                    "score_texte": 0,
                    "score_audio": 0,
                    "score_video": 0,
                    "confiance": 0,
                    "date_calcul": None,
                    "date_maj": None,
                    "historique": []
                }
            
            
            historique = []
            if row['historique']:
                try:
                    if isinstance(row['historique'], str):
                        historique = json.loads(row['historique'])
                    else:
                        historique = row['historique']
                except:
                    historique = []
            
            return {
                "score_texte": float(row['score_texte']) if row['score_texte'] else 0,
                "score_audio": float(row['score_audio']) if row['score_audio'] else 0,
                "score_video": float(row['score_video']) if row['score_video'] else 0,
                "confiance": float(row['confiance']) if row['confiance'] else 0,
                "date_calcul": row['date_calcul'].isoformat() if row['date_calcul'] else None,
                "date_maj": row['date_maj'].isoformat() if row['date_maj'] else None,
                "historique": historique
            }
            
    except Exception as e:
        logger.error(f"Erreur récupération préférences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des préférences"
        )

@app.get("/users/me/results", response_model=List[LearningResultResponse])
async def get_my_results(current_user: UserInDB = Depends(get_current_user)):
    
    try:
        results = await db.get_user_learning_results(current_user.id)
        return [LearningResultResponse(**r) for r in results]
    except Exception as e:
        logger.error(f"Erreur récupération résultats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des résultats"
        )

@app.get("/users/me/progress")
async def get_my_progress(current_user: UserInDB = Depends(get_current_user)):
    
    try:
        
        async with db.get_connection() as conn:
            
            cours_complets = await conn.fetchval("""
                SELECT COUNT(DISTINCT cours_id) 
                FROM resultats_apprentissage 
                WHERE utilisateur_id = $1 AND est_reussi = true
            """, current_user.id)
            
            
            score_moyen = await conn.fetchval("""
                SELECT COALESCE(AVG(score_quiz), 0)
                FROM resultats_apprentissage 
                WHERE utilisateur_id = $1
            """, current_user.id)
            
            
            temps_total = await conn.fetchval("""
                SELECT COALESCE(SUM(temps_passe), 0)
                FROM resultats_apprentissage 
                WHERE utilisateur_id = $1
            """, current_user.id)
            
            
            total_cours = await conn.fetchval("SELECT COUNT(*) FROM cours_html WHERE est_actif = true")
            progression_niveau = (cours_complets / total_cours * 100) if total_cours > 0 else 0
            
            
            stats_par_mode = {}
            
            for mode in ['texte', 'audio', 'video']:
                stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as nb_cours,
                        COALESCE(AVG(score_quiz), 0) as score_moyen
                    FROM resultats_apprentissage 
                    WHERE utilisateur_id = $1 AND mode = $2
                """, current_user.id, mode)
                
                stats_par_mode[mode] = {
                    'nb_cours': stats['nb_cours'] if stats else 0,
                    'score_moyen': float(stats['score_moyen']) if stats and stats['score_moyen'] else 0
                }
            
            
            result = {
                "cours_complets": cours_complets or 0,
                "score_moyen": float(score_moyen) if score_moyen else 0,
                "temps_total": temps_total or 0,
                "progression_niveau": float(progression_niveau) if progression_niveau else 0,
                "stats_par_mode": stats_par_mode
            }
            
            logger.info(f"📊 Progression calculée pour utilisateur {current_user.id}: {result}")
            return result
            
    except Exception as e:
        logger.error(f"❌ Erreur récupération progression: {e}")
        logger.error(traceback.format_exc())
        
        return {
            "cours_complets": 0,
            "score_moyen": 0,
            "temps_total": 0,
            "progression_niveau": 0,
            "stats_par_mode": {
                "texte": {"nb_cours": 0, "score_moyen": 0},
                "audio": {"nb_cours": 0, "score_moyen": 0},
                "video": {"nb_cours": 0, "score_moyen": 0}
            }
        }


@app.get("/search/courses")
async def search_courses(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100)
):
    
    try:
        courses = await db.search_courses(q, limit)
        return courses
    except Exception as e:
        logger.error(f"Erreur recherche cours: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la recherche"
        )



@app.get("/stats/system")
async def get_system_stats(current_user: UserInDB = Depends(require_admin)):
    
    try:
        stats = await db.get_system_stats()
        return stats
    except Exception as e:
        logger.error(f"Erreur récupération stats système: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des statistiques"
        )

@app.get("/stats/users")
async def get_users_stats(current_user: UserInDB = Depends(require_admin)):
    
    try:
        stats = await db.get_user_statistics_view()
        return stats
    except Exception as e:
        logger.error(f"Erreur récupération stats utilisateurs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des statistiques"
        )



@app.get("/auth/roles", response_model=List[Dict[str, Any]])
async def get_roles(current_user: UserInDB = Depends(get_current_user)):
    
    try:
        async with db.get_connection() as conn:
            query = """
            SELECT id, nom_role, description, permissions
            FROM roles
            ORDER BY id
            """
            
            roles = await conn.fetch(query)
            
            return [
                {
                    "id": role['id'],
                    "nom_role": role['nom_role'],
                    "description": role['description'],
                    "permissions": role['permissions']
                }
                for role in roles
            ]
            
    except Exception as e:
        logger.error(f"Erreur récupération rôles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des rôles"
        )



@app.get("/auth/check-email/{email}")
async def check_email(email: str):
    
    try:
        existing_user = await db.get_user_by_email(email)
        return {
            "email": email,
            "available": existing_user is None,
            "exists": existing_user is not None
        }
    except Exception as e:
        logger.error(f"Erreur vérification email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la vérification de l'email"
        )

@app.post("/auth/validate-password")
async def validate_password(password_request: Dict[str, str]):
    
    try:
        password = password_request.get("password", "")
        
        if not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mot de passe requis"
            )
        
        validation_result = {
            "valid": True,
            "score": 0,
            "max_score": 5,
            "requirements": [],
            "suggestions": []
        }
        
        import re
        
        
        checks = []
        
        
        if len(password) >= 8:
            validation_result["score"] += 1
            checks.append({"rule": "min_length", "passed": True, "message": "Longueur ≥ 8 caractères"})
        else:
            checks.append({"rule": "min_length", "passed": False, "message": "Doit contenir au moins 8 caractères"})
            validation_result["valid"] = False
        
        
        if re.search(r"[A-Z]", password):
            validation_result["score"] += 1
            checks.append({"rule": "uppercase", "passed": True, "message": "Contient une majuscule"})
        else:
            checks.append({"rule": "uppercase", "passed": False, "message": "Doit contenir au moins une majuscule"})
            validation_result["valid"] = False
        
        
        if re.search(r"[a-z]", password):
            validation_result["score"] += 1
            checks.append({"rule": "lowercase", "passed": True, "message": "Contient une minuscule"})
        else:
            checks.append({"rule": "lowercase", "passed": False, "message": "Doit contenir au moins une minuscule"})
            validation_result["valid"] = False
        
        
        if re.search(r"\d", password):
            validation_result["score"] += 1
            checks.append({"rule": "digit", "passed": True, "message": "Contient un chiffre"})
        else:
            checks.append({"rule": "digit", "passed": False, "message": "Doit contenir au moins un chiffre"})
            validation_result["valid"] = False
        
        
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            validation_result["score"] += 1
            checks.append({"rule": "special", "passed": True, "message": "Contient un caractère spécial"})
        else:
            checks.append({"rule": "special", "passed": False, "message": "Recommandé: ajouter un caractère spécial"})
        
        validation_result["requirements"] = checks
        
        
        if validation_result["score"] <= 2:
            validation_result["strength"] = "faible"
        elif validation_result["score"] <= 4:
            validation_result["strength"] = "moyen"
        else:
            validation_result["strength"] = "fort"
        
        return validation_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur validation mot de passe: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la validation du mot de passe"
        )



@app.get("/")
async def root():
    
    return {
        "message": "Bienvenue sur la Plateforme Éducative Intelligente",
        "version": config.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "auth": {
                "public_register": "/auth/public-register (POST)",
                "login": "/auth/login (POST)",
                "me": "/users/me (GET)",
                "check_email": "/auth/check-email/{email} (GET)"
            },
            "courses": {
                "list": "/courses (GET)",
                "get": "/courses/{id} (GET)",
                "search": "/search/courses?q=... (GET)"
            },
            "stats": {
                "user_progress": "/users/me/progress (GET)",
                "user_results": "/users/me/results (GET)"
            }
        }
    }

@app.get("/health")
async def health_check():
    
    try:
        async with db.get_connection() as conn:
            db_status = await conn.fetchval("SELECT 1")
            
            return {
                "status": "healthy",
                "database": "connected" if db_status else "disconnected",
                "timestamp": datetime.now().isoformat(),
                "version": config.APP_VERSION
            }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }



@app.get("/admin/logs")
async def get_admin_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UserInDB = Depends(require_admin)
):
    
    try:
        logs = await db.get_admin_logs(limit, skip)
        return logs
    except Exception as e:
        logger.error(f"Erreur récupération logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des logs"
        )

@app.get("/admin/interactions")
async def get_interaction_logs(
    user_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    current_user: UserInDB = Depends(require_admin)
):
    
    try:
        logs = await db.get_interaction_logs(user_id, limit)
        return logs
    except Exception as e:
        logger.error(f"Erreur récupération logs interactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des logs"
        )



@app.get("/debug/tables")
async def debug_tables(current_user: UserInDB = Depends(require_admin)):
    
    try:
        async with db.get_connection() as conn:
            query = """
            SELECT table_name, 
                   pg_size_pretty(pg_total_relation_size('"' || table_name || '"')) as size
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
            """
            
            tables = await conn.fetch(query)
            return [
                {
                    "table_name": table['table_name'],
                    "size": table['size']
                }
                for table in tables
            ]
    except Exception as e:
        logger.error(f"Erreur debug tables: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des tables"
        )








@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error": exc.__class__.__name__,
            "path": request.url.path,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    
    logger.error(f"Erreur non gérée: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Une erreur interne est survenue",
            "error": exc.__class__.__name__,
            "path": request.url.path,
            "timestamp": datetime.now().isoformat()
        }
    )



@app.get("/admin/stats")
async def get_admin_stats(current_user: UserInDB = Depends(require_admin)):
    
    try:
        
        stats = await db.get_system_stats()
        
        
        async with db.get_connection() as conn:
            
            users_per_day = await conn.fetch("""
                SELECT DATE(date_inscription) as date, COUNT(*) as count
                FROM utilisateurs
                WHERE date_inscription >= CURRENT_DATE - INTERVAL '7 days'
                GROUP BY DATE(date_inscription)
                ORDER BY date
            """)
            
            
            activity_per_hour = [
                {"hour": f"{i:02d}:00", "activity": 10 + (i * 3)}
                for i in range(24)
            ]
            
            
            popular_courses = await conn.fetch("""
                SELECT c.titre, COUNT(r.id) as attempts
                FROM cours_html c
                LEFT JOIN resultats_apprentissage r ON c.id = r.cours_id
                WHERE c.est_actif = TRUE
                GROUP BY c.id, c.titre
                ORDER BY attempts DESC
                LIMIT 5
            """)
        
        
        result = {
            **stats,
            "users_per_day": [
                {"date": row['date'].strftime("%Y-%m-%d"), "count": row['count']}
                for row in users_per_day
            ],
            "activity_per_hour": activity_per_hour,
            "popular_courses": [
                {"course": row['titre'], "attempts": row['attempts']}
                for row in popular_courses
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Erreur récupération stats admin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des statistiques admin"
        )



if __name__ == "__main__":
    uvicorn.run(
        "mainApp:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level="info"
    )