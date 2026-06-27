
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

def inserer_cours_css_tables():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "css-tables"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>📊 CSS Tables - Styliser les Tableaux en CSS</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Les tableaux HTML peuvent être stylisés avec CSS pour les rendre plus attrayants et plus faciles à lire. CSS permet de contrôler les bordures, les couleurs, l'alignement, les dimensions et bien plus encore.</p>
    </div>
    
    <h2>Introduction aux Tableaux CSS</h2>
    <p>CSS offre de nombreuses propriétés pour améliorer l'apparence des tableaux HTML : bordures, fusion des bordures, dimensions, alignement, espacement, couleurs, etc.</p>
    
    <h2>1. Bordures des tableaux</h2>
    <p>La propriété <code>border</code> permet d'ajouter des bordures aux tableaux et aux cellules.</p>
    
    <pre><code>/* Bordures du tableau et des cellules */
table, th, td {
    border: 1px solid black;
}</code></pre>
    
    <div class="warning-box">
        <p><strong>⚠️ Note :</strong> Lorsque les bordures sont appliquées au tableau ET aux cellules, des bordures doubles apparaissent car le tableau et les cellules ont chacun leurs propres bordures.</p>
    </div>
    
    <h2>2. Fusion des bordures (border-collapse)</h2>
    <p>La propriété <code>border-collapse</code> permet de fusionner les bordures doubles en une seule ligne.</p>
    
    <h3>Valeurs possibles :</h3>
    <ul>
        <li><strong>collapse</strong> : Fusionne les bordures en une seule</li>
        <li><strong>separate</strong> : Sépare les bordures (par défaut)</li>
    </ul>
    
    <pre><code>/* Fusionner les bordures */
table {
    border-collapse: collapse;
}

table, th, td {
    border: 1px solid black;
}</code></pre>
    
    <h2>3. Dimensions du tableau</h2>
    <p>Les propriétés <code>width</code> et <code>height</code> permettent de définir la taille du tableau et des cellules.</p>
    
    <pre><code>/* Tableau pleine largeur */
table {
    width: 100%;
}

/* Hauteur des en-têtes */
th {
    height: 50px;
}

/* Largeur spécifique pour certaines colonnes */
td.col1 {
    width: 30%;
}</code></pre>
    
    <h2>4. Alignement du texte</h2>
    
    <h3>Alignement horizontal (text-align) :</h3>
    <ul>
        <li><strong>left</strong> : Aligné à gauche (par défaut pour les cellules)</li>
        <li><strong>center</strong> : Centré (par défaut pour les en-têtes)</li>
        <li><strong>right</strong> : Aligné à droite</li>
    </ul>
    
    <h3>Alignement vertical (vertical-align) :</h3>
    <ul>
        <li><strong>top</strong> : Aligné en haut (par défaut)</li>
        <li><strong>middle</strong> : Centré verticalement</li>
        <li><strong>bottom</strong> : Aligné en bas</li>
    </ul>
    
    <pre><code>/* Alignement horizontal */
th {
    text-align: left;
}

td {
    text-align: center;
}

/* Alignement vertical */
td {
    vertical-align: middle;
}</code></pre>
    
    <h2>5. Espacement intérieur (padding)</h2>
    <p>La propriété <code>padding</code> ajoute de l'espace entre le contenu et la bordure de la cellule.</p>
    
    <pre><code>/* Padding uniforme */
th, td {
    padding: 15px;
}

/* Padding différent selon les cellules */
td {
    padding: 10px 20px;
}</code></pre>
    
    <h2>6. Couleurs et arrière-plans</h2>
    
    <pre><code>/* Couleur d'arrière-plan du tableau */
table {
    background-color: #f0f0f0;
}

/* Couleur des en-têtes */
th {
    background-color: #333;
    color: white;
}

/* Alternance des lignes (striped) */
tr:nth-child(even) {
    background-color: #f2f2f2;
}

