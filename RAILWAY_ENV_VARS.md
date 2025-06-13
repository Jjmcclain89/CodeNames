# Railway Environment Variables Setup

## Frontend Service Environment Variables
Add these to your Railway **Frontend** service:

```
VITE_API_URL=https://backend-production-8bea.up.railway.app
VITE_WS_URL=https://backend-production-8bea.up.railway.app  
VITE_NODE_ENV=production
```

## Backend Service Environment Variables
Add these to your Railway **Backend** service:

```
NODE_ENV=production
FRONTEND_URL=https://frontend-production-acc1.up.railway.app
JWT_SECRET=your-super-secret-jwt-key-change-this
DATABASE_URL=(auto-provided by Railway PostgreSQL service)
```

## How to Set Environment Variables in Railway:

1. Go to your Railway dashboard
2. Select your project
3. Click on the **Frontend** service
4. Go to **Variables** tab  
5. Add each VITE_* variable with its value
6. Repeat for **Backend** service with its variables
7. Redeploy both services after setting variables

## Testing After Setting Variables:

1. **Backend Health Check**: 
   - Visit: https://backend-production-8bea.up.railway.app/api/health
   - Should show JSON with status: "OK"

2. **Frontend Test**:
   - Visit: https://frontend-production-acc1.up.railway.app
   - Open browser console (F12)
   - Should see successful Socket.io connection logs

3. **Full Test**:
   - Try logging in
   - Create a game lobby
   - Test real-time features
