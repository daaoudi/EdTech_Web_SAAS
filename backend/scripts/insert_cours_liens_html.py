import psycopg2
import json
from typing import List, Dict, Any, Optional

class QuestionManager:
    """Gestionnaire de questions avec équilibrage par mode"""
    
    def __init__(self):
        self.conn = None
        self.cur = None
        
    def get_connection(self):
        try:
            self.conn = psycopg2.connect(
                host="localhost",
                database="plateforme_elearning",
                user="postgres",
                password="root",
                port="5432"
            )
            self.cur = self.conn.cursor()
            return True
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    def close_connection(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
    
    def get_admin_user(self):
        try:
            self.cur.execute("""
                SELECT u.id, u.email, u.nom, u.prenom
                FROM utilisateurs u
                JOIN roles r ON u.role_id = r.id
                WHERE r.nom_role = 'admin'
                AND u.est_actif = true
                LIMIT 1
            """)
            
            admin = self.cur.fetchone()
            
            if admin:
                admin_id, email, nom, prenom = admin
                print(f"✅ Admin trouvé: {nom} {prenom} ({email}) - ID: {admin_id}")
                return admin_id
            
            self.cur.execute("""
                SELECT id, email, nom, prenom 
                FROM utilisateurs 
                WHERE est_actif = true
                ORDER BY id
                LIMIT 1
            """)
            
            user = self.cur.fetchone()
            
            if user:
                user_id, email, nom, prenom = user
                print(f"⚠️ Utilisation de: {nom} {prenom} ({email}) - ID: {user_id}")
                return user_id
            
            print("❌ Aucun utilisateur trouvé")
            return None
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return None
    
    def get_existing_questions_count(self, cours_id: int, mode: str) -> int:
        """Récupère le nombre de questions existantes pour un mode donné"""
        try:
            self.cur.execute("""
                SELECT COUNT(*) FROM questions_quiz 
                WHERE cours_id = %s AND mode_specifique = %s
            """, (cours_id, mode))
            return self.cur.fetchone()[0]
        except Exception as e:
            print(f"❌ Erreur comptage: {e}")
            return 0
    
    def insert_question(self, cours_id: int, question_data: Dict[str, Any], admin_id: int) -> Optional[int]:
        """Insère une question avec vérification des doublons"""
        try:
            # Vérifier si la question existe déjà
            self.cur.execute("""
                SELECT id FROM questions_quiz 
                WHERE cours_id = %s AND question = %s AND mode_specifique = %s
            """, (
                cours_id,
                question_data["question"],
                question_data.get("mode_specifique", "texte")
            ))
            
            existing = self.cur.fetchone()
            
            if existing:
                print(f"  ⚠️ Question déjà existante: {question_data['question'][:40]}...")
                return existing[0]
            
            # Préparer les données
            options_json = json.dumps(question_data.get("options", {}), ensure_ascii=False)
            
            # Insérer la question
            self.cur.execute("""
                INSERT INTO questions_quiz 
                (cours_id, question, type_question, points, difficulte, 
                 options, reponse_correcte, explication, mode_specifique, 
                 created_by, date_creation)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                RETURNING id
            """, (
                cours_id,
                question_data["question"],
                question_data.get("type_question", "choix_multiple"),
                question_data.get("points", 10),
                question_data.get("difficulte", "moyen"),
                options_json,
                question_data.get("reponse_correcte", "A"),
                question_data.get("explication", ""),
                question_data.get("mode_specifique", "texte"),
                admin_id
            ))
            
            question_id = self.cur.fetchone()[0]
            return question_id
            
        except Exception as e:
            print(f"  ❌ Erreur insertion: {e}")
            return None

# ============================================================================
# DONNÉES DES QUESTIONS ÉQUILIBRÉES PAR MODE
# ============================================================================

def get_questions_texte() -> List[Dict[str, Any]]:
    """Questions en mode texte (5 questions)"""
    return [
        {
            "question": "Quelle est la syntaxe correcte pour créer un lien vers la page 'apropos.html' située dans le même dossier ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "<link href='apropos.html'>À propos</link>",
                "B": "<a src='apropos.html'>À propos</a>",
                "C": "<a href='apropos.html'>À propos</a>",
                "D": "<hyperlink='apropos.html'>À propos</hyperlink>"
            },
            "reponse_correcte": "C",
            "explication": "La balise <a> (anchor) avec l'attribut href est utilisée pour créer des liens hypertextes en HTML.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quelle est la différence entre un lien relatif et un lien absolu en HTML ?",
            "type_question": "choix_multiple",
            "points": 20,
            "difficulte": "avance",
            "options": {
                "A": "Les liens relatifs sont plus rapides à charger",
                "B": "Les liens relatifs sont basés sur l'emplacement actuel, les absolus sur la racine",
                "C": "Les liens absolus ne fonctionnent qu'en ligne",
                "D": "Il n'y a pas de différence fonctionnelle"
            },
            "reponse_correcte": "B",
            "explication": "Un lien relatif est basé sur l'emplacement actuel, un lien absolu part toujours de la racine du site.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quelle est la bonne pratique pour nommer la page d'accueil d'un site web ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "home.html",
                "B": "accueil.html",
                "C": "index.html",
                "D": "main.html"
            },
            "reponse_correcte": "C",
            "explication": "La convention est d'utiliser 'index.html' car les serveurs web servent ce fichier par défaut.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quel attribut est utilisé pour spécifier l'URL d'un lien en HTML ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "src",
                "B": "url", 
                "C": "href",
                "D": "link"
            },
            "reponse_correcte": "C",
            "explication": "L'attribut href (Hypertext Reference) spécifie l'URL de destination du lien.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quel est l'avantage d'utiliser des chemins relatifs pour les liens internes ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "Ils sont plus rapides à charger",
                "B": "Ils fonctionnent quel que soit le domaine du site",
                "C": "Ils sont plus sécurisés",
                "D": "Ils sont plus courts à écrire"
            },
            "reponse_correcte": "B",
            "explication": "Les chemins relatifs permettent de déplacer un site entier sans modifier tous les liens, car ils sont basés sur la structure des dossiers.",
            "mode_specifique": "texte"
        }
    ]

