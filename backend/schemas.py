from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class LearningMode(str, Enum):
    TEXTE = "texte"
    AUDIO = "audio"
    VIDEO = "video"

class Difficulty(str, Enum):
    DEBUTANT = "debutant"
    INTERMEDIAIRE = "intermediaire"
    AVANCE = "avance"
    
    AVANCE_ACCENT = "avancé" 
    DIFFICILE = "difficile"  
    FACILE = "facile"        
    MOYEN = "moyen"           

class QuestionType(str, Enum):
    CHOIX_MULTIPLE = "choix_multiple"
    VRAI_FAUX = "vrai_faux"
    TEXTE_LIBRE = "texte_libre"
    CODE = "code"


class UserBase(BaseModel):
    email: EmailStr
    nom: Optional[str] = None
    prenom: Optional[str] = None

class UserCreate(UserBase):
    mot_de_passe: str = Field(..., min_length=6)
    role_id: int = 1

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    role_id: Optional[int] = None
    preferences: Optional[Dict[str, Any]] = None

class User(UserBase):
    id: int
    role_id: int
    date_inscription: datetime
    derniere_connexion: Optional[datetime] = None
    type_apprenant: Optional[str] = None
    niveau_global: Optional[str] = "débutant"
    est_actif: bool = True
    
    class Config:
        from_attributes = True

class CourseBase(BaseModel):
    titre: str = Field(..., min_length=3, max_length=255)
    slug: str = Field(..., min_length=3, max_length=300)
    description: Optional[str] = None
    contenu_texte: str
    difficulte: Difficulty
    duree_estimee: int = Field(..., gt=0)

class CourseCreate(CourseBase):
    url_audio: Optional[str] = None
    url_video: Optional[str] = None
    ordre_affichage: int = 0
    tags: List[str] = []
    est_actif: bool = True

class Course(CourseBase):
    id: int
    created_by: Optional[int] = None
    date_creation: datetime
    date_maj: datetime
    
    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    question: str
    type_question: QuestionType
    points: int = Field(1, ge=1, le=10)
    difficulte: str = "moyen"  # Utiliser str au lieu de Difficulty pour plus de flexibilité
    reponse_correcte: str
    explication: Optional[str] = None
    mode_specifique: Optional[LearningMode] = None

class QuestionCreate(QuestionBase):
    cours_id: int
    options: Optional[Dict[str, str]] = None

class Question(QuestionBase):
    id: int
    cours_id: int
    created_by: Optional[int] = None
    date_creation: datetime
    
    class Config:
        from_attributes = True
    
    # Validator pour normaliser la difficulté
    @validator('difficulte', pre=True)
    def normalize_difficulte(cls, v):
        if v is None:
            return "moyen"
        v_str = str(v).lower()
        
        # Normaliser les valeurs
        mapping = {
            'facile': 'facile',
            'moyen': 'moyen',
            'difficile': 'difficile',
            'avancé': 'difficile',
            'avance': 'difficile',
            'advanced': 'difficile',
            'debutant': 'facile',
            'débutant': 'facile',
            'beginner': 'facile',
            'intermediaire': 'moyen',
            'intermédiaire': 'moyen',
            'intermediate': 'moyen',
            'easy': 'facile',
            'medium': 'moyen',
            'hard': 'difficile'
        }
        
        return mapping.get(v_str, 'moyen')

class LearningResultBase(BaseModel):
    cours_id: int
    mode: LearningMode
    score_quiz: Optional[float] = Field(None, ge=0, le=100)
    temps_passe: int = Field(..., gt=0)
    taux_completion: float = Field(100, ge=0, le=100)

class LearningResultCreate(LearningResultBase):
    feedback: Optional[str] = None
    est_reussi: Optional[bool] = False

class LearningResult(LearningResultBase):
    id: int
    utilisateur_id: int
    nb_tentatives: int = 1
    est_reussi: bool = False
    date_debut: datetime
    date_completion: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class TokenData(BaseModel):
    user_id: Optional[int] = None


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

class StatsResponse(BaseModel):
    total_users: int
    total_courses: int
    total_questions: int
    total_results: int
    avg_score: Optional[float]
    recent_users: int
    active_today: int



class ErreurUtilisateurBase(BaseModel):
    utilisateur_id: int
    cours_id: int
    question_id: int
    question_texte: str
    reponse_utilisateur: str
    reponse_correcte: str
    mode_apprentissage: str
    score_obtenu: Optional[int] = 0
    points_possibles: Optional[int] = 0

class ErreurUtilisateurCreate(ErreurUtilisateurBase):
    pass

class ErreurUtilisateurResponse(ErreurUtilisateurBase):
    id: int
    nb_fois_erreur: int
    est_revu: bool
    date_erreur: datetime
    derniere_erreur: datetime
    date_revision: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ErreurStatsResponse(BaseModel):
    total_erreurs: int
    erreurs_non_revues: int
    erreurs_critiques: int
    cours_plus_erreurs: Optional[str]
    mode_plus_erreurs: Optional[str]

class MarquerRevueRequest(BaseModel):
    erreur_id: int

class CertificateGenerateRequest(BaseModel):
    user_id: int
    course_id: int
    score: float
    course_name: str
    mode: str
    date: Optional[str] = None

class CertificateResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    mode: str
    score: float
    certificate_url: str
    certificate_code: str
    date_created: datetime
    
    class Config:
        from_attributes = True

class CertificateVerifyResponse(BaseModel):
    valid: bool
    certificate: Optional[Dict[str, Any]] = None
    message: Optional[str] = None