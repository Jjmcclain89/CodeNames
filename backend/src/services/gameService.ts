// Game Service - Manages games and integrates with existing storage
import { CodenamesGameModel } from '../models/Game';
import { CodenamesGame, TeamColor, PlayerRole, getAllPlayers, getPlayerTeam, getPlayerRole, isTeamValid, isSoloMode } from '../../../shared/types/game';

interface GameWithMeta {
  model: CodenamesGameModel;
  lastActivity: Date;
}

export class GameService {
  private games: Map<string, GameWithMeta> = new Map();
  public playerGameMap: Map<string, string> = new Map(); // playerId -> gameId
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
  createGameForRoom(gameCode: string): CodenamesGameModel {
    // Check if game already exists - don't delete it!
    const existingGame = this.getGameForRoom(gameCode);
    if (existingGame) {
      console.log(`⚠️  Game already exists for room ${gameCode}, returning existing game`);
      return existingGame;
    }

    console.log(`🎮 Creating new game for room: ${gameCode}`);
    const gameModel = new CodenamesGameModel(gameCode);
    this.games.set(gameModel.getId(), {
      model: gameModel,
      lastActivity: new Date()
    });

    return gameModel;
  }

  // Method to explicitly create a fresh game (for reset/restart scenarios)
  createFreshGameForRoom(gameCode: string): CodenamesGameModel {
    console.log(`🎮 Creating fresh game for room: ${gameCode} (deleting any existing)`);
    this.deleteGameForRoom(gameCode);

    const gameModel = new CodenamesGameModel(gameCode);
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

  getGameForRoom(gameCode: string): CodenamesGameModel | null {
    for (const [gameId, gameWithMeta] of this.games.entries()) {
      if (gameWithMeta.model.getGameCode() === gameCode) {
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
      // Remove all players from the player map using new helper
      const game = gameWithMeta.model.getGame();
      const allPlayers = getAllPlayers(game);
      allPlayers.forEach((player: any) => {
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

  deleteGameForRoom(gameCode: string): boolean {
    for (const [gameId, gameWithMeta] of this.games.entries()) {
      if (gameWithMeta.model.getGameCode() === gameCode) {
        return this.deleteGame(gameId);
      }
    }
    return false;
  }

  // Player management
  addPlayerToGame(gameId: string, playerId: string, username: string, socketId: string): boolean {
    console.log(`🎯 [ADDPLAYER] Adding ${username} (${playerId}) to game ${gameId}`);
    
    const game = this.getGame(gameId);
    if (!game) {
      console.log(`❌ [ADDPLAYER] Game ${gameId} not found`);
      return false;
    }

    // Check if player is already in THIS game
    const currentGame = this.getGameByPlayer(playerId);
    if (currentGame && currentGame.getId() === gameId) {
      console.log(`ℹ️  [ADDPLAYER] ${username} already in game ${gameId}`);
      return true; // Already in the correct game
    }

    // Remove player from any other game first
    if (currentGame && currentGame.getId() !== gameId) {
      console.log(`🔄 [ADDPLAYER] Moving ${username} from game ${currentGame.getId()} to ${gameId}`);
      this.removePlayerFromAllGames(playerId);
    }

    const success = game.addPlayer(playerId, username, socketId);
    if (success) {
      this.playerGameMap.set(playerId, gameId);
      console.log(`✅ [ADDPLAYER] Successfully added ${username} to game ${gameId}`);
    } else {
      console.log(`❌ [ADDPLAYER] Failed to add ${username} to game ${gameId}`);
    }
    
    return success;
  }

  removePlayerFromAllGames(playerId: string): boolean {
    const game = this.getGameByPlayer(playerId);
    if (game) {
      const success = game.removePlayer(playerId);
      if (success) {
        this.playerGameMap.delete(playerId);
        
        // Don't immediately delete empty games - they might be rejoined
        const gameState = game.getGame();
        const allPlayers = getAllPlayers(gameState);
        if (allPlayers.length === 0) {
          console.log(`🎯 Game ${gameState.id} is now empty but keeping it alive for potential reconnection`);
          // this.deleteGame(gameState.id); // Commented out - let cleanupInactiveGames handle this later
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
    console.log(`🎯 [GAMESERVICE] assignPlayerToTeam called for player ${playerId} to join ${team} as ${role}`);
    
    const game = this.getGameByPlayer(playerId);
    if (!game) {
      console.log(`❌ [GAMESERVICE] Player ${playerId} not found in any game`);
      console.log(`🎯 [GAMESERVICE] Current player-game mappings:`, Array.from(this.playerGameMap.entries()));
      return { success: false, error: 'Player not in any game' };
    }

    console.log(`🎯 [GAMESERVICE] Found game ${game.getId()} for player ${playerId}`);
    const preState = game.getGame();
    const preAllPlayers = getAllPlayers(preState);
    console.log(`🎯 [GAMESERVICE] Pre-assignment game state:`, preAllPlayers.map(p => `${p.username}(${getPlayerTeam(preState, p.id)}/${getPlayerRole(preState, p.id)})`));
    
    const success = game.assignPlayerToTeam(playerId, team, role);
    
    const postState = game.getGame();
    const postAllPlayers = getAllPlayers(postState);
    console.log(`🎯 [GAMESERVICE] Post-assignment game state:`, postAllPlayers.map(p => `${p.username}(${getPlayerTeam(postState, p.id)}/${getPlayerRole(postState, p.id)})`));
    console.log(`🎯 [GAMESERVICE] Assignment result: ${success}`);
    
    return { 
      success, 
      error: success ? undefined : 'Cannot assign to team - team may already have a spymaster or operatives need a spymaster first' 
    };
  }

  // Game actions
  startGame(playerId: string): { success: boolean; error?: string } {
    console.log('🎯 [GAMESERVICE] startGame called for player:', playerId);
    
    const game = this.getGameByPlayer(playerId);
    console.log('🎯 [GAMESERVICE] Game found for player:', !!game);
    
    if (!game) {
      console.log('❌ [GAMESERVICE] Player not in any game');
      // Log current player-game mappings for debugging
      console.log('🎯 [GAMESERVICE] Current player mappings:');
      for (const [pid, gid] of this.playerGameMap.entries()) {
        console.log(`  Player ${pid} -> Game ${gid}`);
      }
      return { success: false, error: 'Player not in any game' };
    }

    console.log('🎯 [GAMESERVICE] Checking if game can start...');
    const canStart = game.canStartGame();
    console.log('🎯 [GAMESERVICE] Can start result:', canStart);
    
    if (!canStart) {
      return { success: false, error: 'Cannot start game - need at least one complete team (spymaster + operatives)' };
    }

    console.log('🎯 [GAMESERVICE] Starting game...');
    const success = game.startGame();
    console.log('🎯 [GAMESERVICE] Start game result:', success);
    
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

  // Get all active games for the games list API
  getAllActiveGames(): Array<{
    code: string;
    id: string;
    status: string;
    playerCount: number;
    players: string[];
    createdAt: string;
    lastActivity: string;
  }> {
    const activeGames: any[] = [];
    
    // Iterate over ALL games (not just gameCodes) to catch games created via createGameForRoom
    for (const [gameId, gameWithMeta] of this.games.entries()) {
      const gameState = gameWithMeta.model.getGame();
      
      // Use roomCode as the display code (works for both room-based and code-based games)
      const displayCode = gameState.gameCode || gameId.substring(0, 6).toUpperCase();
      
      // Get all players using new helper function
      const allPlayers = getAllPlayers(gameState);
      
      activeGames.push({
        code: displayCode,
        id: gameState.id,
        status: gameState.status,
        playerCount: allPlayers.length,
        players: allPlayers.map((p: any) => p.username),
        createdAt: gameState.createdAt || new Date().toISOString(),
        lastActivity: gameWithMeta.lastActivity.toISOString()
      });
    }
    
    // Sort by most recent activity
    return activeGames.sort((a, b) => 
      new Date(b.lastActivity).getTime() - new Date(a.lastActivity).getTime()
    );
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
