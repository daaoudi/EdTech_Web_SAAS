
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

def inserer_cours_javascript_events():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "javascript-events"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>🎯 JavaScript Events - Event Handlers vs Event Listeners</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Les événements permettent de réagir aux actions de l'utilisateur comme les clics de bouton ou les survols de souris. Il existe deux façons de les gérer : les gestionnaires d'événements (event handlers) et les écouteurs d'événements (event listeners).</p>
    </div>
    
    <h2>Introduction aux Événements</h2>
    <p>Les événements incluent des actions comme les clics de bouton ou les survols de souris. Deux méthodes principales permettent de les gérer : les gestionnaires d'événements (event handlers) et les écouteurs d'événements (event listeners).</p>
    
    <div class="tip-box">
        <p><strong>💡 Recommandation :</strong> Les écouteurs d'événements (addEventListener) sont préférés pour les applications modernes car ils permettent d'attacher plusieurs fonctions au même événement.</p>
    </div>
    
    <h2>1. Les gestionnaires d'événements (Event Handlers)</h2>
    <p>Les gestionnaires d'événements sont des propriétés comme <code>onclick</code>, <code>onmouseover</code>, etc. Ils ne permettent qu'une seule fonction par type d'événement. Les nouvelles assignations remplacent les précédentes.</p>
    
    <pre><code>// Récupérer le bouton
let button = document.getElementById("myButton");

// Premier gestionnaire
button.onclick = function() {
    console.log("Premier clic !");
};

// Deuxième gestionnaire - remplace le premier
button.onclick = function() {
    console.log("Deuxième clic !");
};

// Seul "Deuxième clic !" sera affiché</code></pre>
    
    <div class="warning-box">
        <p><strong>⚠️ Limitation :</strong> Un seul gestionnaire par type d'événement. Le dernier assigné écrase les précédents.</p>
    </div>
    
    <h2>2. Les écouteurs d'événements (Event Listeners)</h2>
    <p>Les écouteurs d'événements utilisent la méthode <code>addEventListener()</code>. Ils peuvent attacher plusieurs fonctions au même événement, ce qui les rend plus flexibles.</p>
    
    <pre><code>let button = document.getElementById("myButton");

// Premier écouteur
button.addEventListener("click", function() {
    console.log("Premier clic !");
});

// Deuxième écouteur - s'ajoute sans remplacer le premier
button.addEventListener("click", function() {
    console.log("Deuxième clic !");
});

// Les deux messages s'afficheront</code></pre>
    
    <h2>3. Différence clé démontrée</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;style&gt;
        button {
            padding: 10px 20px;
            font-size: 16px;
            margin: 10px;
            cursor: pointer;
        }
        .output {
            margin-top: 20px;
            padding: 10px;
            border: 1px solid #ccc;
            background-color: #f9f9f9;
        }
    &lt;/style&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;h2&gt;Démonstration: Handlers vs Listeners&lt;/h2&gt;
    
    &lt;button id="handlerBtn"&gt;Handler (onclick)&lt;/button&gt;
    &lt;button id="listenerBtn"&gt;Listener (addEventListener)&lt;/button&gt;
    
    &lt;div class="output" id="output"&gt;&lt;/div&gt;
    
    &lt;script&gt;
        let output = document.getElementById("output");
        
        // Handler - seul le dernier s'exécute
        let handlerBtn = document.getElementById("handlerBtn");
        handlerBtn.onclick = function() {
            output.innerHTML += "Handler 1: Premier clic&lt;br&gt;";
        };
        handlerBtn.onclick = function() {
            output.innerHTML += "Handler 2: Deuxième clic (écrase le premier)&lt;br&gt;";
        };
        
        // Listener - les deux s'exécutent
        let listenerBtn = document.getElementById("listenerBtn");
        listenerBtn.addEventListener("click", function() {
            output.innerHTML += "Listener 1: Premier écouteur&lt;br&gt;";
        });
        listenerBtn.addEventListener("click", function() {
            output.innerHTML += "Listener 2: Deuxième écouteur (s'ajoute)&lt;br&gt;";
        });
    &lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h2>4. Supprimer un écouteur d'événement</h2>
    <p>La méthode <code>removeEventListener()</code> permet de supprimer un écouteur spécifique. Nécessite de passer la même fonction que celle ajoutée.</p>
    
    <pre><code>function maFonction() {
    console.log("Événement déclenché");
}

