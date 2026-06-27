
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

def inserer_cours_javascript_maps():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "javascript-maps"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>🗺️ JavaScript Maps - Les Dictionnaires</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Map est une structure de données qui stocke des paires clé-valeur. Introduit avec ES6, il permet d'utiliser n'importe quel type de données comme clé (pas seulement des chaînes).</p>
    </div>
    
    <h2>Introduction à Map</h2>
    <p>Map stocke des paires clé-valeur et préserve l'ordre d'insertion. Il est particulièrement utile lorsque vous avez besoin d'un stockage fiable avec des méthodes simples pour la manipulation.</p>
    
    <div class="tip-box">
        <p><strong>💡 Map vs Object :</strong>
        <br><strong>Object</strong> : Clés uniquement des chaînes ou Symboles, pas directement itérable, pas de propriété size.
        <br><strong>Map</strong> : Clés de tout type, directement itérable, propriété size, ordre d'insertion préservé.</p>
    </div>
    
    <h2>1. Créer une Map</h2>
    <p>On utilise le constructeur <code>new Map()</code> pour créer une Map.</p>
    
    <pre><code>// Map vide
let pays = new Map();

// Map avec des valeurs initiales
let codesPays = new Map([
    ["FR", "France"],
    ["US", "États-Unis"],
    ["UK", "Royaume-Uni"],
    ["DE", "Allemagne"]
]);

console.log(codesPays); // Map(4) { "FR" => "France", "US" => "États-Unis", ... }</code></pre>
    
    <h2>2. Ajouter des entrées (.set())</h2>
    <p>La méthode <code>.set(key, value)</code> ajoute une nouvelle paire clé-valeur à la Map.</p>
    
    <pre><code>let pays = new Map();

pays.set("FR", "France");
pays.set("US", "États-Unis");
pays.set("UK", "Royaume-Uni");
pays.set("DE", "Allemagne");

// Ajout avec une clé numérique
pays.set(1, "Numéro un");

// Ajout avec un objet comme clé
let obj = {id: 1};
pays.set(obj, "Clé objet");

console.log(pays);</code></pre>
    
    <h2>3. Récupérer des valeurs (.get())</h2>
    <p>La méthode <code>.get(key)</code> retourne la valeur associée à une clé.</p>
    
    <pre><code>let codesPays = new Map([
    ["FR", "France"],
    ["US", "États-Unis"],
    ["UK", "Royaume-Uni"]
]);

console.log(codesPays.get("FR")); // "France"
console.log(codesPays.get("DE")); // undefined (n'existe pas)</code></pre>
    
    <h2>4. Vérifier l'existence d'une clé (.has())</h2>
    <p>La méthode <code>.has(key)</code> vérifie si une clé existe dans la Map.</p>
    
    <pre><code>let codesPays = new Map([
    ["FR", "France"],
    ["US", "États-Unis"],
    ["UK", "Royaume-Uni"]
]);

console.log(codesPays.has("FR")); // true
console.log(codesPays.has("DE")); // false</code></pre>
    
    <h2>5. Supprimer des entrées (.delete() et .clear())</h2>
    
    <pre><code>let codesPays = new Map([
    ["FR", "France"],
    ["US", "États-Unis"],
    ["UK", "Royaume-Uni"]
]);

// Supprimer une entrée spécifique
codesPays.delete("UK");
console.log(codesPays.has("UK")); // false

// Vider complètement la Map
codesPays.clear();
console.log(codesPays.size); // 0</code></pre>
    
    <h2>6. Taille d'une Map (.size)</h2>
    <p>La propriété <code>.size</code> donne le nombre d'entrées dans la Map.</p>
    
    <pre><code>let codesPays = new Map([
    ["FR", "France"],
    ["US", "États-Unis"],
    ["UK", "Royaume-Uni"]
]);

console.log(codesPays.size); // 3</code></pre>
    
    <h2>7. Parcourir une Map</h2>
    
    <h3>forEach()</h3>
    <pre><code>let codesPays = new Map([
    ["FR", "France"],
    ["US", "États-Unis"],
    ["UK", "Royaume-Uni"]
]);

