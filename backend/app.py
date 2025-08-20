from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from chatbot import SymptomCheckerBot

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize the chatbot
chatbot = SymptomCheckerBot()

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        response = chatbot.get_response(user_message)
        return jsonify({'response': response})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Symptom Checker Bot is running'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
