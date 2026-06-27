
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List, Union
import bcrypt
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import logging
import json

from config import config
from models.user import TokenData, UserInDB, UserRole
from models.database import db

logger = logging.getLogger(__name__)




oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login",
    auto_error=True
)



class AuthService:
    
    
    def __init__(self):
        self.secret_key = config.SECRET_KEY
        self.algorithm = config.ALGORITHM
        self.token_expire_minutes = config.ACCESS_TOKEN_EXPIRE_MINUTES
    
    
    
    def hash_password(self, password: str) -> str:
        
        try:
            logger.debug(f"Hashing password for new user")
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Erreur lors du hashage du mot de passe: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors du traitement du mot de passe"
            )
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        
        try:
            logger.debug(f"Verifying password against hash")
            result = bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
            logger.debug(f"Password verification result: {result}")
            return result
        except ValueError as e:
            logger.error(f"Hash invalide: {e}")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du mot de passe: {e}")
            return False
    
    

    
    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        
        try:
            logger.info(f"🔐 Tentative d'authentification pour: {email}")
            
            async with db.get_connection() as conn:
                
                query = """
                SELECT 
                    u.id,
                    u.email,
                    u.nom,
                    u.prenom,
                    u.role_id,
                    u.type_apprenant,
                    u.niveau_global,
                    u.preferences,
                    u.est_actif,
                    u.date_inscription,
                    u.derniere_connexion,
                    u.mot_de_passe_hash,
                    r.nom_role as role_name
                FROM utilisateurs u
                LEFT JOIN roles r ON u.role_id = r.id
                WHERE u.email = $1
                """
                
                row = await conn.fetchrow(query, email)
                
                if not row:
                    logger.warning(f"❌ Utilisateur non trouvé: {email}")
                    return None
                
                
                if not row['est_actif']:
                    logger.warning(f"❌ Compte inactif: {email}")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Compte désactivé"
                    )
                
                logger.info(f"✅ Utilisateur trouvé: {row['email']}")
                logger.debug(f"   Hash stocké: {row['mot_de_passe_hash'][:15]}...")
                
                
                is_valid = self.verify_password(password, row['mot_de_passe_hash'])
                
                if not is_valid:
                    logger.warning(f"❌ Mot de passe incorrect pour: {email}")
                    
                    return None
                
                logger.info(f"   Validation: ✅ SUCCÈS")
                
                
                try:
                    await conn.execute(
                        """
                        UPDATE utilisateurs 
                        SET derniere_connexion = $1 
                        WHERE id = $2
                        """,
                        datetime.now(timezone.utc), 
                        row['id']
                    )
                except Exception as update_error:
                    logger.warning(f"Erreur mise à jour dernière connexion: {update_error}")
                    
                
                
                user_data = {
                    'id': row['id'],
                    'email': row['email'],
                    'nom': row['nom'],
                    'prenom': row['prenom'],
                    'role_id': row['role_id'],
                    'role_name': row['role_name'],
                    'type_apprenant': row['type_apprenant'],
                    'niveau_global': row['niveau_global'],
                    'preferences': row['preferences'],
                    'est_actif': row['est_actif'],
                    'date_inscription': row['date_inscription'],
                    'derniere_connexion': row['derniere_connexion'],
                    'mot_de_passe_hash': row['mot_de_passe_hash']  
                }
                
                
                try:
                    user = UserInDB(**user_data)
                    logger.info(f"🎉 Authentification réussie: {email} (ID: {user.id})")
                    logger.debug(f"   Rôle: {user.role_name}")
                    logger.debug(f"   Préférences: {user.preferences}")
                    return user
                    
                except Exception as model_error:
                    logger.error(f"❌ Erreur création modèle UserInDB: {model_error}")
                    logger.error(f"   Données utilisateur: {user_data}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Erreur lors du traitement des données utilisateur"
                    )
                    
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Erreur d'authentification: {e}", exc_info=True)
            return None
    
    
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        
        try:
            to_encode = data.copy()
            
            
            now = datetime.now(timezone.utc)
            
            if expires_delta:
                expire = now + expires_delta
            else:
                expire = now + timedelta(minutes=self.token_expire_minutes)
            
            
            to_encode.update({
                "iat": int(now.timestamp()),      
                "exp": int(expire.timestamp()),   
                "type": "access_token",           
                "iss": config.APP_TITLE,          
                "aud": "elearning-platform"       
            })
            
            
            encoded_jwt = jwt.encode(
                to_encode, 
                self.secret_key, 
                algorithm=self.algorithm
            )
            
            logger.info(f"🔐 Token créé pour: {data.get('email', 'unknown')}")
            logger.debug(f"   Expiration: {expire}")
            logger.debug(f"   Claims: {list(to_encode.keys())}")
            
            return encoded_jwt
            
        except Exception as e:
            logger.error(f"❌ Erreur création token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la création du token"
            )
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                audience="elearning-platform",
                options={"verify_aud": True}
            )
            return payload
        except JWTError as e:
            logger.error(f"❌ Erreur décodage token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide ou expiré",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def create_refresh_token(self, user_id: int, email: str) -> str:
        
        refresh_data = {
            "sub": str(user_id),
            "email": email,
            "type": "refresh_token"
        }
        
        
        refresh_expires = timedelta(days=7)
        
        return self.create_access_token(refresh_data, refresh_expires)
    
    
    
    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> UserInDB:
        
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Impossible de valider les identifiants",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            
            payload = self.decode_token(token)
            
            
            user_id_str = payload.get("sub")
            email = payload.get("email")
            token_type = payload.get("type")
            
            if not user_id_str or not email:
                logger.warning("Token incomplet: missing sub or email")
                raise credentials_exception
            
            if token_type != "access_token":
                logger.warning(f"Token de type incorrect: {token_type}")
                raise credentials_exception
            
            user_id = int(user_id_str)
            
            logger.debug(f"Token validé pour user_id: {user_id}, email: {email}")
            
        except (ValueError, JWTError) as e:
            logger.error(f"Erreur validation token: {e}")
            raise credentials_exception
        
        
        try:
            async with db.get_connection() as conn:
                query = """
                SELECT 
                    u.id,
                    u.email,
                    u.nom,
                    u.prenom,
                    u.role_id,
                    u.type_apprenant,
                    u.niveau_global,
                    u.preferences,
                    u.est_actif,
                    u.date_inscription,
                    u.derniere_connexion,
                    u.mot_de_passe_hash,
                    r.nom_role as role_name
                FROM utilisateurs u
                LEFT JOIN roles r ON u.role_id = r.id
                WHERE u.id = $1 AND u.email = $2
                """
                
                row = await conn.fetchrow(query, user_id, email)
                
                if not row:
                    logger.warning(f"❌ Utilisateur non trouvé dans DB: {email}")
                    raise credentials_exception
                
                
                if not row['est_actif']:
                    logger.warning(f"❌ Compte inactif: {email}")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Compte désactivé"
                    )
                
                
                user_data = {
                    'id': row['id'],
                    'email': row['email'],
                    'nom': row['nom'],
                    'prenom': row['prenom'],
                    'role_id': row['role_id'],
                    'role_name': row['role_name'],
                    'type_apprenant': row['type_apprenant'],
                    'niveau_global': row['niveau_global'],
                    'preferences': row['preferences'],
                    'est_actif': row['est_actif'],
                    'date_inscription': row['date_inscription'],
                    'derniere_connexion': row['derniere_connexion'],
                    'mot_de_passe_hash': row['mot_de_passe_hash']
                }
                
                user = UserInDB(**user_data)
                logger.debug(f"Utilisateur récupéré: {user.email}, rôle: {user.role_name}")
                return user
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Erreur récupération utilisateur: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la récupération des informations utilisateur"
            )
    
    async def get_current_active_user(self, current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
        """Vérifier que l'utilisateur est actif"""
        if not current_user.est_actif:
            logger.warning(f"Tentative d'accès avec compte inactif: {current_user.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Compte désactivé"
            )
        return current_user
    
    
    
    async def check_permission(self, user: UserInDB, permission_name: str) -> bool:
        
        try:
            async with db.get_connection() as conn:
                
                query = """
                SELECT permissions
                FROM roles
                WHERE id = $1
                """
                permissions_json = await conn.fetchval(query, user.role_id)
                
                if not permissions_json:
                    return False
                
                
                import json
                permissions = json.loads(permissions_json) if isinstance(permissions_json, str) else permissions_json
                
                
                has_permission = permissions.get(permission_name, False)
                
                logger.debug(f"Vérification permission '{permission_name}' pour {user.email}: {has_permission}")
                return has_permission
                
        except Exception as e:
            logger.error(f"Erreur vérification permission: {e}")
            return False
    
    def require_permission(self, permission_name: str):
        
        async def permission_dependency(
            current_user: UserInDB = Depends(get_current_active_user)
        ):
            has_permission = await self.check_permission(current_user, permission_name)
            if not has_permission:
                logger.warning(f"Permission refusée '{permission_name}' pour {current_user.email}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission_name}' requise"
                )
            return current_user
        return permission_dependency
    
    
    
    def require_admin(self):
        
        async def admin_dependency(
            current_user: UserInDB = Depends(get_current_active_user)
        ):
            
            is_admin = (current_user.role_id == 1 or 
                       (current_user.role_name and current_user.role_name.lower() == "admin"))
            
            if not is_admin:
                logger.warning(f"Accès admin refusé pour {current_user.email}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Administrateur requis"
                )
            return current_user
        return admin_dependency
    
    def require_moderator(self):
        
        async def moderator_dependency(
            current_user: UserInDB = Depends(get_current_active_user)
        ):
            
            allowed_role_ids = [1, 3]
            allowed_role_names = ["admin", "moderateur", "moderator"]
            
            is_allowed = (
                current_user.role_id in allowed_role_ids or
                (current_user.role_name and current_user.role_name.lower() in allowed_role_names)
            )
            
            if not is_allowed:
                logger.warning(f"Accès modérateur refusé pour {current_user.email}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Modérateur ou administrateur requis"
                )
            return current_user
        return moderator_dependency
    
    
    
    async def register_user(self, user_data: Dict[str, Any]) -> UserInDB:
        
        try:
            logger.info(f"📝 Tentative d'inscription pour: {user_data.get('email')}")
            
            
            async with db.get_connection() as conn:
                existing_user = await conn.fetchval(
                    "SELECT id FROM utilisateurs WHERE email = $1",
                    user_data['email']
                )
                
                if existing_user:
                    logger.warning(f"❌ Email déjà utilisé: {user_data['email']}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cet email est déjà utilisé"
                    )
                
                
                hashed_password = self.hash_password(user_data['mot_de_passe'])
                
                
                role_id = user_data.get('role_id', 2)  
                now = datetime.now(timezone.utc)
                
                # Insérer l'utilisateur
                query = """
                INSERT INTO utilisateurs (
                    email, nom, prenom, mot_de_passe_hash, role_id,
                    type_apprenant, niveau_global, preferences,
                    est_actif, date_inscription, derniere_connexion
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                RETURNING *
                """
                
                row = await conn.fetchrow(
                    query,
                    user_data['email'],
                    user_data.get('nom'),
                    user_data.get('prenom'),
                    hashed_password,
                    role_id,
                    user_data.get('type_apprenant'),
                    user_data.get('niveau_global', 'débutant'),
                    json.dumps(user_data.get('preferences', {})),
                    True,  
                    now,   
                    now    
                )
                
                
                role_query = "SELECT nom_role FROM roles WHERE id = $1"
                role_name = await conn.fetchval(role_query, role_id)
                
                
                user_obj = UserInDB(
                    id=row['id'],
                    email=row['email'],
                    nom=row['nom'],
                    prenom=row['prenom'],
                    role_id=row['role_id'],
                    role_name=role_name,
                    type_apprenant=row['type_apprenant'],
                    niveau_global=row['niveau_global'],
                    preferences=row['preferences'],
                    est_actif=row['est_actif'],
                    date_inscription=row['date_inscription'],
                    derniere_connexion=row['derniere_connexion']
                )
                
                logger.info(f"✅ Inscription réussie: {user_data['email']} (ID: {user_obj.id})")
                return user_obj
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'inscription: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de l'inscription"
            )
    
    
    
    async def initiate_password_reset(self, email: str) -> bool:
        
        try:
            logger.info(f"🔑 Initiation réinitialisation mot de passe pour: {email}")
            
            async with db.get_connection() as conn:
                
                user_id = await conn.fetchval(
                    "SELECT id FROM utilisateurs WHERE email = $1 AND est_actif = TRUE",
                    email
                )
                
                if not user_id:
                    
                    logger.info(f"Email non trouvé (ou compte inactif): {email}")
                    return True  
                
                
                reset_token = self.create_access_token(
                    data={
                        "sub": str(user_id),
                        "email": email,
                        "type": "password_reset"
                    },
                    expires_delta=timedelta(hours=24)  
                )
                
                
                
                logger.info(f"Token de réinitialisation généré pour {email}")
                logger.debug(f"Token: {reset_token[:20]}...")
                
                # TODO: Implémenter l'envoi d'email
                # send_reset_email(email, reset_token)
                
                return True
                
        except Exception as e:
            logger.error(f"Erreur initiation réinitialisation: {e}")
            return False
    
    async def reset_password(self, token: str, new_password: str) -> bool:
        """Réinitialiser le mot de passe avec un token"""
        try:
            
            payload = self.decode_token(token)
            
            if payload.get("type") != "password_reset":
                logger.warning("Token de réinitialisation invalide")
                return False
            
            user_id = int(payload.get("sub"))
            email = payload.get("email")
            
            
            hashed_password = self.hash_password(new_password)
            
            
            async with db.get_connection() as conn:
                result = await conn.execute(
                    """
                    UPDATE utilisateurs 
                    SET mot_de_passe_hash = $1 
                    WHERE id = $2 AND email = $3 AND est_actif = TRUE
                    """,
                    hashed_password, user_id, email
                )
                
                if "UPDATE 1" in result:
                    logger.info(f"✅ Mot de passe réinitialisé pour: {email}")
                    return True
                else:
                    logger.warning(f"Échec réinitialisation pour: {email}")
                    return False
                    
        except (JWTError, ValueError) as e:
            logger.error(f"Token de réinitialisation invalide: {e}")
            return False
        except Exception as e:
            logger.error(f"Erreur réinitialisation mot de passe: {e}")
            return False




