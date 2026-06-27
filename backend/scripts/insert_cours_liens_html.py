
import psycopg2
import json

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
        print(f"❌ Erreur de connexion à la base de données: {e}")
        return None

def get_admin_user():
    
    try:
        conn = get_connection()
        if not conn:
            return None
        
        cur = conn.cursor()
        
        
        cur.execute("""
            SELECT u.id, u.email, u.nom, u.prenom, r.nom_role
            FROM utilisateurs u
            JOIN roles r ON u.role_id = r.id
            WHERE u.id = 3
            AND u.est_actif = true
        """)
        
        admin = cur.fetchone()
        
        if admin:
            admin_id, email, nom, prenom, role = admin
            print(f"✅ Admin trouvé: {nom} {prenom} ({email}) - Rôle: {role} - ID: {admin_id}")
            cur.close()
            conn.close()
            return admin_id
        
        
        cur.execute("""
            SELECT u.id, u.email, u.nom, u.prenom
            FROM utilisateurs u
            JOIN roles r ON u.role_id = r.id
            WHERE r.nom_role = 'admin'
            AND u.est_actif = true
            LIMIT 1
        """)
        
        admin = cur.fetchone()
        
        if admin:
            admin_id, email, nom, prenom = admin
            print(f"✅ Admin trouvé: {nom} {prenom} ({email}) - ID: {admin_id}")
            cur.close()
            conn.close()
            return admin_id
        
        
        cur.execute("""
            SELECT id, email, nom, prenom 
            FROM utilisateurs 
            WHERE est_actif = true
            ORDER BY id
            LIMIT 1
        """)
        
        user = cur.fetchone()
        
        if user:
            user_id, email, nom, prenom = user
            print(f"⚠️ Aucun admin trouvé. Utilisation de: {nom} {prenom} ({email}) - ID: {user_id}")
            cur.close()
            conn.close()
            return user_id
        
        cur.close()
        conn.close()
        print("❌ Aucun utilisateur trouvé dans la base de données")
        return None
        
    except Exception as e:
        print(f"❌ Erreur lors de la recherche d'utilisateur: {e}")
        return None

