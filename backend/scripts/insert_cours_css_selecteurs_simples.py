
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

def inserer_cours_css_selecteurs():
    
    
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
    
    
    slug_cours = "css-selecteurs-simples"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    
    contenu_html = """
    <h1>🎨 CSS - Les Sélecteurs Simples (Element, ID, Class)</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Les sélecteurs CSS sont la base du stylage web. Ils permettent de cibler précisément les éléments HTML à styliser. Ce cours couvre les trois sélecteurs les plus courants : les sélecteurs d'élément, d'ID et de classe.</p>
    </div>
    
    <h2>Introduction aux Sélecteurs CSS</h2>
    <p>Les sélecteurs CSS déterminent quels éléments HTML vont recevoir les styles définis. Sans sélecteurs, il serait impossible d'appliquer du style spécifique à des éléments particuliers d'une page web.</p>
    
    <div class="tip-box">
        <p><strong>💡 À retenir :</strong> Maîtriser les sélecteurs est essentiel pour écrire du CSS efficace et maintenable.</p>
    </div>
    
    <h2>1. Les Sélecteurs d'Élément (Type Selectors)</h2>
    <p>Le sélecteur d'élément cible <strong>toutes les occurrences</strong> d'une balise HTML spécifique dans la page.</p>
    
    <h3>Syntaxe :</h3>
    <pre><code>nom_de_la_balise {
    propriété: valeur;
}</code></pre>
    
    <h3>Exemple :</h3>
    <pre><code>/* Tous les paragraphes deviennent rouges */
p {
    color: red;
    font-size: 16px;
}

/* Tous les titres h1 deviennent bleus */
h1 {
    color: blue;
}

/* Tous les liens n'ont plus de soulignement */
a {
    text-decoration: none;
}</code></pre>
    
    <div class="info-box">
        <p><strong>📝 Résultat :</strong> Tous les paragraphes &lt;p&gt; de la page auront du texte rouge, tous les &lt;h1&gt; seront bleus.</p>
    </div>
    
    <h3>Avantages et inconvénients :</h3>
    <ul>
        <li><strong>Avantage :</strong> Applique rapidement un style global à tous les éléments d'un type.</li>
        <li><strong>Inconvénient :</strong> Manque de précision - affecte TOUS les éléments, même ceux qu'on ne veut pas styliser.</li>
    </ul>
    
    <h2>2. Les Sélecteurs d'ID</h2>
    <p>Le sélecteur d'ID cible <strong>un élément unique</strong> dans la page. Chaque ID doit être unique dans le document HTML.</p>
    
    <h3>Syntaxe :</h3>
    <pre><code>#nom_de_l_id {
    propriété: valeur;
}</code></pre>
    
    <h3>En HTML :</h3>
    <pre><code>&lt;div id="header"&gt;Contenu de l'en-tête&lt;/div&gt;
&lt;p id="introduction"&gt;Ceci est une introduction unique.&lt;/p&gt;</code></pre>
    
    <h3>Exemple CSS :</h3>
    <pre><code>/* L'élément avec l'ID "header" aura une police de 20px */
#header {
    font-size: 20px;
    background-color: #f0f0f0;
}

/* L'élément avec l'ID "introduction" aura une marge spécifique */
#introduction {
    margin-top: 20px;
    font-weight: bold;
}</code></pre>
    
    <div class="warning-box">
        <p><strong>⚠️ Important :</strong> Un ID ne peut être utilisé qu'UNE SEULE fois par page. C'est idéal pour les éléments uniques comme l'en-tête, le pied de page, ou une section spécifique.</p>
    </div>
    
    <h3>Avantages :</h3>
    <ul>
        <li>Très précis - cible un élément unique</li>
        <li>Haute spécificité (priorité sur les autres sélecteurs)</li>
        <li>Idéal pour le JavaScript (getElementById)</li>
    </ul>
    
    <h2>3. Les Sélecteurs de Classe</h2>
    <p>Le sélecteur de classe cible <strong>plusieurs éléments</strong> qui partagent le même nom de classe. C'est le sélecteur le plus polyvalent !</p>
    
    <h3>Syntaxe :</h3>
    <pre><code>.nom_de_la_classe {
    propriété: valeur;
}</code></pre>
    
    <h3>En HTML :</h3>
    <pre><code>&lt;p class="highlight"&gt;Texte surligné&lt;/p&gt;
&lt;div class="highlight"&gt;Div surlignée&lt;/div&gt;
&lt;span class="highlight"&gt;Span surligné&lt;/span&gt;

&lt;!-- Un élément peut avoir plusieurs classes --&gt;
&lt;button class="btn btn-primary large"&gt;Cliquez-moi&lt;/button&gt;</code></pre>
    
    <h3>Exemple CSS :</h3>
    <pre><code>/* Tous les éléments avec la classe "highlight" auront un fond jaune */
.highlight {
    background-color: yellow;
    font-weight: bold;
}

/* Tous les éléments avec la classe "btn" auront les styles de bouton */
.btn {
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

/* Combinaison avec sélecteur d'élément - seulement les paragraphes avec classe "highlight" */
p.highlight {
    color: darkred;
}</code></pre>
    
    <div class="tip-box">
        <p><strong>💡 Astuce :</strong> Les classes sont réutilisables et permettent d'appliquer les mêmes styles à plusieurs éléments différents. C'est la méthode la plus courante en CSS moderne !</p>
    </div>
    
    <h3>Avantages :</h3>
    <ul>
        <li>Réutilisable plusieurs fois sur la même page</li>
        <li>Un élément peut avoir plusieurs classes</li>
        <li>Idéal pour les composants réutilisables</li>
        <li>Facile à maintenir</li>
    </ul>
    
    <h2>4. Comparaison des Sélecteurs</h2>
    
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left;">Sélecteur</th>
            <th style="padding: 8px; text-align: left;">Syntaxe</th>
            <th style="padding: 8px; text-align: left;">Cible</th>
            <th style="padding: 8px; text-align: left;">Utilisation typique</th>
        </thead>
        <tbody>
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 8px;"><strong>Élément</strong></td>
                <td style="padding: 8px;"><code>p { }</code></td>
                <td style="padding: 8px;">Toutes les balises &lt;p&gt;</td>
                <td style="padding: 8px;">Styles globaux</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 8px;"><strong>ID</strong></td>
                <td style="padding: 8px;"><code>#header { }</code></td>
                <td style="padding: 8px;">Un élément unique</td>
                <td style="padding: 8px;">Éléments uniques dans la page</td>
            </tr>
            <tr>
                <td style="padding: 8px;"><strong>Classe</strong></td>
                <td style="padding: 8px;"><code>.highlight { }</code></td>
                <td style="padding: 8px;">Plusieurs éléments</td>
                <td style="padding: 8px;">Groupes d'éléments, composants réutilisables</td>
            </tr>
        </tbody>
    </table>
    
    <h2>5. Bonnes pratiques avec les sélecteurs</h2>
    
    <ul>
        <li><strong>Utilisez les classes par défaut :</strong> Elles sont réutilisables et faciles à maintenir.</li>
        <li><strong>Réservez les ID pour les éléments vraiment uniques :</strong> En-tête, footer, ou ciblage JavaScript.</li>
        <li><strong>Privilégiez des noms sémantiques :</strong> .btn, .card, .nav-item plutôt que .rouge, .gauche.</li>
        <li><strong>Évitez les sélecteurs trop spécifiques :</strong> Commencez simple avec des classes.</li>
        <li><strong>Un élément peut avoir plusieurs classes :</strong> &lt;div class="card shadow large"&gt;.</li>
        <li><strong>Combinez les sélecteurs quand c'est utile :</strong> p.highlight pour cibler seulement les paragraphes avec cette classe.</li>
    </ul>
    
    <h2>6. Exemple complet</h2>
    
    <h3>HTML :</h3>
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;link rel="stylesheet" href="style.css"&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;div id="header"&gt;
        &lt;h1&gt;Bienvenue sur mon site&lt;/h1&gt;
    &lt;/div&gt;
    
    &lt;div class="container"&gt;
        &lt;p class="highlight"&gt;Ce paragraphe est surligné.&lt;/p&gt;
        &lt;p&gt;Ce paragraphe est normal.&lt;/p&gt;
        &lt;p class="highlight"&gt;Ce paragraphe aussi est surligné.&lt;/p&gt;
    &lt;/div&gt;
    
    &lt;button class="btn btn-primary"&gt;Cliquez ici&lt;/button&gt;
    &lt;button class="btn btn-secondary"&gt;Annuler&lt;/button&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h3>CSS :</h3>
    <pre><code>/* Sélecteur d'élément */
p {
    line-height: 1.5;
    margin-bottom: 10px;
}

/* Sélecteur d'ID */
#header {
    background-color: #333;
    color: white;
    padding: 20px;
    text-align: center;
}

/* Sélecteurs de classe */
.highlight {
    background-color: yellow;
    font-weight: bold;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.btn {
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
}

.btn-primary {
    background-color: blue;
    color: white;
}

.btn-secondary {
    background-color: gray;
    color: white;
}</code></pre>
    
    <h2>7. Exercice pratique</h2>
    <p>Créez une page HTML et son CSS associé avec les caractéristiques suivantes :</p>
    <ol>
        <li>Un en-tête avec l'ID "main-header" - fond bleu, texte blanc, centré</li>
        <li>Trois cartes avec la classe "card" - bordure, padding, ombre légère</li>
        <li>Dans chaque carte, un titre h3 et un paragraphe</li>
        <li>Les titres h3 doivent être en bleu (sélecteur d'élément)</li>
        <li>Une classe "text-highlight" pour les paragraphes importants - fond jaune</li>
        <li>Les cartes doivent avoir une classe "large" pour celles qui sont plus larges</li>
    </ol>
    
    <div class="info-box">
        <p><strong>💡 Objectif :</strong> Pratiquez les trois types de sélecteurs et comprenez quand utiliser chacun d'eux.</p>
    </div>
    """.strip()
    
    
    cours_data = {
        "titre": "CSS - Les Sélecteurs Simples (Element, ID, Class)",
        "slug": slug_cours,
        "description": "Apprenez les trois sélecteurs CSS les plus courants : les sélecteurs d'élément, d'ID et de classe. Découvrez comment cibler précisément les éléments HTML à styliser, avec des exemples pratiques et des bonnes pratiques pour un CSS efficace et maintenable.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 20,
        "ordre_affichage": 17,
        "chapitre_id": chapitre_id,  
        "tags": ["css", "selecteurs", "element-selector", "id-selector", "class-selector", "selecteurs-css", "css-debutant", "styling"],
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

def inserer_questions_css_selecteurs(cours_id):
    
    
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
            "question": "Quel est le sélecteur CSS qui cible TOUS les paragraphes d'une page ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "#paragraph",
                "B": ".paragraph",
                "C": "p",
                "D": "<p>"
            },
            "reponse_correcte": "C",
            "explication": "Le sélecteur d'élément 'p' cible tous les paragraphes &lt;p&gt; de la page.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quelle syntaxe utilise-t-on pour cibler un élément par son ID ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": ".monId",
                "B": "#monId",
                "C": "monId",
                "D": "*monId"
            },
            "reponse_correcte": "B",
            "explication": "Le sélecteur d'ID utilise le symbole # suivi du nom de l'ID.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle est la principale différence entre un ID et une classe en CSS ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "Les IDs sont pour le texte, les classes pour les images",
                "B": "Un ID est unique sur la page, une classe peut être réutilisée plusieurs fois",
                "C": "Les IDs fonctionnent uniquement sur mobile",
                "D": "Les classes sont plus récentes que les IDs"
            },
            "reponse_correcte": "B",
            "explication": "Un ID doit être unique dans la page (un seul élément), tandis qu'une classe peut être appliquée à plusieurs éléments.",
            "mode_specifique": "audio"
        },
        {
            "question": "Comment cibler tous les éléments qui ont la classe 'highlight' ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "#highlight",
                "B": "highlight",
                "C": ".highlight",
                "D": "*highlight"
            },
            "reponse_correcte": "C",
            "explication": "Le sélecteur de classe utilise le point '.' suivi du nom de la classe.",
            "mode_specifique": "video"
        },
        {
            "question": "Que signifie le sélecteur CSS 'p.highlight' ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "Tous les paragraphes ET tous les éléments avec classe highlight",
                "B": "Tous les paragraphes qui ont la classe highlight",
                "C": "Tous les éléments avec la classe highlight à l'intérieur d'un paragraphe",
                "D": "Le paragraphe ayant l'ID highlight"
            },
            "reponse_correcte": "B",
            "explication": "p.highlight cible spécifiquement les balises &lt;p&gt; qui ont la classe 'highlight'.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quel sélecteur est le plus approprié pour styliser un bouton 'Envoyer' présent plusieurs fois sur une page ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "ID (#submit)",
                "B": "Classe (.btn-submit)",
                "C": "Élément (button)",
                "D": "Attribut ([type='submit'])"
            },
            "reponse_correcte": "B",
            "explication": "Une classe est idéale car elle permet d'appliquer les mêmes styles à plusieurs boutons similaires.",
            "mode_specifique": "audio"
        },
        {
            "question": "Un élément HTML peut-il avoir plusieurs classes ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "Oui, en séparant les classes par des espaces",
                "B": "Non, un élément ne peut avoir qu'une seule classe",
                "C": "Oui, mais seulement deux classes maximum",
                "D": "Non, car cela créerait des conflits"
            },
            "reponse_correcte": "A",
            "explication": "Un élément peut avoir plusieurs classes séparées par des espaces, par exemple class='btn btn-primary large'.",
            "mode_specifique": "video"
        },
        {
            "question": "Le sélecteur '#header' a une spécificité plus élevée que le sélecteur '.header' ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "Oui, les IDs ont une spécificité plus élevée que les classes",
                "B": "Non, ils ont la même spécificité",
                "C": "Cela dépend de l'ordre dans le fichier CSS",
                "D": "Les classes ont une spécificité plus élevée"
            },
            "reponse_correcte": "A",
            "explication": "Les sélecteurs d'ID ont une spécificité plus élevée (100) que les classes (10).",
            "mode_specifique": "texte"
        },
        {
            "question": "Quel sélecteur CSS ciblera tous les titres h1 de la page ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "#h1",
                "B": ".h1",
                "C": "h1",
                "D": "<h1>"
            },
            "reponse_correcte": "C",
            "explication": "Le sélecteur d'élément 'h1' cible toutes les balises &lt;h1&gt; de la page.",
            "mode_specifique": "video"
        },
        {
            "question": "Pourquoi est-il recommandé d'utiliser des classes plutôt que des IDs pour le styling ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "Parce que les IDs sont obsolètes",
                "B": "Parce que les classes sont réutilisables et plus flexibles",
                "C": "Parce que les IDs ne fonctionnent pas sur tous les navigateurs",
                "D": "Parce que les classes sont plus rapides"
            },
            "reponse_correcte": "B",
            "explication": "Les classes sont réutilisables, permettent plus de flexibilité et rendent le CSS plus maintenable.",
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
    print("🎓 INSERTION DU COURS: CSS - SÉLECTEURS SIMPLES")
    print("(Element, ID, Class Selectors)")
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
    
    
    cours_id = inserer_cours_css_selecteurs()
    
    if cours_id:
        
        inserer_questions_css_selecteurs(cours_id)
        
        print(f"\n🎉 Succès ! Le cours 'CSS - Les Sélecteurs Simples (Element, ID, Class)' a été inséré avec succès!")
        print(f"   📚 Cours ID: {cours_id}")
        
        
        lister_cours_et_chapitres()
    else:
        print("\n❌ Échec de l'insertion du cours")

if __name__ == "__main__":
    main()