auth_service = AuthService()



get_current_user = auth_service.get_current_user
get_current_active_user = auth_service.get_current_active_user
require_permission = auth_service.require_permission
require_admin = auth_service.require_admin
require_moderator = auth_service.require_moderator



def get_token_payload(token: str) -> Dict[str, Any]:
    
    try:
        payload = jwt.decode(
            token,
            config.SECRET_KEY,
            algorithms=[config.ALGORITHM],
            options={"verify_signature": False}
        )
        return payload
    except JWTError as e:
        logger.error(f"Erreur décodage token: {e}")
        return {}

def is_token_expired(token: str) -> bool:
    
    try:
        payload = get_token_payload(token)
        exp = payload.get("exp")
        if not exp:
            return True
        
        now = datetime.now(timezone.utc).timestamp()
        return exp < now
    except:
        return True

def get_user_id_from_token(token: str) -> Optional[int]:
    
    try:
        payload = get_token_payload(token)
        user_id_str = payload.get("sub")
        return int(user_id_str) if user_id_str else None
    except:
        return None



__all__ = [
    
    'oauth2_scheme',
    
    
    'AuthService',
    'auth_service',
    
    
    'get_current_user',
    'get_current_active_user',
    'require_permission',
    'require_admin',
    'require_moderator',
    
    
    'get_token_payload',
    'is_token_expired',
    'get_user_id_from_token'
]