def creer_cours_liens_html():
    
    try:
        
        admin_id = get_admin_user()
        if not admin_id:
            print("❌ Impossible de trouver un utilisateur valide pour créer les cours")
            return False
        
        print(f"\n👤 Utilisateur qui créera le cours: ID {admin_id}")
        
        
        conn = get_connection()
        if not conn:
            return False
        
        cur = conn.cursor()
        
        
        cours_liens = {
            "titre": "Apprendre l'HTML : Les liens hypertextes",
            "slug": "liens-hypertextes-html",
            "description": "Master the art of creating and managing hyperlinks in HTML. Learn relative paths, external links, anchors, and best practices for website navigation.",
            "contenu_texte": """
                <h1>Apprendre l'HTML : Les liens hypertextes</h1>
                
                <h2>📋 Introduction</h2>
                <p>Les liens hypertextes sont le fondement du web. Ils permettent de relier des pages entre elles, créant ainsi le "World Wide Web". Dans ce cours, vous apprendrez à créer et gérer différents types de liens en HTML.</p>
                
                <h2>🕐 Création d'une page d'accueil et d'une page menu (0:01)</h2>
                
                <h3>Pourquoi index.html ?</h3>
                <p>La page d'accueil d'un site web est traditionnellement nommée <code>index.html</code>. Les serveurs web sont configurés pour servir automatiquement ce fichier lorsqu'on accède à un répertoire.</p>
                
                <h3>Création de menu.html</h3>
                <pre><code>&lt;!DOCTYPE html&gt;
&lt;html lang="fr"&gt;
&lt;head&gt;
    &lt;meta charset="UTF-8"&gt;
    &lt;meta name="viewport" content="width=device-width, initial-scale=1.0"&gt;
    &lt;title&gt;Menu du Restaurant&lt;/title&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;h1&gt;Notre Restaurant&lt;/h1&gt;
    &lt;h2&gt;Menu Principal&lt;/h2&gt;
    
    &lt;h3&gt;Entrées&lt;/h3&gt;
    &lt;ul&gt;
        &lt;li&gt;Salade César&lt;/li&gt;
        &lt;li&gt;Soupe à l'oignon&lt;/li&gt;
        &lt;li&gt;Tartare de saumon&lt;/li&gt;
    &lt;/ul&gt;
    
    &lt;h3&gt;Plats Principaux&lt;/h3&gt;
    &lt;ul&gt;
        &lt;li&gt;Steak Frites&lt;/li&gt;
        &lt;li&gt;Poulet Rôti&lt;/li&gt;
        &lt;li&gt;Lasagnes Végétariennes&lt;/li&gt;
    &lt;/ul&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
                
                <h2>🔗 Introduction aux liens hypertextes (4:00)</h2>
                
                <h3>La balise &lt;a&gt;</h3>
                <p>La balise <code>&lt;a&gt;</code> (anchor) est utilisée pour créer des liens. L'attribut <code>href</code> spécifie la destination du lien.</p>
                
                <h3>Syntaxe de base :</h3>
                <pre><code>&lt;a href="menu.html"&gt;Voir notre menu&lt;/a&gt;</code></pre>
                
                <h3>Comportement du navigateur :</h3>
                <ul>
                    <li>🔵 <strong>Lien non visité</strong> : Souligné en bleu</li>
                    <li>🟣 <strong>Lien visité</strong> : Souligné en violet</li>
                    <li>🖱️ <strong>Au survol</strong> : Curseur change en main</li>
                </ul>
                
                <h2>📁 Travailler avec des sous-dossiers (6:02)</h2>
                
                <h3>Structure de dossiers :</h3>
                <pre><code>votre-site/
├── index.html
└── menus/
    ├── entrées.html
    ├── plats.html
    └── desserts.html</code></pre>
                
                <h3>Chemins relatifs :</h3>
                <pre><code>&lt;!-- Depuis index.html --&gt;
&lt;a href="menus/entrées.html"&gt;Voir les entrées&lt;/a&gt;

&lt;!-- Depuis entrées.html vers index.html --&gt;
&lt;a href="../index.html"&gt;Retour à l'accueil&lt;/a&gt;</code></pre>
                
                <h3>Symboles spéciaux :</h3>
                <ul>
                    <li><code>.</code> : Dossier courant</li>
                    <li><code>..</code> : Dossier parent</li>
                    <li><code>/</code> : Racine du site</li>
                </ul>
                
                <h2>🌐 Liens externes et attribut target (10:01)</h2>
                
                <h3>Liens vers d'autres sites :</h3>
                <pre><code>&lt;a href="https://www.google.com"&gt;Rechercher sur Google&lt;/a&gt;</code></pre>
                
                <h3>Ouvrir dans un nouvel onglet :</h3>
                <pre><code>&lt;a href="https://www.example.com" target="_blank"&gt;
    Visiter Example (nouvel onglet)
&lt;/a&gt;</code></pre>
                
                <h3>Attribut rel pour la sécurité :</h3>
                <pre><code>&lt;a href="https://site-externe.com" 
   target="_blank" 
   rel="noopener noreferrer"&gt;
    Site externe sécurisé
&lt;/a&gt;</code></pre>
                
                <h2>🎯 Liens absolus et ancres internes (15:16)</h2>
                
                <h3>Liens absolus :</h3>
                <pre><code>&lt;!-- Depuis la racine du site --&gt;
&lt;a href="/contact.html"&gt;Contact&lt;/a&gt;

&lt;!-- Site complet --&gt;
&lt;a href="https://mondomaine.com/produits"&gt;
    Nos produits
&lt;/a&gt;</code></pre>
                
                <h3>Ancres internes :</h3>
                <p>Permettent de naviguer à l'intérieur d'une même page.</p>
                
                <h4>Étape 1 : Définir l'ancre</h4>
                <pre><code>&lt;h2 id="plats-chauds"&gt;Plats chauds&lt;/h2&gt;</code></pre>
                
                <h4>Étape 2 : Créer le lien vers l'ancre</h4>
                <pre><code>&lt;a href="#plats-chauds"&gt;
    Aller directement aux plats chauds
&lt;/a&gt;</code></pre>
                
                <h4>Exemple complet (18:26) :</h4>
                <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;title&gt;Menu Restaurant&lt;/title&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;h1&gt;Menu du Restaurant&lt;/h1&gt;
    
    &lt;!-- Navigation interne --&gt;
    &lt;nav&gt;
        &lt;a href="#entrees"&gt;Entrées&lt;/a&gt;
        &lt;a href="#plats-chauds"&gt;Plats chauds&lt;/a&gt;
        &lt;a href="#desserts"&gt;Desserts&lt;/a&gt;
    &lt;/nav&gt;
    
    &lt;!-- Section Entrées --&gt;
    &lt;section id="entrees"&gt;
        &lt;h2&gt;Entrées&lt;/h2&gt;
        &lt;ul&gt;
            &lt;li&gt;Salade verte&lt;/li&gt;
            &lt;li&gt;Soupe du jour&lt;/li&gt;
        &lt;/ul&gt;
    &lt;/section&gt;
    
    &lt;!-- Section Plats chauds --&gt;
    &lt;section id="plats-chauds"&gt;
        &lt;h2&gt;Plats chauds&lt;/h2&gt;
        &lt;ul&gt;
            &lt;li&gt;Steak au poivre&lt;/li&gt;
            &lt;li&gt;Poulet rôti&lt;/li&gt;
        &lt;/ul&gt;
    &lt;/section&gt;
    
    &lt;!-- Lien pour remonter en haut --&gt;
    &lt;a href="#"&gt;Retour en haut&lt;/a&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
                
                <h2>🎓 Récapitulatif et bonnes pratiques</h2>
                
                <h3>Points clés :</h3>
                <ol>
                    <li>📄 <strong>index.html</strong> est le nom standard pour la page d'accueil</li>
                    <li>🔗 Utilisez <code>&lt;a href="..."&gt;</code> pour créer des liens</li>
                    <li>🗂️ <strong>Chemins relatifs</strong> pour les fichiers locaux</li>
                    <li>🌐 <strong>URLs complètes</strong> pour les sites externes</li>
                    <li>🪟 <code>target="_blank"</code> ouvre dans un nouvel onglet</li>
                    <li>⚓ <code>#id</code> permet de créer des ancres internes</li>
                </ol>
                
                <h3>Bonnes pratiques d'organisation :</h3>
                <ul>
                    <li>📂 Organisez vos fichiers en dossiers logiques</li>
                    <li>🏷️ Utilisez des noms de fichiers descriptifs</li>
                    <li>🔗 Testez tous vos liens régulièrement</li>
                    <li>📱 Assurez-vous que les liens sont accessibles sur mobile</li>
                    <li>🎯 Utilisez des textes de lien descriptifs (évitez "cliquez ici")</li>
                </ul>
                
                <h3>Types de liens :</h3>
                <table border="1" cellpadding="10" cellspacing="0">
                    <tr>
                        <th>Type</th>
                        <th>Syntaxe</th>
                        <th>Utilisation</th>
                    </tr>
                    <tr>
                        <td>Lien relatif</td>
                        <td><code>&lt;a href="page.html"&gt;</code></td>
                        <td>Pages du même site</td>
                    </tr>
                    <tr>
                        <td>Lien absolu</td>
                        <td><code>&lt;a href="/dossier/page.html"&gt;</code></td>
                        <td>À partir de la racine</td>
                    </tr>
                    <tr>
                        <td>Lien externe</td>
                        <td><code>&lt;a href="https://..."&gt;</code></td>
                        <td>Autres sites web</td>
                    </tr>
                    <tr>
                        <td>Ancre interne</td>
                        <td><code>&lt;a href="#section"&gt;</code></td>
                        <td>Navigation dans la page</td>
                    </tr>
                    <tr>
                        <td>Lien email</td>
                        <td><code>&lt;a href="mailto:..."&gt;</code></td>
                        <td>Envoyer un email</td>
                    </tr>
                    <tr>
                        <td>Lien téléphone</td>
                        <td><code>&lt;a href="tel:+33123456789"&gt;</code></td>
                        <td>Appeler un numéro</td>
                    </tr>
                </table>
                
                <h2>💻 Exercice pratique</h2>
                
                <h3>Objectif : Créer un site web de restaurant</h3>
                
                <h4>Structure des fichiers :</h4>
                <pre><code>restaurant/
├── index.html
├── menu.html
├── contact.html
├── images/
│   └── logo.png
└── assets/
    └── style.css</code></pre>
                
                <h4>Instructions :</h4>
                <ol>
                    <li>Créez la page d'accueil (<code>index.html</code>) avec :
                        <ul>
                            <li>Un titre principal</li>
                            <li>Un menu de navigation vers les autres pages</li>
                            <li>Une image du restaurant</li>
                            <li>Un lien vers le menu</li>
                        </ul>
                    </li>
                    <li>Créez la page menu (<code>menu.html</code>) avec :
                        <ul>
                            <li>Un titre "Notre Menu"</li>
                            <li>Sections pour entrées, plats, desserts</li>
                            <li>Ancres pour chaque section</li>
                            <li>Un lien de retour à l'accueil</li>
                        </ul>
                    </li>
                    <li>Créez la page contact (<code>contact.html</code>) avec :
                        <ul>
                            <li>Un formulaire de contact</li>
                            <li>Un lien email vers <code>contact@restaurant.com</code></li>
                            <li>Un lien pour appeler le restaurant</li>
                            <li>Un lien vers Google Maps</li>
                        </ul>
                    </li>
                    <li>Testez tous les liens dans votre navigateur</li>
                </ol>
                
                <h3>Solution type :</h3>
                <pre><code>&lt;!-- index.html --&gt;
&lt;!DOCTYPE html&gt;
&lt;html lang="fr"&gt;
&lt;head&gt;
    &lt;meta charset="UTF-8"&gt;
    &lt;title&gt;Le Bon Resto - Accueil&lt;/title&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;header&gt;
        &lt;h1&gt;🍽️ Le Bon Resto&lt;/h1&gt;
        &lt;nav&gt;
            &lt;a href="index.html"&gt;Accueil&lt;/a&gt;
            &lt;a href="menu.html"&gt;Menu&lt;/a&gt;
            &lt;a href="contact.html"&gt;Contact&lt;/a&gt;
        &lt;/nav&gt;
    &lt;/header&gt;
    
    &lt;main&gt;
        &lt;h2&gt;Bienvenue chez Le Bon Resto&lt;/h2&gt;
        &lt;p&gt;Découvrez notre cuisine traditionnelle.&lt;/p&gt;
        
        &lt;a href="menu.html#plats-du-jour"&gt;
            &lt;button&gt;Voir les plats du jour&lt;/button&gt;
        &lt;/a&gt;
    &lt;/main&gt;
    
    &lt;footer&gt;
        &lt;p&gt;Suivez-nous sur 
            &lt;a href="https://facebook.com" target="_blank"&gt;Facebook&lt;/a&gt;
        &lt;/p&gt;
    &lt;/footer&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
                
                <h2>🔍 Points à retenir</h2>
                <div style="background: #f0f8ff; padding: 15px; border-radius: 10px; border-left: 5px solid #3B82F6;">
                    <p><strong>Leçon principale :</strong> Les liens hypertextes en HTML sont créés avec la balise <code>&lt;a&gt;</code> et l'attribut <code>href</code>. Ils peuvent pointer vers des chemins relatifs, des URLs externes, ou des ancres internes.</p>
                    <p><strong>Conseil :</strong> Une organisation propre des fichiers et une nomenclature appropriée rendent les liens plus faciles à gérer et à maintenir.</p>
                </div>
                """,
            "url_video": "https://www.youtube.com/embed/LkZ-KqxgVQ4",
            "difficulte": "debutant",
            "duree_estimee": 25,
            "ordre_affichage": 6,
            "chapitre_id": None,
            "tags": ["html", "liens", "hypertextes", "debutant", "navigation", "ancres", "chemins"]
        }
        
        print(f"\n📚 Création du cours sur les liens hypertextes...")
        
        
        cur.execute("SELECT id FROM cours_html WHERE slug = %s", (cours_liens["slug"],))
        
        result = cur.fetchone()
        
        if result:
            print(f"⚠️ Cours déjà existant : {cours_liens['titre']}")
            print(f"   ID du cours existant : {result[0]}")
            cur.close()
            conn.close()
            return result[0]  
        
        try:
            
            cur.execute("""
                INSERT INTO cours_html 
                (titre, slug, description, contenu_texte, url_video, difficulte, 
                 duree_estimee, ordre_affichage, chapitre_id, tags, est_actif, 
                 created_by, date_creation, date_maj, last_modified_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, %s)
                RETURNING id
            """, (
                cours_liens["titre"],
                cours_liens["slug"],
                cours_liens["description"],
                cours_liens["contenu_texte"],
                cours_liens["url_video"],
                cours_liens["difficulte"],
                cours_liens["duree_estimee"],
                cours_liens["ordre_affichage"],
                cours_liens["chapitre_id"],
                cours_liens["tags"],
                True,
                admin_id,  
                admin_id   
            ))
            
            cours_id = cur.fetchone()[0]
            print(f"✅ Cours créé avec succès !")
            print(f"   ID: {cours_id}")
            print(f"   Titre: {cours_liens['titre']}")
            print(f"   Slug: {cours_liens['slug']}")
            print(f"   Durée: {cours_liens['duree_estimee']} minutes")
            print(f"   Difficulté: {cours_liens['difficulte']}")
            print(f"   Tags: {', '.join(cours_liens['tags'])}")
            
            conn.commit()
            cur.close()
            conn.close()
            
            return cours_id
            
        except Exception as e:
            print(f"❌ Erreur lors de la création du cours: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
            cur.close()
            conn.close()
            return None
        
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE lors de la création du cours: {e}")
        import traceback
        traceback.print_exc()
        return None

def creer_questions_pour_liens_html(cours_id):
    
    try:
        
        admin_id = get_admin_user()
        if not admin_id:
            print("❌ Impossible de trouver un utilisateur valide")
            return False
        
        if not cours_id:
            print("❌ ID du cours non fourni")
            return False
        
        conn = get_connection()
        if not conn:
            return False
        
        cur = conn.cursor()
        
        print("\n📝 Création des questions de quiz pour le cours sur les liens...")
        
        
        questions = [
            {
                "question": "Pourquoi la page d'accueil d'un site web est-elle généralement nommée 'index.html' ?",
                "type_question": "choix_multiple",
                "points": 10,
                "difficulte": "facile",
                "options": {
                    "A": "C'est une convention imposée par le W3C",
                    "B": "Les serveurs web sont configurés pour servir ce fichier par défaut",
                    "C": "C'est plus facile à retenir pour les débutants",
                    "D": "Cela améliore le référencement SEO"
                },
                "reponse_correcte": "B",
                "explication": "Les serveurs web sont configurés pour servir automatiquement 'index.html' (ou 'index.php', 'index.htm') lorsqu'on accède à un répertoire. C'est une convention largement adoptée.",
                "mode_specifique": "video"
            },
            {
                "question": "Quelle est la syntaxe correcte pour créer un lien vers la page 'apropos.html' située dans le même dossier ?",
                "type_question": "choix_multiple",
                "points": 10,
                "difficulte": "facile",
                "options": {
                    "A": "<link href='apropos.html'>À propos</link>",
                    "B": "<a src='apropos.html'>À propos</a>",
                    "C": "<a href='apropos.html'>À propos</a>",
                    "D": "<hyperlink='apropos.html'>À propos</hyperlink>"
                },
                "reponse_correcte": "C",
                "explication": "La balise <a> (anchor) avec l'attribut href est utilisée pour créer des liens hypertextes en HTML.",
                "mode_specifique": "texte"
            },
            {
                "question": "Comment créer un lien qui ouvre une page externe dans un nouvel onglet ?",
                "type_question": "choix_multiple",
                "points": 15,
                "difficulte": "moyen",
                "options": {
                    "A": "<a href='https://example.com' target='_new'>Exemple</a>",
                    "B": "<a href='https://example.com' newtab>Exemple</a>",
                    "C": "<a href='https://example.com' target='_blank'>Exemple</a>",
                    "D": "<a href='https://example.com' open='new'>Exemple</a>"
                },
                "reponse_correcte": "C",
                "explication": "L'attribut target='_blank' indique au navigateur d'ouvrir le lien dans un nouvel onglet ou une nouvelle fenêtre.",
                "mode_specifique": "video"
            },
            {
                "question": "Vous avez la structure suivante : site/index.html et site/produits/liste.html. Quel chemin utiliser depuis liste.html pour revenir à index.html ?",
                "type_question": "choix_multiple",
                "points": 15,
                "difficulte": "moyen",
                "options": {
                    "A": "<a href='../index.html'>Accueil</a>",
                    "B": "<a href='./index.html'>Accueil</a>",
                    "C": "<a href='/index.html'>Accueil</a>",
                    "D": "<a href='index.html'>Accueil</a>"
                },
                "reponse_correcte": "A",
                "explication": "Le chemin '../' remonte d'un niveau dans l'arborescence des dossiers. Depuis le dossier 'produits', '../' nous ramène au dossier parent 'site' où se trouve index.html.",
                "mode_specifique": "video"
            },
            {
                "question": "Comment créer une ancre interne qui permet de sauter à une section avec l'id 'contact' dans la même page ?",
                "type_question": "choix_multiple",
                "points": 10,
                "difficulte": "facile",
                "options": {
                    "A": "<a link='#contact'>Contact</a>",
                    "B": "<a href='#contact'>Contact</a>",
                    "C": "<a anchor='contact'>Contact</a>",
                    "D": "<a goto='contact'>Contact</a>"
                },
                "reponse_correcte": "B",
                "explication": "Les ancres internes utilisent le symbole # suivi de l'id de l'élément cible dans l'attribut href.",
                "mode_specifique": "video"
            },
            {
                "question": "Quelle est la différence entre un lien relatif et un lien absolu en HTML ?",
                "type_question": "choix_multiple",
                "points": 20,
                "difficulte": "avance",
                "options": {
                    "A": "Les liens relatifs sont plus rapides à charger",
                    "B": "Les liens relatifs sont basés sur l'emplacement actuel, les absolus sur la racine",
                    "C": "Les liens absolus ne fonctionnent qu'en ligne, les relatifs fonctionnent localement",
                    "D": "Il n'y a pas de différence fonctionnelle"
                },
                "reponse_correcte": "B",
                "explication": "Un lien relatif (comme 'page.html' ou '../dossier/page.html') est relatif à l'emplacement de la page actuelle. Un lien absolu (comme '/dossier/page.html') part toujours de la racine du site.",
                "mode_specifique": "texte"
            }
        ]
        
        total_questions_creees = 0
        
        print(f"\n📚 Création des questions pour le cours ID: {cours_id}")
        
        for q in questions:
            try:
                cur.execute("""
                    INSERT INTO questions_quiz 
                    (cours_id, question, type_question, points, difficulte, 
                     options, reponse_correcte, explication, mode_specifique, 
                     created_by, date_creation)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    RETURNING id
                """, (
                    cours_id,
                    q["question"],
                    q["type_question"],
                    q["points"],
                    q["difficulte"],
                    json.dumps(q["options"], ensure_ascii=False),
                    q["reponse_correcte"],
                    q["explication"],
                    q["mode_specifique"],
                    admin_id
                ))
                
                question_id = cur.fetchone()[0]
                total_questions_creees += 1
                print(f"  ✅ Question {total_questions_creees}: {q['question'][:50]}...")
                
            except Exception as e:
                print(f"  ❌ Erreur sur la question: {e}")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"\n📝 TOTAL: {total_questions_creees} questions créées pour ce cours")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des questions: {e}")
        import traceback
        traceback.print_exc()
        return False

