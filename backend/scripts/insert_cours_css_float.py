
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

def inserer_cours_css_float():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "css-float"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>🌊 CSS Float - Positionner les Éléments</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> La propriété CSS <code>float</code> permet de positionner un élément à gauche ou à droite, permettant au texte et aux autres éléments de s'enrouler autour.</p>
    </div>
    
    <h2>Introduction à Float</h2>
    <p>La propriété <code>float</code> est utilisée pour positionner un élément sur le côté gauche ou droit de son conteneur, permettant au texte et aux autres éléments de s'enrouler autour.</p>
    
    <div class="tip-box">
        <p><strong>💡 Cas d'usage :</strong> Floats sont souvent utilisés pour créer des mises en page avec texte autour d'images, des galeries d'images, et des colonnes de texte.</p>
    </div>
    
    <h2>1. Valeurs de float</h2>
    
    <ul>
        <li><strong>left</strong> : Flotte l'élément à gauche</li>
        <li><strong>right</strong> : Flotte l'élément à droite</li>
        <li><strong>none</strong> : Pas de flottement (par défaut)</li>
        <li><strong>inherit</strong> : Hérite de la valeur du parent</li>
    </ul>
    
    <pre><code>/* Flotter l'image à gauche */
img {
    float: left;
    margin-right: 15px;
}

/* Flotter l'image à droite */
img {
    float: right;
    margin-left: 15px;
}</code></pre>
    
    <h2>2. Flotter des images avec texte</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;style&gt;
        .img-left {
            float: left;
            margin-right: 15px;
            width: 150px;
        }
        
        .img-right {
            float: right;
            margin-left: 15px;
            width: 150px;
        }
        
        .text {
            text-align: justify;
        }
    &lt;/style&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;h2&gt;Image flottante à gauche&lt;/h2&gt;
    &lt;img src="image.jpg" class="img-left"&gt;
    &lt;p class="text"&gt;Ce texte s'enroule autour de l'image flottante à gauche. 
    L'image est positionnée à gauche et le texte remplit l'espace restant à droite.&lt;/p&gt;
    
    &lt;h2&gt;Image flottante à droite&lt;/h2&gt;
    &lt;img src="image.jpg" class="img-right"&gt;
    &lt;p class="text"&gt;Ce texte s'enroule autour de l'image flottante à droite. 
    L'image est positionnée à droite et le texte remplit l'espace restant à gauche.&lt;/p&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h2>3. Galerie d'images avec float</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;style&gt;
        .gallery {
            width: 100%;
            overflow: auto;
        }
        
        .box {
            float: left;
            width: 30%;
            margin: 1.5%;
            background-color: #f0f0f0;
            padding: 10px;
            box-sizing: border-box;
            text-align: center;
        }
        
        .box img {
            width: 100%;
            height: auto;
        }
        
        /* Clearfix pour le conteneur parent */
        .clearfix::after {
            content: "";
            clear: both;
            display: table;
        }
    &lt;/style&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;h2&gt;Galerie d'images&lt;/h2&gt;
    &lt;div class="gallery clearfix"&gt;
        &lt;div class="box"&gt;
            &lt;img src="image1.jpg" alt="Image 1"&gt;
            &lt;p&gt;Description image 1&lt;/p&gt;
        &lt;/div&gt;
        &lt;div class="box"&gt;
            &lt;img src="image2.jpg" alt="Image 2"&gt;
            &lt;p&gt;Description image 2&lt;/p&gt;
        &lt;/div&gt;
        &lt;div class="box"&gt;
            &lt;img src="image3.jpg" alt="Image 3"&gt;
            &lt;p&gt;Description image 3&lt;/p&gt;
        &lt;/div&gt;
    &lt;/div&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h2>4. La propriété clear</h2>
    <p>La propriété <code>clear</code> empêche les éléments flottants d'apparaître sur un côté spécifique d'un élément.</p>
    
    <h3>Valeurs de clear :</h3>
    <ul>
        <li><strong>left</strong> : Aucun élément flottant à gauche</li>
        <li><strong>right</strong> : Aucun élément flottant à droite</li>
        <li><strong>both</strong> : Aucun élément flottant ni à gauche ni à droite</li>
        <li><strong>none</strong> : Pas de restriction (par défaut)</li>
    </ul>
    
    <pre><code>/* Empêcher les flottements de chaque côté */
