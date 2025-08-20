# Symptom Checker Chatbot

An AI-powered medical assistant chatbot specifically trained to help with abdominal pain in adults. Built with Flask, React, TypeScript, and transformer-based AI models.

## Features

- 🤖 **AI-Powered Chatbot**: Fine-tuned transformer model for medical symptom analysis
- 🎯 **Specialized Focus**: Trained specifically for abdominal pain in adults
- 💬 **Natural Conversation**: Understands greetings and general questions
- 🚫 **Scope Awareness**: Clearly indicates when queries are outside its training scope
- 🏥 **Medical Information**: Provides causes, symptoms, and when to seek medical attention
- 🎨 **Modern UI**: Beautiful React TypeScript frontend with Tailwind CSS
- 🔧 **Fine-tuning**: Custom training pipeline for medical domain adaptation

## Technology Stack

### Backend
- **Framework**: Flask (Python)
- **AI/ML**: 
  - Sentence Transformers (all-MiniLM-L6-v2)
  - PyTorch
  - Scikit-learn
  - NLTK
- **Fine-tuning**: Custom transformer-based approach
- **Vector Database**: ChromaDB for embeddings

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Axios

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd symptom-checker
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```

   This will:
   - Install Python dependencies
   - Generate training data
   - Run fine-tuning
   - Install frontend dependencies

3. **Start the backend**
   ```bash
   python backend/app.py
   ```

4. **Start the frontend** (in a new terminal)
   ```bash
   cd frontend
   npm run dev
   ```

5. **Open your browser**
   Navigate to `http://localhost:3000`

## Manual Setup

If you prefer to set up manually:

### Backend Setup

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate training data**
   ```bash
   python backend/data_scraper.py
   ```

3. **Run fine-tuning**
   ```bash
   python backend/fine_tuning.py
   ```

4. **Start the Flask server**
   ```bash
   python backend/app.py
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

## Project Structure

```
symptom-checker/
├── backend/
│   ├── app.py                 # Flask application
│   ├── chatbot.py            # Main chatbot logic
│   ├── data_scraper.py       # Data collection from Mayo Clinic
│   ├── fine_tuning.py        # Model fine-tuning pipeline
│   ├── data/                 # Training data and knowledge base
│   └── models/               # Fine-tuned models
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── types/           # TypeScript type definitions
│   │   ├── App.tsx          # Main app component
│   │   └── main.tsx         # Entry point
│   ├── package.json         # Frontend dependencies
│   └── vite.config.ts       # Vite configuration
├── requirements.txt          # Python dependencies
├── setup.py                 # Setup script
└── README.md               # This file
```

## AI Model Details

### Fine-tuning Approach

The chatbot uses a transformer-based approach with the following components:

1. **Base Model**: Sentence Transformers (all-MiniLM-L6-v2)
2. **Fine-tuning**: Custom training on abdominal pain data
3. **Embeddings**: 384-dimensional sentence embeddings
4. **Similarity**: Cosine similarity for response matching

### Training Data

The model is trained on comprehensive abdominal pain data including:
- Common causes (indigestion, food poisoning, IBS, etc.)
- Associated symptoms
- Emergency indicators
- Home remedies
- Prevention strategies

### Scope Management

The chatbot is designed to:
- ✅ Answer questions about abdominal pain
- ✅ Respond to general greetings
- ✅ Provide medical information within its scope
- ❌ Clearly indicate when queries are outside its training scope

## API Endpoints

### POST /api/chat
Send a message to the chatbot.

**Request:**
```json
{
  "message": "What causes abdominal pain?"
}
```

**Response:**
```json
{
  "response": "Abdominal pain in adults can be caused by various factors including..."
}
```

### GET /api/health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "message": "Symptom Checker Bot is running"
}
```

## Development

### Running Tests
```bash
# Backend tests
python -m pytest backend/tests/

# Frontend tests
cd frontend
npm test
```

### Building for Production
```bash
# Frontend build
cd frontend
npm run build

# Backend (Flask is ready for production with proper WSGI server)
```

## Medical Disclaimer

⚠️ **Important**: This AI assistant is for informational purposes only and should not replace professional medical advice. 

- Always consult with a healthcare professional for medical concerns
- In emergency situations, call emergency services immediately
- The assistant is trained specifically for abdominal pain in adults
- Information provided is based on general medical knowledge

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Medical data inspired by Mayo Clinic symptom checker
- Built with modern AI/ML technologies
- Designed for educational and informational purposes
