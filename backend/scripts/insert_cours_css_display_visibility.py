
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

def inserer_cours_css_display_visibility():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "css-display-visibility"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>👁️ CSS Display & Visibility - Contrôler l'Affichage des Éléments</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Les propriétés CSS <code>display</code> et <code>visibility</code> contrôlent comment les éléments sont affichés ou cachés sur la page, mais elles fonctionnent différemment.</p>
    </div>
    
    <h2>Introduction à Display et Visibility</h2>
    <p>La propriété <code>display</code> contrôle comment un élément est rendu (s'il est visible et comment il occupe l'espace).<br>
    La propriété <code>visibility</code> contrôle si un élément est visible mais conserve sa place dans la mise en page.</p>
    
    <h2>1. Masquer des éléments</h2>
    
    <h3>visibility: hidden</h3>
    <p>Cache l'élément mais <strong>conserve l'espace qu'il occupe</strong> dans la mise en page. Le reste du contenu ne se déplace pas.</p>
    
    <pre><code>/* Cache l'élément mais garde son espace */
.element {
    visibility: hidden;
}</code></pre>
    
    <h3>display: none</h3>
    <p>Supprime complètement l'élément. Il n'occupe <strong>aucun espace</strong> dans la mise en page. Les autres éléments se repositionnent comme si l'élément n'existait pas.</p>
    
    <pre><code>/* Supprime complètement l'élément */
.element {
    display: none;
}</code></pre>
    
    <div class="warning-box">
        <p><strong>⚠️ Différence clé :</strong>
        <br>- <code>visibility: hidden</code> → invisible mais l'espace reste réservé
        <br>- <code>display: none</code> → complètement supprimé, l'espace disparaît</p>
    </div>
    
    <h2>2. Éléments block vs inline</h2>
    
    <h3>Éléments block (display: block) :</h3>
    <ul>
        <li>Prennent toute la largeur disponible</li>
        <li>Forcent un saut de ligne avant et après</li>
        <li>Exemples : &lt;div&gt;, &lt;p&gt;, &lt;h1&gt; à &lt;h6&gt;, &lt;section&gt;, &lt;article&gt;</li>
    </ul>
    
    <h3>Éléments inline (display: inline) :</h3>
    <ul>
        <li>Ne prennent que la largeur nécessaire</li>
        <li>Pas de saut de ligne forcé</li>
        <li>Exemples : &lt;span&gt;, &lt;a&gt;, &lt;strong&gt;, &lt;em&gt;</li>
    </ul>
    
    <pre><code>/* Élément block par défaut */
div {
    display: block;
}

/* Élément inline par défaut */
span {
    display: inline;
}</code></pre>
    
    <h2>3. Modifier le comportement d'affichage</h2>
    <p>On peut modifier la valeur par défaut de <code>display</code> pour changer le comportement d'un élément.</p>
    
    <pre><code>/* Transformer un span inline en block */
span {
    display: block;
}

/* Transformer un lien inline en block */
a {
    display: block;
    width: 200px;
    height: 50px;
    background-color: lightblue;
}

