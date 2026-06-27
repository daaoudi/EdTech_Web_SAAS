# backend/models/result.py
from pydantic import BaseModel, Field, validator, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum



class LearningMode(str, Enum):
    TEXT = "texte"
    AUDIO = "audio"
    VIDEO = "video"

class CompletionStatus(str, Enum):
    IN_PROGRESS = "en_cours"
    COMPLETED = "termine"
    FAILED = "echoue"



class LearningResultBase(BaseModel):
    cours_id: int = Field(..., ge=1, description="ID du cours")
    mode: LearningMode = Field(..., description="Mode d'apprentissage")
    temps_passe: int = Field(..., ge=1, description="Temps passé en secondes")
    taux_completion: float = Field(0.0, ge=0.0, le=100.0, description="Taux de complétion en %")
    nb_tentatives: int = Field(1, ge=1, description="Nombre de tentatives")
    est_reussi: bool = Field(False, description="Le cours a-t-il été réussi")
    feedback: Optional[str] = Field(None, description="Feedback sur l'apprentissage")



class LearningResultCreate(LearningResultBase):
    utilisateur_id: int = Field(..., ge=1, description="ID de l'utilisateur")
    score_quiz: Optional[float] = Field(None, ge=0.0, le=100.0, description="Score du quiz en %")
    
    @field_validator('score_quiz')
    @classmethod
    def validate_quiz_score(cls, v):
        """Valider le score du quiz"""
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Le score du quiz doit être entre 0 et 100')
        return v



class LearningResultUpdate(BaseModel):
    mode: Optional[LearningMode] = None
    temps_passe: Optional[int] = Field(None, ge=1)
    score_quiz: Optional[float] = Field(None, ge=0.0, le=100.0)
    taux_completion: Optional[float] = Field(None, ge=0.0, le=100.0)
    nb_tentatives: Optional[int] = Field(None, ge=1)
    est_reussi: Optional[bool] = None
    feedback: Optional[str] = None
    date_completion: Optional[datetime] = None



class LearningResultInDB(LearningResultBase):
    id: int
    utilisateur_id: int
    score_quiz: Optional[float] = None
    date_debut: datetime
    date_completion: Optional[datetime] = None
    cours_titre: Optional[str] = None  
    utilisateur_nom: Optional[str] = None  
    utilisateur_email: Optional[str] = None  
    
    @field_validator('date_completion', mode='before')
    @classmethod
    def parse_date_completion(cls, v):
        
        if v is None:
            return None
        return v



class LearningResultResponse(LearningResultBase):
    id: int
    utilisateur_id: int
    score_quiz: Optional[float] = None
    date_debut: datetime
    date_completion: Optional[datetime] = None
    cours_titre: Optional[str] = None
    utilisateur_nom: Optional[str] = None
    
    class Config:
        from_attributes = True



class DetailedLearningResult(LearningResultResponse):
    
    cours_difficulte: Optional[str] = None
    cours_duree: Optional[int] = None
    utilisateur_type_apprenant: Optional[str] = None
    reponses_quiz: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        from_attributes = True



class QuizResponseBase(BaseModel):
    resultat_id: int = Field(..., ge=1, description="ID du résultat")
    question_id: int = Field(..., ge=1, description="ID de la question")
    reponse_utilisateur: str = Field(..., description="Réponse de l'utilisateur")
    temps_reponse: Optional[int] = Field(None, ge=0, description="Temps de réponse en secondes")

class QuizResponseCreate(QuizResponseBase):
    pass

class QuizResponseInDB(QuizResponseBase):
    id: int
    est_correcte: bool
    date_reponse: datetime
    question_texte: Optional[str] = None  
    reponse_correcte: Optional[str] = None  

class QuizResponseResponse(QuizResponseBase):
    id: int
    est_correcte: bool
    date_reponse: datetime
    question_texte: Optional[str] = None
    reponse_correcte: Optional[str] = None
    
    class Config:
        from_attributes = True



class UserLearningStats(BaseModel):
    
    utilisateur_id: int
    nb_cours_complets: int = 0
    score_moyen: Optional[float] = None
    temps_total: int = 0  
    meilleur_score: Optional[float] = None
    pire_score: Optional[float] = None
    taux_reussite: Optional[float] = None
    distribution_modes: Dict[str, int] = Field(default_factory=dict)
    progression_niveau: Optional[float] = None
    derniere_activite: Optional[datetime] = None
    streak_courant: int = 0
    streak_max: int = 0