def get_questions_audio() -> List[Dict[str, Any]]:
    """Questions en mode audio (5 questions)"""
    return [
        {
            "question": "Quelle est la balise HTML utilisée pour créer des liens hypertextes ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "La balise <link>",
                "B": "La balise <a>",
                "C": "La balise <href>",
                "D": "La balise <url>"
            },
            "reponse_correcte": "B",
            "explication": "La balise <a> (anchor) est utilisée pour créer des liens hypertextes en HTML.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quel attribut est utilisé pour spécifier la destination d'un lien en HTML ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "src",
                "B": "url", 
                "C": "href",
                "D": "link"
            },
            "reponse_correcte": "C",
            "explication": "L'attribut href (Hypertext Reference) spécifie l'URL de destination du lien.",
            "mode_specifique": "audio"
        },
        {
            "question": "Comment ouvrir un lien dans un nouvel onglet en HTML ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "moyen",
            "options": {
                "A": "target='_self'",
                "B": "target='_blank'",
                "C": "target='_new'",
                "D": "target='_top'"
            },
            "reponse_correcte": "B",
            "explication": "L'attribut target='_blank' ouvre le lien dans un nouvel onglet.",
            "mode_specifique": "audio"
        },
        {
            "question": "Que signifie le symbole '..' dans un chemin de fichier en HTML ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "moyen",
            "options": {
                "A": "Dossier courant",
                "B": "Dossier parent",
                "C": "Racine du site",
                "D": "Dossier utilisateur"
            },
            "reponse_correcte": "B",
            "explication": "Le symbole '..' permet de remonter d'un niveau dans l'arborescence des dossiers.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle est la différence entre un chemin relatif et un chemin absolu en HTML ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "Les chemins relatifs sont plus rapides",
                "B": "Les chemins relatifs sont basés sur l'emplacement actuel",
                "C": "Les chemins absolus ne fonctionnent qu'en ligne",
                "D": "Il n'y a pas de différence"
            },
            "reponse_correcte": "B",
            "explication": "Un chemin relatif est basé sur l'emplacement du fichier actuel.",
            "mode_specifique": "audio"
        }
    ]