h3 {
    clear: both;
}

/* Empêcher les flottements uniquement à gauche */
h3 {
    clear: left;
}</code></pre>
    
    <h2>5. Clearfix pour conteneurs parents</h2>
    <p>Lorsque des éléments à l'intérieur d'un conteneur sont flottants, le conteneur peut s'effondrer. Le clearfix résout ce problème.</p>
    
    <pre><code>/* Technique clearfix moderne */
.clearfix::after {
    content: "";
    clear: both;
    display: table;
}

/* Application */
.container {
    border: 2px solid black;
}

.container.clearfix::after {
    content: "";
    clear: both;
    display: table;
}</code></pre>
    
    <div class="info-box">
        <p><strong>💡 Astuce :</strong> La technique clearfix est essentielle pour que les conteneurs parents englobent correctement leurs éléments flottants.</p>
    </div>
    
    <h2>6. Créer des colonnes avec float</h2>
    
    <pre><code>/* Mise en page à 2 colonnes */
.column {
    float: left;
    width: 48%;
    margin: 1%;
    padding: 15px;
    background-color: #f9f9f9;
    box-sizing: border-box;
}

/* Mise en page à 3 colonnes */
.column-3 {
    float: left;
    width: 31.33%;
    margin: 1%;
    padding: 15px;
    background-color: #f9f9f9;
    box-sizing: border-box;
}

