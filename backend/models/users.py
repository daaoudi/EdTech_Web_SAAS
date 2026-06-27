
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from enum import Enum
import json
import logging
import re

logger = logging.getLogger(__name__)



class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "utilisateur"
    MODERATOR = "moderateur"

class LearningType(str, Enum):
    VISUAL = "visuel"
    AUDITORY = "auditif"
    KINESTHETIC = "kinesthesique"
    READING = "lecture"  
    MIXED = "mixte"

class GlobalLevel(str, Enum):
    BEGINNER = "debutant"
    INTERMEDIATE = "intermediaire"
    ADVANCED = "avance"
    EXPERT = "expert"



class UserBase(BaseModel):
    email: EmailStr
    nom: Optional[str] = None
    prenom: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)



class UserCreate(UserBase):
    mot_de_passe: str = Field(..., min_length=8, description="Mot de passe d'au moins 8 caractères")
    role_id: Optional[int] = 2 
    type_apprenant: Optional[LearningType] = None
    niveau_global: Optional[GlobalLevel] = GlobalLevel.BEGINNER
    preferences: Optional[Dict[str, Any]] = None
    
    @field_validator('mot_de_passe')
    @classmethod
    def validate_password(cls, v):
        """Valider la force du mot de passe"""
        errors = []
        
        
        if len(v) < 8:
            errors.append('doit contenir au moins 8 caractères')
        
        
        if not any(char.isdigit() for char in v):
            errors.append('doit contenir au moins un chiffre')
        
        
        if not any(char.isupper() for char in v):
            errors.append('doit contenir au moins une majuscule')
        
        
        if not any(char.islower() for char in v):
            errors.append('doit contenir au moins une minuscule')
        
        
        if not re.search(r'[A-Z]', v):
            errors.append('doit contenir au moins une majuscule (regex)')
        if not re.search(r'[a-z]', v):
            errors.append('doit contenir au moins une minuscule (regex)')
        if not re.search(r'\d', v):
            errors.append('doit contenir au moins un chiffre (regex)')
        
        if errors:
            raise ValueError('Le mot de passe ' + ', '.join(errors))
        
        return v
    
    model_config = ConfigDict(use_enum_values=True)



class UserLogin(BaseModel):
    email: EmailStr
    mot_de_passe: str



class UserUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[EmailStr] = None
    type_apprenant: Optional[str] = None
    niveau_global: Optional[str] = None  
    preferences: Optional[Dict[str, Any]] = None
    role_id: Optional[int] = None
    
    @field_validator('niveau_global')
    @classmethod
    def validate_niveau_global(cls, v: str) -> str:
        if v is None:
            return v
        valid_levels = ['débutant', 'intermédiaire', 'avancé']
        
        normalized = v.lower().replace('é', 'e').replace('è', 'e')
        if normalized == 'intermediaire':
            normalized = 'intermédiaire'
        if normalized in valid_levels or v in valid_levels:
            return v
        raise ValueError(f'Niveau invalide. Doit être débutant, intermédiaire ou avancé')
    
    @field_validator('type_apprenant')
    @classmethod
    def validate_type_apprenant(cls, v: str) -> str:
        if v is None:
            return v
        valid_types = ['visuel', 'auditif', 'lecture', 'mixte']
        if v.lower() in valid_types:
            return v.lower()
        raise ValueError(f'Type invalide. Doit être visuel, auditif, lecture ou mixte')
    
    model_config = ConfigDict(extra='ignore')



