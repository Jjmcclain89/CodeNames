import express, { Request, Response } from 'express';
import { gameService } from '../services/gameService';

const router = express.Router();

// Test endpoint
router.get('/test', (req: Request, res: Response): void => {
  console.log('🧪 API test endpoint hit!');
  res.json({ 
    success: true, 
    message: 'Games API is working!',
    timestamp: new Date().toISOString()
  });
});

// List all active games - using gameService
router.get('/', (req: Request, res: Response): void => {
  try {
    console.log('📋 GET /api/games - Listing all games...');
    
    const stats = gameService.getStats();
    const activeGames = gameService.getAllActiveGames();
    
    console.log(`📤 Found ${stats.totalGames} active games`);
    
    res.json({
      success: true,
      games: activeGames, // Return actual active games
      total: stats.totalGames,
      stats: stats,
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

// Get game info by code - using gameService
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
    
    let game = gameService.getGameByCode(gameCode.toUpperCase());
    
    // Fallback: try getGameForRoom if getGameByCode fails (for lobby-created games)
    if (!game) {
      console.log(`Game ${gameCode} not found via getGameByCode, trying getGameForRoom...`);
      game = gameService.getGameForRoom(gameCode.toUpperCase());
      
      if (game) {
        console.log(`Found game ${gameCode} via getGameForRoom, repairing mapping...`);
        // Fix the mapping for future requests
        (gameService as any).gameCodes.set(gameCode.toUpperCase(), game.getId());
      }
    }
    
    if (game) {
      const gameState = game.getGame();
      
      
      
      
      
      // Return full game state for GameBoard component
      const responseData = { 
        success: true, 
        game: {
          ...gameState,  // Include ALL game state data
          code: gameCode.toUpperCase(),  // Ensure code is uppercase
        },
        timestamp: new Date().toISOString()
      };
      
      
      res.json(responseData);
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

// Create a new game - using gameService
router.post('/create', (req: Request, res: Response): void => {
  try {
    console.log('🎮 POST /api/games/create - Creating new game...');
    
    const { userId, username } = req.body;
    
    // Generate game code using gameService
    const gameCode = gameService.generateGameCode();
    
    // Create game using gameService
    const game = gameService.createGameWithCode(gameCode, userId || 'anonymous');
    
    // Add creator if provided
    if (username && userId) {
      gameService.addPlayerToGameByCode(gameCode, userId, username, '');
    }
    
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

// Join an existing game - using gameService
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
    
    let game = gameService.getGameByCode(gameCode.toUpperCase());
    
    // Fallback: try getGameForRoom if getGameByCode fails (for lobby-created games)
    if (!game) {
      console.log(`Game ${gameCode} not found via getGameByCode, trying getGameForRoom...`);
      game = gameService.getGameForRoom(gameCode.toUpperCase());
      
      if (game) {
        console.log(`Found game ${gameCode} via getGameForRoom, repairing mapping...`);
        // Fix the mapping for future requests
        (gameService as any).gameCodes.set(gameCode.toUpperCase(), game.getId());
      }
    }
    
    if (!game) {
      res.status(404).json({ 
        success: false,
        error: 'Game not found' 
      });
      return;
    }
    
    // Add player to game using gameService
    if (username && userId) {
      const success = gameService.addPlayerToGameByCode(gameCode.toUpperCase(), userId, username, '');
      
      if (success) {
        console.log(`✅ Added ${username} to game ${gameCode}`);
      } else {
        console.log(`ℹ️ ${username} already in game ${gameCode}`);
      }
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

export default router;
