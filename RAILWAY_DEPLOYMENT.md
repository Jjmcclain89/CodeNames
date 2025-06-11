# Railway Deployment Checklist for Codenames App

## 🚀 Pre-Deployment Steps

### 1. Railway Account Setup
- [ ] Create Railway account at railway.app
- [ ] Install Railway CLI: `npm install -g @railway/cli`
- [ ] Login: `railway login`

### 2. Project Setup
- [ ] Create new Railway project: `railway new`
- [ ] Link to this directory: `railway link`

### 3. Database Setup
- [ ] Add PostgreSQL service in Railway dashboard
- [ ] Copy DATABASE_URL from Railway to environment variables
- [ ] Verify Prisma schema matches your needs

### 4. Environment Variables (Railway Dashboard)
**Backend Service:**
- [ ] JWT_SECRET=your-super-secret-jwt-key-change-this
- [ ] NODE_ENV=production
- [ ] FRONTEND_URL=https://your-frontend-domain.railway.app
- [ ] DATABASE_URL (auto-provided by PostgreSQL service)

**Frontend Service:**
- [ ] VITE_API_URL=https://your-backend-domain.railway.app
- [ ] VITE_WS_URL=https://your-backend-domain.railway.app
- [ ] VITE_NODE_ENV=production

## 🔧 Deployment Steps

### 1. Backend Deployment
```bash
cd backend
railway deploy
```

### 2. Database Migration
```bash
railway run npx prisma migrate deploy
```

### 3. Frontend Deployment
```bash
cd frontend
railway deploy
```

### 4. Update Backend Code (if needed)
- [ ] Switch from in-memory Maps to Prisma database calls
- [ ] Update socket handlers to use database
- [ ] Test authentication with PostgreSQL

## 🧪 Testing Steps

### 1. Backend Testing
- [ ] Visit: https://your-backend-domain.railway.app/api/health
- [ ] Should show: {"status": "OK", "message": "..."}

### 2. Frontend Testing
- [ ] Visit: https://your-frontend-domain.railway.app
- [ ] Test user registration/login
- [ ] Create a game lobby
- [ ] Test real-time Socket.io connection

### 3. Full Integration Testing
- [ ] Multiple users join same lobby
- [ ] Real-time team assignment works
- [ ] Game creation and gameplay functions
- [ ] Mobile access works

## 🚨 Troubleshooting

### Common Issues:
1. **Database Connection**: Check DATABASE_URL in Railway dashboard
2. **CORS Errors**: Update FRONTEND_URL environment variable
3. **Socket.io Issues**: Verify WebSocket proxy settings
4. **Build Failures**: Check Node.js version (should be 18+)

### Useful Railway Commands:
```bash
railway logs         # View deployment logs  
railway shell        # Access deployed container
railway status       # Check service status
railway restart      # Restart services
```

## 📝 Post-Deployment

### 1. Performance Monitoring
- [ ] Set up Railway monitoring alerts
- [ ] Test app performance under load
- [ ] Monitor database connection limits

### 2. Domain Setup (Optional)
- [ ] Configure custom domain in Railway
- [ ] Update CORS settings for new domain
- [ ] Set up SSL certificate (auto-handled by Railway)

### 3. Scaling Considerations
- [ ] Monitor resource usage
- [ ] Consider upgrading Railway plan if needed
- [ ] Implement connection pooling for database

## 🎉 Success Criteria

✅ **Deployment Successful When:**
- Backend health check responds
- Frontend loads without errors
- Users can create accounts and login
- Real-time lobby functionality works
- Mobile devices can access the app
- Game creation and team assignment functions
- WebSocket connections are stable

---

**Estimated Deployment Time:** 30-60 minutes
**Railway Free Tier Limits:** $5/month credit, sufficient for testing
**Production Ready:** After successful testing and custom domain setup
