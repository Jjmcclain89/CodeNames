#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fix TypeScript Types
Fixes the TypeScript type errors in games routes by properly defining interfaces
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
    print("🔧 Fixing TypeScript Types in Games Routes...")
    
    # Create properly typed games routes
    typed_games_routes = '''import express, { Request, Response } from 'express';

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

// Test endpoint to verify API is working
router.get('/test', (req: Request, res: Response): void => {
  console.log('🧪 API test endpoint hit!');
  res.json({ 
    success: true, 
    message: 'Games API is working!',
    timestamp: new Date().toISOString()
  });
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
      const response = { 
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
          messages: gameRoom.messages.slice(-20) // Last 20 messages
        },
        timestamp: new Date().toISOString()
      };
      
      console.log('📤 Sending game info:', response);
      res.json(response);
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
    console.log('📦 Request body:', req.body);
    
    const { userId, username } = req.body;
    
    // Generate simple 6-character game code
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let gameCode = '';
    for (let i = 0; i < 6; i++) {
      gameCode += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    
    // Create the game room with proper typing
    const gameRoom: GameRoom = {
      code: gameCode,
      id: `game_${gameCode.toLowerCase()}_${Date.now()}`,
      status: 'waiting',
      players: [],
      messages: [],
      createdAt: new Date().toISOString()
    };
    
    // Add creator as first player if provided
    if (username) {
      const newPlayer: Player = {
        id: userId || `user_${Date.now()}`,
        username: username,
        joinedAt: new Date().toISOString()
      };
      gameRoom.players.push(newPlayer);
    }
    
    gameRooms.set(gameCode, gameRoom);
    
    console.log(`✅ Created game room: ${gameCode} with ${gameRoom.players.length} initial players`);
    
    const response = { 
      success: true, 
      gameCode: gameCode,
      message: 'Game created successfully!',
      game: {
        code: gameCode,
        id: gameRoom.id,
        status: gameRoom.status,
        playerCount: gameRoom.players.length
      },
      timestamp: new Date().toISOString()
    };
    
    console.log('📤 Sending response:', response);
    res.json(response);
    
  } catch (error) {
    console.error('❌ Error in /api/games/create:', error);
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
    console.log(`🚪 POST /api/games/join - User ${username} joining game: ${gameCode}`);
    
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
    
    // Add player to game if not already in it
    if (username && !gameRoom.players.find(p => p.username === username)) {
      const newPlayer: Player = {
        id: userId || `user_${Date.now()}`,
        username: username,
        joinedAt: new Date().toISOString()
      };
      gameRoom.players.push(newPlayer);
      
      console.log(`✅ Added player ${username} to game ${gameCode}. Total players: ${gameRoom.players.length}`);
    }
    
    const response = { 
      success: true, 
      gameCode: gameCode.toUpperCase(),
      message: 'Joined game successfully!',
      game: {
        code: gameRoom.code,
        id: gameRoom.id,
        status: gameRoom.status,
        playerCount: gameRoom.players.length
      },
      timestamp: new Date().toISOString()
    };
    
    console.log('📤 Sending response:', response);
    res.json(response);
    
  } catch (error) {
    console.error('❌ Error in /api/games/join:', error);
    res.status(500).json({ 
      success: false,
      error: 'Failed to join game',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Export gameRooms for use in socket handlers
export { gameRooms };
export default router;
'''

    # Update the games routes file
    games_route_path = 'backend/src/routes/games.ts'
    if update_file_content(games_route_path, typed_games_routes):
        print("✅ Fixed TypeScript types in backend/src/routes/games.ts")
    else:
        print("❌ Failed to fix games routes file")
        return
    
    # Update changelog
    try:
        changelog_path = 'CHANGELOG.md'
        with open(changelog_path, 'r', encoding='utf-8') as f:
            changelog = f.read()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        new_entry = f'- TypeScript Types Fix: Fixed type definitions and interfaces in games routes ({timestamp})'
        
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
    
    print(f"\n🎉 TypeScript Types Fix Complete!")
    print("\n🔧 What was fixed:")
    print("• Added proper TypeScript interfaces for Player, RoomMessage, GameRoom")
    print("• Fixed players array typing from 'never[]' to 'Player[]'")
    print("• Added explicit type annotations for player objects")
    print("• Maintained all existing functionality with proper types")
    print("\n🎯 Next Steps:")
    print("1. Backend should now compile without TypeScript errors")
    print("2. Don't forget to add the socket handlers to backend index.ts (manual step)")
    print("3. Restart backend server")
    print("4. Test game creation and joining with proper multiplayer!")

if __name__ == "__main__":
    main()
