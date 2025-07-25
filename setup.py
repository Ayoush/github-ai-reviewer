#!/usr/bin/env python3
"""
Setup script for GitHub AI Code Reviewer
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def main():
    """Main setup function."""
    print("🚀 Setting up GitHub AI Code Reviewer (Python)")
    print("=" * 50)
    
    # Check if we're in a virtual environment
    if sys.prefix == sys.base_prefix:
        print("⚠️  Warning: You're not in a virtual environment!")
        create_venv = input("Would you like to create one? (y/n): ").lower().strip()
        if create_venv == 'y':
            run_command("python -m venv venv", "Creating virtual environment")
            print("📝 Please activate the virtual environment:")
            print("   source venv/bin/activate  # On macOS/Linux")
            print("   venv\\Scripts\\activate     # On Windows")
            print("\nThen run this setup script again.")
            return
    
    # Install dependencies
    if run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("📦 All dependencies installed successfully")
    
    # Check for .env file
    if not os.path.exists('.env'):
        print("📝 Creating .env file from template...")
        if os.path.exists('.env.example'):
            run_command("cp .env.example .env", "Copying environment template")
            print("⚠️  Please edit .env file with your actual values:")
            print("   - GITHUB_APP_ID")
            print("   - GITHUB_INSTALLATION_ID") 
            print("   - WEBHOOK_SECRET")
            print("   - GEMINI_API_KEY")
        else:
            print("❌ .env.example not found!")
    
    # Check for private key
    if not os.path.exists('private-key.pem'):
        print("🔑 Please add your GitHub App private key as 'private-key.pem'")
    
    # Check if ngrok is installed
    ngrok_check = run_command("which ngrok", "Checking for ngrok")
    if not ngrok_check:
        print("📥 ngrok not found. Please install it:")
        print("   brew install ngrok  # On macOS")
        print("   Or download from https://ngrok.com/")
    
    print("\n🎉 Setup completed!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your configuration")
    print("2. Add private-key.pem from your GitHub App")
    print("3. Start ngrok: ngrok http 5000")
    print("4. Update your GitHub App webhook URL with ngrok URL")
    print("5. Run the server: python server.py")
    print("\n🧪 For testing:")
    print("   python -m pytest tests/  # Run tests")
    print("   curl http://localhost:5000/health  # Health check")

if __name__ == "__main__":
    main()
