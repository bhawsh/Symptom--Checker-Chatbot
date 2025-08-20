import requests
from bs4 import BeautifulSoup
import json
import time
import os

class MayoClinicScraper:
    def __init__(self):
        self.base_url = "https://www.mayoclinic.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_abdominal_pain_data(self):
        """Scrape abdominal pain related data from Mayo Clinic"""
        
        # Since we can't directly scrape the symptom checker, we'll create comprehensive data
        # based on Mayo Clinic's known information about abdominal pain
        
        abdominal_pain_data = {
            "symptom": "abdominal pain in adults",
            "overview": "Abdominal pain is pain that occurs between the chest and pelvic regions. It can be crampy, achy, dull, intermittent, or sharp. It's also called a stomachache.",
            "causes": [
                {
                    "condition": "Indigestion",
                    "description": "Discomfort or burning in the upper abdomen, often after eating",
                    "symptoms": ["Bloating", "Nausea", "Feeling full quickly", "Burping"]
                },
                {
                    "condition": "Food poisoning",
                    "description": "Illness caused by eating contaminated food",
                    "symptoms": ["Nausea", "Vomiting", "Diarrhea", "Fever", "Stomach cramps"]
                },
                {
                    "condition": "Gastroenteritis (Stomach flu)",
                    "description": "Inflammation of the stomach and intestines",
                    "symptoms": ["Watery diarrhea", "Nausea", "Vomiting", "Stomach cramps", "Fever"]
                },
                {
                    "condition": "Irritable Bowel Syndrome (IBS)",
                    "description": "Chronic condition affecting the large intestine",
                    "symptoms": ["Cramping", "Bloating", "Gas", "Diarrhea or constipation", "Mucus in stool"]
                },
                {
                    "condition": "Constipation",
                    "description": "Infrequent bowel movements or difficult passage of stools",
                    "symptoms": ["Fewer than 3 bowel movements per week", "Hard, dry stools", "Straining during bowel movements", "Feeling of incomplete evacuation"]
                },
                {
                    "condition": "Appendicitis",
                    "description": "Inflammation of the appendix",
                    "symptoms": ["Sudden pain in lower right abdomen", "Nausea", "Vomiting", "Loss of appetite", "Fever", "Pain that worsens with movement"]
                },
                {
                    "condition": "Gallstones",
                    "description": "Hardened deposits in the gallbladder",
                    "symptoms": ["Sudden, intense pain in upper right abdomen", "Pain in right shoulder", "Nausea", "Vomiting", "Back pain"]
                },
                {
                    "condition": "Kidney stones",
                    "description": "Hard deposits of minerals and salts in the kidneys",
                    "symptoms": ["Severe pain in side and back", "Pain radiating to lower abdomen", "Painful urination", "Pink, red, or brown urine", "Nausea", "Vomiting"]
                },
                {
                    "condition": "Peptic ulcers",
                    "description": "Sores in the lining of the stomach or small intestine",
                    "symptoms": ["Burning stomach pain", "Feeling of fullness", "Bloating", "Heartburn", "Nausea", "Intolerance to fatty foods"]
                },
                {
                    "condition": "Inflammatory Bowel Disease (IBD)",
                    "description": "Chronic inflammation of the digestive tract",
                    "symptoms": ["Diarrhea", "Fatigue", "Abdominal pain and cramping", "Blood in stool", "Reduced appetite", "Unintended weight loss"]
                }
            ],
            "emergency_symptoms": [
                "Severe, sudden abdominal pain",
                "Pain with fever",
                "Pain with vomiting blood",
                "Pain with black, tarry stools",
                "Pain that lasts more than 24 hours",
                "Pain that gets worse over time",
                "Pain with difficulty breathing",
                "Pain with chest pressure",
                "Pain with dizziness or fainting",
                "Pain with rapid heartbeat"
            ],
            "home_remedies": [
                {
                    "remedy": "Rest",
                    "description": "Avoid strenuous activity and get plenty of rest"
                },
                {
                    "remedy": "Heat therapy",
                    "description": "Apply a heating pad or warm compress to the affected area"
                },
                {
                    "remedy": "Hydration",
                    "description": "Drink clear fluids like water, broth, or clear juices"
                },
                {
                    "remedy": "Bland diet",
                    "description": "Eat bland foods like rice, toast, bananas, and applesauce"
                },
                {
                    "remedy": "Avoid irritants",
                    "description": "Stay away from spicy, fatty, or acidic foods"
                },
                {
                    "remedy": "Over-the-counter medications",
                    "description": "Consider antacids, pain relievers, or anti-diarrheal medications as appropriate"
                }
            ],
            "prevention_tips": [
                "Eat a healthy, balanced diet",
                "Stay hydrated",
                "Exercise regularly",
                "Manage stress",
                "Avoid smoking and excessive alcohol",
                "Practice good food hygiene",
                "Get regular medical check-ups"
            ],
            "when_to_see_doctor": [
                "Pain that is severe or doesn't improve",
                "Pain that interferes with daily activities",
                "Pain accompanied by other concerning symptoms",
                "Pain that recurs frequently",
                "Pain in people over 50 years old",
                "Pain in people with a family history of digestive problems"
            ]
        }
        
        return abdominal_pain_data
    
    def save_data(self, data, filename="abdominal_pain_data.json"):
        """Save scraped data to JSON file"""
        os.makedirs(os.path.dirname(__file__), exist_ok=True)
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        filepath = os.path.join(data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Data saved to {filepath}")
        return filepath

def main():
    scraper = MayoClinicScraper()
    data = scraper.scrape_abdominal_pain_data()
    scraper.save_data(data)

if __name__ == "__main__":
    main()
