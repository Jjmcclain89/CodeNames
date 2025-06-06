import { Server, Socket } from 'socket.io';
import { PrismaClient } from '@prisma/client';
import jwt from 'jsonwebtoken';

interface AuthenticatedSocket extends Socket {
  userId?: string;
  username?: string;
  currentRoom?: string;
}

// Store active users by room
const roomUsers = new Map<string, Set<string>>();
let gameState: any = null;

export const handleSocketConnection = (io: Server, socket: AuthenticatedSocket, prisma: PrismaClient) => {
  console.log(`📡 Socket connected: ${socket.id}`);

  // Simple authentication that always works
  socket.on('authenticate', async (token: string) => {
    console.log(`🔐 Authenticating socket: ${socket.id}`);
    
    // Simple fallback authentication for testing
    socket.userId = '1';
    socket.username = 'TestUser';
    socket.currentRoom = 'GLOBAL';
    
    // Join the global room
    socket.join('GLOBAL');
    
    socket.emit('authenticated', { 
      success: true, 
      userId: socket.userId,
      username: socket.username 
    });
    
    console.log(`✅ Socket ${socket.id} authenticated as ${socket.username}`);
  });

  // Auth bypass for testing
  socket.on('auth-bypass', (username: string) => {
    console.log('🔓 Auth bypass requested');
    socket.userId = '1';
    socket.username = username || 'TestUser';
    socket.currentRoom = 'GLOBAL';
    socket.join('GLOBAL');
    
    socket.emit('authenticated', { 
      success: true, 
      userId: socket.userId,
      username: socket.username 
    });
    
    console.log(`✅ Auth bypass successful for ${socket.username}`);
  });

  // Simple test handler
  socket.on('test-connection', () => {
    console.log('🧪 Test connection from:', socket.username || 'unauthenticated');
    socket.emit('test-response', { 
      message: 'Backend is working!', 
      username: socket.username,
      authenticated: !!socket.userId
    });
  });

  // Simple game creation - only create once
  socket.on('game:create', () => {
    if (!socket.userId) {
      socket.emit('game:error', 'Not authenticated');
      return;
    }

    if (gameState) {
      console.log('🎮 Game already exists, joining existing game');
      socket.emit('game:state-updated', gameState);
      return;
    }

    console.log(`🎮 Creating new game by ${socket.username}`);
    
    // Create simple game state
    gameState = {
      id: 'game_1',
      status: 'waiting',
      players: [{
        id: socket.userId,
        username: socket.username,
        team: 'neutral',
        role: 'operative'
      }],
      board: [],
      currentTurn: 'red'
    };

    io.to('GLOBAL').emit('game:state-updated', gameState);
    console.log(`✅ Game created successfully`);
  });

  // Add test players
  socket.on('game:add-test-players', () => {
    if (!socket.userId) {
      socket.emit('game:error', 'Not authenticated');
      return;
    }

    if (!gameState) {
      socket.emit('game:error', 'No game exists');
      return;
    }

    console.log('🤖 Adding test players...');

    // Add test players to existing game state
    const testPlayers = [
      { id: 'test_red_spy', username: '🔴 Red Spy (AI)', team: 'red', role: 'spymaster' },
      { id: 'test_red_op', username: '🔴 Red Op (AI)', team: 'red', role: 'operative' },
      { id: 'test_blue_spy', username: '🔵 Blue Spy (AI)', team: 'blue', role: 'spymaster' }
    ];

    // Remove existing test players first
    gameState.players = gameState.players.filter((p: any) => !p.id.startsWith('test_'));
    
    // Add new test players
    gameState.players.push(...testPlayers);

    io.to('GLOBAL').emit('game:state-updated', gameState);
    socket.emit('game:test-players-added', { message: 'Test players added!', playersAdded: 3 });
    
    console.log(`✅ Added ${testPlayers.length} test players`);
  });

  // Join team
  socket.on('game:join-team', (team: string, role: string) => {
    if (!socket.userId || !gameState) {
      socket.emit('game:error', 'Not authenticated or no game');
      return;
    }

    console.log(`👥 ${socket.username} joining ${team} team as ${role}`);

    // Find and update player
    const player = gameState.players.find((p: any) => p.id === socket.userId);
    if (player) {
      player.team = team;
      player.role = role;
      
      io.to('GLOBAL').emit('game:state-updated', gameState);
      console.log(`✅ ${socket.username} joined ${team} team as ${role}`);
    }
  });

  // Start game
  socket.on('game:start', () => {
    if (!socket.userId || !gameState) {
      socket.emit('game:error', 'Not authenticated or no game');
      return;
    }

    console.log(`🚀 Starting game...`);
    
    gameState.status = 'playing';
    gameState.board = createSimpleBoard();
    
    io.to('GLOBAL').emit('game:state-updated', gameState);
    console.log(`✅ Game started successfully`);
  });

  // Handle disconnection
  socket.on('disconnect', () => {
    console.log(`📡 Socket disconnected: ${socket.id}`);
  });
};

// Create a simple board for testing
function createSimpleBoard() {
  const words = ['APPLE', 'BOOK', 'CAR', 'DOG', 'ELEPHANT'];
  return words.map((word, index) => ({
    id: `card-${index}`,
    word,
    team: index < 2 ? 'red' : index < 4 ? 'blue' : 'neutral',
    isRevealed: false,
    position: index
  }));
}