class UserInDB(UserBase):
    id: int
    role_id: int
    role_name: Optional[str] = None  
    permissions: Dict[str, Any] = {}  
    type_apprenant: Optional[str] = None
    niveau_global: Optional[str] = "debutant"
    preferences: Dict[str, Any] = {}
    est_actif: bool = True
    date_inscription: datetime
    derniere_connexion: Optional[datetime] = None
    date_maj: Optional[datetime] = None  
    mot_de_passe_hash: Optional[str] = None  
    
    
    @field_validator('preferences', mode='before')
    @classmethod
    def parse_preferences(cls, v):
        
        logger.debug(f"Parsing preferences: {type(v)} - {v}")
        
        if v is None:
            return {}
        
        if isinstance(v, str):
            try:
                
                parsed = json.loads(v)
                logger.debug(f"Successfully parsed preferences JSON: {parsed}")
                return parsed
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse preferences as JSON: {e}")
                
                if v.startswith('{') and v.endswith('}'):
                    
                    cleaned = v.replace("'", '"')
                    try:
                        parsed = json.loads(cleaned)
                        logger.debug(f"Successfully parsed cleaned JSON: {parsed}")
                        return parsed
                    except:
                        pass
                return {}
        
        
        if isinstance(v, dict):
            return v
        
        
        logger.warning(f"Unexpected preferences type: {type(v)}")
        return {}
    
    
    @field_validator('permissions', mode='before')
    @classmethod
    def parse_permissions(cls, v):
        
        if v is None:
            return {}
        
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return {}
        
        if isinstance(v, dict):
            return v
        
        return {}
    
    
    @field_validator('role_name', mode='after')
    @classmethod
    def set_default_role_name(cls, v, info):
        
        if v is None:
            role_id = info.data.get('role_id')
            role_mapping = {
                1: "admin",
                2: "utilisateur",
                3: "moderateur"
            }
            return role_mapping.get(role_id, "utilisateur")
        return v
    
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )



class UserResponse(UserBase):
    id: int
    role_id: int  
    role_name: str
    type_apprenant: Optional[str] = None
    niveau_global: str = "debutant"
    est_actif: bool = True
    date_inscription: datetime
    derniere_connexion: Optional[datetime] = None  
    
    model_config = ConfigDict(from_attributes=True)



class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: str  
    role: str
    role_id: int  
    expires_in: int

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None
    role_id: Optional[int] = None



class Permission(BaseModel):
    read: bool = True
    write: bool = False
    delete: bool = False
    manage_users: bool = False
    manage_courses: bool = False
    view_logs: bool = False

class RoleBase(BaseModel):
    nom_role: str
    description: Optional[str] = None
    permissions: Dict[str, bool] = {}

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)



class UserPreferences(BaseModel):
    theme: str = "clair"
    notifications: bool = True
    language: str = "fr"
    email_notifications: bool = True
    push_notifications: bool = False
    daily_goal: int = 30  
    show_progress: bool = True
    auto_play_videos: bool = False
    text_size: str = "medium"

class UserStats(BaseModel):
    total_courses: int = 0
    completed_courses: int = 0
    total_time: int = 0  
    current_streak: int = 0
    longest_streak: int = 0
    average_score: float = 0.0
    certificates_count: int = 0

class UserProfile(UserResponse):
    derniere_connexion: Optional[datetime] = None
    date_maj: Optional[datetime] = None
    preferences: UserPreferences = UserPreferences()
    stats: UserStats = UserStats()
    permissions: Dict[str, Any] = {}
    
    @field_validator('preferences', mode='before')
    @classmethod
    def parse_user_preferences(cls, v):
        
        if isinstance(v, dict):
            return UserPreferences(**v)
        return UserPreferences()
    
    @field_validator('permissions', mode='before')
    @classmethod
    def parse_profile_permissions(cls, v):
        
        if v is None:
            return {}
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return {}
        return {}



class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        errors = []
        if len(v) < 8:
            errors.append('doit contenir au moins 8 caractères')
        if not any(char.isdigit() for char in v):
            errors.append('doit contenir au moins un chiffre')
        if not any(char.isupper() for char in v):
            errors.append('doit contenir au moins une majuscule')
        if not any(char.islower() for char in v):
            errors.append('doit contenir au moins une minuscule')
        
        if errors:
            raise ValueError('Le nouveau mot de passe ' + ', '.join(errors))
        return v

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        errors = []
        if len(v) < 8:
            errors.append('doit contenir au moins 8 caractères')
        if not any(char.isdigit() for char in v):
            errors.append('doit contenir au moins un chiffre')
        if not any(char.isupper() for char in v):
            errors.append('doit contenir au moins une majuscule')
        if not any(char.islower() for char in v):
            errors.append('doit contenir au moins une minuscule')
        
        if errors:
            raise ValueError('Le mot de passe ' + ', '.join(errors))
        return v



