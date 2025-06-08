// Game Model for Codenames - Updated for new team structure
import { CodenamesGame, CodeCard, GamePlayer, GameClue, GameConfig, TeamColor, PlayerRole, GAME_CONFIG, CODENAMES_WORDS, Team, getAllPlayers, getPlayerTeam, getPlayerRole, isTeamValid, canStartGame as canStartGameHelper } from '../../../shared/types/game';

export class CodenamesGameModel {
  private game: CodenamesGame;

  constructor(gameCode: string, config: GameConfig = GAME_CONFIG.STANDARD_SETUP) {
    const board = this.generateBoard(config);
    
    // ✅ Count red vs blue cards to determine starting team
    const redCardCount = board.filter(card => card.team === 'red').length;
    const blueCardCount = board.filter(card => card.team === 'blue').length;
    const startingTeam: TeamColor = redCardCount > blueCardCount ? 'red' : 'blue';
    
    console.log(`🎯 Game Setup: Red ${redCardCount} cards, Blue ${blueCardCount} cards`);
    console.log(`🚀 Starting team: ${startingTeam} (has more words to guess)`);

    this.game = {
      id: this.generateGameId(),
      gameCode,
      status: 'waiting',
      currentTurn: startingTeam,
      redTeam: undefined,   // Start with no teams
      blueTeam: undefined,  // Start with no teams
      board,
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

  getGameCode(): string {
    return this.game.gameCode;
  }

  // Player management - Updated for team structure
  addPlayer(playerId: string, username: string, socketId: string): boolean {
    const allPlayers = getAllPlayers(this.game);
    
    if (allPlayers.length >= GAME_CONFIG.MAX_PLAYERS) {
      return false;
    }

    if (allPlayers.find(p => p.id === playerId)) {
      return false; // Player already exists
    }

    // For now, just track that we added the player
    // They'll be assigned to a team via assignPlayerToTeam
    console.log(`✅ Player ${username} (${playerId}) ready to join teams`);
    this.updateTimestamp();
    return true;
  }

  removePlayer(playerId: string): boolean {
    let removed = false;
    
    // Remove from red team
    if (this.game.redTeam) {
      if (this.game.redTeam.spymaster && this.game.redTeam.spymaster.id === playerId) {
        this.game.redTeam = undefined; // Remove entire team if spymaster leaves
        removed = true;
      } else if (this.game.redTeam.operatives) {
        const initialLength = this.game.redTeam.operatives.length;
        this.game.redTeam.operatives = this.game.redTeam.operatives.filter(p => p.id !== playerId);
        if (this.game.redTeam.operatives.length < initialLength) {
          removed = true;
        }
      }
    }
    
    // Remove from blue team
    if (this.game.blueTeam) {
      if (this.game.blueTeam.spymaster && this.game.blueTeam.spymaster.id === playerId) {
        this.game.blueTeam = undefined; // Remove entire team if spymaster leaves
        removed = true;
      } else if (this.game.blueTeam.operatives) {
        const initialLength = this.game.blueTeam.operatives.length;
        this.game.blueTeam.operatives = this.game.blueTeam.operatives.filter(p => p.id !== playerId);
        if (this.game.blueTeam.operatives.length < initialLength) {
          removed = true;
        }
      }
    }
    
    if (removed) {
      this.updateTimestamp();
    }
    return removed;
  }

  assignPlayerToTeam(playerId: string, team: TeamColor, role: PlayerRole): boolean {
    if (team === 'neutral' || team === 'assassin') {
      return false;
    }

    // Create player object
    const player: GamePlayer = {
      id: playerId,
      username: this.getPlayerUsername(playerId) || 'Unknown',
      isOnline: true,
      socketId: '' // Will be updated by service layer
    };

    // Remove player from any existing team first
    this.removePlayer(playerId);

    if (team === 'red') {
      if (role === 'spymaster') {
        // Can only have one spymaster - replace existing team or create new
        this.game.redTeam = {
          spymaster: player,
          operatives: this.game.redTeam?.operatives || []
        };
      } else {
        // Adding operative
        if (!this.game.redTeam) {
          // Can't add operative without spymaster - return false
          return false;
        }
        this.game.redTeam.operatives.push(player);
      }
    } else if (team === 'blue') {
      if (role === 'spymaster') {
        // Can only have one spymaster - replace existing team or create new
        this.game.blueTeam = {
          spymaster: player,
          operatives: this.game.blueTeam?.operatives || []
        };
      } else {
        // Adding operative
        if (!this.game.blueTeam) {
          // Can't add operative without spymaster - return false
          return false;
        }
        this.game.blueTeam.operatives.push(player);
      }
    }

    this.updateTimestamp();
    return true;
  }


  // Set teams wholesale (for lobby-to-game transfer)
  setTeams(redTeam?: Team, blueTeam?: Team): void {
    console.log('🔄 [GAME MODEL] setTeams called with:', {
      redTeam: redTeam ? `Spymaster: ${redTeam.spymaster?.username || 'none'}, Operatives: ${redTeam.operatives?.map(p => p.username).join(', ') || 'none'}` : 'undefined',
      blueTeam: blueTeam ? `Spymaster: ${blueTeam.spymaster?.username || 'none'}, Operatives: ${blueTeam.operatives?.map(p => p.username).join(', ') || 'none'}` : 'undefined'
    });
    
    this.game.redTeam = redTeam;
    this.game.blueTeam = blueTeam;
    this.updateTimestamp();
    
    console.log('✅ [GAME MODEL] Teams set successfully');
  }

    updatePlayerOnlineStatus(playerId: string, isOnline: boolean): boolean {
    const allPlayers = getAllPlayers(this.game);
    const player = allPlayers.find(p => p.id === playerId);
    if (!player) return false;

    player.isOnline = isOnline;
    this.updateTimestamp();
    return true;
  }

  // Game flow - Updated validation
  canStartGame(): boolean {
    console.log('🔍 [VALIDATION] Checking if game can start with new team structure');
    console.log('🔍 [VALIDATION] Game status:', this.game.status);
    
    if (this.game.status !== 'waiting') {
      console.log('❌ [VALIDATION] Game not in waiting status');
      return false;
    }
    
    console.log('🔍 [VALIDATION] Red team valid:', isTeamValid(this.game.redTeam));
    console.log('🔍 [VALIDATION] Blue team valid:', isTeamValid(this.game.blueTeam));
    
    const canStart = canStartGameHelper(this.game);
    console.log('🔍 [VALIDATION] Can start game:', canStart);
    
    return canStart;
  }

  startGame(): boolean {
    if (!this.canStartGame()) return false;

    this.game.status = 'playing';
    this.game.currentTurn = 'red';
    this.game.guessesRemaining = 0;
    this.updateTimestamp();
    return true;
  }

  // Game actions - Updated for team structure
  giveClue(playerId: string, word: string, number: number): boolean {
    const playerTeam = getPlayerTeam(this.game, playerId);
    const playerRole = getPlayerRole(this.game, playerId);
    
    if (playerRole !== 'spymaster' || playerTeam !== this.game.currentTurn) {
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
    const playerTeam = getPlayerTeam(this.game, playerId);
    const playerRole = getPlayerRole(this.game, playerId);
    
    if (playerRole !== 'operative' || playerTeam !== this.game.currentTurn) {
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
    const gameCode = this.game.gameCode;
    // Preserve team assignments through reset
    const redTeam = this.game.redTeam;
    const blueTeam = this.game.blueTeam;

    this.game = {
      id: this.generateGameId(),
      gameCode,
      status: 'waiting',
      currentTurn: 'red',
      redTeam,
      blueTeam,
      board: this.generateBoard(),
      guessesRemaining: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
  }

  // Helper methods
  private getPlayerUsername(playerId: string): string | undefined {
    const allPlayers = getAllPlayers(this.game);
    return allPlayers.find(p => p.id === playerId)?.username;
  }

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
