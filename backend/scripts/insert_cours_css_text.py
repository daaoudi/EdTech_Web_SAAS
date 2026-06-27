
import psycopg2
import json
from datetime import datetime

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
        print(f"❌ Erreur de connexion: {e}")
        return None

def get_admin_user():
    try:
        conn = get_connection()
        if not conn:
            return None
        
        cur = conn.cursor()
        cur.execute("""
            SELECT u.id 
            FROM utilisateurs u
            JOIN roles r ON u.role_id = r.id
            WHERE r.nom_role = 'admin' AND u.est_actif = true
            LIMIT 1
        """)
        
        admin = cur.fetchone()
        if admin:
            admin_id = admin[0]
            print(f"✅ Admin trouvé (ID: {admin_id})")
            cur.close()
            conn.close()
            return admin_id
        
        cur.execute("SELECT id FROM utilisateurs WHERE est_actif = true LIMIT 1")
        user = cur.fetchone()
        if user:
            user_id = user[0]
            print(f"⚠️ Aucun admin trouvé. Utilisation ID: {user_id}")
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

def get_chapitre_id():
    try:
        conn = get_connection()
        if not conn:
            return None
        
        cur = conn.cursor()
        cur.execute("SELECT id FROM chapitres WHERE id = 2 OR titre ILIKE %s", ('%CSS%',))
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result:
            chapitre_id = result[0]
            print(f"📚 Chapitre CSS trouvé (ID: {chapitre_id})")
            return chapitre_id
        return None
    except Exception as e:
        print(f"⚠️ Erreur récupération chapitre: {e}")
        return None

