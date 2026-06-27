
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

def inserer_cours_css_overflow():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "css-overflow"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>📦 CSS Overflow - Gérer le Dépassement de Contenu</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> La propriété <code>overflow</code> contrôle comment le contenu se comporte lorsqu'il ne rentre pas à l'intérieur de son élément parent.</p>
    </div>
    
    <h2>Introduction à Overflow</h2>
    <p>Le dépassement (overflow) se produit lorsque le contenu dépasse les limites de son conteneur parent. CSS offre différentes façons de gérer cette situation.</p>
    
    <div class="tip-box">
        <p><strong>💡 Cas d'usage :</strong> overflow est essentiel pour les boîtes de texte, les cartes de contenu, les galeries d'images, et les zones de commentaires.</p>
    </div>
    
    <h2>Les différentes valeurs d'overflow</h2>
    
    <h3>1. visible (valeur par défaut)</h3>
    <p>Le contenu qui dépasse s'affiche en dehors de la boîte, sans aucune restriction. C'est le comportement normal.</p>
    
    <pre><code>.box {
    width: 200px;
    height: 100px;
    overflow: visible; /* Par défaut, le contenu dépasse visiblement */
}</code></pre>
    
    <div class="info-box">
        <p><strong>📝 Note :</strong> Le contenu reste accessible même s'il dépasse visuellement de son conteneur.</p>
    </div>
    
    <h3>2. hidden</h3>
    <p>Le contenu qui dépasse est coupé (caché) et n'est pas affiché. Cependant, il reste accessible (ex: copier-coller).</p>
    
    <pre><code>.box {
    width: 200px;
    height: 100px;
    overflow: hidden; /* Le contenu excédentaire est coupé */
}</code></pre>
    
    <div class="tip-box">
        <p><strong>💡 Cas d'usage :</strong> Masquer les débordements dans des designs précis où l'espace est limité.</p>
    </div>
    
    <h3>3. clip</h3>
    <p>Similaire à <code>hidden</code>, mais fonctionne avec la propriété <code>overflow-clip-margin</code>. Permet un dépassement partiel jusqu'à une certaine marge avant de cacher le reste.</p>
    
    <pre><code>.box {
    width: 200px;
    height: 100px;
    overflow: clip;
    overflow-clip-margin: 10px; /* Permet 10px de dépassement avant le clipping */
}</code></pre>
    
    <div class="info-box">
        <p><strong>📝 Note :</strong> <code>clip</code> est une valeur plus récente, idéale pour un contrôle précis du débordement.</p>
    </div>
    
    <h3>4. scroll</h3>
    <p>Ajoute des barres de défilement (verticales et horizontales) quel que soit le contenu. Les barres apparaissent même si elles ne sont pas nécessaires.</p>
    
    <pre><code>.box {
    width: 200px;
    height: 100px;
    overflow: scroll; /* Barres de défilement toujours présentes */
}</code></pre>
    
    <div class="warning-box">
        <p><strong>⚠️ Inconvénient :</strong> Les barres de défilement s'affichent même quand le contenu rentre, ce qui peut être inesthétique.</p>
    </div>
    
    <h3>5. auto</h3>
    <p>Ajoute des barres de défilement uniquement lorsque cela est nécessaire. C'est la solution la plus propre et recommandée.</p>
    
    <pre><code>.box {
    width: 200px;
    height: 100px;
    overflow: auto; /* Barres de défilement seulement si nécessaire */
}</code></pre>
    
    <div class="tip-box">
        <p><strong>💡 Recommandation :</strong> Utilisez <code>overflow: auto</code> pour un affichage propre avec défilement conditionnel.</p>
    </div>
    
    <h2>Overflow sur axes spécifiques</h2>
    <p>Vous pouvez contrôler séparément l'overflow horizontal et vertical :</p>
    
    <pre><code>/* Contrôle séparé */
