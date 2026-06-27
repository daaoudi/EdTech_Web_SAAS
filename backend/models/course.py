
from pydantic import BaseModel, Field, validator, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import re



class DifficultyLevel(str, Enum):
    BEGINNER = "debutant"
    INTERMEDIATE = "intermediaire"
    ADVANCED = "avance"

class CourseStatus(str, Enum):
    DRAFT = "brouillon"
    PUBLISHED = "publie"
    ARCHIVED = "archive"



class CourseBase(BaseModel):
    titre: str = Field(..., min_length=1, max_length=255, description="Titre du cours")
    description: Optional[str] = Field(None, description="Description du cours")
    difficulte: Optional[DifficultyLevel] = DifficultyLevel.BEGINNER
    duree_estimee: Optional[int] = Field(None, ge=1, description="Durée estimée en minutes")
    chapitre_id: Optional[int] = Field(None, description="ID du chapitre parent")
    ordre_affichage: Optional[int] = Field(0, ge=0, description="Ordre d'affichage")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags du cours")
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        
        if v is None:
            return []
        
        cleaned_tags = []
        for tag in v:
            if isinstance(tag, str) and tag.strip():
                cleaned_tags.append(tag.strip().lower())
        return cleaned_tags



class CourseCreate(CourseBase):
    contenu_texte: str = Field(..., min_length=10, description="Contenu texte du cours")
    url_audio: Optional[str] = Field(None, description="URL de l'audio")
    url_video: Optional[str] = Field(None, description="URL de la vidéo")
    est_actif: bool = Field(True, description="Cours actif ou non")
    
    @field_validator('url_audio', 'url_video')
    @classmethod
    def validate_url(cls, v, info):
        
        if v is None:
            return v
        
        if not isinstance(v, str):
            raise ValueError('URL doit être une chaîne de caractères')
        
        
        url_pattern = re.compile(
            r'^(https?:\/\/)?'  
            r'([\da-z\.-]+)\.'  
            r'([a-z\.]{2,6})'  
            r'([\/\w \.-]*)*\/?$'  
        )
        
        if not url_pattern.match(v):
            raise ValueError('URL invalide')
        
        return v
    
    @field_validator('contenu_texte')
    @classmethod
    def validate_content_length(cls, v):
        
        if len(v) < 10:
            raise ValueError('Le contenu doit contenir au moins 10 caractères')
        return v



class CourseUpdate(BaseModel):
    titre: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    contenu_texte: Optional[str] = Field(None, min_length=10)
    difficulte: Optional[DifficultyLevel] = None
    duree_estimee: Optional[int] = Field(None, ge=1)
    url_audio: Optional[str] = None
    url_video: Optional[str] = None
    chapitre_id: Optional[int] = None
    ordre_affichage: Optional[int] = Field(None, ge=0)
    tags: Optional[List[str]] = None
    est_actif: Optional[bool] = None
    
    @field_validator('url_audio', 'url_video')
    @classmethod
    def validate_update_url(cls, v):
        """Valider les URLs pour la mise à jour"""
        if v is None:
            return v
        
        if not isinstance(v, str):
            raise ValueError('URL doit être une chaîne de caractères')
        
        
        url_pattern = re.compile(
            r'^(https?:\/\/)?'  
            r'([\da-z\.-]+)\.'  
            r'([a-z\.]{2,6})'  
            r'([\/\w \.-]*)*\/?$'  
        )
        
        if not url_pattern.match(v):
            raise ValueError('URL invalide')
        
        return v



class CourseInDB(CourseBase):
    id: int
    slug: str
    contenu_texte: str
    url_audio: Optional[str] = None
    url_video: Optional[str] = None
    est_actif: bool = True
    status: Optional[str] = "publié"
    created_by: Optional[int] = None
    last_modified_by: Optional[int] = None
    date_creation: datetime
    date_maj: Optional[datetime] = None
    chapitre_titre: Optional[str] = None  
    createur_email: Optional[str] = None  
    nb_questions: Optional[int] = 0 
    nb_completions: Optional[int] = 0  
    
    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v):
        
        if v is None:
            return []
        
        if isinstance(v, str):
            
            import json
            try:
                v = json.loads(v)
            except:
                
                v = [tag.strip() for tag in v.split(',') if tag.strip()]
        
        if isinstance(v, list):
            return v
        
        return []



