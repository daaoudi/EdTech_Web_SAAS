
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

def inserer_cours_css_positioning():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "css-positioning"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>📍 CSS Positioning - Maîtriser le Positionnement</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Le positionnement CSS contrôle comment les éléments sont placés sur la page. Il existe cinq valeurs principales : static, relative, absolute, fixed et sticky.</p>
    </div>
    
    <h2>Introduction au Positionnement CSS</h2>
    <p>Le positionnement définit comment les éléments sont placés dans le flux du document. Par défaut, les éléments suivent le flux normal de la page.</p>
    
    <div class="tip-box">
        <p><strong>💡 À retenir :</strong> La propriété <code>position</code> est utilisée avec les propriétés <code>top</code>, <code>right</code>, <code>bottom</code>, <code>left</code> pour déplacer un élément.</p>
    </div>
    
    <h2>1. Position static (par défaut)</h2>
    <p>Tous les éléments ont <code>position: static</code> par défaut. Les éléments suivent l'ordre normal du flux HTML.</p>
    
    <pre><code>/* Position par défaut */
.element {
    position: static;
    /* top, right, bottom, left n'ont aucun effet */
}</code></pre>
    
    <h2>2. Position relative</h2>
    <p><code>position: relative</code> permet de déplacer un élément par rapport à sa position normale, sans retirer l'élément du flux.</p>
    
    <pre><code>/* Décaler un élément de 20px vers le bas et 30px vers la droite */
.relative-box {
    position: relative;
    top: 20px;
    left: 30px;
}

/* Décaler vers le haut */
.move-up {
    position: relative;
    top: -10px;
}</code></pre>
    
    <div class="info-box">
        <p><strong>📝 Note :</strong> L'espace d'origine de l'élément reste réservé dans la mise en page.</p>
    </div>
    
    <h2>3. Position absolute</h2>
    <p><code>position: absolute</code> retire l'élément du flux normal. Il est positionné par rapport à son ancêtre positionné le plus proche.</p>
    
    <pre><code>/* Position absolue par rapport au parent */
.container {
    position: relative;  /* Ancêtre de référence */
    height: 200px;
}

.absolute-box {
    position: absolute;
    top: 50px;
    left: 20px;
}

/* Positionné par rapport à la page */
.page-absolute {
    position: absolute;
    bottom: 0;
    right: 0;
}</code></pre>
    
    <div class="warning-box">
        <p><strong>⚠️ Important :</strong> Si aucun ancêtre positionné n'existe, l'élément absolu se positionne par rapport au corps de la page (&lt;body&gt;).</p>
    </div>
    
    <h2>4. Position fixed</h2>
    <p><code>position: fixed</code> fixe l'élément par rapport à la fenêtre du navigateur (viewport). Il reste à la même place lors du défilement.</p>
    
    <pre><code>/* Barre de navigation fixe en haut */
.navbar {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    background-color: 
    color: white;
}

/* Bouton flottant en bas à droite */
.floating-btn {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background-color: red;
    border-radius: 50%;
}</code></pre>
    
    <div class="tip-box">
        <p><strong>💡 Cas d'usage :</strong> Menus de navigation fixes, boutons "Retour en haut", cookies banners.</p>
    </div>
    
    <h2>5. Position sticky</h2>
    <p><code>position: sticky</code> alterne entre relative et fixed selon le défilement. L'élément reste collé à un seuil défini.</p>
    
    <pre><code>/* En-tête qui reste collé en haut */
.sticky-header {
    position: sticky;
    top: 0;
    background-color: 
    padding: 10px;
}

