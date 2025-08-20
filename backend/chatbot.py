import json
import os
import re
from typing import List, Dict, Any, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pickle

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class SymptomCheckerBot:
    def __init__(self):
        # Prefer fine-tuned encoder if available
        finetuned_dir = os.path.join(os.path.dirname(__file__), 'models', 'fine_tuned_symptom_checker')
        if os.path.isdir(finetuned_dir):
            self.model = SentenceTransformer(finetuned_dir)
        else:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')

        self.knowledge_base = self._load_knowledge_base()
        self.medical_data = self._load_medical_data()
        self.conversation_history: List[Dict[str, Any]] = []
        self.session_in_scope = False
        self.current_case: Dict[str, Any] = {
            'onset': None,
            'location': None,
            'severity': None,
            'associated_symptoms': set(),
            'duration': None
        }
        self.greeting_patterns = [
            r'\b(hi|hello|hey|good morning|good afternoon|good evening)\b',
            r'\bhow are you\b',
            r"\bwhat's up\b",
            r"\bhow's it going\b"
        ]
        
        # Short, templated lists as fallback explanations
        self.abdominal_pain_responses = {
            'causes': [
                "Abdominal pain in adults can be caused by various factors including:",
                "• Indigestion or heartburn",
                "• Food poisoning",
                "• Stomach flu (gastroenteritis)",
                "• Irritable bowel syndrome (IBS)",
                "• Constipation",
                "• Gas and bloating",
                "• Appendicitis",
                "• Gallstones",
                "• Kidney stones",
                "• Ulcers",
                "• Inflammatory bowel disease (IBD)"
            ],
            'symptoms': [
                "Common symptoms associated with abdominal pain include:",
                "• Cramping or sharp pain",
                "• Nausea and vomiting",
                "• Loss of appetite",
                "• Fever",
                "• Diarrhea or constipation",
                "• Bloating",
                "• Heartburn",
                "• Pain that radiates to other areas"
            ],
            'when_to_seek_help': [
                "Seek immediate medical attention if you experience:",
                "• Severe, sudden abdominal pain",
                "• Pain with fever",
                "• Pain with vomiting blood",
                "• Pain with black, tarry stools",
                "• Pain that lasts more than 24 hours",
                "• Pain that gets worse over time",
                "• Pain with difficulty breathing",
                "• Pain with chest pressure"
            ],
            'home_remedies': [
                "For mild abdominal pain, you can try:",
                "• Rest and avoid strenuous activity",
                "• Apply a heating pad to the area",
                "• Drink clear fluids (water, broth)",
                "• Eat bland foods (rice, toast, bananas)",
                "• Avoid spicy, fatty, or acidic foods",
                "• Take over-the-counter pain relievers if appropriate",
                "• Practice relaxation techniques"
            ]
        }
        
        # Load fine-tuned model pickled state if present (legacy)
        self.fine_tuned_model = self._load_fine_tuned_model()
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load a minimal knowledge base for quick checks"""
        knowledge_file = os.path.join(os.path.dirname(__file__), 'data', 'abdominal_pain_knowledge.json')
        if os.path.exists(knowledge_file):
            with open(knowledge_file, 'r') as f:
                return json.load(f)
        return {
            'symptom': 'abdominal pain in adults',
            'causes': [
                'indigestion', 'heartburn', 'food poisoning', 'stomach flu', 
                'gastroenteritis', 'ibs', 'irritable bowel syndrome', 'constipation',
                'gas', 'bloating', 'appendicitis', 'gallstones', 'kidney stones',
                'ulcers', 'inflammatory bowel disease', 'ibd'
            ],
            'symptoms': [
                'cramping', 'sharp pain', 'nausea', 'vomiting', 'loss of appetite',
                'fever', 'diarrhea', 'constipation', 'bloating', 'heartburn'
            ],
            'severity_indicators': [
                'severe pain', 'sudden pain', 'fever', 'vomiting blood',
                'black stools', 'difficulty breathing', 'chest pressure'
            ]
        }

    def _load_medical_data(self) -> Dict[str, Any]:
        """Load structured abdominal pain dataset used for responses"""
        data_file = os.path.join(os.path.dirname(__file__), 'data', 'abdominal_pain_data.json')
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                return json.load(f)
        # Fallback minimal structure
        return {
            'symptom': 'abdominal pain in adults',
            'causes': [],
            'emergency_symptoms': [],
            'home_remedies': [],
            'prevention_tips': [],
            'when_to_see_doctor': []
        }
    
    def _load_fine_tuned_model(self):
        """Load legacy fine-tuned pickle if available"""
        model_path = os.path.join(os.path.dirname(__file__), 'models', 'fine_tuned_model.pkl')
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    return pickle.load(f)
            except Exception:
                return None
        return None
    
    def _is_greeting(self, message: str) -> bool:
        message_lower = message.lower()
        for pattern in self.greeting_patterns:
            if re.search(pattern, message_lower):
                return True
        return False
    
    def _get_greeting_response(self) -> str:
        greetings = [
            "Hello! I'm your symptom checker assistant. I'm here to help you understand abdominal pain and related symptoms. How can I assist you today?",
            "Hi there! I'm a medical AI assistant specializing in abdominal pain. I can help answer your questions about symptoms, causes, and when to seek medical attention. What would you like to know?",
            "Hello! I'm here to help you with questions about abdominal pain in adults. I can provide information about causes, symptoms, and treatment options. How may I help you?"
        ]
        return np.random.choice(greetings)
    
    def _extract_keywords(self, message: str) -> List[str]:
        tokens = word_tokenize(message.lower())
        stop_words = set(stopwords.words('english'))
        keywords = [word for word in tokens if word.isalnum() and word not in stop_words]
        return keywords

    def _extract_structured_facts(self, message: str) -> Dict[str, Any]:
        """Extract structured symptom facts from free text.
        Only uses terms defined in our training data.
        """
        text = message.lower()
        facts: Dict[str, Any] = {'onset': None, 'location': None, 'severity': None, 'associated_symptoms': set(), 'duration': None}

        # Onset/duration
        if re.search(r'\b(today|this\s+morning|this\s+evening|now|just|since)\b', text):
            facts['onset'] = 'today'
        if re.search(r'\b(yesterday|last\s+night)\b', text):
            facts['onset'] = 'yesterday'
        m = re.search(r'\b(\d+|one|two|three|four|five)\s*(hour|hours|day|days)\b', text)
        if m:
            facts['duration'] = m.group(0)

        # Location
        location_map = [
            ('upper right', ['upper right', 'right upper', 'ruq']),
            ('upper left', ['upper left', 'left upper', 'luq']),
            ('lower right', ['lower right', 'right lower', 'rlq']),
            ('lower left', ['lower left', 'left lower', 'llq']),
            ('upper abdomen', ['upper abdomen', 'upper stomach']),
            ('lower abdomen', ['lower abdomen', 'lower stomach']),
            ('whole abdomen', ['whole abdomen', 'entire abdomen', 'all over', 'whole stomach'])
        ]
        for loc_label, patterns in location_map:
            if any(p in text for p in patterns):
                facts['location'] = loc_label
                break

        # Severity
        if 'mild' in text:
            facts['severity'] = 'mild'
        elif 'moderate' in text:
            facts['severity'] = 'moderate'
        elif 'severe' in text or 'worst' in text:
            facts['severity'] = 'severe'

        # Associated symptoms (limited to our dataset terms)
        assoc_terms = ['nausea', 'vomiting', 'diarrhea', 'constipation', 'fever', 'bloating', 'heartburn', 'gas', 'loss of appetite', 'back pain', 'shoulder pain']
        for term in assoc_terms:
            if term in text:
                facts['associated_symptoms'].add(term)
        if 'vomit' in text and 'vomiting' not in facts['associated_symptoms']:
            facts['associated_symptoms'].add('vomiting')

        return facts

    def _update_case_state(self, facts: Dict[str, Any]):
        if facts.get('onset'):
            self.current_case['onset'] = facts['onset']
        if facts.get('location'):
            self.current_case['location'] = facts['location']
        if facts.get('severity'):
            self.current_case['severity'] = facts['severity']
        if facts.get('duration'):
            self.current_case['duration'] = facts['duration']
        if facts.get('associated_symptoms'):
            self.current_case['associated_symptoms'].update(facts['associated_symptoms'])

    def _case_summary_text(self) -> str:
        parts = []
        if self.current_case['onset']:
            parts.append(f"onset {self.current_case['onset']}")
        if self.current_case['duration']:
            parts.append(f"duration {self.current_case['duration']}")
        if self.current_case['location']:
            parts.append(f"location {self.current_case['location']}")
        if self.current_case['severity']:
            parts.append(f"severity {self.current_case['severity']}")
        if self.current_case['associated_symptoms']:
            parts.append("symptoms " + ", ".join(sorted(self.current_case['associated_symptoms'])))
        if not parts:
            return "abdominal pain"
        return "; ".join(parts)

    def _rank_causes(self) -> List[Tuple[Dict[str, Any], float]]:
        """Rank likely causes by embedding similarity between case summary and cause descriptions."""
        causes = self.medical_data.get('causes', [])
        if not causes:
            return []
        case_text = self._case_summary_text()
        cause_texts = [f"{c.get('condition','')}. {c.get('description','')}. Symptoms: {', '.join(c.get('symptoms', []))}" for c in causes]
        case_vec = self.model.encode([case_text])
        cause_vecs = self.model.encode(cause_texts)
        sims = cosine_similarity(case_vec, cause_vecs)[0]
        ranked = sorted(zip(causes, sims), key=lambda x: x[1], reverse=True)
        return ranked[:3]

    def _red_flag_check(self) -> List[str]:
        flags = []
        emergencies = [s.lower() for s in self.medical_data.get('emergency_symptoms', [])]
        text = self._case_summary_text().lower()
        for item in emergencies:
            # simple token match
            terms = [t.strip() for t in re.split(r'[,:;]', item)]
            if any(term and term in text for term in terms):
                flags.append(item)
        # explicit patterns
        if self.current_case.get('severity') == 'severe':
            flags.append('Severe abdominal pain')
        if 'fever' in self.current_case['associated_symptoms']:
            flags.append('Pain with fever')
        if 'vomiting' in self.current_case['associated_symptoms'] and 'blood' in text:
            flags.append('Vomiting blood')
        return list(dict.fromkeys(flags))

    def _build_analysis_response(self) -> str:
        summary = self._case_summary_text()
        red_flags = self._red_flag_check()
        ranked = self._rank_causes()

        lines: List[str] = []
        lines.append(f"Thanks for the details. From what you've shared ({summary}), here are the most likely possibilities based on my training data:")
        if ranked:
            for cause, score in ranked:
                lines.append(f"• {cause.get('condition')}: {cause.get('description')}")
        else:
            lines.append("• I need a bit more detail (location, severity, associated symptoms) to narrow causes.")

        if red_flags:
            lines.append("\nBased on red-flag symptoms, I recommend urgent medical attention:")
            for f in red_flags[:5]:
                lines.append(f"• {f}")
        else:
            # Home care suggestions strictly from dataset
            remedies = self.medical_data.get('home_remedies', [])
            if remedies:
                lines.append("\nSelf‑care that may help for mild symptoms:")
                for r in remedies[:4]:
                    lines.append(f"• {r.get('remedy')}: {r.get('description')}")

        # Follow-up prompts if info missing
        need = []
        if not self.current_case['location']:
            need.append('where exactly the pain is located')
        if not self.current_case['severity']:
            need.append('how severe it feels (mild, moderate, severe)')
        if not self.current_case['onset'] and not self.current_case['duration']:
            need.append('when it started and for how long')
        if need:
            lines.append("\nTo improve accuracy, please tell me " + ", ".join(need) + ".")

        lines.append("\nNote: I share general information about abdominal pain in adults and don’t replace a clinician.")
        return "\n".join(lines)

    def _calculate_similarity(self, message: str, knowledge_items: List[str]) -> float:
        if not knowledge_items:
            return 0.0
        message_embedding = self.model.encode([message])
        knowledge_embeddings = self.model.encode(knowledge_items)
        similarities = cosine_similarity(message_embedding, knowledge_embeddings)[0]
        return float(np.max(similarities))
    
    def _get_abdominal_pain_response(self, message: str) -> str:
        message_lower = message.lower()

        # Allow direct knowledge queries
        if any(word in message_lower for word in ['cause', 'causes', 'why', 'reason']):
            return '\n'.join(self.abdominal_pain_responses['causes'])
        elif any(word in message_lower for word in ['symptom', 'symptoms', 'sign', 'signs']):
            return '\n'.join(self.abdominal_pain_responses['symptoms'])
        elif any(word in message_lower for word in ['emergency', 'urgent', 'hospital', 'doctor', 'medical attention']):
            return '\n'.join(self.abdominal_pain_responses['when_to_seek_help'])
        elif any(word in message_lower for word in ['home', 'remedy', 'treatment', 'cure', 'help']):
            return '\n'.join(self.abdominal_pain_responses['home_remedies'])

        # Otherwise, treat as case details and analyze
        facts = self._extract_structured_facts(message)
        self._update_case_state(facts)
        return self._build_analysis_response()
    
    def _is_out_of_scope(self, message: str) -> bool:
        message_lower = message.lower()
        abdominal_keywords = [
            'abdominal', 'stomach', 'belly', 'gut', 'pain', 'ache', 'cramp',
            'indigestion', 'heartburn', 'nausea', 'vomiting', 'diarrhea',
            'constipation', 'bloating', 'gas', 'appendicitis', 'ulcer'
        ]
        has_abdominal_keywords = any(keyword in message_lower for keyword in abdominal_keywords)
        # Keep session in scope once established
        return not (has_abdominal_keywords or self.session_in_scope or self._is_greeting(message))
    
    def get_response(self, message: str) -> str:
        # Track session
        self.conversation_history.append({'user': message, 'timestamp': None})
        if self._is_greeting(message):
            response = self._get_greeting_response()
            self.conversation_history[-1]['bot'] = response
            return response

        # Mark session as in-scope if abdominal terms are present
        if not self.session_in_scope:
            message_lower = message.lower()
            if any(k in message_lower for k in ['abdominal', 'stomach', 'belly', 'gut', 'pain']):
                self.session_in_scope = True

        if self._is_out_of_scope(message):
            response = ("I apologize, but I'm specifically trained to help with abdominal pain in adults. "
                       "I can provide information about causes, symptoms, when to seek medical attention, "
                       "and home remedies related to abdominal pain. Please ask me about abdominal pain or related symptoms.")
            self.conversation_history[-1]['bot'] = response
            return response

        # In scope → analyze
        self.session_in_scope = True
        response = self._get_abdominal_pain_response(message)
        self.conversation_history[-1]['bot'] = response
        return response
    
    def fine_tune(self, training_data: List[Dict[str, str]]):
        # Simplified knowledge base update (kept for compatibility)
        for data_point in training_data:
            question = data_point['question']
            answer = data_point['answer']
            if 'causes' in question.lower():
                self.knowledge_base['causes'].extend(answer.split())
            elif 'symptoms' in question.lower():
                self.knowledge_base['symptoms'].extend(answer.split())
        knowledge_file = os.path.join(os.path.dirname(__file__), 'data', 'abdominal_pain_knowledge.json')
        os.makedirs(os.path.dirname(knowledge_file), exist_ok=True)
        with open(knowledge_file, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
        model_path = os.path.join(os.path.dirname(__file__), 'models', 'fine_tuned_model.pkl')
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        with open(model_path, 'wb') as f:
            pickle.dump(self, f)
