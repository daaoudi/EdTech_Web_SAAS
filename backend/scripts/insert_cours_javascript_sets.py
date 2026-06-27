
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
        cur.execute("SELECT id FROM chapitres WHERE id = 3 OR titre ILIKE %s", ('%JavaScript%',))
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result:
            chapitre_id = result[0]
            print(f"📚 Chapitre JavaScript trouvé (ID: {chapitre_id})")
            return chapitre_id
        return None
    except Exception as e:
        print(f"⚠️ Erreur récupération chapitre: {e}")
        return None

def inserer_cours_javascript_sets():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "javascript-sets"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>🔢 Set in JavaScript - Les Ensembles</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Set est une structure de données qui stocke des valeurs uniques. Contrairement aux tableaux, les Sets ne permettent pas les doublons et ne sont pas basés sur des indices.</p>
    </div>
    
    <h2>Pourquoi utiliser Set ?</h2>
    <p>Les tableaux autorisent les doublons, mais Set impose l'unicité. Cela le rend très utile pour filtrer les valeurs répétées.</p>
    
    <div class="tip-box">
        <p><strong>💡 Différence entre Set et Array :</strong>
        <br><strong>Array (Tableau)</strong> : Permet des doublons, basé sur des indices (0,1,2...), maintient l'ordre d'insertion.
        <br><strong>Set</strong> : Pas de doublons, pas d'indices, itération par valeurs, maintient l'ordre d'insertion.</p>
    </div>
    
    <h2>1. Créer un Set</h2>
    <p>On utilise le constructeur <code>new Set()</code> pour créer un Set.</p>
    
    <pre><code>// Set vide
let monSet = new Set();

// Set avec des valeurs initiales
let lettres = new Set(["b", "o", "o", "k", "k", "e", "e", "p", "e", "r"]);
console.log(lettres); // Set(6) { "b", "o", "k", "e", "p", "r" }

// Exemple: "bookkeeper" devient un Set de lettres uniques
let mot = "bookkeeper";
let lettresUniques = new Set(mot);
console.log(lettresUniques); // Set(6) { "b", "o", "k", "e", "p", "r" }</code></pre>
    
    <h2>2. Suppression automatique des doublons</h2>
    <p>"bookkeeper" a 10 caractères, mais Set ne stocke que 6 lettres uniques. Les doublons sont automatiquement ignorés.</p>
    
    <pre><code>let nombres = new Set([1, 2, 2, 3, 3, 3, 4]);
console.log(nombres); // Set(4) { 1, 2, 3, 4 }</code></pre>
    
    <h2>3. Ajouter des valeurs (.add())</h2>
    <p>La méthode <code>.add()</code> insère de nouvelles valeurs dans le Set. Les doublons sont ignorés.</p>
    
    <pre><code>let fruits = new Set();
fruits.add("pomme");
fruits.add("banane");
fruits.add("pomme"); // Ignoré car déjà présent
fruits.add("orange");

console.log(fruits); // Set(3) { "pomme", "banane", "orange" }

// Fonctionne avec différents types de données
let mixte = new Set();
mixte.add(42);
mixte.add("texte");
mixte.add(true);
mixte.add(42); // Ignoré</code></pre>
    
    <h2>4. Parcourir un Set (.forEach())</h2>
    <p>La méthode <code>.forEach()</code> permet d'itérer sur les valeurs d'un Set. Il n'y a pas d'indices, l'itération se concentre uniquement sur les valeurs.</p>
    
    <pre><code>let couleurs = new Set(["rouge", "vert", "bleu"]);

couleurs.forEach(function(valeur) {
    console.log(valeur);
});

// Avec une fonction fléchée
couleurs.forEach(valeur => console.log(valeur));</code></pre>
    
    <h2>5. Vérifier l'existence d'une valeur (.has())</h2>
    <p>La méthode <code>.has()</code> vérifie si une valeur existe dans le Set. Retourne true ou false. Attention : la vérification est sensible à la casse.</p>
    
    <pre><code>let fruits = new Set(["pomme", "banane", "orange"]);