class CourseResponse(CourseBase):
    id: int
    slug: str
    contenu_texte: str
    url_audio: Optional[str] = None
    url_video: Optional[str] = None
    est_actif: bool
    status: str = "publie"
    created_by: Optional[int] = None
    date_creation: datetime
    date_maj: Optional[datetime] = None
    chapitre_titre: Optional[str] = None
    createur_nom: Optional[str] = None
    nb_questions: int = 0
    nb_completions: int = 0
    score_moyen: Optional[float] = None
    temps_moyen: Optional[int] = None
    
    class Config:
        from_attributes = True



class CourseWithStats(CourseResponse):
    stats: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def from_course_response(cls, course_response: CourseResponse, stats: Dict[str, Any]):
        
        data = course_response.dict()
        data['stats'] = stats
        return cls(**data)



class ChapterBase(BaseModel):
    titre: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    ordre_affichage: Optional[int] = Field(0, ge=0)
    module: Optional[str] = Field(None, max_length=100)

class ChapterCreate(ChapterBase):
    pass

class ChapterUpdate(ChapterBase):
    pass

class ChapterResponse(ChapterBase):
    id: int
    nb_cours: int = 0
    
    class Config:
        from_attributes = True



class MediaBase(BaseModel):
    type_media: str = Field(..., description="Type de média (audio, video, image)")
    url: str = Field(..., description="URL du média")
    taille: Optional[int] = Field(None, ge=0, description="Taille en octets")
    duree: Optional[int] = Field(None, ge=0, description="Durée en secondes")
    format: Optional[str] = Field(None, max_length=20, description="Format du fichier")

class MediaCreate(MediaBase):
    cours_id: int = Field(..., ge=1, description="ID du cours associé")

class MediaResponse(MediaBase):
    id: int
    cours_id: int
    uploaded_by: Optional[int] = None
    date_upload: datetime
    est_verifie: bool = False
    
    class Config:
        from_attributes = True



class CourseEmbedding(BaseModel):
    cours_id: int
    embedding_vector: List[float]
    embedding_dimension: int = 384
    metadata: Dict[str, Any] = Field(default_factory=lambda: {"model": "sentence-bert", "version": "1.0"})
    date_calcul: Optional[datetime] = None

class EmbeddingCreate(CourseEmbedding):
    pass

class EmbeddingResponse(CourseEmbedding):
    id: int
    
    class Config:
        from_attributes = True



def generate_slug(title: str) -> str:
    
    import unicodedata
    import re
    
    
    slug = unicodedata.normalize('NFKD', title)
    slug = slug.encode('ascii', 'ignore').decode('ascii')
    slug = slug.lower()
    
    
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    
    
    slug = slug.strip('-')
    
    return slug

def create_course_response(course_in_db: CourseInDB) -> CourseResponse:
    
    return CourseResponse(
        id=course_in_db.id,
        titre=course_in_db.titre,
        slug=course_in_db.slug,
        description=course_in_db.description,
        contenu_texte=course_in_db.contenu_texte,
        difficulte=course_in_db.difficulte,
        duree_estimee=course_in_db.duree_estimee,
        url_audio=course_in_db.url_audio,
        url_video=course_in_db.url_video,
        chapitre_id=course_in_db.chapitre_id,
        ordre_affichage=course_in_db.ordre_affichage,
        tags=course_in_db.tags,
        est_actif=course_in_db.est_actif,
        status=course_in_db.status or "publie",
        created_by=course_in_db.created_by,
        date_creation=course_in_db.date_creation,
        date_maj=course_in_db.date_maj,
        chapitre_titre=course_in_db.chapitre_titre,
        createur_nom=course_in_db.createur_email,  
        nb_questions=course_in_db.nb_questions or 0,
        nb_completions=course_in_db.nb_completions or 0
    )



__all__ = [
    'DifficultyLevel',
    'CourseStatus',
    'CourseBase',
    'CourseCreate',
    'CourseUpdate',
    'CourseInDB',
    'CourseResponse',
    'CourseWithStats',
    'ChapterBase',
    'ChapterCreate',
    'ChapterUpdate',
    'ChapterResponse',
    'MediaBase',
    'MediaCreate',
    'MediaResponse',
    'CourseEmbedding',
    'EmbeddingCreate',
    'EmbeddingResponse',
    'generate_slug',
    'create_course_response'
]