
import whisper
import torch
import tempfile
import os
import logging
from typing import Dict, List, Any, Optional
import re

logger = logging.getLogger(__name__)

class VoiceSearchService:
    def __init__(self):
        self.model = None
        self.intent_map = self.create_intent_map()
        
    def load_model(self):
        """Charger le modèle Whisper"""
        if self.model is None:
            try:
                
                self.model = whisper.load_model("base")
                logger.info("✅ Modèle Whisper chargé avec succès")
            except Exception as e:
                logger.error(f"❌ Erreur chargement modèle Whisper: {e}")
                raise
    
    def create_intent_map(self) -> Dict[str, Any]:
        
        return {
            
            "topics": {
                "html": {
                    "keywords": ["html", "balise", "structure", "page web", "hypertexte", "html5"],
                    "course_ids": [6, 7, 11]
                },
                "css": {
                    "keywords": ["css", "style", "design", "mise en page", "couleur", "flexbox", "grid"],
                    "course_ids": [10]
                },
                "javascript": {
                    "keywords": ["javascript", "js", "script", "interactif", "dynamique"],
                    "course_ids": []
                },
                "formulaire": {
                    "keywords": ["formulaire", "form", "input", "champ", "saisie", "validation"],
                    "course_ids": [8]
                },
                "lien": {
                    "keywords": ["lien", "hyperlien", "anchor", "href", "navigation", "url"],
                    "course_ids": [7, 11]
                },
                "image": {
                    "keywords": ["image", "img", "photo", "illustration", "visuel"],
                    "course_ids": [7]
                },
                "texte": {
                    "keywords": ["texte", "paragraphe", "titre", "formatage", "heading"],
                    "course_ids": [6]
                },
                "tableau": {
                    "keywords": ["tableau", "table", "data", "cellule", "ligne"],
                    "course_ids": []
                },
                "semantique": {
                    "keywords": ["sémantique", "semantique", "html5", "structure", "header", "footer", "nav", "article"],
                    "course_ids": [9]
                }
            },
            
            "difficulty": {
                "debutant": ["débutant", "facile", "base", "introduction", "premier pas", "découvrir", "apprendre"],
                "intermediaire": ["intermédiaire", "moyen", "approfondi", "pratique", "avancé"],
                "avance": ["avancé", "expert", "difficile", "complexe", "maîtriser", "perfectionnement"]
            },
            
            "actions": {
                "chercher": ["cherche", "trouver", "recherche", "afficher", "montrer", "donner"],
                "apprendre": ["apprendre", "étudier", "comprendre", "maîtriser", "découvrir"],
                "pratiquer": ["pratiquer", "exercice", "entraînement", "travailler"]
            }
        }
    
    def analyze_intent(self, text: str) -> Dict[str, Any]:
        
        text_lower = text.lower()
        
        intent = {
            "original_query": text,
            "processed_query": text_lower,
            "topics": [],
            "difficulty": None,
            "actions": [],
            "keywords": [],
            "course_ids": set(),
            "confidence": 0.0
        }
        
        
        for topic, data in self.intent_map["topics"].items():
            for keyword in data["keywords"]:
                if keyword in text_lower:
                    intent["topics"].append(topic)
                    intent["course_ids"].update(data["course_ids"])
                    intent["keywords"].append(keyword)
                    break
        
        
        for level, keywords in self.intent_map["difficulty"].items():
            for keyword in keywords:
                if keyword in text_lower:
                    intent["difficulty"] = level
                    intent["keywords"].append(keyword)
                    break
        
        
        for action, keywords in self.intent_map["actions"].items():
            for keyword in keywords:
                if keyword in text_lower:
                    intent["actions"].append(action)
                    intent["keywords"].append(keyword)
                    break
        
        
        stop_words = ["je", "tu", "il", "elle", "nous", "vous", "ils", "elles", 
                      "le", "la", "les", "un", "une", "des", "pour", "par", "sur", 
                      "dans", "avec", "sans", "et", "ou", "donc", "or", "ni", "car",
                      "veux", "cherche", "trouver", "apprendre", "cours", "moi", "toi",
                      "lui", "elle", "eux", "elles", "ce", "cet", "cette", "ces",
                      "du", "de", "au", "aux", "en", "vers", "pendant", "depuis"]
        
        words = re.findall(r'\b\w+\b', text_lower)
        for word in words:
            if len(word) > 2 and word not in stop_words and word not in intent["keywords"]:
                intent["keywords"].append(word)
        
        
        confidence = 0.0
        if intent["topics"]:
            confidence += 0.4
        if intent["difficulty"]:
            confidence += 0.3
        if intent["actions"]:
            confidence += 0.2
        if len(intent["keywords"]) > 0:
            confidence += 0.1
        
        intent["confidence"] = min(confidence, 1.0)
        
        return intent
    
    def transcribe_audio(self, audio_file_path: str) -> Dict[str, Any]:
        
        try:
            self.load_model()
            
            
            result = self.model.transcribe(
                audio_file_path,
                language="fr",
                task="transcribe",
                fp16=False  
            )
            
            transcript = result["text"].strip()
            confidence = 1.0 - result.get("no_speech_prob", 0.0)
            
            
            intent = self.analyze_intent(transcript)
            
            return {
                "success": True,
                "transcript": transcript,
                "confidence": confidence,
                "intent": intent
            }
            
        except Exception as e:
            logger.error(f"Erreur transcription: {e}")
            return {
                "success": False,
                "error": str(e),
                "transcript": "",
                "confidence": 0.0,
                "intent": None
            }


voice_search_service = VoiceSearchService()