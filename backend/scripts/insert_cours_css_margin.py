
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

def inserer_cours_margin():
    admin_id = get_admin_user()
    if not admin_id:
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "css-margin"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>📐 CSS Margin - Les Marges en CSS</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Les marges créent de l'espace à l'extérieur de la bordure d'un élément.</p>
    </div>
    
    <h2>Introduction aux Marges</h2>
    <p>La propriété <code>margin</code> définit l'espace extérieur autour d'un élément.</p>
    
    <h2>1. Propriétés individuelles</h2>
    <ul>
        <li><strong>margin-top</strong> : Marge supérieure</li>
        <li><strong>margin-right</strong> : Marge droite</li>
        <li><strong>margin-bottom</strong> : Marge inférieure</li>
        <li><strong>margin-left</strong> : Marge gauche</li>
    </ul>
    
    <h2>2. Propriété raccourcie margin</h2>
    <pre><code>margin: 20px;           /* 1 valeur : les 4 côtés */
margin: 10px 20px;      /* 2 valeurs : haut/bas et droite/gauche */
margin: 10px 20px 30px; /* 3 valeurs : haut, droite/gauche, bas */
margin: 10px 20px 30px 40px; /* 4 valeurs : haut, droite, bas, gauche */</code></pre>
    
    <h2>3. Auto margins pour centrer</h2>
    <pre><code>margin: 0 auto;  /* centre horizontalement */</code></pre>
    
    <h2>4. Le margin collapsing</h2>
    <p>Les marges verticales entre éléments adjacents se fusionnent en une seule marge.</p>
    """.strip()
    
    cours_data = {
        "titre": "CSS Margin - Les Marges en CSS",
        "slug": slug_cours,
        "description": "Apprenez à utiliser les marges en CSS pour contrôler l'espacement extérieur des éléments.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 20,
        "ordre_affichage": 22,
        "chapitre_id": chapitre_id,
        "tags": ["css", "margin", "espacement", "box-model", "debutant"],
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

def inserer_questions_margin(cours_id):
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
        
        ("Quelle est la différence entre margin et padding ?",
         '{"A": "margin et padding font la même chose", "B": "margin est l\'espace extérieur (hors bordure), padding est l\'espace intérieur", "C": "margin s\'applique au texte, padding aux images", "D": "margin ne fonctionne que sur mobile"}',
         'B', 10, 'facile', "Margin crée de l'espace à l'extérieur, padding à l'intérieur.", 'texte'),
        
        ("Que signifie margin: 10px 20px 30px 40px ?",
         '{"A": "top=10px, right=20px, bottom=30px, left=40px", "B": "top=40px, right=30px, bottom=20px, left=10px", "C": "top=10px, right=30px, bottom=20px, left=40px", "D": "top=10px, right=40px, bottom=20px, left=30px"}',
         'A', 15, 'moyen', "L'ordre est horaire : haut, droite, bas, gauche.", 'texte'),
        
        
        ("Comment centrer horizontalement un élément block avec margin ?",
         '{"A": "margin: center;", "B": "margin: 0 auto;", "C": "margin: auto 0;", "D": "text-align: center;"}',
         'B', 10, 'facile', "margin: 0 auto centre l'élément horizontalement.", 'audio'),
        
        ("Quelle propriété définit la marge uniquement à droite ?",
         '{"A": "margin-right", "B": "margin-left", "C": "margin-bottom", "D": "margin-top"}',
         'A', 10, 'facile', "margin-right définit la marge à droite.", 'audio'),
        
        ("Quelle est la valeur par défaut de margin ?",
         '{"A": "0", "B": "auto", "C": "1px", "D": "none"}',
         'A', 10, 'facile', "Par défaut, margin est à 0.", 'audio'),
        
        
        ("Qu'est-ce que le 'margin collapsing' ?",
         '{"A": "Les marges disparaissent", "B": "Les marges horizontales se fusionnent", "C": "Les marges verticales adjacentes se fusionnent", "D": "Les marges deviennent transparentes"}',
         'C', 15, 'moyen', "Les marges verticales adjacentes se fusionnent en une seule.", 'video'),
        
        ("Si vous voulez espacer deux éléments verticalement, quelle propriété utilisez-vous ?",
         '{"A": "padding-top", "B": "margin-bottom", "C": "padding-bottom", "D": "margin-left"}',
         'B', 10, 'facile', "margin-bottom crée de l'espace sous l'élément.", 'video'),
        
        ("Que fait margin: auto ?",
         '{"A": "Centrage vertical", "B": "Centrage horizontal", "C": "Centrage complet", "D": "Aucun effet"}',
         'B', 10, 'facile', "margin: auto permet de centrer horizontalement.", 'video')
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
    
    print(f"✅ {len(questions)} questions Margin insérées")
    return True

def main():
    print("\n" + "=" * 60)
    print("🎓 INSERTION DU COURS: CSS MARGIN")
    print("=" * 60)
    
    cours_id = inserer_cours_margin()
    if cours_id:
        inserer_questions_margin(cours_id)
        print(f"\n🎉 Succès ! Cours Margin créé (ID: {cours_id})")
    else:
        print("\n❌ Échec")

if __name__ == "__main__":
    main()