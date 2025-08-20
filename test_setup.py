#!/usr/bin/env python3
"""
Test script to verify the Symptom Checker Chatbot setup
"""

import os
import sys
import json
import requests
import subprocess
from pathlib import Path

def test_backend_imports():
    """Test if backend modules can be imported"""
    print("Testing backend imports...")
    
    try:
        sys.path.append('backend')
        from chatbot import SymptomCheckerBot
        print("✅ Chatbot module imported successfully")
        
        # Test chatbot initialization
        bot = SymptomCheckerBot()
        print("✅ Chatbot initialized successfully")
        
        # Test basic response
        response = bot.get_response("Hello")
        print(f"✅ Basic response test: {response[:50]}...")
        
        return True
    except Exception as e:
        print(f"❌ Backend import test failed: {e}")
        return False

def test_data_files():
    """Test if data files exist"""
    print("Testing data files...")
    
    data_dir = Path("backend/data")
    if not data_dir.exists():
        print("❌ Data directory does not exist")
        return False
    
    # Check if data file exists (will be created by scraper)
    data_file = data_dir / "abdominal_pain_data.json"
    if data_file.exists():
        print("✅ Data file exists")
        return True
    else:
        print("⚠️  Data file not found (will be created during setup)")
        return True

def test_frontend_files():
    """Test if frontend files exist"""
    print("Testing frontend files...")
    
    required_files = [
        "frontend/package.json",
        "frontend/src/App.tsx",
        "frontend/src/main.tsx",
        "frontend/vite.config.ts"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            return False
    
    return True

def test_flask_server():
    """Test if Flask server can start"""
    print("Testing Flask server...")
    
    try:
        # Start Flask server in background
        process = subprocess.Popen(
            [sys.executable, "backend/app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit for server to start
        import time
        time.sleep(3)
        
        # Test health endpoint
        try:
            response = requests.get("http://localhost:5000/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Flask server is running and responding")
                process.terminate()
                return True
            else:
                print(f"❌ Flask server responded with status {response.status_code}")
                process.terminate()
                return False
        except requests.exceptions.RequestException:
            print("❌ Flask server is not responding")
            process.terminate()
            return False
            
    except Exception as e:
        print(f"❌ Flask server test failed: {e}")
        return False

def test_chat_endpoint():
    """Test the chat endpoint"""
    print("Testing chat endpoint...")
    
    try:
        response = requests.post(
            "http://localhost:5000/api/chat",
            json={"message": "What causes abdominal pain?"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "response" in data:
                print("✅ Chat endpoint working correctly")
                print(f"   Response: {data['response'][:100]}...")
                return True
            else:
                print("❌ Chat endpoint response missing 'response' field")
                return False
        else:
            print(f"❌ Chat endpoint returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Chat endpoint test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Running Symptom Checker Chatbot tests...")
    print("=" * 50)
    
    tests = [
        ("Backend Imports", test_backend_imports),
        ("Data Files", test_data_files),
        ("Frontend Files", test_frontend_files),
        ("Flask Server", test_flask_server),
        ("Chat Endpoint", test_chat_endpoint),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The setup is working correctly.")
        print("\nTo start using the application:")
        print("1. Start the backend: python backend/app.py")
        print("2. Start the frontend: cd frontend && npm run dev")
        print("3. Open http://localhost:3000 in your browser")
    else:
        print("❌ Some tests failed. Please check the setup.")
        sys.exit(1)

if __name__ == "__main__":
    main()
