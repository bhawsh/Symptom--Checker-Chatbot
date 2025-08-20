#!/usr/bin/env python3
"""
Setup script for Symptom Checker Chatbot
"""

import os
import subprocess
import sys
import json

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, cwd=cwd)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e}")
        return None

def setup_backend():
    """Setup the Flask backend"""
    print("Setting up Flask backend...")
    
    # Create necessary directories
    os.makedirs("backend/data", exist_ok=True)
    os.makedirs("backend/models", exist_ok=True)
    
    # Install Python dependencies
    print("Installing Python dependencies...")
    if run_command("pip install -r requirements.txt") is None:
        print("Failed to install Python dependencies")
        return False
    
    # Generate training data
    print("Generating training data...")
    if run_command("python backend/data_scraper.py", cwd=".") is None:
        print("Failed to generate training data")
        return False
    
    # Run fine-tuning
    print("Running fine-tuning...")
    if run_command("python backend/fine_tuning.py", cwd=".") is None:
        print("Failed to run fine-tuning")
        return False
    
    print("Backend setup completed!")
    return True

def setup_frontend():
    """Setup the React frontend"""
    print("Setting up React frontend...")
    
    # Check if Node.js is installed
    if run_command("node --version") is None:
        print("Node.js is not installed. Please install Node.js first.")
        return False
    
    # Check if npm is installed
    if run_command("npm --version") is None:
        print("npm is not installed. Please install npm first.")
        return False
    
    # Install frontend dependencies
    print("Installing frontend dependencies...")
    if run_command("npm install", cwd="frontend") is None:
        print("Failed to install frontend dependencies")
        return False
    
    print("Frontend setup completed!")
    return True

def create_env_file():
    """Create .env file with necessary environment variables"""
    env_content = """# Flask Configuration
FLASK_APP=backend/app.py
FLASK_ENV=development

# AI Model Configuration
MODEL_NAME=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# Database Configuration (if needed)
# DATABASE_URL=sqlite:///symptom_checker.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("Created .env file")

def main():
    """Main setup function"""
    print("Setting up Symptom Checker Chatbot...")
    print("=" * 50)
    
    # Create .env file
    create_env_file()
    
    # Setup backend
    if not setup_backend():
        print("Backend setup failed!")
        sys.exit(1)
    
    # Setup frontend
    if not setup_frontend():
        print("Frontend setup failed!")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("\nTo run the application:")
    print("1. Start the backend: python backend/app.py")
    print("2. Start the frontend: cd frontend && npm run dev")
    print("3. Open http://localhost:3000 in your browser")
    print("\nThe backend will be available at http://localhost:5000")

if __name__ == "__main__":
    main()
