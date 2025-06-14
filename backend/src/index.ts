import { gameLobbies, scheduleClosedLobbyCleanup } from './routes/gameLobbies';
import express, { Request, Response, NextFunction } from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import dotenv from 'dotenv';
import gameRoutes from './routes/games';
import gameLobbyRoutes from './routes/gameLobbies';
import { handleSocketConnection, setUsersMap } from './socket/socketHandlers';

// Load environment variables
dotenv.config();

console.log('🚀 Starting Codenames backend server...');

const app = express();
const server = createServer(app);

// CORS configuration for production deployment
const corsOptions = {
  origin: [
    "http://localhost:5173",
    "http://localhost:4173", // Vite preview mode
    process.env.FRONTEND_URL || "http://localhost:5173",
    // Allow any IP on local network for mobile testing
    /^http:\/\/192\.168\.\d{1,3}\.\d{1,3}:5173$/,
    /^http:\/\/10\.\d{1,3}\.\d{1,3}\.\d{1,3}:5173$/,
    /^http:\/\/172\.16\.\d{1,3}\.\d{1,3}:5173$/,
    // Production Railway domains (both formats)
    /^https:\/\/.*\.railway\.app$/,
    /^https:\/\/.*\.up\.railway\.app$/,
    // Specific Railway frontend URL
    "https://codenames.up.railway.app"
  ],
  methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
  credentials: true,
  allowedHeaders: ["Content-Type", "Authorization", "x-requested-with"]
};

app.use(cors(corsOptions));
app.use(express.json());

console.log('📦 Express middleware configured');

// ========================================
// SHARED VARIABLES FOR SOCKET HANDLERS
// ========================================

// In-memory storage for deployment (will migrate to DB later)
const users = new Map<string, any>();
const rooms = new Map<string, any>();
const connectedUsers = new Map<string, any>();
const userRooms = new Map<string, string>();

// Prisma client ready for future database migration
import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient({
  // Optional: Disable Prisma for now, enable when ready for DB migration
  log: process.env.NODE_ENV === 'production' ? [] : ['query', 'info', 'warn', 'error']
});

// Debug function to log users
function logUsers() {
  console.log('👥 Current users in memory:', users.size);
  for (const [userId, userData] of users.entries()) {
    console.log(`   - ${userData.username} (${userId}) token: ${userData.token.substring(0, 20)}...`);
  }
}

// ========================================
// API ROUTES
// ========================================

// Health check endpoint
app.get('/api/health', (req: Request, res: Response): void => {
  console.log('🏥 Health check endpoint called');
  res.json({ 
    status: 'OK', 
    message: 'Codenames backend server is running',
    timestamp: new Date().toISOString(),
    connectedUsers: connectedUsers.size,
    activeRooms: rooms.size,
    totalUsers: users.size,
    environment: process.env.NODE_ENV || 'development',
    endpoints: [
      'GET /api/health',
      'POST /api/auth/login', 
      'POST /api/auth/verify',
      'GET /api/games/test',
      'POST /api/games/create',
      'POST /api/games/join'
    ]
  });
});

// Games routes
// Add io instance to request for real-time updates
app.use((req: any, res, next) => {
  req.io = io;
  next();
});

app.use('/api/games', gameRoutes);
app.use('/api/gamelobbies', gameLobbyRoutes);

