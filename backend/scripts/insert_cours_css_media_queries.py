
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
        
        cur.execute("SELECT id FROM chapitres WHERE id = 2 OR titre ILIKE %s", (f'%{chapitre_titre}%',))
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result:
            chapitre_id = result[0]
            print(f"📚 Chapitre trouvé: ID {chapitre_id}")
            return chapitre_id
        return None
    except Exception as e:
        print(f"⚠️ Erreur récupération chapitre: {e}")
        return None

def inserer_cours_css_media_queries():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    
    chapitre_id = get_chapitre_id("CSS")
    if chapitre_id:
        print(f"📚 Chapitre CSS trouvé (ID: {chapitre_id})")
    else:
        print("⚠️ Chapitre CSS non trouvé, le cours sera inséré sans chapitre")
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    
    slug_cours = "css-media-queries-responsive-design"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    
    contenu_html = """
    <h1>📱 CSS Media Queries - Fondamentaux du Responsive Design</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Les media queries sont la base du responsive design. Elles permettent d'adapter les styles CSS en fonction des caractéristiques de l'appareil (largeur d'écran, orientation, type d'affichage, etc.).</p>
    </div>
    
    <h2>Introduction aux Media Queries</h2>
    <p>Les CSS media queries sont essentielles pour créer des sites web responsives qui s'adaptent à différents appareils : ordinateurs, tablettes, smartphones, et même les impressions papier.</p>
    
    <div class="tip-box">
        <p><strong>💡 Astuce :</strong> Sans media queries, les sites web ressemblent à la version desktop sur mobile, ce qui rend la navigation difficile. Les media queries résolvent ce problème.</p>
    </div>
    
    <h2>1. Syntaxe de base des Media Queries</h2>
    <p>La syntaxe utilise le mot-clé <code>@media</code> suivi d'un type d'appareil et d'une condition :</p>
    
    <pre><code>@media (condition) {
    /* Styles CSS appliqués si la condition est vraie */
}</code></pre>
    
    <h3>Types d'appareils (media types) :</h3>
    <ul>
        <li><strong>screen</strong> : Écrans d'ordinateurs, tablettes, smartphones</li>
        <li><strong>print</strong> : Impression papier</li>
        <li><strong>speech</strong> : Lecteurs d'écran (synthèse vocale)</li>
        <li><strong>all</strong> : Tous les types d'appareils</li>
    </ul>
    
    <h3>Exemple basique :</h3>
    <pre><code>/* Style par défaut (couleur rouge) */
body {
    color: red;
}

/* Si l'écran a une largeur maximale de 500px */
@media (max-width: 500px) {
    body {
        color: blue; /* La couleur devient bleue */
    }
}</code></pre>
    
    <p>Résultat : Le texte est rouge sur les grands écrans, mais devient bleu lorsque la largeur de l'écran est inférieure à 500px.</p>
    
    <h2>2. Media Queries pour l'impression</h2>
    <p>Vous pouvez créer des styles spécifiques pour l'impression papier en utilisant <code>@media print</code> :</p>
    
    <pre><code>/* Styles normaux pour l'écran */
body {
    color: black;
}

/* Styles spécifiques à l'impression */
@media print {
    body {
        color: blue; /* Le texte devient bleu sur papier */
    }
    .no-print {
        display: none; /* Masque certains éléments à l'impression */
    }
}</code></pre>
    
    <div class="info-box">
        <p><strong>💡 Utilité :</strong> Idéal pour supprimer les menus de navigation, les publicités ou changer les couleurs lors de l'impression.</p>
    </div>
    
    <h2>3. Media Queries pour l'orientation</h2>
    <p>Les requêtes d'orientation permettent de détecter si l'appareil est en mode paysage ou portrait :</p>
    
    <pre><code>/* Mode paysage (écran large en largeur) */
@media (orientation: landscape) {
    h1 {
        color: green; /* Titre vert en paysage */
    }
}

/* Mode portrait (écran plus haut que large) */
@media (orientation: portrait) {
    h2 {
        color: cyan; /* Sous-titre cyan en portrait */
    }
}</code></pre>
    
    <div class="tip-box">
        <p><strong>📱 Cas d'usage :</strong> Utile pour les applications mobiles où la mise en page diffère selon comment l'utilisateur tient son appareil.</p>
    </div>
    
    <h2>4. Combinaison de conditions</h2>
    
    <h3>ET logique (&) :</h3>
    <pre><code>/* Mode paysage ET largeur minimale de 600px */
@media (orientation: landscape) and (min-width: 600px) {
    .content {
        display: flex; /* Mise en page flexbox */
    }
}</code></pre>
    
    <h3>OU logique (,) :</h3>
    <pre><code>/* Soit pour l'impression, soit pour les écrans de petite taille */
@media print, (max-width: 400px) {
    body {
        font-size: 12px; /* Police plus petite */
    }
}</code></pre>
    
    <h2>5. Les sélecteurs les plus utiles</h2>
    
    <ul>
        <li><strong>max-width</strong> : Applique les styles lorsque la largeur est <strong>inférieure ou égale</strong> à une valeur</li>
        <li><strong>min-width</strong> : Applique les styles lorsque la largeur est <strong>supérieure ou égale</strong> à une valeur</li>
        <li><strong>orientation</strong> : Détecte l'orientation (landscape ou portrait)</li>
        <li><strong>print</strong> : Styles spécifiques à l'impression</li>
    </ul>
    
    <h3>Exemple avec min-width et max-width :</h3>
    <pre><code>/* Mobile (jusqu'à 768px) */
@media (max-width: 768px) {
    .container {
        width: 100%;
    }
}

/* Tablette (769px à 1024px) */
@media (min-width: 769px) and (max-width: 1024px) {
    .container {
        width: 90%;
    }
}

/* Desktop (plus de 1024px) */
@media (min-width: 1025px) {
    .container {
        width: 80%;
    }
}</code></pre>
    
    <h2>6. Ordre et spécificité CSS</h2>
    <div class="warning-box">
        <p><strong>⚠️ Important :</strong> L'ordre des règles CSS compte ! Les règles qui apparaissent plus tard dans la feuille de style l'emportent sur celles qui apparaissent avant, même à l'intérieur des media queries.</p>
    </div>
    
    <pre><code>/* Cette règle sera ignorée si elle apparaît avant la suivante */
@media (max-width: 500px) {
    p {
        color: blue;
    }
}

/* Cette règle l'emporte car elle est plus récente */
@media (max-width: 500px) {
    p {
        color: green;
    }
}</code></pre>
    
    <h2>7. Breakpoints communs pour responsive design</h2>
    <p>Voici les breakpoints les plus utilisés pour les appareils standards :</p>
    
    <pre><code>/* Smartphones très petits (portrait) */
@media (max-width: 480px) { }

/* Smartphones (portrait et paysage) */
@media (min-width: 481px) and (max-width: 768px) { }

/* Tablettes (portrait et paysage) */
@media (min-width: 769px) and (max-width: 1024px) { }

/* Desktops et laptops */
@media (min-width: 1025px) and (max-width: 1280px) { }

/* Grands écrans (TV, etc.) */
@media (min-width: 1281px) { }</code></pre>
    
    <h2>8. Exercice pratique</h2>
    <p>Créez une page HTML/CSS responsive avec les caractéristiques suivantes :</p>
    <ol>
        <li>Par défaut : fond blanc, texte noir</li>
        <li>Sur écran < 600px : fond gris clair, texte bleu</li>
        <li>En orientation paysage : les titres doivent être en vert</li>
        <li>À l'impression : le texte doit être en noir avec fond blanc, et le menu de navigation doit être masqué</li>
        <li>Pour les écrans de tablette (entre 768px et 1024px) : conteneur principal à 90% de largeur</li>
    </ol>
    
    <div class="info-box">
        <p><strong>💡 Rappel :</strong> Les media queries sont la fondation du responsive design. Maîtrisez-les pour créer des sites web qui fonctionnent parfaitement sur tous les appareils !</p>
    </div>
    """.strip()
    
    
    cours_data = {
        "titre": "CSS Media Queries - Fondamentaux du Responsive Design",
        "slug": slug_cours,
        "description": "Apprenez à utiliser les CSS Media Queries pour créer des sites web responsives. Découvrez la syntaxe @media, les types d'appareils (screen, print), les conditions (max-width, min-width, orientation), et comment combiner les conditions pour adapter vos styles à tous les écrans.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 25,
        "ordre_affichage": 16,
        "chapitre_id": chapitre_id,  
        "tags": ["css", "media queries", "responsive", "responsive design", "max-width", "min-width", "orientation", "print", "breakpoints", "mobile", "tablet", "desktop"],
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
            print(f"   📚 Associé au chapitre CSS (ID: {chapitre_id})")
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
            print(f"   📚 Associé au chapitre CSS (ID: {chapitre_id})")
    
    conn.commit()
    return cours_id

def inserer_questions_css_media_queries(cours_id):
    
    
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
            "question": "Quel est le rôle principal des CSS Media Queries ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "Rendre les sites web plus rapides",
                "B": "Adapter les styles CSS à différents appareils et conditions",
                "C": "Créer des animations CSS",
                "D": "Optimiser les images"
            },
            "reponse_correcte": "B",
            "explication": "Les media queries permettent d'adapter les styles CSS en fonction des caractéristiques de l'appareil (taille d'écran, orientation, type d'affichage, etc.).",
            "mode_specifique": "texte"
        },
        {
            "question": "Quelle est la syntaxe correcte pour une media query ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "@media (max-width: 500px) { }",
                "B": "@query (max-width: 500px) { }",
                "C": "@responsive (max-width: 500px) { }",
                "D": "@screen (max-width: 500px) { }"
            },
            "reponse_correcte": "A",
            "explication": "La syntaxe correcte utilise @media suivie de la condition entre parenthèses et des styles entre accolades.",
            "mode_specifique": "video"
        },
        {
            "question": "Le type d'appareil 'print' est utilisé pour :",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "Les écrans d'ordinateur",
                "B": "Les impressions papier",
                "C": "Les lecteurs d'écran",
                "D": "Tous les appareils"
            },
            "reponse_correcte": "B",
            "explication": "@media print permet d'appliquer des styles spécifiques uniquement lors de l'impression de la page.",
            "mode_specifique": "video"
        },
        {
            "question": "Que signifie la condition 'orientation: landscape' ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "L'écran est en mode portrait (plus haut que large)",
                "B": "L'écran est en mode paysage (plus large que haut)",
                "C": "L'écran est en noir et blanc",
                "D": "L'écran a une résolution élevée"
            },
            "reponse_correcte": "B",
            "explication": "landscape signifie que la largeur de l'écran est supérieure à sa hauteur (paysage).",
            "mode_specifique": "audio"
        },
        {
            "question": "Comment combiner deux conditions avec un ET logique dans une media query ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "@media (condition1) OR (condition2)",
                "B": "@media (condition1, condition2)",
                "C": "@media (condition1) and (condition2)",
                "D": "@media (condition1) && (condition2)"
            },
            "reponse_correcte": "C",
            "explication": "Le mot-clé 'and' permet de combiner plusieurs conditions avec un ET logique.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle media query est la plus courante pour cibler les smartphones ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "@media (max-width: 480px)",
                "B": "@media (min-width: 1024px)",
                "C": "@media (orientation: landscape)",
                "D": "@media print"
            },
            "reponse_correcte": "A",
            "explication": "max-width: 480px est un breakpoint courant pour cibler les smartphones en mode portrait.",
            "mode_specifique": "texte"
        },
        {
            "question": "Que signifie 'min-width: 768px' ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "Pour les écrans jusqu'à 768px",
                "B": "Pour les écrans de 768px et plus",
                "C": "Pour les écrans exactement à 768px",
                "D": "Pour les écrans inférieurs à 768px"
            },
            "reponse_correcte": "B",
            "explication": "min-width: 768px applique les styles aux écrans ayant une largeur minimale de 768px.",
            "mode_specifique": "texte"
        },
        {
            "question": "Comment combiner des conditions avec un OU logique dans une media query ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "@media (condition1) or (condition2)",
                "B": "@media (condition1) and (condition2)",
                "C": "@media (condition1, condition2)",
                "D": "@media (condition1) || (condition2)"
            },
            "reponse_correcte": "C",
            "explication": "La virgule ',' sert d'opérateur OU dans les media queries.",
            "mode_specifique": "video"
        },
        {
            "question": "Pourquoi l'ordre des règles CSS est-il important avec les media queries ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "Les media queries n'ont pas besoin d'ordre spécifique",
                "B": "Les règles qui apparaissent plus tard l'emportent sur les précédentes",
                "C": "L'ordre n'a pas d'importance en CSS",
                "D": "Les media queries doivent toujours être en premier"
            },
            "reponse_correcte": "B",
            "explication": "En CSS, les règles définies plus tard dans la feuille de style l'emportent sur celles définies avant, même à l'intérieur des media queries.",
            "mode_specifique": "video"
        },
        {
            "question": "Quel est l'avantage des media queries pour les sites web modernes ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "Elles permettent de créer des animations complexes",
                "B": "Elles sont la base du responsive design (adaptation mobile/tablette/desktop)",
                "C": "Elles remplacent JavaScript",
                "D": "Elles améliorent uniquement le référencement SEO"
            },
            "reponse_correcte": "B",
            "explication": "Les media queries sont la fondation du responsive design, permettant d'adapter l'affichage sur mobile, tablette et desktop.",
            "mode_specifique": "audio"
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
    print("🎓 INSERTION DU COURS: CSS MEDIA QUERIES (RESPONSIVE DESIGN)")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    chapitre_id = get_chapitre_id("CSS")
    if chapitre_id:
        print(f"📚 Chapitre CSS trouvé (ID: {chapitre_id})")
    else:
        print("⚠️ Chapitre CSS non trouvé, le cours sera inséré sans chapitre")
    
    
    cours_id = inserer_cours_css_media_queries()
    
    if cours_id:
        
        inserer_questions_css_media_queries(cours_id)
        
        print(f"\n🎉 Succès ! Le cours 'CSS Media Queries - Fondamentaux du Responsive Design' a été inséré avec succès!")
        print(f"   📚 Cours ID: {cours_id}")
        
        
        lister_cours_et_chapitres()
    else:
        print("\n❌ Échec de l'insertion du cours")

if __name__ == "__main__":
    main()