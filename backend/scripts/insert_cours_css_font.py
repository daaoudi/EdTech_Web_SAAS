
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

def inserer_cours_css_font():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "css-font-properties"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>🔤 CSS Font - Les Propriétés des Polices en CSS</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Les propriétés CSS pour les polices permettent de contrôler l'apparence du texte : famille, taille, style, graisse et bien plus encore.</p>
    </div>
    
    <h2>Introduction aux Propriétés Font</h2>
    <p>CSS offre de nombreuses propriétés pour personnaliser l'apparence typographique du texte : <code>font-family</code>, <code>font-size</code>, <code>font-weight</code>, <code>font-style</code>, etc.</p>
    
    <h2>1. Familles de polices (font-family)</h2>
    <p>La propriété <code>font-family</code> définit la police à utiliser pour le texte.</p>
    
    <h3>Familles génériques :</h3>
    <ul>
        <li><strong>serif</strong> : Polices avec empattements (ex: Times New Roman)</li>
        <li><strong>sans-serif</strong> : Polices sans empattements (ex: Arial, Helvetica)</li>
        <li><strong>monospace</strong> : Tous les caractères ont la même largeur (ex: Courier New)</li>
        <li><strong>cursive</strong> : Polices cursives (ex: Comic Sans MS)</li>
        <li><strong>fantasy</strong> : Polices décoratives</li>
    </ul>
    
    <h3>Système de fallback :</h3>
    <pre><code>/* Fallback : si Arial n'est pas disponible, on utilise sans-serif */
body {
    font-family: Arial, Helvetica, sans-serif;
}

/* Multi-word fonts need quotes */
h1 {
    font-family: "Times New Roman", Times, serif;
}

/* Monospace pour le code */
code {
    font-family: "Courier New", Courier, monospace;
}</code></pre>
    
    <div class="tip-box">
        <p><strong>💡 Astuce :</strong> Toujours terminer une liste de polices par une famille générique pour garantir une compatibilité maximale.</p>
    </div>
    
    <h2>2. Style de police (font-style)</h2>
    <p>La propriété <code>font-style</code> contrôle si le texte est en italique ou non.</p>
    
    <h3>Valeurs possibles :</h3>
    <ul>
        <li><strong>normal</strong> : Texte normal (par défaut)</li>
        <li><strong>italic</strong> : Texte en italique</li>
        <li><strong>oblique</strong> : Texte incliné (moins supporté que italic)</li>
    </ul>
    
    <pre><code>/* Texte en italique */
em {
    font-style: italic;
}

/* Texte normal */
.normal {
    font-style: normal;
}</code></pre>
    
    <h2>3. Taille de police (font-size)</h2>
    <p>La propriété <code>font-size</code> définit la taille du texte.</p>
    
    <h3>Unités absolues vs relatives :</h3>
    <ul>
        <li><strong>px</strong> (pixels) : Taille fixe, ne permet pas le redimensionnement</li>
        <li><strong>em</strong> : Relatif à la taille de la police parente (1em = taille actuelle)</li>
        <li><strong>rem</strong> : Relatif à la taille de la police racine (html)</li>
        <li><strong>%</strong> : Pourcentage de la taille parente</li>
    </ul>
    
    <pre><code>/* Taille absolue en pixels */
h1 {
    font-size: 24px;
}

/* Taille relative en em (16px = 1em par défaut) */
p {
    font-size: 1em;  /* Taille normale */
}

/* Pour l'accessibilité, utiliser des unités relatives */
body {
    font-size: 16px;  /* Base */
}

h1 {
    font-size: 2em;   /* 32px si parent est 16px */
}

h2 {
    font-size: 1.5em; /* 24px si parent est 16px */
}</code></pre>
    
    <div class="tip-box">
        <p><strong>💡 Accessibilité :</strong> Utilisez des unités relatives (em/rem) plutôt que des pixels pour permettre aux utilisateurs de redimensionner le texte dans leur navigateur.</p>
    </div>
    
    <h2>4. Graisse de police (font-weight)</h2>
    <p>La propriété <code>font-weight</code> contrôle l'épaisseur du texte (gras).</p>
    
    <h3>Valeurs possibles :</h3>
    <ul>
        <li><strong>normal</strong> : Poids normal (400)</li>
        <li><strong>bold</strong> : Gras (700)</li>
        <li><strong>bolder</strong> : Plus gras que le parent</li>
        <li><strong>lighter</strong> : Moins gras que le parent</li>
        <li><strong>100 à 900</strong> : Valeurs numériques (100 = plus fin, 900 = plus gras)</li>
    </ul>
    
    <pre><code>/* Gras simple */
strong {
    font-weight: bold;
}

/* Valeurs numériques */
.thin {
    font-weight: 100;
}

.normal-weight {
    font-weight: 400;  /* équivaut à normal */
}