.box {
    overflow-x: auto;   /* Gère le débordement horizontal */
    overflow-y: scroll; /* Gère le débordement vertical */
}</code></pre>
    
    <h2>Exemple complet</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;style&gt;
        .container {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        
        .box {
            width: 250px;
            height: 150px;
            border: 2px solid #333;
            margin: 10px;
            font-family: Arial, sans-serif;
        }
        
        .box-visible {
            overflow: visible;
            background-color: #f8f9fa;
        }
        
        .box-hidden {
            overflow: hidden;
            background-color: #e8f4f8;
        }
        
        .box-clip {
            overflow: clip;
            overflow-clip-margin: 15px;
            background-color: #f0f8e8;
        }
        
        .box-scroll {
            overflow: scroll;
            background-color: #ffe8e8;
        }
        
        .box-auto {
            overflow: auto;
            background-color: #f8e8ff;
        }
        
        .content {
            width: 300px;
            padding: 10px;
        }
        
        h3 {
            margin: 0 0 10px 0;
            padding: 8px;
            background-color: rgba(0,0,0,0.1);
        }
        
        .long-text {
            width: 100%;
        }
    &lt;/style&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;h1&gt;Démonstration des propriétés Overflow&lt;/h1&gt;
    
    &lt;div class="container"&gt;
        &lt;div class="box box-visible"&gt;
            &lt;h3&gt;overflow: visible&lt;/h3&gt;
            &lt;div class="content"&gt;
                Ce texte dépasse du conteneur visiblement. Lorem ipsum dolor sit amet.
            &lt;/div&gt;
        &lt;/div&gt;
        
        &lt;div class="box box-hidden"&gt;
            &lt;h3&gt;overflow: hidden&lt;/h3&gt;
            &lt;div class="content"&gt;
                Ce texte dépasse du conteneur mais est coupé (caché).
            &lt;/div&gt;
        &lt;/div&gt;
        
        &lt;div class="box box-scroll"&gt;
            &lt;h3&gt;overflow: scroll&lt;/h3&gt;
            &lt;div class="content"&gt;
                Barres de défilement toujours présentes, même avec peu de texte.
            &lt;/div&gt;
        &lt;/div&gt;
        
        &lt;div class="box box-auto"&gt;
            &lt;h3&gt;overflow: auto&lt;/h3&gt;
            &lt;div class="content"&gt;
                Avec peu de texte, pas de barre. Avec un texte très long qui dépasse, une barre de défilement apparaît automatiquement.
            &lt;/div&gt;
        &lt;/div&gt;
    &lt;/div&gt;
    
    &lt;h2&gt;Exemple pratique : zone de commentaires&lt;/h2&gt;
    &lt;div style="width: 300px; height: 150px; overflow: auto; border: 1px solid #ccc; padding: 10px;"&gt;
        &lt;p&gt;Commentaire 1 : Excellent tutoriel !&lt;/p&gt;
        &lt;p&gt;Commentaire 2 : Très utile, merci !&lt;/p&gt;
        &lt;p&gt;Commentaire 3 : Je vais partager ces exemples.&lt;/p&gt;
        &lt;p&gt;Commentaire 4 : Le CSS overflow est essentiel à maîtriser.&lt;/p&gt;
        &lt;p&gt;Commentaire 5 : Enfin une explication claire !&lt;/p&gt;
    &lt;/div&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h2>Résumé des valeurs overflow</h2>
    
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left;">Valeur</th>
            <th style="padding: 8px; text-align: left;">Comportement</th>
            <th style="padding: 8px; text-align: left;">Cas d'usage</th>
        </thead>
        <tbody>
            <tr><td style="padding: 8px;"><strong>visible</strong></td><td style="padding: 8px;">Débordement visible, par défaut</td><td style="padding: 8px;">Contenu qui peut dépasser</td></tr>
            <tr><td style="padding: 8px;"><strong>hidden</strong></td><td style="padding: 8px;">Débordement coupé/caché</td><td style="padding: 8px;">Contenu à masquer</td></tr>
            <tr><td style="padding: 8px;"><strong>clip</strong></td><td style="padding: 8px;">Débordement coupé avec marge</td><td style="padding: 8px;">Contrôle précis</td></tr>
            <tr><td style="padding: 8px;"><strong>scroll</strong></td><td style="padding: 8px;">Barres de défilement permanentes</td><td style="padding: 8px;">Zones de texte, commentaires</td></tr>
            <tr><td style="padding: 8px;"><strong>auto</strong></td><td style="padding: 8px;">Barres conditionnelles</td><td style="padding: 8px;">Recommandé</td></tr>
        </tbody>
    </table>
    
    <h2>Bonnes pratiques</h2>
    
    <ul>
        <li><strong>Utilisez overflow: auto</strong> plutôt que scroll pour une meilleure expérience utilisateur</li>
        <li><strong>overflow: hidden</strong> peut masquer accidentellement du contenu important</li>
        <li><strong>overflow: clip</strong> est idéal pour des designs où vous voulez un dépassement contrôlé</li>
        <li><strong>Testez sur différents navigateurs</strong> car le rendu des barres de défilement varie</li>
        <li><strong>Combinez avec max-width et max-height</strong> pour des conteneurs responsives</li>
        <li><strong>Pour du texte long</strong>, préférez auto pour permettre le défilement sans barres inutiles</li>
    </ul>
    
    <div class="info-box">
        <p><strong>💡 Astuce :</strong> Utilisez <code>overflow-x</code> et <code>overflow-y</code> pour contrôler séparément les axes horizontal et vertical.</p>
    </div>
    """.strip()
    
    cours_data = {
        "titre": "CSS Overflow - Gérer le Dépassement de Contenu",
        "slug": slug_cours,
        "description": "Apprenez à maîtriser la propriété CSS overflow pour gérer le contenu qui dépasse de son conteneur. Découvrez les valeurs visible, hidden, clip, scroll et auto, ainsi que leur utilisation pratique pour créer des boîtes de texte, zones de commentaires et interfaces responsives.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 15,
        "ordre_affichage": 31,
        "chapitre_id": chapitre_id,
        "tags": ["css", "overflow", "overflow-x", "overflow-y", "hidden", "scroll", "auto", "visible", "clip", "debutant"],
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

def inserer_questions_css_overflow(cours_id):
    
    
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
            "question": "Quelle est la valeur par défaut de la propriété CSS overflow ?",
            "options": '{"A": "hidden", "B": "scroll", "C": "visible", "D": "auto"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "overflow: visible est la valeur par défaut. Le contenu qui dépasse s'affiche en dehors de la boîte.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quelle valeur d'overflow ajoute des barres de défilement uniquement lorsque c'est nécessaire ?",
            "options": '{"A": "scroll", "B": "auto", "C": "hidden", "D": "visible"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "overflow: auto ajoute des barres de défilement seulement si le contenu dépasse le conteneur.",
            "mode_specifique": "texte"
        },
        
        
        {
            "question": "Comment couper (cacher) le contenu qui dépasse d'un élément ?",
            "options": '{"A": "overflow: visible", "B": "overflow: hidden", "C": "overflow: scroll", "D": "overflow: auto"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "overflow: hidden coupe et cache le contenu qui dépasse du conteneur.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle valeur d'overflow ajoute des barres de défilement quel que soit le contenu ?",
            "options": '{"A": "scroll", "B": "auto", "C": "hidden", "D": "visible"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "overflow: scroll ajoute toujours des barres de défilement, même si le contenu rentre parfaitement.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle propriété permet de contrôler le débordement horizontal uniquement ?",
            "options": '{"A": "overflow", "B": "overflow-y", "C": "overflow-x", "D": "overflow-clip"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "overflow-x contrôle le débordement horizontal, tandis que overflow-y contrôle le vertical.",
            "mode_specifique": "audio"
        },
        
        
        {
            "question": "Que signifie overflow: clip ?",
            "options": '{"A": "Ajoute des barres de défilement", "B": "Similaire à hidden mais permet un dépassement partiel avec marge", "C": "Affiche le contenu qui dépasse", "D": "Supprime le contenu qui dépasse"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "clip est similaire à hidden mais fonctionne avec overflow-clip-margin pour permettre un dépassement partiel.",
            "mode_specifique": "video"
        },
        {
            "question": "Quel est l'inconvénient principal de overflow: scroll ?",
            "options": '{"A": "Il cache le contenu", "B": "Il affiche toujours des barres de défilement, même si inutiles", "C": "Il ne fonctionne pas sur mobile", "D": "Il ralentit la page"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "scroll affiche toujours des barres de défilement, même quand le contenu rentre, ce qui peut être inesthétique.",
            "mode_specifique": "video"
        },
        {
            "question": "Avec overflow: hidden, le contenu caché est-il accessible par copier-coller ?",
            "options": '{"A": "Non, il est complètement inaccessible", "B": "Oui, il reste accessible", "C": "Seulement sur certains navigateurs", "D": "Oui, mais uniquement sur mobile"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "Même avec hidden, le contenu reste dans le DOM et est accessible (copier-coller, inspecteur, etc.)",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle valeur d'overflow est recommandée pour une zone de texte qui peut contenir beaucoup de contenu ?",
            "options": '{"A": "scroll", "B": "hidden", "C": "visible", "D": "auto"}',
            "reponse_correcte": "D",
            "points": 10,
            "difficulte": "facile",
            "explication": "auto est recommandé car il ajoute des barres de défilement uniquement si nécessaire.",
            "mode_specifique": "video"
        },
        {
            "question": "Laquelle de ces affirmations sur overflow: visible est correcte ?",
            "options": '{"A": "Cache le contenu qui dépasse", "B": "Ajoute des barres de défilement", "C": "Le contenu qui dépasse s\'affiche hors de la boîte", "D": "Supprime le contenu qui dépasse"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "visible permet au contenu qui dépasse de s'afficher en dehors de la boîte.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment permettre un défilement vertical uniquement sur un élément ?",
            "options": '{"A": "overflow: auto;", "B": "overflow-y: auto; overflow-x: hidden;", "C": "overflow: scroll;", "D": "overflow-y: scroll; overflow-x: scroll;"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "overflow-y: auto; permet le défilement vertical, overflow-x: hidden; bloque le défilement horizontal.",
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
    print("🎓 INSERTION DU COURS: CSS OVERFLOW")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    cours_id = inserer_cours_css_overflow()
    
    if cours_id:
        inserer_questions_css_overflow(cours_id)
        print(f"\n🎉 Succès ! Cours 'CSS Overflow - Gérer le Dépassement de Contenu' créé (ID: {cours_id})")
    else:
        print("\n❌ Échec de l'insertion")

if __name__ == "__main__":
    main()