// Ajouter l'écouteur
button.addEventListener("click", maFonction);

// Supprimer l'écouteur
button.removeEventListener("click", maFonction);</code></pre>
    
    <h2>5. Types d'événements courants</h2>
    
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left;">Événement</th>
            <th style="padding: 8px; text-align: left;">Description</th>
        </thead>
        <tbody>
            <tr><td style="padding: 8px;"><code>click</code></td><td style="padding: 8px;">Clic de souris</td></tr>
            <tr><td style="padding: 8px;"><code>dblclick</code></td><td style="padding: 8px;">Double clic</td></tr>
            <tr><td style="padding: 8px;"><code>mouseover</code></td><td style="padding: 8px;">Souris au-dessus</td></tr>
            <tr><td style="padding: 8px;"><code>mouseout</code></td><td style="padding: 8px;">Souris quitte</td></tr>
            <tr><td style="padding: 8px;"><code>keydown</code></td><td style="padding: 8px;">Touche enfoncée</td></tr>
            <tr><td style="padding: 8px;"><code>keyup</code></td><td style="padding: 8px;">Touche relâchée</td></tr>
            <tr><td style="padding: 8px;"><code>submit</code></td><td style="padding: 8px;">Formulaire soumis</td></tr>
            <tr><td style="padding: 8px;"><code>load</code></td><td style="padding: 8px;">Page chargée</td></tr>
        </tbody>
    </table>
    
    <h2>6. Exemple complet</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;body&gt;
    &lt;h2&gt;Gestionnaire vs Écouteur d'Événements&lt;/h2&gt;
    
    &lt;button id="demoBtn"&gt;Cliquez-moi&lt;/button&gt;
    &lt;p id="message"&gt;&lt;/p&gt;
    
    &lt;script&gt;
        let btn = document.getElementById("demoBtn");
        let msg = document.getElementById("message");
        
        // Avec handler (remplace)
        btn.onclick = () => msg.innerHTML = "Handler: Premier message";
        btn.onclick = () => msg.innerHTML = "Handler: Ce message remplace le premier";
        
        // Avec listener (ajoute)
        btn.addEventListener("click", () => {
            console.log("Listener: Premier écouteur");
        });
        btn.addEventListener("click", () => {
            console.log("Listener: Deuxième écouteur");
        });
        
        // Alternative: fonctions nommées
        function showAlert() {
            alert("Bouton cliqué !");
        }
        
        // Ajouter un écouteur supplémentaire
        btn.addEventListener("click", showAlert);
        
        // Supprimer après 5 secondes
        setTimeout(() => {
            btn.removeEventListener("click", showAlert);
            console.log("Écouteur showAlert supprimé");
        }, 5000);
    &lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <div class="info-box">
        <p><strong>💡 À retenir :</strong> Event handlers = une seule fonction par événement (remplacement). Event listeners = plusieurs fonctions par événement (ajout). Les écouteurs d'événements sont recommandés pour le développement JavaScript moderne.</p>
    </div>
    """.strip()
    
    cours_data = {
        "titre": "JavaScript Events - Handlers vs Listeners",
        "slug": slug_cours,
        "description": "Apprenez la différence entre les gestionnaires d'événements (onclick) et les écouteurs d'événements (addEventListener) en JavaScript. Découvrez pourquoi les event listeners sont préférés pour les applications modernes.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 20,
        "ordre_affichage": 16,
        "chapitre_id": chapitre_id,
        "tags": ["javascript", "events", "event-handlers", "event-listeners", "addEventListener", "onclick", "debutant"],
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

def inserer_questions_javascript_events(cours_id):
    
    
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
            "question": "Quelle est la principale différence entre un event handler et un event listener ?",
            "options": '{"A": "Handler ne fonctionne que sur mobile", "B": "Handler permet plusieurs fonctions, Listener une seule", "C": "Handler permet une seule fonction par événement, Listener permet plusieurs", "D": "Ils sont identiques"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "Event handlers (comme onclick) ne permettent qu'une seule fonction par événement. Event listeners (addEventListener) permettent d'attacher plusieurs fonctions.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quelle méthode permet d'attacher un écouteur d'événement ?",
            "options": '{"A": "attachEvent()", "B": "addEvent()", "C": "addEventListener()", "D": "setListener()"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "addEventListener() est la méthode standard pour attacher des écouteurs d'événements.",
            "mode_specifique": "texte"
        },
        
        
        {
            "question": "Que se passe-t-on si on assigne deux fois onclick sur le même bouton ?",
            "options": '{"A": "Les deux s\'exécutent", "B": "Le second remplace le premier", "C": "Une erreur se produit", "D": "Rien ne se passe"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Le second gestionnaire remplace le premier car un seul handler par événement est autorisé.",
            "mode_specifique": "audio"
        },
        {
            "question": "Que se passe-t-on si on utilise deux fois addEventListener sur le même événement ?",
            "options": '{"A": "Le second remplace le premier", "B": "Les deux s\'exécutent", "C": "Une erreur se produit", "D": "Seul le premier s\'exécute"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Les deux écouteurs s'exécutent car addEventListener permet d'attacher plusieurs fonctions.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle méthode permet de supprimer un écouteur d'événement ?",
            "options": '{"A": "removeEvent()", "B": "detachListener()", "C": "removeEventListener()", "D": "deleteListener()"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "removeEventListener() supprime un écouteur d'événement précédemment ajouté.",
            "mode_specifique": "audio"
        },
        
        
        {
            "question": "Quelle est la syntaxe correcte pour ajouter un écouteur de clic ?",
            "options": '{"A": "button.onclick = function() {}", "B": "button.click(function() {})", "C": "button.addEventListener(\'click\', function() {})", "D": "button.addEvent(\'click\', function() {})"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "addEventListener('click', callback) est la syntaxe standard pour ajouter un écouteur de clic.",
            "mode_specifique": "video"
        },
        {
            "question": "Quel événement correspond à un double clic ?",
            "options": '{"A": "click", "B": "doubleclick", "C": "dblclick", "D": "double-click"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "dblclick est l'événement pour le double clic.",
            "mode_specifique": "video"
        },
        {
            "question": "Quel événement est déclenché quand la souris passe au-dessus d'un élément ?",
            "options": '{"A": "mouseenter", "B": "mouseover", "C": "mouseup", "D": "mousedown"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "mouseover est déclenché quand la souris passe au-dessus d'un élément.",
            "mode_specifique": "video"
        },
        {
            "question": "Pourquoi recommande-t-on d'utiliser addEventListener plutôt que les handlers onclick ?",
            "options": '{"A": "C\'est plus rapide", "B": "Cela permet d\'attacher plusieurs fonctions", "C": "Cela fonctionne sur plus de navigateurs", "D": "Cela utilise moins de mémoire"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "addEventListener permet d'attacher plusieurs fonctions au même événement, contrairement à onclick.",
            "mode_specifique": "video"
        },
        {
            "question": "Que doit-on passer à removeEventListener pour supprimer un écouteur ?",
            "options": '{"A": "Seulement le type d\'événement", "B": "La fonction originale utilisée dans addEventListener", "C": "Le nom de l\'élément", "D": "L\'index de l\'écouteur"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "removeEventListener nécessite la même fonction que celle ajoutée avec addEventListener.",
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
    print("🎓 INSERTION DU COURS: JAVASCRIPT EVENTS")
    print("(Event Handlers vs Event Listeners)")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    cours_id = inserer_cours_javascript_events()
    
    if cours_id:
        inserer_questions_javascript_events(cours_id)
        print(f"\n🎉 Succès ! Cours 'JavaScript Events - Handlers vs Listeners' créé (ID: {cours_id})")
    else:
        print("\n❌ Échec de l'insertion")

if __name__ == "__main__":
    main()