def afficher_info_cours():
    
    try:
        conn = get_connection()
        if not conn:
            return False
        
        cur = conn.cursor()
        
        
        cur.execute("SELECT COUNT(*) FROM cours_html WHERE est_actif = true")
        total_cours = cur.fetchone()[0]
        
        
        cur.execute("""
            SELECT difficulte, COUNT(*) 
            FROM cours_html 
            WHERE est_actif = true
            GROUP BY difficulte
            ORDER BY 
                CASE difficulte 
                    WHEN 'debutant' THEN 1
                    WHEN 'intermediaire' THEN 2
                    WHEN 'avance' THEN 3
                    ELSE 4
                END
        """)
        
        stats_difficulte = cur.fetchall()
        
        
        cur.execute("""
            SELECT id, titre, slug, difficulte, date_creation, created_by
            FROM cours_html 
            WHERE est_actif = true
            ORDER BY date_creation DESC
            LIMIT 5
        """)
        
        derniers_cours = cur.fetchall()
        
        print("\n" + "=" * 80)
        print("📊 STATISTIQUES DES COURS HTML")
        print("=" * 80)
        
        print(f"\n📚 Nombre total de cours actifs : {total_cours}")
        
        print(f"\n🎯 Répartition par difficulté :")
        for difficulte, count in stats_difficulte:
            print(f"   • {difficulte.capitalize():<12} : {count} cours")
        
        print(f"\n🆕 Derniers cours créés :")
        for cours in derniers_cours:
            c_id, titre, slug, difficulte, date_creation, created_by = cours
            date_str = date_creation.strftime("%d/%m/%Y")
            print(f"   • [{c_id}] {titre[:40]}... ({difficulte}) - {date_str}")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'affichage des statistiques: {e}")
        return False