def get_questions_video() -> List[Dict[str, Any]]:
    """Questions en mode vidéo (5 questions)"""
    return [
        {
            "question": "Pourquoi la page d'accueil d'un site web est-elle généralement nommée 'index.html' ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "C'est une convention imposée par le W3C",
                "B": "Les serveurs web sont configurés pour servir ce fichier par défaut",
                "C": "C'est plus facile à retenir pour les débutants",
                "D": "Cela améliore le référencement SEO"
            },
            "reponse_correcte": "B",
            "explication": "Les serveurs web sont configurés pour servir automatiquement 'index.html' lorsqu'on accède à un répertoire.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment créer un lien qui ouvre une page externe dans un nouvel onglet en HTML ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "<a href='https://example.com' target='_new'>Exemple</a>",
                "B": "<a href='https://example.com' newtab>Exemple</a>",
                "C": "<a href='https://example.com' target='_blank'>Exemple</a>",
                "D": "<a href='https://example.com' open='new'>Exemple</a>"
            },
            "reponse_correcte": "C",
            "explication": "L'attribut target='_blank' indique au navigateur d'ouvrir le lien dans un nouvel onglet.",
            "mode_specifique": "video"
        },
        {
            "question": "Vous avez la structure suivante : site/index.html et site/produits/liste.html. Quel chemin utiliser depuis liste.html pour revenir à index.html ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "<a href='../index.html'>Accueil</a>",
                "B": "<a href='./index.html'>Accueil</a>",
                "C": "<a href='/index.html'>Accueil</a>",
                "D": "<a href='index.html'>Accueil</a>"
            },
            "reponse_correcte": "A",
            "explication": "Le chemin '../' remonte d'un niveau dans l'arborescence des dossiers.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment créer une ancre interne qui permet de sauter à une section avec l'id 'contact' dans la même page HTML ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "<a link='#contact'>Contact</a>",
                "B": "<a href='#contact'>Contact</a>",
                "C": "<a anchor='contact'>Contact</a>",
                "D": "<a goto='contact'>Contact</a>"
            },
            "reponse_correcte": "B",
            "explication": "Les ancres internes utilisent le symbole # suivi de l'id de l'élément cible.",
            "mode_specifique": "video"
        },
        {
            "question": "Quel attribut de sécurité recommande-t-on d'ajouter avec target='_blank' pour les liens externes ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "avance",
            "options": {
                "A": "rel='noopener noreferrer'",
                "B": "rel='safe'",
                "C": "rel='secure'",
                "D": "rel='external'"
            },
            "reponse_correcte": "A",
            "explication": "L'attribut rel='noopener noreferrer' est une bonne pratique de sécurité pour les liens externes.",
            "mode_specifique": "video"
        }
    ]

# ============================================================================
# FONCTIONS DE CRÉATION DES QUESTIONS ÉQUILIBRÉES
# ============================================================================

def creer_questions_equilibrees(cours_id: int, nombre_par_mode: int = 5):
    """
    Crée des questions équilibrées pour chaque mode
    
    Args:
        cours_id: ID du cours
        nombre_par_mode: Nombre de questions par mode (défaut: 5)
    """
    try:
        manager = QuestionManager()
        
        if not manager.get_connection():
            print("❌ Impossible de se connecter à la base de données")
            return False
        
        admin_id = manager.get_admin_user()
        if not admin_id:
            manager.close_connection()
            return False
        
        print(f"\n📚 Création de questions équilibrées pour le cours ID: {cours_id}")
        print("=" * 80)
        
        # Récupérer les questions par mode
        questions_par_mode = {
            'texte': get_questions_texte(),
            'audio': get_questions_audio(),
            'video': get_questions_video()
        }
        
        total_inserees = 0
        
        for mode, questions in questions_par_mode.items():
            print(f"\n🎯 Insertion des questions {mode.upper()}...")
            print("-" * 60)
            
            # Vérifier combien de questions existent déjà
            existantes = manager.get_existing_questions_count(cours_id, mode)
            
            if existantes >= nombre_par_mode:
                print(f"  ✅ {existantes} questions {mode} existent déjà (suffisant)")
                continue
            
            # Sélectionner les questions à insérer
            questions_a_inserer = questions[:nombre_par_mode]
            
            # Insérer les questions
            count = 0
            for q in questions_a_inserer:
                result = manager.insert_question(cours_id, q, admin_id)
                if result:
                    count += 1
                    print(f"  ✅ Question {mode} ajoutée: {q['question'][:40]}...")
            
            # Commit après chaque mode
            manager.conn.commit()
            total_inserees += count
            print(f"  📊 {count} nouvelles questions {mode} insérées")
        
        # Afficher les statistiques finales
        print("\n" + "=" * 80)
        print("📊 STATISTIQUES FINALES PAR MODE")
        print("=" * 80)
        
        for mode in ['texte', 'audio', 'video']:
            count = manager.get_existing_questions_count(cours_id, mode)
            print(f"  • {mode.upper()}: {count} questions")
        
        print(f"\n✅ TOTAL: {total_inserees} nouvelles questions insérées")
        
        manager.close_connection()
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def verifier_equilibrage_questions(cours_id: int):
    """Vérifie l'équilibrage des questions par mode"""
    try:
        conn = get_connection()
        if not conn:
            return False
        
        cur = conn.cursor()
        
        print(f"\n🔍 VÉRIFICATION DE L'ÉQUILIBRAGE DU COURS {cours_id}")
        print("=" * 80)
        
        # Compter les questions par mode
        cur.execute("""
            SELECT mode_specifique, COUNT(*) 
            FROM questions_quiz 
            WHERE cours_id = %s
            GROUP BY mode_specifique
            ORDER BY mode_specifique
        """, (cours_id,))
        
        results = cur.fetchall()
        
        print("\n📊 RÉPARTITION DES QUESTIONS PAR MODE:")
        print("-" * 40)
        
        total = 0
        for mode, count in results:
            mode_label = mode if mode else 'non_spécifié'
            print(f"  • {mode_label.upper()}: {count} questions")
            total += count
        
        print(f"\n📝 TOTAL: {total} questions")
        
        # Vérifier l'équilibrage
        if len(results) >= 3:
            counts = [count for _, count in results]
            if max(counts) - min(counts) <= 1:
                print("\n✅ Les questions sont bien équilibrées !")
            else:
                print("\n⚠️ Les questions ne sont pas parfaitement équilibrées.")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

