
import psycopg2
import json
from datetime import datetime

def get_connection():
    """Établir la connexion à PostgreSQL"""
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
    """Trouver l'utilisateur admin"""
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

def get_chapitre_id(chapitre_titre):
    """Récupérer l'ID du chapitre par son titre exact"""
    try:
        conn = get_connection()
        if not conn:
            return None
        
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM chapitres WHERE id = 2 OR titre ILIKE %s", (f'%{chapitre_titre}%',))
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result:
            chapitre_id = result[0]
            print(f"📚 Chapitre trouvé: ID {chapitre_id}")
            return chapitre_id
        return None
    except Exception as e:
        print(f"⚠️ Erreur récupération chapitre: {e}")
        return None

def inserer_cours_css_background_images():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    
    chapitre_id = get_chapitre_id("CSS")
    if chapitre_id:
        print(f"📚 Chapitre CSS trouvé (ID: {chapitre_id})")
    else:
        print("⚠️ Chapitre CSS non trouvé, le cours sera inséré sans chapitre")
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    
    slug_cours = "css-background-images"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    
    contenu_html = """
    <h1>🖼️ CSS Background Images - Guide Complet</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Les images d'arrière-plan permettent d'ajouter des visuels attrayants derrière le contenu de vos pages web. CSS offre de nombreuses propriétés pour contrôler leur apparence et leur comportement.</p>
    </div>
    
    <h2>Introduction aux Images d'Arrière-plan</h2>
    <p>La propriété <code>background-image</code> permet de définir une image comme arrière-plan d'un élément HTML. Les images d'arrière-plan peuvent être utilisées sur n'importe quel élément (page entière, sections, cartes, etc.) et offrent une grande flexibilité de design.</p>
    
    <div class="tip-box">
        <p><strong>💡 Astuce :</strong> Les images d'arrière-plan ne font pas partie du flux du contenu - elles restent derrière le texte et les autres éléments.</p>
    </div>
    
    <h2>1. Application d'une image d'arrière-plan</h2>
    <p>La syntaxe de base utilise <code>background-image: url("chemin_de_l_image");</code></p>
    
    <h3>Exemple :</h3>
    <pre><code>/* Image d'arrière-plan pour toute la page */
body {
    background-image: url("fond-etoile.jpg");
}

/* Image d'arrière-plan pour une section spécifique */
.hero-section {
    background-image: url("banniere.jpg");
}

/* Image d'arrière-plan pour une carte */
.card {
    background-image: url("pattern.png");
}</code></pre>
    
    <div class="warning-box">
        <p><strong>⚠️ Important :</strong> Le chemin de l'image peut être relatif (url('images/mon-image.jpg')) ou absolu (url('https://exemple.com/image.jpg')).</p>
    </div>
    
    <h2>2. Contrôle de la répétition (background-repeat)</h2>
    <p>Par défaut, les images d'arrière-plan se répètent horizontalement et verticalement pour remplir tout l'élément. La propriété <code>background-repeat</code> permet de contrôler ce comportement.</p>
    
    <h3>Valeurs possibles :</h3>
    <ul>
        <li><strong>repeat</strong> : Par défaut - répète dans les deux directions</li>
        <li><strong>repeat-x</strong> : Répète uniquement horizontalement</li>
        <li><strong>repeat-y</strong> : Répète uniquement verticalement</li>
        <li><strong>no-repeat</strong> : Pas de répétition (image unique)</li>
    </ul>
    
    <h3>Exemples :</h3>
    <pre><code>/* Pas de répétition - image unique */
.header {
    background-image: url("logo.png");
    background-repeat: no-repeat;
}

/* Répétition horizontale seulement */
.divider {
    background-image: url("pattern-ligne.png");
    background-repeat: repeat-x;
}

/* Répétition verticale seulement */
.sidebar {
    background-image: url("border-vertical.png");
    background-repeat: repeat-y;
}</code></pre>
    
    <h2>3. Positionnement (background-position)</h2>
    <p>La propriété <code>background-position</code> permet de contrôler l'emplacement de l'image d'arrière-plan.</p>
    
    <h3>Valeurs possibles :</h3>
    <ul>
        <li><strong>Mots-clés</strong> : top, bottom, left, right, center</li>
        <li><strong>Pourcentages</strong> : 0% à 100%</li>
        <li><strong>Longueurs</strong> : px, em, rem, etc.</li>
    </ul>
    
    <h3>Exemples :</h3>
    <pre><code>/* Position centrée */
.hero {
    background-image: url("hero.jpg");
    background-repeat: no-repeat;
    background-position: center;
}

/* Position en haut à droite */
.header {
    background-image: url("logo.png");
    background-repeat: no-repeat;
    background-position: top right;
}

/* Position avec pourcentages */
.card {
    background-image: url("image.jpg");
    background-repeat: no-repeat;
    background-position: 20% 80%;
}

/* Position avec valeurs exactes */
.section {
    background-image: url("pattern.png");
    background-repeat: repeat-x;
    background-position: 50px 0;
}</code></pre>
    
    <h2>4. Dimensionnement (background-size)</h2>
    <p>La propriété <code>background-size</code> contrôle la taille de l'image d'arrière-plan. C'est une propriété essentielle pour le responsive design.</p>
    
    <h3>Valeurs possibles :</h3>
    <ul>
        <li><strong>cover</strong> : Redimensionne l'image pour couvrir entièrement l'élément (peut rogner)</li>
        <li><strong>contain</strong> : Redimensionne l'image pour qu'elle soit entièrement visible (peut laisser des espaces)</li>
        <li><strong>largeur hauteur</strong> : Dimensions spécifiques en pixels ou pourcentages</li>
        <li><strong>auto</strong> : Taille originale</li>
    </ul>
    
    <h3>Exemples :</h3>
    <pre><code>/* Cover - idéal pour les héros et bannières */
.hero {
    background-image: url("paysage.jpg");
    background-size: cover;
    background-position: center;
}

/* Contain - image entièrement visible */
.gallery {
    background-image: url("oeuvre.jpg");
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
}

/* Dimensions spécifiques */
.thumbnail {
    background-image: url("miniature.jpg");
    background-size: 150px 100px;
    background-repeat: no-repeat;
}

/* Pourcentage de l'élément */
.section {
    background-image: url("pattern.png");
    background-size: 50% auto;
    background-repeat: repeat;
}</code></pre>
    
    <div class="tip-box">
        <p><strong>💡 Astuce :</strong> <code>background-size: cover</code> est parfait pour les images pleine largeur qui doivent toujours remplir l'espace, tandis que <code>contain</code> est idéal pour préserver l'intégralité d'une image.</p>
    </div>
    
    <h2>5. Combinaison avec couleurs (background-color)</h2>
    <p>Vous pouvez combiner une couleur d'arrière-plan avec une image. La couleur sert alors de fallback pendant le chargement ou si l'image est transparente.</p>
    
    <h3>Exemples :</h3>
    <pre><code>/* Couleur de secours */
.hero {
    background-color: #333;
    background-image: url("hero.jpg");
    background-size: cover;
}

/* Superposition avec image semi-transparente */
.card {
    background-color: rgba(0, 0, 0, 0.5);
    background-image: url("overlay.png");
    background-blend-mode: overlay;
}

/* Dégradé combiné avec image */
.header {
    background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("fond.jpg");
    background-size: cover;
    background-position: center;
}</code></pre>
    
    <h2>6. Propriété raccourcie (background)</h2>
    <p>La propriété <code>background</code> permet de regrouper toutes les propriétés d'arrière-plan en une seule ligne.</p>
    
    <h3>Syntaxe :</h3>
    <pre><code>background: color image repeat position / size;</code></pre>
    
    <h3>Exemples :</h3>
    <pre><code>/* Version complète */
body {
    background: #f0f0f0 url("pattern.png") repeat-x center top / auto;
}

/* Version plus simple */
.hero {
    background: url("hero.jpg") no-repeat center / cover;
}

/* Sans image */
.card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}</code></pre>
    
    <h2>7. Multiple arrière-plans</h2>
    <p>CSS permet d'utiliser plusieurs images d'arrière-plan sur le même élément, séparées par des virgules.</p>
    
    <h3>Exemple :</h3>
    <pre><code>/* Deux images superposées */
.hero {
    background-image: url("pattern.png"), url("hero.jpg");
    background-repeat: repeat, no-repeat;
    background-position: top left, center;
    background-size: auto, cover;
}

/* Version raccourcie */
.section {
    background: url("overlay.png") repeat, url("fond.jpg") no-repeat center / cover;
}</code></pre>
    
    <h2>8. Images d'arrière-plan responsives</h2>
    <p>Voici les bonnes pratiques pour des arrière-plans responsifs :</p>
    
    <pre><code>/* Hero section responsive */
.hero {
    background-image: url("hero-mobile.jpg");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}

/* Media query pour desktop */
@media (min-width: 768px) {
    .hero {
        background-image: url("hero-desktop.jpg");
    }
}

/* Pattern responsive */
.pattern {
    background-image: url("pattern.svg");
    background-size: 30px 30px;
    background-repeat: repeat;
}</code></pre>
    
    <h2>9. Exemple complet</h2>
    
    <h3>HTML :</h3>
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;link rel="stylesheet" href="background.css"&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;div class="hero"&gt;
        &lt;h1&gt;Bienvenue sur mon site&lt;/h1&gt;
        &lt;p&gt;Découvrez nos services exceptionnels&lt;/p&gt;
        &lt;button&gt;En savoir plus&lt;/button&gt;
    &lt;/div&gt;
    
    &lt;div class="cards"&gt;
        &lt;div class="card service1"&gt;
            &lt;h3&gt;Service Premium&lt;/h3&gt;
            &lt;p&gt;Description du service&lt;/p&gt;
        &lt;/div&gt;
        &lt;div class="card service2"&gt;
            &lt;h3&gt;Service Express&lt;/h3&gt;
            &lt;p&gt;Description du service&lt;/p&gt;
        &lt;/div&gt;
    &lt;/div&gt;
    
    &lt;div class="cta"&gt;
        &lt;h2&gt;Prêt à commencer ?&lt;/h2&gt;
        &lt;button&gt;Contactez-nous&lt;/button&gt;
    &lt;/div&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h3>CSS (background.css) :</h3>
    <pre><code>/* Hero section avec image pleine largeur */
.hero {
    background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('hero-bg.jpg');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    height: 500px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    color: white;
    text-align: center;
}

/* Cartes avec icônes d'arrière-plan */
.card {
    padding: 30px;
    border-radius: 10px;
    color: white;
    height: 200px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.service1 {
    background-image: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.service2 {
    background-image: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

/* Section CTA avec pattern */
.cta {
    background-color: #2c3e50;
    background-image: url('pattern-dots.png');
    background-repeat: repeat;
    text-align: center;
    padding: 80px 20px;
    color: white;
}</code></pre>
    
    <h2>10. Bonnes pratiques</h2>
    
    <ul>
        <li><strong>Optimisez vos images</strong> : Compressez vos images d'arrière-plan pour améliorer les performances</li>
        <li><strong>Utilisez des couleurs de fallback</strong> : Toujours définir une couleur d'arrière-plan de secours</li>
        <li><strong>Privilégiez background-size: cover</strong> pour les grandes sections et hero banners</li>
        <li><strong>Testez sur mobile</strong> : Assurez-vous que les images s'affichent correctement sur tous les appareils</li>
        <li><strong>Évitez les images trop chargées</strong> : Préférez des motifs simples ou des dégradés si possible</li>
        <li><strong>Utilisez des media queries</strong> pour charger des images différentes selon l'appareil</li>
        <li><strong>Pensez à l'accessibilité</strong> : Assurez un bon contraste entre l'arrière-plan et le texte</li>
    </ul>
    
    <div class="tip-box">
        <p><strong>💡 Astuce :</strong> Utilisez des outils comme TinyPNG ou Squoosh pour compresser vos images d'arrière-plan sans perdre en qualité.</p>
    </div>
    
    <h2>11. Exercice pratique</h2>
    <p>Créez une page web avec les caractéristiques suivantes :</p>
    <ol>
        <li>Un hero section avec une image d'arrière-plan en cover et un dégradé sombre par-dessus</li>
        <li>Une section avec un motif (pattern) qui se répète</li>
        <li>Plusieurs cartes avec des images d'arrière-plan différentes</li>
        <li>Une image d'arrière-plan qui ne se répète pas et est positionnée en bas à droite</li>
        <li>Utilisez background-size: contain pour une image</li>
    </ol>
    
    <div class="info-box">
        <p><strong>💡 Conseil :</strong> Utilisez des images de haute qualité mais optimisées. Les images d'arrière-plan peuvent grandement améliorer le design d'un site quand elles sont bien utilisées.</p>
    </div>
    """.strip()
    
    
    cours_data = {
        "titre": "CSS Background Images - Images d'Arrière-plan",
        "slug": slug_cours,
        "description": "Apprenez à utiliser les images d'arrière-plan en CSS pour enrichir vos pages web. Découvrez les propriétés background-image, background-repeat, background-position, background-size, et comment combiner images et couleurs pour des designs professionnels.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 25,
        "ordre_affichage": 19,
        "chapitre_id": chapitre_id,  
        "tags": ["css", "background", "background-image", "background-repeat", "background-position", "background-size", "cover", "contain", "images", "web design", "debutant"],
        "est_actif": True,
        "created_by": admin_id,
        "last_modified_by": admin_id
    }
    
    if existing:
        cours_id = existing[0]
        print(f"⚠️ Le cours avec le slug '{slug_cours}' existe déjà (ID: {cours_id})")
        
        
        cur.execute("""
            UPDATE cours_html 
            SET titre = %s, description = %s, contenu_texte = %s, 
                difficulte = %s, duree_estimee = %s, ordre_affichage = %s,
                chapitre_id = %s, tags = %s, est_actif = %s, last_modified_by = %s,
                date_maj = CURRENT_TIMESTAMP
            WHERE slug = %s
            RETURNING id
        """, (
            cours_data["titre"],
            cours_data["description"],
            cours_data["contenu_texte"],
            cours_data["difficulte"],
            cours_data["duree_estimee"],
            cours_data["ordre_affichage"],
            cours_data["chapitre_id"],
            cours_data["tags"],
            cours_data["est_actif"],
            cours_data["last_modified_by"],
            slug_cours
        ))
        
        cours_id = cur.fetchone()[0]
        print(f"✅ Cours mis à jour (ID: {cours_id})")
        if chapitre_id:
            print(f"   📚 Associé au chapitre CSS (ID: {chapitre_id})")
    else:
        
        cur.execute("""
            INSERT INTO cours_html 
            (titre, slug, description, contenu_texte, difficulte, 
             duree_estimee, ordre_affichage, chapitre_id, tags, est_actif, 
             created_by, date_creation, date_maj, last_modified_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, %s)
            RETURNING id
        """, (
            cours_data["titre"],
            cours_data["slug"],
            cours_data["description"],
            cours_data["contenu_texte"],
            cours_data["difficulte"],
            cours_data["duree_estimee"],
            cours_data["ordre_affichage"],
            cours_data["chapitre_id"],
            cours_data["tags"],
            cours_data["est_actif"],
            cours_data["created_by"],
            cours_data["last_modified_by"]
        ))
        
        cours_id = cur.fetchone()[0]
        print(f"✅ Cours créé (ID: {cours_id})")
        if chapitre_id:
            print(f"   📚 Associé au chapitre CSS (ID: {chapitre_id})")
    
    conn.commit()
    return cours_id

