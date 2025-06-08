import express, { Request, Response } from 'express';

const router = express.Router();

// Define proper TypeScript interfaces
interface GameLobbyPlayer {
  id: string;
  username: string;
  team: string;
  role: string;
  isOnline: boolean;
  isOwner: boolean;
}

interface GameLobby {
  id: string;
  code: string;
  owner: string;
  players: GameLobbyPlayer[];
  status: string;
  createdAt: string;
  updatedAt: string;
}

// In-memory storage for game lobbies
const gameLobbies = new Map<string, GameLobby>();

// Generate lobby code
function generateLobbyCode(): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let code = '';
  for (let i = 0; i < 6; i++) {
    code += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  
  if (gameLobbies.has(code)) {
    return generateLobbyCode(); // Try again if exists
  }
  
  return code;
}

// Create game lobby
router.post('/create', (req: Request, res: Response): void => {
  try {
    console.log('🎮 Creating new game lobby...');
    
    const { userId, username } = req.body;
    const lobbyCode = generateLobbyCode();
    
    const gameLobby: GameLobby = {
      id: lobbyCode,
      code: lobbyCode,
      owner: userId || 'anonymous',
      players: [],
      status: 'waiting',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    // Add creator as first player
    if (username && userId) {
      gameLobby.players.push({
        id: userId,
        username,
        team: 'neutral',
        role: 'operative',
        isOnline: true,
        isOwner: true
      });
    }
    
    gameLobbies.set(lobbyCode, gameLobby);
    
    console.log(`✅ Created game lobby: ${lobbyCode}`);
    
    res.json({ 
      success: true, 
      lobbyCode: lobbyCode,
      message: 'Game lobby created successfully!',
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ Error creating game lobby:', error);
    res.status(500).json({ 
      success: false,
      error: 'Failed to create game lobby',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Join game lobby
router.post('/join', (req: Request, res: Response): void => {
  try {
    const { lobbyCode, userId, username } = req.body;
    console.log(`🚪 User ${username} joining game lobby: ${lobbyCode}`);
    
    if (!lobbyCode) {
      res.status(400).json({ 
        success: false,
        error: 'Lobby code is required' 
      });
      return;
    }
    
    const gameLobby = gameLobbies.get(lobbyCode.toUpperCase());
    
    if (!gameLobby) {
      res.status(404).json({ 
        success: false,
        error: 'Game lobby not found' 
      });
      return;
    }
    
    // Add player to lobby if not already there
    if (username && userId) {
      const existingPlayer = gameLobby.players.find((p: GameLobbyPlayer) => p.id === userId);
      if (!existingPlayer) {
        gameLobby.players.push({
          id: userId,
          username,
          team: 'neutral',
          role: 'operative',
          isOnline: true,
          isOwner: false
        });
        gameLobby.updatedAt = new Date().toISOString();
        console.log(`✅ Added ${username} to game lobby ${lobbyCode}`);
      }
    }
    
    res.json({ 
      success: true, 
      lobbyCode: lobbyCode.toUpperCase(),
      message: 'Joined game lobby successfully!',
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ Error joining game lobby:', error);
    res.status(500).json({ 
      success: false,
      error: 'Failed to join game lobby',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Get game lobby info
router.get('/:lobbyCode', (req: Request, res: Response): void => {
  try {
    const { lobbyCode } = req.params;
    console.log(`🔍 Getting game lobby info: ${lobbyCode}`);
    
    if (!lobbyCode) {
      res.status(400).json({ 
        success: false,
        error: 'Lobby code is required' 
      });
      return;
    }
    
    const gameLobby = gameLobbies.get(lobbyCode.toUpperCase());
    
    if (gameLobby) {
      res.json({ 
        success: true, 
        gameLobby: gameLobby,
        timestamp: new Date().toISOString()
      });
    } else {
      res.status(404).json({ 
        success: false,
        error: 'Game lobby not found' 
      });
    }
    
  } catch (error) {
    console.error('❌ Error getting game lobby info:', error);
    res.status(500).json({ 
      success: false,
      error: 'Failed to get game lobby info',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// List all game lobbies
router.get('/', (req: Request, res: Response): void => {
  try {
    console.log('📋 Listing all game lobbies...');
    
    const activeGameLobbies = Array.from(gameLobbies.values()).map(lobby => {
      // Find the owner player to get their username
      const ownerPlayer = lobby.players.find((p: GameLobbyPlayer) => p.isOwner);
      
      return {
        code: lobby.code,
        id: lobby.id,
        status: lobby.status,
        playerCount: lobby.players.length,
        players: lobby.players.map((p: GameLobbyPlayer) => p.username),
        ownerUsername: ownerPlayer?.username || 'Unknown',
        createdAt: lobby.createdAt,
        lastActivity: lobby.updatedAt
      };
    });
    
    // Sort by most recent activity
    activeGameLobbies.sort((a, b) => 
      new Date(b.lastActivity).getTime() - new Date(a.lastActivity).getTime()
    );
    
    res.json({
      success: true,
      gameLobbies: activeGameLobbies,
      total: gameLobbies.size,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ Error listing game lobbies:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to list game lobbies',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

export default router;
export { gameLobbies, GameLobby, GameLobbyPlayer };