console.log(fruits.has("pomme"));  // true
console.log(fruits.has("POMME"));  // false (sensible à la casse)
console.log(fruits.has("raisin")); // false</code></pre>
    
    <h2>6. Autres méthodes utiles</h2>
    
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left;">Méthode</th>
            <th style="padding: 8px; text-align: left;">Description</th>
            <th style="padding: 8px; text-align: left;">Exemple</th>
        </thead>
        <tbody>
            <tr><td style="padding: 8px;"><code>.delete()</code></td><td style="padding: 8px;">Supprime une valeur</td><td style="padding: 8px;"><code>fruits.delete("banane")</code></td></tr>
            <tr><td style="padding: 8px;"><code>.clear()</code></td><td style="padding: 8px;">Supprime toutes les valeurs</td><td style="padding: 8px;"><code>fruits.clear()</code></td></tr>
            <tr><td style="padding: 8px;"><code>.size</code></td><td style="padding: 8px;">Propriété: nombre d'éléments</td><td style="padding: 8px;"><code>console.log(fruits.size)</code></td></tr>
            <tr><td style="padding: 8px;"><code>for...of</code></td><td style="padding: 8px;">Boucle pour parcourir</td><td style="padding: 8px;"><code>for (let fruit of fruits) { }</code></td></tr>
        </tbody>
    </table>
    
    <h2>7. Exemple complet</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;body&gt;
    &lt;h2&gt;Démonstration des Sets JavaScript&lt;/h2&gt;
    &lt;p id="demo"&gt;&lt;/p&gt;
    
    &lt;script&gt;
        // Création d'un Set à partir d'un tableau avec doublons
        let nombres = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5];
        let setNombres = new Set(nombres);
        
        // Ajout de valeurs
        setNombres.add(6);
        setNombres.add(3); // Ignoré
        
        // Suppression
        setNombres.delete(1);
        
        let output = "&lt;strong&gt;Set de nombres :&lt;/strong&gt;&lt;br&gt;";
        output += "Taille : " + setNombres.size + "&lt;br&gt;";
        output += "Contient 3 ? " + setNombres.has(3) + "&lt;br&gt;";
        output += "Valeurs : ";
        
        setNombres.forEach(valeur => {
            output += valeur + " ";
        });
        
        // Exemple avec bookkeeper
        let mot = "bookkeeper";
        let lettresUniques = new Set(mot);
        
        output += "&lt;br&gt;&lt;br&gt;&lt;strong&gt;Mot original :&lt;/strong&gt; " + mot + "&lt;br&gt;";
        output += "&lt;strong&gt;Lettres uniques :&lt;/strong&gt; ";
        lettresUniques.forEach(lettre => {
            output += lettre + " ";
        });
        output += "(" + lettresUniques.size + " lettres)";
        
        document.getElementById("demo").innerHTML = output;
    &lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <div class="info-box">
        <p><strong>💡 À retenir :</strong> Sets = valeurs uniques, pas d'indices. Parfaits pour supprimer des doublons et gérer des collections où l'unicité est importante.</p>
    </div>
    """.strip()
    
    cours_data = {
        "titre": "JavaScript Sets - Les Ensembles",
        "slug": slug_cours,
        "description": "Apprenez à utiliser les Sets en JavaScript : création, ajout de valeurs avec add(), suppression des doublons, parcours avec forEach(), vérification avec has(), propriété size. Différence entre Set et Array.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 20,
        "ordre_affichage": 12,
        "chapitre_id": chapitre_id,
        "tags": ["javascript", "set", "ensemble", "unique", "add", "has", "forEach", "size", "debutant"],
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

def inserer_questions_javascript_sets(cours_id):
    
    
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
            "question": "Quelle est la principale caractéristique d'un Set en JavaScript ?",
            "options": '{"A": "Stocke des valeurs ordonnées", "B": "Stocke uniquement des valeurs uniques", "C": "Stocke des paires clé-valeur", "D": "Stocke des valeurs triées"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Un Set stocke uniquement des valeurs uniques. Les doublons sont automatiquement ignorés.",
            "mode_specifique": "texte"
        },
        {
            "question": "Comment crée-t-on un Set en JavaScript ?",
            "options": '{"A": "let set = []", "B": "let set = {}", "C": "let set = new Set()", "D": "let set = new Array()"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "On utilise le constructeur new Set() pour créer un Set.",
            "mode_specifique": "texte"
        },
        
        
        {
            "question": "Quelle méthode ajoute une valeur à un Set ?",
            "options": '{"A": ".push()", "B": ".append()", "C": ".add()", "D": ".insert()"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "La méthode .add() insère une nouvelle valeur dans le Set.",
            "mode_specifique": "audio"
        },
        {
            "question": "Comment vérifier si une valeur existe dans un Set ?",
            "options": '{"A": ".contains()", "B": ".has()", "C": ".includes()", "D": ".exist()"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "La méthode .has() vérifie si une valeur existe dans le Set et retourne true ou false.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle propriété donne le nombre d'éléments dans un Set ?",
            "options": '{"A": "length", "B": "count", "C": "size", "D": "items"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "La propriété size retourne le nombre d'éléments dans le Set.",
            "mode_specifique": "audio"
        },
        
        
        {
            "question": "Que se passe-t-il si on ajoute un doublon à un Set ?",
            "options": '{"A": "Une erreur se produit", "B": "La valeur est dupliquée", "C": "Le doublon est ignoré", "D": "Le Set est vidé"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "Les doublons sont automatiquement ignorés lors de l'ajout à un Set.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle est la différence entre un Set et un Array ?",
            "options": '{"A": "Array permet les doublons, Set non", "B": "Set est basé sur des indices, Array non", "C": "Array stocke des valeurs uniques", "D": "Il n\'y a pas de différence"}',
            "reponse_correcte": "A",
            "points": 15,
            "difficulte": "moyen",
            "explication": "Les tableaux (Array) permettent les doublons, tandis que les Sets stockent uniquement des valeurs uniques.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment supprimer toutes les valeurs d'un Set ?",
            "options": '{"A": ".removeAll()", "B": ".deleteAll()", "C": ".clear()", "D": ".reset()"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "La méthode .clear() supprime toutes les valeurs d'un Set.",
            "mode_specifique": "video"
        },
        {
            "question": "Que donne new Set([1, 2, 2, 3, 3, 3]) ?",
            "options": '{"A": "Set(3) {1, 2, 3}", "B": "Set(6) {1, 2, 2, 3, 3, 3}", "C": "Erreur", "D": "[1, 2, 3]"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "Set supprime automatiquement les doublons, donc ne conserve que 1, 2, 3.",
            "mode_specifique": "video"
        },
        {
            "question": "La méthode .has() est-elle sensible à la casse ?",
            "options": '{"A": "Oui", "B": "Non", "C": "Dépend du navigateur", "D": "Uniquement sur mobile"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": ".has() est sensible à la casse. 'Pomme' et 'pomme' sont considérés comme différents.",
            "mode_specifique": "video"
        },
        {
            "question": "Quel mot-clé utilise-t-on pour parcourir un Set avec une boucle ?",
            "options": '{"A": "for...in", "B": "for...of", "C": "forEach", "D": "Les réponses B et C"}',
            "reponse_correcte": "D",
            "points": 10,
            "difficulte": "facile",
            "explication": "On peut parcourir un Set avec for...of ou la méthode .forEach().",
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
    print("🎓 INSERTION DU COURS: JAVASCRIPT SETS")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    cours_id = inserer_cours_javascript_sets()
    
    if cours_id:
        inserer_questions_javascript_sets(cours_id)
        print(f"\n🎉 Succès ! Cours 'JavaScript Sets - Les Ensembles' créé (ID: {cours_id})")
    else:
        print("\n❌ Échec de l'insertion")

if __name__ == "__main__":
    main()