def inserer_questions_css_background_images(cours_id):
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    
    questions = [
        {
            "question": "Quelle propriété CSS permet de définir une image d'arrière-plan ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "image-background",
                "B": "background-image",
                "C": "bg-image",
                "D": "img-background"
            },
            "reponse_correcte": "B",
            "explication": "La propriété 'background-image' permet de définir une image comme arrière-plan d'un élément.",
            "mode_specifique": "texte"
        },
        {
            "question": "Comment empêcher une image d'arrière-plan de se répéter ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "background-repeat: repeat",
                "B": "background-repeat: once",
                "C": "background-repeat: no-repeat",
                "D": "background-repeat: none"
            },
            "reponse_correcte": "C",
            "explication": "background-repeat: no-repeat empêche l'image de se répéter.",
            "mode_specifique": "video"
        },
        {
            "question": "Que signifie background-size: cover ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "L'image est affichée en taille réelle",
                "B": "L'image couvre entièrement l'élément (peut être rognée)",
                "C": "L'image est réduite à 50%",
                "D": "L'image est agrandie à 200%"
            },
            "reponse_correcte": "B",
            "explication": "cover redimensionne l'image pour couvrir entièrement l'élément, même si cela signifie rogner certaines parties.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle propriété contrôle la position d'une image d'arrière-plan ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "background-location",
                "B": "background-align",
                "C": "background-position",
                "D": "background-place"
            },
            "reponse_correcte": "C",
            "explication": "background-position contrôle l'emplacement de l'image d'arrière-plan.",
            "mode_specifique": "video"
        },
        {
            "question": "Que fait background-repeat: repeat-x ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "Répète l'image verticalement seulement",
                "B": "Répète l'image horizontalement seulement",
                "C": "Répète l'image dans les deux directions",
                "D": "Ne répète pas l'image"
            },
            "reponse_correcte": "B",
            "explication": "repeat-x répète l'image uniquement horizontalement (de gauche à droite).",
            "mode_specifique": "texte"
        },
        {
            "question": "Quelle est la différence entre background-size: cover et contain ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "cover remplit l'élément (peut rogner), contain montre l'image entière (peut laisser des espaces)",
                "B": "cover et contain font la même chose",
                "C": "contain remplit l'élément, cover montre l'image entière",
                "D": "cover est pour mobile, contain pour desktop"
            },
            "reponse_correcte": "A",
            "explication": "cover remplit entièrement l'élément (peut rogner), contain montre l'image entière (peut laisser des espaces vides).",
            "mode_specifique": "video"
        },
        {
            "question": "Pourquoi est-il important de définir une couleur d'arrière-plan avec une image ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "Pour améliorer les performances",
                "B": "Comme fallback si l'image ne charge pas",
                "C": "Pour que l'image soit plus belle",
                "D": "C'est obligatoire"
            },
            "reponse_correcte": "B",
            "explication": "La couleur d'arrière-plan sert de fallback pendant le chargement ou si l'image ne peut pas être chargée.",
            "mode_specifique": "audio"
        },
        {
            "question": "Comment centrer une image d'arrière-plan ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "background-position: middle",
                "B": "background-position: center",
                "C": "background-align: center",
                "D": "background-pos: 50%"
            },
            "reponse_correcte": "B",
            "explication": "background-position: center centre l'image d'arrière-plan horizontalement et verticalement.",
            "mode_specifique": "texte"
        },
        {
            "question": "Comment appliquer plusieurs images d'arrière-plan sur le même élément ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "difficile",
            "options": {
                "A": "Impossible en CSS",
                "B": "En séparant les images par des virgules",
                "C": "En utilisant plusieurs propriétés background-image",
                "D": "Avec la propriété background-stack"
            },
            "reponse_correcte": "B",
            "explication": "On peut utiliser plusieurs images en les séparant par des virgules dans background-image.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle propriété permet de contrôler la taille d'une image d'arrière-plan ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "background-size",
                "B": "background-dimension",
                "C": "image-size",
                "D": "bg-size"
            },
            "reponse_correcte": "A",
            "explication": "background-size contrôle la taille de l'image d'arrière-plan.",
            "mode_specifique": "audio"
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
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (
                cours_id,
                q["question"],
                q["type_question"],
                q["points"],
                q["difficulte"],
                json.dumps(q["options"]),
                q["reponse_correcte"],
                q["explication"],
                q["mode_specifique"],
                admin_id
            ))
            
            questions_creees += 1
            print(f"  ✅ Question créée: {q['question'][:50]}...")
            
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"\n📊 RÉSUMÉ:")
    print(f"   • Questions créées: {questions_creees}")
    print(f"   • Questions existantes: {questions_existantes}")
    
    return True

