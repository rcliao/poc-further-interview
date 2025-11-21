# Railway Quick Start

## ⚡ Deploy in 5 Minutes

### Step 1: Create Railway Project
```bash
# Install Railway CLI (optional)
npm install -g @railway/cli

# Or use the web interface at railway.app
```

### Step 2: Push Code to GitHub
```bash
git push origin main
```

### Step 3: Deploy via Railway Web

1. **Go to**: https://railway.app/new
2. **Select**: "Deploy from GitHub repo"
3. **Choose**: Your repository

### Step 4: Add Services

#### PostgreSQL (Database)
1. Click "+ New" → "Database" → "PostgreSQL"
2. **Enable pgvector**:
   - Click PostgreSQL service
   - Go to "Data" tab
   - Click "Query" and run:
     ```sql
     CREATE EXTENSION IF NOT EXISTS vector;
     ```

#### Backend (Django API)
1. Click "+ New" → "GitHub Repo" → Select repo
2. **Root Directory**: `backend`
3. **Add Variables**:
   ```
   DATABASE_URL              ${PostgreSQL.DATABASE_URL}
   OPENAI_API_KEY           sk-your-key-here
   DJANGO_SECRET_KEY        your-secret-key-here
   DEBUG                    False
   ALLOWED_HOSTS            *.railway.app
   CORS_ALLOWED_ORIGINS     https://your-frontend.railway.app,https://your-admin.railway.app
   PORT                     8000
   ```
4. **Generate Domain**: Click "Settings" → "Networking" → "Generate Domain"

#### Frontend (Chat UI)
1. Click "+ New" → "GitHub Repo" → Select repo
2. **Root Directory**: `frontend`
3. **Add Variables**:
   ```
   VITE_API_URL    https://your-backend.railway.app
   ```
4. **Generate Domain**

#### Admin Dashboard
1. Click "+ New" → "GitHub Repo" → Select repo
2. **Root Directory**: `admin`
3. **Add Variables**:
   ```
   VITE_API_URL    https://your-backend.railway.app
   ```
4. **Generate Domain**

### Step 5: Update CORS
After getting frontend URLs, update backend variables:
```
CORS_ALLOWED_ORIGINS=https://frontend-xxx.railway.app,https://admin-xxx.railway.app
```

### Step 6: Redeploy Frontends
1. Go to frontend service → Deployments → Redeploy
2. Go to admin service → Deployments → Redeploy

## ✅ Verify Deployment

- [ ] Backend health check: `https://your-backend.railway.app/api/admin/prospects`
- [ ] Frontend loads: `https://your-frontend.railway.app`
- [ ] Admin loads: `https://your-admin.railway.app`
- [ ] Chat works (send a test message)
- [ ] Admin shows prospects

## 🔑 Required Environment Variables

### Backend
```env
DATABASE_URL=${PostgreSQL.DATABASE_URL}  # Auto-linked
OPENAI_API_KEY=sk-...                   # Get from OpenAI
DJANGO_SECRET_KEY=random-string-here    # Generate with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
DEBUG=False
ALLOWED_HOSTS=*.railway.app
CORS_ALLOWED_ORIGINS=https://frontend.railway.app,https://admin.railway.app
PORT=8000
```

### Frontend & Admin
```env
VITE_API_URL=https://your-backend.railway.app
```

## 💡 Tips

1. **Generate Django Secret Key**:
   ```python
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```

2. **Check Logs**: Click on any service → "Deployments" → Latest deployment → "View Logs"

3. **Service Order**:
   - Deploy PostgreSQL first
   - Then Backend (needs database)
   - Finally Frontends (need backend URL)

4. **Rebuild Frontends**: After changing backend URL, redeploy frontends to rebuild with new VITE_API_URL

5. **Database Backup**: Railway auto-backups PostgreSQL, but export data regularly for safety

## 🐛 Common Issues

**Frontend shows blank page**:
- Check browser console for CORS errors
- Verify VITE_API_URL is set correctly
- Redeploy after changing env vars

**Backend errors**:
- Check DATABASE_URL is linked: `${PostgreSQL.DATABASE_URL}`
- Verify OPENAI_API_KEY is valid
- Check pgvector extension is enabled

**"Internal Server Error"**:
- View logs in Railway dashboard
- Most likely: missing env variable or database issue

## 📊 Costs

- **Hobby Plan**: $5/month + usage (~$20-30/month total)
- **Pro Plan**: $20/month + usage
- OpenAI API: ~$0.01-0.10 per conversation

## 🚀 Next Steps

After deployment:
1. Test all agent types (pricing, tour, amenities, financing)
2. Schedule a test tour
3. Check admin dashboard
4. Monitor logs for errors
5. Set up custom domains (optional)
6. Record your demo video!