def inserer_cours_text():
    admin_id = get_admin_user()
    if not admin_id:
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "css-text-properties"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>📝 CSS Text - Propriétés du Texte en CSS</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Les propriétés CSS pour le texte permettent de personnaliser l'apparence du contenu textuel.</p>
    </div>
    
    <h2>Propriétés principales</h2>
    <ul>
        <li><strong>text-align</strong> : Alignement (left, right, center, justify)</li>
        <li><strong>text-decoration</strong> : Décoration (underline, overline, line-through, none)</li>
        <li><strong>text-transform</strong> : Casse (uppercase, lowercase, capitalize)</li>
        <li><strong>letter-spacing</strong> : Espacement entre lettres</li>
        <li><strong>word-spacing</strong> : Espacement entre mots</li>
        <li><strong>line-height</strong> : Hauteur de ligne (interlignage)</li>
        <li><strong>text-indent</strong> : Indentation première ligne</li>
        <li><strong>text-shadow</strong> : Ombre du texte</li>
        <li><strong>color</strong> : Couleur du texte</li>
    </ul>
    """.strip()
    
    cours_data = {
        "titre": "CSS Text - Propriétés de Mise en Forme du Texte",
        "slug": slug_cours,
        "description": "Apprenez à maîtriser les propriétés CSS pour la mise en forme du texte.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 25,
        "ordre_affichage": 24,
        "chapitre_id": chapitre_id,
        "tags": ["css", "text", "typographie", "debutant"],
        "est_actif": True,
        "created_by": admin_id,
        "last_modified_by": admin_id
    }
    
    if existing:
        cours_id = existing[0]
        print(f"⚠️ Le cours existe déjà (ID: {cours_id})")
        cur.execute("""
            UPDATE cours_html 
            SET titre=%s, description=%s, contenu_texte=%s, difficulte=%s, 
                duree_estimee=%s, ordre_affichage=%s, chapitre_id=%s, tags=%s, 
                est_actif=%s, last_modified_by=%s, date_maj=CURRENT_TIMESTAMP
            WHERE slug=%s RETURNING id
        """, (cours_data["titre"], cours_data["description"], cours_data["contenu_texte"],
              cours_data["difficulte"], cours_data["duree_estimee"], cours_data["ordre_affichage"],
              cours_data["chapitre_id"], cours_data["tags"], cours_data["est_actif"],
              cours_data["last_modified_by"], slug_cours))
        cours_id = cur.fetchone()[0]
        print(f"✅ Cours mis à jour (ID: {cours_id})")
    else:
        cur.execute("""
            INSERT INTO cours_html 
            (titre, slug, description, contenu_texte, difficulte, duree_estimee, 
             ordre_affichage, chapitre_id, tags, est_actif, created_by, last_modified_by, date_creation, date_maj)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)
            RETURNING id
        """, (cours_data["titre"], slug_cours, cours_data["description"], cours_data["contenu_texte"],
              cours_data["difficulte"], cours_data["duree_estimee"], cours_data["ordre_affichage"],
              cours_data["chapitre_id"], cours_data["tags"], cours_data["est_actif"],
              cours_data["created_by"], cours_data["last_modified_by"]))
        cours_id = cur.fetchone()[0]
        print(f"✅ Cours créé (ID: {cours_id})")
    
    conn.commit()
    cur.close()
    conn.close()
    return cours_id

def inserer_questions_text(cours_id):
    admin_id = get_admin_user()
    if not admin_id:
        return False
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    try:
        cur.execute("ALTER TABLE questions_quiz DISABLE TRIGGER trigger_log_questions")
    except:
        pass
    
    cur.execute("DELETE FROM questions_quiz WHERE cours_id = %s", (cours_id,))
    
    questions = [
        
        ("Quelle propriété CSS permet d'aligner le texte horizontalement ?",
         '{"A": "text-align", "B": "text-decoration", "C": "text-transform", "D": "text-shadow"}',
         'A', 10, 'facile', "text-align contrôle l'alignement horizontal du texte.", 'texte'),
        
        ("Que signifie text-transform: capitalize ?",
         '{"A": "Tout en majuscules", "B": "Tout en minuscules", "C": "Première lettre de chaque mot en majuscule", "D": "Aucune transformation"}',
         'C', 15, 'moyen', "capitalize met la première lettre de chaque mot en majuscule.", 'texte'),
        
        
        ("Comment retirer le soulignement d'un lien en CSS ?",
         '{"A": "text-decoration: none;", "B": "text-decoration: underline;", "C": "text-transform: none;", "D": "text-align: none;"}',
         'A', 10, 'facile', "text-decoration: none; supprime la décoration du texte.", 'audio'),
        
        ("Quelle propriété permet d'ajouter une ombre au texte ?",
         '{"A": "text-decoration", "B": "text-shadow", "C": "box-shadow", "D": "text-align"}',
         'B', 10, 'facile', "text-shadow ajoute une ombre portée au texte.", 'audio'),
        
        ("Quelle propriété contrôle l'espacement entre les lettres ?",
         '{"A": "word-spacing", "B": "letter-spacing", "C": "line-height", "D": "text-indent"}',
         'B', 15, 'moyen', "letter-spacing définit l'espacement entre les caractères.", 'audio'),
        
        
        ("Comment justifier un paragraphe (texte aligné à gauche et à droite) ?",
         '{"A": "text-align: left;", "B": "text-align: right;", "C": "text-align: center;", "D": "text-align: justify;"}',
         'D', 10, 'facile', "text-align: justify; justifie le texte.", 'video'),
        
        ("Quelle propriété définit la hauteur de ligne (interlignage) ?",
         '{"A": "line-height", "B": "letter-spacing", "C": "word-spacing", "D": "text-indent"}',
         'A', 10, 'facile', "line-height contrôle l'interlignage.", 'video'),
        
        ("Quelle valeur de text-decoration permet de barrer le texte ?",
         '{"A": "underline", "B": "overline", "C": "line-through", "D": "none"}',
         'C', 10, 'facile', "text-decoration: line-through; barre le texte.", 'video'),
        
        ("Quelle propriété permet de décaler la première ligne d'un paragraphe ?",
         '{"A": "text-align", "B": "text-indent", "C": "letter-spacing", "D": "word-spacing"}',
         'B', 15, 'moyen', "text-indent définit l'indentation de la première ligne.", 'video'),
        
        ("Que fait la propriété text-transform: uppercase ?",
         '{"A": "Met le texte en minuscules", "B": "Met le texte en majuscules", "C": "Met la première lettre en majuscule", "D": "Supprime les espaces"}',
         'B', 10, 'facile', "text-transform: uppercase transforme tout le texte en majuscules.", 'video')
    ]
    
    for q in questions:
        cur.execute("""
            INSERT INTO questions_quiz 
            (cours_id, question, type_question, points, difficulte, 
             options, reponse_correcte, explication, mode_specifique, created_by, date_creation)
            VALUES (%s, %s, 'choix_multiple', %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        """, (cours_id, q[0], q[3], q[4], q[1], q[2], q[5], q[6], admin_id))
        print(f"  ✅ [{q[6].upper()}] {q[0][:50]}...")
    
    conn.commit()
    
    try:
        cur.execute("ALTER TABLE questions_quiz ENABLE TRIGGER trigger_log_questions")
    except:
        pass
    
    cur.close()
    conn.close()
    
    print(f"✅ {len(questions)} questions Text insérées")
    return True

def main():
    print("\n" + "=" * 60)
    print("🎓 INSERTION DU COURS: CSS TEXT")
    print("=" * 60)
    
    cours_id = inserer_cours_text()
    if cours_id:
        inserer_questions_text(cours_id)
        print(f"\n🎉 Succès ! Cours Text créé (ID: {cours_id})")
    else:
        print("\n❌ Échec")

if __name__ == "__main__":
    main()