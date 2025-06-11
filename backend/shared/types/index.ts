// Shared type definitions between frontend and backend

export interface User {
  id: string;
  username: string;
  avatarUrl?: string;
  createdAt: Date;
  gamesPlayed: number;
  gamesWon: number;
}

export interface GameRoom {
  id: string;
  name: string;
  hostId: string;
  players: Player[];
  gameState: GameState;
  settings: RoomSettings;
  createdAt: Date;
  isActive: boolean;
}

export interface RoomSettings {
  maxPlayers: number;
  turnTimeLimit?: number;
  customWordList?: string[];
  isPrivate: boolean;
}

export interface GameState {
  status: 'waiting' | 'active' | 'finished';
  currentTurn: 'red' | 'blue';
  board: Card[];
  redSpymaster: string;
  blueSpymaster: string;
  currentClue?: Clue;
  guessesRemaining: number;
  redAgentsLeft: number;
  blueAgentsLeft: number;
  winner?: 'red' | 'blue';
  turnHistory: TurnHistory[];
}

export interface Card {
  id: string;
  word: string;
  type: 'red' | 'blue' | 'neutral' | 'assassin';
  isRevealed: boolean;
  position: number;
}

export interface Clue {
  word: string;
  number: number;
  spymasterId: string;
  timestamp: Date;
}

export interface Player {
  id: string;
  userId: string;
  username: string;
  team: 'red' | 'blue' | 'spectator';
  role: 'spymaster' | 'operative';
  isConnected: boolean;
  joinedAt: Date;
}

export interface TurnHistory {
  clue: Clue;
  guesses: string[];
  team: 'red' | 'blue';
  timestamp: Date;
}
