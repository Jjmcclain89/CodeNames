// Frontend Game Service - Extends existing socketService for game functionality
import { socketService } from './socketService';
import { CodenamesGame, GamePlayer, TeamColor, PlayerRole, GameClue, CodeCard } from '../types/game';

class GameService {
  // Game management
  createGame(): void {
    socketService.socket?.emit('game:create');
  }

  startGame(): void {
    
    socketService.socket?.emit('game:start');
    
  }

  resetGame(): void {
    socketService.socket?.emit('game:reset');
  }

  // Team and role management
  joinTeam(team: TeamColor, role: PlayerRole): void {
    if (team === 'neutral' || team === 'assassin') {
      console.error('Cannot join neutral or assassin team');
      return;
    }
    socketService.socket?.emit('game:join-team', team, role);
  }

  // Game actions
  giveClue(gameId: string, word: string, number: number): void {
    if (!gameId || !word.trim() || number < 1 || number > 9) {
      console.error('Invalid clue parameters');
      return;
    }
    
    console.log('📡 Emitting game:give-clue event:', { gameId, word: word.trim().toUpperCase(), number });
    socketService.socket?.emit('game:give-clue', { 
      gameId: gameId.toUpperCase(),
      word: word.trim().toUpperCase(), 
      number 
    });
  }

  revealCard(gameId: string, cardId: string): void {
    if (!gameId || !cardId) {
      console.error('Invalid reveal card parameters');
      return;
    }
    
    console.log('📡 Emitting game:reveal-card event:', { gameId, cardId });
    socketService.socket?.emit('game:reveal-card', { 
      gameId: gameId.toUpperCase(), 
      cardId 
    });
  }

  endTurn(gameId: string): void {
    if (!gameId) {
      console.error('Invalid end turn parameters');
      return;
    }
    
    console.log('📡 Emitting game:end-turn event:', { gameId });
    socketService.socket?.emit('game:end-turn', { 
      gameId: gameId.toUpperCase() 
    });
  }

  // Event listeners for game events
  onGameStateUpdated(callback: (game: CodenamesGame) => void): void {
    
    
    const wrappedCallback = (game: CodenamesGame) => {
      console.log('📡 [FRONTEND] Received game:state-updated event');
      console.log('📡 [FRONTEND] Game status:', game.status);
      console.log('📡 [FRONTEND] Board length:', game.board?.length);
      callback(game);
    };
    
    socketService.socket?.on('game:state-updated', wrappedCallback);
  }

  onPlayerJoined(callback: (player: GamePlayer) => void): void {
    socketService.socket?.on('game:player-joined', callback);
  }

  onCardRevealed(callback: (card: CodeCard) => void): void {
    socketService.socket?.on('game:card-revealed', callback);
  }

  onClueGiven(callback: (clue: GameClue) => void): void {
    socketService.socket?.on('game:clue-given', callback);
  }

  onTurnChanged(callback: (newTurn: TeamColor) => void): void {
    socketService.socket?.on('game:turn-changed', callback);
  }

  onGameEnded(callback: (winner: TeamColor) => void): void {
    socketService.socket?.on('game:game-ended', callback);
  }

  onGameError(callback: (error: string) => void): void {
    const wrappedErrorCallback = (error: string) => {
      console.log('❌ [FRONTEND] Received game:error:', error);
      callback(error);
    };
    socketService.socket?.on('game:error', wrappedErrorCallback);
  }

  // Cleanup method
  removeAllGameListeners(): void {
    socketService.socket?.off('game:state-updated');
    socketService.socket?.off('game:player-joined');
    socketService.socket?.off('game:card-revealed');
    socketService.socket?.off('game:clue-given');
    socketService.socket?.off('game:turn-changed');
    socketService.socket?.off('game:game-ended');
    socketService.socket?.off('game:error');
  }

  // Utility methods
  getTeamStats(game: CodenamesGame) {
    // Defensive programming - handle missing board data
    if (!game || !game.board || !Array.isArray(game.board)) {
      console.warn('⚠️ GameService: Missing or invalid board data, returning default stats');
      return {
        red: { total: 0, revealed: 0, remaining: 0 },
        blue: { total: 0, revealed: 0, remaining: 0 }
      };
    }
    
    const redCards = game.board.filter(c => c.team === 'red');
    const blueCards = game.board.filter(c => c.team === 'blue');
    const redRevealed = redCards.filter(c => c.isRevealed).length;
    const blueRevealed = blueCards.filter(c => c.isRevealed).length;

    return {
      red: { 
        total: redCards.length, 
        revealed: redRevealed, 
        remaining: redCards.length - redRevealed 
      },
      blue: { 
        total: blueCards.length, 
        revealed: blueRevealed, 
        remaining: blueCards.length - blueRevealed 
      }
    };
  }

  isPlayerTurn(game: CodenamesGame, player: GamePlayer | null): boolean {
    if (!player) return false;
    
    // In solo mode, it's always the solo team's turn
    if (game.isSoloMode) {
      return player.team === game.soloTeam;
    }
    
    // In classic mode, normal turn rules
    return player.team === game.currentTurn;
  }

  canPlayerGiveClue(game: CodenamesGame, player: GamePlayer | null): boolean {
    if (!player || game.status !== 'playing') {
      return false;
    }
    
    // In solo mode, allow clue giving if:
    // 1. Player is spymaster of solo team
    // 2. No active clue OR all turn guesses are used up
    if (game.isSoloMode) {
      const isCorrectPlayer = player.role === 'spymaster' && player.team === game.soloTeam;
      const noActiveClue = !game.currentClue;
      const turnGuessesFinished = (game.soloTurnGuessesRemaining || 0) === 0;
      
      console.log('🔍 [CLUE CHECK] Solo mode checks:', {
        isCorrectPlayer,
        noActiveClue,
        turnGuessesFinished,
        currentClue: game.currentClue,
        turnGuesses: game.soloTurnGuessesRemaining
      });
      
      return isCorrectPlayer && (noActiveClue || turnGuessesFinished);
    }
    
    // In classic mode, normal rules apply
    return player.role === 'spymaster' && 
           player.team === game.currentTurn && 
           !game.currentClue;
  }

  canPlayerRevealCard(game: CodenamesGame, player: GamePlayer | null): boolean {
    if (!player || game.status !== 'playing') {
      return false;
    }
    
    // In solo mode, check solo turn guesses and team
    if (game.isSoloMode) {
      return player.role === 'operative' && 
             player.team === game.soloTeam && 
             (game.soloTurnGuessesRemaining || 0) > 0;
    }
    
    // In classic mode, normal rules apply
    return player.role === 'operative' && 
           player.team === game.currentTurn && 
           game.guessesRemaining > 0;
  }
}

export const gameService = new GameService();
export default gameService;
