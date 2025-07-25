# 🤖 GitHub AI Code Reviewer (Python)

An intelligent GitHub App that automatically reviews pull requests using Google's Gemini AI. Built with Python, Flask, and the GitHub API.

## ✨ Features

- 🔍 **Automatic Code Review**: Reviews code in pull requests using Gemini AI
- 🚀 **Real-time Processing**: Responds to PR events instantly via webhooks
- 🛡️ **Secure**: Proper webhook signature verification and GitHub App authentication
- ⚡ **Async Support**: Optional async version for better performance
- 🧪 **Local Testing**: Easy local development with ngrok
- 📦 **Easy Deployment**: Ready for Vercel, Heroku, or any Python hosting

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo>
cd github-ai-reviewer-python

# Run the setup script
python setup.py
```

### 2. Manual Setup (Alternative)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 3. Configure Environment

Edit `.env` file with your values:

```env
GITHUB_APP_ID=your_app_id_here
GITHUB_INSTALLATION_ID=your_installation_id_here
WEBHOOK_SECRET=your_webhook_secret_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. GitHub App Setup

1. Go to GitHub Settings → Developer settings → GitHub Apps → New GitHub App
2. Fill in the details:
   - **Name**: AI Code Reviewer (Dev)
   - **Homepage URL**: `http://localhost:5000`
   - **Webhook URL**: `https://your-ngrok-url.ngrok.io/webhook`
   - **Webhook Secret**: Generate a random string
3. **Permissions**:
   - Repository permissions:
     - Contents: Read
     - Pull requests: Write
     - Metadata: Read
4. **Subscribe to events**: Pull request
5. Download the private key and save as `private-key.pem`

### 5. Local Testing

```bash
# Terminal 1: Start ngrok
ngrok http 5000

# Terminal 2: Start the server
python server.py

# Or use the async version for better performance
python async_server.py
```

### 6. Test the Setup

1. Update your GitHub App webhook URL with the ngrok URL
2. Create a test pull request in a repository where the app is installed
3. Watch the magic happen! 🎉

## 📁 Project Structure

```
github-ai-reviewer-python/
├── server.py              # Main Flask server
├── async_server.py        # Async version with Quart
├── setup.py              # Setup script
├── test_server.py        # Unit tests
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
├── vercel.json          # Vercel deployment config
├── private-key.pem      # GitHub App private key (you add this)
└── README.md           # This file
```

## 🧪 Testing

```bash
# Run unit tests
python test_server.py

# Test health endpoint
curl http://localhost:5000/health

# Test webhook (with proper signature)
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: pull_request" \
  -d '{"action": "opened", "pull_request": {...}}'
```

## 🚀 Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# Set environment variables in Vercel dashboard
```

### Heroku

```bash
# Create Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set GITHUB_APP_ID=your_app_id
heroku config:set GITHUB_INSTALLATION_ID=your_installation_id
heroku config:set WEBHOOK_SECRET=your_webhook_secret
heroku config:set GEMINI_API_KEY=your_gemini_key

# Deploy
git push heroku main
```

### Docker

```bash
# Build image
docker build -t github-ai-reviewer .

# Run container
docker run -p 5000:5000 --env-file .env github-ai-reviewer
```

## 🔧 Configuration

### Supported File Types

The reviewer currently supports these file extensions:
- Python: `.py`
- JavaScript/TypeScript: `.js`, `.ts`, `.jsx`, `.tsx`
- Java: `.java`
- C/C++: `.c`, `.cpp`
- Go: `.go`
- Rust: `.rs`
- PHP: `.php`
- Ruby: `.rb`

### Customizing Reviews

Edit the `review_with_gemini()` function to customize the AI prompts:

```python
prompt = f"""
Please review this {filename} file for:
1. Code quality and best practices
2. Potential bugs or security issues
3. Performance improvements
4. Code style and readability

Your custom instructions here...
"""
```

## 🛡️ Security Features

- ✅ Webhook signature verification
- ✅ GitHub App authentication (more secure than personal tokens)
- ✅ Environment variable protection
- ✅ Input validation and sanitization
- ✅ Error handling and logging

## 📊 Performance

### Standard Version (`server.py`)
- Simple Flask implementation
- Synchronous processing
- Good for low-traffic scenarios

### Async Version (`async_server.py`)
- Uses Quart (async Flask)
- Concurrent file processing
- Better for high-traffic scenarios
- Faster response times

## 🐛 Troubleshooting

### Common Issues

1. **"Invalid signature" error**
   - Check your `WEBHOOK_SECRET` matches GitHub App settings
   - Ensure webhook URL is correct

2. **"Authentication failed" error**
   - Verify `GITHUB_APP_ID` and `GITHUB_INSTALLATION_ID`
   - Check `private-key.pem` file exists and is valid

3. **"Gemini API error"**
   - Verify `GEMINI_API_KEY` is correct
   - Check API quota and billing

4. **Webhook not receiving events**
   - Ensure ngrok is running and URL is updated in GitHub App
   - Check GitHub App is installed on the repository

### Debug Mode

```bash
# Enable debug logging
export FLASK_ENV=development
python server.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- GitHub API and PyGithub library
- Google Gemini AI
- Flask/Quart web frameworks
- ngrok for local development

---

**Happy coding!** 🚀 If you find this useful, please give it a ⭐!
