# Railway Deployment Guide

This guide walks you through deploying the ACME Sales Agent to Railway.

## Prerequisites

1. Railway account (sign up at https://railway.app)
2. GitHub repository with this code
3. OpenAI API key

## Deployment Steps

### 1. Create a New Railway Project

1. Go to https://railway.app/new
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access your GitHub account
5. Select this repository

### 2. Set Up PostgreSQL Database

1. In your Railway project, click "+ New"
2. Select "Database" → "Add PostgreSQL"
3. Once created, click on the PostgreSQL service
4. Go to "Variables" tab and note the `DATABASE_URL`
5. **IMPORTANT**: Enable pgvector extension:
   - Click on the PostgreSQL service
   - Go to "Data" tab
   - Click "Query" and run:
     ```sql
     CREATE EXTENSION IF NOT EXISTS vector;
     ```

### 3. Deploy Backend Service

1. Click "+ New" → "GitHub Repo"
2. Select your repository
3. Railway will detect the Dockerfile in `backend/`
4. Configure the service:
   - **Name**: `backend`
   - **Root Directory**: `backend`
   - **Dockerfile Path**: `Dockerfile`

5. Add environment variables (go to Variables tab):
   ```
   DATABASE_URL=${PostgreSQL.DATABASE_URL}
   OPENAI_API_KEY=<your-openai-api-key>
   DJANGO_SECRET_KEY=<generate-a-secret-key>
   DEBUG=False
   ALLOWED_HOSTS=*.railway.app
   PORT=8000
   ```

6. Under "Settings" → "Networking":
   - Generate a domain (e.g., `acme-backend.up.railway.app`)
   - Note this URL for frontend configuration

7. Deploy will start automatically

### 4. Deploy Frontend (Chat UI)

1. Click "+ New" → "GitHub Repo"
2. Select your repository again
3. Configure the service:
   - **Name**: `frontend`
   - **Root Directory**: `frontend`
   - **Dockerfile Path**: `Dockerfile`

4. Add environment variables:
   ```
   VITE_API_URL=https://<your-backend-domain>.railway.app
   ```

5. Under "Settings" → "Networking":
   - Generate a domain (e.g., `acme-chat.up.railway.app`)

### 5. Deploy Admin Dashboard

1. Click "+ New" → "GitHub Repo"
2. Select your repository again
3. Configure the service:
   - **Name**: `admin`
   - **Root Directory**: `admin`
   - **Dockerfile Path**: `Dockerfile`

4. Add environment variables:
   ```
   VITE_API_URL=https://<your-backend-domain>.railway.app
   ```

5. Under "Settings" → "Networking":
   - Generate a domain (e.g., `acme-admin.up.railway.app`)

### 6. Update Backend CORS Settings

1. Go to backend service → Variables
2. Add/update:
   ```
   CORS_ALLOWED_ORIGINS=https://<frontend-domain>.railway.app,https://<admin-domain>.railway.app
   ```

3. Redeploy the backend service

### 7. Rebuild Frontends

After backend is deployed and you have the actual backend URL:

1. Go to frontend service → Variables
2. Update `VITE_API_URL` to the actual backend Railway URL
3. Go to "Deployments" and click "Redeploy"

4. Repeat for admin service

## Environment Variables Checklist

### PostgreSQL Service
- Automatically created by Railway
- Enable `vector` extension manually

### Backend Service
```env
DATABASE_URL=${PostgreSQL.DATABASE_URL}
OPENAI_API_KEY=sk-...
DJANGO_SECRET_KEY=<random-string>
DEBUG=False
ALLOWED_HOSTS=*.railway.app
PORT=8000
CORS_ALLOWED_ORIGINS=https://acme-chat.up.railway.app,https://acme-admin.up.railway.app
```

### Frontend Service
```env
VITE_API_URL=https://acme-backend.up.railway.app
```

### Admin Service
```env
VITE_API_URL=https://acme-backend.up.railway.app
```

## Troubleshooting

### Backend Won't Start
1. Check logs in Railway dashboard
2. Verify DATABASE_URL is set correctly
3. Ensure pgvector extension is enabled
4. Check OPENAI_API_KEY is valid

### Frontend Shows CORS Errors
1. Verify CORS_ALLOWED_ORIGINS includes frontend domain
2. Make sure both frontend domains are listed
3. Redeploy backend after changing CORS settings

### Database Connection Errors
1. Ensure DATABASE_URL uses the correct format
2. Check PostgreSQL service is running
3. Verify pgvector extension is installed

### Build Failures
1. Check Node.js version (should be 20+)
2. Verify all dependencies are in package.json
3. Check Dockerfile syntax

## Post-Deployment

1. Test the chat interface at your frontend URL
2. Test the admin dashboard at your admin URL
3. Verify tour scheduling works
4. Check enrichment events are being captured
5. Test all agent types (pricing, financing, amenities, tour)

## Monitoring

- Check Railway logs for each service
- Monitor PostgreSQL usage
- Set up alerts for service downtime
- Track API usage for OpenAI

## Costs

Railway pricing (approximate):
- PostgreSQL: $5-10/month
- Backend: $5-10/month
- Frontend: $5/month
- Admin: $5/month
- **Total**: ~$20-35/month

Plus OpenAI API costs (usage-based).

## Scaling

To handle more traffic:
1. Increase backend replicas in Railway
2. Add Redis for caching (optional)
3. Use CDN for frontend assets
4. Consider upgrading PostgreSQL plan
