# Railway Deployment - Quick Checklist

## ✅ What I Fixed

1. **Updated `main.py`** to properly handle Railway's `PORT` environment variable
2. **Added auto-data loading** on first startup (if database is empty)
3. **Created comprehensive troubleshooting guide** ([RAILWAY_TROUBLESHOOT.md](RAILWAY_TROUBLESHOOT.md))

## 🔍 Why "Deployment Successful" But Can't Access

**Most likely cause**: Your domain has underscores (`insightx_ai.railway.app`) but Railway converts them to hyphens.

**Your actual domain is probably**: `https://insightx-ai.railway.app/` (not `insightx_ai`)

## ⚡ Quick Fix (5 minutes)

### 1. Find Your Correct Domain

1. Go to https://railway.app
2. Select your project
3. Click **"Deployments"**
4. **Copy the exact domain** shown there (check if it has hyphens, not underscores)

### 2. Test Your API

```bash
# Replace with your actual domain
curl https://YOUR-EXACT-DOMAIN/api/health

# Should return: {"status": "healthy"}
```

### 3. Update Streamlit Cloud Secrets

1. Go to **Streamlit Cloud Dashboard** → Your app
2. Click **Settings** ⚙️ → **Secrets**
3. Update:
```toml
api_url = "https://YOUR-EXACT-DOMAIN"
```
4. **Save** → Wait for auto-redeploy

### 4. Verify in Streamlit

Open your Streamlit app - you should see:
- ✅ **"✓ API Connected"** (top right) = Success!
- ❌ **"✗ API Down"** = Check your domain in Secrets

## 📋 Verification Steps

| What | Command | Expected Result |
|------|---------|-----------------|
| **Health check** | `curl https://domain/api/health` | HTTP 200 + `{"status": "healthy"}` |
| **Root endpoint** | `curl https://domain/` | HTTP 200 + API info JSON |
| **Swagger docs** | Visit `https://domain/docs` in browser | Swagger UI loads |

## 🐛 If Still Not Working

Check in order:
1. ✅ Domain from Railway dashboard (has hyphens, not underscores)
2. ✅ Deployment shows ✅ **"Success"** in Railway logs
3. ✅ No errors in Railway deployment logs
4. ✅ Your domain in Streamlit Secrets matches exactly

If still failing, go to [RAILWAY_TROUBLESHOOT.md](RAILWAY_TROUBLESHOOT.md) for advanced troubleshooting.

## 📝 Key Changes Made

```python
# Before (main.py)
port = int(os.getenv("FASTAPI_PORT", 8000))

# After (handles Railway's PORT variable)
port = int(os.getenv("PORT", os.getenv("FASTAPI_PORT", 8000)))
```

## Next Steps

After confirming API works:
```bash
git add .
git commit -m "Fix: Railway PORT configuration + auto-data loading"
git push
```

This triggers Railway to redeploy with the fixes.

---

**Still need help?** Share your Railway domain and I can help debug further!