/* Section qui reste collée après défilement */
.section-title {
    position: sticky;
    top: 20px;
    background-color: yellow;
}</code></pre>
    
    <div class="info-box">
        <p><strong>💡 Astuce :</strong> Sticky est parfait pour les titres de sections dans une longue liste ou un tableau.</p>
    </div>
    
    <h2>6. Exemple complet</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;style&gt;
        /* Barre de navigation fixe */
        .navbar {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background-color: 
            color: white;
            padding: 15px;
            z-index: 1000;
        }
        
        /* Conteneur pour l'absolute */
        .container {
            position: relative;
            height: 200px;
            background-color: 
            margin: 20px 0;
        }
        
        /* Élément absolu */
        .absolute-box {
            position: absolute;
            bottom: 10px;
            right: 10px;
            background-color: 
            padding: 10px;
            color: white;
        }
        
        /* Élément relatif */
        .relative-box {
            position: relative;
            top: 20px;
            left: 20px;
            background-color: 
            padding: 10px;
        }
        
        /* En-tête sticky */
        .sticky-header {
            position: sticky;
            top: 60px;
            background-color: 
            color: white;
            padding: 10px;
            margin: 10px 0;
        }
        
        /* Contenu principal (pour éviter d'être caché sous la navbar) */
        .content {
            margin-top: 60px;
        }
        
        /* Bouton flottant */
        .floating-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: 
            color: white;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            text-align: center;
            line-height: 50px;
            cursor: pointer;
            z-index: 1000;
        }
    &lt;/style&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;div class="navbar"&gt;Menu de navigation fixe&lt;/div&gt;
    
    &lt;div class="content"&gt;
        &lt;h1&gt;Exemple de Positionnement CSS&lt;/h1&gt;
        
        &lt;div class="container"&gt;
            &lt;div class="absolute-box"&gt;Position absolute&lt;/div&gt;
        &lt;/div&gt;
        
        &lt;div class="relative-box"&gt;Position relative (décalée)&lt;/div&gt;
        
        &lt;div class="sticky-header"&gt;Titre sticky - reste visible&lt;/div&gt;
        &lt;p&gt;Contenu de la section 1...&lt;/p&gt;
        &lt;p&gt;Plus de contenu...&lt;/p&gt;
        
        &lt;div class="sticky-header"&gt;Titre sticky 2&lt;/div&gt;
        &lt;p&gt;Contenu de la section 2...&lt;/p&gt;
    &lt;/div&gt;
    
    &lt;div class="floating-btn"&gt;↑&lt;/div&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h2>7. Résumé des valeurs position</h2>
    
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead style="background-color: 
            <th style="padding: 8px; text-align: left;">Valeur</th>
            <th style="padding: 8px; text-align: left;">Comportement</th>
            <th style="padding: 8px; text-align: left;">Cas d'usage</th>
        </thead>
        <tbody>
            <tr><td style="padding: 8px;"><strong>static</strong></td><td style="padding: 8px;">Position normale, par défaut</td><td style="padding: 8px;">Layout standard</td></tr>
            <tr><td style="padding: 8px;"><strong>relative</strong></td><td style="padding: 8px;">Décalé par rapport à sa position normale</td><td style="padding: 8px;">Ajustements fins</td></tr>
            <tr><td style="padding: 8px;"><strong>absolute</strong></td><td style="padding: 8px;">Retiré du flux, positionné par rapport à un ancêtre</td><td style="padding: 8px;">Modales, tooltips</td></tr>
            <tr><td style="padding: 8px;"><strong>fixed</strong></td><td style="padding: 8px;">Fixé par rapport à la fenêtre</td><td style="padding: 8px;">Menus, boutons flottants</td></tr>
            <tr><td style="padding: 8px;"><strong>sticky</strong></td><td style="padding: 8px;">Collé au défilement</td><td style="padding: 8px;">En-têtes de sections</td></tr>
        </tbody>
    </table>
    
    <h2>8. Bonnes pratiques</h2>
    
    <ul>
        <li><strong>Utilisez z-index</strong> pour contrôler l'empilement des éléments positionnés</li>
        <li><strong>Les éléments positionnés</strong> créent un nouveau contexte d'empilement</li>
        <li><strong>Absolute sans ancêtre positionné</strong> se positionne par rapport à &lt;body&gt;</li>
        <li><strong>Relative sans décalage</strong> sert souvent de conteneur pour des éléments absolus</li>
        <li><strong>Fixed</strong> est idéal pour les éléments qui doivent toujours être visibles</li>
        <li><strong>Sticky</strong> nécessite un seuil (top, bottom, etc.) pour fonctionner</li>
    </ul>
    
    <div class="info-box">
        <p><strong>💡 Astuce :</strong> Combinez <code>z-index</code> avec les éléments positionnés pour gérer les superpositions.</p>
    </div>
    """.strip()
    
    cours_data = {
        "titre": "CSS Positioning - Positionnement d'Éléments",
        "slug": slug_cours,
        "description": "Apprenez à maîtriser le positionnement CSS : static, relative, absolute, fixed et sticky. Découvrez comment contrôler précisément la position des éléments sur votre page, créer des menus fixes, des tooltips, des modales et des en-têtes collants.",
        "contenu_texte": contenu_html,
        "difficulte": "intermediaire",
        "duree_estimee": 25,
        "ordre_affichage": 30,
        "chapitre_id": chapitre_id,
        "tags": ["css", "positioning", "position", "relative", "absolute", "fixed", "sticky", "z-index", "layout", "intermediaire"],
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

def inserer_questions_css_positioning(cours_id):
    
    
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
            "question": "Quelle est la valeur par défaut de la propriété CSS position ?",
            "options": '{"A": "relative", "B": "absolute", "C": "static", "D": "fixed"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "position: static est la valeur par défaut. Les éléments suivent le flux normal de la page.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quelle propriété permet de contrôler l'ordre d'empilement des éléments positionnés ?",
            "options": '{"A": "stack-order", "B": "layer-index", "C": "z-index", "D": "overlay"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "z-index contrôle l'ordre d'empilement des éléments positionnés. Plus la valeur est élevée, plus l'élément apparaît au-dessus.",
            "mode_specifique": "texte"
        },
        
        
        {
            "question": "Quelle valeur de position retire complètement un élément du flux normal de la page ?",
            "options": '{"A": "relative", "B": "absolute", "C": "fixed", "D": "static"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "position: absolute retire l'élément du flux normal. Il est positionné par rapport à son ancêtre positionné le plus proche.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle valeur de position permet de créer une barre de navigation qui reste visible pendant le défilement ?",
            "options": '{"A": "relative", "B": "absolute", "C": "fixed", "D": "sticky"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "position: fixed fixe l'élément par rapport à la fenêtre du navigateur. Il reste à sa place lors du défilement.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle valeur de position permet de décaler un élément par rapport à sa position normale sans le retirer du flux ?",
            "options": '{"A": "relative", "B": "absolute", "C": "fixed", "D": "static"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "position: relative déplace l'élément par rapport à sa position normale tout en conservant son espace d'origine.",
            "mode_specifique": "audio"
        },
        
        
        {
            "question": "Que se passe-t-il si on utilise position: absolute sans ancêtre positionné ?",
            "options": '{"A": "L\'élément est positionné par rapport au body", "B": "L\'élément reste à sa position normale", "C": "L\'élément disparaît", "D": "L\'élément devient fixed"}',
            "reponse_correcte": "A",
            "points": 15,
            "difficulte": "moyen",
            "explication": "Sans ancêtre positionné, l'élément absolu se positionne par rapport au corps de la page (&lt;body&gt;).",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle est la caractéristique principale de position: sticky ?",
            "options": '{"A": "Il retire l\'élément du flux", "B": "Il alterne entre relative et fixed selon le défilement", "C": "Il fixe l\'élément en bas de page", "D": "Il empêche le défilement"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "sticky alterne entre relative et fixed : l'élément reste collé à un seuil lors du défilement.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle propriété est nécessaire pour que position: sticky fonctionne ?",
            "options": '{"A": "z-index", "B": "display", "C": "top, bottom, left ou right", "D": "margin"}',
            "reponse_correcte": "C",
            "points": 15,
            "difficulte": "moyen",
            "explication": "sticky nécessite un seuil comme top: 0 pour déterminer à quel moment l'élément devient collant.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle valeur de position est souvent utilisée comme conteneur pour des éléments absolus ?",
            "options": '{"A": "static", "B": "relative", "C": "fixed", "D": "sticky"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "position: relative sans décalage est souvent utilisé pour créer un contexte de positionnement pour des éléments absolus.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle valeur de position permet à un élément de rester visible lors du défilement d'une section ?",
            "options": '{"A": "relative", "B": "absolute", "C": "fixed", "D": "sticky"}',
            "reponse_correcte": "D",
            "points": 15,
            "difficulte": "moyen",
            "explication": "sticky est parfait pour des en-têtes de section qui restent visibles lors du défilement jusqu'à la section suivante.",
            "mode_specifique": "video"
        },
        {
            "question": "Les propriétés top, right, bottom, left fonctionnent-elles avec position: static ?",
            "options": '{"A": "Oui, comme pour les autres positions", "B": "Non, elles n\'ont aucun effet", "C": "Oui, mais seulement sur mobile", "D": "Non, seulement sur desktop"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "top, right, bottom, left n'ont aucun effet sur un élément avec position: static.",
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
    print("🎓 INSERTION DU COURS: CSS POSITIONING (POSITIONNEMENT)")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    cours_id = inserer_cours_css_positioning()
    
    if cours_id:
        inserer_questions_css_positioning(cours_id)
        print(f"\n🎉 Succès ! Cours 'CSS Positioning - Positionnement d\'Éléments' créé (ID: {cours_id})")
    else:
        print("\n❌ Échec de l'insertion")

if __name__ == "__main__":
    main()