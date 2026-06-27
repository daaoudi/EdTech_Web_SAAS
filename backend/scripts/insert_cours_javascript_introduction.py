
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
        cur.execute("SELECT id FROM chapitres WHERE id = 3 OR titre ILIKE %s", ('%JavaScript%',))
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result:
            chapitre_id = result[0]
            print(f"📚 Chapitre JavaScript trouvé (ID: {chapitre_id})")
            return chapitre_id
        return None
    except Exception as e:
        print(f"⚠️ Erreur récupération chapitre: {e}")
        return None

def inserer_cours_javascript_introduction():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "javascript-introduction"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>🚀 JavaScript - Introduction</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> JavaScript est le langage de programmation du web. Il permet de rendre les pages web interactives et dynamiques.</p>
    </div>
    
    <h2>Qu'est-ce que JavaScript ?</h2>
    <p>JavaScript est un langage de programmation qui permet de :</p>
    <ul>
        <li>Calculer, manipuler et valider des données</li>
        <li>Mettre à jour et modifier HTML et CSS</li>
        <li>Réagir aux actions de l'utilisateur (clics, saisies, etc.)</li>
        <li>Communiquer avec des serveurs</li>
    </ul>
    
    <h2>1. JavaScript peut modifier le contenu HTML</h2>
    <p>Une des méthodes JavaScript les plus utilisées est <code>getElementById()</code>. Elle permet de "trouver" un élément HTML et de modifier son contenu.</p>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;body&gt;
    &lt;h2&gt;JavaScript peut modifier HTML&lt;/h2&gt;
    
    &lt;p id="demo"&gt;Texte original&lt;/p&gt;
    
    &lt;button type="button" onclick='document.getElementById("demo").innerHTML = "Hello JavaScript!"'&gt;
        Cliquez-moi !
    &lt;/button&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <div class="tip-box">
        <p><strong>💡 Astuce :</strong> JavaScript accepte à la fois les guillemets simples et doubles pour les chaînes de caractères.</p>
    </div>
    
    <h2>2. JavaScript peut modifier les attributs HTML</h2>
    <p>JavaScript peut changer la valeur des attributs HTML, comme l'attribut <code>src</code> d'une image.</p>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;body&gt;
    &lt;h2&gt;JavaScript peut modifier les attributs HTML&lt;/h2&gt;
    
    &lt;img id="myImage" src="bulb_off.jpg" width="100" height="180"&gt;
    
    &lt;button onclick="document.getElementById('myImage').src='bulb_on.jpg'"&gt;
        Allumer la lampe
    &lt;/button&gt;
    
    &lt;button onclick="document.getElementById('myImage').src='bulb_off.jpg'"&gt;
        Éteindre la lampe
    &lt;/button&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h2>3. JavaScript peut modifier les styles CSS</h2>
    <p>Changer le style d'un élément HTML est une variante de la modification d'un attribut HTML.</p>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;body&gt;
    &lt;h2&gt;JavaScript peut modifier les styles CSS&lt;/h2&gt;
    
    &lt;p id="demo"&gt;Ce texte va changer de couleur.&lt;/p&gt;
    
    &lt;button onclick="document.getElementById('demo').style.color = 'red'"&gt;
        Rouge
    &lt;/button&gt;
    
    &lt;button onclick="document.getElementById('demo').style.color = 'blue'"&gt;
        Bleu
    &lt;/button&gt;
    
    &lt;button onclick="document.getElementById('demo').style.fontSize = '35px'"&gt;
        Agrandir
    &lt;/button&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h2>4. JavaScript peut masquer des éléments HTML</h2>
    <p>Masquer des éléments HTML peut se faire en modifiant la propriété <code>display</code> du style.</p>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;body&gt;
    &lt;h2&gt;JavaScript peut masquer des éléments&lt;/h2&gt;
    
    &lt;p id="demo"&gt;Ce texte va être masqué.&lt;/p&gt;
    
    &lt;button onclick="document.getElementById('demo').style.display = 'none'"&gt;
        Masquer
    &lt;/button&gt;
    
    &lt;button onclick="document.getElementById('demo').style.display = 'block'"&gt;
        Afficher
    &lt;/button&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h2>5. JavaScript peut afficher des éléments masqués</h2>
    <p>Afficher des éléments HTML masqués se fait en restaurant la propriété <code>display</code>.</p>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;body&gt;
    &lt;h2&gt;JavaScript peut afficher des éléments masqués&lt;/h2&gt;
    
    &lt;p id="demo" style="display: none"&gt;Ce texte est masqué au départ.&lt;/p&gt;
    
    &lt;button onclick="document.getElementById('demo').style.display = 'block'"&gt;
        Afficher
    &lt;/button&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h2>6. Exemple complet</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;style&gt;
        .container {
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            border: 1px solid #ccc;
            border-radius: 10px;
            font-family: Arial, sans-serif;
        }
        
        button {
            margin: 5px;
            padding: 10px 15px;
            cursor: pointer;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
        }
        
        button:hover {
            background-color: #45a049;
        }
        
        .output {
            margin-top: 20px;
            padding: 15px;
            background-color: #f0f0f0;
            border-radius: 5px;
        }
    &lt;/style&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;div class="container"&gt;
        &lt;h1&gt;Démonstration JavaScript&lt;/h1&gt;
        
        &lt;div class="output" id="demo"&gt;
            &lt;p&gt;Ce contenu va changer !&lt;/p&gt;
        &lt;/div&gt;
        
        &lt;button onclick='document.getElementById("demo").innerHTML = "&lt;p&gt;Nouveau contenu !&lt;/p&gt;"'&gt;
            Changer le contenu
        &lt;/button&gt;
        
        &lt;button onclick="document.getElementById('demo').style.backgroundColor = '#ffcccc'"&gt;
            Fond rouge
        &lt;/button&gt;
        
        &lt;button onclick="document.getElementById('demo').style.backgroundColor = '#ccffcc'"&gt;
            Fond vert
        &lt;/button&gt;
        
        &lt;button onclick="document.getElementById('demo').style.display = 'none'"&gt;
            Masquer
        &lt;/button&gt;
        
        &lt;button onclick="document.getElementById('demo').style.display = 'block'"&gt;
            Afficher
        &lt;/button&gt;
        
        &lt;button onclick='document.getElementById("demo").innerHTML = "&lt;p&gt;Contenu restauré !&lt;/p&gt;; document.getElementById(\"demo\").style.backgroundColor = \"#f0f0f0\""'&gt;
            Réinitialiser
        &lt;/button&gt;
    &lt;/div&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h2>Résumé</h2>
    
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left;">Action</th>
            <th style="padding: 8px; text-align: left;">Syntaxe JavaScript</th>
        </thead>
        <tbody>
            <tr><td style="padding: 8px;">Modifier le contenu</td><td style="padding: 8px;"><code>document.getElementById(id).innerHTML = nouveauTexte</code></td></tr>
            <tr><td style="padding: 8px;">Modifier un attribut</td><td style="padding: 8px;"><code>document.getElementById(id).attribut = nouvelleValeur</code></td></tr>
            <tr><td style="padding: 8px;">Modifier le style</td><td style="padding: 8px;"><code>document.getElementById(id).style.propriete = nouvelleValeur</code></td></tr>
            <tr><td style="padding: 8px;">Masquer</td><td style="padding: 8px;"><code>document.getElementById(id).style.display = 'none'</code></td></tr>
            <tr><td style="padding: 8px;">Afficher</td><td style="padding: 8px;"><code>document.getElementById(id).style.display = 'block'</code></td></tr>
        </tbody>
    </table>
    
    <div class="info-box">
        <p><strong>💡 À retenir :</strong> JavaScript est le langage qui donne vie aux pages web. Il peut tout modifier : contenu, attributs, styles.</p>
    </div>
    """.strip()
    
    cours_data = {
        "titre": "JavaScript Introduction - Les Bases",
        "slug": slug_cours,
        "description": "Découvrez JavaScript, le langage de programmation du web. Apprenez à modifier le contenu HTML, les attributs, les styles CSS, ainsi qu'à masquer et afficher des éléments.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 20,
        "ordre_affichage": 1,
        "chapitre_id": chapitre_id,
        "tags": ["javascript", "introduction", "getElementById", "innerHTML", "styles", "debutant"],
        "est_actif": True,
        "created_by": admin_id,
        "last_modified_by": admin_id
    }
    
    if existing:
        cours_id = existing[0]
        print(f"⚠️ Le cours existe déjà (ID: {cours_id})")
        cur.execute("""
            UPDATE cours_html 
            SET titre = %s, description = %s, contenu_texte = %s, 
                difficulte = %s, duree_estimee = %s, ordre_affichage = %s,
                chapitre_id = %s, tags = %s, est_actif = %s, last_modified_by = %s,
                date_maj = CURRENT_TIMESTAMP
            WHERE slug = %s
            RETURNING id
        """, (cours_data["titre"], cours_data["description"], cours_data["contenu_texte"],
              cours_data["difficulte"], cours_data["duree_estimee"], cours_data["ordre_affichage"],
              cours_data["chapitre_id"], cours_data["tags"], cours_data["est_actif"],
              cours_data["last_modified_by"], slug_cours))
        cours_id = cur.fetchone()[0]
        print(f"✅ Cours mis à jour (ID: {cours_id})")
    else:
        cur.execute("""
            INSERT INTO cours_html 
            (titre, slug, description, contenu_texte, difficulte, 
             duree_estimee, ordre_affichage, chapitre_id, tags, est_actif, 
             created_by, last_modified_by, date_creation, date_maj)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id
        """, (cours_data["titre"], cours_data["slug"], cours_data["description"], cours_data["contenu_texte"],
              cours_data["difficulte"], cours_data["duree_estimee"], cours_data["ordre_affichage"],
              cours_data["chapitre_id"], cours_data["tags"], cours_data["est_actif"],
              cours_data["created_by"], cours_data["last_modified_by"]))
        cours_id = cur.fetchone()[0]
        print(f"✅ Cours créé (ID: {cours_id})")
    
    conn.commit()
    cur.close()
    conn.close()
    return cours_id

def inserer_questions_javascript_introduction(cours_id):
    
    
    admin_id = get_admin_user()
    if not admin_id:
        return False
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    
    try:
        cur.execute("ALTER TABLE questions_quiz DISABLE TRIGGER trigger_log_questions")
        conn.commit()
    except:
        pass
    
    
    try:
        cur.execute("DELETE FROM questions_quiz WHERE cours_id = %s", (cours_id,))
        conn.commit()
        print(f"✅ Anciennes questions supprimées")
    except:
        conn.rollback()
    
    questions = [  
        
        {
            "question": "Qu'est-ce que JavaScript ?",
            "options": '{"A": "Un langage de balisage comme HTML", "B": "Un langage de programmation du web", "C": "Un langage de style comme CSS", "D": "Un logiciel de montage video"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "JavaScript est le langage de programmation du web. Il permet de rendre les pages interactives.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quelle methode JavaScript permet de trouver un element HTML par son ID ?",
            "options": '{"A": "getElementById()", "B": "getElementByClass()", "C": "getElementByName()", "D": "getElementByTag()"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "getElementById() est la methode qui permet de selectionner un element HTML par son attribut id.",
            "mode_specifique": "texte"
        },
        
        
        {
            "question": "Comment modifier le contenu texte d'un element HTML en JavaScript ?",
            "options": '{"A": "element.value = nouveauTexte", "B": "element.innerHTML = nouveauTexte", "C": "element.text = nouveauTexte", "D": "element.content = nouveauTexte"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "innerHTML permet de modifier le contenu HTML d'un element.",
            "mode_specifique": "audio"
        },
        {
            "question": "Comment masquer un element HTML avec JavaScript ?",
            "options": '{"A": "element.style.hide = true", "B": "element.style.display = \'none\'", "C": "element.style.visible = false", "D": "element.style.opacity = 0"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "element.style.display = 'none' masque l'element en le supprimant de la mise en page.",
            "mode_specifique": "audio"
        },
        {
            "question": "Comment reafficher un element masque avec JavaScript ?",
            "options": '{"A": "element.style.display = \'visible\'", "B": "element.style.display = \'show\'", "C": "element.style.display = \'block\'", "D": "element.style.display = \'on\'"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "element.style.display = 'block' (ou 'inline') permet de reafficher un element masque.",
            "mode_specifique": "audio"
        },
        
        
        {
            "question": "JavaScript peut-il modifier les attributs HTML comme src d'une image ?",
            "options": '{"A": "Oui", "B": "Non", "C": "Uniquement avec du CSS", "D": "Seulement sur mobile"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "Oui, JavaScript peut modifier n'importe quel attribut HTML, y compris src d'une image.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle propriete CSS utilise-t-on pour modifier la couleur de fond d'un element en JavaScript ?",
            "options": '{"A": "backgroundColor", "B": "background-color", "C": "bgColor", "D": "background"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "En JavaScript, on utilise backgroundColor (camelCase) pour modifier la couleur de fond.",
            "mode_specifique": "video"
        },
        {
            "question": "JavaScript accepte-t-il les guillemets simples et doubles pour les chaines ?",
            "options": '{"A": "Uniquement les guillemets doubles", "B": "Uniquement les guillemets simples", "C": "Les deux", "D": "Ni l\'un ni l\'autre"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "JavaScript accepte a la fois les guillemets simples et doubles pour les chaines de caracteres.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle est la bonne syntaxe pour modifier la taille de police d'un element ?",
            "options": '{"A": "element.style.font-size = \'20px\'", "B": "element.style.fontSize = \'20px\'", "C": "element.style.fontsize = \'20px\'", "D": "element.style.fontSize = 20px"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "En JavaScript, les proprietes CSS s'ecrivent en camelCase : fontSize, backgroundColor, etc.",
            "mode_specifique": "video"
        },
        {
            "question": "Que peut-on faire avec JavaScript sur une page web ?",
            "options": '{"A": "Modifier le HTML", "B": "Modifier les styles CSS", "C": "Masquer/afficher des elements", "D": "Toutes ces reponses"}',
            "reponse_correcte": "D",
            "points": 10,
            "difficulte": "facile",
            "explication": "JavaScript peut tout modifier : contenu HTML, styles CSS, attributs, et peut masquer/afficher des elements.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle est la methode JavaScript pour changer le contenu HTML d'un element ?",
            "options": '{"A": "innerContent", "B": "innerHTML", "C": "innerText", "D": "htmlContent"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "innerHTML est la propriete qui permet de lire ou modifier le contenu HTML d'un element.",
            "mode_specifique": "video"
        }
    ]
    
    print(f"\n📝 Insertion de {len(questions)} questions pour le cours ID {cours_id}...")
    
    questions_creees = 0
    questions_existantes = 0
    
    for q in questions:
        
        cur.execute("""
            SELECT id FROM questions_quiz 
            WHERE cours_id = %s AND question = %s
        """, (cours_id, q["question"]))
        
        existing = cur.fetchone()
        
        if existing:
            questions_existantes += 1
            print(f"  ⚠️ Question déjà existante: {q['question'][:50]}...")
            continue
        
        try:
            cur.execute("""
                INSERT INTO questions_quiz 
                (cours_id, question, type_question, points, difficulte, 
                 options, reponse_correcte, explication, mode_specifique, 
                 created_by, date_creation)
                VALUES (%s, %s, 'choix_multiple', %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (
                cours_id,
                q["question"],
                q["points"],
                q["difficulte"],
                q["options"],
                q["reponse_correcte"],
                q["explication"],
                q["mode_specifique"],
                admin_id
            ))
            
            questions_creees += 1
            print(f"  ✅ [{q['mode_specifique'].upper()}] {q['question'][:50]}...")
            conn.commit()
            
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
            print(f"     Question: {q['question']}")
            print(f"     Options: {q['options']}")
            conn.rollback()
    
    
    try:
        cur.execute("ALTER TABLE questions_quiz ENABLE TRIGGER trigger_log_questions")
        conn.commit()
    except:
        pass
    
    cur.close()
    conn.close()
    
    print(f"\n📊 RÉSUMÉ:")
    print(f"   • Questions créées: {questions_creees}")
    print(f"   • Questions existantes: {questions_existantes}")
    
    return True

def main():
    print("\n" + "=" * 60)
    print("🎓 INSERTION DU COURS: JAVASCRIPT INTRODUCTION")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    cours_id = inserer_cours_javascript_introduction()
    
    if cours_id:
        inserer_questions_javascript_introduction(cours_id)
        print(f"\n🎉 Succès ! Cours 'JavaScript Introduction - Les Bases' créé (ID: {cours_id})")
    else:
        print("\n❌ Échec de l'insertion")

if __name__ == "__main__":
    main()