
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
        
        # Si l'ID 3 n'existe pas, chercher un autre admin
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
        
        # Sinon, prendre le premier utilisateur actif
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

def inserer_cours_images():
    
    try:
        
        admin_id = get_admin_user()
        if not admin_id:
            print("❌ Impossible de trouver un utilisateur valide pour créer le cours")
            return False
        
        print(f"\n👤 Utilisateur qui créera le cours: ID {admin_id}")
        
        
        conn = get_connection()
        if not conn:
            return False
        
        cur = conn.cursor()
        
        
        slug_cours = "images-html"
        
        cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
        existing = cur.fetchone()
        
        if existing:
            print(f"⚠️ Le cours avec le slug '{slug_cours}' existe déjà (ID: {existing[0]})")
            
            
            print("\nVoulez-vous mettre à jour ce cours ? (o/n)")
            reponse = input("> ").strip().lower()
            
            if reponse != 'o':
                print("❌ Annulation de l'insertion")
                cur.close()
                conn.close()
                return False
        
        
        contenu_html = """
        <h1>📷 Les Images en HTML</h1>
        
        <h2>Introduction</h2>
        <p>Les images sont essentielles pour enrichir le contenu visuel d'une page web. HTML propose la balise <code>&lt;img&gt;</code> pour intégrer des images.</p>
        
        <div class="info-box">
            <p><strong>💡 Important :</strong> La balise <code>&lt;img&gt;</code> est une balise auto-fermante (pas de balise de fermeture).</p>
        </div>
        
        <h2>1. La balise &lt;img&gt; et ses attributs clés</h2>
        
        <h3>Syntaxe de base :</h3>
        <pre><code>&lt;img src="chemin/vers/image.jpg" alt="Description de l'image"&gt;</code></pre>
        
        <h3>Attributs essentiels :</h3>
        <ul>
            <li><strong>src (source)</strong> : Spécifie l'URL ou le chemin de l'image (obligatoire)</li>
            <li><strong>alt (alternative text)</strong> : Texte alternatif pour l'accessibilité et en cas d'erreur de chargement (obligatoire pour HTML valide)</li>
        </ul>
        
        <div class="example-box">
            <h4>📝 Exemple :</h4>
            <pre><code>&lt;img src="logo-entreprise.png" alt="Logo de notre entreprise"&gt;</code></pre>
        </div>
        
        <h2>2. Dimensionnement des images</h2>
        <p>Pour éviter le "flicker" (saut de page) pendant le chargement, spécifiez toujours les dimensions de vos images.</p>
        
        <h3>Méthode 1 : Attributs width et height</h3>
        <pre><code>&lt;img src="photo.jpg" alt="Description" width="300" height="200"&gt;</code></pre>
        
        <h3>Méthode 2 : Style CSS (recommandé)</h3>
        <pre><code>&lt;img src="photo.jpg" alt="Description" style="width: 300px; height: 200px;"&gt;</code></pre>
        
        <div class="tip-box">
            <p><strong>💡 Astuce :</strong> Spécifier les dimensions permet au navigateur de réserver l'espace nécessaire avant le chargement de l'image, évitant ainsi les sauts de page.</p>
        </div>
        
        <h2>3. Stockage et emplacement des images</h2>
        
        <h3>Structure de dossiers recommandée :</h3>
        <pre><code>votre-site/
├── index.html
├── images/
│   ├── logo.png
│   ├── photo-principale.jpg
│   └── background.jpg
└── css/
    └── style.css</code></pre>
        
        <h3>Chemins d'accès :</h3>
        <ul>
            <li><strong>Même dossier :</strong> <code>&lt;img src="image.jpg"&gt;</code></li>
            <li><strong>Sous-dossier :</strong> <code>&lt;img src="images/image.jpg"&gt;</code></li>
            <li><strong>Dossier parent :</strong> <code>&lt;img src="../image.jpg"&gt;</code></li>
            <li><strong>URL externe :</strong> <code>&lt;img src="https://example.com/image.jpg"&gt;</code></li>
        </ul>
        
        <h2>4. Images animées (GIF)</h2>
        <p>Les images au format GIF animé fonctionnent exactement comme les images statiques :</p>
        <pre><code>&lt;img src="animation.gif" alt="Animation explicative"&gt;</code></pre>
        
        <h2>5. Images cliquables (liens)</h2>
        <p>Pour rendre une image cliquable, il suffit de l'entourer d'une balise <code>&lt;a&gt;</code> :</p>
        <pre><code>&lt;a href="galerie.html"&gt;
    &lt;img src="miniature.jpg" alt="Voir la galerie complète"&gt;
&lt;/a&gt;</code></pre>
        
        <div class="example-box">
            <h4>📝 Exemple complet :</h4>
            <pre><code>&lt;a href="https://www.wikipedia.org" target="_blank"&gt;
    &lt;img src="wikipedia-logo.png" 
         alt="Logo Wikipedia - Ouvre dans un nouvel onglet"
         width="200" 
         height="100"&gt;
&lt;/a&gt;</code></pre>
        </div>
        
        <h2>6. Mise en page avec CSS</h2>
        
        <h3>Faire flotter une image (float) :</h3>
        <pre><code>&lt;img src="image.jpg" alt="Description" style="float: right; margin-left: 15px;"&gt;
&lt;p&gt;Le texte qui s'affiche autour de l'image. L'image flotte à droite.&lt;/p&gt;</code></pre>
        
        <h3>Images de fond (background-image) :</h3>
        <pre><code>&lt;div style="background-image: url('fond.jpg'); 
            background-size: cover; 
            padding: 50px;"&gt;
    &lt;p&gt;Ce texte s'affiche sur une image de fond.&lt;/p&gt;
&lt;/div&gt;</code></pre>
        
        <div class="tip-box">
            <p><strong>💡 Astuce CSS :</strong> Utilisez <code>background-size: cover</code> pour que l'image de fond couvre tout l'espace disponible.</p>
        </div>
        
        <h2>7. Bonnes pratiques et accessibilité</h2>
        <ul>
            <li><strong>Toujours l'attribut alt :</strong> Essentiel pour l'accessibilité (lecteurs d'écran) et le SEO</li>
            <li><strong>Optimisation :</strong> Compressez vos images pour réduire leur taille</li>
            <li><strong>Formats adaptés :</strong> JPG pour les photos, PNG pour la transparence, WebP pour un meilleur compromis</li>
            <li><strong>Images responsives :</strong> Utilisez <code>max-width: 100%; height: auto;</code> pour des images adaptatives</li>
        </ul>
        
        <div class="warning-box">
            <p><strong>⚠️ Performance :</strong> Les images trop volumineuses ralentissent considérablement le chargement des pages. Utilisez-les avec parcimonie et optimisez-les.</p>
        </div>
        
        <h2>8. Formats d'images supportés</h2>
        <table border="1" cellpadding="10">
            <tr>
                <th>Format</th>
                <th>Extension</th>
                <th>Utilisation</th>
            </tr>
            <tr>
                <td>JPEG/JPG</td>
                <td>.jpg, .jpeg</td>
                <td>Photos, images avec dégradés</td>
            </tr>
            <tr>
                <td>PNG</td>
                <td>.png</td>
                <td>Logos, icônes, transparence</td>
            </tr>
            <tr>
                <td>GIF</td>
                <td>.gif</td>
                <td>Animations, petites images</td>
            </tr>
            <tr>
                <td>WebP</td>
                <td>.webp</td>
                <td>Moderne, meilleure compression</td>
            </tr>
            <tr>
                <td>SVG</td>
                <td>.svg</td>
                <td>Vectoriel, logos, icônes</td>
            </tr>
        </table>
        
        <h2>9. Exercice pratique</h2>
        <p>Créez une galerie d'images avec :</p>
        <ol>
            <li>Une image principale avec dimensions spécifiées</li>
            <li>Une image cliquable qui ouvre un lien externe dans un nouvel onglet</li>
            <li>Deux images flottantes (une à gauche, une à droite)</li>
            <li>Un paragraphe avec une image de fond</li>
            <li>Des textes alternatifs (alt) pertinents pour chaque image</li>
        </ol>
        
        <div class="summary-box">
            <h3>📌 Récapitulatif</h3>
            <ul>
                <li>La balise <code>&lt;img&gt;</code> est auto-fermante</li>
                <li>Les attributs <code>src</code> et <code>alt</code> sont obligatoires</li>
                <li>Spécifiez les dimensions pour éviter les sauts de page</li>
                <li>Les images peuvent être cliquables avec <code>&lt;a&gt;</code></li>
                <li>Utilisez <code>float</code> ou <code>background-image</code> pour la mise en page</li>
                <li>Optimisez vos images pour les performances</li>
            </ul>
        </div>
        """.strip()
        
        
        cours_data = {
            "titre": "Images en HTML - Guide Complet",
            "slug": slug_cours,
            "description": "Apprenez à intégrer et optimiser des images en HTML. Découvrez la balise <img>, ses attributs, le dimensionnement, les images cliquables, et les bonnes pratiques pour des pages web performantes.",
            "contenu_texte": contenu_html,
            "difficulte": "debutant",
            "duree_estimee": 25,
            "ordre_affichage": 7,
            "tags": ["html", "images", "img", "debutant", "web", "accessibilite", "optimisation"],
            "est_actif": True,
            "created_by": admin_id,
            "last_modified_by": admin_id
        }
        
        if existing:
            
            cur.execute("""
                UPDATE cours_html 
                SET titre = %s, description = %s, contenu_texte = %s, 
                    difficulte = %s, duree_estimee = %s, ordre_affichage = %s,
                    tags = %s, est_actif = %s, last_modified_by = %s,
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
                cours_data["tags"],
                cours_data["est_actif"],
                cours_data["last_modified_by"],
                slug_cours
            ))
            
            cours_id = cur.fetchone()[0]
            print(f"✅ Cours mis à jour (ID: {cours_id}): {cours_data['titre']}")
        else:
            
            cur.execute("""
                INSERT INTO cours_html 
                (titre, slug, description, contenu_texte, difficulte, 
                 duree_estimee, ordre_affichage, tags, est_actif, 
                 created_by, date_creation, date_maj, last_modified_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, %s)
                RETURNING id
            """, (
                cours_data["titre"],
                cours_data["slug"],
                cours_data["description"],
                cours_data["contenu_texte"],
                cours_data["difficulte"],
                cours_data["duree_estimee"],
                cours_data["ordre_affichage"],
                cours_data["tags"],
                cours_data["est_actif"],
                cours_data["created_by"],
                cours_data["last_modified_by"]
            ))
            
            cours_id = cur.fetchone()[0]
            print(f"✅ Cours créé (ID: {cours_id}): {cours_data['titre']}")
        
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"\n🎉 Succès ! Le cours 'Images en HTML' a été {'mis à jour' if existing else 'créé'} avec succès.")
        print(f"   ID: {cours_id}")
        print(f"   Slug: {slug_cours}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'insertion du cours: {e}")
        import traceback
        traceback.print_exc()
        return False

def creer_questions_images():
    
    try:
        admin_id = get_admin_user()
        if not admin_id:
            print("❌ Impossible de trouver un utilisateur valide")
            return False
        
        conn = get_connection()
        if not conn:
            return False
        
        cur = conn.cursor()
        
        
        cur.execute("SELECT id FROM cours_html WHERE slug = 'images-html'")
        result = cur.fetchone()
        
        if not result:
            print("❌ Cours 'images-html' non trouvé. Veuillez d'abord créer le cours.")
            cur.close()
            conn.close()
            return False
        
        cours_id = result[0]
        
        print(f"\n📝 Création des questions pour le cours 'Images en HTML' (ID: {cours_id})...")
        
        
        questions = [
            {
                "question": "Quelle balise HTML est utilisée pour insérer une image ?",
                "type_question": "choix_multiple",
                "points": 10,
                "difficulte": "facile",
                "options": {
                    "A": "&lt;image&gt;",
                    "B": "&lt;img&gt;",
                    "C": "&lt;src&gt;",
                    "D": "&lt;picture&gt;"
                },
                "reponse_correcte": "B",
                "explication": "La balise &lt;img&gt; (image) est utilisée pour insérer des images en HTML. C'est une balise auto-fermante.",
                "mode_specifique": "texte"
            },
            {
                "question": "Quels sont les deux attributs obligatoires de la balise &lt;img&gt; ?",
                "type_question": "choix_multiple",
                "points": 10,
                "difficulte": "facile",
                "options": {
                    "A": "src et width",
                    "B": "src et height",
                    "C": "src et alt",
                    "D": "alt et title"
                },
                "reponse_correcte": "C",
                "explication": "Les attributs src (source) et alt (texte alternatif) sont obligatoires pour une balise &lt;img&gt; valide.",
                "mode_specifique": "video"
            },
            {
                "question": "À quoi sert l'attribut 'alt' dans une balise &lt;img&gt; ?",
                "type_question": "choix_multiple",
                "points": 15,
                "difficulte": "moyen",
                "options": {
                    "A": "Définir la hauteur de l'image",
                    "B": "Définir la largeur de l'image",
                    "C": "Fournir un texte alternatif pour l'accessibilité et le SEO",
                    "D": "Définir le titre de l'image au survol"
                },
                "reponse_correcte": "C",
                "explication": "L'attribut 'alt' (alternative text) décrit le contenu de l'image pour les lecteurs d'écran et s'affiche si l'image ne peut pas être chargée.",
                "mode_specifique": "audio"
            },
            {
                "question": "Comment créer une image cliquable qui ouvre un lien ?",
                "type_question": "choix_multiple",
                "points": 15,
                "difficulte": "moyen",
                "options": {
                    "A": "&lt;img src='image.jpg' href='https://example.com'&gt;",
                    "B": "&lt;a href='https://example.com'&gt;&lt;img src='image.jpg' alt='Description'&gt;&lt;/a&gt;",
                    "C": "&lt;img src='image.jpg' link='https://example.com'&gt;",
                    "D": "&lt;image src='image.jpg' url='https://example.com'&gt;"
                },
                "reponse_correcte": "B",
                "explication": "Pour rendre une image cliquable, il faut l'entourer d'une balise &lt;a&gt; avec l'attribut href.",
                "mode_specifique": "video"
            },
            {
                "question": "Quelle propriété CSS permet de faire flotter une image à gauche ou à droite du texte ?",
                "type_question": "choix_multiple",
                "points": 15,
                "difficulte": "moyen",
                "options": {
                    "A": "display",
                    "B": "position",
                    "C": "float",
                    "D": "align"
                },
                "reponse_correcte": "C",
                "explication": "La propriété CSS 'float' permet de faire flotter un élément, comme une image, à gauche ou à droite du texte.",
                "mode_specifique": "texte"
            },
            {
                "question": "Quel est le format d'image recommandé pour les logos et les images avec transparence ?",
                "type_question": "choix_multiple",
                "points": 10,
                "difficulte": "facile",
                "options": {
                    "A": "JPEG",
                    "B": "GIF",
                    "C": "PNG",
                    "D": "BMP"
                },
                "reponse_correcte": "C",
                "explication": "Le format PNG supporte la transparence et est idéal pour les logos et les images nécessitant un fond transparent.",
                "mode_specifique": "audio"
            },
            {
                "question": "Comment spécifier les dimensions d'une image en CSS ?",
                "type_question": "choix_multiple",
                "points": 10,
                "difficulte": "facile",
                "options": {
                    "A": "&lt;img width='300' height='200'&gt;",
                    "B": "&lt;img style='width: 300px; height: 200px;'&gt;",
                    "C": "Les deux méthodes sont valides",
                    "D": "Aucune des deux"
                },
                "reponse_correcte": "C",
                "explication": "On peut utiliser soit les attributs width/height, soit la propriété CSS style pour dimensionner une image.",
                "mode_specifique": "video"
            },
            {
                "question": "Quel attribut est recommandé pour améliorer l'accessibilité des images ?",
                "type_question": "choix_multiple",
                "points": 10,
                "difficulte": "facile",
                "options": {
                    "A": "title",
                    "B": "src",
                    "C": "width",
                    "D": "alt"
                },
                "reponse_correcte": "D",
                "explication": "L'attribut 'alt' est indispensable pour l'accessibilité car il décrit l'image aux lecteurs d'écran.",
                "mode_specifique": "audio"
            },
            {
                "question": "Que signifie 'src' dans la balise &lt;img&gt; ?",
                "type_question": "choix_multiple",
                "points": 10,
                "difficulte": "facile",
                "options": {
                    "A": "Source",
                    "B": "Screen",
                    "C": "Script",
                    "D": "Style"
                },
                "reponse_correcte": "A",
                "explication": "'src' signifie 'source' et indique le chemin ou l'URL de l'image à afficher.",
                "mode_specifique": "texte"
            }
        ]
        
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
                    RETURNING id
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
                
                question_id = cur.fetchone()[0]
                questions_creees += 1
                print(f"  ✅ Question créée (ID {question_id}): {q['question'][:50]}...")
                
            except Exception as e:
                print(f"  ❌ Erreur sur la question: {e}")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"\n📊 RÉSUMÉ:")
        print(f"   • Questions créées: {questions_creees}")
        print(f"   • Questions déjà existantes: {questions_existantes}")
        print(f"   • Total: {questions_creees + questions_existantes}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des questions: {e}")
        import traceback
        traceback.print_exc()
        return False

def menu():
    
    print("\n" + "=" * 60)
    print("🎓 INSERTION DU COURS 'IMAGES EN HTML'")
    print("=" * 60)
    print("\nQue souhaitez-vous faire ?")
    print("1. Créer le cours 'Images en HTML'")
    print("2. Créer les questions de quiz pour ce cours")
    print("3. Tout faire (cours + questions)")
    print("4. Quitter")
    
    choix = input("\nVotre choix (1-4) : ").strip()
    
    if choix == "1":
        print("\n" + "📷" * 30)
        print("CRÉATION DU COURS")
        print("📷" * 30)
        inserer_cours_images()
        
    elif choix == "2":
        print("\n" + "📝" * 30)
        print("CRÉATION DES QUESTIONS")
        print("📝" * 30)
        creer_questions_images()
        
    elif choix == "3":
        print("\n" + "⚡" * 30)
        print("CRÉATION COMPLÈTE")
        print("⚡" * 30)
        if inserer_cours_images():
            creer_questions_images()
            
    elif choix == "4":
        print("\n👋 Au revoir !")
        return False
    else:
        print("❌ Choix invalide.")
    
    return True

if __name__ == "__main__":
    print("\n" + "🌟" * 30)
    print("🔧 INSERTION DU COURS SUR LES IMAGES EN HTML")
    print("🌟" * 30)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        exit(1)
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    while menu():
        input("\nAppuyez sur Entrée pour continuer...")
    
    print("\n" + "🎉" * 30)
    print("SCRIPT TERMINÉ")
    print("🎉" * 30)