/* Créer un menu horizontal avec display: inline */
li {
    display: inline;
    margin-right: 20px;
}</code></pre>
    
    <h2>4. Exemple pratique : menu de navigation</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;style&gt;
        /* Menu vertical standard */
        .vertical-menu {
            list-style-type: none;
            padding: 0;
        }
        
        .vertical-menu li {
            margin: 5px 0;
            background-color: #f0f0f0;
            padding: 10px;
        }
        
        /* Menu horizontal avec display: inline */
        .horizontal-menu {
            list-style-type: none;
            padding: 0;
            background-color: #333;
        }
        
        .horizontal-menu li {
            display: inline;
        }
        
        .horizontal-menu li a {
            display: inline-block;
            color: white;
            padding: 14px 16px;
            text-decoration: none;
        }
        
        .horizontal-menu li a:hover {
            background-color: #111;
        }
        
        /* Cacher des éléments */
        .hidden-visibility {
            visibility: hidden;
        }
        
        .hidden-display {
            display: none;
        }
    &lt;/style&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;h2&gt;Menu vertical&lt;/h2&gt;
    &lt;ul class="vertical-menu"&gt;
        &lt;li&gt;Accueil&lt;/li&gt;
        &lt;li&gt;Services&lt;/li&gt;
        &lt;li&gt;Contact&lt;/li&gt;
    &lt;/ul&gt;
    
    &lt;h2&gt;Menu horizontal (display: inline)&lt;/h2&gt;
    &lt;ul class="horizontal-menu"&gt;
        &lt;li&gt;&lt;a href="#"&gt;Accueil&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="#"&gt;Services&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="#"&gt;Contact&lt;/a&gt;&lt;/li&gt;
    &lt;/ul&gt;
    
    &lt;h2&gt;Démonstration visibility vs display&lt;/h2&gt;
    &lt;p&gt;Texte normal avant les éléments masqués.&lt;/p&gt;
    
    &lt;div style="background-color: yellow; padding: 10px;"&gt;
        Cet élément est visible
    &lt;/div&gt;
    
    &lt;div class="hidden-visibility" style="background-color: lightblue; padding: 10px;"&gt;
        visibility: hidden (l'espace reste)
    &lt;/div&gt;
    
    &lt;div style="background-color: lightgreen; padding: 10px;"&gt;
        Cet élément est visible
    &lt;/div&gt;
    
    &lt;div class="hidden-display" style="background-color: orange; padding: 10px;"&gt;
        display: none (l'espace disparaît)
    &lt;/div&gt;
    
    &lt;div style="background-color: pink; padding: 10px;"&gt;
        Cet élément est visible
    &lt;/div&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h2>5. Les différentes valeurs de display</h2>
    
    <ul>
        <li><strong>block</strong> : Élément block, prend toute la largeur</li>
        <li><strong>inline</strong> : Élément inline, prend la largeur nécessaire</li>
        <li><strong>inline-block</strong> : Mélange inline et block (permet largeur/hauteur, mais pas de saut de ligne)</li>
        <li><strong>none</strong> : Supprime complètement l'élément</li>
        <li><strong>flex</strong> : Conteneur flexbox</li>
        <li><strong>grid</strong> : Conteneur grid</li>
    </ul>
    
    <pre><code>/* Examples display */
.inline-block-element {
    display: inline-block;
    width: 100px;
    height: 100px;
    background-color: lightblue;
}

.flex-container {
    display: flex;
    justify-content: space-between;
}

.grid-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
}</code></pre>
    
    <div class="tip-box">
        <p><strong>💡 Astuce :</strong> Utilisez <code>display: none</code> pour masquer des éléments dynamiquement (ex: menus cachés). Utilisez <code>visibility: hidden</code> si vous avez besoin de conserver l'espace (ex: placeholders).</p>
    </div>
    
    <h2>6. Bonnes pratiques</h2>
    
    <ul>
        <li><strong>Utilisez display: none pour cacher complètement</strong> des éléments (menus, modales)</li>
        <li><strong>Utilisez visibility: hidden pour conserver l'espace</strong> (ex: pendant les animations)</li>
        <li><strong>Préférez inline-block</strong> pour créer des éléments qui ont besoin d'une largeur définie dans une ligne</li>
        <li><strong>display: inline</strong> est idéal pour les menus de navigation horizontaux</li>
        <li><strong>Évitez de changer display sur des éléments qui ont besoin d'une sémantique spécifique</strong></li>
    </ul>
    
    <div class="info-box">
        <p><strong>💡 Rappel :</strong> Modifier la valeur de <code>display</code> change comment l'élément est rendu visuellement, pas sa signification sémantique.</p>
    </div>
    """.strip()
    
    cours_data = {
        "titre": "CSS Display & Visibility - Contrôler l'Affichage",
        "slug": slug_cours,
        "description": "Apprenez la différence entre display et visibility en CSS. Découvrez comment masquer des éléments, la différence entre visibility: hidden et display: none, les différences entre éléments block et inline, et comment modifier le comportement d'affichage pour créer des mises en page flexibles.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 20,
        "ordre_affichage": 29,
        "chapitre_id": chapitre_id,
        "tags": ["css", "display", "visibility", "block", "inline", "inline-block", "none", "hidden", "masquer", "navigation", "debutant"],
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

def inserer_questions_css_display_visibility(cours_id):
    
    
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
            "question": "Quelle est la différence entre visibility: hidden et display: none ?",
            "options": '{"A": "Ils font exactement la même chose", "B": "visibility: hidden cache mais garde l\'espace, display: none supprime complètement l\'élément", "C": "display: none cache mais garde l\'espace, visibility: hidden supprime l\'élément", "D": "visibility: hidden fonctionne seulement sur mobile"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "visibility: hidden cache l'élément mais conserve son espace dans la mise en page. display: none supprime complètement l'élément, l'espace disparaît.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quel est le comportement par défaut d'un élément <span> en CSS ?",
            "options": '{"A": "block", "B": "inline", "C": "inline-block", "D": "flex"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "<span> est un élément inline par défaut, il ne prend que la largeur nécessaire.",
            "mode_specifique": "texte"
        },
        
        
        {
            "question": "Comment créer un menu horizontal avec une liste ul et des éléments li ?",
            "options": '{"A": "display: block;", "B": "display: inline;", "C": "display: none;", "D": "visibility: hidden;"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "display: inline sur les éléments li permet de les afficher horizontalement.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle valeur de display supprime complètement un élément de la mise en page ?",
            "options": '{"A": "hidden", "B": "invisible", "C": "none", "D": "collapse"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "display: none; supprime complètement l'élément, comme s'il n'existait pas.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quel est le comportement par défaut d'un élément <div> en CSS ?",
            "options": '{"A": "inline", "B": "inline-block", "C": "block", "D": "flex"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "<div> est un élément block par défaut, il prend toute la largeur disponible.",
            "mode_specifique": "audio"
        },
        
        
        {
            "question": "Que se passe-t-il quand on applique visibility: hidden à un élément ?",
            "options": '{"A": "L\'élément disparaît mais l\'espace reste vide", "B": "L\'élément disparaît et l\'espace est supprimé", "C": "L\'élément devient transparent mais reste cliquable", "D": "L\'élément est déplacé hors de l\'écran"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "visibility: hidden cache l'élément, mais l'espace qu'il occupait reste réservé dans la mise en page.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle propriété permet de combiner les avantages de block et inline (permet largeur/hauteur mais pas de saut de ligne) ?",
            "options": '{"A": "display: block", "B": "display: inline", "C": "display: inline-block", "D": "display: flex"}',
            "reponse_correcte": "C",
            "points": 15,
            "difficulte": "moyen",
            "explication": "inline-block permet de définir une largeur et une hauteur tout en restant sur la même ligne.",
            "mode_specifique": "video"
        },
        {
            "question": "Les éléments block ont quelle caractéristique ?",
            "options": '{"A": "Prennent toute la largeur disponible", "B": "Ne prennent que la largeur nécessaire", "C": "Restent sur la même ligne", "D": "Ne peuvent pas avoir de largeur définie"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "Les éléments block prennent toute la largeur disponible et forcent un saut de ligne.",
            "mode_specifique": "video"
        },
        {
            "question": "Que se passe-t-il quand on applique display: inline à un élément block comme un <div> ?",
            "options": '{"A": "Il devient invisible", "B": "Il reste block mais change de couleur", "C": "Il se comporte comme un élément inline", "D": "Il double de taille"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "display: inline transforme un élément block en élément inline, il ne prend plus que la largeur nécessaire.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle propriété CSS permet de supprimer complètement un élément ?",
            "options": '{"A": "opacity: 0;", "B": "visibility: hidden;", "C": "display: none;", "D": "hidden: true;"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "display: none; supprime complètement l'élément de la mise en page.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle est la différence entre display: inline-block et display: block ?",
            "options": '{"A": "inline-block permet de rester sur la même ligne, block force un saut", "B": "inline-block ne permet pas de largeur fixe", "C": "block ne permet pas de hauteur fixe", "D": "Il n\'y a pas de différence"}',
            "reponse_correcte": "A",
            "points": 15,
            "difficulte": "moyen",
            "explication": "inline-block permet à l'élément de rester sur la même ligne tout en acceptant largeur et hauteur, contrairement à block qui force un saut de ligne.",
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
    print("🎓 INSERTION DU COURS: CSS DISPLAY & VISIBILITY")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    cours_id = inserer_cours_css_display_visibility()
    
    if cours_id:
        inserer_questions_css_display_visibility(cours_id)
        print(f"\n🎉 Succès ! Cours 'CSS Display & Visibility - Contrôler l'Affichage' créé (ID: {cours_id})")
    else:
        print("\n❌ Échec de l'insertion")

if __name__ == "__main__":
    main()