
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import json



class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "choix_multiple"
    TRUE_FALSE = "vrai_faux"
    TEXT_INPUT = "texte_libre"
    CODE = "code"

class QuestionDifficulty(str, Enum):
    EASY = "facile"
    MEDIUM = "moyen"
    HARD = "difficile"

class LearningMode(str, Enum):
    TEXT = "texte"
    AUDIO = "audio"
    VIDEO = "video"



class QuestionBase(BaseModel):
    question: str = Field(..., min_length=1, description="Texte de la question")
    type_question: QuestionType = QuestionType.MULTIPLE_CHOICE
    points: int = Field(1, ge=1, le=20, description="Points pour la question")  
    difficulte: QuestionDifficulty = QuestionDifficulty.MEDIUM
    explication: Optional[str] = Field(None, description="Explication de la réponse")
    mode_specifique: Optional[LearningMode] = Field(None, description="Mode d'apprentissage spécifique")



class QuestionCreate(QuestionBase):
    cours_id: int = Field(..., ge=1, description="ID du cours associé")
    options: Optional[Dict[str, str]] = Field(None, description="Options de réponse (pour choix multiple)")
    reponse_correcte: str = Field(..., min_length=1, description="Réponse correcte")
    
    @field_validator('options', mode='before')
    @classmethod
    def validate_options(cls, v, info):
        """Valider les options de réponse"""
        if v is None:
            
            question_type = info.data.get('type_question') if info.data else None
            if question_type == QuestionType.MULTIPLE_CHOICE:
                raise ValueError('Les options sont requises pour les questions à choix multiple')
            return None
        
        if isinstance(v, str):
            try:
                v = json.loads(v)
            except json.JSONDecodeError:
                raise ValueError('Format JSON invalide pour les options')
        
        if isinstance(v, dict):
            
            if info.data and info.data.get('type_question') == QuestionType.MULTIPLE_CHOICE:
                if not all(key in v for key in ['A', 'B', 'C', 'D']):
                    raise ValueError('Les options doivent contenir les clés A, B, C, D')
            return v
        
        raise ValueError('Options doit être un dictionnaire ou une chaîne JSON')
    
    @field_validator('reponse_correcte')
    @classmethod
    def validate_correct_answer(cls, v, info):
        
        if not info.data:
            return v
        
        question_type = info.data.get('type_question')
        
        if question_type == QuestionType.MULTIPLE_CHOICE:
            options = info.data.get('options')
            if options:
                
                if v not in options:
                    raise ValueError('La réponse correcte doit correspondre à une des options')
            
            if v.upper() not in ['A', 'B', 'C', 'D']:
                raise ValueError('Pour les choix multiples, la réponse doit être A, B, C ou D')
        
        elif question_type == QuestionType.TRUE_FALSE:
            if v.lower() not in ['vrai', 'faux', 'true', 'false']:
                raise ValueError('Pour les questions vrai/faux, la réponse doit être "vrai" ou "faux"')
        
        return v



class QuestionUpdate(BaseModel):
    question: Optional[str] = Field(None, min_length=1)
    type_question: Optional[QuestionType] = None
    points: Optional[int] = Field(None, ge=1, le=10)
    difficulte: Optional[QuestionDifficulty] = None
    options: Optional[Dict[str, str]] = None
    reponse_correcte: Optional[str] = Field(None, min_length=1)
    explication: Optional[str] = None
    mode_specifique: Optional[LearningMode] = None
    
    @field_validator('options', mode='before')
    @classmethod
    def validate_options_update(cls, v, info):
        
        if v is None:
            return None
        
        if isinstance(v, str):
            try:
                v = json.loads(v)
            except json.JSONDecodeError:
                raise ValueError('Format JSON invalide pour les options')
        
        if isinstance(v, dict):
            return v
        
        raise ValueError('Options doit être un dictionnaire ou une chaîne JSON')
    
    @field_validator('reponse_correcte')
    @classmethod
    def validate_update_correct_answer(cls, v, info):
        
        if v is None:
            return v
        
        if not info.data:
            return v
        
        
        question_type = info.data.get('type_question')
        options = info.data.get('options')
        
        if question_type == QuestionType.MULTIPLE_CHOICE and options:
            if v not in options:
                raise ValueError('La réponse correcte doit correspondre à une des options')
        
        return v