def lister_cours_et_chapitres():
    
    try:
        conn = get_connection()
        if not conn:
            return
        
        cur = conn.cursor()
        
        cur.execute("""
            SELECT c.id, c.titre, c.slug, c.difficulte, ch.titre as chapitre_titre
            FROM cours_html c
            LEFT JOIN chapitres ch ON c.chapitre_id = ch.id
            WHERE c.est_actif = true
            ORDER BY ch.ordre_affichage, c.ordre_affichage
        """)
        
        cours = cur.fetchall()
        
        print("\n" + "=" * 80)
        print("📚 LISTE DES COURS AVEC LEURS CHAPITRES")
        print("=" * 80)
        
        current_chapitre = None
        for c in cours:
            if c[4] != current_chapitre:
                current_chapitre = c[4]
                print(f"\n📖 {current_chapitre or 'Sans chapitre'}")
                print("-" * 40)
            print(f"   [{c[3]}] {c[1]}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    print("\n" + "=" * 60)
    print("🎓 INSERTION DU COURS: CSS BACKGROUND IMAGES")
    print("(Images d'Arrière-plan CSS)")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    chapitre_id = get_chapitre_id("CSS")
    if chapitre_id:
        print(f"📚 Chapitre CSS trouvé (ID: {chapitre_id})")
    else:
        print("⚠️ Chapitre CSS non trouvé, le cours sera inséré sans chapitre")
    
    
    cours_id = inserer_cours_css_background_images()
    
    if cours_id:
        
        inserer_questions_css_background_images(cours_id)
        
        print(f"\n🎉 Succès ! Le cours 'CSS Background Images - Images d'Arrière-plan' a été inséré avec succès!")
        print(f"   📚 Cours ID: {cours_id}")
        
        
        lister_cours_et_chapitres()
    else:
        print("\n❌ Échec de l'insertion du cours")

if __name__ == "__main__":
    main()