// Auth routes
app.post('/api/auth/login', (req: Request, res: Response): void => {
  try {
    console.log('🔑 Login attempt:', req.body);
    
    const { username } = req.body;
    if (!username || username.trim().length === 0) {
      res.status(400).json({
        success: false,
        error: 'Username is required'
      });
      return;
    }
    
    // Create simple user for deployment
    const user = {
      id: `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      username: username.trim(),
      createdAt: new Date().toISOString()
    };
    
    // Simple token
    const token = `token_${user.id}_${Date.now()}`;
    
    // Store user in memory (for now)
    users.set(user.id, { ...user, token });
    
    console.log('✅ Login successful for:', username, 'User ID:', user.id);
    console.log('🎫 Generated token:', token.substring(0, 30) + '...');
    
    // Log current users for debugging
    logUsers();
    
    res.json({
      success: true,
      token,
      user: {
        id: user.id,
        username: user.username
      }
    });
    
  } catch (error) {
    console.error('❌ Login error:', error);
    res.status(500).json({
      success: false,
      error: 'Login failed',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Token verification
app.post('/api/auth/verify', (req: Request, res: Response): void => {
  try {
    console.log('🔍 Token verification attempt');
    
    const { token } = req.body;
    if (!token) {
      res.status(400).json({
        success: false,
        error: 'Token is required'
      });
      return;
    }
    
    console.log('🔍 Verifying token:', token.substring(0, 30) + '...');
    
    // Find user by token
    let foundUser = null;
    for (const [userId, userData] of users.entries()) {
      if (userData.token === token) {
        foundUser = userData;
        break;
      }
    }
    
    if (!foundUser) {
      console.log('❌ Token not found in users map');
      logUsers();
      res.status(401).json({
        success: false,
        error: 'Invalid token'
      });
      return;
    }
    
    console.log('✅ Token verification successful for:', foundUser.username);
    
    res.json({
      success: true,
      user: {
        id: foundUser.id,
        username: foundUser.username
      }
    });
    
  } catch (error) {
    console.error('❌ Token verification error:', error);
    res.status(500).json({
      success: false,
      error: 'Token verification failed',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Get user's current authorized games
app.get('/api/auth/user-games', (req: Request, res: Response): void => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');
    
    if (!token) {
      res.status(401).json({
        success: false,
        error: 'Authorization token required'
      });
      return;
    }
    
    // Find user by token
    let foundUser = null;
    for (const [userId, userData] of users.entries()) {
      if (userData.token === token) {
        foundUser = userData;
        break;
      }
    }
    
    if (!foundUser) {
      res.status(401).json({
        success: false,
        error: 'Invalid token'
      });
      return;
    }
    
    // For now, return empty games array - will be populated as users join games
    res.json({
      success: true,
      games: [],
      user: {
        id: foundUser.id,
        username: foundUser.username
      }
    });
    
  } catch (error) {
    console.error('❌ Error fetching user games:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch user games'
    });
  }
});

console.log('🔗 API routes configured');

// ========================================
// SOCKET.IO SETUP
// ========================================

const io = new Server(server, {
    cors: corsOptions,
    transports: ['websocket', 'polling'],
    allowEIO3: true, // Enable compatibility
    pingTimeout: 60000, // Increase timeout for Railway
    pingInterval: 25000,
    upgradeTimeout: 30000,
    allowUpgrades: true
});

console.log('📡 Socket.io configured - all handlers in socketHandlers.ts');

// Share the users map with socketHandlers.ts so authentication works
setUsersMap(users);

io.on('connection', (socket) => {
    console.log('📡 New socket connection:', socket.id);
    
    // All socket handling is delegated to socketHandlers.ts
    handleSocketConnection(io, socket, {} as any);
});

console.log('📡 Socket.io setup complete');

// ========================================
// ERROR HANDLING
// ========================================

// 404 handler for API routes
app.use('/api/*', (req: Request, res: Response): void => {
  console.log(`❌ API route not found: ${req.method} ${req.path}`);
  res.status(404).json({ 
    success: false, 
    error: 'API endpoint not found',
    path: req.path,
    method: req.method,
    availableEndpoints: [
      'GET /api/health',
      'POST /api/auth/login',
      'POST /api/auth/verify',
      'GET /api/games/test',
      'POST /api/games/create',
      'POST /api/games/join'
    ]
  });
});

// General error handler
app.use((err: any, req: Request, res: Response, next: NextFunction): void => {
  console.error('❌ Server error:', err);
  res.status(500).json({ 
    success: false, 
    error: 'Internal server error',
    message: err instanceof Error ? err.message : 'Unknown error'
  });
});

// ========================================
// START SERVER
// ========================================

const PORT = Number(process.env.PORT) || 3001;

server.listen(Number(PORT), '0.0.0.0', () => {
  console.log('');
  console.log('🎉 ================================');
  console.log(`🚀 Codenames Server running on port ${PORT}`);
  console.log(`📱 Mobile access: http://192.168.86.148:${PORT}`);
  console.log('📡 Socket.io using unified socketHandlers.ts');
  console.log(`🔗 API endpoints: http://localhost:${PORT}/api`);
  console.log(`🏥 Health check: http://localhost:${PORT}/api/health`);
  console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log('✅ All systems ready!');
  console.log('🎉 ================================');
  console.log('');
});

// Graceful shutdown for production
process.on('SIGTERM', async () => {
  console.log('🛑 SIGTERM received, shutting down gracefully');
  await prisma.$disconnect();
  process.exit(0);
});

process.on('SIGINT', async () => {
  console.log('🛑 SIGINT received, shutting down gracefully');  
  await prisma.$disconnect();
  process.exit(0);
});

export default app;
