# GitHub App Python Setup Guide (1-2 Hours)

## Phase 1: Setup (20 minutes)

```bash
# 1. Install ngrok
# Download from ngrok.com or use homebrew on macOS
brew install ngrok

# 2. Create project directory
mkdir github-ai-reviewer-python
cd github-ai-reviewer-python

# 3. Create virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate  # On Windows

# 4. Install dependencies
pip install flask PyGithub python-dotenv cryptography requests
```

## Phase 2: Create GitHub App (15 minutes)

Same as original guide:
1. Go to GitHub Settings → Developer settings → GitHub Apps → New GitHub App
2. Fill required fields:
   - Name: AI Code Reviewer (Dev)
   - Homepage URL: http://localhost:5000
   - Webhook URL: https://your-ngrok-url.ngrok.io/webhook
   - Webhook Secret: Generate a random string
3. Permissions: Contents (Read), Pull requests (Write), Metadata (Read)
4. Subscribe to events: Pull request
5. Download private key and save as private-key.pem

## Phase 3: Basic Server (30 minutes)

Create the main server file:
