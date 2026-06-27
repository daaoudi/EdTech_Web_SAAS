
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

def inserer_cours_css_lists():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "css-lists"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>📋 CSS Lists - Styliser les Listes en CSS</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Les listes HTML (<code>&lt;ul&gt;</code> et <code>&lt;ol&gt;</code>) peuvent être stylisées pour améliorer l'apparence et la lisibilité de votre contenu.</p>
    </div>
    
    <h2>Introduction aux Listes en CSS</h2>
    <p>CSS offre plusieurs propriétés pour personnaliser l'apparence des listes : changement des puces, positionnement, utilisation d'images personnalisées, et plus encore.</p>
    
    <div class="tip-box">
        <p><strong>💡 Types de listes :</strong>
        <br>- <strong>Listes non ordonnées (&lt;ul&gt;)</strong> : Utilisent des puces par défaut (•)
        <br>- <strong>Listes ordonnées (&lt;ol&gt;)</strong> : Utilisent des numéros par défaut (1, 2, 3...)</p>
    </div>
    
    <h2>1. La propriété list-style-type</h2>
    <p>La propriété <code>list-style-type</code> permet de changer le type de marqueur (puce ou numéro) des listes.</p>
    
    <h3>Valeurs pour les listes non ordonnées (&lt;ul&gt;) :</h3>
    <ul>
        <li><strong>disc</strong> : Puce pleine (par défaut)</li>
        <li><strong>circle</strong> : Puce creuse (cercle)</li>
        <li><strong>square</strong> : Puce carrée</li>
        <li><strong>none</strong> : Pas de puce</li>
    </ul>
    
    <h3>Valeurs pour les listes ordonnées (&lt;ol&gt;) :</h3>
    <ul>
        <li><strong>decimal</strong> : 1, 2, 3... (par défaut)</li>
        <li><strong>decimal-leading-zero</strong> : 01, 02, 03...</li>
        <li><strong>lower-roman</strong> : i, ii, iii, iv...</li>
        <li><strong>upper-roman</strong> : I, II, III, IV...</li>
        <li><strong>lower-alpha</strong> : a, b, c, d...</li>
        <li><strong>upper-alpha</strong> : A, B, C, D...</li>
        <li><strong>lower-greek</strong> : α, β, γ...</li>
    </ul>
    
    <pre><code>/* Listes non ordonnées */
ul.circle {
    list-style-type: circle;
}

ul.square {
    list-style-type: square;
}

ul.none {
    list-style-type: none;
}

/* Listes ordonnées */
ol.roman {
    list-style-type: upper-roman;
}

ol.alpha {
    list-style-type: lower-alpha;
}

ol.decimal-leading {
    list-style-type: decimal-leading-zero;
}</code></pre>
    
    <h2>2. La propriété list-style-position</h2>
    <p>La propriété <code>list-style-position</code> contrôle l'emplacement du marqueur par rapport au contenu de l'élément de liste.</p>
    
    <h3>Valeurs possibles :</h3>
    <ul>
        <li><strong>outside</strong> : Le marqueur est placé à l'extérieur du bloc de texte (par défaut)</li>
        <li><strong>inside</strong> : Le marqueur est placé à l'intérieur du bloc de texte</li>
    </ul>
    
    <pre><code>/* Marqueurs à l'intérieur */
ul.inside {
    list-style-position: inside;
}

/* Marqueurs à l'extérieur (par défaut) */
ul.outside {
    list-style-position: outside;
}

/* Exemple complet */
li {
    list-style-position: inside;
    background-color: #f0f0f0;
    margin: 5px 0;
    padding: 10px;
}</code></pre>
    
    <div class="info-box">
        <p><strong>📝 Différence :</strong> <code>inside</code> place le marqueur à l'intérieur du bloc, le texte se décale. <code>outside</code> place le marqueur à l'extérieur, le texte reste aligné.</p>
    </div>
    
    <h2>3. La propriété list-style-image</h2>
    <p>La propriété <code>list-style-image</code> permet de remplacer la puce standard par une image personnalisée.</p>
    
    <pre><code>/* Utiliser une image comme puce */
ul.custom {
    list-style-image: url('star.png');
}

/* Alternative : combiner avec list-style-type pour fallback */
ul.custom {
    list-style-image: url('star.png');
    list-style-type: square; /* fallback si l'image ne charge pas */
}</code></pre>
    
    <div class="tip-box">
        <p><strong>💡 Astuce :</strong> Toujours définir <code>list-style-type</code> comme fallback au cas où l'image personnalisée ne se charge pas.</p>
    </div>
    
    <h2>4. La propriété raccourcie list-style</h2>
    <p>La propriété <code>list-style</code> permet de définir <code>list-style-type</code>, <code>list-style-position</code> et <code>list-style-image</code> en une seule déclaration.</p>
    
    <pre><code>/* Syntaxe : list-style: type position image; */
