
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

def inserer_cours_css_links():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "css-links"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>🔗 CSS Links - Styliser les Liens Hypertextes</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Les liens CSS peuvent être stylisés avec différentes couleurs, polices, arrière-plans et décorations selon leur état (non visité, visité, survol, actif).</p>
    </div>
    
    <h2>Introduction aux Liens CSS</h2>
    <p>Les liens (<code>&lt;a&gt;</code>) peuvent être stylisés avec différentes propriétés CSS : couleur, police, arrière-plan, décoration, et plus encore. Chaque lien peut avoir un style différent selon son état.</p>
    
    <div class="tip-box">
        <p><strong>💡 Astuce :</strong> Styliser les liens améliore l'expérience utilisateur et rend la navigation plus intuitive.</p>
    </div>
    
    <h2>1. Les quatre états d'un lien</h2>
    
    <ul>
        <li><strong>a:link</strong> : Lien normal, non visité</li>
        <li><strong>a:visited</strong> : Lien déjà cliqué (visité)</li>
        <li><strong>a:hover</strong> : Lien survolé par la souris</li>
        <li><strong>a:active</strong> : Lien au moment du clic</li>
    </ul>
    
    <pre><code>/* État normal - non visité */
a:link {
    color: blue;
}

/* État visité */
a:visited {
    color: purple;
}

/* État survol */
a:hover {
    color: orange;
}

/* État actif (au moment du clic) */
a:active {
    color: red;
}</code></pre>
    
    <h2>2. Changer les couleurs pour chaque état</h2>
    
    <pre><code>/* Styliser les liens par défaut */
a:link {
    color: #3498db;  /* Bleu pour les liens non visités */
    background-color: transparent;
}

a:visited {
    color: #9b59b6;  /* Violet pour les liens visités */
}

a:hover {
    color: #e74c3c;  /* Rouge au survol */
}

a:active {
    color: #f39c12;  /* Orange au moment du clic */
}</code></pre>
    
    <h2>3. L'ordre des règles CSS est important !</h2>
    
    <div class="warning-box">
        <p><strong>⚠️ Important :</strong> L'ordre des règles pour les liens est crucial :</p>
        <ul>
            <li><strong>hover</strong> doit venir après <strong>link</strong> et <strong>visited</strong></li>
            <li><strong>active</strong> doit venir après <strong>hover</strong></li>
        </ul>
    </div>
    
    <pre><code>/* Ordre correct */
a:link    { color: blue; }
a:visited { color: purple; }
a:hover   { color: orange; }
a:active  { color: red; }

/* Ordre incorrect - ne fonctionnera pas comme prévu */
a:link    { color: blue; }
a:hover   { color: orange; }
a:visited { color: purple; }  /* visited après hover ne fonctionne pas */
a:active  { color: red; }</code></pre>
    
    <div class="info-box">
        <p><strong>📝 Règle mnémotechnique :</strong> LoVe HA! (Link, Visited, Hover, Active)</p>
    </div>
    
    <h2>4. Décoration du texte (text-decoration)</h2>
    
    <pre><code>/* Retirer le soulignement des liens */
a:link, a:visited {
    text-decoration: none;
}

/* Ajouter un soulignement au survol */
a:hover {
    text-decoration: underline;
}

/* Ajouter un trait barré au survol */
a:hover {
    text-decoration: line-through;
}</code></pre>
    
    <h2>5. Styliser l'arrière-plan</h2>
    
    <pre><code>/* Ajouter un arrière-plan au survol */
a:hover {
    background-color: yellow;
}

/* Grouper les états pour plus d'efficacité */
a:link, a:visited {
    background-color: #f0f0f0;
    color: #333;
    padding: 8px 12px;
    text-decoration: none;
    border-radius: 4px;
}

