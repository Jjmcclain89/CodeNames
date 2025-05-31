#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fix Backend Syntax Error
Repairs the TypeScript syntax error caused by the previous script
"""

import os
from datetime import datetime

def update_file_content(file_path, new_content):
    """Update file with proper Windows encoding"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    print("🔧 Fixing Backend Syntax Error...")
    
    # Create a clean, working version of the backend index.ts
    # Based on the original but with properly added games routes
    
    fixed_backend_content = '''import express, { Request, Response, NextFunction } from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import dotenv from 'dotenv';
import { gameService } from './services/gameService';
import gameRoutes from './routes/games';

// Load environment variables
dotenv.config();

console.log('🚀 Starting Codenames backend server...');

const app = express();
const server = createServer(app);

// CORS configuration
const corsOptions = {
  origin: process.env.FRONTEND_URL || "http://localhost:5173",
  methods: ["GET", "POST"],
  credentials: true
};

app.use(cors(corsOptions));
app.use(express.json());

console.log('📦 Express middleware configured');

// Simple in-memory storage for Phase 1
const users = new Map<string, any>();
const rooms = new Map<string, any>();
const connectedUsers = new Map<string, any>();

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
app.use('/api/games', gameRoutes);

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
    
    // Create simple user for Phase 1
    const user = {
      id: `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      username: username.trim(),
      createdAt: new Date().toISOString()
    };
    
    // Simple token
    const token = `token_${user.id}_${Date.now()}`;
    
    // Store user
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

console.log('🔗 API routes configured');

// ========================================
// GAME SOCKET HANDLERS - PHASE 2
// ========================================

import { GameService } from './services/gameService';

// Add game socket handlers to existing socket connection
function addGameHandlers(socket: any, io: any) {
  const user = connectedUsers.get(socket.id);
  if (!user) {
    // safe_print('⚠️ Game handler called for unauthenticated socket:', socket.id);
    return;
  }

  // Game creation and management
  socket.on('game:create', () => {
    try {
      const roomCode = 'GLOBAL'; // For now, use global room for games
      const game = gameService.createGameForRoom(roomCode);
      
      // Add player to game
      const success = gameService.addPlayerToGame(game.getId(), user.id, user.username, socket.id);
      
      if (success) {
        const gameState = game.getGame();
        socket.emit('game:state-updated', gameState);
        socket.to(roomCode).emit('game:player-joined', gameState.players.find((p: any )=> p.id === user.id));
        console.log('🎮 Game created for room:', roomCode, 'by:', user.username);
      } else {
        socket.emit('game:error', 'Failed to create game');
      }
    } catch (error) {
      console.error('❌ Error creating game:', error);
      socket.emit('game:error', 'Failed to create game');
    }
  });

  socket.on('game:start', () => {
    try {
      const result = gameService.startGame(user.id);
      
      if (result.success) {
        const game = gameService.getGameByPlayer(user.id);
        if (game) {
          const gameState = game.getGame();
          io.to(gameState.roomCode).emit('game:state-updated', gameState);
          console.log('🚀 Game started by:', user.username);
        }
      } else {
        socket.emit('game:error', result.error || 'Failed to start game');
      }
    } catch (error) {
      console.error('❌ Error starting game:', error);
      socket.emit('game:error', 'Failed to start game');
    }
  });

  socket.on('game:join-team', (team: string, role: string) => {
    try {
      // Get or create game for current room
      const roomCode = 'GLOBAL';
      let game = gameService.getGameForRoom(roomCode);
      
      if (!game) {
        game = gameService.createGameForRoom(roomCode);
        gameService.addPlayerToGame(game.getId(), user.id, user.username, socket.id);
      }

      const result = gameService.assignPlayerToTeam(user.id, team as any, role as any);
      
      if (result.success) {
        const gameState = game.getGame();
        io.to(roomCode).emit('game:state-updated', gameState);
        console.log('👥 Player', user.username, 'joined', team, 'team as', role);
      } else {
        socket.emit('game:error', result.error || 'Failed to join team');
      }
    } catch (error) {
      console.error('❌ Error joining team:', error);
      socket.emit('game:error', 'Failed to join team');
    }
  });

  socket.on('game:give-clue', (data: { word: string; number: number }) => {
    try {
      const result = gameService.giveClue(user.id, data.word, data.number);
      
      if (result.success) {
        const game = gameService.getGameByPlayer(user.id);
        if (game) {
          const gameState = game.getGame();
          io.to(gameState.roomCode).emit('game:state-updated', gameState);
          if (gameState.currentClue) {
            io.to(gameState.roomCode).emit('game:clue-given', gameState.currentClue);
          }
          console.log('💡 Clue given by', user.username + ':', data.word, data.number);
        }
      } else {
        socket.emit('game:error', result.error || 'Failed to give clue');
      }
    } catch (error) {
      console.error('❌ Error giving clue:', error);
      socket.emit('game:error', 'Failed to give clue');
    }
  });

  socket.on('game:reveal-card', (cardId: string) => {
    try {
      const result = gameService.revealCard(user.id, cardId);
      
      if (result.success && result.card) {
        const game = gameService.getGameByPlayer(user.id);
        if (game) {
          const gameState = game.getGame();
          io.to(gameState.roomCode).emit('game:state-updated', gameState);
          io.to(gameState.roomCode).emit('game:card-revealed', result.card);
          
          if (result.gameEnded && result.winner) {
            io.to(gameState.roomCode).emit('game:game-ended', result.winner);
            console.log('🎉 Game ended! Winner:', result.winner);
          }
          
          console.log('🎯 Card revealed by', user.username + ':', result.card.word, '(' + result.card.team + ')');
        }
      } else {
        socket.emit('game:error', result.error || 'Failed to reveal card');
      }
    } catch (error) {
      console.error('❌ Error revealing card:', error);
      socket.emit('game:error', 'Failed to reveal card');
    }
  });

  socket.on('game:end-turn', () => {
    try {
      const result = gameService.endTurn(user.id);
      
      if (result.success) {
        const game = gameService.getGameByPlayer(user.id);
        if (game) {
          const gameState = game.getGame();
          io.to(gameState.roomCode).emit('game:state-updated', gameState);
          io.to(gameState.roomCode).emit('game:turn-changed', gameState.currentTurn);
          console.log('⏭️ Turn ended by', user.username, '- now', gameState.currentTurn, 'turn');
        }
      } else {
        socket.emit('game:error', result.error || 'Failed to end turn');
      }
    } catch (error) {
      console.error('❌ Error ending turn:', error);
      socket.emit('game:error', 'Failed to end turn');
    }
  });

  socket.on('game:reset', () => {
    try {
      const result = gameService.resetGame(user.id);
      
      if (result.success) {
        const game = gameService.getGameByPlayer(user.id);
        if (game) {
          const gameState = game.getGame();
          io.to(gameState.roomCode).emit('game:state-updated', gameState);
          console.log('🔄 Game reset by:', user.username);
        }
      } else {
        socket.emit('game:error', result.error || 'Failed to reset game');
      }
    } catch (error) {
      console.error('❌ Error resetting game:', error);
      socket.emit('game:error', 'Failed to reset game');
    }
  });
}

// ========================================
// SOCKET.IO SETUP WITH ENHANCED DEBUGGING
// ========================================

const io = new Server(server, {
  cors: corsOptions,
  transports: ['websocket', 'polling']
});

// Helper functions
function findUserByToken(token: string) {
  console.log('🔍 Looking for user with token:', token ? token.substring(0, 30) + '...' : 'null/undefined');
  
  if (!token) {
    console.log('❌ No token provided');
    return null;
  }
  
  for (const [userId, userData] of users.entries()) {
    if (userData.token === token) {
      console.log('✅ Found user:', userData.username, userId);
      return userData;
    }
  }
  
  console.log('❌ User not found for token');
  console.log('🔍 Available users:');
  logUsers();
  return null;
}

function createRoom() {
  const roomCode = Math.random().toString(36).substr(2, 6).toUpperCase();
  const room = {
    code: roomCode,
    users: new Map(),
    messages: [],
    createdAt: new Date().toISOString()
  };
  rooms.set(roomCode, room);
  return room;
}

function getOrCreateGlobalRoom() {
  if (!rooms.has('GLOBAL')) {
    const globalRoom = {
      code: 'GLOBAL',
      users: new Map(),
      messages: [],
      createdAt: new Date().toISOString()
    };
    rooms.set('GLOBAL', globalRoom);
  }
  return rooms.get('GLOBAL');
}

// Socket handlers
io.on('connection', (socket) => {
  console.log('📡 Socket connected:', socket.id);
  
  socket.on('authenticate', (token: string) => {
    console.log('🔐 Socket authentication attempt for socket:', socket.id);
    console.log('🔐 Received token type:', typeof token);
    console.log('🔐 Token value:', token ? token.substring(0, 30) + '...' : 'null/undefined');
    
    const user = findUserByToken(token);
    
    if (user) {
      // Store connected user
      connectedUsers.set(socket.id, {
        ...user,
        socketId: socket.id,
        connectedAt: new Date().toISOString()
      });
      
      // Join global room automatically for Phase 1
      const globalRoom = getOrCreateGlobalRoom();
      globalRoom.users.set(socket.id, user);
      socket.join('GLOBAL');
      
      socket.emit('authenticated', { 
        success: true, 
        user: user,
        roomCode: 'GLOBAL'
      });
      
      // Notify others in global room
      socket.to('GLOBAL').emit('user-joined', {
        user: user,
        message: `${user.username} joined the chat`
      });
      
      // Send current users in room
      const roomUsers = Array.from(globalRoom.users.values());
      io.to('GLOBAL').emit('room-users', { users: roomUsers });
      
      // Send recent messages
      socket.emit('recent-messages', { messages: globalRoom.messages.slice(-10) });
      addGameHandlers(socket, io);
      console.log('✅ Socket authenticated successfully for:', user.username, 'in GLOBAL room');
    } else {
      socket.emit('authenticated', { success: false, error: 'Invalid token' });
      console.log('❌ Socket authentication failed for socket:', socket.id);
    }
  });
  
  socket.on('send-message', (data) => {
    const user = connectedUsers.get(socket.id);
    if (!user) {
      console.log('❌ Message from unauthenticated socket:', socket.id);
      socket.emit('error', { message: 'Not authenticated' });
      return;
    }
    
    const message = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
      username: user.username,
      userId: user.id,
      text: data.message,
      timestamp: new Date().toISOString()
    };
    
    // Add to global room messages
    const globalRoom = getOrCreateGlobalRoom();
    globalRoom.messages.push(message);
    
    // Keep only last 50 messages
    if (globalRoom.messages.length > 50) {
      globalRoom.messages = globalRoom.messages.slice(-50);
    }
    
    // Broadcast to all users in global room
    io.to('GLOBAL').emit('new-message', message);
    
    console.log(`💬 Message from ${user.username}: ${data.message}`);
  });
  
  socket.on('disconnect', () => {
    const user = connectedUsers.get(socket.id);
    if (user) {
      console.log('📡 Socket disconnected:', socket.id, user.username);
      
      // Remove from global room
      const globalRoom = getOrCreateGlobalRoom();
      globalRoom.users.delete(socket.id);
      
      // Notify others
      socket.to('GLOBAL').emit('user-left', {
        user: user,
        message: `${user.username} left the chat`
      });
      
      // Update room users
      const roomUsers = Array.from(globalRoom.users.values());
      io.to('GLOBAL').emit('room-users', { users: roomUsers });
      
      // Remove from connected users

      // Clean up game state for Phase 2
      if (user) gameService.removePlayerFromAllGames(user.id);
      connectedUsers.delete(socket.id);
    } else {
      console.log('📡 Socket disconnected:', socket.id, '(unauthenticated)');
    }
  });
  
  // Handle connection without authentication (after 5 seconds, warn)
  setTimeout(() => {
    if (!connectedUsers.has(socket.id)) {
      console.log('⚠️ Socket', socket.id, 'connected but not authenticated after 5 seconds');
    }
  }, 5000);
});

console.log('📡 Socket.io with enhanced authentication debugging configured');

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

const PORT = process.env.PORT || 3001;

server.listen(PORT, () => {
  console.log('');
  console.log('🎉 ================================');
  console.log(`🚀 Server running on port ${PORT}`);
  console.log('📡 Socket.io with enhanced auth debugging');
  console.log(`🔗 API endpoints: http://localhost:${PORT}/api`);
  console.log(`🏥 Health check: http://localhost:${PORT}/api/health`);
  console.log(`🎮 Games API: http://localhost:${PORT}/api/games/test`);
  console.log('💬 Global chat room ready');
  console.log('🔍 Enhanced authentication logging enabled');
  console.log('🎉 ================================');
  console.log('');
});

export default app;
'''

    # Update the backend index.ts with the corrected content
    if update_file_content('backend/src/index.ts', fixed_backend_content):
        print("✅ Fixed backend/src/index.ts syntax errors")
    else:
        print("❌ Failed to fix backend/src/index.ts")
        return
    
    # Update changelog
    try:
        changelog_path = 'CHANGELOG.md'
        with open(changelog_path, 'r', encoding='utf-8') as f:
            changelog = f.read()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        new_entry = f'- Backend Syntax Fix: Repaired TypeScript compilation errors and properly registered games routes ({timestamp})'
        
        if '### Python Scripts Run' in changelog:
            updated_changelog = changelog.replace(
                '### Python Scripts Run',
                f'### Python Scripts Run\n{new_entry}'
            )
            
            with open(changelog_path, 'w', encoding='utf-8') as f:
                f.write(updated_changelog)
            print("✅ Updated CHANGELOG.md")
    except Exception as e:
        print(f"Note: Could not update changelog: {e}")
    
    print(f"\n🎉 Backend Syntax Fix Complete!")
    print("\n🔧 What was fixed:")
    print("• Repaired TypeScript syntax errors in availableEndpoints array")
    print("• Properly added: import gameRoutes from './routes/games';")
    print("• Properly added: app.use('/api/games', gameRoutes);")
    print("• Clean, working backend index.ts file")
    print("\n🎯 Next Steps:")
    print("1. Your backend should start without errors now")
    print("2. Test: http://localhost:3001/api/games/test in browser")
    print("3. Click 'Test API Connection' on homepage")
    print("4. Try 'Create Game' - should generate codes and work!")
    print("\n💡 The games routes are now properly registered!")

if __name__ == "__main__":
    main()