/* Footer ne doit pas flotter */
footer {
    clear: both;
    background-color: #333;
    color: white;
    text-align: center;
    padding: 10px;
}</code></pre>
    
    <h2>7. Exemple complet</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;style&gt;
        * {
            box-sizing: border-box;
        }
        
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* Galerie d'images */
        .gallery {
            overflow: auto;
            margin-bottom: 30px;
        }
        
        .gallery-item {
            float: left;
            width: 23%;
            margin: 1%;
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .gallery-item img {
            width: 100%;
            border-radius: 5px;
        }
        
        /* Colonnes de texte */
        .col-left {
            float: left;
            width: 60%;
            padding-right: 20px;
        }
        
        .col-right {
            float: right;
            width: 35%;
            background-color: #f0f0f0;
            padding: 15px;
            border-radius: 8px;
        }
        
        /* Image flottante dans le texte */
        .floating-img {
            float: left;
            width: 200px;
            margin-right: 20px;
            border-radius: 8px;
        }
        
        /* Clearfix */
        .clearfix::after {
            content: "";
            clear: both;
            display: table;
        }
        
        /* Footer */
        footer {
            clear: both;
            background-color: #333;
            color: white;
            text-align: center;
            padding: 15px;
            margin-top: 30px;
            border-radius: 8px;
        }
    &lt;/style&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;h1&gt;Démonstration de CSS Float&lt;/h1&gt;
    
    &lt;div class="gallery clearfix"&gt;
        &lt;div class="gallery-item"&gt;
            &lt;img src="placeholder.jpg" alt="Image 1"&gt;
            &lt;p&gt;Image 1&lt;/p&gt;
        &lt;/div&gt;
        &lt;div class="gallery-item"&gt;
            &lt;img src="placeholder.jpg" alt="Image 2"&gt;
            &lt;p&gt;Image 2&lt;/p&gt;
        &lt;/div&gt;
        &lt;div class="gallery-item"&gt;
            &lt;img src="placeholder.jpg" alt="Image 3"&gt;
            &lt;p&gt;Image 3&lt;/p&gt;
        &lt;/div&gt;
        &lt;div class="gallery-item"&gt;
            &lt;img src="placeholder.jpg" alt="Image 4"&gt;
            &lt;p&gt;Image 4&lt;/p&gt;
        &lt;/div&gt;
    &lt;/div&gt;
    
    &lt;div class="clearfix"&gt;
        &lt;div class="col-left"&gt;
            &lt;h2&gt;Article principal&lt;/h2&gt;
            &lt;img src="placeholder.jpg" class="floating-img" alt="Image flottante"&gt;
            &lt;p&gt;Ce texte s'enroule autour de l'image flottante à gauche. 
            La propriété float permet de créer des mises en page flexibles 
            et intéressantes.&lt;/p&gt;
        &lt;/div&gt;
        
        &lt;div class="col-right"&gt;
            &lt;h3&gt;Barre latérale&lt;/h3&gt;
            &lt;p&gt;Cette colonne est flottante à droite. Le contenu de la 
            colonne principale s'enroule autour d'elle.&lt;/p&gt;
        &lt;/div&gt;
    &lt;/div&gt;
    
    &lt;footer&gt;
        &lt;p&gt;© 2024 - Tous droits réservés&lt;/p&gt;
    &lt;/footer&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h2>8. Résumé des valeurs float et clear</h2>
    
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left;">Propriété</th>
            <th style="padding: 8px; text-align: left;">Valeur</th>
            <th style="padding: 8px; text-align: left;">Effet</th>
        </thead>
        <tbody>
            <tr><td style="padding: 8px;"><strong>float</strong></td><td style="padding: 8px;">left</td><td style="padding: 8px;">Flotte à gauche</td></tr>
            <tr><td style="padding: 8px;"><strong>float</strong></td><td style="padding: 8px;">right</td><td style="padding: 8px;">Flotte à droite</td></tr>
            <tr><td style="padding: 8px;"><strong>float</strong></td><td style="padding: 8px;">none</td><td style="padding: 8px;">Pas de flottement</td></tr>
            <tr><td style="padding: 8px;"><strong>clear</strong></td><td style="padding: 8px;">left</td><td style="padding: 8px;">Aucun flottant à gauche</td></tr>
            <tr><td style="padding: 8px;"><strong>clear</strong></td><td style="padding: 8px;">right</td><td style="padding: 8px;">Aucun flottant à droite</td></tr>
            <tr><td style="padding: 8px;"><strong>clear</strong></td><td style="padding: 8px;">both</td><td style="padding: 8px;">Aucun flottant de chaque côté</td></tr>
        </tbody>
    </table>
    
    <h2>9. Bonnes pratiques</h2>
    
    <ul>
        <li><strong>Utilisez clearfix</strong> pour les conteneurs parents d'éléments flottants</li>
        <li><strong>N'oubliez pas clear: both</strong> pour les éléments en bas de la mise en page</li>
        <li><strong>Float n'est pas idéal pour les mises en page complexes</strong> - préférez Flexbox ou Grid</li>
        <li><strong>Définissez toujours une largeur</strong> pour les éléments flottants</li>
        <li><strong>Utilisez box-sizing: border-box</strong> pour faciliter les calculs de largeur</li>
        <li><strong>Testez la responsivité</strong> des galeries d'images flottantes</li>
    </ul>
    
    <div class="info-box">
        <p><strong>💡 Astuce :</strong> Pour les mises en page modernes, Flexbox et Grid sont souvent préférables, mais float reste utile pour le texte autour des images et les galeries simples.</p>
    </div>
    """.strip()
    
    cours_data = {
        "titre": "CSS Float - Positionner les Éléments",
        "slug": slug_cours,
        "description": "Apprenez à utiliser la propriété CSS float pour positionner des éléments à gauche ou à droite, permettant au texte de s'enrouler autour. Découvrez comment créer des galeries d'images, des colonnes de texte, et utiliser la propriété clear pour gérer les flottements.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 20,
        "ordre_affichage": 32,
        "chapitre_id": chapitre_id,
        "tags": ["css", "float", "clear", "clearfix", "gallery", "layout", "columns", "debutant"],
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

def inserer_questions_css_float(cours_id):
    
    
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
            "question": "Quelle valeur de float permet de positionner un élément à gauche ?",
            "options": '{"A": "right", "B": "none", "C": "left", "D": "both"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "float: left; positionne l'élément à gauche, permettant au texte de s'enrouler à droite.",
            "mode_specifique": "texte"
        },
        {
            "question": "À quoi sert la propriété clear en CSS ?",
            "options": '{"A": "À supprimer les flottements", "B": "À empêcher les éléments flottants d\'apparaître autour d\'un élément", "C": "À rendre un élément transparent", "D": "À centrer un élément"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "clear empêche les éléments flottants d'apparaître sur le côté spécifié (left, right, both).",
            "mode_specifique": "texte"
        },
        
        
        {
            "question": "Comment créer une galerie d'images avec des éléments alignés horizontalement en CSS ?",
            "options": '{"A": "display: block;", "B": "position: absolute;", "C": "float: left;", "D": "text-align: center;"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "float: left; permet d'aligner horizontalement les éléments d'une galerie.",
            "mode_specifique": "audio"
        },
        {
            "question": "Que se passe-t-il lorsqu'un conteneur parent contient uniquement des éléments flottants ?",
            "options": '{"A": "Le conteneur s\'étend automatiquement", "B": "Le conteneur s\'effondre (hauteur nulle)", "C": "Le conteneur devient flottant", "D": "Le conteneur se divise en colonnes"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "Un conteneur contenant uniquement des éléments flottants s'effondre. On utilise clearfix pour résoudre ce problème.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle valeur de clear empêche les éléments flottants à gauche ET à droite ?",
            "options": '{"A": "left", "B": "right", "C": "none", "D": "both"}',
            "reponse_correcte": "D",
            "points": 10,
            "difficulte": "facile",
            "explication": "clear: both; empêche les éléments flottants des deux côtés.",
            "mode_specifique": "audio"
        },
        
        
        {
            "question": "Quel est le comportement par défaut de la propriété float ?",
            "options": '{"A": "left", "B": "right", "C": "none", "D": "both"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "float: none; est la valeur par défaut, aucun flottement n'est appliqué.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment résoudre le problème d'effondrement d'un conteneur parent d'éléments flottants ?",
            "options": '{"A": "Ajouter overflow: hidden", "B": "Utiliser la technique clearfix", "C": "Ajouter clear: both en fin de conteneur", "D": "Toutes ces réponses"}',
            "reponse_correcte": "D",
            "points": 15,
            "difficulte": "moyen",
            "explication": "Plusieurs solutions existent : overflow: hidden, clearfix::after, ou un élément avec clear: both.",
            "mode_specifique": "video"
        },
        {
            "question": "Que signifie la technique 'clearfix' ?",
            "options": '{"A": "Une technique pour fixer la hauteur des conteneurs flottants", "B": "Une propriété CSS pour centrer les éléments", "C": "Une méthode pour supprimer les flottements", "D": "Un sélecteur CSS pour les flottants"}',
            "reponse_correcte": "A",
            "points": 15,
            "difficulte": "moyen",
            "explication": "Clearfix est une technique qui empêche les conteneurs parents de s'effondrer quand ils contiennent des éléments flottants.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle est la principale limitation de float pour les mises en page modernes ?",
            "options": '{"A": "Il ne fonctionne pas sur mobile", "B": "Il est plus lent que Flexbox", "C": "Il nécessite des clear pour éviter les problèmes d\'alignement", "D": "Il ne supporte pas les images"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "Float nécessite de gérer les clear pour éviter que les éléments ne s'empilent mal.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle alternative moderne est préférable à float pour les mises en page complexes ?",
            "options": '{"A": "position", "B": "Flexbox ou Grid", "C": "display: block", "D": "text-align"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Pour les mises en page complexes, Flexbox et Grid sont préférables à float.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment faire pour que le texte ne s'enroule pas autour d'une image flottante ?",
            "options": '{"A": "Ajouter clear: both à l\'image", "B": "Ajouter clear: both au paragraphe suivant", "C": "Utiliser float: none", "D": "Ajouter overflow: hidden"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "clear: both sur l'élément suivant empêche l'enroulement autour de l'image flottante.",
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
    print("🎓 INSERTION DU COURS: CSS FLOAT")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    cours_id = inserer_cours_css_float()
    
    if cours_id:
        inserer_questions_css_float(cours_id)
        print(f"\n🎉 Succès ! Cours 'CSS Float - Positionner les Éléments' créé (ID: {cours_id})")
    else:
        print("\n❌ Échec de l'insertion")

if __name__ == "__main__":
    main()