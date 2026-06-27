
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

def inserer_cours_tableaux():
    
    
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
    
    
    slug_cours = "tableaux-html"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    
    contenu_html = """
    <h1>📊 Les Tableaux en HTML</h1>
    
    <h2>Introduction</h2>
    <p>Les tableaux HTML sont utilisés pour organiser et afficher des données structurées sur les pages web. Ils permettent de présenter des informations sous forme de lignes et colonnes, comme des feuilles de calcul.</p>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Les tableaux sont parfaits pour afficher des données comparatives, des horaires, des résultats, ou tout type d'information organisée en grille.</p>
    </div>
    
    <h2>1. Structure de base d'un tableau</h2>
    <p>Un tableau HTML est construit avec trois balises principales :</p>
    <ul>
        <li><strong>&lt;table&gt;</strong> : Conteneur principal du tableau</li>
        <li><strong>&lt;tr&gt;</strong> : Table Row - Définit une ligne</li>
        <li><strong>&lt;td&gt;</strong> : Table Data - Définit une cellule</li>
    </ul>
    
    <h3>Exemple basique :</h3>
    <pre><code>&lt;table border="1"&gt;
    &lt;tr&gt;
        &lt;td&gt;Ligne 1, Cellule 1&lt;/td&gt;
        &lt;td&gt;Ligne 1, Cellule 2&lt;/td&gt;
    &lt;/tr&gt;
    &lt;tr&gt;
        &lt;td&gt;Ligne 2, Cellule 1&lt;/td&gt;
        &lt;td&gt;Ligne 2, Cellule 2&lt;/td&gt;
    &lt;/tr&gt;
&lt;/table&gt;</code></pre>
    
    <h2>2. Les en-têtes de tableau (&lt;th&gt;)</h2>
    <p>La balise &lt;th&gt; (Table Header) est utilisée pour les cellules d'en-tête. Le texte y apparaît généralement en gras et centré par défaut.</p>
    
    <pre><code>&lt;table border="1"&gt;
    &lt;tr&gt;
        &lt;th&gt;Nom&lt;/th&gt;
        &lt;th&gt;Âge&lt;/th&gt;
        &lt;th&gt;Ville&lt;/th&gt;
    &lt;/tr&gt;
    &lt;tr&gt;
        &lt;td&gt;Jean&lt;/td&gt;
        &lt;td&gt;25&lt;/td&gt;
        &lt;td&gt;Paris&lt;/td&gt;
    &lt;/tr&gt;
    &lt;tr&gt;
        &lt;td&gt;Marie&lt;/td&gt;
        &lt;td&gt;30&lt;/td&gt;
        &lt;td&gt;Lyon&lt;/td&gt;
    &lt;/tr&gt;
&lt;/table&gt;</code></pre>
    
    <h2>3. Fusion de cellules</h2>
    <p>Deux attributs permettent de fusionner des cellules :</p>
    <ul>
        <li><strong>colspan</strong> : Fusionne des colonnes (horizontal)</li>
        <li><strong>rowspan</strong> : Fusionne des lignes (vertical)</li>
    </ul>
    
    <h3>Exemple avec colspan :</h3>
    <pre><code>&lt;table border="1"&gt;
    &lt;tr&gt;
        &lt;th colspan="2"&gt;Nom complet&lt;/th&gt;
        &lt;th&gt;Âge&lt;/th&gt;
    &lt;/tr&gt;
    &lt;tr&gt;
        &lt;td&gt;Jean&lt;/td&gt;
        &lt;td&gt;Dupont&lt;/td&gt;
        &lt;td&gt;25&lt;/td&gt;
    &lt;/tr&gt;
&lt;/table&gt;</code></pre>
    
    <h2>4. Styles CSS pour les tableaux</h2>
    <p>Pour rendre les tableaux plus esthétiques, on utilise CSS :</p>
    
    <pre><code>table {
    border-collapse: collapse;
    width: 100%;
}

th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}

th {
    background-color: #f2f2f2;
}

tr:nth-child(even) {
    background-color: #f9f9f9;
}

tr:hover {
    background-color: #f5f5f5;
}</code></pre>
    
    <div class="tip-box">
        <p><strong>💡 Astuce :</strong> Utilisez <code>border-collapse: collapse</code> pour éviter les doubles bordures entre les cellules.</p>
    </div>
    
    <h2>5. Tableaux responsive</h2>
    <p>Pour rendre un tableau responsive sur mobile, on peut utiliser un conteneur avec overflow-x: auto :</p>
    
    <pre><code>&lt;div style="overflow-x: auto;"&gt;
    &lt;table&gt;
        &lt;!-- contenu du tableau --&gt;
    &lt;/table&gt;
&lt;/div&gt;</code></pre>
    
    <h2>6. Exercice pratique</h2>
    <p>Créez un tableau HTML avec les caractéristiques suivantes :</p>
    <ol>
        <li>Un en-tête avec les colonnes : "Produit", "Prix", "Quantité", "Total"</li>
        <li>Au moins 3 lignes de données</li>
        <li>Une ligne de total avec colspan pour "Total général"</li>
        <li>Bordure et style CSS pour le rendre agréable à lire</li>
        <li>Survol des lignes avec changement de couleur</li>
    </ol>
    """.strip()
    
    
    cours_data = {
        "titre": "Tableaux HTML - Organisation de Données",
        "slug": slug_cours,
        "description": "Apprenez à créer et styliser des tableaux en HTML pour organiser et présenter des données structurées. Découvrez les balises table, tr, td, th, ainsi que la fusion de cellules avec colspan et rowspan.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 25,
        "ordre_affichage": 13,
        "chapitre_id": chapitre_id,  
        "tags": ["html", "tableaux", "table", "tr", "td", "th", "colspan", "rowspan", "debutant", "donnees"],
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

def inserer_questions_tableaux(cours_id):
    
    
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
            "question": "Quelle balise HTML est utilisée pour créer une ligne dans un tableau ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "｜｜DSML｜｜",
                "B": "<tr>",
                "C": "<th>",
                "D": "<caption>"
            },
            "reponse_correcte": "B",
            "explication": "La balise <tr> (Table Row) définit une ligne dans un tableau HTML.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quelle balise HTML est utilisée pour une cellule d'en-tête dans un tableau ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "<td>",
                "B": "<th>",
                "C": "</table>",
                "D": "<caption>"
            },
            "reponse_correcte": "B",
            "explication": "La balise <th> (Table Header) est utilisée pour les cellules d'en-tête. Le texte y apparaît en gras et centré.",
            "mode_specifique": "video"
        },
        {
            "question": "Quel attribut permet de fusionner des colonnes horizontalement ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "rowspan",
                "B": "colspan",
                "C": "merge",
                "D": "span"
            },
            "reponse_correcte": "B",
            "explication": "L'attribut colspan spécifie le nombre de colonnes qu'une cellule doit couvrir horizontalement.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quel attribut permet de fusionner des cellules verticalement ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "colspan",
                "B": "rowspan",
                "C": "vspan",
                "D": "merge-vert"
            },
            "reponse_correcte": "B",
            "explication": "L'attribut rowspan spécifie le nombre de lignes qu'une cellule doit couvrir verticalement.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quelle propriété CSS permet d'éviter les doubles bordures entre les cellules d'un tableau ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "border-collapse: collapse",
                "B": "border: none",
                "C": "cell-spacing: 0",
                "D": "border-collapse: separate"
            },
            "reponse_correcte": "A",
            "explication": "border-collapse: collapse fusionne les bordures adjacentes en une seule bordure.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle balise contient toutes les lignes et cellules d'un tableau HTML ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "<thead>",
                "B": "<tbody>",
                "C": "</td>",
                "D": "<tfoot>"
            },
            "reponse_correcte": "C",
            "explication": "La balise <table> est le conteneur principal qui englobe toutes les lignes et cellules du tableau.",
            "mode_specifique": "audio"
        },
        {
            "question": "Comment rendre un tableau responsive sur mobile ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "difficile",
            "options": {
                "A": "overflow-x: auto sur un conteneur",
                "B": "width: 100% sur le tableau",
                "C": "display: block sur le tableau",
                "D": "Toutes ces réponses"
            },
            "reponse_correcte": "D",
            "explication": "Pour un tableau responsive, on peut utiliser overflow-x: auto sur un conteneur, width: 100%, et parfois display: block.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle balise HTML est utilisée pour ajouter une légende à un tableau ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "moyen",
            "options": {
                "A": "<legend>",
                "B": "<caption>",
                "C": "<title>",
                "D": "<label>"
            },
            "reponse_correcte": "B",
            "explication": "La balise <caption> définit une légende pour un tableau. Elle doit être placée immédiatement après la balise </table>.",
            "mode_specifique": "texte"
        },
        {
            "question": "Comment sélectionner les lignes paires d'un tableau avec CSS ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "difficile",
            "options": {
                "A": "table tr:even",
                "B": "table tr:nth-child(even)",
                "C": "table tr:nth-child(2n)",
                "D": "Les deux réponses B et C"
            },
            "reponse_correcte": "D",
            "explication": ":nth-child(even) et :nth-child(2n) permettent tous deux de sélectionner les éléments enfants pairs.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle balise est utilisée pour regrouper le corps d'un tableau ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "moyen",
            "options": {
                "A": "<thead>",
                "B": "<tbody>",
                "C": "<tfoot>",
                "D": "<tgroup>"
            },
            "reponse_correcte": "B",
            "explication": "La balise <tbody> regroupe le corps principal du tableau, contenant les données.",
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
    print("🎓 INSERTION DU COURS: TABLEAUX HTML")
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
    
    
    cours_id = inserer_cours_tableaux()
    
    if cours_id:
        
        inserer_questions_tableaux(cours_id)
        
        print(f"\n🎉 Succès ! Le cours 'Tableaux HTML' a été inséré avec succès!")
        print(f"   📚 Cours ID: {cours_id}")
        
        
        lister_cours_et_chapitres()
    else:
        print("\n❌ Échec de l'insertion du cours")

if __name__ == "__main__":
    main()