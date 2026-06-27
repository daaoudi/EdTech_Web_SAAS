
import torch
import pickle
import os
import numpy as np
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict, Any, Optional
from collections import defaultdict
import logging
from config import config
import re

logger = logging.getLogger(__name__)

class BertTutor:
    
    
    def __init__(self, model_path: str = None):
        
        self.model_path = model_path or config.TUTOR_MODEL_PATH
        self.model = None
        self.cours_embeddings = None
        self.cours_ids = None
        self.cours_texts = None
        self.questions_embeddings = None
        self.questions_texts = None
        self.question_cours_mapping = None
        self.cours_mapping = None
        self.cours_description = None
        self.questions_by_course = None
        self.loaded = False
        
    def load_model(self):
        
        if self.model is None:
            try:
                bert_model_name = getattr(config, 'BERT_MODEL_NAME', 'paraphrase-multilingual-MiniLM-L12-v2')
                logger.info(f"🔄 Chargement du modèle BERT: {bert_model_name}")
                self.model = SentenceTransformer(bert_model_name)
                logger.info(f"✅ Modèle BERT chargé: {bert_model_name}")
            except Exception as e:
                logger.error(f"❌ Erreur chargement BERT: {e}")
                raise
    
    def load_embeddings(self):
        """Charger les embeddings pré-calculés depuis tutor_ia_model"""
        try:
            
            if not os.path.exists(self.model_path):
                logger.error(f"❌ Dossier du modèle non trouvé: {self.model_path}")
                return False
            
            
            required_files = [
                'cours_embeddings.pkl', 'cours_ids.pkl', 'cours_texts.pkl',
                'questions_embeddings.pkl', 'questions_texts.pkl',
                'question_cours_mapping.pkl', 'cours_mapping.pkl', 'cours_description.pkl'
            ]
            
            
            missing_files = []
            for file in required_files:
                if not os.path.exists(f'{self.model_path}{file}'):
                    missing_files.append(file)
            
            if missing_files:
                logger.warning(f"⚠️ Fichiers manquants dans {self.model_path}: {missing_files}")
                return False
            
            
            logger.info(f"🔄 Chargement des embeddings depuis {self.model_path}...")
            
            self.cours_embeddings = torch.tensor(pickle.load(
                open(f'{self.model_path}cours_embeddings.pkl', 'rb')))
            self.cours_ids = pickle.load(open(f'{self.model_path}cours_ids.pkl', 'rb'))
            self.cours_texts = pickle.load(open(f'{self.model_path}cours_texts.pkl', 'rb'))
            self.questions_embeddings = torch.tensor(pickle.load(
                open(f'{self.model_path}questions_embeddings.pkl', 'rb')))
            self.questions_texts = pickle.load(open(f'{self.model_path}questions_texts.pkl', 'rb'))
            self.question_cours_mapping = pickle.load(open(f'{self.model_path}question_cours_mapping.pkl', 'rb'))
            self.cours_mapping = pickle.load(open(f'{self.model_path}cours_mapping.pkl', 'rb'))
            self.cours_description = pickle.load(open(f'{self.model_path}cours_description.pkl', 'rb'))
            
            
            self.questions_by_course = {}
            for question_text, info in self.question_cours_mapping.items():
                cours_id = str(info.get('cours_id', ''))
                if cours_id not in self.questions_by_course:
                    self.questions_by_course[cours_id] = []
                
                
                self.questions_by_course[cours_id].append({
                    'question': question_text,
                    'reponse_correcte': info.get('reponse_correcte', 'A'),
                    'options': self._get_clean_options(question_text, info),
                    'points': info.get('points', 10),
                    'difficulte': info.get('difficulte', 'moyen'),
                    'explication': info.get('explication', '')
                })
            
            self.loaded = True
            logger.info(f"✅ Embeddings chargés: {len(self.cours_ids)} cours, {len(self.questions_texts)} questions")
            logger.info(f"✅ questions_by_course: {len(self.questions_by_course)} cours avec questions")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur chargement embeddings: {e}")
            return False
    
    def is_ready(self) -> bool:
        
        return self.loaded and self.model is not None
    
    def recommend_courses(self, questions_echouees: List[str], 
                          seuil: float = 0.50, 
                          top_n: int = 5) -> List[Dict]:
        
        if not self.is_ready() or not questions_echouees:
            return []
        
        
        cours_directs = set()
        questions_par_cours = defaultdict(list)
        
        for q in questions_echouees:
            if q in self.question_cours_mapping:
                cid = self.question_cours_mapping[q]['cours_id']
                cours_directs.add(cid)
                questions_par_cours[cid].append(q)
        
        
        err_emb = self.model.encode(questions_echouees, convert_to_tensor=True)
        
        resultats = []
        for i, cid in enumerate(self.cours_ids):
            if cid in cours_directs:
                score = 0.95 + (0.05 * min(1.0, len(questions_par_cours.get(cid, [])) / 5))
                resultats.append({
                    'cours_id': cid,
                    'cours_titre': self.cours_mapping.get(cid, '?'),
                    'score': round(score, 4),
                    'description': self.cours_description.get(cid, '')[:200],
                    'direct_match': True,
                    'nb_erreurs': len(questions_par_cours.get(cid, []))
                })
            else:
                c_emb = self.cours_embeddings[i]
                sims = util.cos_sim(c_emb.unsqueeze(0), err_emb)[0]
                score = sims.max().item()
                
                if score >= seuil:
                    resultats.append({
                        'cours_id': cid,
                        'cours_titre': self.cours_mapping.get(cid, '?'),
                        'score': round(score, 4),
                        'description': self.cours_description.get(cid, '')[:200],
                        'direct_match': False,
                        'nb_erreurs': 0
                    })
        
        resultats.sort(key=lambda x: (not x['direct_match'], -x['score']))
        return resultats[:top_n]
    
    def generate_quiz(self, cours_id: str, n: int = 5, 
                  difficulte: str = None) -> Optional[Dict]:
        
        if not self.is_ready():
            return None
        
       
        n = min(n, 20) 
        n = max(n, 1)   
        
       
        cours_id_str = str(cours_id)
        
        if cours_id_str not in self.cours_ids:
            logger.warning(f"Cours {cours_id_str} non trouvé dans les embeddings")
            return None
        
        idx = self.cours_ids.index(cours_id_str)
        cours_emb = self.cours_embeddings[idx]
        
        sims = util.cos_sim(cours_emb.unsqueeze(0), self.questions_embeddings)[0]
        
        results = []
        for i, score in enumerate(sims):
            q_text = self.questions_texts[i]
            q_info = self.question_cours_mapping.get(q_text, {})
            
            if difficulte and q_info.get('difficulte', '') != difficulte:
                continue
            
            
            options = self._get_clean_options(q_text, q_info)
            
            results.append({
                'question': q_text,
                'options': options,
                'correct_answer': q_info.get('reponse_correcte', 'A'),
                'explication': q_info.get('explication', ''),
                'difficulte': q_info.get('difficulte', 'moyen'),
                'points': q_info.get('points', 10),
                'score': round(score.item(), 4)
            })
        
        
        results.sort(key=lambda x: x['score'], reverse=True)
        selected = results[:n]
        
        
        if len(selected) < n and len(results) > 0:
            import random
            while len(selected) < n:
                selected.append(random.choice(results))
            logger.info(f"⚠️ Répétition de questions pour atteindre {n} questions")
        
        return {
            'cours_id': cours_id_str,
            'cours_titre': self.cours_mapping.get(cours_id_str, f"Cours {cours_id}"),
            'questions': selected,
            'generated_by': 'BERT'
        }

    def _get_clean_options(self, question_text: str, q_info: Dict) -> Dict[str, str]:
        
        
        
        CLEAN_OPTIONS = {
            "Quelle balise HTML5 est utilisée pour surligner du texte ?": {
                'A': "<mark>", 'B': "<highlight>", 'C': "<strong>", 'D': "<em>"
            },
            "Quelles balises HTML5 permettent de créer du contenu pliable/dépliable ?": {
                'A': "<details> et <summary>", 'B': "<collapse> et <expand>", 
                'C': "<fold> et <unfold>", 'D': "<hide> et <show>"
            },
            "Quel est l'avantage principal des balises sémantiques HTML5 ?": {
                'A': "Meilleur SEO et accessibilité", 'B': "Chargement plus rapide",
                'C': "Design plus joli", 'D': "Compatibilité avec plus de navigateurs"
            },
            "Comment modifier le contenu texte d'un élément HTML en JavaScript ?": {
                'A': "element.innerHTML = nouveauTexte", 'B': "element.text = nouveauTexte",
                'C': "element.value = nouveauTexte", 'D': "element.content = nouveauTexte"
            },
            "Quelle balise utiliser pour le titre principal d'une page HTML ?": {
                'A': "<title>", 'B': "<h1>", 'C': "<head>", 'D': "<header>"
            },
            "Quelle balise HTML est utilisée pour créer un lien hypertexte ?": {
                'A': "<link>", 'B': "<a>", 'C': "<href>", 'D': "<url>"
            },
            "Comment ouvrir un lien dans un nouvel onglet ?": {
                'A': "target='_self'", 'B': "target='_blank'", 
                'C': "target='_new'", 'D': "target='_top'"
            },
            "Quelle est la syntaxe correcte pour créer un lien ?": {
                'A': "<link href='page.html'>Lien</link>", 'B': "<a src='page.html'>Lien</a>",
                'C': "<a href='page.html'>Lien</a>", 'D': "<hyperlink='page.html'>Lien</hyperlink>"
            }
        }
        
        
        for q_key, clean_opts in CLEAN_OPTIONS.items():
            if q_key in question_text or question_text in q_key:
                return clean_opts
        
        
        options_raw = q_info.get('options_raw', '')
        parsed = self._parse_options(options_raw)
        
        
        if parsed and parsed.get('A') and not parsed['A'].startswith('Option'):
            return parsed
        
        
        return {'A': 'Option A', 'B': 'Option B', 'C': 'Option C', 'D': 'Option D'}
    

    def generate_quiz_from_concepts(self, concepts: List[str], course_id: str, num_questions: int = 5, mode: str = 'audio') -> Optional[Dict]:
        
        
        
        if not self.is_ready():
            logger.warning("BERT Tutor non prêt")
            return None
        
        
        course_id_str = str(course_id)
        
        
        course_questions = self.questions_by_course.get(course_id_str, [])
        
        logger.info(f"📚 Cours {course_id_str}: {len(course_questions)} questions disponibles")
        
        if not course_questions:
            logger.warning(f"Aucune question trouvée pour le cours {course_id_str}")
            
            return self.generate_quiz(course_id_str, min(num_questions, 10))
        
        
        relevant_questions = []
        matched_concepts = []
        
        for question in course_questions:
            question_text = question.get('question', '').lower()
            for concept in concepts:
                concept_lower = concept.lower()
                
                if concept_lower in question_text or any(word in question_text for word in concept_lower.split()[:3]):
                    relevant_questions.append(question)
                    matched_concepts.append(concept[:50])
                    logger.info(f"✅ Match trouvé: '{concept[:50]}' -> '{question_text[:50]}'")
                    break
        
        
        if len(relevant_questions) < num_questions:
            logger.info(f"⚠️ Seulement {len(relevant_questions)} questions pertinentes, ajout de questions du cours")
            for question in course_questions:
                if question not in relevant_questions:
                    relevant_questions.append(question)
                if len(relevant_questions) >= num_questions * 2:
                    break
        
        
        if not relevant_questions:
            logger.warning("Aucune question pertinente trouvée, utilisation du quiz standard")
            return self.generate_quiz(course_id_str, min(num_questions, 10))
        
        
        import random
        selected_questions = random.sample(relevant_questions, min(num_questions, len(relevant_questions)))
        
        
        formatted_questions = []
        for idx, q in enumerate(selected_questions):
            formatted_questions.append({
                "id": idx + 1,
                "question": q.get('question', ''),
                "options": q.get('options', {'A': 'Option A', 'B': 'Option B', 'C': 'Option C', 'D': 'Option D'}),
                "correct_answer": q.get('reponse_correcte', 'A'),
                "points": q.get('points', 10),
                "difficulte": q.get('difficulte', 'moyen'),
                "explanation": q.get('explication', f"Révisez le concept: {concepts[0][:100] if concepts else 'les bases'}")
            })
        
        logger.info(f"🎯 Quiz personnalisé généré: {len(formatted_questions)} questions basées sur {len(concepts)} erreurs")
        
        return {
            "course_id": course_id_str,
            "questions": formatted_questions,
            "generated_by": "BERT",
            "based_on_mistakes": True,
            "mode": mode,
            "concepts_matched": matched_concepts[:5]
        }
    
    def get_questions_by_course(self, course_id: str) -> List[Dict]:
        
        if not self.is_ready():
            return []
        return self.questions_by_course.get(str(course_id), [])
    
    

    def _parse_options(self, options_raw: str) -> Dict[str, str]:
        
        
        opts = {
            'A': 'Option A',
            'B': 'Option B', 
            'C': 'Option C',
            'D': 'Option D'
        }
        
        if not options_raw or not isinstance(options_raw, str):
            return opts
        
        text = options_raw
        
        
        import re
        
        
        double_quotes = re.findall(r'"([^"]+)"', text)
        
        
        single_quotes = re.findall(r"'([^']+)'", text)
        
        
        all_values = []
        for v in double_quotes:
            v = v.replace("''", "'")
            v = v.strip()
            if v and v not in all_values:
                all_values.append(v)
        
        for v in single_quotes:
            v = v.replace("''", "'")
            v = v.strip()
            if v and v not in all_values and len(v) > 1:
                all_values.append(v)
        
        
        
        valid_values = [v for v in all_values if v and not v.startswith('{') and len(v) > 1]
        
        
        for i, letter in enumerate(['A', 'B', 'C', 'D']):
            if i < len(valid_values):
                opts[letter] = valid_values[i]
        
        
        if len(valid_values) < 4:
            
            for letter in ['A', 'B', 'C', 'D']:
                
                pattern = r"'" + letter + r"'\":\s*'\"([^'\"]+)'\""
                match = re.search(pattern, text)
                if match:
                    value = match.group(1)
                    value = value.replace("''", "'")
                    opts[letter] = value
                    continue
                
                
                pattern2 = r"'" + letter + r"'\":\s*\"([^\"]+)\""
                match2 = re.search(pattern2, text)
                if match2:
                    value = match2.group(1)
                    value = value.replace("''", "'")
                    opts[letter] = value
        
        return opts
    
    def analyze_learning_patterns(self, user_results: List[Dict]) -> Dict:
        
        if not user_results:
            return {
                'strong_topics': [],
                'weak_topics': [],
                'preferred_mode': None,
                'recommendations': []
            }
        
        course_scores = {}
        mode_scores = {'texte': [], 'audio': [], 'video': []}
        
        for result in user_results:
            course_id = str(result.get('cours_id'))
            score = result.get('score_quiz', 0)
            mode = result.get('mode', 'texte')
            
            if course_id not in course_scores:
                course_scores[course_id] = []
            course_scores[course_id].append(score)
            
            if mode in mode_scores:
                mode_scores[mode].append(score)
        
        strong_topics = []
        weak_topics = []
        
        for course_id, scores in course_scores.items():
            avg_score = sum(scores) / len(scores) if scores else 0
            course_title = self.cours_mapping.get(course_id, course_id) if self.cours_mapping else course_id
            
            if avg_score >= 75:
                strong_topics.append({'id': course_id, 'title': course_title, 'score': avg_score})
            elif avg_score <= 50:
                weak_topics.append({'id': course_id, 'title': course_title, 'score': avg_score})
        
        preferred_mode = None
        best_avg = 0
        for mode, scores in mode_scores.items():
            if scores:
                avg = sum(scores) / len(scores) if scores else 0
                if avg > best_avg:
                    best_avg = avg
                    preferred_mode = mode
        
        return {
            'strong_topics': sorted(strong_topics, key=lambda x: x['score'], reverse=True)[:5],
            'weak_topics': sorted(weak_topics, key=lambda x: x['score'])[:5],
            'preferred_mode': preferred_mode,
            'recommendations': self._generate_recommendations(weak_topics, preferred_mode)
        }
    
    def _generate_recommendations(self, weak_topics: List, preferred_mode: str) -> List[str]:
        
        recommendations = []
        
        if weak_topics:
            topics_str = ", ".join([t['title'][:30] for t in weak_topics[:3]])
            recommendations.append(f"Revoyez les concepts clés de: {topics_str}")
        
        if preferred_mode:
            mode_map = {'texte': '📖 lecture', 'audio': '🎧 audio', 'video': '🎬 vidéo'}
            recommendations.append(f"Votre mode d'apprentissage préféré est le {mode_map.get(preferred_mode, preferred_mode)}")
        
        recommendations.append("Pratiquez avec des exercices interactifs pour renforcer vos compétences")
        
        return recommendations

    def debug_questions(self):
        
        if not self.is_ready():
            print("BERT non chargé")
            return
        
        print("\n=== DEBUG QUESTIONS ===\n")
        for i, q_text in enumerate(self.questions_texts[:5]):
            q_info = self.question_cours_mapping.get(q_text, {})
            print(f"Question {i+1}: {q_text[:100]}...")
            print(f"Options raw: {q_info.get('options_raw', 'VIDE')[:200]}")
            print(f"Options parsed: {self._parse_options(q_info.get('options_raw', ''))}")
            print("-" * 50)
    def test_parse_options(self, sample_text: str = None):
        
        if sample_text is None:
            
            for q_text, q_info in list(self.question_cours_mapping.items())[:1]:
                sample_text = q_info.get('options_raw', '')
                print(f"\n🔍 Test parsing sur: {q_text[:50]}...")
                print(f"Raw: {sample_text}")
                parsed = self._parse_options(sample_text)
                print(f"Parsed: {parsed}")
                return parsed
        
        return self._parse_options(sample_text)


bert_tutor = BertTutor()