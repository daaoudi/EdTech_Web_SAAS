
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

def creer_cours_html():
    
    try:
        
        admin_id = get_admin_user()
        if not admin_id:
            print("❌ Impossible de trouver un utilisateur valide pour créer les cours")
            return False
        
        print(f"\n👤 Utilisateur qui créera les cours: ID {admin_id}")
        
        
        print("🔍 Vérification de la contrainte de difficulté...")
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            cur.execute("""
                SELECT pg_get_constraintdef(oid) 
                FROM pg_constraint 
                WHERE conrelid = 'cours_html'::regclass 
                AND conname = 'cours_html_difficulte_check'
            """)
            
            result = cur.fetchone()
            cur.close()
            conn.close()
            
            if result:
                print(f"   ✅ Contrainte: {result[0][:80]}...")
        except Exception as e:
            print(f"   ⚠️ Note: {e}")
        
        
        conn = get_connection()
        if not conn:
            return False
        
        cur = conn.cursor()
        
        
        cours_a_creer = [
            {
                "titre": "Formatage du Texte en HTML - Niveau Débutant",
                "slug": "formatage-texte-html-debutant",
                "description": "Apprenez les bases du formatage de texte en HTML à travers des leçons écrites détaillées et des exercices pratiques",
                "contenu_texte": """
                <h1>Formatage du Texte en HTML</h1>
                
                <h2>Introduction</h2>
                <p>HTML (HyperText Markup Language) est le langage fondamental du web. Il permet de structurer et de formater le contenu des pages web. Dans cette leçon, nous allons explorer les différentes manières de formater du texte en HTML.</p>
                
                <h2>1. Les En-têtes (Headings)</h2>
                <p>Les en-têtes sont utilisés pour structurer votre contenu en sections hiérarchiques. HTML propose six niveaux d'en-têtes, de &lt;h1&gt; (le plus important) à &lt;h6&gt; (le moins important).</p>
                
                <h3>Exemple :</h3>
                <pre><code>&lt;h1&gt;Titre Principal&lt;/h1&gt;
                &lt;h2&gt;Section 1&lt;/h2&gt;
                &lt;h3&gt;Sous-section 1.1&lt;/h3&gt;
                &lt;h4&gt;Détails supplémentaires&lt;/h4&gt;</code></pre>
                
                <h3>Bonnes pratiques :</h3>
                <ul>
                    <li>Utilisez un seul &lt;h1&gt; par page</li>
                    <li>Suivez une hiérarchie logique (ne sautez pas de niveaux)</li>
                    <li>Les en-têtes doivent refléter la structure de votre contenu</li>
                </ul>
                
                <h2>2. Les Paragraphes</h2>
                <p>La balise &lt;p&gt; est utilisée pour définir des paragraphes. Chaque paragraphe est automatiquement séparé par un espace vertical.</p>
                
                <h2>3. Mise en Forme Sémantique</h2>
                <p>HTML moderne privilégie la sémantique (signification) plutôt que l'apparence pure.</p>
                
                <h3>Balises sémantiques importantes :</h3>
                <ul>
                    <li><strong>&lt;strong&gt;</strong> : Texte important (sémantique)</li>
                    <li><strong>&lt;em&gt;</strong> : Texte accentué (sémantique)</li>
                    <li><strong>&lt;mark&gt;</strong> : Texte surligné</li>
                    <li><strong>&lt;small&gt;</strong> : Texte secondaire</li>
                    <li><strong>&lt;blockquote&gt;</strong> : Citation longue</li>
                    <li><strong>&lt;code&gt;</strong> : Code informatique</li>
                </ul>
                
                <h2>4. Les Listes</h2>
                <p>HTML propose deux types de listes principales :</p>
                
                <h3>Liste non-ordonnée (&lt;ul&gt;) :</h3>
                <pre><code>&lt;ul&gt;
  &lt;li&gt;Élément 1&lt;/li&gt;
  &lt;li&gt;Élément 2&lt;/li&gt;
  &lt;li&gt;Élément 3&lt;/li&gt;
&lt;/ul&gt;</code></pre>
                
                <h3>Liste ordonnée (&lt;ol&gt;) :</h3>
                <pre><code>&lt;ol&gt;
  &lt;li&gt;Premier élément&lt;/li&gt;
  &lt;li&gt;Deuxième élément&lt;/li&gt;
  &lt;li&gt;Troisième élément&lt;/li&gt;
&lt;/ol&gt;</code></pre>
                
                <h2>5. Exercice pratique</h2>
                <p>Créez une page HTML simple avec :</p>
                <ol>
                    <li>Un titre principal (h1)</li>
                    <li>Deux sections (h2)</li>
                    <li>Dans chaque section, un paragraphe avec du texte mis en forme</li>
                    <li>Une liste à puces</li>
                    <li>Une liste numérotée</li>
                </ol>
                """,
                "difficulte": "debutant",
                "duree_estimee": 15,
                "ordre_affichage": 1,
                "tags": ["html", "texte", "debutant", "formatage", "web"]
            },
            {
                "titre": "Liens et Images en HTML",
                "slug": "liens-images-html",
                "description": "Apprenez à intégrer des liens hypertexte et des images dans vos pages HTML avec des exercices pratiques",
                "contenu_texte": """
                <h1>Liens et Images en HTML</h1>
                
                <h2>Introduction</h2>
                <p>Les liens (hyperliens) et les images sont des éléments fondamentaux du web. Ils permettent de créer des relations entre les pages et d'enrichir le contenu visuel.</p>
                
                <h2>1. Les Liens Hypertexte</h2>
                <p>La balise &lt;a&gt; (anchor) permet de créer des liens hypertexte.</p>
                
                <h3>Syntaxe de base :</h3>
                <pre><code>&lt;a href="URL"&gt;Texte du lien&lt;/a&gt;</code></pre>
                
                <h3>Types de liens :</h3>
                <ul>
                    <li><strong>Lien absolu</strong> : Vers un site externe
                        <pre><code>&lt;a href="https://www.example.com"&gt;Visitez Example&lt;/a&gt;</code></pre>
                    </li>
                    <li><strong>Lien relatif</strong> : Vers une page du même site
                        <pre><code>&lt;a href="/apropos.html"&gt;À propos&lt;/a&gt;</code></pre>
                    </li>
                    <li><strong>Ancre</strong> : Vers une section de la même page
                        <pre><code>&lt;a href="#section2"&gt;Aller à la section 2&lt;/a&gt;</code></pre>
                    </li>
                    <li><strong>Lien mailto</strong> : Pour envoyer un email
                        <pre><code>&lt;a href="mailto:contact@example.com"&gt;Nous contacter&lt;/a&gt;</code></pre>
                    </li>
                </ul>
                
                <h3>Attributs importants :</h3>
                <ul>
                    <li><strong>target="_blank"</strong> : Ouvre le lien dans un nouvel onglet</li>
                    <li><strong>title="description"</strong> : Info-bulle au survol</li>
                    <li><strong>rel="nofollow"</strong> : Indique aux moteurs de recherche de ne pas suivre</li>
                </ul>
                
                <h2>2. Les Images</h2>
                <p>La balise &lt;img&gt; permet d'insérer des images dans une page HTML.</p>
                
                <h3>Syntaxe de base :</h3>
                <pre><code>&lt;img src="chemin/vers/image.jpg" alt="Description de l'image"&gt;</code></pre>
                
                <h3>Attributs essentiels :</h3>
                <ul>
                    <li><strong>src</strong> : Source de l'image (obligatoire)</li>
                    <li><strong>alt</strong> : Texte alternatif (obligatoire pour l'accessibilité)</li>
                    <li><strong>width</strong> et <strong>height</strong> : Dimensions</li>
                    <li><strong>title</strong> : Info-bulle au survol</li>
                </ul>
                
                <h3>Exemple complet :</h3>
                <pre><code>&lt;img src="images/logo.png" 
     alt="Logo de notre entreprise" 
     width="200" 
     height="100" 
     title="Cliquez pour agrandir"&gt;</code></pre>
                
                <h2>3. Images cliquables</h2>
                <p>Combinez une image avec un lien :</p>
                <pre><code>&lt;a href="galerie.html"&gt;
  &lt;img src="miniature.jpg" alt="Voir la galerie"&gt;
&lt;/a&gt;</code></pre>
                
                <h2>4. Bonnes pratiques</h2>
                <ul>
                    <li>Toujours utiliser l'attribut <code>alt</code> pour les images</li>
                    <li>Optimiser les images pour le web (taille et format)</li>
                    <li>Utiliser des URLs relatives pour les ressources internes</li>
                    <li>Testez tous vos liens régulièrement</li>
                </ul>
                
                <h2>5. Exercice pratique</h2>
                <p>Créez une page avec :</p>
                <ol>
                    <li>Un lien vers votre site préféré</li>
                    <li>Un lien vers une autre page de votre site</li>
                    <li>Une image avec description alternative</li>
                    <li>Une image cliquable qui ouvre un lien</li>
                </ol>
                """,
                "difficulte": "debutant",
                "duree_estimee": 20,
                "ordre_affichage": 2,
                "tags": ["html", "liens", "images", "debutant", "web"]
            },
            {
                "titre": "Formulaires HTML Avancés",
                "slug": "formulaires-html-avances",
                "description": "Maîtrisez la création de formulaires HTML complexes avec validation intégrée et bonnes pratiques",
                "contenu_texte": """
                <h1>Formulaires HTML Avancés</h1>
                
                <h2>Introduction</h2>
                <p>Les formulaires HTML permettent aux utilisateurs d'interagir avec votre site web : saisir des données, effectuer des recherches, soumettre des informations, etc.</p>
                
                <h2>1. Structure de base d'un formulaire</h2>
                <pre><code>&lt;form action="/traitement.php" method="POST"&gt;
  &lt;!-- Champs du formulaire ici --&gt;
  &lt;button type="submit"&gt;Envoyer&lt;/button&gt;
&lt;/form&gt;</code></pre>
                
                <h3>Attributs importants :</h3>
                <ul>
                    <li><strong>action</strong> : URL de traitement</li>
                    <li><strong>method</strong> : GET ou POST</li>
                    <li><strong>enctype</strong> : Type d'encodage (pour les fichiers)</li>
                    <li><strong>novalidate</strong> : Désactive la validation HTML5</li>
                </ul>
                
                <h2>2. Types de champs avancés</h2>
                
                <h3>Champs HTML5 :</h3>
                <pre><code>&lt;input type="email" name="email" required&gt;
&lt;input type="url" name="website"&gt;
&lt;input type="tel" name="phone"&gt;
&lt;input type="number" name="age" min="0" max="120"&gt;
&lt;input type="range" name="volume" min="0" max="100"&gt;
&lt;input type="date" name="birthdate"&gt;
&lt;input type="time" name="hour"&gt;
&lt;input type="color" name="color"&gt;
&lt;input type="file" name="document" accept=".pdf,.doc"&gt;</code></pre>
                
                <h2>3. Exercice pratique</h2>
                <p>Créez un formulaire d'inscription avec :</p>
                <ol>
                    <li>Champs texte pour nom et prénom</li>
                    <li>Champ email avec validation</li>
                    <li>Champ date de naissance</li>
                    <li>Liste déroulante pour le pays</li>
                    <li>Cases à cocher pour les centres d'intérêt</li>
                    <li>Zone de texte pour un message</li>
                    <li>Bouton de soumission</li>
                </ol>
                """,
                "difficulte": "intermediaire",
                "duree_estimee": 30,
                "ordre_affichage": 3,
                "tags": ["html", "formulaires", "validation", "intermediaire", "html5"]
            },
            {
                "titre": "HTML5 Sémantique - Structures Modernes",
                "slug": "html5-semantique-structures",
                "description": "Découvrez les nouvelles balises sémantiques d'HTML5 pour une structure plus claire et accessible",
                "contenu_texte": """
                <h1>HTML5 Sémantique - Structures Modernes</h1>
                
                <h2>Introduction</h2>
                <p>HTML5 introduit de nouvelles balises sémantiques qui donnent du sens à la structure de votre page, améliorant ainsi l'accessibilité, le SEO et la maintenabilité du code.</p>
                
                <h2>1. Pourquoi la sémantique ?</h2>
                <ul>
                    <li><strong>Accessibilité</strong> : Les lecteurs d'écran comprennent mieux la structure</li>
                    <li><strong>SEO</strong> : Les moteurs de recherche analysent mieux le contenu</li>
                    <li><strong>Maintenance</strong> : Code plus lisible et compréhensible</li>
                    <li><strong>Style</strong> : Stylisation CSS plus facile et cohérente</li>
                </ul>
                
                <h2>2. Les Nouvelles Balises Sémantiques</h2>
                
                <h3>Structure principale :</h3>
                <pre><code>&lt;header&gt;
  &lt;!-- En-tête de page ou de section --&gt;
&lt;/header&gt;

&lt;nav&gt;
  &lt;!-- Navigation principale --&gt;
&lt;/nav&gt;

&lt;main&gt;
  &lt;!-- Contenu principal unique --&gt;
&lt;/main&gt;

&lt;aside&gt;
  &lt;!-- Contenu complémentaire --&gt;
&lt;/aside&gt;

&lt;footer&gt;
  &lt;!-- Pied de page --&gt;
&lt;/footer&gt;</code></pre>
                
                <h3>Exemple de structure complète :</h3>
                <pre><code>&lt;body&gt;
  &lt;header&gt;
    &lt;h1&gt;Mon Site Web&lt;/h1&gt;
    &lt;nav&gt;
      &lt;ul&gt;
        &lt;li&gt;&lt;a href="/"&gt;Accueil&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="/articles"&gt;Articles&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href="/contact"&gt;Contact&lt;/a&gt;&lt;/li&gt;
      &lt;/ul&gt;
    &lt;/nav&gt;
  &lt;/header&gt;
  
  &lt;main&gt;
    &lt;article&gt;
      &lt;header&gt;
        &lt;h2&gt;Titre de l'article&lt;/h2&gt;
        &lt;p&gt;Publié le &lt;time datetime="2024-01-10"&gt;10 janvier 2024&lt;/time&gt;&lt;/p&gt;
      &lt;/header&gt;
      
      &lt;section&gt;
        &lt;h3&gt;Introduction&lt;/h3&gt;
        &lt;p&gt;Contenu de l'introduction...&lt;/p&gt;
      &lt;/section&gt;
    &lt;/article&gt;
  &lt;/main&gt;
  
  &lt;footer&gt;
    &lt;p&gt;&amp;copy; 2024 Mon Site Web&lt;/p&gt;
  &lt;/footer&gt;
&lt;/body&gt;</code></pre>
                
                <h2>3. Bonnes pratiques</h2>
                <ul>
                    <li>Utilisez <code>&lt;main&gt;</code> une seule fois par page</li>
                    <li>Un <code>&lt;header&gt;</code> et <code>&lt;footer&gt;</code> peuvent être utilisés dans chaque <code>&lt;article&gt;</code> ou <code>&lt;section&gt;</code></li>
                    <li><code>&lt;article&gt;</code> doit être autonome (compréhensible hors contexte)</li>
                    <li><code>&lt;section&gt;</code> doit toujours avoir un titre (h1-h6)</li>
                    <li>Utilisez <code>&lt;nav&gt;</code> pour les liens de navigation principaux</li>
                </ul>
                
                <h2>4. Exercice pratique</h2>
                <p>Créez une page avec :</p>
                <ol>
                    <li>Un en-tête avec logo et navigation</li>
                    <li>Un article avec titre, date et contenu</li>
                    <li>Deux sections dans l'article</li>
                    <li>Une barre latérale avec contenu complémentaire</li>
                    <li>Un pied de page</li>
                </ol>
                """,
                "difficulte": "intermediaire",
                "duree_estimee": 25,
                "ordre_affichage": 4,
                "tags": ["html5", "semantique", "structure", "accessibilite", "seo", "modern"]
            },
            {
                "titre": "CSS pour HTML - Mise en Page Avancée",
                "slug": "css-html-mise-en-page",
                "description": "Apprenez à utiliser CSS Flexbox et Grid pour créer des mises en page modernes, responsives et professionnelles",
                "contenu_texte": """
                <h1>CSS pour HTML - Mise en Page Avancée</h1>
                
                <h2>Introduction</h2>
                <p>Les mises en page modernes nécessitent des techniques CSS avancées pour créer des designs responsives, flexibles et maintenables. Flexbox et Grid sont deux modules CSS puissants qui révolutionnent la création de layouts.</p>
                
                <h2>1. Flexbox (Flexible Box Layout)</h2>
                <p>Flexbox est conçu pour distribuer l'espace dans un conteneur et aligner les éléments de manière prévisible, même quand leur taille est inconnue ou dynamique.</p>
                
                <h3>Activer Flexbox :</h3>
                <pre><code>.container {
  display: flex;
}</code></pre>
                
                <h3>Propriétés principales :</h3>
                <pre><code>.container {
  display: flex;
  flex-direction: row | row-reverse | column | column-reverse;
  justify-content: flex-start | flex-end | center | space-between | space-around | space-evenly;
  align-items: stretch | flex-start | flex-end | center | baseline;
  flex-wrap: nowrap | wrap | wrap-reverse;
  gap: 10px; /* Espacement entre les éléments */
}</code></pre>
                
                <h2>2. CSS Grid Layout</h2>
                <p>CSS Grid permet de créer des layouts bidimensionnels (lignes et colonnes) avec un contrôle précis sur la disposition des éléments.</p>
                
                <h3>Activer Grid :</h3>
                <pre><code>.container {
  display: grid;
}</code></pre>
                
                <h3>Définir la grille :</h3>
                <pre><code>.container {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr; /* 3 colonnes */
  grid-template-rows: 100px auto 100px; /* 3 lignes */
  gap: 20px; /* Espacement */
}</code></pre>
                
                <h2>3. Exercice pratique</h2>
                <p>Créez un layout responsive avec :</p>
                <ol>
                    <li>En-tête qui prend toute la largeur</li>
                    <li>Menu de navigation en Flexbox</li>
                    <li>Layout principal en Grid (sidebar + content)</li>
                    <li>Pied de page</li>
                    <li>Adaptation mobile avec media queries</li>
                </ol>
                """,
                "difficulte": "avance",
                "duree_estimee": 40,
                "ordre_affichage": 5,
                "tags": ["css", "flexbox", "grid", "responsive", "avance", "layout", "design"]
            }
        ]
        
        print(f"\n📚 Création de {len(cours_a_creer)} cours...")
        
        cours_crees = 0
        cours_existants = 0
        
        for cours in cours_a_creer:
            
            cur.execute("SELECT id FROM cours_html WHERE slug = %s", (cours["slug"],))
            
            result = cur.fetchone()
            
            if result:
                cours_existants += 1
                print(f"⚠️ Cours déjà existant : {cours['titre'][:40]}...")
                continue
            
            try:
                
                cur.execute("""
                    INSERT INTO cours_html 
                    (titre, slug, description, contenu_texte, difficulte, 
                     duree_estimee, ordre_affichage, tags, est_actif, 
                     created_by, date_creation, date_maj, last_modified_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, %s)
                    RETURNING id
                """, (
                    cours["titre"],
                    cours["slug"],
                    cours["description"],
                    cours["contenu_texte"],
                    cours["difficulte"],
                    cours["duree_estimee"],
                    cours["ordre_affichage"],
                    cours["tags"],
                    True,
                    admin_id,  
                    admin_id   
                ))
                
                cours_id = cur.fetchone()[0]
                cours_crees += 1
                print(f"✅ Cours créé (ID {cours_id}): {cours['titre'][:40]}...")
                
            except Exception as e:
                print(f"❌ Erreur lors de la création du cours '{cours['titre'][:30]}...': {e}")
                
                conn.rollback()
                cur.close()
                conn.close()
                return False
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"\n📊 RÉSUMÉ DE CRÉATION :")
        print(f"   • Cours créés avec succès : {cours_crees}")
        print(f"   • Cours déjà existants : {cours_existants}")
        print(f"   • Total traités : {cours_crees + cours_existants}")
        
        if cours_crees > 0:
            print(f"\n🎉 Les cours ont été créés avec succès !")
            print(f"   Créés par l'utilisateur ID: {admin_id}")
            return True
        else:
            print(f"\nℹ️ Aucun nouveau cours créé (tous existaient déjà).")
            return True
        
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE lors de la création des cours: {e}")
        import traceback
        traceback.print_exc()
        return False

