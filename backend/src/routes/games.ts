import express, { Request, Response } from 'express';

const router = express.Router();

// Type definitions
interface Player {
  id: string;
  username: string;
  socketId?: string;
  joinedAt: string;
}

interface RoomMessage {
  id: string;
  username: string;
  userId: string;
  text: string;
  timestamp: string;
}

interface GameRoom {
  code: string;
  id: string;
  status: string;
  players: Player[];
  messages: RoomMessage[];
  createdAt: string;
}

// In-memory storage for games and players
const gameRooms = new Map<string, GameRoom>();

// Test endpoint
router.get('/test', (req: Request, res: Response): void => {
  console.log('🧪 API test endpoint hit!');
  res.json({ 
    success: true, 
    message: 'Games API is working!',
    timestamp: new Date().toISOString()
  });
});

// List all active games - SIMPLIFIED
router.get('/', (req: Request, res: Response): void => {
  try {
    console.log('📋 GET /api/games - Listing all games...');
    
    const games = Array.from(gameRooms.values()).map(room => ({
      code: room.code,
      id: room.id,
      status: room.status,
      playerCount: room.players.length,
      players: room.players.map(p => p.username),
      createdAt: room.createdAt,
      lastActivity: room.createdAt  // Simplified to avoid TS errors
    }));
    
    console.log(`📤 Found ${games.length} active games`);
    
    res.json({
      success: true,
      games: games,
      total: games.length,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ Error listing games:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to list games',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Get game info by code
router.get('/:gameCode', (req: Request, res: Response): void => {
  try {
    const { gameCode } = req.params;
    console.log(`🔍 GET /api/games/${gameCode} - Getting game info...`);
    
    if (!gameCode) {
      res.status(400).json({ 
        success: false,
        error: 'Game code is required' 
      });
      return;
    }
    
    const gameRoom = gameRooms.get(gameCode.toUpperCase());
    
    if (gameRoom) {
      res.json({ 
        success: true, 
        game: {
          code: gameRoom.code,
          id: gameRoom.id,
          status: gameRoom.status,
          playerCount: gameRoom.players.length,
          players: gameRoom.players.map(p => ({
            id: p.id,
            username: p.username,
            joinedAt: p.joinedAt
          })),
          messages: gameRoom.messages.slice(-20)
        },
        timestamp: new Date().toISOString()
      });
    } else {
      res.status(404).json({ 
        success: false,
        error: 'Game not found' 
      });
    }
    
  } catch (error) {
    console.error('❌ Error in /api/games/:gameCode:', error);
    res.status(500).json({ 
      success: false,
      error: 'Failed to get game info',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Create a new game
router.post('/create', (req: Request, res: Response): void => {
  try {
    console.log('🎮 POST /api/games/create - Creating new game...');
    
    const { userId, username } = req.body;
    
    // Generate game code
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let gameCode = '';
    for (let i = 0; i < 6; i++) {
      gameCode += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    
    // Create game room
    const gameRoom: GameRoom = {
      code: gameCode,
      id: `game_${gameCode.toLowerCase()}_${Date.now()}`,
      status: 'waiting',
      players: [],
      messages: [],
      createdAt: new Date().toISOString()
    };
    
    // Add creator if provided
    if (username) {
      gameRoom.players.push({
        id: userId || `user_${Date.now()}`,
        username: username,
        joinedAt: new Date().toISOString()
      });
    }
    
    gameRooms.set(gameCode, gameRoom);
    
    console.log(`✅ Created game: ${gameCode}`);
    
    res.json({ 
      success: true, 
      gameCode: gameCode,
      message: 'Game created successfully!',
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ Error creating game:', error);
    res.status(500).json({ 
      success: false,
      error: 'Failed to create game',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Join an existing game
router.post('/join', (req: Request, res: Response): void => {
  try {
    const { gameCode, userId, username } = req.body;
    console.log(`🚪 User ${username} joining game: ${gameCode}`);
    
    if (!gameCode) {
      res.status(400).json({ 
        success: false,
        error: 'Game code is required' 
      });
      return;
    }
    
    const gameRoom = gameRooms.get(gameCode.toUpperCase());
    
    if (!gameRoom) {
      res.status(404).json({ 
        success: false,
        error: 'Game not found' 
      });
      return;
    }
    
    // Add player if not already in game
    if (username && !gameRoom.players.find(p => p.username === username)) {
      gameRoom.players.push({
        id: userId || `user_${Date.now()}`,
        username: username,
        joinedAt: new Date().toISOString()
      });
      
      console.log(`✅ Added ${username} to game ${gameCode}`);
    }
    
    res.json({ 
      success: true, 
      gameCode: gameCode.toUpperCase(),
      message: 'Joined game successfully!',
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ Error joining game:', error);
    res.status(500).json({ 
      success: false,
      error: 'Failed to join game',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Export gameRooms for socket handlers
export { gameRooms };
export default router;
