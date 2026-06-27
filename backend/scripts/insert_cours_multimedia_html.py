# scripts/insert_cours_multimedia_html.py
import psycopg2
import json
from datetime import datetime

def get_connection():
    """Établir la connexion à PostgreSQL"""
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
    """Trouver l'utilisateur admin"""
    try:
        conn = get_connection()
        if not conn:
            return None
        
        cur = conn.cursor()
        
        # Chercher un admin
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
        
        # Sinon, prendre le premier utilisateur
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
    """Récupérer l'ID du chapitre par son titre"""
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

def inserer_cours_multimedia():
    """Insérer le cours sur le multimédia HTML (vidéo, audio et plug-ins)"""
    
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
    
    
    slug_cours = "html-multimedia-video-audio"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    
    contenu_html = """
    <h1>🎬 HTML Multimédia : Vidéo, Audio et Plug-ins</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Le multimédia combine texte, audio, vidéo et animation pour créer des expériences web interactives et engageantes. HTML5 a révolutionné l'intégration multimédia avec des éléments natifs simples à utiliser.</p>
    </div>
    
    <h2>Introduction au Multimédia en HTML</h2>
    <p>Le multimédia sur le web fait référence à tout contenu qui combine différentes formes de médias : texte, audio, vidéo, images, animations. Les navigateurs modernes offrent une interactivité native avec ces éléments grâce aux balises HTML5.</p>
    
    <div class="tip-box">
        <p><strong>💡 Astuce :</strong> L'utilisation du multimédia rend vos pages plus dynamiques et améliore l'engagement des utilisateurs.</p>
    </div>
    
    <h2>1. Formats de fichiers supportés</h2>
    <p>Les formats les plus courants et largement supportés sont :</p>
    <ul>
        <li><strong>Audio :</strong> MP3 (.mp3), WAV, OGG</li>
        <li><strong>Vidéo :</strong> MP4 (.mp4), WebM, OGG</li>
    </ul>
    <p>MP3 pour l'audio et MP4 pour la vidéo sont les formats les plus utilisés à travers le web en raison de leur compatibilité et de leur bonne compression.</p>
    
    <h2>2. La balise &lt;video&gt;</h2>
    <p>La balise <code>&lt;video&gt;</code> permet d'embedder des vidéos directement dans une page HTML sans nécessiter de plug-ins externes.</p>
    
    <h3>Syntaxe de base :</h3>
    <pre><code>&lt;video src="video.mp4" width="640" height="360" controls&gt;
    Votre navigateur ne supporte pas la balise vidéo.
&lt;/video&gt;</code></pre>
    
    <h3>Attributs importants de &lt;video&gt; :</h3>
    <ul>
        <li><strong>src</strong> : Chemin ou URL du fichier vidéo</li>
        <li><strong>width</strong> : Largeur de la vidéo en pixels</li>
        <li><strong>height</strong> : Hauteur de la vidéo en pixels</li>
        <li><strong>controls</strong> : Affiche les contrôles de lecture (play, pause, volume)</li>
        <li><strong>autoplay</strong> : Démarre la vidéo automatiquement</li>
        <li><strong>loop</strong> : Relance la vidéo en boucle</li>
        <li><strong>muted</strong> : Coupe le son par défaut</li>
        <li><strong>poster</strong> : Image d'aperçu avant la lecture</li>
    </ul>
    
    <h3>Exemple complet :</h3>
    <pre><code>&lt;video width="640" height="360" controls poster="preview.jpg"&gt;
    &lt;source src="video.mp4" type="video/mp4"&gt;
    &lt;source src="video.webm" type="video/webm"&gt;
    Votre navigateur ne supporte pas la balise vidéo.
&lt;/video&gt;</code></pre>
    
    <h2>3. La balise &lt;audio&gt;</h2>
    <p>La balise <code>&lt;audio&gt;</code> fonctionne de manière similaire à &lt;video&gt; mais pour le contenu audio.</p>
    
    <h3>Syntaxe de base :</h3>
    <pre><code>&lt;audio src="audio.mp3" controls&gt;
    Votre navigateur ne supporte pas la balise audio.
&lt;/audio&gt;</code></pre>
    
    <h3>Attributs de &lt;audio&gt; :</h3>
    <ul>
        <li><strong>src</strong> : Chemin ou URL du fichier audio</li>
        <li><strong>controls</strong> : Affiche play, pause, volume</li>
        <li><strong>autoplay</strong> : Joue automatiquement</li>
        <li><strong>loop</strong> : Relance en boucle</li>
        <li><strong>muted</strong> : Démarre muet</li>
    </ul>
    
    <h3>Exemple avec sources multiples :</h3>
    <pre><code>&lt;audio controls&gt;
    &lt;source src="audio.mp3" type="audio/mpeg"&gt;
    &lt;source src="audio.ogg" type="audio/ogg"&gt;
    Votre navigateur ne supporte pas la balise audio.
&lt;/audio&gt;</code></pre>
    
    <h2>4. Balises &lt;source&gt; pour multiples formats</h2>
    <p>La balise <code>&lt;source&gt;</code> permet de spécifier plusieurs formats pour un même média. Le navigateur choisit le premier format qu'il supporte.</p>
    
    <pre><code>&lt;video controls width="640"&gt;
    &lt;source src="video.mp4" type="video/mp4"&gt;
    &lt;source src="video.webm" type="video/webm"&gt;
    &lt;source src="video.ogv" type="video/ogg"&gt;
    Votre navigateur ne supporte pas la balise vidéo.
&lt;/video&gt;</code></pre>
    
    <h2>5. Plug-ins et méthodes héritées</h2>
    <p>Avant HTML5, on utilisait des plug-ins externes comme Flash, Silverlight ou QuickTime. Les méthodes anciennes incluent :</p>
    
    <h3>La balise &lt;object&gt; :</h3>
    <pre><code>&lt;object data="video.swf" width="640" height="360"&gt;
    &lt;param name="movie" value="video.swf"&gt;
    Votre navigateur ne supporte pas ce contenu.
&lt;/object&gt;</code></pre>
    
    <h3>La balise &lt;embed&gt; :</h3>
    <pre><code>&lt;embed src="video.swf" width="640" height="360"&gt;</code></pre>
    
    <div class="warning-box">
        <p><strong>⚠️ Note :</strong> Les balises &lt;object&gt; et &lt;embed&gt; sont moins courantes aujourd'hui car HTML5 offre des solutions natives plus simples, plus sûres et plus performantes. Les plug-ins comme Flash sont progressivement abandonnés.</p>
    </div>
    
    <h2>6. Bonnes pratiques pour le multimédia</h2>
    <ul>
        <li><strong>Toujours inclure l'attribut <code>controls</code></strong> pour que l'utilisateur puisse contrôler la lecture</li>
        <li><strong>Fournir plusieurs formats</strong> avec &lt;source&gt; pour la compatibilité navigateurs</li>
        <li><strong>Ajouter un texte alternatif</strong> pour l'accessibilité (le contenu entre les balises)</li>
        <li><strong>Optimiser les fichiers</strong> : compressez vos vidéos et audios pour réduire le temps de chargement</li>
        <li><strong>Éviter l'autoplay</strong> sauf si essentiel - respectez l'expérience utilisateur</li>
        <li><strong>Utiliser des sous-titres</strong> pour les vidéos avec <code>&lt;track&gt;</code></li>
    </ul>
    
    <h2>7. Exercice pratique</h2>
    <p>Créez une page HTML qui intègre à la fois une vidéo et un fichier audio :</p>
    <ol>
        <li>Un lecteur vidéo avec une largeur de 640px et les contrôles</li>
        <li>Un lecteur audio avec les contrôles</li>
        <li>Au moins deux formats de source pour chaque média (MP4/WebM pour vidéo, MP3/OGG pour audio)</li>
        <li>Un texte alternatif pour les navigateurs non supportés</li>
        <li>Une image poster pour la vidéo</li>
    </ol>
    
    <div class="info-box">
        <p><strong>💡 Conseil :</strong> Testez toujours votre multimédia sur différents navigateurs pour vous assurer de la compatibilité.</p>
    </div>
    """.strip()
    
    
    cours_data = {
        "titre": "HTML Multimédia : Vidéo, Audio et Plug-ins",
        "slug": slug_cours,
        "description": "Apprenez à intégrer et utiliser du contenu multimédia dans vos pages web. Découvrez les balises HTML5 <video> et <audio>, les formats supportés (MP3, MP4), les attributs (controls, width, height), et les méthodes héritées avec <object> et <embed>.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 35,
        "ordre_affichage": 15,
        "chapitre_id": chapitre_id,
        "tags": ["html", "multimedia", "video", "audio", "mp3", "mp4", "webm", "controls", "embed", "object", "debutant"],
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
        # Insertion
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

def inserer_questions_multimedia(cours_id):
    
    
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
            "question": "Que permet de faire la balise <video> en HTML5 ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "Jouer uniquement des fichiers audio",
                "B": "Embedder des vidéos sans plug-ins externes",
                "C": "Créer des animations",
                "D": "Afficher des images"
            },
            "reponse_correcte": "B",
            "explication": "La balise <video> permet d'embedder des vidéos directement dans une page HTML sans nécessiter de plug-ins externes comme Flash.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quel attribut permet d'afficher les contrôles de lecture (play, pause, volume) pour une vidéo ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "autoplay",
                "B": "loop",
                "C": "controls",
                "D": "display"
            },
            "reponse_correcte": "C",
            "explication": "L'attribut 'controls' affiche les contrôles de lecture natifs du navigateur (play, pause, volume, progression).",
            "mode_specifique": "video"
        },
        {
            "question": "Quels sont les formats de fichiers multimédia les plus couramment supportés sur le web ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "MP3 pour l'audio, MP4 pour la vidéo",
                "B": "WAV pour l'audio, AVI pour la vidéo",
                "C": "FLAC pour l'audio, MKV pour la vidéo",
                "D": "OGG pour l'audio, MOV pour la vidéo"
            },
            "reponse_correcte": "A",
            "explication": "MP3 pour l'audio et MP4 pour la vidéo sont les formats les plus largement supportés à travers tous les navigateurs modernes.",
            "mode_specifique": "audio"
        },
        {
            "question": "Comment spécifier plusieurs formats pour une même vidéo afin d'assurer la compatibilité ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "Utiliser plusieurs attributs src",
                "B": "Utiliser la balise <source>",
                "C": "Convertir la vidéo en un seul format universel",
                "D": "Utiliser la balise <track>"
            },
            "reponse_correcte": "B",
            "explication": "La balise <source> permet de spécifier plusieurs formats de média. Le navigateur choisit le premier format qu'il supporte.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quelles étaient les méthodes utilisées avant HTML5 pour intégrer du multimédia ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "<video> et <audio>",
                "B": "<source> et <track>",
                "C": "<object> et <embed>",
                "D": "<media> et <content>"
            },
            "reponse_correcte": "C",
            "explication": "Avant HTML5, on utilisait les balises <object> et <embed> avec des plug-ins externes comme Flash ou QuickTime.",
            "mode_specifique": "video"
        },
        {
            "question": "Quel attribut de la balise <video> permet d'afficher une image d'aperçu avant le début de la lecture ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "preview",
                "B": "thumbnail",
                "C": "poster",
                "D": "image"
            },
            "reponse_correcte": "C",
            "explication": "L'attribut 'poster' spécifie une image à afficher avant que la vidéo ne commence à jouer.",
            "mode_specifique": "texte"
        },
        {
            "question": "Pourquoi les balises <object> et <embed> sont-elles moins utilisées aujourd'hui ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "Elles sont trop complexes à utiliser",
                "B": "HTML5 offre des solutions natives plus simples et plus sûres",
                "C": "Elles ne fonctionnent que sur Windows",
                "D": "Elles sont payantes"
            },
            "reponse_correcte": "B",
            "explication": "HTML5 propose les balises natives <video> et <audio> qui sont plus simples, plus sûres et ne nécessitent pas de plug-ins externes.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle est la meilleure pratique pour l'expérience utilisateur concernant l'autoplay ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "Toujours utiliser autoplay pour attirer l'attention",
                "B": "Éviter l'autoplay sauf si essentiel",
                "C": "Forcer l'autoplay avec le son",
                "D": "Utiliser autoplay uniquement sur mobile"
            },
            "reponse_correcte": "B",
            "explication": "Il est recommandé d'éviter l'autoplay car cela peut être intrusif pour l'utilisateur. La plupart des navigateurs bloquent également l'autoplay avec son.",
            "mode_specifique": "audio"
        },
        {
            "question": "Que signifie l'abréviation HTML5 dans le contexte du multimédia ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "HyperText Markup Language version 5",
                "B": "High-Tech Media Language 5",
                "C": "Hyper Transfer Media Language 5",
                "D": "Home Text Markup Language 5"
            },
            "reponse_correcte": "A",
            "explication": "HTML5 signifie HyperText Markup Language version 5, la dernière version majeure du langage HTML qui a introduit les balises <video> et <audio> natives.",
            "mode_specifique": "video"
        },
        {
            "question": "Quel attribut permet de définir la largeur d'une vidéo en HTML ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "size",
                "B": "width",
                "C": "dimension",
                "D": "scale"
            },
            "reponse_correcte": "B",
            "explication": "L'attribut 'width' définit la largeur de la vidéo en pixels. Il est souvent utilisé avec 'height' pour maintenir les proportions.",
            "mode_specifique": "texte"
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
    print("🎓 INSERTION DU COURS: HTML MULTIMÉDIA (VIDÉO & AUDIO)")
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
    
    
    cours_id = inserer_cours_multimedia()
    
    if cours_id:
        
        inserer_questions_multimedia(cours_id)
        
        print(f"\n🎉 Succès ! Le cours 'HTML Multimédia : Vidéo, Audio et Plug-ins' a été inséré avec succès!")
        print(f"   📚 Cours ID: {cours_id}")
        
        
        lister_cours_et_chapitres()
    else:
        print("\n❌ Échec de l'insertion du cours")

if __name__ == "__main__":
    main()