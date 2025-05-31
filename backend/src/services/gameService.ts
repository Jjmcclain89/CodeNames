// Game Service - Manages games and integrates with existing storage
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
