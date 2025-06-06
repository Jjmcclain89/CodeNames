# Mobile Testing Instructions

## 🚀 Your servers are now configured for mobile access!

### Your Computer's IP Address: 192.168.86.138

### Mobile Access URLs:
- **Frontend**: http://192.168.86.138:5173
- **Backend API**: http://192.168.86.138:3001/api/health

### Testing Steps:

1. **Start your servers** (if not already running):
   ```bash
   # Terminal 1 - Backend
   cd backend
   npm run dev
   
   # Terminal 2 - Frontend  
   cd frontend
   npm run dev
   ```

2. **Verify servers are running**:
   - Backend should show: "Mobile access: http://192.168.86.138:3001"
   - Frontend should show network addresses including 192.168.86.138:5173

3. **Connect from your phone**:
   - Make sure your phone is on the same WiFi network
   - Open your phone's browser
   - Go to: http://192.168.86.138:5173
   - You should see the Codenames login page

4. **Test the flow**:
   - Login on your phone
   - Create or join a game
   - Navigate to the game board
   - Everything should work the same as on desktop!

### Troubleshooting:

**If connection fails:**
- Check that both devices are on the same WiFi network
- Try disabling Windows Firewall temporarily
- Make sure no VPN is active on either device
- Verify the IP address is correct: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)

**If API calls fail:**
- Check browser console for CORS errors
- Verify backend is running and showing the mobile access URL
- Test backend directly: http://192.168.86.138:3001/api/health

### Network Security:
- These settings are for development only
- Servers are accessible to any device on your local network
- Don't use these settings in production

Happy mobile testing! 📱🎮