class CourseLearningStats(BaseModel):
    
    cours_id: int
    cours_titre: str
    nb_etudiants: int = 0
    score_moyen: Optional[float] = None
    temps_moyen: Optional[float] = None
    taux_reussite: Optional[float] = None
    distribution_modes: Dict[str, int] = Field(default_factory=dict)
    meilleur_etudiant: Optional[Dict[str, Any]] = None
    feedbacks: List[str] = Field(default_factory=list)



class LearningPreferenceUpdate(BaseModel):
    
    score_texte: Optional[float] = Field(None, ge=0.0, le=100.0)
    score_audio: Optional[float] = Field(None, ge=0.0, le=100.0)
    score_video: Optional[float] = Field(None, ge=0.0, le=100.0)
    confiance: Optional[float] = Field(None, ge=0.0, le=1.0)
    historique: Optional[List[Dict[str, Any]]] = None



def create_learning_result_response(
    result_in_db: LearningResultInDB
) -> LearningResultResponse:
    
    return LearningResultResponse(
        id=result_in_db.id,
        utilisateur_id=result_in_db.utilisateur_id,
        cours_id=result_in_db.cours_id,
        mode=result_in_db.mode,
        score_quiz=result_in_db.score_quiz,
        temps_passe=result_in_db.temps_passe,
        taux_completion=result_in_db.taux_completion,
        nb_tentatives=result_in_db.nb_tentatives,
        est_reussi=result_in_db.est_reussi,
        feedback=result_in_db.feedback,
        date_debut=result_in_db.date_debut,
        date_completion=result_in_db.date_completion,
        cours_titre=result_in_db.cours_titre,
        utilisateur_nom=result_in_db.utilisateur_nom
    )

def create_detailed_learning_result(
    result_in_db: LearningResultInDB,
    additional_data: Dict[str, Any] = None
) -> DetailedLearningResult:
    
    base_response = create_learning_result_response(result_in_db)
    
    data = base_response.dict()
    if additional_data:
        data.update(additional_data)
    
    return DetailedLearningResult(**data)

def calculate_learning_type(
    score_texte: float,
    score_audio: float,
    score_video: float
) -> str:
    
    scores = {
        'visuel': score_video,
        'auditif': score_audio,
        'lecture': score_texte
    }
    
    
    type_apprenant = max(scores, key=scores.get)
    
    
    sorted_scores = sorted(scores.values(), reverse=True)
    if len(sorted_scores) >= 2 and abs(sorted_scores[0] - sorted_scores[1]) < 10:
        return 'mixte'
    
    return type_apprenant

def calculate_user_stats(
    results: List[LearningResultResponse]
) -> UserLearningStats:
    
    if not results:
        return UserLearningStats(utilisateur_id=0)
    
    
    utilisateur_id = results[0].utilisateur_id
    nb_cours_complets = sum(1 for r in results if r.est_reussi)
    scores = [r.score_quiz for r in results if r.score_quiz is not None]
    temps_total = sum(r.temps_passe for r in results) / 60  
    
    
    distribution_modes = {}
    for mode in LearningMode:
        count = sum(1 for r in results if r.mode == mode)
        if count > 0:
            distribution_modes[mode.value] = count
    
    
    score_moyen = sum(scores) / len(scores) if scores else None
    meilleur_score = max(scores) if scores else None
    pire_score = min(scores) if scores else None
    taux_reussite = (nb_cours_complets / len(results)) * 100 if results else None
    
    
    derniere_activite = max(r.date_debut for r in results) if results else None
    
    return UserLearningStats(
        utilisateur_id=utilisateur_id,
        nb_cours_complets=nb_cours_complets,
        score_moyen=score_moyen,
        temps_total=int(temps_total),
        meilleur_score=meilleur_score,
        pire_score=pire_score,
        taux_reussite=taux_reussite,
        distribution_modes=distribution_modes,
        derniere_activite=derniere_activite,
        progression_niveau=min(100.0, (nb_cours_complets / 10) * 100)  
    )



__all__ = [
    'LearningMode',
    'CompletionStatus',
    'LearningResultBase',
    'LearningResultCreate',
    'LearningResultUpdate',
    'LearningResultInDB',
    'LearningResultResponse',
    'DetailedLearningResult',
    'QuizResponseBase',
    'QuizResponseCreate',
    'QuizResponseInDB',
    'QuizResponseResponse',
    'UserLearningStats',
    'CourseLearningStats',
    'LearningPreferenceUpdate',
    'create_learning_result_response',
    'create_detailed_learning_result',
    'calculate_learning_type',
    'calculate_user_stats'
]