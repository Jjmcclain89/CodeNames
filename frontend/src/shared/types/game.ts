// Complete frontend game types with all helper functions
export type TeamColor = 'red' | 'blue' | 'neutral' | 'assassin';
export type PlayerRole = 'spymaster' | 'operative';

export interface GamePlayer {
  id: string;
  username: string;
  isOnline: boolean;
  socketId: string;
  team?: TeamColor;
  role?: PlayerRole;
}

export interface Team {
  spymaster?: GamePlayer;
  operatives: GamePlayer[];
}

export interface CodeCard {
  id: string;
  word: string;
  team: TeamColor;
  isRevealed: boolean;
  position: number;
  revealedBy?: string;
}

export interface GameClue {
  word: string;
  number: number;
  givenBy: string;
  timestamp: string;
}

export interface CodenamesGame {
  id: string;
  gameCode: string;
  status: 'waiting' | 'playing' | 'finished';
  currentTurn: TeamColor;
  redTeam?: Team;
  blueTeam?: Team;
  board: CodeCard[];
  currentClue?: GameClue;
  guessesRemaining: number;
  winner?: TeamColor;
  createdAt: string;
  updatedAt: string;
  
  // Frontend expects this for compatibility
  players?: GamePlayer[];
  
  // Solo mode properties
  isSoloMode?: boolean;
  soloTeam?: TeamColor;
  soloCluesRemaining?: number;
  soloTurnGuessesRemaining?: number;
}

// Helper functions
export function getAllPlayers(game: CodenamesGame): GamePlayer[] {
  const players: GamePlayer[] = [];
  
  if (game.redTeam) {
    if (game.redTeam.spymaster) {
      players.push({ ...game.redTeam.spymaster, team: 'red', role: 'spymaster' });
    }
    players.push(...game.redTeam.operatives.map(p => ({ ...p, team: 'red' as TeamColor, role: 'operative' as PlayerRole })));
  }
  
  if (game.blueTeam) {
    if (game.blueTeam.spymaster) {
      players.push({ ...game.blueTeam.spymaster, team: 'blue', role: 'spymaster' });
    }
    players.push(...game.blueTeam.operatives.map(p => ({ ...p, team: 'blue' as TeamColor, role: 'operative' as PlayerRole })));
  }
  
  return players;
}

export function getPlayerTeam(game: CodenamesGame, playerId: string): TeamColor | null {
  if (game.redTeam) {
    if (game.redTeam.spymaster?.id === playerId) return 'red';
    if (game.redTeam.operatives.some(p => p.id === playerId)) return 'red';
  }
  
  if (game.blueTeam) {
    if (game.blueTeam.spymaster?.id === playerId) return 'blue';
    if (game.blueTeam.operatives.some(p => p.id === playerId)) return 'blue';
  }
  
  return null;
}

export function getPlayerRole(game: CodenamesGame, playerId: string): PlayerRole | null {
  if (game.redTeam) {
    if (game.redTeam.spymaster?.id === playerId) return 'spymaster';
    if (game.redTeam.operatives.some(p => p.id === playerId)) return 'operative';
  }
  
  if (game.blueTeam) {
    if (game.blueTeam.spymaster?.id === playerId) return 'spymaster';
    if (game.blueTeam.operatives.some(p => p.id === playerId)) return 'operative';
  }
  
  return null;
}

// Solo mode helper functions
export function isSoloMode(game: CodenamesGame): boolean {
  return game.isSoloMode || false;
}

export function getSoloTeam(game: CodenamesGame): TeamColor | null {
  return game.soloTeam || null;
}

export function getSoloTeamCards(game: CodenamesGame): CodeCard[] {
  if (!game.soloTeam) return [];
  return game.board.filter(card => card.team === game.soloTeam);
}

// Additional helper functions that frontend may need
export function canStartGame(game: CodenamesGame): boolean {
  const hasValidRedTeam = game.redTeam && game.redTeam.spymaster && game.redTeam.operatives.length > 0;
  const hasValidBlueTeam = game.blueTeam && game.blueTeam.spymaster && game.blueTeam.operatives.length > 0;
  return hasValidRedTeam && hasValidBlueTeam;
}

export function isTeamValid(team?: Team): boolean {
  return !!(team && team.spymaster && team.operatives.length > 0);
}
