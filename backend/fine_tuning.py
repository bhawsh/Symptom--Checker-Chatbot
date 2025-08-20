import json
import os
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
import torch
from sklearn.model_selection import train_test_split
import pickle

class FineTuner:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
    def prepare_training_data(self) -> List[InputExample]:
        """Prepare training data for fine-tuning"""
        
        # Load the abdominal pain data
        data_file = os.path.join(os.path.dirname(__file__), 'data', 'abdominal_pain_data.json')
        
        if not os.path.exists(data_file):
            # Create sample training data if file doesn't exist
            training_data = self._create_sample_training_data()
        else:
            with open(data_file, 'r') as f:
                data = json.load(f)
            training_data = self._extract_training_data(data)
        
        # Convert to InputExample format
        examples = []
        for item in training_data:
            # Positive examples (similar pairs)
            examples.append(InputExample(
                texts=[item['question'], item['answer']],
                label=1.0
            ))
            
            # Negative examples (dissimilar pairs)
            if len(training_data) > 1:
                other_item = training_data[(training_data.index(item) + 1) % len(training_data)]
                examples.append(InputExample(
                    texts=[item['question'], other_item['answer']],
                    label=0.0
                ))
        
        return examples
    
    def _create_sample_training_data(self) -> List[Dict[str, str]]:
        """Create sample training data for abdominal pain"""
        return [
            {
                "question": "What causes abdominal pain?",
                "answer": "Abdominal pain can be caused by indigestion, food poisoning, stomach flu, IBS, constipation, gas, appendicitis, gallstones, kidney stones, ulcers, and inflammatory bowel disease."
            },
            {
                "question": "What are the symptoms of abdominal pain?",
                "answer": "Symptoms include cramping, sharp pain, nausea, vomiting, loss of appetite, fever, diarrhea, constipation, bloating, and heartburn."
            },
            {
                "question": "When should I seek medical attention for abdominal pain?",
                "answer": "Seek immediate medical attention for severe sudden pain, pain with fever, vomiting blood, black stools, pain lasting over 24 hours, or pain with difficulty breathing."
            },
            {
                "question": "What home remedies help with abdominal pain?",
                "answer": "Home remedies include rest, heat therapy, hydration, bland diet, avoiding irritants, and over-the-counter medications as appropriate."
            },
            {
                "question": "How can I prevent abdominal pain?",
                "answer": "Prevention includes eating a healthy diet, staying hydrated, exercising regularly, managing stress, avoiding smoking and excessive alcohol, and practicing good food hygiene."
            },
            {
                "question": "What is appendicitis?",
                "answer": "Appendicitis is inflammation of the appendix causing sudden pain in the lower right abdomen, nausea, vomiting, loss of appetite, fever, and pain that worsens with movement."
            },
            {
                "question": "What are gallstones?",
                "answer": "Gallstones are hardened deposits in the gallbladder causing sudden intense pain in the upper right abdomen, pain in the right shoulder, nausea, vomiting, and back pain."
            },
            {
                "question": "What is IBS?",
                "answer": "Irritable Bowel Syndrome is a chronic condition affecting the large intestine with symptoms including cramping, bloating, gas, diarrhea or constipation, and mucus in stool."
            }
        ]
    
    def _extract_training_data(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract training data from the loaded JSON data"""
        training_data = []
        
        # Add causes
        for cause in data.get('causes', []):
            training_data.append({
                "question": f"What causes {cause.get('condition', '').lower()}?",
                "answer": cause.get('description', '')
            })
        
        # Add emergency symptoms
        emergency_symptoms = data.get('emergency_symptoms', [])
        if emergency_symptoms:
            training_data.append({
                "question": "When should I seek emergency medical attention for abdominal pain?",
                "answer": "Seek emergency care for: " + ", ".join(emergency_symptoms)
            })
        
        # Add home remedies
        home_remedies = data.get('home_remedies', [])
        if home_remedies:
            remedies_text = []
            for remedy in home_remedies:
                remedies_text.append(f"{remedy.get('remedy', '')}: {remedy.get('description', '')}")
            
            training_data.append({
                "question": "What home remedies help with abdominal pain?",
                "answer": "Home remedies include: " + "; ".join(remedies_text)
            })
        
        return training_data
    
    def fine_tune(self, epochs=3, batch_size=16, learning_rate=2e-5):
        """Fine-tune the model"""
        print("Preparing training data...")
        train_examples = self.prepare_training_data()
        
        if not train_examples:
            print("No training data available!")
            return
        
        # Split into train and validation sets
        train_examples, val_examples = train_test_split(
            train_examples, test_size=0.2, random_state=42
        )
        
        print(f"Training examples: {len(train_examples)}")
        print(f"Validation examples: {len(val_examples)}")
        
        # Create data loaders
        train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=batch_size)
        val_dataloader = DataLoader(val_examples, shuffle=False, batch_size=batch_size)
        
        # Define loss function
        train_loss = losses.CosineSimilarityLoss(self.model)
        
        # Fine-tune the model
        print("Starting fine-tuning...")
        self.model.fit(
            train_objectives=[(train_dataloader, train_loss)],
            epochs=epochs,
            warmup_steps=100,
            optimizer_params={'lr': learning_rate},
            show_progress_bar=True
        )
        
        # Save the fine-tuned model
        self.save_model()
        
        print("Fine-tuning completed!")
    
    def save_model(self, model_path=None):
        """Save the fine-tuned model"""
        if model_path is None:
            model_dir = os.path.join(os.path.dirname(__file__), 'models')
            os.makedirs(model_dir, exist_ok=True)
            model_path = os.path.join(model_dir, 'fine_tuned_symptom_checker')
        
        self.model.save(model_path)
        print(f"Model saved to {model_path}")
    
    def load_model(self, model_path=None):
        """Load a fine-tuned model"""
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), 'models', 'fine_tuned_symptom_checker')
        
        if os.path.exists(model_path):
            self.model = SentenceTransformer(model_path)
            self.model.to(self.device)
            print(f"Model loaded from {model_path}")
        else:
            print(f"No fine-tuned model found at {model_path}")
    
    def evaluate_model(self, test_questions: List[str], expected_answers: List[str]) -> float:
        """Evaluate the model performance"""
        if len(test_questions) != len(expected_answers):
            raise ValueError("Number of questions and answers must match")
        
        # Encode questions and answers
        question_embeddings = self.model.encode(test_questions)
        answer_embeddings = self.model.encode(expected_answers)
        
        # Calculate cosine similarities
        similarities = []
        for i in range(len(test_questions)):
            similarity = np.dot(question_embeddings[i], answer_embeddings[i]) / (
                np.linalg.norm(question_embeddings[i]) * np.linalg.norm(answer_embeddings[i])
            )
            similarities.append(similarity)
        
        return np.mean(similarities)

def main():
    """Main function to run fine-tuning"""
    fine_tuner = FineTuner()
    
    # Run fine-tuning
    fine_tuner.fine_tune(epochs=3, batch_size=8, learning_rate=2e-5)
    
    # Test the model
    test_questions = [
        "What causes abdominal pain?",
        "When should I see a doctor?",
        "What home remedies help?"
    ]
    
    expected_answers = [
        "Abdominal pain can be caused by various factors including indigestion, food poisoning, and other conditions.",
        "Seek medical attention for severe pain, fever, or other concerning symptoms.",
        "Home remedies include rest, heat therapy, and hydration."
    ]
    
    accuracy = fine_tuner.evaluate_model(test_questions, expected_answers)
    print(f"Model evaluation accuracy: {accuracy:.4f}")

if __name__ == "__main__":
    main()
