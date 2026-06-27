
import pickle
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import os

logger = logging.getLogger(__name__)

class SequentialPatternMiner:
    
    
      
      
      
      
    

    def __init__(self, min_support=0.10, min_confidence=0.60):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.patterns = []
        self.rules = []

    def extract_sequences(self, df, user_col='user_id', action_col='action',
                           timestamp_col='timestamp', time_window=3600):
        
        sequences = []
        for uid, group in df.groupby(user_col):
            group = group.sort_values(timestamp_col)
            session = []
            last_ts = None
            for _, row in group.iterrows():
                ts = row[timestamp_col]
                if last_ts is None:
                    session.append(row[action_col])
                else:
                    if isinstance(ts, (int, float)):
                        diff = ts - last_ts if isinstance(last_ts, (int, float)) else 0
                    else:
                        diff = (ts - last_ts).total_seconds() if hasattr(ts - last_ts, 'total_seconds') else 0
                    
                    if diff <= time_window:
                        session.append(row[action_col])
                    else:
                        if session:
                            sequences.append(session)
                        session = [row[action_col]]
                last_ts = ts
            if session:
                sequences.append(session)
        return sequences

    def mine_sequential_patterns(self, sequences):
        
        print("🔄 Mining des motifs séquentiels …")
        if not sequences:
            print("⚠️  Aucune séquence.")
            return []
        
        n = len(sequences)
        item_counts = Counter(item for seq in sequences for item in set(seq))
        freq_items = {k: v/n for k, v in item_counts.items() if v/n >= self.min_support}
        patterns = [{k: v} for k, v in freq_items.items()]
        
        pair_counts = Counter(
            (seq[i], seq[i+1])
            for seq in sequences for i in range(len(seq)-1)
        )
        for pair, cnt in pair_counts.items():
            if cnt/n >= self.min_support:
                patterns.append({pair: cnt/n})
        
        self.patterns = patterns
        print(f"✅ {len(patterns)} motifs trouvés")
        return patterns

    def generate_rules(self, sequences):
        
        print("🔄 Génération des règles …")
        if not sequences:
            return []
        
        n = len(sequences)
        seq_counts = Counter(tuple(s) for s in sequences)
        rules = []
        
        for seq, cnt in seq_counts.items():
            if len(seq) < 2:
                continue
            for split in range(1, len(seq)):
                ante = seq[:split]
                cons = seq[split:]
                ante_cnt = sum(1 for s in sequences
                               if tuple(s[:len(ante)]) == ante)
                if ante_cnt == 0:
                    continue
                conf = cnt / ante_cnt
                if conf >= self.min_confidence:
                    rules.append({
                        'antecedent': list(ante),
                        'consequent': list(cons),
                        'support': cnt/n,
                        'confidence': conf,
                        'lift': conf / (len(cons)/n) if n > 0 else 0
                    })
        
        self.rules = sorted(rules, key=lambda x: x['confidence'], reverse=True)
        print(f"✅ {len(self.rules)} règles générées")
        return self.rules

    def predict_dropout_risk(self, user_sequence, threshold=0.60):
        
        score = 0.0
        factors = []
        actions = " ".join(user_sequence)

        if 'inactive' in actions or 'idle' in actions:
            score += 0.30
            factors.append("Période d'inactivité détectée")

        if 'quiz_start' in actions and 'quiz_complete' not in actions:
            score += 0.25
            factors.append("Quiz démarré mais non terminé")

        fails = user_sequence.count('quiz_fail')
        if fails >= 3:
            score += 0.35
            factors.append(f"{fails} échecs consécutifs")

        navs = [a for a in user_sequence if a.startswith('navigate_')]
        if len(navs) > 10 and len(set(navs)) < 3:
            score += 0.20
            factors.append("Navigation erratique")

        for rule in self.rules[:20]:
            ante = rule['antecedent']
            if (len(ante) <= len(user_sequence) and
                user_sequence[:len(ante)] == ante and
                rule['confidence'] > 0.70):
                score += 0.15
                factors.append(f"Pattern : {ante} → {rule['consequent']}")

        risk = min(score, 1.0)
        return {
            'risk_score': risk,
            'risk_level': ('Élevé' if risk > threshold else
                          'Modéré' if risk > 0.30 else 'Faible'),
            'risk_factors': factors
        }

    def save(self, path: str):
        
        try:
            data = {
                'patterns': self.patterns,
                'rules': self.rules,
                'min_support': self.min_support,
                'min_confidence': self.min_confidence
            }
            with open(path, 'wb') as f:
                pickle.dump(data, f)
            logger.info(f"✅ SequentialPatternMiner sauvegardé dans {path}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde: {e}")
            return False

    def load(self, path: str):
        """Charge le modèle - version ultra robuste"""
        if not os.path.exists(path):
            logger.info(f"ℹ️ Fichier non trouvé: {path}")
            return False
        
        try:
            
            with open(path, 'rb') as f:
                data = pickle.load(f)
            
            
            if isinstance(data, dict):
                self.patterns = data.get('patterns', [])
                self.rules = data.get('rules', [])
                self.min_support = data.get('min_support', self.min_support)
                self.min_confidence = data.get('min_confidence', self.min_confidence)
            elif isinstance(data, tuple) and len(data) >= 2:
                self.patterns = data[0] if len(data) > 0 else []
                self.rules = data[1] if len(data) > 1 else []
            else:
                self.patterns = []
                self.rules = []
            
            logger.info(f"✅ SequentialPatternMiner chargé: {len(self.rules)} règles")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement: {e}")
            
            
            try:
                backup_path = path + '.corrupted'
                import shutil
                shutil.copy(path, backup_path)
                logger.info(f"📁 Fichier corrompu sauvegardé vers {backup_path}")
                
                
                self.save(path)
                logger.info(f"✅ Nouveau fichier vide créé")
            except Exception as e2:
                logger.error(f"❌ Impossible de créer le fichier: {e2}")
            
            return False


def generate_sample_logs(n_users=10, n_actions=30):
    
    import random
    actions = [
        'video_start', 'video_complete', 'quiz_start', 'quiz_complete', 'quiz_fail',
        'exercise_start', 'exercise_complete', 'navigate_course', 'navigate_quiz',
        'navigate_profile', 'inactive', 'review_content'
    ]
    base_time = datetime.now()
    rows = []
    for uid in range(1, n_users+1):
        for i in range(n_actions):
            ts = int((base_time + timedelta(minutes=i*random.randint(1,10))).timestamp())
            rows.append({'user_id': uid, 'action': random.choice(actions), 'timestamp': ts})
    return pd.DataFrame(rows)