# ============================================================================
# FONCTIONS EXISTANTES
# ============================================================================

def get_connection():
    try:
        return psycopg2.connect(
            host="localhost",
            database="plateforme_elearning",
            user="postgres",
            password="root",
            port="5432"
        )
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        return None

def get_admin_user():
    try:
        conn = get_connection()
        if not conn:
            return None
        
        cur = conn.cursor()
        
        cur.execute("""
            SELECT u.id, u.email, u.nom, u.prenom, r.nom_role
            FROM utilisateurs u
            JOIN roles r ON u.role_id = r.id
            WHERE r.nom_role = 'admin'
            AND u.est_actif = true
            LIMIT 1
        """)
        
        admin = cur.fetchone()
        
        if admin:
            admin_id, email, nom, prenom, role = admin
            print(f"✅ Admin trouvé: {nom} {prenom} ({email}) - Rôle: {role} - ID: {admin_id}")
            cur.close()
            conn.close()
            return admin_id
        
        cur.execute("""
            SELECT id, email, nom, prenom 
            FROM utilisateurs 
            WHERE est_actif = true
            ORDER BY id
            LIMIT 1
        """)
        
        user = cur.fetchone()
        
        if user:
            user_id, email, nom, prenom = user
            print(f"⚠️ Utilisation de: {nom} {prenom} ({email}) - ID: {user_id}")
            cur.close()
            conn.close()
            return user_id
        
        cur.close()
        conn.close()
        print("❌ Aucun utilisateur trouvé")
        return None
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def creer_cours_liens_html():
    """Création du cours sur les liens hypertextes"""
    try:
        admin_id = get_admin_user()
        if not admin_id:
            print("❌ Impossible de trouver un utilisateur valide")
            return False
        
        print(f"\n👤 Utilisateur qui créera le cours: ID {admin_id}")
        
        conn = get_connection()
        if not conn:
            return False
        
        cur = conn.cursor()
        
        cours_liens = {
            "titre": "Apprendre l'HTML : Les liens hypertextes",
            "slug": "liens-hypertextes-html",
            "description": "Maîtrisez l'art de créer et gérer des liens hypertextes en HTML.",
            "contenu_texte": """
                <h1>Apprendre l'HTML : Les liens hypertextes</h1>
                
                <h2>📋 Introduction</h2>
                <p>Les liens hypertextes sont le fondement du web. Ils permettent de relier des pages entre elles.</p>
                
                <h2>🔗 La balise &lt;a&gt;</h2>
                <p>La balise <code>&lt;a&gt;</code> (anchor) est utilisée pour créer des liens. L'attribut <code>href</code> spécifie la destination.</p>
                
                <h2>📁 Chemins relatifs et absolus</h2>
                <p>Les chemins relatifs sont basés sur l'emplacement actuel, les chemins absolus partent de la racine.</p>
                
                <h2>🌐 Liens externes</h2>
                <p>Utilisez <code>target="_blank"</code> pour ouvrir dans un nouvel onglet.</p>
                
                <h2>🎯 Ancres internes</h2>
                <p>Les ancres internes utilisent <code>#id</code> pour naviguer dans une page.</p>
                """,
            "url_video": "https://www.youtube.com/embed/LkZ-KqxgVQ4",
            "difficulte": "debutant",
            "duree_estimee": 25,
            "ordre_affichage": 6,
            "chapitre_id": None,
            "tags": ["html", "liens", "hypertextes", "debutant"]
        }
        
        print(f"\n📚 Création du cours sur les liens hypertextes...")
        
        cur.execute("SELECT id FROM cours_html WHERE slug = %s", (cours_liens["slug"],))
        result = cur.fetchone()
        
        if result:
            print(f"⚠️ Cours déjà existant : {cours_liens['titre']}")
            print(f"   ID du cours existant : {result[0]}")
            cur.close()
            conn.close()
            return result[0]
        
        cur.execute("""
            INSERT INTO cours_html 
            (titre, slug, description, contenu_texte, url_video, difficulte, 
             duree_estimee, ordre_affichage, chapitre_id, tags, est_actif, 
             created_by, date_creation, date_maj, last_modified_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, %s)
            RETURNING id
        """, (
            cours_liens["titre"],
            cours_liens["slug"],
            cours_liens["description"],
            cours_liens["contenu_texte"],
            cours_liens["url_video"],
            cours_liens["difficulte"],
            cours_liens["duree_estimee"],
            cours_liens["ordre_affichage"],
            cours_liens["chapitre_id"],
            cours_liens["tags"],
            True,
            admin_id,
            admin_id
        ))
        
        cours_id = cur.fetchone()[0]
        print(f"✅ Cours créé avec succès !")
        print(f"   ID: {cours_id}")
        print(f"   Titre: {cours_liens['titre']}")
        print(f"   Slug: {cours_liens['slug']}")
        
        conn.commit()
        cur.close()
        conn.close()
        
        return cours_id
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du cours: {e}")
        import traceback
        traceback.print_exc()
        return None