/* Survol des lignes */
tr:hover {
    background-color: #ddd;
}</code></pre>
    
    <h2>7. Exemple complet</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;style&gt;
        /* Tableau stylisé */
        .styled-table {
            border-collapse: collapse;
            width: 100%;
            font-family: Arial, sans-serif;
        }
        
        .styled-table th, .styled-table td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        
        .styled-table th {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
        }
        
        /* Alternance des lignes */
        .styled-table tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        
        /* Survol des lignes */
        .styled-table tr:hover {
            background-color: #ddd;
        }
        
        /* Alignement spécifique pour les colonnes de nombres */
        .styled-table td.num {
            text-align: right;
        }
        
        /* Bordure arrondie (effet moderne) */
        .styled-table {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        
        /* Tableau responsive */
        .responsive-table {
            overflow-x: auto;
        }
    &lt;/style&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;div class="responsive-table"&gt;
        &lt;table class="styled-table"&gt;
            &lt;thead&gt;
                <tr>
                    &lt;th&gt;Nom&lt;/th&gt;
                    &lt;th&gt;Prénom&lt;/th&gt;
                    &lt;th class="num"&gt;Âge&lt;/th&gt;
                    &lt;th&gt;Ville&lt;/th&gt;
                </tr>
            </thead>
            &lt;tbody&gt;
                <tr>
                    &lt;td&gt;Dupont&lt;/td&gt;
                    &lt;td&gt;Jean&lt;/td&gt;
                    &lt;td class="num"&gt;25&lt;/td&gt;
                    &lt;td&gt;Paris&lt;/td&gt;
                </tr>
                <tr>
                    &lt;td&gt;Martin&lt;/td&gt;
                    &lt;td&gt;Marie&lt;/td&gt;
                    &lt;td class="num"&gt;30&lt;/td&gt;
                    &lt;td&gt;Lyon&lt;/td&gt;
                </tr>
            &lt;/tbody&gt;
        </table>
    &lt;/div&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h2>8. Tableau responsive</h2>
    <p>Pour rendre un tableau responsive sur mobile, on utilise un conteneur avec <code>overflow-x: auto;</code> :</p>
    
    <pre><code>.table-container {
    overflow-x: auto;
}

.table-container table {
    width: 100%;
    border-collapse: collapse;
}</code></pre>
    
    <h2>9. Bonnes pratiques</h2>
    
    <ul>
        <li><strong>Utilisez border-collapse: collapse</strong> pour éviter les doubles bordures</li>
        <li><strong>Ajoutez un padding</strong> pour aérer le contenu des cellules</li>
        <li><strong>Utilisez des couleurs alternées</strong> (striped) pour améliorer la lisibilité</li>
        <li><strong>Ajoutez un effet de survol</strong> pour guider l'utilisateur</li>
        <li><strong>Rendez les tableaux responsive</strong> avec overflow-x: auto sur mobile</li>
        <li><strong>Alignez correctement les données</strong> : gauche pour le texte, droite pour les nombres</li>
    </ul>
    
    <div class="info-box">
        <p><strong>💡 Astuce :</strong> Pour les grands tableaux, pensez à fixer l'en-tête pour qu'il reste visible lors du défilement.</p>
    </div>
    """.strip()
    
    cours_data = {
        "titre": "CSS Tables - Styliser les Tableaux en CSS",
        "slug": slug_cours,
        "description": "Apprenez à styliser les tableaux HTML en CSS : bordures, border-collapse, dimensions, alignement (text-align, vertical-align), padding, couleurs, arrière-plans, tableaux responsives et bonnes pratiques.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 20,
        "ordre_affichage": 28,
        "chapitre_id": chapitre_id,
        "tags": ["css", "tables", "border-collapse", "padding", "text-align", "vertical-align", "responsive", "striped", "debutant"],
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

def inserer_questions_css_tables(cours_id):
    
    
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
            "question": "Quelle propriété CSS permet de fusionner les bordures doubles d'un tableau en une seule ligne ?",
            "options": '{"A": "border-merge", "B": "border-collapse", "C": "border-single", "D": "border-combine"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "border-collapse: collapse; fusionne les bordures adjacentes en une seule ligne.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quelle propriété CSS permet d'ajouter de l'espace entre le contenu et la bordure d'une cellule de tableau ?",
            "options": '{"A": "margin", "B": "spacing", "C": "padding", "D": "border-spacing"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "padding ajoute de l'espace intérieur entre le contenu et la bordure de la cellule.",
            "mode_specifique": "texte"
        },
        
        
        {
            "question": "Comment centrer horizontalement le texte dans une cellule de tableau ?",
            "options": '{"A": "vertical-align: center;", "B": "text-align: center;", "C": "align: center;", "D": "text-center: true;"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "text-align: center; centre le texte horizontalement dans la cellule.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle propriété CSS contrôle l'alignement vertical du contenu dans une cellule de tableau ?",
            "options": '{"A": "text-align", "B": "vertical-align", "C": "align-vertical", "D": "valign"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "vertical-align contrôle l'alignement vertical (top, middle, bottom).",
            "mode_specifique": "audio"
        },
        {
            "question": "Comment créer un tableau qui occupe 100% de la largeur de son conteneur ?",
            "options": '{"A": "width: 100%;", "B": "size: full;", "C": "expand: true;", "D": "full-width: yes;"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "width: 100%; permet au tableau d'occuper toute la largeur de son conteneur parent.",
            "mode_specifique": "audio"
        },
        
        
        {
            "question": "Quel est le problème lorsqu'on applique border à la fois au tableau ET aux cellules sans border-collapse ?",
            "options": '{"A": "Les bordures disparaissent", "B": "Des bordures doubles apparaissent", "C": "Le tableau devient invisible", "D": "Les bordures deviennent rouges"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Sans border-collapse, le tableau ET les cellules ont chacun leurs bordures, créant un effet de double bordure.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment créer un effet de lignes alternées (striped) dans un tableau ?",
            "options": '{"A": "table:nth-child(even)", "B": "tr:nth-child(even)", "C": "td:nth-child(odd)", "D": "table:alternate"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "tr:nth-child(even) { background-color: #f2f2f2; } permet de colorer les lignes paires.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment rendre un tableau responsive sur mobile ?",
            "options": '{"A": "width: 100%;", "B": "overflow-x: auto; sur un conteneur parent", "C": "display: block;", "D": "position: relative;"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "En plaçant le tableau dans un conteneur avec overflow-x: auto, on permet le défilement horizontal sur mobile.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle propriété permet d'ajouter un effet de survol (hover) sur les lignes d'un tableau ?",
            "options": '{"A": "table:hover", "B": "tr:hover", "C": "td:hover", "D": "tbody:hover"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "tr:hover { background-color: #ddd; } change l'arrière-plan des lignes au survol.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle est la valeur par défaut de text-align pour les en-têtes de tableau (th) ?",
            "options": '{"A": "left", "B": "right", "C": "center", "D": "justify"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "Par défaut, les en-têtes de tableau (th) sont centrés horizontalement.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle propriété CSS permet de définir la hauteur des lignes d'en-tête d'un tableau ?",
            "options": '{"A": "line-height", "B": "height", "C": "min-height", "D": "row-height"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "height: 50px; appliqué aux th ou tr permet de définir la hauteur des en-têtes.",
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
    print("🎓 INSERTION DU COURS: CSS TABLES - STYLISER LES TABLEAUX")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    cours_id = inserer_cours_css_tables()
    
    if cours_id:
        inserer_questions_css_tables(cours_id)
        print(f"\n🎉 Succès ! Cours 'CSS Tables - Styliser les Tableaux en CSS' créé (ID: {cours_id})")
    else:
        print("\n❌ Échec de l'insertion")

if __name__ == "__main__":
    main()