def main():
    """Fonction principale"""
    print("\n" + "🌟" * 30)
    print("🔗 CRÉATION DU COURS SUR LES LIENS HYPERTEXTES HTML")
    print("🌟" * 30)
    
    
    print("\n🔍 Test de connexion à la base de données...")
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    afficher_info_cours()
    
    print("\n" + "=" * 80)
    print("🚀 DÉMARRAGE DE LA CRÉATION DU COURS")
    print("=" * 80)
    
    
    cours_id = creer_cours_liens_html()
    
    if cours_id:
        print("\n" + "✅" * 30)
        print("COURS CRÉÉ AVEC SUCCÈS !")
        print("✅" * 30)
        
        
        print("\n📝 Souhaitez-vous créer des questions de quiz pour ce cours ?")
        reponse = input("(O)ui / (N)on : ").strip().lower()
        
        if reponse in ['o', 'oui', 'y', 'yes']:
            creer_questions_pour_liens_html(cours_id)
        
        
        print("\n" + "📊" * 30)
        print("STATISTIQUES MISES À JOUR")
        print("📊" * 30)
        afficher_info_cours()
        
        
        print("\n" + "🎓" * 30)
        print("INSTRUCTIONS POUR UTILISER LE COURS")
        print("🎓" * 30)
        print(f"""
        ✅ Le cours a été créé avec succès !

        🔗 URL du cours dans l'application :
        • Mode texte   : http://localhost:8501/text_learning?cours=liens-hypertextes-html
        • Mode audio   : http://localhost:8501/audio_learning?cours=liens-hypertextes-html  
        • Mode vidéo   : http://localhost:8501/video_learning?cours=liens-hypertextes-html
        
        📋 Pour ajouter ce cours dans l'application :
        1. Dans video_learning.py, ajoutez-le à la fonction get_cours_video_existant()
        2. Dans audio_learning.py, ajoutez-le à la fonction get_cours_audio_existant()
        3. Dans text_learning.py, ajoutez-le à la fonction get_cours_texte_existant()
        
        🎯 Caractéristiques du cours :
        • ID : {cours_id}
        • Slug : liens-hypertextes-html
        • Titre : Apprendre l'HTML : Les liens hypertextes
        • Difficulté : débutant
        • Durée estimée : 25 minutes
        • Tags : html, liens, hypertextes, navigation, ancres
        """)
    
    else:
        print("\n❌ La création du cours a échoué.")
    
    print("\n" + "🎉" * 30)
    print("SCRIPT TERMINÉ")
    print("🎉" * 30)

if __name__ == "__main__":
    main()