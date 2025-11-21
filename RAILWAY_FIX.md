# Railway Configuration Fix

## The Issue

Railway builds from the repository root, but our services are in subdirectories (`backend/`, `frontend/`, `admin/`).

## Solution: Configure Root Directory in Railway Dashboard

### For Each Service (Backend, Frontend, Admin):

1. **Go to Service Settings**:
   - Click on the service in Railway dashboard
   - Go to "Settings" tab

2. **Set Root Directory**:
   - Find "Root Directory" setting
   - For backend service: Enter `backend`
   - For frontend service: Enter `frontend`
   - For admin service: Enter `admin`

3. **Save and Redeploy**:
   - Settings save automatically
   - Click "Deploy" → "Redeploy" to rebuild with correct directory

## Alternative: Delete railway.toml

You can delete `railway.toml` and configure everything in the Railway dashboard instead:

```bash
rm railway.toml
git add railway.toml
git commit -m "Remove railway.toml - using dashboard config"
git push
```

Then configure via dashboard as described above.

## Step-by-Step for Backend Service

1. **In Railway Dashboard**:
   - Click on backend service
   - Go to "Settings"

2. **Configure**:
   ```
   Root Directory: backend
   Build Command: (leave empty - uses Dockerfile)
   Start Command: (leave empty - uses Dockerfile CMD)
   ```

3. **Redeploy**:
   - Go to "Deployments" tab
   - Click latest deployment
   - Click "Redeploy"

## Repeat for Frontend and Admin

- Frontend: Root Directory = `frontend`
- Admin: Root Directory = `admin`

## Verify Build Works

Check deployment logs - you should see:
```
✓ Copying pyproject.toml
✓ Installing dependencies
✓ Building application
```

Instead of:
```
✗ "/pyproject.toml": not found
```
