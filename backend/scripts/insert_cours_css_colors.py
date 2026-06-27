
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

def get_chapitre_id(chapitre_titre):
    
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

def inserer_cours_css_colors():
    
    
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
    
    
    slug_cours = "css-couleurs"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    
    contenu_html = """
    <h1>🎨 CSS Couleurs - Guide Complet</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Les couleurs sont essentielles en CSS pour donner vie à vos pages web. CSS offre plusieurs façons de définir et manipuler les couleurs pour le texte, les arrière-plans, les bordures et bien plus encore.</p>
    </div>
    
    <h2>Introduction aux Couleurs en CSS</h2>
    <p>CSS permet d'appliquer des couleurs à presque tous les éléments d'une page web : texte, arrière-plan, bordures, ombres, etc. Il existe plusieurs formats pour définir une couleur, chacun ayant ses avantages.</p>
    
    <div class="tip-box">
        <p><strong>💡 Astuce :</strong> La maîtrise des couleurs est fondamentale pour créer des designs web attrayants et accessibles.</p>
    </div>
    
    <h2>1. Les noms de couleurs (Color Names)</h2>
    <p>CSS supporte 140 noms de couleurs standards, comme red, blue, green, yellow, etc. C'est le format le plus simple à retenir pour les couleurs de base.</p>
    
    <pre><code>/* Exemples de noms de couleurs */
p {
    color: red;           /* Texte rouge */
}

body {
    background-color: lightblue;  /* Fond bleu clair */
}

h1 {
    color: darkgreen;     /* Titre vert foncé */
}

.border-example {
    border: 2px solid orange;   /* Bordure orange */
}</code></pre>
    
    <h3>Couleurs courantes :</h3>
    <ul>
        <li><span style="color: red;">red</span> - Rouge</li>
        <li><span style="color: blue;">blue</span> - Bleu</li>
        <li><span style="color: green;">green</span> - Vert</li>
        <li><span style="color: yellow;">yellow</span> - Jaune</li>
        <li><span style="color: orange;">orange</span> - Orange</li>
        <li><span style="color: purple;">purple</span> - Violet</li>
        <li><span style="color: pink;">pink</span> - Rose</li>
        <li><span style="color: gray;">gray</span> - Gris</li>
        <li><span style="color: black;">black</span> - Noir</li>
        <li><span style="color: white;">white</span> - Blanc</li>
    </ul>
    
    <div class="info-box">
        <p><strong>📝 Note :</strong> Les noms de couleurs sont faciles à retenir mais limités en nombre. Pour des couleurs plus précises, utilisez HEX, RGB ou HSL.</p>
    </div>
    
    <h2>2. Les codes HEX (Hexadécimal)</h2>
    <p>Le format HEX utilise 6 caractères hexadécimaux (0-9, A-F) précédés d'un # pour définir une couleur. C'est le format le plus utilisé en web design.</p>
    
    <h3>Structure :</h3>
    <pre><code>#RRGGBB
 Où :
 - RR = rouge (00 à FF)
 - GG = vert (00 à FF)
 - BB = bleu (00 à FF)</code></pre>
    
    <h3>Exemples :</h3>
    <pre><code>/* Couleurs HEX */
h1 {
    color: #FF0000;      /* Rouge pur */
}

p {
    color: #00FF00;      /* Vert pur */
}

a {
    color: #0000FF;      /* Bleu pur */
}

.background-dark {
    background-color: #333333;  /* Gris foncé */
}

.text-light {
    color: #FFFFFF;      /* Blanc */
}

/* Format raccourci (3 caractères) */
.text-soft {
    color: #F00;         /* Équivalent à #FF0000 */
}

.card {
    background-color: #CCC;     /* Équivalent à #CCCCCC */
}</code></pre>
    
    <h3>Exemples de couleurs HEX courantes :</h3>
    <ul>
        <li><span style="color: #FF0000;">#FF0000</span> - Rouge</li>
        <li><span style="color: #00FF00;">#00FF00</span> - Vert</li>
        <li><span style="color: #0000FF;">#0000FF</span> - Bleu</li>
        <li><span style="color: #FFFF00;">#FFFF00</span> - Jaune</li>
        <li><span style="color: #000000;">#000000</span> - Noir</li>
        <li><span style="color: #FFFFFF;">#FFFFFF</span> - Blanc</li>
        <li><span style="color: #FFA500;">#FFA500</span> - Orange</li>
        <li><span style="color: #800080;">#800080</span> - Violet</li>
    </ul>
    
    <h2>3. Les valeurs RGB (Red, Green, Blue)</h2>
    <p>RGB définit une couleur par un mélange de rouge, vert et bleu, chaque valeur étant comprise entre 0 et 255.</p>
    
    <h3>Syntaxe :</h3>
    <pre><code>rgb(rouge, vert, bleu)</code></pre>
    
    <h3>Exemples :</h3>
    <pre><code>/* RGB */
button {
    background-color: rgb(255, 0, 0);    /* Rouge */
}

.secondary {
    color: rgb(0, 255, 0);               /* Vert */
}

.card {
    border-color: rgb(0, 0, 255);        /* Bleu */
}

.dark-bg {
    background-color: rgb(51, 51, 51);   /* Gris foncé */
}

/* RGB avec opacité (RGBA) */
.transparent-bg {
    background-color: rgba(255, 0, 0, 0.5); /* Rouge semi-transparent */
}

.overlay {
    background-color: rgba(0, 0, 0, 0.3);   /* Noir semi-transparent */
}</code></pre>
    
    <div class="tip-box">
        <p><strong>💡 Astuce :</strong> RGBA ajoute un quatrième paramètre pour l'opacité (0 = transparent, 1 = opaque).</p>
    </div>
    
    <h2>4. Les valeurs HSL (Hue, Saturation, Lightness)</h2>
    <p>HSL est un format plus intuitif qui définit la couleur par sa teinte (0-360°), sa saturation (0-100%) et sa luminosité (0-100%).</p>
    
    <h3>Syntaxe :</h3>
    <pre><code>hsl(teinte, saturation, luminosité)</code></pre>
    
    <h3>Composition :</h3>
    <ul>
        <li><strong>Teinte (Hue)</strong> : Angle sur le cercle chromatique (0° = rouge, 120° = vert, 240° = bleu)</li>
        <li><strong>Saturation</strong> : Intensité de la couleur (0% = gris, 100% = couleur pure)</li>
        <li><strong>Luminosité (Lightness)</strong> : Clarté de la couleur (0% = noir, 50% = normal, 100% = blanc)</li>
    </ul>
    
    <h3>Exemples :</h3>
    <pre><code>/* HSL */
.element {
    color: hsl(0, 100%, 50%);        /* Rouge vif */
}

.success {
    background-color: hsl(120, 100%, 50%);  /* Vert vif */
}

.warning {
    background-color: hsl(60, 100%, 50%);   /* Jaune vif */
}

.pastel {
    background-color: hsl(200, 50%, 70%);   /* Bleu pastel */
}

/* HSL avec opacité (HSLA) */
.transparent {
    background-color: hsla(240, 100%, 50%, 0.5); /* Bleu semi-transparent */
}</code></pre>
    
    <div class="info-box">
        <p><strong>💡 Avantage de HSL :</strong> Permet de créer facilement des variations de couleurs (plus claires/plus foncées) en ajustant simplement la luminosité.</p>
    </div>
    
    <h2>5. Propriétés CSS pour les couleurs</h2>
    
    <h3>color - Couleur du texte :</h3>
    <pre><code>p {
    color: navy;
}</code></pre>
    
    <h3>background-color - Couleur d'arrière-plan :</h3>
    <pre><code>body {
    background-color: #F0F0F0;
}</code></pre>
    
    <h3>border-color - Couleur des bordures :</h3>
    <pre><code>div {
    border: 2px solid rgb(255, 99, 71);
}</code></pre>
    
    <h3>outline-color - Couleur du contour :</h3>
    <pre><code>input:focus {
    outline-color: hsl(200, 100%, 50%);
}</code></pre>
    
    <h2>6. Exemple complet</h2>
    
    <h3>HTML :</h3>
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;link rel="stylesheet" href="colors.css"&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;h1&gt;Bienvenue sur mon site&lt;/h1&gt;
    
    &lt;div class="card"&gt;
        &lt;h2&gt;Carte de présentation&lt;/h2&gt;
        &lt;p&gt;Ceci est un exemple de carte avec des couleurs CSS.&lt;/p&gt;
        &lt;button class="btn"&gt;En savoir plus&lt;/button&gt;
    &lt;/div&gt;
    
    &lt;div class="colors-demo"&gt;
        &lt;div class="color-box hex"&gt;HEX #FF5722&lt;/div&gt;
        &lt;div class="color-box rgb"&gt;RGB rgb(33, 150, 243)&lt;/div&gt;
        &lt;div class="color-box hsl"&gt;HSL hsl(120, 60%, 70%)&lt;/div&gt;
    &lt;/div&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h3>CSS (colors.css) :</h3>
    <pre><code>/* Variables de couleurs */
:root {
    --primary-color: #3498db;
    --secondary-color: #2ecc71;
    --danger-color: #e74c3c;
    --dark-color: #2c3e50;
    --light-color: #ecf0f1;
}

/* Styles généraux */
body {
    font-family: Arial, sans-serif;
    background-color: var(--light-color);
    color: var(--dark-color);
}

h1 {
    color: var(--primary-color);
    text-align: center;
}

/* Carte */
.card {
    background-color: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 20px;
    margin: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Bouton */
.btn {
    background-color: var(--secondary-color);
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
}

.btn:hover {
    background-color: rgb(37, 155, 89);
}

/* Démonstration des couleurs */
.colors-demo {
    display: flex;
    gap: 15px;
    margin: 20px;
}

.color-box {
    padding: 20px;
    border-radius: 8px;
    text-align: center;
    color: white;
    font-weight: bold;
}

.color-box.hex {
    background-color: #FF5722;
}

.color-box.rgb {
    background-color: rgb(33, 150, 243);
}

.color-box.hsl {
    background-color: hsl(120, 60%, 40%);
}</code></pre>
    
    <h2>7. Bonnes pratiques</h2>
    
    <ul>
        <li><strong>Utilisez des variables CSS</strong> pour les couleurs réutilisables (thèmes)</li>
        <li><strong>Assurez un bon contraste</strong> entre le texte et l'arrière-plan (accessibilité)</li>
        <li><strong>Préférez HEX ou RGB</strong> pour les couleurs précises, <strong>HSL</strong> pour les variations</li>
        <li><strong>Testez vos couleurs</strong> sur différents écrans et pour le daltonisme</li>
        <li><strong>Documentez vos couleurs</strong> (noms, signification) pour la maintenance</li>
    </ul>
    
    <div class="warning-box">
        <p><strong>⚠️ Accessibilité :</strong> Assurez-vous que le contraste entre le texte et l'arrière-plan est suffisant pour les utilisateurs malvoyants (ratio minimum 4.5:1).</p>
    </div>
    
    <h2>8. Exercice pratique</h2>
    <p>Créez une page web avec les caractéristiques suivantes :</p>
    <ol>
        <li>Un titre principal avec une couleur de votre choix (HEX)</li>
        <li>Un paragraphe avec une couleur différente (nom de couleur)</li>
        <li>Un bouton avec un fond RGB et un texte blanc</li>
        <li>Une carte avec un fond HSL et une bordure</li>
        <li>Un effet au survol qui assombrit légèrement les éléments (utilisez rgba ou hsla)</li>
    </ol>
    
    <div class="info-box">
        <p><strong>💡 Conseil :</strong> Utilisez des outils en ligne comme Coolors.co ou Adobe Color pour générer des palettes de couleurs harmonieuses.</p>
    </div>
    """.strip()
    
    
    cours_data = {
        "titre": "CSS Couleurs - Noms, HEX, RGB, HSL",
        "slug": slug_cours,
        "description": "Apprenez à utiliser les couleurs en CSS pour donner vie à vos pages web. Découvrez les différents formats : noms de couleurs, codes HEX, valeurs RGB et HSL. Apprenez à appliquer des couleurs au texte, aux arrière-plans et aux bordures.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 20,
        "ordre_affichage": 18,
        "chapitre_id": chapitre_id,  
        "tags": ["css", "couleurs", "colors", "hex", "rgb", "hsl", "rgba", "hsla", "web design", "accessibilite", "debutant"],
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

def inserer_questions_css_colors(cours_id):
    
    
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
            "question": "Quels sont les différents formats pour définir une couleur en CSS ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "Uniquement les noms de couleurs",
                "B": "Noms de couleurs, HEX, RGB, HSL",
                "C": "Uniquement HEX et RGB",
                "D": "Uniquement les codes HEX"
            },
            "reponse_correcte": "B",
            "explication": "CSS offre plusieurs formats : les noms de couleurs (red), les codes HEX (#FF0000), RGB (rgb(255,0,0)) et HSL (hsl(0,100%,50%)).",
            "mode_specifique": "texte"
        },
        {
            "question": "Que signifie le code HEX #FF0000 ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "Vert",
                "B": "Bleu",
                "C": "Rouge",
                "D": "Jaune"
            },
            "reponse_correcte": "C",
            "explication": "#FF0000 représente le rouge pur (FF = 255 en hexadécimal pour le rouge, 00 pour le vert et le bleu).",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle est la syntaxe correcte pour RGB en CSS ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "rgb(0-255, 0-255, 0-255)",
                "B": "rgb(0-100, 0-100, 0-100)",
                "C": "rgb(0-1, 0-1, 0-1)",
                "D": "rgb(0-360, 0-100%, 0-100%)"
            },
            "reponse_correcte": "A",
            "explication": "RGB utilise trois valeurs entre 0 et 255 pour représenter l'intensité du rouge, du vert et du bleu.",
            "mode_specifique": "audio"
        },
        {
            "question": "Que permet d'ajouter RGBA par rapport à RGB ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "La luminosité",
                "B": "L'opacité (transparence)",
                "C": "La saturation",
                "D": "La teinte"
            },
            "reponse_correcte": "B",
            "explication": "RGBA ajoute un canal alpha (A) qui contrôle l'opacité, de 0 (transparent) à 1 (opaque).",
            "mode_specifique": "video"
        },
        {
            "question": "Dans HSL, que représente la valeur H (Hue) ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "La saturation (0-100%)",
                "B": "La luminosité (0-100%)",
                "C": "La teinte sur le cercle chromatique (0-360°)",
                "D": "La transparence"
            },
            "reponse_correcte": "C",
            "explication": "Hue (teinte) est un angle sur le cercle chromatique : 0° = rouge, 120° = vert, 240° = bleu.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quelle propriété CSS permet de changer la couleur du texte ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "text-color",
                "B": "font-color",
                "C": "color",
                "D": "background-color"
            },
            "reponse_correcte": "C",
            "explication": "La propriété 'color' définit la couleur du texte en CSS.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment écrire le code HEX pour la couleur blanche ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "#000000",
                "B": "#FFFFFF",
                "C": "#FF0000",
                "D": "#00FF00"
            },
            "reponse_correcte": "B",
            "explication": "#FFFFFF (ou blanc) représente la valeur maximale pour le rouge, le vert et le bleu.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle est la valeur minimale pour un canal RGB ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "1",
                "B": "0",
                "C": "50",
                "D": "100"
            },
            "reponse_correcte": "B",
            "explication": "Dans RGB, chaque valeur peut aller de 0 (absence de couleur) à 255 (pleine intensité).",
            "mode_specifique": "texte"
        },
        {
            "question": "Que signifie HSL ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "moyen",
            "options": {
                "A": "High Saturation Light",
                "B": "Hue, Saturation, Lightness",
                "C": "Hex, Saturation, Lightness",
                "D": "Hue, Saturation, Luminance"
            },
            "reponse_correcte": "B",
            "explication": "HSL signifie Hue (teinte), Saturation (saturation), Lightness (luminosité).",
            "mode_specifique": "video"
        },
        {
            "question": "Pourquoi est-il important d'avoir un bon contraste entre texte et arrière-plan ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "Pour que le site soit plus beau",
                "B": "Pour l'accessibilité des utilisateurs malvoyants",
                "C": "Pour le référencement SEO",
                "D": "Pour accélérer le chargement"
            },
            "reponse_correcte": "B",
            "explication": "Un bon contraste améliore la lisibilité pour tous, en particulier pour les personnes malvoyantes ou daltoniennes.",
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
    print("🎓 INSERTION DU COURS: CSS COULEURS (NOMS, HEX, RGB, HSL)")
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
    
    
    cours_id = inserer_cours_css_colors()
    
    if cours_id:
        
        inserer_questions_css_colors(cours_id)
        
        print(f"\n🎉 Succès ! Le cours 'CSS Couleurs - Noms, HEX, RGB, HSL' a été inséré avec succès!")
        print(f"   📚 Cours ID: {cours_id}")
        
        
        lister_cours_et_chapitres()
    else:
        print("\n❌ Échec de l'insertion du cours")

if __name__ == "__main__":
    main()