ul {
    list-style: square inside url('puce.png');
}

/* Avec fallback */
ul {
    list-style: circle outside;
}

/* Sans puce */
ul {
    list-style: none;
}</code></pre>
    
    <h2>5. Supprimer complètement les marqueurs</h2>
    <p>Pour créer des menus de navigation ou des listes sans puces, on utilise souvent :</p>
    
    <pre><code>/* Supprimer les puces */
ul {
    list-style-type: none;
    padding: 0;
    margin: 0;
}

/* Menu horizontal */
.menu li {
    display: inline;
    margin-right: 20px;
}</code></pre>
    
    <h2>6. Styliser les listes imbriquées</h2>
    <p>Les listes peuvent contenir d'autres listes. On peut les styliser différemment :</p>
    
    <pre><code>/* Niveau 1 */
ul {
    list-style-type: square;
}

/* Niveau 2 (listes imbriquées) */
ul ul {
    list-style-type: circle;
}

/* Niveau 3 */
ul ul ul {
    list-style-type: disc;
}</code></pre>
    
    <h2>7. Exemple complet</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;style&gt;
        /* Liste 1 : Puces carrées */
        .list-square {
            list-style-type: square;
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
        }
        
        /* Liste 2 : Numéros romains */
        .list-roman {
            list-style-type: upper-roman;
            background-color: #e8f4f8;
            padding: 20px;
            border-radius: 8px;
        }
        
        /* Liste 3 : Puces personnalisées */
        .list-custom {
            list-style-image: url('checkmark.png');
            list-style-type: square; /* fallback */
            background-color: #f0f8e8;
            padding: 20px;
            border-radius: 8px;
        }
        
        /* Liste 4 : Menu de navigation */
        .nav-menu {
            list-style-type: none;
            padding: 0;
            margin: 0;
            background-color: #333;
            overflow: hidden;
        }
        
        .nav-menu li {
            float: left;
        }
        
        .nav-menu li a {
            display: block;
            color: white;
            text-align: center;
            padding: 14px 16px;
            text-decoration: none;
        }
        
        .nav-menu li a:hover {
            background-color: #111;
        }
        
        /* Position inside */
        .list-inside {
            list-style-position: inside;
            background-color: #fff3e0;
            padding: 10px;
        }
    &lt;/style&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;h2&gt;Liste avec puces carrées&lt;/h2&gt;
    &lt;ul class="list-square"&gt;
        &lt;li&gt;Élément 1&lt;/li&gt;
        &lt;li&gt;Élément 2&lt;/li&gt;
        &lt;li&gt;Élément 3&lt;/li&gt;
    &lt;/ul&gt;
    
    &lt;h2&gt;Liste avec numéros romains&lt;/h2&gt;
    &lt;ol class="list-roman"&gt;
        &lt;li&gt;Premier élément&lt;/li&gt;
        &lt;li&gt;Deuxième élément&lt;/li&gt;
        &lt;li&gt;Troisième élément&lt;/li&gt;
    &lt;/ol&gt;
    
    &lt;h2&gt;Menu de navigation (sans puces)&lt;/h2&gt;
    &lt;ul class="nav-menu"&gt;
        &lt;li&gt;&lt;a href="#"&gt;Accueil&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="#"&gt;Services&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="#"&gt;Contact&lt;/a&gt;&lt;/li&gt;
    &lt;/ul&gt;
    
    &lt;h2&gt;Position inside&lt;/h2&gt;
    &lt;ul class="list-inside"&gt;
        &lt;li&gt;Ce texte est aligné avec la puce&lt;/li&gt;
        &lt;li&gt;Les marqueurs sont à l'intérieur du bloc&lt;/li&gt;
    &lt;/ul&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h2>8. Bonnes pratiques</h2>
    
    <ul>
        <li><strong>Utilisez list-style-type: none</strong> pour les menus de navigation</li>
        <li><strong>Privilégiez les images vectorielles</strong> (SVG) pour list-style-image</li>
        <li><strong>Utilisez des fallbacks</strong> avec list-style-type quand vous utilisez list-style-image</li>
        <li><strong>Pensez à l'accessibilité</strong> : gardez une structure logique</li>
        <li><strong>Utilisez list-style-position: inside</strong> pour un meilleur contrôle sur mobile</li>
    </ul>
    
    <div class="info-box">
        <p><strong>💡 Astuce :</strong> Pour les menus de navigation, on utilise souvent <code>list-style-type: none</code> avec <code>display: inline</code> ou <code>display: inline-block</code>.</p>
    </div>
    """.strip()
    
    cours_data = {
        "titre": "CSS Lists - Styliser les Listes en CSS",
        "slug": slug_cours,
        "description": "Apprenez à styliser les listes HTML en CSS : list-style-type (changer les puces et numéros), list-style-position (position des marqueurs), list-style-image (images personnalisées), et la propriété raccourcie list-style. Découvrez comment créer des menus de navigation et des listes professionnelles.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 25,
        "ordre_affichage": 27,
        "chapitre_id": chapitre_id,
        "tags": ["css", "lists", "list-style-type", "list-style-position", "list-style-image", "list-style", "unordered-list", "ordered-list", "navigation", "debutant"],
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

def inserer_questions_css_lists(cours_id):
    
    
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
            "question": "Quelle propriété CSS permet de changer le type de puce d'une liste non ordonnée (ul) ?",
            "options": '{"A": "list-style-position", "B": "list-style-type", "C": "list-style-image", "D": "list-marker"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "list-style-type permet de changer le type de marqueur (disc, circle, square, none, etc.).",
            "mode_specifique": "texte"
        },
        {
            "question": "Quelle est la différence entre list-style-position: inside et outside ?",
            "options": '{"A": "inside place la puce à l\'intérieur du bloc texte, outside à l\'extérieur", "B": "inside place la puce à gauche, outside à droite", "C": "inside et outside font la même chose", "D": "inside est pour les listes imbriquées"}',
            "reponse_correcte": "A",
            "points": 15,
            "difficulte": "moyen",
            "explication": "inside place le marqueur à l'intérieur du bloc de texte, outside à l'extérieur (par défaut).",
            "mode_specifique": "texte"
        },
        
        
        {
            "question": "Comment remplacer la puce standard par une image personnalisée en CSS ?",
            "options": '{"A": "list-style-type: image;", "B": "list-style-image: url(\'image.png\');", "C": "list-marker: image(\'image.png\');", "D": "bullet-image: url(\'image.png\');"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "list-style-image: url('image.png'); permet d'utiliser une image personnalisée comme puce.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle est la propriété raccourcie pour définir tous les styles de liste en une seule déclaration ?",
            "options": '{"A": "list", "B": "list-style", "C": "ul-style", "D": "marker"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "list-style est la propriété raccourcie qui combine list-style-type, list-style-position et list-style-image.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle valeur de list-style-type faut-il utiliser pour supprimer complètement les puces d'une liste ?",
            "options": '{"A": "disc", "B": "circle", "C": "none", "D": "hidden"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "list-style-type: none; supprime les puces ou numéros d'une liste.",
            "mode_specifique": "audio"
        },
        
        
        {
            "question": "Quel est le type de marqueur par défaut pour une liste non ordonnée (ul) ?",
            "options": '{"A": "circle", "B": "square", "C": "disc", "D": "none"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "disc est le type de marqueur par défaut pour les listes non ordonnées (puce pleine).",
            "mode_specifique": "video"
        },
        {
            "question": "Comment créer un menu de navigation horizontal en CSS à partir d'une liste ul ?",
            "options": '{"A": "list-style-type: horizontal;", "B": "display: block;", "C": "display: inline; ou float: left;", "D": "list-style-position: horizontal;"}',
            "reponse_correcte": "C",
            "points": 15,
            "difficulte": "moyen",
            "explication": "On utilise display: inline ou float: left sur les éléments li pour créer un menu horizontal.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle valeur de list-style-type donne une puce carrée ?",
            "options": '{"A": "disc", "B": "circle", "C": "square", "D": "rectangle"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "square donne une puce carrée pour les listes non ordonnées.",
            "mode_specifique": "video"
        },
        {
            "question": "Pour les listes ordonnées (ol), quelle valeur donne des numéros romains majuscules (I, II, III) ?",
            "options": '{"A": "lower-roman", "B": "upper-roman", "C": "decimal", "D": "upper-alpha"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "upper-roman donne des numéros romains en majuscules (I, II, III, IV...).",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle propriété CSS faut-il souvent ajouter quand on utilise list-style-type: none ?",
            "options": '{"A": "margin: 0; padding: 0;", "B": "border: 0;", "C": "display: block;", "D": "float: left;"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "Il est souvent nécessaire de supprimer les marges et paddings par défaut avec margin: 0; padding: 0;.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle est la différence entre ul (unordered list) et ol (ordered list) ?",
            "options": '{"A": "ul utilise des puces, ol utilise des numéros", "B": "ul est pour les listes horizontales, ol pour les verticales", "C": "ul est pour les menus, ol pour le contenu", "D": "Il n\'y a pas de différence"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "ul utilise des puces (non ordonnée), ol utilise des numéros (ordonnée).",
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
    print("🎓 INSERTION DU COURS: CSS LISTS - STYLISER LES LISTES")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    cours_id = inserer_cours_css_lists()
    
    if cours_id:
        inserer_questions_css_lists(cours_id)
        print(f"\n🎉 Succès ! Cours 'CSS Lists - Styliser les Listes en CSS' créé (ID: {cours_id})")
    else:
        print("\n❌ Échec de l'insertion")

if __name__ == "__main__":
    main()