class RegistrationRequest(BaseModel):
    email: EmailStr
    mot_de_passe: str
    nom: Optional[str] = None
    prenom: Optional[str] = None
    accept_terms: bool = False
    
    @field_validator('accept_terms')
    @classmethod
    def validate_terms(cls, v):
        if not v:
            raise ValueError('Vous devez accepter les conditions d\'utilisation')
        return v
    
    @field_validator('mot_de_passe')
    @classmethod
    def validate_password(cls, v):
        errors = []
        if len(v) < 8:
            errors.append('doit contenir au moins 8 caractères')
        if not any(char.isdigit() for char in v):
            errors.append('doit contenir au moins un chiffre')
        if not any(char.isupper() for char in v):
            errors.append('doit contenir au moins une majuscule')
        if not any(char.islower() for char in v):
            errors.append('doit contenir au moins une minuscule')
        
        if errors:
            raise ValueError('Le mot de passe ' + ', '.join(errors))
        return v

class RegistrationResponse(BaseModel):
    id: int
    email: EmailStr
    message: str = "Inscription réussie. Vous pouvez maintenant vous connecter."



def create_user_response(user_in_db: UserInDB) -> UserResponse:
    
    return UserResponse(
        id=user_in_db.id,
        email=user_in_db.email,
        nom=user_in_db.nom,
        prenom=user_in_db.prenom,
        role_id=user_in_db.role_id,
        role_name=user_in_db.role_name or "utilisateur",
        type_apprenant=user_in_db.type_apprenant,
        niveau_global=user_in_db.niveau_global,
        date_inscription=user_in_db.date_inscription,
        derniere_connexion=user_in_db.derniere_connexion,
        est_actif=user_in_db.est_actif
    )

def create_user_profile(user_in_db: UserInDB, stats: Optional[UserStats] = None) -> UserProfile:
    
    
    prefs_dict = user_in_db.preferences if isinstance(user_in_db.preferences, dict) else {}
    try:
        preferences = UserPreferences(**prefs_dict)
    except:
        preferences = UserPreferences()
    
    
    user_stats = stats or UserStats()
    
    return UserProfile(
        id=user_in_db.id,
        email=user_in_db.email,
        nom=user_in_db.nom,
        prenom=user_in_db.prenom,
        role_id=user_in_db.role_id,
        role_name=user_in_db.role_name or "utilisateur",
        type_apprenant=user_in_db.type_apprenant,
        niveau_global=user_in_db.niveau_global,
        date_inscription=user_in_db.date_inscription,
        derniere_connexion=user_in_db.derniere_connexion,
        date_maj=user_in_db.date_maj,
        est_actif=user_in_db.est_actif,
        preferences=preferences,
        stats=user_stats,
        permissions=user_in_db.permissions
    )

def create_token_response(token: str, user: UserInDB, expires_in: int = 3600) -> Token:
    
    return Token(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        role=user.role_name or "utilisateur",
        role_id=user.role_id,
        expires_in=expires_in
    )



__all__ = [
    
    'UserRole',
    'LearningType',
    'GlobalLevel',
    
    
    'UserBase',
    'UserCreate',
    'UserLogin',
    'UserUpdate',
    'UserInDB',
    'UserResponse',
    'UserProfile',
    
    
    'Token',
    'TokenData',
    'create_token_response',
    
    
    'Permission',
    'RoleBase',
    'RoleCreate',
    'RoleResponse',
    
    
    'UserPreferences',
    'UserStats',
    
    
    'PasswordChange',
    'PasswordResetRequest',
    'PasswordReset',
    
    
    'RegistrationRequest',
    'RegistrationResponse',
    
    
    'create_user_response',
    'create_user_profile'
]