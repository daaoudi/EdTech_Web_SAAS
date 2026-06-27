
import asyncpg
from typing import Optional, Any, Dict, List, Union
from contextlib import asynccontextmanager
import logging
from datetime import datetime
import json
from config import DATABASE_URL
import traceback

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        
        try:
            self.pool = await asyncpg.create_pool(
                DATABASE_URL,
                min_size=1,
                max_size=20,
                command_timeout=60,
                statement_cache_size=0  
            )
            
            
            async with self.pool.acquire() as conn:
                await conn.execute("SELECT 1")
            
            logger.info("✅ Connexion à la base de données établie avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur de connexion à la base: {e}")
            raise
    
    async def disconnect(self):
        
        if self.pool:
            await self.pool.close()
            logger.info("Connexion à la base de données fermée")
    
    @asynccontextmanager
    async def get_connection(self):
        
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as connection:
            yield connection
    
    @asynccontextmanager
    async def get_transaction(self):
        
        async with self.get_connection() as connection:
            async with connection.transaction():
                yield connection

    
    
    async def create(self, table: str, data: Dict[str, Any], returning: str = "id") -> Any:
        
        
        
        
            
            
            
        
        
            
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join([f'${i+1}' for i in range(len(data))])
        values = list(data.values())
        
        query = f"""
            INSERT INTO {table} ({columns})
            VALUES ({placeholders})
            RETURNING {returning}
        """
        
        try:
            async with self.get_connection() as conn:
                result = await conn.fetchval(query, *values)
                logger.info(f"✅ Création réussie dans {table}, ID: {result}")
                return result
        except Exception as e:
            logger.error(f"❌ Erreur lors de la création dans {table}: {e}")
            raise
    
    async def read_one(self, table: str, conditions: Dict[str, Any] = None, 
                      columns: List[str] = None) -> Optional[Dict[str, Any]]:
        
        
        
        
            
            
            
        
        
            
        
        select_cols = ', '.join(columns) if columns else '*'
        
        if conditions:
            where_clause = ' AND '.join([f"{k} = ${i+1}" for i, k in enumerate(conditions.keys())])
            values = list(conditions.values())
            query = f"SELECT {select_cols} FROM {table} WHERE {where_clause} LIMIT 1"
        else:
            query = f"SELECT {select_cols} FROM {table} LIMIT 1"
            values = []
        
        try:
            async with self.get_connection() as conn:
                if values:
                    row = await conn.fetchrow(query, *values)
                else:
                    row = await conn.fetchrow(query)
                
                if row:
                    return dict(row)
                return None
        except Exception as e:
            logger.error(f"❌ Erreur lors de la lecture dans {table}: {e}")
            raise
    
    async def read_all(self, table: str, conditions: Dict[str, Any] = None,
                      columns: List[str] = None, order_by: str = None,
                      limit: int = None, offset: int = None) -> List[Dict[str, Any]]:
        
        
        
        
            
            
            
            
            
            
        
        
            
        
        select_cols = ', '.join(columns) if columns else '*'
        
        query_parts = [f"SELECT {select_cols} FROM {table}"]
        values = []
        
        if conditions:
            where_clause = ' AND '.join([f"{k} = ${i+1}" for i, k in enumerate(conditions.keys())])
            query_parts.append(f"WHERE {where_clause}")
            values.extend(list(conditions.values()))
        
        if order_by:
            query_parts.append(f"ORDER BY {order_by}")
        
        if limit is not None:
            query_parts.append(f"LIMIT {limit}")
        
        if offset is not None:
            query_parts.append(f"OFFSET {offset}")
        
        query = ' '.join(query_parts)
        
        try:
            async with self.get_connection() as conn:
                rows = await conn.fetch(query, *values) if values else await conn.fetch(query)
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Erreur lors de la lecture multiple dans {table}: {e}")
            raise
    
    async def update(self, table: str, record_id: int, data: Dict[str, Any]) -> bool:
        
        
        
        
            
            
            
        
        
            
        
        
        set_clause = ', '.join([f"{k} = ${i+1}" for i, k in enumerate(data.keys())])
        values = list(data.values())
        
        
        
        if table == "utilisateurs":
            query = f"""
                UPDATE {table}
                SET {set_clause}
                WHERE id = ${len(values) + 1}
                RETURNING id
            """
        else:
            query = f"""
                UPDATE {table}
                SET {set_clause}, date_maj = CURRENT_TIMESTAMP
                WHERE id = ${len(values) + 1}
                RETURNING id
            """
        values.append(record_id)
        
        try:
            async with self.get_connection() as conn:
                result = await conn.fetchval(query, *values)
                if result:
                    logger.info(f"✅ Mise à jour réussie dans {table}, ID: {result}")
                    return True
                return False
        except Exception as e:
            logger.error(f"❌ Erreur lors de la mise à jour dans {table}: {e}")
            raise
    
    async def delete(self, table: str, record_id: int) -> bool:
        
        
        
        
            
            
        
        
            
        
        query = f"DELETE FROM {table} WHERE id = $1 RETURNING id"
        
        try:
            async with self.get_connection() as conn:
                result = await conn.fetchval(query, record_id)
                if result:
                    logger.info(f"✅ Suppression réussie dans {table}, ID: {result}")
                    return True
                return False
        except Exception as e:
            logger.error(f"❌ Erreur lors de la suppression dans {table}: {e}")
            raise
    
    async def execute_query(self, query: str, *args) -> List[Dict[str, Any]]:
        
        
        
        
            
            
        
        
            
        
        try:
            async with self.get_connection() as conn:
                rows = await conn.fetch(query, *args)
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'exécution de la requête: {e}")
            raise
    
    async def execute_scalar(self, query: str, *args) -> Any:
        
        
        
        
            
            
        
        
            
        
        try:
            async with self.get_connection() as conn:
                return await conn.fetchval(query, *args)
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'exécution scalaire: {e}")
            raise

    
    
    
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        
        return await self.read_one("utilisateurs", {"email": email})
    
    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        
        return await self.read_one("utilisateurs", {"id": user_id})
    
    async def create_user(self, email: str, password_hash: str, nom: str = None, 
                         prenom: str = None, role_id: int = 2) -> int:
        
        data = {
            "email": email,
            "mot_de_passe_hash": password_hash,
            "nom": nom,
            "prenom": prenom,
            "role_id": role_id,
            "date_inscription": datetime.now(),
            "est_actif": True
        }
        return await self.create("utilisateurs", data)
    
    async def update_user_last_login(self, user_id: int):
        
        query = """
            UPDATE utilisateurs 
            SET derniere_connexion = CURRENT_TIMESTAMP 
            WHERE id = $1
        """
        await self.execute_query(query, user_id)
    
    async def get_users_with_stats(self, limit: int = 100, skip: int = 0) -> List[Dict]:
        
        try:
            query = """
            SELECT 
                u.id,
                u.email,
                u.nom,
                u.prenom,
                u.role_id,
                r.nom_role as role_name,
                u.est_actif,
                u.date_inscription,
                u.derniere_connexion,
                COUNT(DISTINCT ra.id) as total_results,
                COALESCE(AVG(ra.score_quiz), 0) as avg_score
            FROM utilisateurs u
            LEFT JOIN roles r ON u.role_id = r.id
            LEFT JOIN resultats_apprentissage ra ON u.id = ra.utilisateur_id
            GROUP BY u.id, u.email, u.nom, u.prenom, u.role_id, r.nom_role, u.est_actif, u.date_inscription, u.derniere_connexion
            ORDER BY u.id
            LIMIT $1 OFFSET $2
            """
            rows = await self.fetch(query, limit, skip)
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Erreur dans get_users_with_stats: {e}")
            raise
    
    
    
    async def get_all_courses(self, active_only: bool = True, limit: int = 100) -> List[Dict[str, Any]]:
        
        conditions = {"est_actif": True} if active_only else None
        return await self.read_all("cours_html", conditions, limit=limit, order_by="ordre_affichage, titre")
    
    async def get_course_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        
        return await self.read_one("cours_html", {"slug": slug})
    
    async def search_courses(self, search_term: str, limit: int = 20) -> List[Dict[str, Any]]:
        
        query = """
            SELECT id, titre, slug, description, difficulte, duree_estimee
            FROM cours_html
            WHERE est_actif = true 
            AND (titre ILIKE $1 OR description ILIKE $1 OR tags::text ILIKE $1)
            ORDER BY titre
            LIMIT $2
        """
        return await self.execute_query(query, f"%{search_term}%", limit)
    
    async def get_course_stats(self, course_id: int) -> Dict[str, Any]:
        
        query = """
            SELECT 
                c.*,
                COUNT(DISTINCT ra.utilisateur_id) as nb_utilisateurs,
                AVG(ra.score_quiz) as score_moyen,
                COUNT(DISTINCT q.id) as nb_questions
            FROM cours_html c
            LEFT JOIN resultats_apprentissage ra ON c.id = ra.cours_id
            LEFT JOIN questions_quiz q ON c.id = q.cours_id
            WHERE c.id = $1
            GROUP BY c.id
        """
        results = await self.execute_query(query, course_id)
        return results[0] if results else {}
    
   
    
    async def get_questions_by_course(self, course_id: int, mode: str = None) -> List[Dict[str, Any]]:
        
        try:
            async with self.get_connection() as conn:
                if mode:
                    
                    query = """
                        SELECT * FROM questions_quiz 
                        WHERE cours_id = $1 
                        AND (mode_specifique = $2 OR mode_specifique IS NULL)
                        ORDER BY id
                    """
                    rows = await conn.fetch(query, course_id, mode)
                else:
                    
                    query = """
                        SELECT * FROM questions_quiz 
                        WHERE cours_id = $1 
                        ORDER BY id
                    """
                    rows = await conn.fetch(query, course_id)
                
                print(f"🔍 Requête SQL exécutée, {len(rows)} questions trouvées")
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"❌ Erreur dans get_questions_by_course: {e}")
            raise
    
    async def get_random_questions(self, course_id: int, limit: int = 10, 
                                 difficulty: str = None) -> List[Dict[str, Any]]:
        
        where_clause = "WHERE cours_id = $1"
        params = [course_id]
        
        if difficulty:
            where_clause += " AND difficulte = $2"
            params.append(difficulty)
        
        query = f"""
            SELECT * FROM questions_quiz
            {where_clause}
            ORDER BY RANDOM()
            LIMIT $3
        """
        params.append(limit)
        
        return await self.execute_query(query, *params)
    
    
    
    async def save_learning_result(self, user_id: int, course_id: int, mode: str,
                                 score: float, time_spent: int, completion_rate: float = 100,
                                 is_success: bool = True, feedback: str = None) -> int:
        
        data = {
            "utilisateur_id": user_id,
            "cours_id": course_id,
            "mode": mode,
            "score_quiz": score,
            "temps_passe": time_spent,
            "taux_completion": completion_rate,
            "est_reussi": is_success,
            "date_debut": datetime.now(),
            "date_completion": datetime.now(),
            "feedback": feedback
        }
        
        
        query = """
            SELECT COALESCE(MAX(nb_tentatives), 0) + 1
            FROM resultats_apprentissage
            WHERE utilisateur_id = $1 AND cours_id = $2 AND mode = $3
        """
        attempts = await self.execute_scalar(query, user_id, course_id, mode)
        data["nb_tentatives"] = attempts
        
        return await self.create("resultats_apprentissage", data)
    
    async def get_user_learning_stats(self, user_id: int) -> Dict[str, Any]:
        
        query = """
            SELECT 
                COUNT(DISTINCT cours_id) as total_courses,
                COUNT(*) as total_attempts,
                AVG(score_quiz) as avg_score,
                SUM(temps_passe) as total_time,
                mode,
                COUNT(CASE WHEN est_reussi THEN 1 END) as successful_attempts
            FROM resultats_apprentissage
            WHERE utilisateur_id = $1
            GROUP BY mode
        """
        return await self.execute_query(query, user_id)
    
    async def get_user_progress(self, user_id: int) -> Dict[str, Any]:
        
        try:
            async with self.get_connection() as conn:
                
                cours_complets = await conn.fetchval("""
                    SELECT COUNT(DISTINCT cours_id) 
                    FROM resultats_apprentissage 
                    WHERE utilisateur_id = $1 AND est_reussi = true
                """, user_id)
                
                
                score_moyen = await conn.fetchval("""
                    SELECT COALESCE(AVG(score_quiz), 0)
                    FROM resultats_apprentissage 
                    WHERE utilisateur_id = $1
                """, user_id)
                
                
                temps_total = await conn.fetchval("""
                    SELECT COALESCE(SUM(temps_passe), 0)
                    FROM resultats_apprentissage 
                    WHERE utilisateur_id = $1
                """, user_id)
                
                
                total_cours = await conn.fetchval("""
                    SELECT COUNT(*) FROM cours_html WHERE est_actif = true
                """)
                progression_niveau = (cours_complets / total_cours * 100) if total_cours and total_cours > 0 else 0
                
               
                stats_par_mode = {
                    "texte": {"nb_cours": 0, "score_moyen": 0},
                    "audio": {"nb_cours": 0, "score_moyen": 0},
                    "video": {"nb_cours": 0, "score_moyen": 0}
                }
                
                for mode in ['texte', 'audio', 'video']:
                    stats = await conn.fetchrow("""
                        SELECT 
                            COUNT(*) as nb_cours,
                            COALESCE(AVG(score_quiz), 0) as score_moyen
                        FROM resultats_apprentissage 
                        WHERE utilisateur_id = $1 AND mode = $2
                    """, user_id, mode)
                    
                    if stats:
                        stats_par_mode[mode] = {
                            'nb_cours': stats['nb_cours'] or 0,
                            'score_moyen': float(stats['score_moyen']) if stats['score_moyen'] else 0
                        }
                
                
                result = {
                    "cours_complets": cours_complets or 0,
                    "score_moyen": float(score_moyen) if score_moyen else 0,
                    "temps_total": temps_total or 0,
                    "progression_niveau": float(progression_niveau) if progression_niveau else 0,
                    "stats_par_mode": stats_par_mode
                }
                
                logger.info(f"📊 Progression pour utilisateur {user_id}: {result}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Erreur dans get_user_progress: {e}")
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
    
    

    

    async def save_user_mistake(self, conn, utilisateur_id: int, cours_id: int, question_id: int, question_texte: str, reponse_utilisateur: str, reponse_correcte: str, mode_apprentissage: str, score_obtenu: int = 0, points_possibles: int = 10) -> int:
        
        try:
            
            existing = await conn.fetchrow("""
                SELECT id, nb_fois_erreur 
                FROM erreurs_utilisateurs 
                WHERE utilisateur_id = $1 
                  AND question_id = $2 
                  AND mode_apprentissage = $3 
                  AND est_revu = FALSE
            """, utilisateur_id, question_id, mode_apprentissage)
            
            if existing:
                
                await conn.execute("""
                    UPDATE erreurs_utilisateurs 
                    SET nb_fois_erreur = nb_fois_erreur + 1,
                        derniere_erreur = CURRENT_TIMESTAMP,
                        reponse_utilisateur = $1
                    WHERE id = $2
                """, reponse_utilisateur, existing['id'])
                return existing['id']
            else:
                
                row = await conn.fetchrow("""
                    INSERT INTO erreurs_utilisateurs (
                        utilisateur_id, cours_id, question_id, question_texte,
                        reponse_utilisateur, reponse_correcte, mode_apprentissage,
                        score_obtenu, points_possibles
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    RETURNING id
                """, utilisateur_id, cours_id, question_id, question_texte,
                    reponse_utilisateur, reponse_correcte, mode_apprentissage,
                    score_obtenu, points_possibles)
                return row['id']
        except Exception as e:
            logger.error(f"Erreur save_user_mistake: {e}")
            return None 


    async def get_user_mistakes(self, conn, utilisateur_id: int, cours_id: Optional[int] = None, mode: Optional[str] = None, limit: int = 30) -> List[dict]:
        
        try:
            query = """
                SELECT 
                    eu.id,
                    eu.question_texte,
                    eu.reponse_utilisateur,
                    eu.reponse_correcte,
                    eu.mode_apprentissage,
                    eu.nb_fois_erreur,
                    eu.est_revu,
                    eu.date_erreur,
                    eu.derniere_erreur,
                    c.titre as cours_titre
                FROM erreurs_utilisateurs eu
                JOIN cours_html c ON eu.cours_id = c.id
                WHERE eu.utilisateur_id = $1
                  AND eu.est_revu = FALSE
            """
            params = [utilisateur_id]
            param_index = 2
            
            if cours_id:
                query += f" AND eu.cours_id = ${param_index}"
                params.append(cours_id)
                param_index += 1
            
            if mode:
                query += f" AND eu.mode_apprentissage = ${param_index}"
                params.append(mode)
                param_index += 1
            
            query += f" ORDER BY eu.nb_fois_erreur DESC, eu.derniere_erreur DESC LIMIT ${param_index}"
            params.append(limit)
            
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Erreur get_user_mistakes: {e}")
            return []


    async def get_user_mistakes_stats(self, conn, utilisateur_id: int) -> dict:
        
        try:
            row = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_erreurs,
                    COUNT(*) FILTER (WHERE est_revu = FALSE) as erreurs_non_revues,
                    COUNT(*) FILTER (WHERE nb_fois_erreur >= 3) as erreurs_critiques,
                    (SELECT c.titre 
                     FROM erreurs_utilisateurs eu2 
                     JOIN cours_html c ON eu2.cours_id = c.id
                     WHERE eu2.utilisateur_id = $1
                     GROUP BY c.titre
                     ORDER BY COUNT(*) DESC 
                     LIMIT 1) as cours_plus_erreurs,
                    (SELECT mode_apprentissage
                     FROM erreurs_utilisateurs
                     WHERE utilisateur_id = $1
                     GROUP BY mode_apprentissage
                     ORDER BY COUNT(*) DESC 
                     LIMIT 1) as mode_plus_erreurs
                FROM erreurs_utilisateurs
                WHERE utilisateur_id = $1
            """, utilisateur_id)
            
            if row:
                return {
                    'total_erreurs': row['total_erreurs'] or 0,
                    'erreurs_non_revues': row['erreurs_non_revues'] or 0,
                    'erreurs_critiques': row['erreurs_critiques'] or 0,
                    'cours_plus_erreurs': row['cours_plus_erreurs'],
                    'mode_plus_erreurs': row['mode_plus_erreurs']
                }
            return {
                'total_erreurs': 0,
                'erreurs_non_revues': 0,
                'erreurs_critiques': 0,
                'cours_plus_erreurs': None,
                'mode_plus_erreurs': None
            }
        except Exception as e:
            logger.error(f"Erreur get_user_mistakes_stats: {e}")
            return {
                'total_erreurs': 0,
                'erreurs_non_revues': 0,
                'erreurs_critiques': 0,
                'cours_plus_erreurs': None,
                'mode_plus_erreurs': None
            }


    async def mark_mistake_as_revised(conn, erreur_id: int, utilisateur_id: int) -> bool:
        
        try:
            result = await conn.execute("""
                UPDATE erreurs_utilisateurs
                SET est_revu = TRUE, date_revision = CURRENT_TIMESTAMP
                WHERE id = $1 AND utilisateur_id = $2 AND est_revu = FALSE
            """, erreur_id, utilisateur_id)
            
            return result == "UPDATE 1"
        except Exception as e:
            logger.error(f"Erreur mark_mistake_as_revised: {e}")
            return False
    
    
    
    async def save_voice_search(self, user_id: int, query_text: str, 
                              confidence: float, results_found: int,
                              response_time: int, success: bool = True) -> int:
        
        data = {
            "utilisateur_id": user_id,
            "requete_transcrite": query_text,
            "confiance_transcription": confidence,
            "resultats_trouves": results_found,
            "temps_reponse": response_time,
            "succes": success,
            "date_recherche": datetime.now()
        }
        return await self.create("recherches_vocales", data)
    
    
    
    async def get_admin_logs(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        
        query = """
            SELECT la.*, u.email as admin_email
            FROM logs_admin la
            LEFT JOIN utilisateurs u ON la.admin_id = u.id
            ORDER BY la.timestamp DESC
            LIMIT $1 OFFSET $2
        """
        return await self.execute_query(query, limit, offset)
    
    async def get_interaction_logs(self, user_id: int = None, limit: int = 50) -> List[Dict[str, Any]]:
        
        if user_id:
            query = """
                SELECT * FROM logs_interaction
                WHERE utilisateur_id = $1
                ORDER BY timestamp DESC
                LIMIT $2
            """
            return await self.execute_query(query, user_id, limit)
        else:
            query = """
                SELECT li.*, u.email
                FROM logs_interaction li
                LEFT JOIN utilisateurs u ON li.utilisateur_id = u.id
                ORDER BY li.timestamp DESC
                LIMIT $1
            """
            return await self.execute_query(query, limit)
    
    async def get_system_stats(self) -> Dict[str, Any]:
        
        queries = {
            "total_users": "SELECT COUNT(*) FROM utilisateurs WHERE est_actif = true",
            "total_courses": "SELECT COUNT(*) FROM cours_html WHERE est_actif = true",
            "total_questions": "SELECT COUNT(*) FROM questions_quiz",
            "total_results": "SELECT COUNT(*) FROM resultats_apprentissage",
            "avg_score": "SELECT AVG(score_quiz) FROM resultats_apprentissage WHERE score_quiz IS NOT NULL",
            "recent_users": """
                SELECT COUNT(*) FROM utilisateurs 
                WHERE date_inscription > CURRENT_DATE - INTERVAL '7 days'
            """,
            "active_today": """
                SELECT COUNT(DISTINCT utilisateur_id) FROM logs_interaction 
                WHERE timestamp > CURRENT_DATE
            """
        }
        
        stats = {}
        for key, query in queries.items():
            try:
                stats[key] = await self.execute_scalar(query)
            except:
                stats[key] = 0
        
        return stats
    
    
    
    async def calculate_learner_type(self, user_id: int) -> str:
        
        query = """
            SELECT calculer_type_apprenant($1)
        """
        return await self.execute_scalar(query, user_id)
    
    async def get_course_recommendations(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        
        query = """
            SELECT * FROM vue_recommandations_cours
            WHERE difficulte IN ('débutant', 'intermédiaire')
            ORDER BY score_moyen DESC NULLS LAST, nb_etudiants DESC
            LIMIT $1
        """
        return await self.execute_query(query, limit)
    
    async def get_user_statistics_view(self, user_id: int = None) -> List[Dict[str, Any]]:
        
        if user_id:
            query = "SELECT * FROM vue_statistiques_utilisateurs WHERE id = $1"
            return await self.execute_query(query, user_id)
        else:
            query = "SELECT * FROM vue_statistiques_utilisateurs ORDER BY nb_cours_complets DESC"
            return await self.execute_query(query)
    
    
    
    async def create_course_with_questions(self, course_data: Dict[str, Any], 
                                         questions: List[Dict[str, Any]]) -> int:
        
        async with self.get_transaction() as conn:
            
            course_cols = ', '.join(course_data.keys())
            course_placeholders = ', '.join([f'${i+1}' for i in range(len(course_data))])
            course_values = list(course_data.values())
            
            course_query = f"""
                INSERT INTO cours_html ({course_cols})
                VALUES ({course_placeholders})
                RETURNING id
            """
            
            course_id = await conn.fetchval(course_query, *course_values)
            
            
            for question in questions:
                question['cours_id'] = course_id
                question_cols = ', '.join(question.keys())
                question_placeholders = ', '.join([f'${i+1}' for i in range(len(question))])
                question_values = list(question.values())
                
                question_query = f"""
                    INSERT INTO questions_quiz ({question_cols})
                    VALUES ({question_placeholders})
                """
                
                await conn.execute(question_query, *question_values)
            
            return course_id
    
    async def batch_update_users(self, user_ids: List[int], updates: Dict[str, Any]) -> int:
        
        set_clause = ', '.join([f"{k} = ${i+1}" for i, k in enumerate(updates.keys())])
        
        query = f"""
            UPDATE utilisateurs 
            SET {set_clause}, date_maj = CURRENT_TIMESTAMP
            WHERE id = ANY(${len(updates) + 1})
            RETURNING COUNT(*)
        """
        
        values = list(updates.values())
        values.append(user_ids)
        
        count = await self.execute_scalar(query, *values)
        logger.info(f"✅ {count} utilisateur(s) mis à jour")
        return count

    
    
    async def export_table_to_json(self, table: str, conditions: Dict[str, Any] = None) -> str:
        
        rows = await self.read_all(table, conditions)
        return json.dumps(rows, indent=2, default=str, ensure_ascii=False)
    
    async def export_user_data(self, user_id: int) -> Dict[str, Any]:
        
        queries = {
            "user_info": "SELECT * FROM utilisateurs WHERE id = $1",
            "learning_results": "SELECT * FROM resultats_apprentissage WHERE utilisateur_id = $1",
            "quiz_responses": """
                SELECT rq.*, q.question 
                FROM reponses_quiz rq
                JOIN questions_quiz q ON rq.question_id = q.id
                WHERE rq.resultat_id IN (
                    SELECT id FROM resultats_apprentissage WHERE utilisateur_id = $1
                )
            """,
            "voice_searches": "SELECT * FROM recherches_vocales WHERE utilisateur_id = $1",
            "interaction_logs": "SELECT * FROM logs_interaction WHERE utilisateur_id = $1"
        }
        
        user_data = {}
        for key, query in queries.items():
            user_data[key] = await self.execute_query(query, user_id)
        
        return user_data


db = Database()


async def init_database():
    
    await db.connect()


async def close_database():
    
    await db.disconnect()