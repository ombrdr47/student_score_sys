# Deployment Guide - Communication Skills Scoring Tool

## 📋 Table of Contents
1. [Local Development Setup](#local-development-setup)
2. [Testing Locally](#testing-locally)
3. [Cloud Deployment Options](#cloud-deployment-options)
4. [Production Configuration](#production-configuration)

---

##  Local Development Setup

### Prerequisites Check
Before starting, ensure you have:
- **Python 3.8+**: Run `python3 --version`
- **pip**: Run `pip --version`
- **Git**: Run `git --version`
- **Java** (for LanguageTool): Run `java --version`

If Java is missing:
```bash
# macOS
brew install openjdk@11

# Ubuntu/Debian
sudo apt-get install openjdk-11-jre

# Windows
# Download from https://www.oracle.com/java/technologies/downloads/
```

### Step-by-Step Local Setup

#### 1. Create Project Directory
```bash
cd ~
mkdir communication-scorer
cd communication-scorer
```

#### 2. Clone or Copy Files
If from GitHub:
```bash
git clone <your-repository-url> .
```

Or manually create files:
- `app.py` (main application)
- `requirements.txt` (dependencies)
- `templates/index.html` (frontend)
- `README.md` (documentation)

#### 3. Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

#### 4. Install Dependencies
```bash
# Upgrade pip first
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

**Expected Installation Time**: 5-10 minutes (downloads models)

**Installation Output**: You should see:
```
Installing collected packages: flask, flask-cors, sentence-transformers, language-tool-python...
Successfully installed...
```

#### 5. Verify Installation
```bash
# Check if packages are installed
pip list | grep -E "flask|sentence|language-tool|vader"
```

Expected output:
```
Flask                     3.0.0
flask-cors                4.0.0
language-tool-python      2.7.1
sentence-transformers     2.2.2
vaderSentiment            3.3.2
```

---

##  Testing Locally

### 1. Start the Server
```bash
# Make sure virtual environment is activated
python app.py
```

**Expected Output**:
```
Starting Communication Scoring API...
Semantic model loaded: True
Grammar tool loaded: True
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
```

**Troubleshooting**:
- If port 5000 is busy: `lsof -ti:5000 | xargs kill -9`
- If models fail to load: Check internet connection (first run downloads models)

### 2. Test the Web Interface

#### Open Browser
```bash
# macOS
open http://localhost:5000

# Linux
xdg-open http://localhost:5000

# Windows
start http://localhost:5000
```

#### Manual Testing Steps
1. **Load Sample Data**:
   - Click "Load Sample" button
   - Verify sample transcript appears in text area
   - Duration field shows "52"

2. **Score the Transcript**:
   - Click "Score Transcript" button
   - Wait for processing (5-10 seconds first time)
   - Results should show overall score around 86/100

3. **Verify Each Criterion**:
   - Content & Structure: ~29-30/40
   - Speech Rate: 10/10
   - Language & Grammar: 16-20/20
   - Clarity: 15/15
   - Engagement: 12-15/15

### 3. Test the API Directly

#### Test Health Endpoint
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "semantic_model_loaded": true,
  "grammar_tool_loaded": true
}
```

#### Test Score Endpoint
```bash
curl -X POST http://localhost:5000/api/score \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Hello everyone, myself John, studying in class 8th. I am 13 years old.",
    "duration_sec": 10
  }'
```

Expected response (JSON with scores and criteria details)

### 4. Test with Custom Transcript
Create a test file `test_transcript.json`:
```json
{
  "transcript": "Good morning everyone. I am excited to introduce myself. My name is Sarah, and I am 14 years old. I study in class 9th at Green Valley School. I live with my parents and younger brother. My family is very supportive. I love playing basketball and reading books. My dream is to become a scientist. Thank you for listening.",
  "duration_sec": 30
}
```

Test it:
```bash
curl -X POST http://localhost:5000/api/score \
  -H "Content-Type: application/json" \
  -d @test_transcript.json
```

---

##  Cloud Deployment Options

### Option 1: Heroku (Easiest)

#### Prerequisites
```bash
# Install Heroku CLI
# macOS
brew tap heroku/brew && brew install heroku

# Ubuntu
curl https://cli-assets.heroku.com/install.sh | sh
```

#### Deployment Steps

1. **Create Procfile**
```bash
echo "web: gunicorn app:app" > Procfile
```

2. **Update requirements.txt**
```bash
echo "gunicorn==21.2.0" >> requirements.txt
```

3. **Create Heroku App**
```bash
heroku login
heroku create your-app-name
```

4. **Deploy**
```bash
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

5. **Open App**
```bash
heroku open
```

**Notes**:
- Free tier sleeps after 30 min inactivity
- First request after sleep takes 10-15 seconds
- 550 free dyno hours/month

---

### Option 2: AWS EC2 (More Control)

#### Launch EC2 Instance

1. **Go to AWS Console** → EC2 → Launch Instance
2. **Select**: Ubuntu Server 22.04 LTS (Free tier eligible)
3. **Instance Type**: t2.micro (1 GB RAM)
4. **Create Key Pair**: Save .pem file securely
5. **Security Group**: Allow ports 22 (SSH), 80 (HTTP), 5000 (Custom)
6. **Launch** instance

#### Connect to Instance
```bash
# Change key permissions
chmod 400 your-key.pem

# Connect via SSH
ssh -i your-key.pem ubuntu@your-instance-public-ip
```

#### Setup on EC2
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python, pip, git
sudo apt install python3 python3-pip python3-venv git openjdk-11-jre -y

# Clone repository
git clone <your-repo-url>
cd Assignment

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test run
python app.py
```

#### Run in Background
```bash
# Install screen
sudo apt install screen -y

# Start screen session
screen -S scorer

# Run app
python app.py

# Detach: Press Ctrl+A, then D
# Reattach: screen -r scorer
```

#### Setup with Nginx (Production)
```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx config
sudo nano /etc/nginx/sites-available/scorer
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/scorer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Setup with Gunicorn
```bash
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Create systemd service `/etc/systemd/system/scorer.service`:
```ini
[Unit]
Description=Communication Scorer
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/Assignment
Environment="PATH=/home/ubuntu/Assignment/venv/bin"
ExecStart=/home/ubuntu/Assignment/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl enable scorer
sudo systemctl start scorer
sudo systemctl status scorer
```

---

### Option 3: Render (Simplest)

1. **Sign up** at [render.com](https://render.com)
2. **New Web Service** → Connect GitHub repo
3. **Configure**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment**: Python 3
4. **Deploy** (automatic)

Access at: `https://your-app-name.onrender.com`

---

### Option 4: Railway

1. **Sign up** at [railway.app](https://railway.app)
2. **New Project** → Deploy from GitHub
3. Railway auto-detects Python
4. **Add** `gunicorn` to requirements.txt
5. **Deploy** automatically

---

##  Production Configuration

### 1. Update app.py for Production

Change the last line from:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

To:
```python
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False') == 'True'
    app.run(debug=debug, host='0.0.0.0', port=port)
```

### 2. Environment Variables

Create `.env` file (for local testing):
```bash
DEBUG=False
PORT=5000
FLASK_ENV=production
```

### 3. Add `.gitignore`
```bash
cat > .gitignore << EOF
venv/
__pycache__/
*.pyc
.env
*.log
.DS_Store
EOF
```

### 4. Security Headers (Optional)

Add to app.py after `app = Flask(__name__)`:
```python
from flask import Flask
from flask_talisman import Talisman

app = Flask(__name__)
Talisman(app, content_security_policy=None)
```

Install: `pip install flask-talisman`

---

##  Monitoring & Logs

### View Logs

#### Local
```bash
# Terminal where app is running shows live logs
```

#### Heroku
```bash
heroku logs --tail
```

#### AWS EC2
```bash
# If using screen
screen -r scorer

# If using systemd
sudo journalctl -u scorer -f
```

### Health Monitoring

Add to crontab for periodic health checks:
```bash
crontab -e
```

Add:
```
*/5 * * * * curl http://localhost:5000/api/health || echo "App down" | mail -s "Alert" your@email.com
```

---

##  Common Issues & Solutions

### Issue 1: Port Already in Use
```bash
# Find process
lsof -ti:5000

# Kill it
lsof -ti:5000 | xargs kill -9
```

### Issue 2: LanguageTool Fails
```bash
# Check Java
java -version

# Install if missing
sudo apt install openjdk-11-jre
```

### Issue 3: Out of Memory
```bash
# Use smaller model or CPU-only torch
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Issue 4: Slow Response
- First request downloads models (10-15 sec)
- Subsequent requests: 2-5 seconds
- Consider model caching or smaller models

---

##  Deployment Checklist

- [ ] Virtual environment created and activated
- [ ] All dependencies installed
- [ ] Java installed (for LanguageTool)
- [ ] App runs locally without errors
- [ ] Sample transcript scores correctly (~86)
- [ ] API endpoints tested
- [ ] Production settings configured
- [ ] Security headers added
- [ ] Logs accessible
- [ ] Health check endpoint working
- [ ] .gitignore configured
- [ ] README.md complete
- [ ] Deployed to cloud (if required)
- [ ] Domain configured (if applicable)
- [ ] SSL certificate setup (for HTTPS)

---

## 📞 Support

For deployment issues:
1. Check logs for error messages
2. Verify all prerequisites installed
3. Test API endpoints individually
4. Review this guide's troubleshooting section

---

**Last Updated**: November 2025
