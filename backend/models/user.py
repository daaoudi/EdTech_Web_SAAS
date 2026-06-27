
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)



class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "utilisateur"
    MODERATOR = "moderateur"

class LearningType(str, Enum):
    VISUAL = "visuel"
    AUDITORY = "auditif"
    KINESTHETIC = "kinesthesique"
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
    mot_de_passe: str
    role_id: Optional[int] = None  
    type_apprenant: Optional[LearningType] = None
    niveau_global: Optional[GlobalLevel] = GlobalLevel.BEGINNER
    preferences: Optional[Dict[str, Any]] = None
    
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
    
    model_config = ConfigDict(use_enum_values=True)



class UserLogin(BaseModel):
    email: EmailStr
    mot_de_passe: str



class UserUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[EmailStr] = None
    type_apprenant: Optional[LearningType] = None
    niveau_global: Optional[GlobalLevel] = None
    preferences: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(use_enum_values=True)



class UserInDB(UserBase):
    id: int
    role_id: int
    role_name: Optional[str] = None  
    type_apprenant: Optional[str] = None
    niveau_global: Optional[str] = "debutant"
    preferences: Dict[str, Any] = {}
    est_actif: bool = True
    date_inscription: datetime
    derniere_connexion: Optional[datetime] = None
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
    role_name: str
    type_apprenant: Optional[str] = None
    niveau_global: str = "debutant"
    date_inscription: datetime
    est_actif: bool = True
    
    model_config = ConfigDict(from_attributes=True)



class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    role: str
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

class UserStats(BaseModel):
    total_courses: int = 0
    completed_courses: int = 0
    total_time: int = 0  
    current_streak: int = 0
    longest_streak: int = 0

class UserProfile(UserResponse):
    derniere_connexion: Optional[datetime] = None
    preferences: UserPreferences = UserPreferences()
    stats: UserStats = UserStats()
    
    @field_validator('preferences', mode='before')
    @classmethod
    def parse_user_preferences(cls, v):
        
        if isinstance(v, dict):
            return UserPreferences(**v)
        return UserPreferences()



class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Le mot de passe doit contenir au moins 8 caractères')
        if not any(char.isdigit() for char in v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        if not any(char.isupper() for char in v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule')
        return v

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Le mot de passe doit contenir au moins 8 caractères')
        if not any(char.isdigit() for char in v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        if not any(char.isupper() for char in v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule')
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
        if len(v) < 8:
            raise ValueError('Le mot de passe doit contenir au moins 8 caractères')
        if not any(char.isdigit() for char in v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        if not any(char.isupper() for char in v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule')
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
        role_name=user_in_db.role_name or "utilisateur",
        type_apprenant=user_in_db.type_apprenant,
        niveau_global=user_in_db.niveau_global,
        date_inscription=user_in_db.date_inscription,
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
        role_name=user_in_db.role_name or "utilisateur",
        type_apprenant=user_in_db.type_apprenant,
        niveau_global=user_in_db.niveau_global,
        date_inscription=user_in_db.date_inscription,
        derniere_connexion=user_in_db.derniere_connexion,
        est_actif=user_in_db.est_actif,
        preferences=preferences,
        stats=user_stats
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