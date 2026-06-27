
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

def inserer_cours_javascript_loops():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "javascript-loops"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>🔄 JavaScript Loops - Les Boucles (for loop)</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Les boucles permettent de répéter des actions efficacement sans écrire de code répétitif. La boucle <code>for</code> est la plus utilisée.</p>
    </div>
    
    <h2>Pourquoi utiliser des boucles ?</h2>
    <p>Répéter du code manuellement est inefficace. Les boucles automatisent la répétition avec une syntaxe plus propre et plus lisible.</p>
    
    <div class="tip-box">
        <p><strong>💡 Cas d'usage :</strong> Parcourir des tableaux, afficher des listes, calculer des sommes, effectuer des opérations répétitives.</p>
    </div>
    
    <h2>1. Structure de la boucle for</h2>
    <p>Une boucle <code>for</code> comporte trois parties :</p>
    <ul>
        <li><strong>Initialisation</strong> : <code>let i = 0</code> (déclare un compteur)</li>
        <li><strong>Condition</strong> : <code>i < 5</code> (la boucle continue tant que c'est vrai)</li>
        <li><strong>Incément</strong> : <code>i++</code> (modifie le compteur après chaque itération)</li>
    </ul>
    
    <pre><code>// Syntaxe de base
for (initialisation; condition; incrément) {
    // code à répéter
}

// Exemple : afficher "Hello World" 5 fois
for (let i = 0; i < 5; i++) {
    console.log("Hello World");
}</code></pre>
    
    <h2>2. Déroulement d'une boucle for</h2>
    <p>La boucle s'exécute tant que la condition est vraie. i s'incrémente après chaque itération.</p>
    
    <pre><code>for (let i = 0; i < 5; i++) {
    console.log(i);  // Affiche 0, 1, 2, 3, 4
}
// Quand i = 5, la condition i < 5 est fausse → la boucle s'arrête</code></pre>
    
    <h2>3. Compter de 1 à 5</h2>
    <pre><code>for (let i = 1; i <= 5; i++) {
    console.log(i);  // Affiche 1, 2, 3, 4, 5
}</code></pre>
    
    <h2>4. Compter avec un pas différent</h2>
    <pre><code>// De 2 en 2
for (let i = 0; i <= 10; i += 2) {
    console.log(i);  // 0, 2, 4, 6, 8, 10
}

// De 5 en 5
for (let i = 0; i <= 20; i += 5) {
    console.log(i);  // 0, 5, 10, 15, 20
}</code></pre>
    
    <h2>5. Boucle avec condition interne (filter)</h2>
    <pre><code>// Afficher uniquement les nombres impairs
for (let i = 0; i <= 10; i++) {
    if (i % 2 !== 0) {
        console.log(i);  // 1, 3, 5, 7, 9
    }
}</code></pre>
    
    <h2>6. Boucle inversée (decrement)</h2>
    <pre><code>// Compter à rebours de 5 à 1
for (let i = 5; i >= 1; i--) {
    console.log(i);  // 5, 4, 3, 2, 1
}

// De 10 à 0
for (let i = 10; i >= 0; i--) {
    console.log(i);
}</code></pre>
    
    <h2>7. Boucle sur un tableau</h2>
    <pre><code>let fruits = ["pomme", "banane", "orange", "mangue"];

for (let i = 0; i < fruits.length; i++) {
    console.log(fruits[i]);
}</code></pre>
    
    <h2>8. Autres types de boucles</h2>
    
    <h3>while loop</h3>
    <pre><code>let i = 0;
while (i < 5) {
    console.log(i);
    i++;
}</code></pre>
    
    <h3>do...while loop</h3>
    <pre><code>let i = 0;
do {
    console.log(i);
    i++;
} while (i < 5);</code></pre>
    
    <h3>for...of (pour les tableaux)</h3>
    <pre><code>let fruits = ["pomme", "banane", "orange"];
for (let fruit of fruits) {
    console.log(fruit);
}</code></pre>
    
    <h2>9. Exemple complet</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;body&gt;
    &lt;h2&gt;Démonstration des Boucles JavaScript&lt;/h2&gt;
    &lt;p id="demo"&gt;&lt;/p&gt;
    
    &lt;script&gt;
        let output = "&lt;strong&gt;Boucle for (0 à 4)&lt;/strong&gt;&lt;br&gt;";
        for (let i = 0; i < 5; i++) {
            output += "Itération " + i + "&lt;br&gt;";
        }
        
        output += "&lt;br&gt;&lt;strong&gt;Nombres impairs (0 à 10)&lt;/strong&gt;&lt;br&gt;";
        for (let i = 0; i <= 10; i++) {
            if (i % 2 !== 0) {
                output += i + " ";
            }
        }
        
        output += "&lt;br&gt;&lt;br&gt;&lt;strong&gt;Boucle inversée (5 à 1)&lt;/strong&gt;&lt;br&gt;";
        for (let i = 5; i >= 1; i--) {
            output += i + " ";
        }
        
        output += "&lt;br&gt;&lt;br&gt;&lt;strong&gt;Parcours d'un tableau&lt;/strong&gt;&lt;br&gt;";
        let fruits = ["Pomme", "Banane", "Orange", "Mangue"];
        for (let i = 0; i < fruits.length; i++) {
            output += fruits[i] + "&lt;br&gt;";
        }
        
        document.getElementById("demo").innerHTML = output;
    &lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h2>Tableau récapitulatif</h2>
    
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left;">Type de boucle</th>
            <th style="padding: 8px; text-align: left;">Syntaxe</th>
            <th style="padding: 8px; text-align: left;">Quand l'utiliser</th>
        </thead>
        <tbody>
            <tr><td style="padding: 8px;"><code>for</code></td>
                <td style="padding: 8px;"><code>for (let i=0; i<n; i++)</code></td>
                <td style="padding: 8px;">Nombre d'itérations connu</td>
            </tr>
            <tr><td style="padding: 8px;"><code>while</code></td>
                <td style="padding: 8px;"><code>while (condition)</code></td>
                <td style="padding: 8px;">Condition dépendante de l'exécution</td>
            </tr>
            <tr><td style="padding: 8px;"><code>do...while</code></td>
                <td style="padding: 8px;"><code>do {...} while (condition)</code></td>
                <td style="padding: 8px;">Exécution au moins une fois</td>
            </tr>
            <tr><td style="padding: 8px;"><code>for...of</code></td>
                <td style="padding: 8px;"><code>for (let item of array)</code></td>
                <td style="padding: 8px;">Parcourir les valeurs d'un tableau</td>
            </tr>
        </tbody>
    </table>
    
    <div class="info-box">
        <p><strong>💡 À retenir :</strong> Les boucles sont essentielles pour manipuler des collections de données et répéter des actions. La boucle <code>for</code> est la plus polyvalente.</p>
    </div>
    """.strip()
    
    cours_data = {
        "titre": "JavaScript Loops - Les Boucles (for loop)",
        "slug": slug_cours,
        "description": "Apprenez à utiliser les boucles en JavaScript, en particulier la boucle for. Découvrez l'initialisation, la condition, l'incrément, comment compter de 0 à n, compter à rebours, filtrer avec des conditions internes, et parcourir des tableaux.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 20,
        "ordre_affichage": 6,
        "chapitre_id": chapitre_id,
        "tags": ["javascript", "loops", "for", "while", "do-while", "for-of", "debutant"],
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

def inserer_questions_javascript_loops(cours_id):
    
    
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
            "question": "Quelles sont les trois parties d'une boucle for en JavaScript ?",
            "options": '{"A": "début, milieu, fin", "B": "initialisation, condition, incrément", "C": "start, stop, step", "D": "init, while, update"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Une boucle for comporte : initialisation, condition, incrément.",
            "mode_specifique": "texte"
        },
        {
            "question": "Que fait i++ dans une boucle for ?",
            "options": '{"A": "Décrémente i de 1", "B": "Incrémente i de 1", "C": "Multiplie i par 2", "D": "Divise i par 2"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "i++ incrémente la variable i de 1 à chaque itération.",
            "mode_specifique": "texte"
        },
        
        
        {
            "question": "Combien de fois la boucle for (let i = 0; i < 5; i++) s'exécute-t-elle ?",
            "options": '{"A": "4 fois", "B": "5 fois", "C": "6 fois", "D": "0 fois"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "La boucle s'exécute pour i = 0,1,2,3,4 → 5 fois.",
            "mode_specifique": "audio"
        },
        {
            "question": "Comment écrire une boucle for qui affiche les nombres de 1 à 5 ?",
            "options": '{"A": "for (let i = 0; i < 5; i++)", "B": "for (let i = 1; i <= 5; i++)", "C": "for (let i = 1; i < 5; i++)", "D": "for (let i = 0; i <= 5; i++)"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "for (let i = 1; i <= 5; i++) affiche i = 1,2,3,4,5.",
            "mode_specifique": "audio"
        },
        {
            "question": "Que se passe-t-il si la condition d'une boucle for n'est jamais vraie ?",
            "options": '{"A": "La boucle s\'exécute une fois", "B": "La boucle ne s\'exécute pas", "C": "La boucle s\'exécute à l\'infini", "D": "Une erreur se produit"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Si la condition est fausse dès le départ, la boucle ne s'exécute pas.",
            "mode_specifique": "audio"
        },
        
        
        {
            "question": "Quelle boucle est idéale quand on connaît le nombre d'itérations à l'avance ?",
            "options": '{"A": "while", "B": "do...while", "C": "for", "D": "for...in"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "for est idéale quand le nombre d'itérations est connu à l'avance.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment créer une boucle for inversée de 5 à 1 ?",
            "options": '{"A": "for (let i = 5; i > 0; i++)", "B": "for (let i = 5; i >= 1; i--)", "C": "for (let i = 1; i <= 5; i++)", "D": "for (let i = 5; i < 1; i--)"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "i-- décrémente, on commence à 5 et on continue tant que i >= 1.",
            "mode_specifique": "video"
        },
        {
            "question": "Que fait l'opérateur i += 2 dans une boucle for ?",
            "options": '{"A": "Incrémente i de 2", "B": "Décrémente i de 2", "C": "Multiplie i par 2", "D": "Divise i par 2"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "i += 2 est équivalent à i = i + 2, on avance de 2 en 2.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment parcourir tous les éléments d'un tableau fruits avec une boucle for ?",
            "options": '{"A": "for (let i = 0; i < fruits.length; i++)", "B": "for (let i = 0; i <= fruits.length; i++)", "C": "for (let i = 1; i < fruits.length; i++)", "D": "for (let i = fruits.length; i > 0; i--)"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "La condition i < fruits.length permet de parcourir toutes les cases du tableau.",
            "mode_specifique": "video"
        },
        {
            "question": "Que signifie l'opérateur % (modulo) dans une condition comme i % 2 !== 0 ?",
            "options": '{"A": "Division", "B": "Reste de la division", "C": "Multiplication", "D": "Addition"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "% retourne le reste de la division. i % 2 !== 0 est vrai pour les nombres impairs.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle boucle garantit que le code s'exécute au moins une fois ?",
            "options": '{"A": "for", "B": "while", "C": "do...while", "D": "for...of"}',
            "reponse_correcte": "C",
            "points": 15,
            "difficulte": "moyen",
            "explication": "do...while exécute le bloc avant de vérifier la condition, donc au moins une fois.",
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
    print("🎓 INSERTION DU COURS: JAVASCRIPT LOOPS (Boucles)")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    cours_id = inserer_cours_javascript_loops()
    
    if cours_id:
        inserer_questions_javascript_loops(cours_id)
        print(f"\n🎉 Succès ! Cours 'JavaScript Loops - Les Boucles (for loop)' créé (ID: {cours_id})")
    else:
        print("\n❌ Échec de l'insertion")

if __name__ == "__main__":
    main()