def creer_questions_pour_cours():
    
    try:
        
        admin_id = get_admin_user()
        if not admin_id:
            print("❌ Impossible de trouver un utilisateur valide")
            return False
        
        conn = get_connection()
        if not conn:
            return False
        
        cur = conn.cursor()
        
        print("\n📝 Création des questions de quiz...")
        
        
        questions_par_cours = {
            "formatage-texte-html-debutant": [
                {
                    "question": "Quelle balise utiliser pour le titre principal d'une page HTML ?",
                    "type_question": "choix_multiple",
                    "points": 10,
                    "difficulte": "facile",
                    "options": {
                        "A": "<title>",
                        "B": "<h1>", 
                        "C": "<head>",
                        "D": "<header>"
                    },
                    "reponse_correcte": "B",
                    "explication": "La balise <h1> est utilisée pour le titre principal d'une page. <title> définit le titre de l'onglet, <head> est pour les métadonnées, et <header> pour l'en-tête de section.",
                    "mode_specifique": "texte"
                },
                {
                    "question": "Quelle est la différence entre <strong> et <b> en HTML ?",
                    "type_question": "choix_multiple",
                    "points": 15,
                    "difficulte": "moyen",
                    "options": {
                        "A": "Aucune différence, ce sont des synonymes",
                        "B": "<strong> est sémantique (important), <b> est seulement visuel (gras)",
                        "C": "<b> est plus récent et devrait toujours être utilisé",
                        "D": "<strong> fonctionne seulement dans les titres"
                    },
                    "reponse_correcte": "B",
                    "explication": "<strong> a une signification sémantique (contenu important), tandis que <b> est seulement pour l'apparence visuelle. Pour l'accessibilité et le SEO, préférez <strong>.",
                    "mode_specifique": "texte"
                }
            ]
        }
        
        total_questions_creees = 0
        
        for slug, questions in questions_par_cours.items():
            
            cur.execute("SELECT id, titre FROM cours_html WHERE slug = %s", (slug,))
            cours_result = cur.fetchone()
            
            if not cours_result:
                print(f"❌ Cours '{slug}' non trouvé")
                continue
            
            cours_id, cours_titre = cours_result
            
            print(f"\n📚 Création des questions pour: {cours_titre[:40]}...")
            
            questions_creees = 0
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
                        json.dumps(q["options"]),
                        q["reponse_correcte"],
                        q["explication"],
                        q["mode_specifique"],
                        admin_id  
                    ))
                    
                    question_id = cur.fetchone()[0]
                    questions_creees += 1
                    print(f"  ✅ Question créée: {q['question'][:40]}...")
                    
                except Exception as e:
                    print(f"  ❌ Erreur sur la question: {e}")
            
            total_questions_creees += questions_creees
            print(f"  📊 {questions_creees} questions créées pour ce cours")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"\n📝 TOTAL: {total_questions_creees} questions créées")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des questions: {e}")
        import traceback
        traceback.print_exc()
        return False

