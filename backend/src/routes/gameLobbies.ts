import express, { Request, Response } from 'express';


// Extend Request interface to include io instance
interface RequestWithIo extends Request {
  io?: any;
}
const router = express.Router();

// Define proper TypeScript interfaces using new team structure
interface Player {
  id: string;
  username: string;
  isOnline: boolean;
  socketId?: string;
}

interface Team {
  spymaster?: Player;
  operatives: Player[];
}

interface GameLobby {
  id: string;
  code: string;
  owner: string;
  ownerUsername: string;  // Store owner username directly
  redTeam?: Team;
  blueTeam?: Team;
  status: string;
  createdAt: string;
  updatedAt: string;
}

// In-memory storage for game lobbies
const gameLobbies = new Map<string, GameLobby>();

// Helper function to get all players from both teams
function getAllPlayers(lobby: GameLobby): Player[] {
  const players: Player[] = [];
  
  if (lobby.redTeam) {
    if (lobby.redTeam.spymaster) players.push(lobby.redTeam.spymaster);
    players.push(...lobby.redTeam.operatives);
  }
  
  if (lobby.blueTeam) {
    if (lobby.blueTeam.spymaster) players.push(lobby.blueTeam.spymaster);
    players.push(...lobby.blueTeam.operatives);
  }
  
  return players;
}

