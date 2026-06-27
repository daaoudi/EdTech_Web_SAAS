
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

def inserer_cours_padding():
    admin_id = get_admin_user()
    if not admin_id:
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "css-padding"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>📦 CSS Padding - Le Remplissage en CSS</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Le padding crée de l'espace à l'intérieur d'un élément.</p>
    </div>
    
    <h2>Introduction au Padding</h2>
    <p>La propriété <code>padding</code> définit l'espace intérieur d'un élément.</p>
    
    <h2>1. Propriétés individuelles</h2>
    <ul>
        <li><strong>padding-top</strong> : Padding supérieur</li>
        <li><strong>padding-right</strong> : Padding droit</li>
        <li><strong>padding-bottom</strong> : Padding inférieur</li>
        <li><strong>padding-left</strong> : Padding gauche</li>
    </ul>
    
    <h2>2. Propriété raccourcie padding</h2>
    <pre><code>padding: 20px;           /* 1 valeur : les 4 côtés */
padding: 10px 20px;      /* 2 valeurs : haut/bas et droite/gauche */
padding: 10px 20px 30px; /* 3 valeurs : haut, droite/gauche, bas */
padding: 10px 20px 30px 40px; /* 4 valeurs : haut, droite, bas, gauche */</code></pre>
    
    <h2>3. Unités et pourcentages</h2>
    <pre><code>padding: 20px;   /* pixels */
padding: 10%;    /* pourcentage relatif au parent */
padding: 2em;    /* relatif à la police */</code></pre>
    """.strip()
    
    cours_data = {
        "titre": "CSS Padding - Le Remplissage en CSS",
        "slug": slug_cours,
        "description": "Apprenez à utiliser le padding en CSS pour contrôler l'espacement intérieur des éléments.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 20,
        "ordre_affichage": 23,
        "chapitre_id": chapitre_id,
        "tags": ["css", "padding", "espacement", "box-model", "debutant"],
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

def inserer_questions_padding(cours_id):
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
        
        ("Que fait la propriété padding en CSS ?",
         '{"A": "Crée de l\'espace à l\'extérieur", "B": "Crée de l\'espace à l\'intérieur, entre contenu et bordure", "C": "Ajoute une bordure", "D": "Change la couleur"}',
         'B', 10, 'facile', "Padding crée l'espace intérieur entre contenu et bordure.", 'texte'),
        
        ("À quoi correspond padding: 20px ?",
         '{"A": "20px en haut", "B": "20px sur les 4 côtés", "C": "20px à gauche/droite", "D": "20px en haut/bas"}',
         'B', 10, 'facile', "Une seule valeur s'applique aux 4 côtés.", 'texte'),
        
        
        ("Quel padding applique 10px en haut/bas et 20px à gauche/droite ?",
         '{"A": "padding: 10px 20px;", "B": "padding: 20px 10px;", "C": "padding: 10px 20px 10px 20px;", "D": "Les réponses A et C"}',
         'D', 10, 'facile', "padding: 10px 20px = 10px haut/bas, 20px droite/gauche.", 'audio'),
        
        ("Quelle propriété pour ajouter de l'espace à l'intérieur d'un élément à gauche ?",
         '{"A": "margin-left", "B": "padding-left", "C": "margin-right", "D": "padding-right"}',
         'B', 10, 'facile', "padding-left ajoute de l'espace intérieur à gauche.", 'audio'),
        
        
        ("Le padding peut-il avoir une couleur d'arrière-plan ?",
         '{"A": "Non, transparent", "B": "Oui, à l\'intérieur de la bordure", "C": "Seulement sur block", "D": "Uniquement en impression"}',
         'B', 10, 'facile', "Padding hérite de la couleur d'arrière-plan.", 'video'),
        
        ("Comment définir un padding de 5px en haut et 15px sur les autres côtés ?",
         '{"A": "padding: 5px 15px;", "B": "padding: 15px 5px;", "C": "padding: 5px 15px 15px 15px;", "D": "padding: 15px 5px 5px 5px;"}',
         'C', 15, 'moyen', "padding: 5px 15px 15px 15px donne top=5, autres=15.", 'video'),
        
        ("Comment éviter que padding n'augmente la largeur totale ?",
         '{"A": "overflow: hidden", "B": "box-sizing: border-box", "C": "display: block", "D": "position: relative"}',
         'B', 15, 'moyen', "box-sizing: border-box inclut padding dans la largeur.", 'video')
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
    
    print(f"✅ {len(questions)} questions Padding insérées")
    return True

def main():
    print("\n" + "=" * 60)
    print("🎓 INSERTION DU COURS: CSS PADDING")
    print("=" * 60)
    
    cours_id = inserer_cours_padding()
    if cours_id:
        inserer_questions_padding(cours_id)
        print(f"\n🎉 Succès ! Cours Padding créé (ID: {cours_id})")
    else:
        print("\n❌ Échec")

if __name__ == "__main__":
    main()