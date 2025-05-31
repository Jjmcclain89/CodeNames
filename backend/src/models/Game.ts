// Game Model for Codenames - Integrates with existing in-memory storage
import { CodenamesGame, CodeCard, GamePlayer, GameClue, GameConfig, TeamColor, PlayerRole, GAME_CONFIG, CODENAMES_WORDS } from '../../../shared/types/game';

export class CodenamesGameModel {
  private game: CodenamesGame;

  constructor(roomCode: string, config: GameConfig = GAME_CONFIG.STANDARD_SETUP) {
    this.game = {
      id: this.generateGameId(),
      roomCode,
      status: 'waiting',
      currentTurn: 'red', // Red team always starts
      players: [],
      board: this.generateBoard(config),
      guessesRemaining: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
  }

  // Getters
  getGame(): CodenamesGame {
    return { ...this.game };
  }

  getId(): string {
    return this.game.id;
  }

  getStatus(): CodenamesGame['status'] {
    return this.game.status;
  }

  getRoomCode(): string {
    return this.game.roomCode;
  }

  // Player management
  addPlayer(playerId: string, username: string, socketId: string): boolean {
    if (this.game.players.length >= GAME_CONFIG.MAX_PLAYERS) {
      return false;
    }

    if (this.game.players.find(p => p.id === playerId)) {
      return false; // Player already exists
    }

    const player: GamePlayer = {
      id: playerId,
      username,
      team: 'neutral',
      role: 'operative',
      isOnline: true,
      socketId
    };

    this.game.players.push(player);
    this.updateTimestamp();
    return true;
  }

  removePlayer(playerId: string): boolean {
    const index = this.game.players.findIndex(p => p.id === playerId);
    if (index === -1) return false;

    this.game.players.splice(index, 1);
    this.updateTimestamp();
    return true;
  }

  assignPlayerToTeam(playerId: string, team: TeamColor, role: PlayerRole): boolean {
    if (team === 'neutral' || team === 'assassin') {
      return false;
    }

    const player = this.game.players.find(p => p.id === playerId);
    if (!player) return false;

    // Check if team already has a spymaster
    if (role === 'spymaster') {
      const existingSpymaster = this.game.players.find(
        p => p.team === team && p.role === 'spymaster' && p.id !== playerId
      );
      if (existingSpymaster) {
        return false;
      }
    }

    player.team = team;
    player.role = role;
    this.updateTimestamp();
    return true;
  }

  updatePlayerOnlineStatus(playerId: string, isOnline: boolean): boolean {
    const player = this.game.players.find(p => p.id === playerId);
    if (!player) return false;

    player.isOnline = isOnline;
    this.updateTimestamp();
    return true;
  }

  // Game flow
  canStartGame(): boolean {
    if (this.game.status !== 'waiting') return false;
    
    // For testing: allow starting with just one player
    if (process.env.NODE_ENV === 'development' && this.game.players.length >= 1) {
      return true;
    }
    
    // Production: need proper teams
    if (this.game.players.length < GAME_CONFIG.MIN_PLAYERS) return false;

    const redSpymaster = this.game.players.find(p => p.team === 'red' && p.role === 'spymaster');
    const blueSpymaster = this.game.players.find(p => p.team === 'blue' && p.role === 'spymaster');
    const redOperatives = this.game.players.filter(p => p.team === 'red' && p.role === 'operative');
    const blueOperatives = this.game.players.filter(p => p.team === 'blue' && p.role === 'operative');

    return !!(redSpymaster && blueSpymaster && redOperatives.length > 0 && blueOperatives.length > 0);
  }

  startGame(): boolean {
    if (!this.canStartGame()) return false;

    this.game.status = 'playing';
    this.game.currentTurn = 'red';
    this.game.guessesRemaining = 0;
    this.updateTimestamp();
    return true;
  }

  // Game actions
  giveClue(playerId: string, word: string, number: number): boolean {
    const player = this.game.players.find(p => p.id === playerId);
    
    if (!player || player.role !== 'spymaster' || player.team !== this.game.currentTurn) {
      return false;
    }

    if (this.game.status !== 'playing') return false;

    this.game.currentClue = {
      word: word.toUpperCase(),
      number,
      givenBy: playerId,
      timestamp: new Date().toISOString()
    };

    this.game.guessesRemaining = number + 1; // Players get one extra guess
    this.updateTimestamp();
    return true;
  }

  revealCard(playerId: string, cardId: string): { success: boolean; card?: CodeCard; gameEnded?: boolean; winner?: TeamColor } {
    const player = this.game.players.find(p => p.id === playerId);
    
    if (!player || player.role !== 'operative' || player.team !== this.game.currentTurn) {
      return { success: false };
    }

    if (this.game.status !== 'playing' || this.game.guessesRemaining <= 0) {
      return { success: false };
    }

    const card = this.game.board.find(c => c.id === cardId);
    if (!card || card.isRevealed) {
      return { success: false };
    }

    // Reveal the card
    card.isRevealed = true;
    card.revealedBy = playerId;
    this.game.guessesRemaining--;

    let gameEnded = false;
    let winner: TeamColor | undefined;

    // Check game ending conditions
    if (card.team === 'assassin') {
      // Game ends immediately - other team wins
      this.game.status = 'finished';
      winner = this.game.currentTurn === 'red' ? 'blue' : 'red';
      gameEnded = true;
    } else {
      // Check if team found all their cards
      const redCards = this.game.board.filter(c => c.team === 'red');
      const blueCards = this.game.board.filter(c => c.team === 'blue');
      const redRevealed = redCards.filter(c => c.isRevealed).length;
      const blueRevealed = blueCards.filter(c => c.isRevealed).length;

      if (redRevealed === redCards.length) {
        this.game.status = 'finished';
        winner = 'red';
        gameEnded = true;
      } else if (blueRevealed === blueCards.length) {
        this.game.status = 'finished';
        winner = 'blue';
        gameEnded = true;
      } else if (card.team !== this.game.currentTurn || this.game.guessesRemaining === 0) {
        // Wrong team card or out of guesses - end turn
        this.endTurn();
      }
    }

    if (gameEnded && winner) {
      this.game.winner = winner;
    }

    this.updateTimestamp();
    return { success: true, card, gameEnded, winner };
  }

  endTurn(): boolean {
    if (this.game.status !== 'playing') return false;

    this.game.currentTurn = this.game.currentTurn === 'red' ? 'blue' : 'red';
    this.game.guessesRemaining = 0;
    this.game.currentClue = undefined;
    this.updateTimestamp();
    return true;
  }

  resetGame(): void {
    const roomCode = this.game.roomCode;
    const players = this.game.players.map(p => ({ ...p, role: 'operative' as PlayerRole }));

    this.game = {
      id: this.generateGameId(),
      roomCode,
      status: 'waiting',
      currentTurn: 'red',
      players,
      board: this.generateBoard(),
      guessesRemaining: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
  }

  // Private methods
  private generateBoard(config: GameConfig = GAME_CONFIG.STANDARD_SETUP): CodeCard[] {
    // Shuffle and pick 25 words
    const shuffledWords = [...CODENAMES_WORDS].sort(() => Math.random() - 0.5).slice(0, 25);
    
    // Create team assignments with proper typing
    const teamAssignments: TeamColor[] = [
      ...Array(config.redCards).fill('red' as TeamColor),
      ...Array(config.blueCards).fill('blue' as TeamColor),
      ...Array(config.neutralCards).fill('neutral' as TeamColor),
      ...Array(config.assassinCards).fill('assassin' as TeamColor)
    ];
    
    // Ensure we have exactly 25 assignments
    while (teamAssignments.length < 25) {
      teamAssignments.push('neutral' as TeamColor);
    }
    teamAssignments.length = 25; // Trim to exactly 25

    // Shuffle team assignments
    teamAssignments.sort(() => Math.random() - 0.5);

    // Create cards with proper type safety
    return shuffledWords.map((word, index) => ({
      id: `card-${index}`,
      word,
      team: teamAssignments[index] || 'neutral', // Fallback to prevent undefined
      isRevealed: false,
      position: index
    }));
  }

  private generateGameId(): string {
    return `game_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private updateTimestamp(): void {
    this.game.updatedAt = new Date().toISOString();
  }
}
