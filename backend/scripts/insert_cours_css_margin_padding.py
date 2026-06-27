
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

def inserer_cours_css_margin_padding():
    
    
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
    
    
    slug_cours = "css-margin-padding"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    
    contenu_html = """
    <h1>📐 CSS Margin & Padding - Guide Complet</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Les marges et les paddings sont essentiels pour contrôler l'espacement en CSS. La marge crée de l'espace à l'extérieur de l'élément, tandis que le padding crée de l'espace à l'intérieur, entre le contenu et la bordure.</p>
    </div>
    
    <h2>Introduction aux Marges et Paddings</h2>
    <p>Ces deux propriétés sont fondamentales pour la mise en page CSS :</p>
    <ul>
        <li><strong>Margin (marge)</strong> : Espace à l'extérieur de la bordure, qui pousse l'élément loin des autres éléments</li>
        <li><strong>Padding (remplissage)</strong> : Espace à l'intérieur de la bordure, entre le contenu et la bordure</li>
    </ul>
    
    <div class="tip-box">
        <p><strong>💡 Astuce :</strong> Visualisez chaque élément HTML comme une boîte avec du contenu à l'intérieur. Le padding est l'espace à l'intérieur de la boîte, la marge est l'espace à l'extérieur.</p>
    </div>
    
    <!-- PARTIE 1: MARGIN -->
    <h2>PARTIE 1: CSS MARGIN</h2>
    
    <h2>1. Introduction aux Marges</h2>
    <p>La marge crée de l'espace à l'extérieur de la bordure d'un élément, le poussant loin des autres éléments. Contrairement au padding, la marge est transparente et ne peut pas avoir de couleur d'arrière-plan.</p>
    
    <h3>Différence entre margin et padding :</h3>
    <pre><code>/* Visualisation d'une boîte CSS */
.element {
    margin: 20px;    /* Espace EXTÉRIEUR (transparent) */
    border: 2px solid black;  /* Bordure */
    padding: 10px;   /* Espace INTÉRIEUR (couleur de fond possible) */
    background-color: lightblue; /* La couleur s'applique à l'intérieur de la bordure */
}</code></pre>
    
    <h2>2. Définir les marges individuellement</h2>
    <p>CSS permet de contrôler chaque côté d'un élément indépendamment :</p>
    
    <h3>Propriétés individuelles :</h3>
    <ul>
        <li><strong>margin-top</strong> : Marge supérieure</li>
        <li><strong>margin-right</strong> : Marge droite</li>
        <li><strong>margin-bottom</strong> : Marge inférieure</li>
        <li><strong>margin-left</strong> : Marge gauche</li>
    </ul>
    
    <h3>Exemples :</h3>
    <pre><code>/* Marge supérieure de 10px */
.box {
    margin-top: 10px;
}

/* Marge droite de 20px */
.box {
    margin-right: 20px;
}

/* Marge inférieure de 30px */
.box {
    margin-bottom: 30px;
}

/* Marge gauche de 40px */
.box {
    margin-left: 40px;
}

/* Différentes marges sur chaque côté */
.custom-margin {
    margin-top: 20px;
    margin-right: 15px;
    margin-bottom: 10px;
    margin-left: 5px;
}</code></pre>
    
    <h2>3. La propriété raccourcie margin</h2>
    <p>La propriété <code>margin</code> permet de définir toutes les marges en une seule ligne.</p>
    
    <h3>Différentes syntaxes :</h3>
    <pre><code>/* 1 valeur : appliquée aux 4 côtés */
.margin-one {
    margin: 20px;  /* top, right, bottom, left = 20px */
}

/* 2 valeurs : (top/bottom) et (right/left) */
.margin-two {
    margin: 10px 20px;  /* top/bottom = 10px, right/left = 20px */
}

/* 3 valeurs : top, (right/left), bottom */
.margin-three {
    margin: 10px 20px 30px;  /* top=10px, right/left=20px, bottom=30px */
}

/* 4 valeurs : top, right, bottom, left */
.margin-four {
    margin: 10px 20px 30px 40px;  /* top=10px, right=20px, bottom=30px, left=40px */
}</code></pre>
    
    <h2>4. Auto margins pour centrer les éléments</h2>
    <p>La valeur <code>auto</code> pour les marges est très utile pour centrer horizontalement des éléments block.</p>
    
    <h3>Exemple :</h3>
    <pre><code>/* Centrer un élément block horizontalement */
.center {
    width: 80%;
    margin-left: auto;
    margin-right: auto;
}

/* Version raccourcie */
.center-2 {
    width: 80%;
    margin: 0 auto;  /* top/bottom = 0, left/right = auto */
}</code></pre>
    
    <div class="tip-box">
        <p><strong>💡 Astuce :</strong> <code>margin: 0 auto;</code> est la façon standard de centrer un élément block horizontalement. L'élément doit avoir une largeur définie.</p>
    </div>
    
    <h2>5. Le phénomène de collapse des marges</h2>
    <p>Les marges verticales entre éléments peuvent se "fusionner" (collaps) en une seule marge, prenant la valeur la plus grande des deux.</p>
    
    <h3>Exemples :</h3>
    <pre><code>/* Deux paragraphes avec marges verticales */
p {
    margin-top: 20px;
    margin-bottom: 30px;
}

/* Au lieu d'avoir 50px d'espace total,
   les marges se fusionnent en une seule de 30px (la plus grande) */</code></pre>
    
    <div class="warning-box">
        <p><strong>⚠️ Important :</strong> Le collapse des marges ne s'applique qu'aux marges verticales (top et bottom). Les marges horizontales ne se fusionnent jamais.</p>
    </div>
    
    <h3>Cas particuliers :</h3>
    <ul>
        <li>Les marges d'éléments adjacents se fusionnent</li>
        <li>Les marges d'éléments parents/enfants peuvent se fusionner</li>
        <li>Les marges d'éléments vides peuvent se fusionner</li>
    </ul>
    
    <!-- PARTIE 2: PADDING -->
    <h2>PARTIE 2: CSS PADDING</h2>
    
    <h2>6. Introduction aux Paddings</h2>
    <p>Le padding crée de l'espace à l'intérieur d'un élément, entre son contenu et sa bordure. Contrairement à la marge, le padding peut avoir une couleur d'arrière-plan.</p>
    
    <div class="info-box">
        <p><strong>📝 Note :</strong> Le padding rend l'élément plus spacieux à l'intérieur, alors que la marge l'éloigne des autres éléments.</p>
    </div>
    
    <h2>7. Définir les paddings individuellement</h2>
    
    <h3>Propriétés individuelles :</h3>
    <ul>
        <li><strong>padding-top</strong> : Padding supérieur</li>
        <li><strong>padding-right</strong> : Padding droit</li>
        <li><strong>padding-bottom</strong> : Padding inférieur</li>
        <li><strong>padding-left</strong> : Padding gauche</li>
    </ul>
    
    <h3>Exemples :</h3>
    <pre><code>/* Padding supérieur de 10px */
.card {
    padding-top: 10px;
}

/* Padding droit de 20px */
.card {
    padding-right: 20px;
}

/* Différents paddings */
.custom-padding {
    padding-top: 10px;
    padding-right: 60px;
    padding-bottom: 80px;
    padding-left: 120px;
}</code></pre>
    
    <h2>8. La propriété raccourcie padding</h2>
    <p>Comme pour margin, <code>padding</code> permet de définir tous les paddings en une ligne.</p>
    
    <h3>Différentes syntaxes :</h3>
    <pre><code>/* 1 valeur : appliquée aux 4 côtés */
.padding-one {
    padding: 20px;  /* top, right, bottom, left = 20px */
}

/* 2 valeurs : (top/bottom) et (right/left) */
.padding-two {
    padding: 10px 20px;  /* top/bottom = 10px, right/left = 20px */
}

/* 3 valeurs : top, (right/left), bottom */
.padding-three {
    padding: 10px 20px 30px;  /* top=10px, right/left=20px, bottom=30px */
}

/* 4 valeurs : top, right, bottom, left */
.padding-four {
    padding: 10px 20px 30px 40px;  /* top=10px, right=20px, bottom=30px, left=40px */
}</code></pre>
    
    <h2>9. Unités et pourcentages</h2>
    <p>Les paddings peuvent être définis en différentes unités :</p>
    
    <h3>Exemples :</h3>
    <pre><code>/* Pixels - valeur fixe */
.fixed-padding {
    padding: 20px;
}

/* Pourcentages - relatif à la largeur du parent */
.percentage-padding {
    padding: 10%;  /* 10% de la largeur de l'élément parent */
}

/* EMs - relatif à la taille de police */
.em-padding {
    padding: 2em;  /* 2x la taille de police de l'élément */
}

/* Combinaison de valeurs */
.mixed-padding {
    padding: 10px 5% 20px 2em;
}</code></pre>
    
    <div class="info-box">
        <p><strong>💡 Conseil :</strong> Les pourcentages pour padding sont calculés par rapport à la largeur de l'élément parent, même pour les paddings top et bottom.</p>
    </div>
    
    <h2>10. Exemple complet</h2>
    
    <h3>HTML :</h3>
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;link rel="stylesheet" href="style.css"&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;div class="container"&gt;
        &lt;div class="card"&gt;
            &lt;h3&gt;Carte avec padding&lt;/h3&gt;
            &lt;p&gt;Ce contenu a un espace intérieur grâce au padding.&lt;/p&gt;
        &lt;/div&gt;
        
        &lt;div class="card spaced"&gt;
            &lt;h3&gt;Carte avec marge&lt;/h3&gt;
            &lt;p&gt;Cette carte a une marge pour s'éloigner des autres.&lt;/p&gt;
        &lt;/div&gt;
        
        &lt;div class="card centered"&gt;
            &lt;h3&gt;Carte centrée&lt;/h3&gt;
            &lt;p&gt;Cette carte utilise margin: auto pour être centrée.&lt;/p&gt;
        &lt;/div&gt;
    &lt;/div&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h3>CSS (style.css) :</h3>
    <pre><code>/* Style de base */
body {
    font-family: Arial, sans-serif;
    background-color: #f0f0f0;
}

.container {
    max-width: 1200px;
    margin: 0 auto;  /* Centrer le conteneur */
    padding: 20px;   /* Espace intérieur du conteneur */
}

/* Cartes */
.card {
    background-color: white;
    border: 2px solid #ddd;
    border-radius: 8px;
    padding: 20px 30px;  /* 20px top/bottom, 30px left/right */
    margin-bottom: 20px;  /* Espace entre les cartes */
}

/* Carte avec padding différent */
.card.spaced {
    padding: 40px;  /* Plus grand espace intérieur */
    margin: 30px 0;  /* marge verticale plus grande */
}

/* Carte centrée */
.card.centered {
    width: 60%;
    margin: 20px auto;  /* Centrée horizontalement */
    text-align: center;
}</code></pre>
    
    <h2>11. Bonnes pratiques</h2>
    
    <ul>
        <li><strong>Utilisez margin pour l'espacement extérieur</strong> - Pour éloigner les éléments entre eux</li>
        <li><strong>Utilisez padding pour l'espacement intérieur</strong> - Pour aérer le contenu</li>
        <li><strong>Préférez la propriété raccourcie</strong> pour un code plus concis</li>
        <li><strong>Souvenez-vous du sens horaire</strong> : top, right, bottom, left pour l'ordre des 4 valeurs</li>
        <li><strong>Utilisez margin: 0 auto</strong> pour centrer les éléments block horizontaux</li>
        <li><strong>Attention au collapse des marges</strong> - les marges verticales se fusionnent</li>
        <li><strong>Le padding augmente la taille totale</strong> de l'élément (sauf avec box-sizing: border-box)</li>
    </ul>
    
    <div class="tip-box">
        <p><strong>💡 Astuce :</strong> Utilisez <code>box-sizing: border-box</code> pour que le padding ne modifie pas la largeur totale de l'élément.</p>
    </div>
    
    <h2>12. Exercice pratique</h2>
    <p>Créez une page web avec les caractéristiques suivantes :</p>
    <ol>
        <li>Un conteneur principal centré avec margin: auto</li>
        <li>Un header avec un padding intérieur de 20px</li>
        <li>Trois cartes avec des marges différentes :
            <ul>
                <li>Carte 1 : marge inférieure de 30px</li>
                <li>Carte 2 : marge de 20px sur tous les côtés</li>
                <li>Carte 3 : marge centrée avec auto</li>
            </ul>
        </li>
        <li>Un footer avec un padding de 40px en haut et en bas</li>
        <li>Expérimentez avec le collapse des marges entre les éléments</li>
    </ol>
    
    <div class="info-box">
        <p><strong>💡 Rappel :</strong> Margin = espace extérieur, Padding = espace intérieur. Maîtrisez ces deux concepts pour créer des mises en page harmonieuses.</p>
    </div>
    """.strip()
    
    
    cours_data = {
        "titre": "CSS Margin & Padding - Espacements en CSS",
        "slug": slug_cours,
        "description": "Apprenez à maîtriser les espaces en CSS avec margin (marge extérieure) et padding (remplissage intérieur). Découvrez comment espacer, centrer et organiser vos éléments. Comprenez le phénomène de collapse des marges et les bonnes pratiques.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 35,
        "ordre_affichage": 21,
        "chapitre_id": chapitre_id,  
        "tags": ["css", "margin", "padding", "margin-auto", "margin-collapse", "espacement", "box-model", "centrage", "responsif", "debutant"],
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

def inserer_questions_css_margin_padding(cours_id):
    
    
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
            "question": "Quelle est la différence fondamentale entre margin et padding en CSS ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "margin et padding font la même chose",
                "B": "margin est l'espace extérieur (hors bordure), padding est l'espace intérieur (entre contenu et bordure)",
                "C": "margin s'applique au texte, padding aux images",
                "D": "margin ne fonctionne que sur mobile"
            },
            "reponse_correcte": "B",
            "explication": "Margin crée de l'espace à l'extérieur de la bordure (entre les éléments), tandis que padding crée de l'espace à l'intérieur (entre le contenu et la bordure).",
            "mode_specifique": "texte"
        },
        {
            "question": "Comment centrer horizontalement un élément block avec margin ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "margin: center;",
                "B": "margin: 0 auto;",
                "C": "margin: auto 0;",
                "D": "text-align: center;"
            },
            "reponse_correcte": "B",
            "explication": "margin: 0 auto; centre l'élément horizontalement. L'élément doit avoir une largeur définie.",
            "mode_specifique": "video"
        },
        {
            "question": "Que signifie margin: 10px 20px 30px 40px ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "top=10px, right=20px, bottom=30px, left=40px",
                "B": "top=40px, right=30px, bottom=20px, left=10px",
                "C": "top=10px, right=30px, bottom=20px, left=40px",
                "D": "top=10px, right=40px, bottom=20px, left=30px"
            },
            "reponse_correcte": "A",
            "explication": "L'ordre est horaire : top (haut), right (droite), bottom (bas), left (gauche).",
            "mode_specifique": "audio"
        },
        {
            "question": "Qu'est-ce que le 'margin collapsing' ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "Les marges disparaissent complètement",
                "B": "Les marges horizontales se fusionnent",
                "C": "Les marges verticales entre éléments adjacents se fusionnent en une seule marge",
                "D": "Les marges deviennent transparentes"
            },
            "reponse_correcte": "C",
            "explication": "Le margin collapsing est un comportement où les marges verticales d'éléments adjacents se fusionnent en une seule marge (la plus grande des deux).",
            "mode_specifique": "video"
        },
        {
            "question": "Quel padding applique 10px en haut/bas et 20px à gauche/droite ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "padding: 10px 20px;",
                "B": "padding: 20px 10px;",
                "C": "padding: 10px 20px 10px 20px;",
                "D": "Les réponses A et C sont correctes"
            },
            "reponse_correcte": "D",
            "explication": "padding: 10px 20px; équivaut à padding: 10px 20px 10px 20px; (top/bottom=10px, right/left=20px).",
            "mode_specifique": "texte"
        },
        {
            "question": "Pourquoi le padding peut augmenter la largeur totale d'un élément ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "Parce que padding s'ajoute à la largeur définie",
                "B": "Parce que padding réduit la largeur du contenu",
                "C": "Parce que padding crée une nouvelle bordure",
                "D": "Parce que padding transforme l'élément"
            },
            "reponse_correcte": "A",
            "explication": "Par défaut, le padding s'ajoute à la largeur définie. Utilisez box-sizing: border-box pour inclure le padding dans la largeur totale.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle propriété utilise-t-on pour définir la marge uniquement à droite ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "margin-right",
                "B": "margin-left",
                "C": "margin-bottom",
                "D": "margin-top"
            },
            "reponse_correcte": "A",
            "explication": "margin-right définit la marge sur le côté droit de l'élément.",
            "mode_specifique": "video"
        },
        {
            "question": "Que signifie padding: 20px ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "Padding de 20px uniquement en haut",
                "B": "Padding de 20px sur les 4 côtés",
                "C": "Padding de 20px à gauche et droite",
                "D": "Padding de 20px en haut et bas"
            },
            "reponse_correcte": "B",
            "explication": "Une seule valeur pour padding s'applique aux 4 côtés (top, right, bottom, left).",
            "mode_specifique": "audio"
        },
        {
            "question": "Comment éviter que les marges verticales ne se fusionnent (margin collapse) ?",
            "type_question": "choix_multiple",
            "points": 20,
            "difficulte": "difficile",
            "options": {
                "A": "Ajouter une bordure ou un padding à l'élément parent",
                "B": "Utiliser overflow: auto sur l'élément parent",
                "C": "Ajouter un élément avec min-height",
                "D": "Toutes ces réponses"
            },
            "reponse_correcte": "D",
            "explication": "Pour éviter le margin collapse, on peut ajouter une bordure, un padding, overflow: auto, ou créer un nouveau contexte de formatage.",
            "mode_specifique": "texte"
        },
        {
            "question": "Laquelle de ces affirmations sur padding est correcte ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "Le padding ne peut pas avoir de couleur d'arrière-plan",
                "B": "Le padding peut avoir une couleur d'arrière-plan car il est à l'intérieur de la bordure",
                "C": "Le padding est toujours transparent",
                "D": "Le padding n'affecte pas la taille de l'élément"
            },
            "reponse_correcte": "B",
            "explication": "Le padding est à l'intérieur de la bordure et hérite de la couleur d'arrière-plan de l'élément.",
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
    print("🎓 INSERTION DU COURS: CSS MARGIN & PADDING")
    print("(Espacements en CSS)")
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
    
    
    cours_id = inserer_cours_css_margin_padding()
    
    if cours_id:
        
        inserer_questions_css_margin_padding(cours_id)
        
        print(f"\n🎉 Succès ! Le cours 'CSS Margin & Padding - Espacements en CSS' a été inséré avec succès!")
        print(f"   📚 Cours ID: {cours_id}")
        
        
        lister_cours_et_chapitres()
    else:
        print("\n❌ Échec de l'insertion du cours")

if __name__ == "__main__":
    main()