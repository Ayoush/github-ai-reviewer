#!/usr/bin/env python3
"""
Helper script to find your GitHub App Installation ID
"""

import os
import requests
import time
from dotenv import load_dotenv

# Handle JWT import properly
try:
    import jwt
except ImportError:
    print("❌ PyJWT not installed. Run: pip install PyJWT==2.8.0")
    exit(1)

load_dotenv()

def get_installation_id():
    """Find the installation ID for your GitHub App."""
    
    app_id = os.environ.get('GITHUB_APP_ID')
    if not app_id:
        print("❌ GITHUB_APP_ID not found in environment variables")
        print("💡 Make sure to set GITHUB_APP_ID in your .env file")
        return
    
    if not os.path.exists('private-key.pem'):
        print("❌ private-key.pem not found")
        print("💡 Download your GitHub App's private key and save it as 'private-key.pem'")
        return
    
    try:
        # Read private key
        with open('private-key.pem', 'r') as key_file:
            private_key = key_file.read()
        
        # Create JWT token for GitHub App authentication
        now = int(time.time())
        payload = {
            'iat': now - 60,  # Issued 1 minute ago (to account for clock skew)
            'exp': now + 600,  # Expires in 10 minutes
            'iss': int(app_id)
        }
        
        # Encode JWT token
        token = jwt.encode(payload, private_key, algorithm='RS256')
        
        # Ensure token is a string (PyJWT 2.x returns string, 1.x returns bytes)
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        
        print(f"🔑 Generated JWT token: {token[:50]}...")
        
        # Get installations
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHub-AI-Reviewer'
        }
        
        print("🌐 Fetching installations from GitHub API...")
        response = requests.get('https://api.github.com/app/installations', headers=headers)
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 401:
                print("\n🔧 Troubleshooting 401 Unauthorized:")
                print("1. Check that GITHUB_APP_ID is correct (should be just numbers)")
                print("2. Verify private-key.pem is the correct private key file")
                print("3. Make sure the private key matches your GitHub App")
                print("4. Check that your GitHub App exists and is active")
            
            return
        
        installations = response.json()
        
        if not installations:
            print("❌ No installations found for this GitHub App")
            print("💡 Make sure you've installed the app on at least one repository")
            print("📖 To install: Go to your GitHub App settings → Install App")
            return
        
        print("🎉 Found GitHub App installations:")
        print("=" * 50)
        
        for i, installation in enumerate(installations, 1):
            print(f"\n📦 Installation #{i}:")
            print(f"   ID: {installation['id']}")
            print(f"   Account: {installation['account']['login']}")
            print(f"   Type: {installation['account']['type']}")
            print(f"   URL: https://github.com/settings/installations/{installation['id']}")
            
            # Get repositories for this installation
            try:
                repo_headers = headers.copy()
                repo_response = requests.get(
                    f"https://api.github.com/app/installations/{installation['id']}/repositories",
                    headers=repo_headers
                )
                if repo_response.status_code == 200:
                    repos = repo_response.json()
                    print(f"   Repositories: {repos['total_count']}")
                    if repos['repositories']:
                        print("   Repository names:")
                        for repo in repos['repositories'][:3]:  # Show first 3
                            print(f"     - {repo['full_name']}")
                        if len(repos['repositories']) > 3:
                            print(f"     ... and {len(repos['repositories']) - 3} more")
            except:
                pass  # Skip if we can't get repo info
        
        if len(installations) == 1:
            installation_id = installations[0]['id']
            print(f"\n✅ Use this in your .env file:")
            print(f"GITHUB_INSTALLATION_ID={installation_id}")
            
            # Update .env file if it exists
            if os.path.exists('.env'):
                update_env = input("\n🔄 Update .env file automatically? (y/n): ").lower().strip()
                if update_env == 'y':
                    update_env_file(installation_id)
        else:
            print(f"\n💡 You have {len(installations)} installations.")
            print("Choose the installation ID for the repositories you want to review.")
            
    except jwt.InvalidKeyError:
        print("❌ Invalid private key format")
        print("💡 Make sure private-key.pem contains a valid RSA private key")
    except jwt.InvalidTokenError as e:
        print(f"❌ JWT Token Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure GITHUB_APP_ID is correct (numbers only)")
        print("2. Make sure private-key.pem is the correct private key")
        print("3. Make sure your GitHub App is installed on at least one repository")

def update_env_file(installation_id):
    """Update the .env file with the installation ID."""
    try:
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('GITHUB_INSTALLATION_ID='):
                lines[i] = f'GITHUB_INSTALLATION_ID={installation_id}\n'
                updated = True
                break
        
        if not updated:
            lines.append(f'GITHUB_INSTALLATION_ID={installation_id}\n')
        
        with open('.env', 'w') as f:
            f.writelines(lines)
        
        print("✅ Updated .env file with installation ID")
        
    except Exception as e:
        print(f"❌ Could not update .env file: {e}")

if __name__ == "__main__":
    print("🔍 Finding GitHub App Installation ID...")
    get_installation_id()
