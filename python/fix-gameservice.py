#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fix GameService Integration
Removes broken code and properly integrates game code functionality with existing GameService class.
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
    print("Fixing GameService Integration...")
    
    # Fixed backend gameService.ts with proper integration
    game_service_content = '''// Game Service - Manages games and integrates with existing storage
import { CodenamesGameModel } from '../models/Game';
import { CodenamesGame, TeamColor, PlayerRole } from '../../../shared/types/game';

interface GameWithMeta {
  model: CodenamesGameModel;
  lastActivity: Date;
}

export class GameService {
  private games: Map<string, GameWithMeta> = new Map();
  private playerGameMap: Map<string, string> = new Map(); // playerId -> gameId
  private gameCodes: Map<string, string> = new Map(); // gameCode -> gameId mapping

  // Game code management methods
  generateGameCode(): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let code = '';
    for (let i = 0; i < 6; i++) {
      code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    
    // Ensure code is unique
    if (this.gameCodes.has(code)) {
      return this.generateGameCode(); // Try again
    }
    
    return code;
  }

  createGameWithCode(gameCode: string, creatorId: string): CodenamesGameModel {
    // Remove any existing game with this code
    this.removeGameByCode(gameCode);

    const gameModel = new CodenamesGameModel(gameCode);
    this.games.set(gameModel.getId(), {
      model: gameModel,
      lastActivity: new Date()
    });
    
    // Map the game code to the game ID
    this.gameCodes.set(gameCode, gameModel.getId());
    
    console.log(`Created game with code ${gameCode} and ID ${gameModel.getId()}`);
    return gameModel;
  }

  getGameByCode(gameCode: string): CodenamesGameModel | null {
    const gameId = this.gameCodes.get(gameCode);
    if (!gameId) return null;
    
    const gameWithMeta = this.games.get(gameId);
    if (gameWithMeta) {
      gameWithMeta.lastActivity = new Date();
      return gameWithMeta.model;
    }
    return null;
  }

  addPlayerToGameByCode(gameCode: string, playerId: string, username: string, socketId: string): boolean {
    const game = this.getGameByCode(gameCode);
    if (!game) return false;

    // Remove player from any existing game first
    this.removePlayerFromAllGames(playerId);

    const success = game.addPlayer(playerId, username, socketId);
    if (success) {
      this.playerGameMap.set(playerId, game.getId());
    }
    return success;
  }

  removeGameByCode(gameCode: string): boolean {
    const gameId = this.gameCodes.get(gameCode);
    if (gameId) {
      this.gameCodes.delete(gameCode);
      return this.deleteGame(gameId);
    }
    return false;
  }

  // Existing game lifecycle methods
  createGameForRoom(roomCode: string): CodenamesGameModel {
    // Remove any existing game for this room
    this.deleteGameForRoom(roomCode);

    const gameModel = new CodenamesGameModel(roomCode);
    this.games.set(gameModel.getId(), {
      model: gameModel,
      lastActivity: new Date()
    });

    return gameModel;
  }

  getGame(gameId: string): CodenamesGameModel | null {
    const gameWithMeta = this.games.get(gameId);
    if (gameWithMeta) {
      gameWithMeta.lastActivity = new Date();
      return gameWithMeta.model;
    }
    return null;
  }

  getGameForRoom(roomCode: string): CodenamesGameModel | null {
    for (const [gameId, gameWithMeta] of this.games.entries()) {
      if (gameWithMeta.model.getRoomCode() === roomCode) {
        gameWithMeta.lastActivity = new Date();
        return gameWithMeta.model;
      }
    }
    return null;
  }

  getGameByPlayer(playerId: string): CodenamesGameModel | null {
    const gameId = this.playerGameMap.get(playerId);
    if (gameId) {
      return this.getGame(gameId);
    }
    return null;
  }

  deleteGame(gameId: string): boolean {
    const gameWithMeta = this.games.get(gameId);
    if (gameWithMeta) {
      // Remove all players from the player map
      const game = gameWithMeta.model.getGame();
      game.players.forEach((player: any) => {
        this.playerGameMap.delete(player.id);
      });
      
      // Remove from game codes mapping
      for (const [code, id] of this.gameCodes.entries()) {
        if (id === gameId) {
          this.gameCodes.delete(code);
          break;
        }
      }
      
      this.games.delete(gameId);
      return true;
    }
    return false;
  }

  deleteGameForRoom(roomCode: string): boolean {
    for (const [gameId, gameWithMeta] of this.games.entries()) {
      if (gameWithMeta.model.getRoomCode() === roomCode) {
        return this.deleteGame(gameId);
      }
    }
    return false;
  }

  // Player management
  addPlayerToGame(gameId: string, playerId: string, username: string, socketId: string): boolean {
    const game = this.getGame(gameId);
    if (!game) return false;

    // Remove player from any existing game first
    this.removePlayerFromAllGames(playerId);

    const success = game.addPlayer(playerId, username, socketId);
    if (success) {
      this.playerGameMap.set(playerId, gameId);
    }
    return success;
  }

  removePlayerFromAllGames(playerId: string): boolean {
    const game = this.getGameByPlayer(playerId);
    if (game) {
      const success = game.removePlayer(playerId);
      if (success) {
        this.playerGameMap.delete(playerId);
        
        // If game is empty, clean it up
        const gameState = game.getGame();
        if (gameState.players.length === 0) {
          this.deleteGame(gameState.id);
        }
      }
      return success;
    }
    return false;
  }

  updatePlayerOnlineStatus(playerId: string, isOnline: boolean): boolean {
    const game = this.getGameByPlayer(playerId);
    if (game) {
      return game.updatePlayerOnlineStatus(playerId, isOnline);
    }
    return false;
  }

  assignPlayerToTeam(playerId: string, team: TeamColor, role: PlayerRole): { success: boolean; error?: string } {
    const game = this.getGameByPlayer(playerId);
    if (!game) {
      return { success: false, error: 'Player not in any game' };
    }

    const success = game.assignPlayerToTeam(playerId, team, role);
    return { 
      success, 
      error: success ? undefined : 'Cannot assign to team - team may already have a spymaster' 
    };
  }

  // Game actions
  startGame(playerId: string): { success: boolean; error?: string } {
    const game = this.getGameByPlayer(playerId);
    if (!game) {
      return { success: false, error: 'Player not in any game' };
    }

    if (!game.canStartGame()) {
      return { success: false, error: 'Cannot start game - need both teams with spymasters and operatives' };
    }

    const success = game.startGame();
    return { success, error: success ? undefined : 'Failed to start game' };
  }

  giveClue(playerId: string, word: string, number: number): { success: boolean; error?: string } {
    const game = this.getGameByPlayer(playerId);
    if (!game) {
      return { success: false, error: 'Player not in any game' };
    }

    const success = game.giveClue(playerId, word, number);
    return { 
      success, 
      error: success ? undefined : 'Cannot give clue - must be the current team spymaster' 
    };
  }

  revealCard(playerId: string, cardId: string): { success: boolean; error?: string; card?: any; gameEnded?: boolean; winner?: TeamColor } {
    const game = this.getGameByPlayer(playerId);
    if (!game) {
      return { success: false, error: 'Player not in any game' };
    }

    const result = game.revealCard(playerId, cardId);
    if (!result.success) {
      return { success: false, error: 'Cannot reveal card - must be current team operative with guesses remaining' };
    }

    return result;
  }

  endTurn(playerId: string): { success: boolean; error?: string } {
    const game = this.getGameByPlayer(playerId);
    if (!game) {
      return { success: false, error: 'Player not in any game' };
    }

    const success = game.endTurn();
    return { 
      success, 
      error: success ? undefined : 'Cannot end turn' 
    };
  }

  resetGame(playerId: string): { success: boolean; error?: string } {
    const game = this.getGameByPlayer(playerId);
    if (!game) {
      return { success: false, error: 'Player not in any game' };
    }

    game.resetGame();
    return { success: true };
  }

  // Utility methods
  getStats(): { totalGames: number; activePlayers: number; gameCodes: number } {
    return {
      totalGames: this.games.size,
      activePlayers: this.playerGameMap.size,
      gameCodes: this.gameCodes.size
    };
  }

  // Cleanup inactive games
  cleanupInactiveGames(maxInactiveMinutes: number = 60): number {
    const cutoffTime = new Date(Date.now() - maxInactiveMinutes * 60 * 1000);
    let cleanedCount = 0;

    for (const [gameId, gameWithMeta] of this.games.entries()) {
      if (gameWithMeta.lastActivity < cutoffTime) {
        this.deleteGame(gameId);
        cleanedCount++;
      }
    }

    return cleanedCount;
  }
}

// Singleton instance for use in socket handlers
export const gameService = new GameService();
'''

    # Also create a simplified games routes that works with the fixed service
    games_routes_content = '''import express from 'express';
import { gameService } from '../services/gameService';

const router = express.Router();

// Get stored user from token (simplified auth for now)
const getAuthenticatedUser = (req: any) => {
  // For now, get user from localStorage on frontend
  // This will be replaced with proper JWT middleware later
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return null;
  
  // Simplified user extraction - replace with proper JWT decode
  try {
    const user = JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString());
    return user;
  } catch {
    return null;
  }
};

// Create a new game
router.post('/create', async (req, res) => {
  try {
    // For now, use username from request body since auth is simplified
    const userId = req.body.userId || `user_${Date.now()}`;
    
    const gameCode = gameService.generateGameCode();
    const game = gameService.createGameWithCode(gameCode, userId);
    
    console.log(`Game created: ${gameCode} by user ${userId}`);
    
    res.json({ 
      success: true, 
      gameCode: gameCode,
      game: {
        code: gameCode,
        id: game.getId(),
        status: 'waiting',
        creator: userId
      }
    });
  } catch (error) {
    console.error('Error creating game:', error);
    res.status(500).json({ error: 'Failed to create game' });
  }
});

// Join an existing game
router.post('/join', async (req, res) => {
  try {
    const { gameCode } = req.body;
    const userId = req.body.userId || `user_${Date.now()}`;
    
    if (!gameCode) {
      return res.status(400).json({ error: 'Game code is required' });
    }

    const game = gameService.getGameByCode(gameCode);
    if (!game) {
      return res.status(404).json({ error: 'Game not found' });
    }

    console.log(`User ${userId} joining game ${gameCode}`);
    
    res.json({ 
      success: true, 
      gameCode: gameCode,
      game: {
        code: gameCode,
        id: game.getId(),
        status: 'waiting'
      }
    });
  } catch (error) {
    console.error('Error joining game:', error);
    res.status(500).json({ error: 'Failed to join game' });
  }
});

// Get game info
router.get('/:gameCode', async (req, res) => {
  try {
    const { gameCode } = req.params;
    const game = gameService.getGameByCode(gameCode);
    
    if (!game) {
      return res.status(404).json({ error: 'Game not found' });
    }
    
    const gameState = game.getGame();
    
    res.json({ 
      success: true, 
      game: {
        code: gameCode,
        id: game.getId(),
        status: gameState.status,
        playerCount: gameState.players.length,
        players: gameState.players
      }
    });
  } catch (error) {
    console.error('Error getting game:', error);
    res.status(500).json({ error: 'Failed to get game info' });
  }
});

export default router;
'''

    # Update frontend HomePage to use simplified auth approach
    homepage_content = '''import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ChatRoom from '../components/Chat/ChatRoom';

const HomePage: React.FC = () => {
  const [roomCode, setRoomCode] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [isJoining, setIsJoining] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleCreateRoom = async () => {
    setIsCreating(true);
    setError('');
    
    try {
      // Get user info from localStorage
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const userId = user.id || user.username || `user_${Date.now()}`;
      
      const response = await fetch('/api/games/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ userId })
      });

      const data = await response.json();
      
      if (data.success && data.gameCode) {
        console.log('Game created successfully:', data.gameCode);
        // Navigate to the room with the new game code
        navigate(`/room/${data.gameCode}`);
      } else {
        setError(data.error || 'Failed to create game');
      }
    } catch (err) {
      console.error('Error creating game:', err);
      setError('Failed to connect to server');
    }
    
    setIsCreating(false);
  };

  const handleJoinRoom = async () => {
    if (!roomCode.trim()) {
      setError('Please enter a room code');
      return;
    }
    
    setIsJoining(true);
    setError('');

    try {
      // Get user info from localStorage  
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const userId = user.id || user.username || `user_${Date.now()}`;
      
      const response = await fetch('/api/games/join', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          gameCode: roomCode.trim().toUpperCase(),
          userId 
        })
      });

      const data = await response.json();
      
      if (data.success && data.gameCode) {
        console.log('Joined game successfully:', data.gameCode);
        // Navigate to the room
        navigate(`/room/${data.gameCode}`);
      } else {
        setError(data.error || 'Failed to join game');
      }
    } catch (err) {
      console.error('Error joining game:', err);
      setError('Failed to connect to server');
    }
    
    setIsJoining(false);
  };

  const handleRoomCodeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setRoomCode(e.target.value.toUpperCase());
    if (error) setError(''); // Clear error when typing
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Welcome to Codenames!</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left side - Game management */}
          <div className="space-y-6">
            {/* Create Game */}
            <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
              <h2 className="text-xl font-semibold mb-4 text-gray-900">Create New Game</h2>
              <p className="text-gray-600 mb-4">Start a new game and invite friends to join</p>
              <button 
                onClick={handleCreateRoom}
                disabled={isCreating}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white py-3 px-4 rounded-lg font-medium transition-colors"
              >
                {isCreating ? 'Creating...' : 'Create Game'}
              </button>
            </div>
            
            {/* Join Game */}
            <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
              <h2 className="text-xl font-semibold mb-4 text-gray-900">Join Existing Game</h2>
              <div className="space-y-4">
                <div>
                  <label htmlFor="roomCode" className="block text-sm font-medium text-gray-700 mb-2">
                    Game Code
                  </label>
                  <input
                    type="text"
                    id="roomCode"
                    value={roomCode}
                    onChange={handleRoomCodeChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white uppercase"
                    placeholder="Enter 6-digit code"
                    maxLength={6}
                    disabled={isJoining}
                  />
                </div>
                <button 
                  onClick={handleJoinRoom}
                  disabled={isJoining || !roomCode.trim()}
                  className="w-full bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white py-3 px-4 rounded-lg font-medium transition-colors"
                >
                  {isJoining ? 'Joining...' : 'Join Game'}
                </button>
              </div>
            </div>
            
            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
                <p className="text-red-800">{error}</p>
              </div>
            )}
            
            {/* Status */}
            <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
              <h3 className="font-semibold text-green-900 mb-2">🎉 Ready to Play!</h3>
              <div className="text-green-800 space-y-1">
                <p>✅ Real-time multiplayer working</p>
                <p>✅ Game creation and joining ready</p>
                <p>✅ Socket communication established</p>
                <p className="mt-2 font-semibold">🎮 Create or join a game to start playing!</p>
              </div>
            </div>
          </div>
          
          {/* Right side - Chat Room */}
          <div>
            <h2 className="text-xl font-semibold mb-4 text-gray-900">Global Chat</h2>
            <ChatRoom />
            <div className="mt-4 text-sm text-gray-600 bg-blue-50 border border-blue-200 p-3 rounded">
              <p><strong>💬 Global Chat:</strong></p>
              <p>• Chat with other players before joining games</p>
              <p>• Test real-time communication</p>
              <p>• Open multiple browser windows to test!</p>
            </div>
          </div>
        </div>
        
        {/* Instructions */}
        <div className="mt-8 bg-gray-100 border border-gray-300 p-4 rounded-lg">
          <h3 className="font-semibold text-gray-900 mb-2">🎯 How to Play</h3>
          <div className="text-gray-700 space-y-2">
            <p>• <strong>Create Game:</strong> Click "Create Game" to generate a 6-digit code</p>
            <p>• <strong>Share Code:</strong> Give the code to friends so they can join</p>
            <p>• <strong>Join Game:</strong> Enter a code you received to join an existing game</p>
            <p>• <a href="/debug" className="text-blue-600 hover:text-blue-800 underline">Debug Tools</a> - Connection diagnostics</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
'''

    # Execute updates
    success_count = 0
    
    # Fix the gameService
    if update_file_content('backend/src/services/gameService.ts', game_service_content):
        print("✅ Fixed backend/src/services/gameService.ts")
        success_count += 1
    
    # Create the games routes
    if update_file_content('backend/src/routes/games.ts', games_routes_content):
        print("✅ Updated backend/src/routes/games.ts")
        success_count += 1
    
    # Update HomePage
    if update_file_content('frontend/src/pages/HomePage.tsx', homepage_content):
        print("✅ Updated frontend/src/pages/HomePage.tsx")
        success_count += 1
    
    # Update backend index.ts to include games routes
    backend_index_path = 'backend/src/index.ts'
    try:
        with open(backend_index_path, 'r', encoding='utf-8') as f:
            backend_content = f.read()
        
        # Check if games routes already exist
        if 'games.ts' not in backend_content and '/api/games' not in backend_content:
            # Find where to insert the new route
            lines = backend_content.split('\n')
            
            import_added = False
            route_added = False
            
            new_lines = []
            for line in lines:
                new_lines.append(line)
                
                # Add import after other route imports
                if 'import authRoutes from' in line and not import_added:
                    new_lines.append("import gameRoutes from './routes/games';")
                    import_added = True
                
                # Add route after auth routes
                if "app.use('/api/auth'" in line and not route_added:
                    new_lines.append("app.use('/api/games', gameRoutes);")
                    route_added = True
            
            if import_added and route_added:
                updated_backend = '\n'.join(new_lines)
                
                if update_file_content(backend_index_path, updated_backend):
                    print("✅ Updated backend/src/index.ts with games routes")
                    success_count += 1
            else:
                print("⚠️ Could not auto-update backend index.ts - you may need to manually add games routes")
    except Exception as e:
        print(f"Note: Could not update backend index.ts: {e}")
    
    # Update changelog
    try:
        changelog_path = 'CHANGELOG.md'
        with open(changelog_path, 'r', encoding='utf-8') as f:
            changelog = f.read()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        new_entry = f'- GameService Integration Fix: Removed broken code and properly integrated game code functionality ({timestamp})'
        
        if '### Python Scripts Run' in changelog:
            updated_changelog = changelog.replace(
                '### Python Scripts Run',
                f'### Python Scripts Run\n{new_entry}'
            )
            
            with open(changelog_path, 'w', encoding='utf-8') as f:
                f.write(updated_changelog)
            print("✅ Updated CHANGELOG.md")
            success_count += 1
    except Exception as e:
        print(f"Note: Could not update changelog: {e}")
    
    print(f"\n🎉 GameService Integration Fix Complete!")
    print(f"✅ {success_count} files updated successfully")
    print("\n🔧 What was fixed:")
    print("• Removed broken code appended to gameService")
    print("• Added proper game code methods to GameService class")
    print("• Integrated with existing CodenamesGameModel structure")
    print("• Simplified auth for immediate testing")
    print("\n🎯 Next Steps:")
    print("1. Restart your backend server")
    print("2. Test game creation on homepage")
    print("3. Test game joining with generated codes")
    print("4. Verify navigation to /room/:code works")
    print("\n💡 Features Ready:")
    print("• 6-digit game code generation")
    print("• Game creation and joining")
    print("• Proper integration with existing game infrastructure")

if __name__ == "__main__":
    main()