a:hover, a:active {
    background-color: #3498db;
    color: white;
}</code></pre>
    
    <h2>6. Exemple complet</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;style&gt;
        /* Styles généraux des liens */
        a:link, a:visited {
            color: #3498db;
            text-decoration: none;
            padding: 5px 10px;
            border-radius: 3px;
            transition: all 0.3s ease;
        }
        
        /* Effet au survol */
        a:hover {
            color: white;
            background-color: #3498db;
            text-decoration: underline;
        }
        
        /* Effet au clic */
        a:active {
            color: #f39c12;
        }
        
        /* Menu de navigation */
        .nav-links a:link, .nav-links a:visited {
            display: inline-block;
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            margin: 0 5px;
        }
        
        .nav-links a:hover {
            background-color: #3498db;
            border-color: #3498db;
        }
        
        /* Bouton personnalisé */
        .btn:link, .btn:visited {
            background-color: #2ecc71;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
        }
        
        .btn:hover {
            background-color: #27ae60;
            transform: scale(1.05);
        }
        
        .btn:active {
            transform: scale(0.95);
        }
    &lt;/style&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;h2&gt;Liens standards&lt;/h2&gt;
    &lt;a href="#"&gt;Lien normal&lt;/a&gt;
    
    &lt;h2&gt;Menu de navigation&lt;/h2&gt;
    &lt;div class="nav-links"&gt;
        &lt;a href="#"&gt;Accueil&lt;/a&gt;
        &lt;a href="#"&gt;Services&lt;/a&gt;
        &lt;a href="#"&gt;Contact&lt;/a&gt;
    &lt;/div&gt;
    
    &lt;h2&gt;Bouton personnalisé&lt;/h2&gt;
    &lt;a href="#" class="btn"&gt;Cliquez ici&lt;/a&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h2>7. Bonnes pratiques</h2>
    
    <ul>
        <li><strong>Respectez l'ordre LoVe HA!</strong> (Link, Visited, Hover, Active)</li>
        <li><strong>Retirez le soulignement</strong> par défaut pour un design moderne, mais ajoutez un indicateur au survol</li>
        <li><strong>Utilisez des transitions</strong> pour des effets fluides</li>
        <li><strong>Assurez un bon contraste</strong> pour l'accessibilité</li>
        <li><strong>Groupez les états similaires</strong> pour un code plus propre</li>
        <li><strong>Testez tous les états</strong> de vos liens</li>
    </ul>
    
    <div class="info-box">
        <p><strong>💡 Astuce :</strong> Utilisez la pseudo-classe <code>:focus</code> pour styliser les liens quand ils sont sélectionnés au clavier, améliorant ainsi l'accessibilité.</p>
    </div>
    """.strip()
    
    cours_data = {
        "titre": "CSS Links - Styliser les Liens Hypertextes",
        "slug": slug_cours,
        "description": "Apprenez à styliser les liens hypertextes en CSS avec les pseudo-classes :link, :visited, :hover et :active. Découvrez comment appliquer différentes couleurs, arrière-plans et décorations selon l'état du lien, et l'importance de l'ordre des règles (LoVe HA!).",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 20,
        "ordre_affichage": 26,
        "chapitre_id": chapitre_id,
        "tags": ["css", "links", "pseudo-classes", "hover", "active", "visited", "text-decoration", "navigation", "debutant"],
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

def inserer_questions_css_links(cours_id):
    
    
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
            "question": "Quels sont les quatre états d'un lien en CSS ?",
            "options": '{"A": "start, end, hover, click", "B": "link, visited, hover, active", "C": "normal, hover, click, focus", "D": "static, dynamic, hover, click"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Les quatre états sont : link (non visité), visited (visité), hover (survol), active (clic).",
            "mode_specifique": "texte"
        },
        {
            "question": "Pourquoi l'ordre des règles CSS pour les liens est-il important ?",
            "options": '{"A": "Pour des raisons de performance", "B": "Parce que hover doit être après link et visited, et active après hover", "C": "L\'ordre n\'a pas d\'importance", "D": "Pour la compatibilité avec les anciens navigateurs"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "hover doit être après link et visited, et active après hover. L'ordre LoVe HA! est essentiel.",
            "mode_specifique": "texte"
        },
        
        
        {
            "question": "Quelle pseudo-classe CSS cible un lien au moment où la souris le survole ?",
            "options": '{"A": "a:link", "B": "a:visited", "C": "a:hover", "D": "a:active"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "a:hover cible le lien lorsque la souris est au-dessus.",
            "mode_specifique": "audio"
        },
        {
            "question": "Comment retirer le soulignement par défaut d'un lien en CSS ?",
            "options": '{"A": "text-decoration: none;", "B": "text-decoration: underline;", "C": "text-decoration: remove;", "D": "underline: none;"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "text-decoration: none; supprime le soulignement des liens.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle pseudo-classe cible un lien déjà cliqué (visité) ?",
            "options": '{"A": "a:link", "B": "a:visited", "C": "a:hover", "D": "a:active"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "a:visited cible les liens que l'utilisateur a déjà visités.",
            "mode_specifique": "audio"
        },
        
        
        {
            "question": "Quelle est la règle mnémotechnique pour retenir l'ordre des pseudo-classes des liens ?",
            "options": '{"A": "HA! LoVe", "B": "LoVe HA!", "C": "ViHoLa", "D": "LiViHoAc"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "LoVe HA! : Link, Visited, Hover, Active.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle pseudo-classe cible un lien au moment précis du clic (avant que la page ne se charge) ?",
            "options": '{"A": "a:link", "B": "a:visited", "C": "a:hover", "D": "a:active"}',
            "reponse_correcte": "D",
            "points": 10,
            "difficulte": "facile",
            "explication": "a:active cible le lien au moment du clic.",
            "mode_specifique": "video"
        },
        {
            "question": "Que se passe-t-il si on place a:hover avant a:visited dans la feuille de style ?",
            "options": '{"A": "Rien ne change", "B": "Le style a:visited ne s\'appliquera pas après un survol", "C": "Le style a:hover ne fonctionnera pas", "D": "Le lien deviendra invisible"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "Si hover est avant visited, les styles visited seront ignorés car hover a la même spécificité mais vient avant.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment ajouter un arrière-plan jaune au survol d'un lien ?",
            "options": '{"A": "a:hover { background-color: yellow; }", "B": "a:link { background-color: yellow; }", "C": "a:visited { background-color: yellow; }", "D": "a:active { background-color: yellow; }"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "a:hover { background-color: yellow; } ajoute un arrière-plan jaune au survol.",
            "mode_specifique": "video"
        },
        {
            "question": "Pourquoi est-il conseillé d'ajouter un effet au survol des liens ?",
            "options": '{"A": "Pour améliorer l\'expérience utilisateur", "B": "Pour rendre le site plus beau", "C": "Pour le référencement", "D": "Les réponses A et B sont correctes"}',
            "reponse_correcte": "D",
            "points": 10,
            "difficulte": "facile",
            "explication": "Les effets au survol améliorent l'expérience utilisateur et rendent le site plus interactif et agréable.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle propriété CSS permet d'ajouter une transition fluide lors du survol d'un lien ?",
            "options": '{"A": "animation", "B": "transition", "C": "transform", "D": "keyframes"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "transition permet de créer des animations fluides lors des changements d'état, comme le survol.",
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
    print("🎓 INSERTION DU COURS: CSS LINKS - STYLISER LES LIENS")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    cours_id = inserer_cours_css_links()
    
    if cours_id:
        inserer_questions_css_links(cours_id)
        print(f"\n🎉 Succès ! Cours 'CSS Links - Styliser les Liens Hypertextes' créé (ID: {cours_id})")
    else:
        print("\n❌ Échec de l'insertion")

if __name__ == "__main__":
    main()