def afficher_info_cours():
    try:
        conn = get_connection()
        if not conn:
            return False
        
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM cours_html WHERE est_actif = true")
        total_cours = cur.fetchone()[0]
        
        cur.execute("""
            SELECT difficulte, COUNT(*) 
            FROM cours_html 
            WHERE est_actif = true
            GROUP BY difficulte
            ORDER BY 
                CASE difficulte 
                    WHEN 'debutant' THEN 1
                    WHEN 'intermediaire' THEN 2
                    WHEN 'avance' THEN 3
                    ELSE 4
                END
        """)
        
        stats_difficulte = cur.fetchall()
        
        print("\n" + "=" * 80)
        print("📊 STATISTIQUES DES COURS HTML")
        print("=" * 80)
        
        print(f"\n📚 Nombre total de cours actifs : {total_cours}")
        
        print(f"\n🎯 Répartition par difficulté :")
        for difficulte, count in stats_difficulte:
            print(f"   • {difficulte.capitalize():<12} : {count} cours")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

# ============================================================================
# MENU PRINCIPAL
# ============================================================================

def main():
    """Fonction principale avec menu"""
    print("\n" + "🌟" * 30)
    print("📚 GESTIONNAIRE DE COURS ET QUESTIONS")
    print("🌟" * 30)
    
    print("\n🔍 Test de connexion à la base de données...")
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    afficher_info_cours()
    
    print("\n" + "=" * 80)
    print("🚀 CRÉATION DU COURS AVEC QUESTIONS ÉQUILIBRÉES")
    print("=" * 80)
    
    # Créer le cours
    cours_id = creer_cours_liens_html()
    
    if cours_id:
        print("\n" + "✅" * 30)
        print("COURS CRÉÉ AVEC SUCCÈS !")
        print("✅" * 30)
        
        # Créer les questions équilibrées
        print("\n📝 Création des questions équilibrées (texte, audio, video)...")
        creer_questions_equilibrees(cours_id, 5)
        
        # Vérifier l'équilibrage
        verifier_equilibrage_questions(cours_id)
        
        print("\n" + "🎓" * 30)
        print("INSTRUCTIONS POUR UTILISER LE COURS")
        print("🎓" * 30)
        print(f"""
        ✅ Le cours a été créé avec succès !

        🔗 URL du cours dans l'application :
        • Mode texte   : http://localhost:8501/text_learning?cours=liens-hypertextes-html
        • Mode audio   : http://localhost:8501/audio_learning?cours=liens-hypertextes-html  
        • Mode vidéo   : http://localhost:8501/video_learning?cours=liens-hypertextes-html
        
        🎯 Caractéristiques du cours :
        • ID : {cours_id}
        • Slug : liens-hypertextes-html
        • Titre : Apprendre l'HTML : Les liens hypertextes
        • Difficulté : débutant
        • Durée estimée : 25 minutes
        
        📊 Questions créées :
        • 5 questions en mode TEXTE
        • 5 questions en mode AUDIO
        • 5 questions en mode VIDEO
        """)
    
    else:
        print("\n❌ La création du cours a échoué.")
    
    print("\n" + "🎉" * 30)
    print("SCRIPT TERMINÉ")
    print("🎉" * 30)

if __name__ == "__main__":
    main()