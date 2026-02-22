# Quick Fix: "API Down" on Streamlit Cloud

## What's Happening?
Your Streamlit Cloud app is deployed, but it's trying to connect to `http://localhost:8000` - which doesn't exist in the cloud. Your FastAPI backend isn't publicly accessible.

## Quick Solution (3 Steps)

### 1️⃣ Deploy the FastAPI Backend

Choose ONE of these (fastest to slowest):

**🚀 Railway (Recommended - Takes 2 minutes)**
- Go to https://railway.app
- Click "New Project" → "Deploy from GitHub"
- Select your repo → Railway auto-deploys
- Your API URL: `https://[project-name].railway.app`

**🔵 Heroku (Takes 5 minutes)**
```bash
heroku login
heroku create insightx-api
git push heroku main
```
- Your API URL: `https://insightx-api.herokuapp.com`

**☁️ PythonAnywhere (Takes 10 minutes)**
- Sign up at https://www.pythonanywhere.com
- Upload code → Configure web app
- Your API URL: `https://yourusername.pythonanywhere.com`

### 2️⃣ Add API URL to Streamlit Cloud Secrets

1. Go to **Streamlit Cloud Dashboard**
2. Click your app → **Settings** (⚙️)
3. Click **Secrets** in sidebar
4. Paste:
```toml
api_url = "https://YOUR-API-DOMAIN"
```
5. Save

Replace `YOUR-API-DOMAIN` with your deployed API URL from Step 1

### 3️⃣ Redeploy Your Streamlit App

Streamlit Cloud auto-redeploys when you push to GitHub:
```bash
git add .
git commit -m "Add API URL configuration"
git push
```

## Verify It Works

After redeploy, open your Streamlit app. You should see:
- ✅ "✓ API Connected" (top right) - Success!
- ❌ "✗ API Down" - Check your API URL in Secrets

## Testing API Health

Can't wait? Test your API directly:
```bash
curl https://YOUR-API-DOMAIN/api/health
```

Should return HTTP 200 with success message.

## Did I Miss Something?

Check [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Detailed deployment steps
- Troubleshooting
- Security notes
- Database setup for cloud

---

**Need Help?**
- Check deployment logs on your platform
- Verify API URL is correct (no typos, has https://)
- Make sure API and Streamlit are deployed (not running locally)