def lister_cours_existants():
    
    try:
        conn = get_connection()
        if not conn:
            return False
        
        cur = conn.cursor()
        
        cur.execute("""
            SELECT c.id, c.titre, c.slug, c.difficulte, c.est_actif, 
                   c.date_creation, COUNT(q.id) as nb_questions,
                   c.duree_estimee, c.tags, u.email as createur
            FROM cours_html c
            LEFT JOIN questions_quiz q ON c.id = q.cours_id
            LEFT JOIN utilisateurs u ON c.created_by = u.id
            GROUP BY c.id, c.titre, c.slug, c.difficulte, c.est_actif, 
                     c.date_creation, c.duree_estimee, c.tags, u.email
            ORDER BY c.ordre_affichage, c.date_creation
        """)
        
        cours = cur.fetchall()
        
        print("\n" + "=" * 120)
        print("📚 LISTE COMPLÈTE DES COURS EXISTANTS")
        print("=" * 120)
        print(f"{'ID':<4} {'Actif':<6} {'Difficulté':<12} {'Durée':<6} {'Questions':<10} {'Créé par'}")
        print("-" * 120)
        
        for c in cours:
            c_id, titre, slug, difficulte, est_actif, date_creation, nb_questions, duree, tags, createur = c
            statut = "✅" if est_actif else "⏸️"
            createur_display = createur if createur else "Inconnu"
            print(f"{c_id:<4} {statut:<6} {difficulte:<12} {duree:<6}min {nb_questions:<10} {createur_display}")
            print(f"     {titre[:80]}...")
            print(f"     Slug: {slug}")
            print()
        
        print(f"📊 Total: {len(cours)} cours dans la base de données")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du listing des cours: {e}")
        return False