// Helper function to find owner
function findOwner(lobby: GameLobby): { username: string; id: string } | undefined {
  // First, try to find the owner in the teams (if they've joined a team)
  const allPlayers = getAllPlayers(lobby);
  const ownerInTeam = allPlayers.find(player => player.id === lobby.owner);
  
  if (ownerInTeam) {
    return { username: ownerInTeam.username, id: ownerInTeam.id };
  }
  
  // If owner hasn't joined a team yet, use the stored owner username
  if (lobby.ownerUsername) {
    return { username: lobby.ownerUsername, id: lobby.owner };
  }
  
  return undefined;
}

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
router.post('/create', (req: RequestWithIo, res: Response): void => {
  try {
    console.log('🎮 Creating new game lobby...');
    
    const { userId, username } = req.body;
    const lobbyCode = generateLobbyCode();
    
    const gameLobby: GameLobby = {
      id: lobbyCode,
      code: lobbyCode,
      owner: userId || 'anonymous',
      ownerUsername: username || 'Anonymous',  // Store the owner's username
      status: 'waiting',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    // Creator will join a team through the UI later
    
    gameLobbies.set(lobbyCode, gameLobby);
    
    console.log(`✅ Created game lobby: ${lobbyCode}`);
    
    // 📡 BROADCAST: Notify all users about the new lobby
    try {
      if (req.io) {
        const newLobbyData = {
          code: gameLobby.code,
          id: gameLobby.id,
          status: gameLobby.status,
          playerCount: 0,
          players: [],
          ownerUsername: gameLobby.ownerUsername,
          createdAt: gameLobby.createdAt,
          lastActivity: gameLobby.updatedAt
        };
        
        req.io.to('GLOBAL').emit('lobby:created', {
          lobby: newLobbyData,
          message: `New lobby ${lobbyCode} created by ${username || 'Anonymous'}`
        });
        console.log(`📡 SUCCESS: Broadcasted lobby:created for ${lobbyCode} to GLOBAL room`);
        console.log(`📡 Lobby data:`, JSON.stringify(newLobbyData, null, 2));
      } else {
        console.log(`❌ ERROR: req.io not available when creating lobby ${lobbyCode}`);
      }
    } catch (error) {
      console.error(`❌ ERROR broadcasting lobby:created for ${lobbyCode}:`, error);
    }
    
    // 📡 BROADCAST: Notify all users about the new lobby
    try {
      if (req.io) {
        const newLobbyData = {
          code: gameLobby.code,
          id: gameLobby.id,
          status: gameLobby.status,
          playerCount: 0,
          players: [],
          ownerUsername: gameLobby.ownerUsername,
          createdAt: gameLobby.createdAt,
          lastActivity: gameLobby.updatedAt
        };
        
        req.io.to('GLOBAL').emit('lobby:created', {
          lobby: newLobbyData,
          message: `New lobby ${lobbyCode} created by ${username || 'Anonymous'}`
        });
        console.log(`📡 SUCCESS: Broadcasted lobby:created for ${lobbyCode} to GLOBAL room`);
        console.log(`📡 Lobby data:`, JSON.stringify(newLobbyData, null, 2));
      } else {
        console.log(`❌ ERROR: req.io not available when creating lobby ${lobbyCode}`);
      }
    } catch (error) {
      console.error(`❌ ERROR broadcasting lobby:created for ${lobbyCode}:`, error);
    }
    
    // 📡 BROADCAST: Notify all users about the new lobby
    if (req.io) {
      req.io.to('GLOBAL').emit('lobby:created', {
        lobby: {
          code: gameLobby.code,
          id: gameLobby.id,
          status: gameLobby.status,
          playerCount: 0,
          players: [],
          ownerUsername: gameLobby.ownerUsername,
          createdAt: gameLobby.createdAt,
          lastActivity: gameLobby.updatedAt
        },
        message: `New lobby ${lobbyCode} created by ${username || 'Anonymous'}`
      });
      console.log(`📡 Broadcasted lobby:created for ${lobbyCode} to all users`);
    }
    
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
    
    // Check if player is already in the lobby
    if (username && userId) {
      const allPlayers = getAllPlayers(gameLobby);
      const existingPlayer = allPlayers.find(p => p.id === userId);
      if (!existingPlayer) {
        // Don't add them to any team yet - they'll join through the UI
        console.log(`✅ Player ${username} can join lobby ${lobbyCode}`);
      }
      gameLobby.updatedAt = new Date().toISOString();
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
    
    const activeGameLobbies = Array.from(gameLobbies.values())
    .filter(lobby => lobby.status !== 'closed') // 🔒 Filter out closed lobbies
    .map(lobby => {
      const allPlayers = getAllPlayers(lobby);
      const owner = findOwner(lobby);
      
      return {
        code: lobby.code,
        id: lobby.id,
        status: lobby.status,
        playerCount: allPlayers.length,
        players: allPlayers.map(p => p.username),
        ownerUsername: owner?.username || 'Anonymous',  // Better fallback
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


// 🔒 LOBBY STATE MANAGEMENT UTILITIES

// Clean up old closed lobbies (older than specified hours)
function cleanupOldClosedLobbies(maxAgeHours: number = 24): number {
  const cutoffTime = new Date(Date.now() - maxAgeHours * 60 * 60 * 1000);
  let cleanedCount = 0;
  
  for (const [lobbyCode, lobby] of gameLobbies.entries()) {
    if (lobby.status === 'closed') {
      const lastActivity = new Date(lobby.updatedAt);
      if (lastActivity < cutoffTime) {
        gameLobbies.delete(lobbyCode);
        cleanedCount++;
        console.log(`🧹 Cleaned up old closed lobby: ${lobbyCode}`);
      }
    }
  }
  
  if (cleanedCount > 0) {
    console.log(`🧹 Cleaned up ${cleanedCount} old closed lobbies`);
  }
  
  return cleanedCount;
}

// Get lobby statistics
function getLobbyStats(): { total: number; waiting: number; closed: number } {
  let waiting = 0;
  let closed = 0;
  
  for (const lobby of gameLobbies.values()) {
    if (lobby.status === 'waiting') {
      waiting++;
    } else if (lobby.status === 'closed') {
      closed++;
    }
  }
  
  return {
    total: gameLobbies.size,
    waiting,
    closed
  };
}

// Schedule periodic cleanup of old closed lobbies
function scheduleClosedLobbyCleanup(): void {
  // Clean up old closed lobbies every hour
  setInterval(() => {
    console.log('🧹 Running periodic closed lobby cleanup...');
    const cleanedCount = cleanupOldClosedLobbies(24); // Keep closed lobbies for 24 hours
    
    if (cleanedCount === 0) {
      console.log('🧹 No old closed lobbies to clean up');
    }
    
    // Log current lobby stats
    const stats = getLobbyStats();
    console.log(`📊 Lobby stats: ${stats.waiting} waiting, ${stats.closed} closed, ${stats.total} total`);
  }, 60 * 60 * 1000); // Every hour
}


export default router;
export { gameLobbies, GameLobby, Player, Team, cleanupOldClosedLobbies, getLobbyStats, scheduleClosedLobbyCleanup };
