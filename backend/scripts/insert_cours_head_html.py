
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
        cur.execute("SELECT id FROM chapitres WHERE titre ILIKE %s", (f'%{chapitre_titre}%',))
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result:
            return result[0]
        return None
    except Exception as e:
        print(f"⚠️ Erreur récupération chapitre: {e}")
        return None

def inserer_cours_head():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    
    chapitre_id = get_chapitre_id("HTML")
    if chapitre_id:
        print(f"📚 Chapitre HTML trouvé (ID: {chapitre_id})")
    else:
        print("⚠️ Chapitre HTML non trouvé, le cours sera inséré sans chapitre")
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    
    slug_cours = "head-html-metadata"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    
    contenu_html = """
    <h1>🧩 La balise &lt;head&gt; en HTML</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> La section &lt;head&gt; contient des métadonnées sur la page web, c'est-à-dire des informations qui ne sont pas visibles directement par l'utilisateur mais qui sont essentielles pour le fonctionnement, le référencement et l'accessibilité.</p>
    </div>
    
    <h2>Introduction</h2>
    <p>La balise <code>&lt;head&gt;</code> est l'une des sections fondamentales d'un document HTML. Elle se place entre la balise <code>&lt;html&gt;</code> et la balise <code>&lt;body&gt;</code>. Contrairement au contenu du <code>&lt;body&gt;</code>, ce qui se trouve dans le <code>&lt;head&gt;</code> n'est pas affiché directement sur la page.</p>
    
    <h2>1. Les éléments essentiels du &lt;head&gt;</h2>
    
    <h3>1.1 La balise &lt;title&gt;</h3>
    <p>La balise <code>&lt;title&gt;</code> définit le titre de la page, qui apparaît dans l'onglet du navigateur, dans les favoris, et dans les résultats des moteurs de recherche.</p>
    
    <pre><code>&lt;title&gt;Mon Super Site Web - Accueil&lt;/title&gt;</code></pre>
    
    <div class="tip-box">
        <p><strong>💡 Astuce SEO :</strong> Un bon titre doit être descriptif, unique par page, et contenir des mots-clés pertinents (environ 50-60 caractères).</p>
    </div>
    
    <h3>1.2 La balise &lt;meta&gt; pour le jeu de caractères</h3>
    <p>L'encodage des caractères est crucial pour afficher correctement tous les caractères spéciaux (accents, symboles, etc.).</p>
    
    <pre><code>&lt;meta charset="UTF-8"&gt;</code></pre>
    
    <h3>1.3 La balise &lt;meta&gt; pour la description</h3>
    <p>La meta description est utilisée par les moteurs de recherche pour afficher un extrait sous le titre dans les résultats de recherche.</p>
    
    <pre><code>&lt;meta name="description" content="Apprenez le HTML avec des tutoriels complets et interactifs pour débutants."&gt;</code></pre>
    
    <div class="tip-box">
        <p><strong>💡 Astuce SEO :</strong> La description doit être unique, attrayante, et contenir environ 150-160 caractères.</p>
    </div>
    
    <h3>1.4 La balise &lt;meta&gt; pour les mots-clés</h3>
    <p>Autrefois très importante pour le SEO, cette balise est maintenant moins utilisée mais peut encore être utile.</p>
    
    <pre><code>&lt;meta name="keywords" content="HTML, CSS, JavaScript, tutoriel, débutant"&gt;</code></pre>
    
    <h3>1.5 La balise &lt;meta&gt; pour le viewport (responsive)</h3>
    <p>Essentielle pour le responsive design, cette balise contrôle comment la page s'affiche sur les appareils mobiles.</p>
    
    <pre><code>&lt;meta name="viewport" content="width=device-width, initial-scale=1.0"&gt;</code></pre>
    
    <h2>2. Liaison avec des ressources externes</h2>
    
    <h3>2.1 La balise &lt;link&gt; pour les feuilles de style CSS</h3>
    <p>Pour lier un fichier CSS externe à votre page HTML :</p>
    
    <pre><code>&lt;link rel="stylesheet" href="styles.css"&gt;</code></pre>
    
    <h3>2.2 La balise &lt;link&gt; pour les icônes (favicon)</h3>
    <p>Le favicon est la petite icône qui apparaît dans l'onglet du navigateur à côté du titre.</p>
    
    <pre><code>&lt;link rel="icon" type="image/x-icon" href="favicon.ico"&gt;</code></pre>
    
    <h3>2.3 La balise &lt;script&gt; pour JavaScript</h3>
    <p>Bien que les scripts puissent être placés dans le <code>&lt;head&gt;</code>, il est souvent recommandé de les placer en bas du <code>&lt;body&gt;</code> pour ne pas bloquer le chargement de la page.</p>
    
    <pre><code>&lt;script src="script.js"&gt;&lt;/script&gt;</code></pre>
    
    <h2>3. Métadonnées pour les réseaux sociaux (Open Graph)</h2>
    <p>Ces balises contrôlent l'apparence de votre page lorsqu'elle est partagée sur les réseaux sociaux comme Facebook, LinkedIn, etc.</p>
    
    <pre><code>&lt;meta property="og:title" content="Titre pour les réseaux sociaux"&gt;
&lt;meta property="og:description" content="Description pour les réseaux sociaux"&gt;
&lt;meta property="og:image" content="https://monsite.com/image.jpg"&gt;
&lt;meta property="og:url" content="https://monsite.com/page"&gt;
&lt;meta property="og:type" content="website"&gt;</code></pre>
    
    <h2>4. Structure complète d'une page HTML avec &lt;head&gt;</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html lang="fr"&gt;
&lt;head&gt;
    &lt;meta charset="UTF-8"&gt;
    &lt;meta name="viewport" content="width=device-width, initial-scale=1.0"&gt;
    &lt;meta name="description" content="Description de ma page"&gt;
    &lt;meta name="keywords" content="HTML, CSS, tutoriel"&gt;
    &lt;meta name="author" content="Mon Nom"&gt;
    
    &lt;title&gt;Mon Super Site Web&lt;/title&gt;
    
    &lt;link rel="stylesheet" href="style.css"&gt;
    &lt;link rel="icon" type="image/x-icon" href="favicon.ico"&gt;
    
    &lt;!-- Open Graph pour les réseaux sociaux --&gt;
    &lt;meta property="og:title" content="Mon Super Site Web"&gt;
    &lt;meta property="og:description" content="Apprenez le HTML facilement"&gt;
    &lt;meta property="og:image" content="https://monsite.com/preview.jpg"&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;!-- Contenu visible de la page --&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h2>5. Bonnes pratiques pour le &lt;head&gt;</h2>
    
    <ul>
        <li><strong>Toujours inclure <code>&lt;meta charset="UTF-8"&gt;</code></strong> pour un affichage correct des caractères</li>
        <li><strong>Inclure la balise viewport</strong> pour le responsive design</li>
        <li><strong>Donner un titre unique et descriptif</strong> à chaque page</li>
        <li><strong>Utiliser la meta description</strong> pour améliorer le SEO</li>
        <li><strong>Placer les liens CSS tôt dans le <code>&lt;head&gt;</code></strong> pour éviter le FOUC (Flash of Unstyled Content)</li>
        <li><strong>Minimiser le nombre de balises <code>&lt;script&gt;</code> dans le <code>&lt;head&gt;</code></strong> pour ne pas bloquer le chargement</li>
    </ul>
    
    <div class="warning-box">
        <p><strong>⚠️ Attention :</strong> Le contenu du <code>&lt;head&gt;</code> n'est pas visible sur la page. Tous les éléments que vous voulez afficher doivent être placés dans le <code>&lt;body&gt;</code>.</p>
    </div>
    
    <h2>6. Exercice pratique</h2>
    <p>Créez une page HTML complète avec les caractéristiques suivantes :</p>
    <ol>
        <li>Un doctype HTML5 et la balise html avec l'attribut lang="fr"</li>
        <li>Une section <code>&lt;head&gt;</code> contenant :
            <ul>
                <li>Le jeu de caractères UTF-8</li>
                <li>La balise viewport pour le responsive</li>
                <li>Un titre pertinent</li>
                <li>Une meta description attractive</li>
                <li>Un favicon (vous pouvez utiliser une icône par défaut)</li>
                <li>Un lien vers un fichier CSS externe</li>
            </ul>
        </li>
        <li>Une section <code>&lt;body&gt;</code> avec un contenu simple (titre et paragraphe)</li>
    </ol>
    """.strip()
    
    
    cours_data = {
        "titre": "HTML Head - Métadonnées et ressources",
        "slug": slug_cours,
        "description": "Découvrez la balise <head> en HTML et son importance pour le SEO, l'accessibilité et les métadonnées. Apprenez à utiliser les balises title, meta, link, script, et à optimiser votre page pour les moteurs de recherche et les réseaux sociaux.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 30,
        "ordre_affichage": 14,
        "chapitre_id": chapitre_id,
        "tags": ["html", "head", "meta", "title", "seo", "metadata", "viewport", "favicon", "opengraph", "debutant"],
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
            print(f"   📚 Associé au chapitre HTML (ID: {chapitre_id})")
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
            print(f"   📚 Associé au chapitre HTML (ID: {chapitre_id})")
    
    conn.commit()
    return cours_id

def inserer_questions_head(cours_id):
    
    
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
            "question": "Quel est le rôle principal de la section <head> en HTML ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "Afficher le contenu principal de la page",
                "B": "Contenir des métadonnées sur la page (non visible)",
                "C": "Définir la structure des articles",
                "D": "Créer des liens hypertextes"
            },
            "reponse_correcte": "B",
            "explication": "La section <head> contient des métadonnées (informations sur la page) qui ne sont pas visibles directement par l'utilisateur, comme le titre, la description, et les liens vers les ressources externes.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quelle balise définit le titre d'une page qui apparaît dans l'onglet du navigateur ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "<header>",
                "B": "<h1>",
                "C": "<title>",
                "D": "<head>"
            },
            "reponse_correcte": "C",
            "explication": "La balise <title> définit le titre de la page, visible dans l'onglet du navigateur, les favoris et les résultats de recherche.",
            "mode_specifique": "video"
        },
        {
            "question": "À quoi sert la balise <meta charset='UTF-8'> ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "Définir la police d'écriture",
                "B": "Définir l'encodage des caractères",
                "C": "Créer une redirection",
                "D": "Définir la langue de la page"
            },
            "reponse_correcte": "B",
            "explication": "Cette balise définit l'encodage des caractères en UTF-8, permettant d'afficher correctement tous les caractères (accents, symboles, emojis, etc.).",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle balise utilise-t-on pour lier un fichier CSS externe ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "<style>",
                "B": "<css>",
                "C": "<link>",
                "D": "<script>"
            },
            "reponse_correcte": "C",
            "explication": "La balise <link> avec l'attribut rel='stylesheet' permet de lier un fichier CSS externe à la page HTML.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle est l'importance de la balise <meta name='viewport'> pour les appareils mobiles ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "Elle désactive le zoom sur mobile",
                "B": "Elle contrôle la mise à l'échelle et la largeur d'affichage sur mobile",
                "C": "Elle charge plus rapidement sur mobile",
                "D": "Elle n'est pas importante"
            },
            "reponse_correcte": "B",
            "explication": "La balise viewport contrôle comment la page s'affiche sur les appareils mobiles, en définissant la largeur d'affichage et l'échelle initiale. content='width=device-width, initial-scale=1.0' rend la page responsive.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quel attribut de la balise <meta> est utilisé pour la description SEO ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "name='description'",
                "B": "name='keywords'",
                "C": "property='description'",
                "D": "name='seo'"
            },
            "reponse_correcte": "A",
            "explication": "La balise <meta name='description' content='...'> fournit une description de la page utilisée par les moteurs de recherche dans les résultats.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle balise est utilisée pour définir une icône (favicon) dans l'onglet du navigateur ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "<icon>",
                "B": "<favicon>",
                "C": "<link rel='icon'>",
                "D": "<meta icon>"
            },
            "reponse_correcte": "C",
            "explication": "La balise <link rel='icon' type='image/x-icon' href='favicon.ico'> permet d'ajouter une icône personnalisée dans l'onglet du navigateur.",
            "mode_specifique": "audio"
        },
        {
            "question": "Les balises Open Graph (og:) sont utilisées pour quoi ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "Le référencement Google",
                "B": "Le partage sur les réseaux sociaux (Facebook, LinkedIn)",
                "C": "L'accessibilité des lecteurs d'écran",
                "D": "L'optimisation des images"
            },
            "reponse_correcte": "B",
            "explication": "Les balises Open Graph (og:title, og:description, og:image, etc.) contrôlent l'apparence du contenu lorsqu'il est partagé sur les réseaux sociaux.",
            "mode_specifique": "texte"
        },
        {
            "question": "Pourquoi est-il recommandé de placer les balises <script> en bas du <body> plutôt que dans le <head> ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "Pour que le script s'exécute plus vite",
                "B": "Pour ne pas bloquer le chargement de la page",
                "C": "Pour des raisons de sécurité",
                "D": "C'est une obligation HTML"
            },
            "reponse_correcte": "B",
            "explication": "Placer les scripts en bas du <body> empêche le blocage du chargement et de l'affichage du contenu HTML pendant le téléchargement et l'exécution du JavaScript, améliorant ainsi la vitesse perçue de la page.",
            "mode_specifique": "video"
        },
        {
            "question": "Laquelle de ces affirmations sur la balise <head> est correcte ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "Le <head> peut être placé n'importe où dans la page",
                "B": "Le <head> doit contenir toutes les images de la page",
                "C": "Le <head> doit être placé entre <html> et <body>",
                "D": "Le <head> est optionnel en HTML"
            },
            "reponse_correcte": "C",
            "explication": "Le <head> doit être placé entre la balise <html> et la balise <body>. C'est une structure obligatoire d'un document HTML valide.",
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
    print("🎓 INSERTION DU COURS: HEAD HTML (MÉTADONNÉES)")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    chapitre_id = get_chapitre_id("HTML")
    if chapitre_id:
        print(f"📚 Chapitre HTML trouvé (ID: {chapitre_id})")
    else:
        print("⚠️ Chapitre HTML non trouvé, le cours sera inséré sans chapitre")
    
    
    cours_id = inserer_cours_head()
    
    if cours_id:
        
        inserer_questions_head(cours_id)
        
        print(f"\n🎉 Succès ! Le cours 'HTML Head - Métadonnées et ressources' a été inséré avec succès!")
        print(f"   📚 Cours ID: {cours_id}")
        
        
        lister_cours_et_chapitres()
    else:
        print("\n❌ Échec de l'insertion du cours")

if __name__ == "__main__":
    main()