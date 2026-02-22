# Railway Deployment Troubleshooting

## Issue: "Deployment Successful but Cannot Access"

If you see ✅ "Deployment Successful" but can't access `https://insightx_ai.railway.app/`:

### Step 1: Check Your Actual Railway Domain

The domain might be different from what you expect:

1. **Go to Railway Dashboard**: https://railway.app
2. **Select Your Project** → **Deployments**
3. **Look for the URL** in the deployment details
4. **Copy the exact domain** (it might be auto-generated)

Example actual domains:
- `https://insightx-api-production.railway.app/`
- `https://your-project-uuid.railway.app/`
- `https://insightx-api.railway.app/`

**Note**: The domain in your question (`insightx_ai.railway.app`) has underscores. Railway removes underscores and uses hyphens, so it's likely:
- `https://insightx-ai.railway.app/` (not `insightx_ai`)

### Step 2: Test the API Directly

1. **Get the exact domain** from Railway dashboard
2. **Try these endpoints**:
   ```bash
   # Health check
   curl https://your-domain.railway.app/api/health
   
   # Root endpoint (should show API info)
   curl https://your-domain.railway.app/
   
   # Swagger docs
   curl https://your-domain.railway.app/docs
   ```

3. **Expected response** from `/api/health`:
   ```json
   {"status": "healthy"}
   ```

### Step 3: Check Railway Logs

If the endpoints don't work:

1. **Go to Railway Dashboard** → **Your Project**
2. **Click "Logs"** tab
3. **Look for errors** related to:
   - Port binding
   - Database initialization
   - Missing dependencies

### Step 4: Verify Environment Variables

1. **Go to Railway Dashboard** → **Project Settings**
2. **Check "Variables"** tab
3. **Make sure these are set** (if using non-SQLite database):
   ```
   DATABASE_URL=sqlite:///./insightx_db.db
   FASTAPI_HOST=0.0.0.0
   ```

4. **If needed, add variables**:
   ```
   PYTHON_VERSION=3.10
   ```

### Step 5: Rebuild Deployment

If still not working:

1. **Go to Railway Dashboard** → **Deployments**
2. **Click the gear icon** on deployment
3. **Select "Redeploy"**
4. **Wait 2-3 minutes** for rebuild

Or push a new commit to trigger auto-deploy:
```bash
git add .
git commit -m "Fix: Railway deployment configuration"
git push
```

### Step 6: Check Port Binding

Railway automatically sets the `PORT` environment variable. Our `main.py` should handle this:

```python
port = int(os.getenv("PORT", 8000))  # Railway sets PORT
```

If you see "port already in use" errors, this is your issue.

---

## Common Railway Issues & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `502 Bad Gateway` | Port not binding correctly | Check `$PORT` env var usage |
| `Application failed to start` | Missing dependencies | Verify `requirements.txt` |
| `504 Gateway Timeout` | Database loading timeout | Reduce initial data load or fix queries |
| `Cannot connect` | Domain is wrong | Copy exact domain from Railway dashboard |
| `Connection refused` | Port mismatch | Ensure using `$PORT` environment variable |

---

## Complete Railway Setup Checklist

- [ ] Domain copied from Railway dashboard (check for hyphens, not underscores)
- [ ] `Procfile` exists with correct command
- [ ] `main.py` uses `PORT` environment variable
- [ ] `requirements.txt` includes all dependencies
- [ ] Git repo is connected to Railway
- [ ] Environment variables set in Railway dashboard (if needed)
- [ ] Deployment shows ✅ "Success" with no error logs
- [ ] Can access `https://your-domain/` (shows JSON response)
- [ ] Streamlit secrets updated with correct API URL

---

## Update Streamlit with Correct Domain

Once you have the working domain:

1. **Go to Streamlit Cloud Dashboard**
2. **Select your app** → **Settings** (⚙️)
3. **Click "Secrets"**
4. **Update**:
   ```toml
   api_url = "https://your-exact-domain.railway.app"
   ```
5. **Save** → **Redeploy**

---

## Quick Test Script

Save as `test_railway.sh` and run locally:

```bash
#!/bin/bash
DOMAIN="https://your-domain.railway.app"

echo "Testing Railway API..."
echo "========================"

echo "1. Health check:"
curl -w "\nStatus: %{http_code}\n" "${DOMAIN}/api/health"

echo -e "\n2. Root endpoint:"
curl -w "\nStatus: %{http_code}\n" "${DOMAIN}/"

echo -e "\n3. Swagger docs:"
curl -w "\nStatus: %{http_code}\n" "${DOMAIN}/docs"
```

Run:
```bash
chmod +x test_railway.sh
./test_railway.sh
```

---

## Still Stuck?

Check these in order:
1. ✅ Exact domain from Railway (with hyphens)
2. ✅ Deployment logs in Railway dashboard
3. ✅ `curl` test from local machine
4. ✅ `PORT` environment variable in `main.py`
5. ✅ No critical errors in application logs

**If still failing**: Share your Railway deployment logs and exact domain, we can debug further.