.bold-weight {
    font-weight: 700;  /* équivaut à bold */
}

.extra-bold {
    font-weight: 900;
}</code></pre>
    
    <h2>5. Propriété raccourcie (font)</h2>
    <p>La propriété <code>font</code> permet de définir plusieurs propriétés en une seule ligne.</p>
    
    <h3>Syntaxe :</h3>
    <pre><code>font: [font-style] [font-weight] [font-size] [font-family];</code></pre>
    
    <h3>Exemples :</h3>
    <pre><code>/* Gras, 16px, Arial */
p {
    font: bold 16px Arial, sans-serif;
}

/* Italique, gras, 20px, Times */
.title {
    font: italic bold 20px "Times New Roman", serif;
}</code></pre>
    
    <h2>6. Exemple complet</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;style&gt;
        body {
            font-family: Arial, Helvetica, sans-serif;
            font-size: 16px;
            line-height: 1.6;
        }
        
        h1 {
            font-family: "Times New Roman", Times, serif;
            font-size: 2.5em;
            font-weight: bold;
            color: #2c3e50;
        }
        
        h2 {
            font-size: 1.8em;
            font-weight: 600;
            color: #3498db;
        }
        
        .italic-text {
            font-style: italic;
        }
        
        .bold-text {
            font-weight: bold;
        }
        
        code {
            font-family: "Courier New", Courier, monospace;
            font-size: 0.9em;
            background-color: #f4f4f4;
            padding: 2px 4px;
        }
        
        .light {
            font-weight: 300;
        }
        
        .extra-bold {
            font-weight: 800;
        }
    &lt;/style&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;h1&gt;Les Polices en CSS&lt;/h1&gt;
    
    &lt;h2&gt;Introduction&lt;/h2&gt;
    &lt;p&gt;Ceci est un paragraphe normal avec la police Arial.&lt;/p&gt;
    
    &lt;p class="italic-text"&gt;Ce texte est en italique.&lt;/p&gt;
    &lt;p class="bold-text"&gt;Ce texte est en gras.&lt;/p&gt;
    
    &lt;p&gt;Pour afficher du code : &lt;code&gt;font-family: Arial, sans-serif;&lt;/code&gt;&lt;/p&gt;
    
    &lt;p class="light"&gt;Texte léger (font-weight: 300)&lt;/p&gt;
    &lt;p class="extra-bold"&gt;Texte extra gras (font-weight: 800)&lt;/p&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h2>7. Bonnes pratiques</h2>
    
    <ul>
        <li><strong>Toujours utiliser un système de fallback</strong> avec plusieurs polices</li>
        <li><strong>Préférer les unités relatives (em/rem)</strong> pour l'accessibilité</li>
        <li><strong>Utiliser les valeurs numériques pour font-weight</strong> pour plus de précision (400 = normal, 700 = bold)</li>
        <li><strong>Mettre les noms de polices multi-mots entre guillemets</strong> (ex: "Times New Roman")</li>
        <li><strong>Terminer par une famille générique</strong> (serif, sans-serif, monospace)</li>
        <li><strong>Préférer italic plutôt que oblique</strong> pour une meilleure compatibilité</li>
    </ul>
    
    <div class="info-box">
        <p><strong>💡 Astuce :</strong> Google Fonts offre des polices gratuites et faciles à intégrer pour diversifier vos typographies.</p>
    </div>
    """.strip()
    
    cours_data = {
        "titre": "CSS Font - Propriétés des Polices",
        "slug": slug_cours,
        "description": "Apprenez à maîtriser les propriétés CSS pour les polices : font-family, font-size, font-weight, font-style. Découvrez les familles génériques (serif, sans-serif, monospace), le système de fallback, les unités de taille (px, em, rem), et les bonnes pratiques pour l'accessibilité.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 25,
        "ordre_affichage": 25,
        "chapitre_id": chapitre_id,
        "tags": ["css", "font", "typographie", "font-family", "font-size", "font-weight", "font-style", "serif", "sans-serif", "monospace", "debutant"],
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

def inserer_questions_css_font(cours_id):
    
    
    admin_id = get_admin_user()
    if not admin_id:
        return False
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    
    try:
        conn.rollback()
    except:
        pass
    
    
    try:
        cur.execute("ALTER TABLE questions_quiz DISABLE TRIGGER trigger_log_questions")
        conn.commit()
    except Exception as e:
        print(f"⚠️ Impossible de désactiver le trigger: {e}")
    
    
    try:
        cur.execute("DELETE FROM questions_quiz WHERE cours_id = %s", (cours_id,))
        conn.commit()
        print(f"✅ Anciennes questions supprimées pour le cours {cours_id}")
    except Exception as e:
        print(f"⚠️ Erreur lors de la suppression: {e}")
        conn.rollback()
    
    
    questions = [
        
        {
            "question": "Quelle est la différence entre les familles génériques serif, sans-serif et monospace ?",
            "options": '{"A": "Serif a des empattements, sans-serif n\'en a pas, monospace a largeur égale", "B": "Serif est pour les titres, sans-serif pour le texte, monospace pour le code", "C": "Serif est plus petit, sans-serif plus grand, monospace plus large", "D": "Il n\'y a pas de différence"}',
            "reponse_correcte": "A",
            "points": 15,
            "difficulte": "moyen",
            "explication": "Serif a des empattements (petites lignes décoratives), sans-serif n'en a pas, monospace donne la même largeur à tous les caractères.",
            "mode_specifique": "texte"
        },
        {
            "question": "Pourquoi est-il important d'utiliser des unités relatives (em ou rem) plutôt que des pixels pour font-size ?",
            "options": '{"A": "Pour que le site soit plus beau", "B": "Pour permettre aux utilisateurs de redimensionner le texte dans leur navigateur", "C": "Pour que le texte soit plus petit", "D": "Pour des raisons de performance"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "Les unités relatives permettent aux utilisateurs de redimensionner le texte dans leur navigateur, améliorant ainsi l'accessibilité.",
            "mode_specifique": "texte"
        },
        
        
        {
            "question": "Comment définir une police de secours (fallback) en CSS ?",
            "options": '{"A": "font-fallback: Arial;", "B": "font-family: Arial, Helvetica, sans-serif;", "C": "backup-font: Arial;", "D": "font-alternative: Arial;"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "On utilise font-family avec plusieurs polices séparées par des virgules, en terminant par une famille générique.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle propriété CSS permet de mettre le texte en italique ?",
            "options": '{"A": "font-weight", "B": "font-style", "C": "text-decoration", "D": "font-variant"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "font-style: italic; met le texte en italique.",
            "mode_specifique": "audio"
        },
        {
            "question": "A quoi correspondent les valeurs font-weight 400 et font-weight 700 ?",
            "options": '{"A": "400 = light, 700 = extra-bold", "B": "400 = normal, 700 = bold", "C": "400 = italic, 700 = bold", "D": "400 = thin, 700 = black"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "font-weight: 400 équivaut a normal, font-weight: 700 équivaut a bold.",
            "mode_specifique": "audio"
        },
        
        
        {
            "question": "Que signifie monospace en CSS ?",
            "options": '{"A": "Police avec empattements", "B": "Tous les caractères ont la meme largeur", "C": "Police sans empattements", "D": "Police cursive"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Monospace signifie que tous les caracteres ont la meme largeur, ideal pour le code.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment ecrire un nom de police avec plusieurs mots comme Times New Roman en CSS ?",
            "options": '{"A": "font-family: Times New Roman;", "B": "font-family: Times New Roman, serif;", "C": "font-family: Times-New-Roman;", "D": "font-family: Times New Roman, sans-serif;"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Les noms de polices avec plusieurs mots doivent etre en une seule chaine, suivis d'une famille generique.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle est la difference entre font-style italic et font-style oblique ?",
            "options": '{"A": "Italic est plus incline que oblique", "B": "Italic utilise une version italique de la police, oblique incline le texte", "C": "Oblique est plus supporte que italic", "D": "Il n\'y a pas de difference"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "Italic utilise une version italique speciale de la police, oblique incline mecaniquement le texte. Italic est prefere pour la compatibilite.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle propriete CSS controle la taille du texte ?",
            "options": '{"A": "text-size", "B": "font-size", "C": "size", "D": "font-scale"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "font-size definit la taille du texte en CSS.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle est la valeur par defaut de font-weight ?",
            "options": '{"A": "bold", "B": "normal", "C": "100", "D": "medium"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "La valeur par defaut de font-weight est normal (equivalent a 400).",
            "mode_specifique": "video"
        },
        {
            "question": "Que signifie serif en typographie CSS ?",
            "options": '{"A": "Police sans empattements", "B": "Police avec empattements", "C": "Police a largeur fixe", "D": "Police cursive"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Serif designe les polices avec empattements, comme Times New Roman.",
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
    except Exception as e:
        print(f"⚠️ Impossible de réactiver le trigger: {e}")
    
    cur.close()
    conn.close()
    
    print(f"\n📊 RÉSUMÉ:")
    print(f"   • Questions créées: {questions_creees}")
    print(f"   • Questions existantes: {questions_existantes}")
    
    return True

def main():
    print("\n" + "=" * 60)
    print("🎓 INSERTION DU COURS: CSS FONT - PROPRIÉTÉS DES POLICES")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    cours_id = inserer_cours_css_font()
    
    if cours_id:
        
        inserer_questions_css_font(cours_id)
        print(f"\n🎉 Succès ! Cours 'CSS Font - Propriétés des Polices' créé (ID: {cours_id})")
    else:
        print("\n❌ Échec de l'insertion")

if __name__ == "__main__":
    main()