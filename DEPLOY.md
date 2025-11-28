# 🚀 Deployment Guide - Render (Free)

## Quick Steps

### Part 1: Deploy Backend API

1. **Go to [render.com](https://render.com)**
   - Sign up with GitHub (free)

2. **Create New Web Service**
   - Click **"New +"** → **"Web Service"**
   - Connect repository: `rishi02102017/Tradl-AI-Hackathon`
   - Click **"Connect"**

3. **Configure Settings:**
   ```
   Name: financial-news-api
   Environment: Python 3
   Region: Singapore (or closest to you)
   Branch: main
   Root Directory: (leave empty)
   ```

4. **Build & Start Commands:**
   ```
   Build Command:
   pip install -r requirements.txt && python -m spacy download en_core_web_sm
   
   Start Command:
   python main.py
   ```

5. **Environment Variables:**
   - `PORT`: `8000` (Render sets this automatically, but add it)
   - `DATABASE_URL`: `sqlite:///./financial_news.db`

6. **Plan:** Select **"Free"**

7. **Click "Create Web Service"**

8. **Wait 5-10 minutes** for first deployment

9. **Copy your API URL** (e.g., `https://financial-news-api.onrender.com`)

---

### Part 2: Update Frontend Files

After you get your API URL, update the HTML files:

**In `demo_dashboard.html` (line ~721):**
```javascript
// Change this:
const API_URL = 'http://localhost:8000';

// To your Render URL:
const API_URL = 'https://your-api-name.onrender.com';
```

**In `demo_web.html` (line ~418):**
```javascript
// Change this:
const API_URL = 'http://localhost:8000';

// To your Render URL:
const API_URL = 'https://your-api-name.onrender.com';
```

**Then commit and push:**
```bash
git add demo_dashboard.html demo_web.html
git commit -m "Update API URLs for production"
git push
```

---

### Part 3: Deploy Frontend (Static Site)

1. **In Render Dashboard, click "New +" → "Static Site"**

2. **Connect same repository**

3. **Configure:**
   ```
   Name: financial-news-dashboard
   Branch: main
   Root Directory: (leave empty)
   Build Command: (leave empty)
   Publish Directory: /
   ```

4. **Click "Create Static Site"**

5. **Your dashboard will be live!**

---

## Alternative: Railway (Easier, but different)

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repo
5. Railway auto-detects everything!
6. Add env var: `PORT=8000`
7. Done! Get your URL

---

## Important Notes

⚠️ **Free Tier Limitations:**
- Render free tier spins down after 15 min inactivity
- First request after spin-down takes ~30 seconds
- For hackathon demos, this is fine!

✅ **Tips:**
- Keep the dashboard open during demo to prevent spin-down
- Or use Railway (no spin-down, but limited hours/month)

---

## Testing After Deployment

1. Test API: `https://your-api.onrender.com/`
2. Test query: `https://your-api.onrender.com/query?q=HDFC%20Bank%20news`
3. Test dashboard: `https://your-dashboard.onrender.com`

---

## Troubleshooting

**Build fails?**
- Check build logs in Render dashboard
- Make sure all dependencies are in requirements.txt

**API not responding?**
- Check if service is running (might be spinning up)
- Check logs in Render dashboard

**CORS errors?**
- Already configured in `src/api/main.py` with `allow_origins=["*"]`

**Database issues?**
- SQLite works on Render, but data resets on redeploy
- For production, consider PostgreSQL (Render has free tier)

---

## Update README After Deployment

Add to your README:

```markdown
## 🌐 Live Demo

- **API**: https://your-api.onrender.com
- **Dashboard**: https://your-dashboard.onrender.com
```

