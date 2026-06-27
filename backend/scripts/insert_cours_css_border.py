
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

def inserer_cours_css_border():
    
    
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
    
    
    slug_cours = "css-border"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    
    contenu_html = """
    <h1>🖼️ CSS Borders - Guide Complet des Bordures</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Les bordures CSS permettent d'ajouter des contours stylisés autour des éléments HTML. Elles peuvent être personnalisées en termes de style, d'épaisseur, de couleur, et peuvent être appliquées différemment sur chaque côté.</p>
    </div>
    
    <h2>Introduction aux Bordures CSS</h2>
    <p>Les bordures sont des lignes qui entourent les éléments HTML. CSS offre une grande flexibilité pour styliser, dimensionner et colorer les bordures. La propriété <code>border-style</code> est fondamentale car elle doit être définie pour que les autres propriétés de bordure fonctionnent.</p>
    
    <div class="tip-box">
        <p><strong>💡 Astuce :</strong> Sans <code>border-style</code>, les bordures ne s'affichent pas, même si vous définissez une largeur ou une couleur.</p>
    </div>
    
    <h2>1. Les styles de bordures (border-style)</h2>
    <p>La propriété <code>border-style</code> définit l'apparence visuelle de la bordure. Voici les différentes valeurs possibles :</p>
    
    <h3>Valeurs disponibles :</h3>
    <ul>
        <li><strong>none</strong> : Pas de bordure (par défaut)</li>
        <li><strong>hidden</strong> : Bordure cachée (similaire à none)</li>
        <li><strong>dotted</strong> : Bordures en pointillés</li>
        <li><strong>dashed</strong> : Bordures en tirets</li>
        <li><strong>solid</strong> : Bordure pleine</li>
        <li><strong>double</strong> : Double lignes</li>
        <li><strong>groove</strong> : Effet 3D creusé</li>
        <li><strong>ridge</strong> : Effet 3D en relief</li>
        <li><strong>inset</strong> : Effet 3D encastré</li>
        <li><strong>outset</strong> : Effet 3D saillant</li>
    </ul>
    
    <h3>Exemples :</h3>
    <pre><code>/* Bordures pleines */
.solid-border {
    border-style: solid;
}

/* Bordures en pointillés */
.dotted-border {
    border-style: dotted;
}

/* Bordures en tirets */
.dashed-border {
    border-style: dashed;
}

/* Double bordure */
.double-border {
    border-style: double;
}

/* Effet 3D */
.groove-border {
    border-style: groove;
}

.ridge-border {
    border-style: ridge;
}

.inset-border {
    border-style: inset;
}

.outset-border {
    border-style: outset;
}</code></pre>
    
    <div class="info-box">
        <p><strong>📝 Note :</strong> Les styles groove, ridge, inset et outset créent des effets 3D qui dépendent de la couleur de la bordure. L'épaisseur affecte également l'intensité de l'effet 3D.</p>
    </div>
    
    <h2>2. Largeur des bordures (border-width)</h2>
    <p>La propriété <code>border-width</code> contrôle l'épaisseur de la bordure.</p>
    
    <h3>Valeurs possibles :</h3>
    <ul>
        <li><strong>thin</strong> : Bordure fine</li>
        <li><strong>medium</strong> : Bordure moyenne (par défaut)</li>
        <li><strong>thick</strong> : Bordure épaisse</li>
        <li><strong>px, em, rem</strong> : Valeurs spécifiques (ex: 2px, 4px)</li>
    </ul>
    
    <h3>Exemples :</h3>
    <pre><code>/* Épaisseurs prédéfinies */
.thin-border {
    border-style: solid;
    border-width: thin;
}

.medium-border {
    border-style: solid;
    border-width: medium;
}

.thick-border {
    border-style: solid;
    border-width: thick;
}

/* Épaisseur personnalisée */
.custom-border {
    border-style: solid;
    border-width: 5px;
}

/* Différentes épaisseurs par côté */
.mixed-border {
    border-style: solid;
    border-width: 2px 5px 10px 2px; /* top right bottom left */
}</code></pre>
    
    <h2>3. Couleur des bordures (border-color)</h2>
    <p>La propriété <code>border-color</code> définit la couleur de la bordure.</p>
    
    <h3>Formats acceptés :</h3>
    <ul>
        <li>Noms de couleurs (red, blue, green...)</li>
        <li>HEX (#FF0000, #00FF00...)</li>
        <li>RGB (rgb(255,0,0)...)</li>
        <li>HSL (hsl(0,100%,50%)...)</li>
        <li>transparent</li>
    </ul>
    
    <h3>Exemples :</h3>
    <pre><code>/* Noms de couleurs */
.color-name {
    border-style: solid;
    border-color: red;
}

/* HEX */
.hex-border {
    border-style: solid;
    border-color: #3498db;
}

/* RGB */
.rgb-border {
    border-style: solid;
    border-color: rgb(46, 204, 113);
}

/* Différentes couleurs par côté */
.mixed-color {
    border-style: solid;
    border-color: red green blue yellow; /* top right bottom left */
}

/* Par défaut, la bordure hérite de la couleur du texte */
.inherit-color {
    border-style: solid;
    color: purple;
    /* border-color sera purple automatiquement */
}</code></pre>
    
    <h2>4. Bordures différentes par côté</h2>
    <p>CSS permet d'appliquer des styles différents sur chaque côté d'un élément.</p>
    
    <h3>Propriétés individuelles :</h3>
    <ul>
        <li><strong>border-top-style</strong> - Style du haut</li>
        <li><strong>border-right-style</strong> - Style de droite</li>
        <li><strong>border-bottom-style</strong> - Style du bas</li>
        <li><strong>border-left-style</strong> - Style de gauche</li>
    </ul>
    
    <h3>Exemples :</h3>
    <pre><code>/* Styles différents par côté */
.different-sides {
    border-top-style: solid;
    border-right-style: dashed;
    border-bottom-style: dotted;
    border-left-style: double;
    
    border-top-width: 3px;
    border-right-width: 4px;
    border-bottom-width: 2px;
    border-left-width: 5px;
    
    border-top-color: red;
    border-right-color: blue;
    border-bottom-color: green;
    border-left-color: orange;
}

/* Version avec 4 valeurs (top, right, bottom, left) */
.shorthand-sides {
    border-style: solid dashed dotted double;
    border-width: 2px 4px 6px 8px;
    border-color: red blue green orange;
}</code></pre>
    
    <h2>5. La propriété raccourcie (border)</h2>
    <p>La propriété <code>border</code> permet de définir le style, la largeur et la couleur en une seule déclaration.</p>
    
    <h3>Syntaxe :</h3>
    <pre><code>border: [width] [style] [color];</code></pre>
    
    <h3>Exemples :</h3>
    <pre><code>/* Bordure simple */
.simple-border {
    border: 2px solid black;
}

/* Bordure rouge en pointillés */
.dotted-red {
    border: 3px dotted red;
}

/* Bordure épaisse en relief */
.thick-ridge {
    border: 5px ridge gold;
}

/* Pas de bordure */
.no-border {
    border: none;
}</code></pre>
    
    <h2>6. Bordures côté-spécifiques raccourcies</h2>
    <p>CSS offre des propriétés raccourcies pour chaque côté :</p>
    
    <h3>Propriétés disponibles :</h3>
    <ul>
        <li><strong>border-top</strong> - Bordure du haut</li>
        <li><strong>border-right</strong> - Bordure de droite</li>
        <li><strong>border-bottom</strong> - Bordure du bas</li>
        <li><strong>border-left</strong> - Bordure de gauche</li>
    </ul>
    
    <h3>Exemples :</h3>
    <pre><code>/* Bordure uniquement en haut */
.top-border {
    border-top: 3px solid #3498db;
}

/* Bordure uniquement en bas */
.bottom-border {
    border-bottom: 2px dashed red;
}

/* Bordures différentes sur chaque côté */
.side-borders {
    border-top: 2px solid black;
    border-right: 4px dotted blue;
    border-bottom: 3px double green;
    border-left: 5px groove orange;
}</code></pre>
    
    <h2>7. Bordures arrondies (border-radius)</h2>
    <p>La propriété <code>border-radius</code> permet d'arrondir les coins des bordures.</p>
    
    <h3>Exemples :</h3>
    <pre><code>/* Coins légèrement arrondis */
.slight-round {
    border: 2px solid #333;
    border-radius: 5px;
}

/* Coins très arrondis (cercle) */
.round {
    border: 2px solid #333;
    border-radius: 50px;
    width: 100px;
    height: 100px;
}

/* Chaque coin différent */
.different-corners {
    border: 2px solid #333;
    border-radius: 10px 20px 30px 40px; /* top-left top-right bottom-right bottom-left */
}</code></pre>
    
    <h2>8. Exemple complet</h2>
    
    <h3>HTML :</h3>
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;link rel="stylesheet" href="border-styles.css"&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;h1&gt;Démonstration des Bordures CSS&lt;/h1&gt;
    
    &lt;div class="card"&gt;
        &lt;h2&gt;Carte standard&lt;/h2&gt;
        &lt;p&gt;Cette carte a une bordure simple et arrondie.&lt;/p&gt;
    &lt;/div&gt;
    
    &lt;div class="card featured"&gt;
        &lt;h2&gt;Carte mise en avant&lt;/h2&gt;
        &lt;p&gt;Bordure en relief avec double contour.&lt;/p&gt;
    &lt;/div&gt;
    
    &lt;div class="alert success"&gt;
        ✅ Opération réussie !
    &lt;/div&gt;
    
    &lt;div class="alert error"&gt;
        ❌ Une erreur est survenue.
    &lt;/div&gt;
    
    &lt;div class="gallery"&gt;
        &lt;div class="photo"&gt;Photo 1&lt;/div&gt;
        &lt;div class="photo"&gt;Photo 2&lt;/div&gt;
        &lt;div class="photo"&gt;Photo 3&lt;/div&gt;
    &lt;/div&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h3>CSS (border-styles.css) :</h3>
    <pre><code>/* Style général des cartes */
.card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 20px;
    margin: 15px;
    background-color: white;
}

/* Carte mise en avant */
.featured {
    border: 3px solid #3498db;
    border-top: 8px solid #3498db;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

/* Alertes */
.alert {
    padding: 15px;
    margin: 15px;
    border-radius: 5px;
    font-weight: bold;
}

.alert.success {
    border-left: 5px solid #2ecc71;
    background-color: #d5f5e3;
    color: #27ae60;
}

.alert.error {
    border-left: 5px solid #e74c3c;
    background-color: #fadbd8;
    color: #c0392b;
}

/* Galerie */
.gallery {
    display: flex;
    gap: 20px;
    margin: 15px;
}

.photo {
    border: 2px solid #ddd;
    border-radius: 10px;
    padding: 40px;
    text-align: center;
    flex: 1;
    transition: all 0.3s ease;
}

.photo:hover {
    border-color: #3498db;
    transform: scale(1.05);
}</code></pre>
    
    <h2>9. Bonnes pratiques</h2>
    
    <ul>
        <li><strong>Toujours définir border-style</strong> - Sans style, la bordure ne s'affiche pas</li>
        <li><strong>Utilisez border-radius</strong> pour des designs modernes et arrondis</li>
        <li><strong>Préférez les propriétés raccourcies</strong> pour un code plus concis</li>
        <li><strong>Testez les effets 3D</strong> - Ils dépendent de l'épaisseur et de la couleur</li>
        <li><strong>Utilisez border-left ou border-top</strong> pour des accents visuels subtils</li>
        <li><strong>Combinez les bordures avec box-shadow</strong> pour plus de profondeur</li>
        <li><strong>Attention aux performances</strong> - Les bordures complexes peuvent affecter le rendu</li>
    </ul>
    
    <h2>10. Exercice pratique</h2>
    <p>Créez une page web avec les caractéristiques suivantes :</p>
    <ol>
        <li>Un titre principal avec une bordure en bas (border-bottom) de couleur bleue, épaisseur 3px</li>
        <li>Trois cartes avec des bordures différentes :
            <ul>
                <li>Carte 1 : bordure pointillée (dotted) rouge</li>
                <li>Carte 2 : bordure en tirets (dashed) verte</li>
                <li>Carte 3 : double bordure bleue</li>
            </ul>
        </li>
        <li>Des alertes avec une bordure à gauche (border-left) colorée</li>
        <li>Une galerie d'images avec bordures arrondies qui changent au survol</li>
        <li>Un élément avec un effet 3D (groove, ridge, inset ou outset)</li>
    </ol>
    
    <div class="info-box">
        <p><strong>💡 Conseil :</strong> Expérimentez avec différentes combinaisons de style, largeur et couleur pour créer des designs uniques et professionnels.</p>
    </div>
    """.strip()
    
    
    cours_data = {
        "titre": "CSS Borders - Bordures en CSS",
        "slug": slug_cours,
        "description": "Apprenez à styliser, dimensionner et colorer les bordures autour des éléments HTML. Découvrez les différents styles (solid, dotted, dashed, double, 3D), les épaisseurs, les couleurs, et comment appliquer des bordures différentes sur chaque côté.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 25,
        "ordre_affichage": 20,
        "chapitre_id": chapitre_id,  
        "tags": ["css", "border", "border-style", "border-width", "border-color", "border-radius", "solid", "dotted", "dashed", "double", "groove", "ridge", "web design"],
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

def inserer_questions_css_border(cours_id):
    
    
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
            "question": "Quelle propriété CSS est fondamentale car elle doit être définie pour que la bordure s'affiche ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "border-width",
                "B": "border-color",
                "C": "border-style",
                "D": "border-radius"
            },
            "reponse_correcte": "C",
            "explication": "border-style est la propriété fondamentale. Sans style défini, la bordure ne s'affiche pas, même si width et color sont définis.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quel style de bordure donne un effet 3D creusé (enfoncé) ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "ridge",
                "B": "groove",
                "C": "outset",
                "D": "inset"
            },
            "reponse_correcte": "B",
            "explication": "groove crée un effet 3D creusé (comme une rainure), tandis que ridge donne un effet en relief.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment créer une bordure pleine rouge de 2 pixels ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "border: 2px solid red;",
                "B": "border: red 2px solid;",
                "C": "border: solid red 2px;",
                "D": "Toutes ces réponses"
            },
            "reponse_correcte": "D",
            "explication": "Toutes ces syntaxes sont correctes. border accepte les valeurs dans n'importe quel ordre (width, style, color).",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle propriété permet d'arrondir les coins d'une bordure ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "border-round",
                "B": "border-corner",
                "C": "border-radius",
                "D": "border-circle"
            },
            "reponse_correcte": "C",
            "explication": "border-radius permet d'arrondir les coins des bordures. Plus la valeur est grande, plus les coins sont arrondis.",
            "mode_specifique": "texte"
        },
        {
            "question": "Comment appliquer une bordure uniquement en bas d'un élément ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "border: bottom 2px solid red;",
                "B": "border-bottom: 2px solid red;",
                "C": "border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: red;",
                "D": "Les réponses B et C sont correctes"
            },
            "reponse_correcte": "D",
            "explication": "border-bottom est la propriété raccourcie, mais on peut aussi utiliser les propriétés individuelles border-bottom-style, border-bottom-width, border-bottom-color.",
            "mode_specifique": "video"
        },
        {
            "question": "Que signifie border-style: double ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "Deux bordures superposées",
                "B": "Deux lignes parallèles avec un espace entre elles",
                "C": "Bordure qui change de couleur",
                "D": "Bordure clignotante"
            },
            "reponse_correcte": "B",
            "explication": "double crée deux lignes parallèles. L'épaisseur totale est divisée pour créer la bordure double.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle est la valeur par défaut de border-width ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "thin",
                "B": "medium",
                "C": "thick",
                "D": "1px"
            },
            "reponse_correcte": "B",
            "explication": "La valeur par défaut de border-width est 'medium' (environ 3-4px selon le navigateur).",
            "mode_specifique": "audio"
        },
        {
            "question": "Comment écrire la propriété raccourcie pour définir des bordures différentes sur chaque côté ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "border: solid 2px red, dashed 4px blue;",
                "B": "border-style: solid dashed dotted double;",
                "C": "border: top solid, right dashed, bottom dotted, left double;",
                "D": "border-sides: solid 2px;"
            },
            "reponse_correcte": "B",
            "explication": "On peut utiliser border-style avec 4 valeurs (top, right, bottom, left) pour définir des styles différents sur chaque côté.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quel style de bordure donne un effet 3D saillant (qui ressort) ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "inset",
                "B": "outset",
                "C": "groove",
                "D": "ridge"
            },
            "reponse_correcte": "B",
            "explication": "outset crée un effet 3D saillant, comme si la bordure ressortait de l'écran.",
            "mode_specifique": "video"
        },
        {
            "question": "Que se passe-t-il si on définit border-color sans définir border-style ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "La bordure s'affiche avec le style solid par défaut",
                "B": "La bordure s'affiche avec la couleur définie",
                "C": "Aucune bordure ne s'affiche car border-style n'est pas défini",
                "D": "La bordure hérite du style de l'élément parent"
            },
            "reponse_correcte": "C",
            "explication": "border-style doit toujours être défini. Sans style, la bordure ne s'affiche pas, peu importe les autres propriétés définies.",
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
    print("🎓 INSERTION DU COURS: CSS BORDERS (BORDURES CSS)")
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
    
    
    cours_id = inserer_cours_css_border()
    
    if cours_id:
        
        inserer_questions_css_border(cours_id)
        
        print(f"\n🎉 Succès ! Le cours 'CSS Borders - Bordures en CSS' a été inséré avec succès!")
        print(f"   📚 Cours ID: {cours_id}")
        
        
        lister_cours_et_chapitres()
    else:
        print("\n❌ Échec de l'insertion du cours")

if __name__ == "__main__":
    main()