class QuestionInDB(QuestionBase):
    id: int
    cours_id: int
    options: Optional[Dict[str, Any]] = None
    reponse_correcte: str
    created_by: Optional[int] = None
    date_creation: datetime
    cours_titre: Optional[str] = None  
    
    @field_validator('options', mode='before')
    @classmethod
    def parse_db_options(cls, v):
        
        if v is None:
            return None
        
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return {}
        
        if isinstance(v, dict):
            return v
        
        return {}



class QuestionResponse(QuestionBase):
    id: int
    cours_id: int
    options: Optional[Dict[str, str]] = None
    reponse_correcte: str
    created_by: Optional[int] = None
    date_creation: datetime
    cours_titre: Optional[str] = None
    
    @field_validator('options', mode='before')
    @classmethod
    def parse_response_options(cls, v):
        
        if v is None:
            return None
        
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return {}
        
        if isinstance(v, dict):
            return v
        
        return {}
    
    class Config:
        from_attributes = True



class QuestionWithAnswer(QuestionResponse):
    
    pass

class QuestionWithoutAnswer(QuestionResponse):
    
    class Config:
        exclude = {'reponse_correcte'}



class QuizAnswer(BaseModel):
    question_id: int
    reponse_utilisateur: str

class QuizSubmission(BaseModel):
    cours_id: int
    mode: LearningMode
    reponses: List[QuizAnswer]
    
    @field_validator('reponses')
    @classmethod
    def validate_responses(cls, v):
        
        if not v:
            raise ValueError('Au moins une réponse est requise')
        return v



class QuizResult(BaseModel):
    question_id: int
    question_text: str
    reponse_utilisateur: str
    reponse_correcte: str
    est_correcte: bool
    explication: Optional[str] = None
    points_obtenus: float = 0.0
    temps_reponse: Optional[int] = None



def create_question_response(question_in_db: QuestionInDB) -> QuestionResponse:
    
    return QuestionResponse(
        id=question_in_db.id,
        cours_id=question_in_db.cours_id,
        question=question_in_db.question,
        type_question=question_in_db.type_question,
        points=question_in_db.points,
        difficulte=question_in_db.difficulte,
        options=question_in_db.options,
        reponse_correcte=question_in_db.reponse_correcte,
        explication=question_in_db.explication,
        mode_specifique=question_in_db.mode_specifique,
        created_by=question_in_db.created_by,
        date_creation=question_in_db.date_creation,
        cours_titre=question_in_db.cours_titre
    )

def format_options_for_display(options: Dict[str, str]) -> List[Dict[str, str]]:
    
    if not options:
        return []
    
    formatted = []
    for key, value in options.items():
        formatted.append({
            "lettre": key,
            "texte": value
        })
    return formatted

def calculate_quiz_score(results: List[QuizResult]) -> Dict[str, Any]:
    
    if not results:
        return {
            "score_total": 0.0,
            "points_obtenus": 0.0,
            "points_possibles": 0.0,
            "pourcentage": 0.0,
            "nb_correctes": 0,
            "nb_total": 0
        }
    
    points_obtenus = sum(r.points_obtenus for r in results)
    points_possibles = len(results)  
    
    return {
        "score_total": points_obtenus,
        "points_obtenus": points_obtenus,
        "points_possibles": points_possibles,
        "pourcentage": (points_obtenus / points_possibles) * 100 if points_possibles > 0 else 0,
        "nb_correctes": sum(1 for r in results if r.est_correcte),
        "nb_total": len(results)
    }



__all__ = [
    'QuestionType',
    'QuestionDifficulty',
    'LearningMode',
    'QuestionBase',
    'QuestionCreate',
    'QuestionUpdate',
    'QuestionInDB',
    'QuestionResponse',
    'QuestionWithAnswer',
    'QuestionWithoutAnswer',
    'QuizAnswer',
    'QuizSubmission',
    'QuizResult',
    'create_question_response',
    'format_options_for_display',
    'calculate_quiz_score'
]