codesPays.forEach((value, key) => {
    console.log(key + " => " + value);
});</code></pre>
    
    <h3>for...of</h3>
    <pre><code>for (let [key, value] of codesPays) {
    console.log(key + " => " + value);
}</code></pre>
    
    <h3>Itérer uniquement sur les clés ou les valeurs</h3>
    <pre><code>// Uniquement les clés
for (let key of codesPays.keys()) {
    console.log(key);
}

// Uniquement les valeurs
for (let value of codesPays.values()) {
    console.log(value);
}</code></pre>
    
    <h2>8. Map vs Object - Tableau comparatif</h2>
    
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left;">Caractéristique</th>
            <th style="padding: 8px; text-align: left;">Map</th>
            <th style="padding: 8px; text-align: left;">Object</th>
        </thead>
        <tbody>
            <tr><td style="padding: 8px;">Types de clés</td>
                <td style="padding: 8px;">N'importe quel type (string, number, object, etc.)</td>
                <td style="padding: 8px;">Uniquement string ou Symbol</td>
            </tr>
            <tr><td style="padding: 8px;">Itération</td>
                <td style="padding: 8px;">Directement itérable</td>
                <td style="padding: 8px;">Non directement itérable</td>
            </tr>
            <tr><td style="padding: 8px;">Taille</td>
                <td style="padding: 8px;">Propriété .size</td>
                <td style="padding: 8px;">Pas de propriété directe</td>
            </tr>
            <tr><td style="padding: 8px;">Ordre</td>
                <td style="padding: 8px;">Ordre d'insertion préservé</td>
                <td style="padding: 8px;">Ordre non garanti</td>
            </tr>
            <tr><td style="padding: 8px;">Clés par défaut</td>
                <td style="padding: 8px;">Pas de clés par défaut</td>
                <td style="padding: 8px;">A des clés par défaut (prototype)</td>
            </tr>
        </tbody>
    </table>
    
    <h2>9. Exemple complet</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;body&gt;
    &lt;h2&gt;Démonstration des Maps JavaScript&lt;/h2&gt;
    &lt;p id="demo"&gt;&lt;/p&gt;
    
    &lt;script&gt;
        // Création d'une Map de pays
        let pays = new Map();
        
        pays.set("FR", "France");
        pays.set("US", "États-Unis");
        pays.set("UK", "Royaume-Uni");
        pays.set("DE", "Allemagne");
        pays.set("ES", "Espagne");
        
        let output = "&lt;strong&gt;Map des pays :&lt;/strong&gt;&lt;br&gt;";
        output += "Taille : " + pays.size + "&lt;br&gt;";
        output += "Contient FR ? " + pays.has("FR") + "&lt;br&gt;";
        output += "Valeur pour UK : " + pays.get("UK") + "&lt;br&gt;&lt;br&gt;";
        
        output += "&lt;strong&gt;Toutes les entrées :&lt;/strong&gt;&lt;br&gt;";
        
        // Parcours avec for...of
        for (let [code, nom] of pays) {
            output += code + " => " + nom + "&lt;br&gt;";
        }
        
        // Exemple avec des clés numériques
        let scores = new Map();
        scores.set(1, "Faible");
        scores.set(5, "Moyen");
        scores.set(10, "Excellent");
        
        output += "&lt;br&gt;&lt;strong&gt;Scores avec clés numériques :&lt;/strong&gt;&lt;br&gt;";
        scores.forEach((valeur, cle) => {
            output += "Score " + cle + " : " + valeur + "&lt;br&gt;";
        });
        
        document.getElementById("demo").innerHTML = output;
    &lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <div class="info-box">
        <p><strong>💡 À retenir :</strong> Map est flexible et puissant pour le stockage clé-valeur. Utilisez Map quand vous avez besoin de clés de types variés ou d'une itération directe.</p>
    </div>
    """.strip()
    
    cours_data = {
        "titre": "JavaScript Maps - Les Dictionnaires",
        "slug": slug_cours,
        "description": "Apprenez à utiliser les Maps en JavaScript : création, ajout d'entrées avec set(), récupération de valeurs avec get(), vérification avec has(), suppression avec delete() et clear(), propriété size, parcours avec forEach() et for...of. Différence entre Map et Object.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 20,
        "ordre_affichage": 13,
        "chapitre_id": chapitre_id,
        "tags": ["javascript", "map", "dictionary", "key-value", "set", "get", "has", "size", "debutant"],
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

def inserer_questions_javascript_maps(cours_id):
    
    
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
            "question": "Qu'est-ce qu'une Map en JavaScript ?",
            "options": '{"A": "Un tableau", "B": "Une structure de données clé-valeur", "C": "Une fonction", "D": "Une variable"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Map est une structure de données qui stocke des paires clé-valeur.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quelle méthode ajoute une paire clé-valeur à une Map ?",
            "options": '{"A": ".add()", "B": ".push()", "C": ".set()", "D": ".insert()"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "La méthode .set(key, value) ajoute une paire clé-valeur à la Map.",
            "mode_specifique": "texte"
        },
        
        
        {
            "question": "Comment récupérer la valeur associée à une clé dans une Map ?",
            "options": '{"A": ".fetch()", "B": ".get()", "C": ".retrieve()", "D": ".value()"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "La méthode .get(key) retourne la valeur associée à la clé.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle propriété donne le nombre d'entrées dans une Map ?",
            "options": '{"A": "length", "B": "count", "C": "size", "D": "entries"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "La propriété size retourne le nombre d'entrées dans la Map.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle méthode vérifie si une clé existe dans une Map ?",
            "options": '{"A": ".contains()", "B": ".has()", "C": ".exists()", "D": ".includes()"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "La méthode .has(key) vérifie si une clé existe dans la Map.",
            "mode_specifique": "audio"
        },
        
        
        {
            "question": "Quel type de clés peut-on utiliser dans une Map ?",
            "options": '{"A": "Uniquement des chaînes", "B": "Uniquement des nombres", "C": "N\'importe quel type", "D": "Uniquement des objets"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "Map permet d'utiliser n'importe quel type de données comme clé : string, number, object, etc.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle est la différence entre Map et Object ?",
            "options": '{"A": "Map a une propriété size, Object non", "B": "Map est itérable, Object non", "C": "Map permet des clés de tout type", "D": "Toutes ces réponses"}',
            "reponse_correcte": "D",
            "points": 15,
            "difficulte": "moyen",
            "explication": "Map a une propriété size, est directement itérable, et permet des clés de tout type.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment supprimer une entrée spécifique d'une Map ?",
            "options": '{"A": ".remove()", "B": ".delete()", "C": ".clear()", "D": ".pop()"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "La méthode .delete(key) supprime une entrée spécifique de la Map.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment vider complètement une Map ?",
            "options": '{"A": ".removeAll()", "B": ".deleteAll()", "C": ".clear()", "D": ".empty()"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "La méthode .clear() supprime toutes les entrées de la Map.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle boucle peut-on utiliser pour parcourir une Map ?",
            "options": '{"A": "for...in", "B": "for...of", "C": "forEach", "D": "Les réponses B et C"}',
            "reponse_correcte": "D",
            "points": 10,
            "difficulte": "facile",
            "explication": "On peut parcourir une Map avec for...of ou la méthode .forEach().",
            "mode_specifique": "video"
        },
        {
            "question": "Que retourne .get() si la clé n'existe pas ?",
            "options": '{"A": "null", "B": "undefined", "C": "0", "D": "false"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": ".get() retourne undefined si la clé n'existe pas dans la Map.",
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
    print("🎓 INSERTION DU COURS: JAVASCRIPT MAPS")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    cours_id = inserer_cours_javascript_maps()
    
    if cours_id:
        inserer_questions_javascript_maps(cours_id)
        print(f"\n🎉 Succès ! Cours 'JavaScript Maps - Les Dictionnaires' créé (ID: {cours_id})")
    else:
        print("\n❌ Échec de l'insertion")

if __name__ == "__main__":
    main()