def menu_principal():
    
    print("\n" + "=" * 60)
    print("🎓 PLATEFORME E-LEARNING - GESTION DES COURS")
    print("=" * 60)
    print("\nQue souhaitez-vous faire ?")
    print("1. Créer tous les cours HTML (5 cours)")
    print("2. Créer les questions de quiz")
    print("3. Lister les cours existants")
    print("4. Tout faire (cours + questions)")
    print("5. Quitter")
    
    choix = input("\nVotre choix (1-5) : ").strip()
    
    if choix == "1":
        print("\n" + "🚀" * 30)
        print("CRÉATION DES COURS HTML")
        print("🚀" * 30)
        success = creer_cours_html()
        if success:
            print("\n✅ Opération terminée avec succès !")
        else:
            print("\n❌ Des erreurs sont survenues.")
            
    elif choix == "2":
        print("\n" + "📝" * 30)
        print("CRÉATION DES QUESTIONS DE QUIZ")
        print("📝" * 30)
        success = creer_questions_pour_cours()
        if success:
            print("\n✅ Questions créées avec succès !")
        else:
            print("\n❌ Des erreurs sont survenues.")
            
    elif choix == "3":
        print("\n" + "📚" * 30)
        print("LISTE DES COURS EXISTANTS")
        print("📚" * 30)
        lister_cours_existants()
        
    elif choix == "4":
        print("\n" + "⚡" * 30)
        print("CRÉATION COMPLÈTE (COURS + QUESTIONS)")
        print("⚡" * 30)
        if creer_cours_html():
            creer_questions_pour_cours()
        print("\n✅ Opération complète terminée !")
        
    elif choix == "5":
        print("\n👋 Au revoir ! Merci d'avoir utilisé la plateforme e-learning.")
        return False
    else:
        print("❌ Choix invalide. Veuillez choisir un nombre entre 1 et 5.")
    
    input("\nAppuyez sur Entrée pour continuer...")
    return True

def main():
    
    print("\n" + "🌟" * 30)
    print("🔧 INITIALISATION DU SYSTÈME E-LEARNING")
    print("🌟" * 30)
    
    
    print("\n🔍 Test de connexion à la base de données...")
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        print("   Vérifiez vos paramètres de connexion dans la fonction get_connection()")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    continuer = True
    while continuer:
        continuer = menu_principal()
    
    print("\n" + "🎉" * 30)
    print("SCRIPT TERMINÉ AVEC SUCCÈS")
    print("🎉" * 30)

if __name__ == "__main__":
    main()