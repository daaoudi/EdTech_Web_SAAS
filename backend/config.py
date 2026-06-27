
import os
from dotenv import load_dotenv
from datetime import timedelta
import logging

load_dotenv()

class Config:
    
    ENV = os.getenv("ENV", "development")
    
    
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "8001"))
    
    
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "plateforme_elearning")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
    
    
    SECRET_KEY = os.getenv("SECRET_KEY", "ZPL9KCkx1LUUgHP5MytIYD4VYfewssE8njlD0PMwlOg=")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    
    
    APP_TITLE = "Plateforme Éducative Intelligente"
    APP_VERSION = "1.0.0"
    DEBUG = ENV == "development"
    
    
    
    TUTOR_MODEL_PATH = os.getenv("TUTOR_MODEL_PATH", "./tutor_ia_model/")
    
    
    BERT_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
    
    
    SEQUENTIAL_MINER_PATH = os.getenv("SEQUENTIAL_MINER_PATH", "./tutor_ia_model/sequential_miner.pkl")
    SEQUENTIAL_MIN_SUPPORT = 0.10
    SEQUENTIAL_MIN_CONFIDENCE = 0.60
    
    
    if ENV == "production":
        ALLOWED_ORIGINS = [
            "https://votre-domaine.com",
        ]
    else:
        ALLOWED_ORIGINS = [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:8001",
        ]
    
    @classmethod
    def validate(cls):
        
        required = ['DB_NAME', 'DB_USER', 'SECRET_KEY']
        for var in required:
            if not getattr(cls, var):
                raise ValueError(f"Variable {var} manquante ou vide")
        
        if cls.SECRET_KEY == "changez-cette-cle-en-production":
            logging.warning("⚠️  SECRET_KEY par défaut utilisée - Non sécurisé pour la production")
        
        # Vérifier si le dossier du modèle existe
        if os.path.exists(cls.TUTOR_MODEL_PATH):
            logging.info(f"✅ Dossier du modèle trouvé: {cls.TUTOR_MODEL_PATH}")
        else:
            logging.warning(f"⚠️ Dossier du modèle non trouvé: {cls.TUTOR_MODEL_PATH}")

config = Config()


config.validate()


logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


DATABASE_URL = f"postgresql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
ASYNC_DATABASE_URL = f"postgresql+asyncpg://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"