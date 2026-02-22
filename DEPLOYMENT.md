# InsightX Deployment Guide

## Problem: "API Down" on Streamlit Cloud

When you deploy the Streamlit app to Streamlit Cloud but the FastAPI backend is still running locally, the app shows "API Down" because Streamlit Cloud cannot reach `http://localhost:8000`.

**Solution**: Deploy the FastAPI backend to a public server (cloud platform).

## Step 1: Deploy FastAPI Backend

Choose one of the following platforms:

### Option A: Heroku (Free tier available)

1. **Create Heroku Account** and install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

2. **Create Procfile** in project root:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

3. **Initialize Git Repository** (if not already done):
```bash
git init
git add .
git commit -m "Initial commit"
```

4. **Deploy to Heroku**:
```bash
heroku login
heroku create insightx-api
git push heroku main
# View logs
heroku logs --tail
```

5. **Your API URL**: `https://insightx-api.herokuapp.com`

### Option B: Railway (Recommended - Easier)

1. **Go to [railway.app](https://railway.app)**

2. **Connect GitHub repository** and authorize Railway

3. **Create new project from GitHub repo**

4. **Railway will auto-detect** FastAPI and deploy

5. **Set environment variables**:
   - `Python_VERSION = 3.10`
   - `DATABASE_URL = sqlite:///./insightx_db.db`

6. **Your API URL**: Available in Railway dashboard

### Option C: PythonAnywhere

1. **Sign up at [pythonanywhere.com](https://www.pythonanywhere.com/)**

2. **Upload your code** via Web interface or Git

3. **Create WSGI file** pointing to `main:app`

4. **Reload web app**

5. **Your API URL**: `https://yourusername.pythonanywhere.com`

## Step 2: Configure Streamlit Cloud

### Method 1: Using Secrets (Recommended)

1. **In Streamlit Cloud dashboard**, go to your app settings

2. **Click "Secrets"** in the left sidebar

3. **Paste your API configuration**:
```toml
api_url = "https://your-deployed-api-domain.com"
```

4. **Save and redeploy**

### Method 2: Using Environment Variables

1. **Create `secrets.toml` locally** (for local testing):
```bash
mkdir -p .streamlit
echo 'api_url = "https://your-api-domain.com"' > .streamlit/secrets.toml
```

2. **Push to GitHub** (but add to `.gitignore` for production secrets)

3. **Streamlit Cloud will use this** when deploying

## Step 3: Verify Deployment

1. **Check API is running**:
```bash
curl https://your-api-url/api/health
# Should return 200 OK
```

2. **Open your Streamlit Cloud app**

3. **You should see** "✓ API Connected" in the top right

## Quick Reference: API Endpoint Configuration

| Environment | Command | API URL Location |
|-------------|---------|------------------|
| **Local** | `python main.py` | `http://localhost:8000` |
| **Docker** | `docker run ...` | `http://docker-host:8000` |
| **Heroku** | Auto | `https://app-name.herokuapp.com` |
| **Railway** | Auto | `https://app-name.railway.app` |
| **AWS** | Manual | `https://your-ec2-instance` |
| **Docker Hub** | Pull & run | `https://docker-registry` |

## Troubleshooting

### Still seeing "API Down"?

1. **Verify API is deployed**:
```bash
curl -v https://your-deployed-api-url/api/health
```

2. **Check Streamlit secrets** are set correctly:
   - Dashboard → App → Secrets → Verify `api_url`

3. **Check CORS is enabled** in `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

4. **Review deployment logs**:
   - Heroku: `heroku logs --tail`
   - Railway: Dashboard → Deployments → View logs
   - PythonAnywhere: Web app → Error log

### Database Issues on Cloud

If you see database errors after deployment:

1. **Generate fresh data**:
```bash
python -m src.database.data_loader
```

2. **Commit database to repo** (optional):
```bash
git add insightx_db.db
git commit -m "Add database"
git push
```

OR

3. **Auto-initialize on cloud** (in `main.py`):
```python
@app.on_event("startup")
async def startup_event():
    init_db()  # Creates database automatically
```

## Security Notes

🔒 **Important**: 

- Never commit `.env` files with real API keys
- Use cloud platform's secrets/environment variables
- For production, use environment variables instead of `secrets.toml`
- Update `allow_origins` in CORS if you lock down access

## What's Next?

After deployment:

1. ✅ Your Streamlit Cloud app connects to cloud API
2. ✅ Both frontend and backend are publicly accessible
3. 🎯 Share the Streamlit URL with users
4. 📊 Monitor API logs for issues

For questions or issues, check the logs on your deployed platform.
