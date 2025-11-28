# Deployment Guide

## Option 1: Render (Recommended - Easiest)

### Step 1: Prepare for Deployment

1. **Update main.py** to use PORT from environment:
```python
import os
port = int(os.environ.get("PORT", 8000))
uvicorn.run("src.api.main:app", host="0.0.0.0", port=port)
```

2. **Create Procfile** (for Render):
```
web: python main.py
```

### Step 2: Deploy on Render

1. Go to [render.com](https://render.com) and sign up/login (free with GitHub)

2. Click **"New +"** → **"Web Service"**

3. Connect your GitHub repository:
   - Select **"Public Git repository"**
   - Paste: `https://github.com/rishi02102017/Tradl-AI-Hackathon`
   - Click **"Connect"**

4. Configure the service:
   - **Name**: `financial-news-intelligence` (or any name)
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && python -m spacy download en_core_web_sm
     ```
   - **Start Command**: 
     ```bash
     python main.py
     ```
   - **Plan**: Select **"Free"**

5. **Environment Variables** (optional):
   - `DATABASE_URL`: `sqlite:///./financial_news.db`
   - `PORT`: `8000` (Render sets this automatically)

6. Click **"Create Web Service"**

7. Wait for deployment (5-10 minutes first time)

8. Your API will be live at: `https://your-app-name.onrender.com`

### Step 3: Deploy Frontend (Static Site)

1. In Render dashboard, click **"New +"** → **"Static Site"**

2. Connect same repository

3. Configure:
   - **Name**: `financial-news-dashboard`
   - **Build Command**: (leave empty)
   - **Publish Directory**: `/` (root)
   - **Static Files**: Select `demo_dashboard.html` and `demo_web.html`

4. **Important**: Update HTML files to use your API URL:
   - Change `const API_URL = 'http://localhost:8000'` 
   - To: `const API_URL = 'https://your-api-name.onrender.com'`

5. Click **"Create Static Site"**

6. Your dashboard will be live at: `https://your-dashboard-name.onrender.com`

---

## Option 2: Railway (Alternative)

### Step 1: Sign up
- Go to [railway.app](https://railway.app)
- Sign up with GitHub

### Step 2: Deploy
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Select your repository
4. Railway auto-detects Python
5. Add environment variable: `PORT=8000`
6. Deploy!

Railway will give you a URL like: `https://your-app.railway.app`

---

## Option 3: Fly.io (Best Performance)

### Step 1: Install Fly CLI
```bash
curl -L https://fly.io/install.sh | sh
```

### Step 2: Login
```bash
fly auth login
```

### Step 3: Create fly.toml
```toml
app = "financial-news-intelligence"
primary_region = "iad"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8080"

[[services]]
  internal_port = 8080
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]
    force_https = true

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
```

### Step 4: Deploy
```bash
fly deploy
```

---

## Quick Fixes Needed

### 1. Update main.py for production:
```python
import os
import uvicorn

if __name__ == "__main__":
    from src.database.init_db import init_database
    init_database()
    
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=port,
        reload=False  # Disable reload in production
    )
```

### 2. Update HTML files to use production URL:
In both `demo_dashboard.html` and `demo_web.html`, change:
```javascript
const API_URL = 'http://localhost:8000';
```
To:
```javascript
const API_URL = 'https://your-api-url.onrender.com';
```

### 3. CORS might need adjustment:
In `src/api/main.py`, make sure CORS allows your frontend domain:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Recommended: Render (Easiest)

**Pros:**
- Free tier available
- Easy GitHub integration
- Auto-deploys on push
- Supports both backend and static sites
- Good documentation

**Cons:**
- Free tier spins down after 15 min inactivity
- First request after spin-down is slow (~30s)

**Best for:** Hackathon demos, quick deployment

---

## After Deployment

1. Test your API: `https://your-api.onrender.com/`
2. Test your dashboard: `https://your-dashboard.onrender.com`
3. Update README with live URLs
4. Share with hackathon judges!

