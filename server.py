#!/usr/bin/env python3
"""
GitHub AI Code Reviewer - Python Implementation
"""

import os
import hmac
import hashlib
import json
import requests
from flask import Flask, request, jsonify
from github import Github
from github import Auth
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def verify_signature(payload_body, signature_header):
    """Verify that the payload was sent from GitHub by validating SHA256."""
    if not signature_header:
        return False
    
    hash_object = hmac.new(
        os.environ.get('WEBHOOK_SECRET', '').encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    
    return hmac.compare_digest(expected_signature, signature_header)

def get_github_client(installation_id):
    """Create authenticated GitHub client for the installation."""
    # Read private key
    with open('private-key.pem', 'r') as key_file:
        private_key = key_file.read()
    
    # Create GitHub App authentication
    auth = Auth.AppAuth(
        app_id=os.environ.get('GITHUB_APP_ID'),
        private_key=private_key
    )
    
    # Get installation access token
    gi = Github(auth=auth)
    installation = gi.get_app().get_installation(installation_id)
    
    # Create client with installation token
    auth_token = Auth.AppInstallationAuth(
        app_id=os.environ.get('GITHUB_APP_ID'),
        private_key=private_key,
        installation_id=installation_id
    )
    
    return Github(auth=auth_token)

async def review_with_gemini(content, filename):
    """Send code to Gemini for review."""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return "Error: Gemini API key not configured"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"
    
    prompt = f"""
    Please review this {filename} file for:
    1. Code quality and best practices
    2. Potential bugs or security issues
    3. Performance improvements
    4. Code style and readability
    
    If you find issues, start your response with "ISSUES FOUND:" and list them.
    If the code looks good, start with "CODE LOOKS GOOD:"
    
    Code to review:
    ```
    {content}
    ```
    """
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    
    try:
        response = requests.post(
            url,
            headers={'Content-Type': 'application/json'},
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        if 'candidates' in result and len(result['candidates']) > 0:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return "Error: No response from Gemini"
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Gemini API: {e}")
        return f"Error calling Gemini API: {str(e)}"

def should_review_file(filename):
    """Check if file should be reviewed based on extension."""
    reviewable_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.rb']
    return any(filename.endswith(ext) for ext in reviewable_extensions)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle GitHub webhook events."""
    # Verify signature
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_signature(request.data, signature):
        logger.warning("Invalid signature")
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Parse payload
    payload = request.json
    event_type = request.headers.get('X-GitHub-Event')
    
    logger.info(f"Received {event_type} event")
    
    # Only handle pull request events
    if event_type != 'pull_request':
        return jsonify({'message': 'Event ignored'}), 200
    
    action = payload.get('action')
    if action not in ['opened', 'synchronize']:
        return jsonify({'message': 'Action ignored'}), 200
    
    try:
        # Extract data from payload
        pull_request = payload['pull_request']
        repository = payload['repository']
        installation_id = payload['installation']['id']
        
        logger.info(f"Processing PR #{pull_request['number']} in {repository['full_name']}")
        
        # Get GitHub client
        github_client = get_github_client(installation_id)
        repo = github_client.get_repo(repository['full_name'])
        pr = repo.get_pull(pull_request['number'])
        
        # Get changed files
        files = pr.get_files()
        issues = []
        
        for file in files:
            if should_review_file(file.filename):
                logger.info(f"Reviewing file: {file.filename}")
                
                try:
                    # Get file content
                    file_content = repo.get_contents(file.filename, ref=pull_request['head']['sha'])
                    content = file_content.decoded_content.decode('utf-8')
                    
                    # Review with Gemini
                    review = review_with_gemini(content, file.filename)
                    
                    if review.startswith('ISSUES FOUND:'):
                        issues.append(f"## 🔍 {file.filename}\n{review}")
                        
                except Exception as e:
                    logger.error(f"Error reviewing {file.filename}: {e}")
                    issues.append(f"## ❌ {file.filename}\nError reviewing file: {str(e)}")
        
        # Post review comment if issues found
        if issues:
            comment_body = f"""## 🤖 AI Code Review

{chr(10).join(issues)}

---
*Automated review powered by Gemini AI - Please address issues before human review*
"""
            pr.create_issue_comment(comment_body)
            logger.info(f"Posted review comment with {len(issues)} issues")
        else:
            # Post positive comment
            pr.create_issue_comment("""## 🤖 AI Code Review

✅ **Code looks good!** No major issues found.

---
*Automated review powered by Gemini AI*
""")
            logger.info("Posted positive review comment")
            
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({'error': str(e)}), 500
    
    return jsonify({'message': 'Success'}), 200

@app.route('/')
def home():
    """Health check endpoint."""
    return "🤖 AI Code Reviewer is running!"

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'github-ai-reviewer'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
