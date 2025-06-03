// Frontend Game Service - Extends existing socketService for game functionality
import { socketService } from './socketService';
import { CodenamesGame, GamePlayer, TeamColor, PlayerRole, GameClue, CodeCard } from '../types/game';

class GameService {
  // Game management
  createGame(): void {
    socketService.socket?.emit('game:create');
  }

  startGame(): void {
    console.log('🚀 [GAMESERVICE] Emitting game:start event to backend');
    socketService.socket?.emit('game:start');
    console.log('🚀 [GAMESERVICE] game:start event emitted');
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
  giveClue(word: string, number: number): void {
    if (!word.trim() || number < 1 || number > 9) {
      console.error('Invalid clue parameters');
      return;
    }
    
    socketService.socket?.emit('game:give-clue', { 
      word: word.trim().toUpperCase(), 
      number 
    });
  }

  revealCard(cardId: string): void {
    socketService.socket?.emit('game:reveal-card', cardId);
  }

  endTurn(): void {
    socketService.socket?.emit('game:end-turn');
  }

  // Event listeners for game events
  onGameStateUpdated(callback: (game: CodenamesGame) => void): void {
    console.log('🎮 [GAMESERVICE] Registering game:state-updated listener');
    
    const wrappedCallback = (game: CodenamesGame) => {
      console.log('🎮 [GAMESERVICE] game:state-updated event received:', game);
      console.log('🎮 [GAMESERVICE] Game status in event:', game.status);
      console.log('🎮 [GAMESERVICE] Game players count:', game.players?.length);
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
    socketService.socket?.on('game:error', callback);
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
    return !!(player && player.team === game.currentTurn);
  }

  canPlayerGiveClue(game: CodenamesGame, player: GamePlayer | null): boolean {
    return !!(
      player && 
      player.role === 'spymaster' && 
      player.team === game.currentTurn && 
      !game.currentClue && 
      game.status === 'playing'
    );
  }

  canPlayerRevealCard(game: CodenamesGame, player: GamePlayer | null): boolean {
    return !!(
      player && 
      player.role === 'operative' && 
      player.team === game.currentTurn && 
      game.guessesRemaining > 0 && 
      game.status === 'playing'
    );
  }
}

export const gameService = new GameService();
export default gameService;
