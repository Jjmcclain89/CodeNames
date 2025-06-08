// Shared Game Types for Codenames - Phase 2
// Integrates with existing shared/types/index.ts

export type TeamColor = 'red' | 'blue' | 'neutral' | 'assassin';
export type PlayerRole = 'spymaster' | 'operative';
export type GameStatus = 'waiting' | 'setup' | 'playing' | 'finished';

export interface CodeCard {
  id: string;
  word: string;
  team: TeamColor;
  isRevealed: boolean;
  revealedBy?: string; // player id who revealed it
  position: number; // 0-24 for 5x5 grid
}

export interface GamePlayer {
  id: string;
  username: string;
  isOnline: boolean;
  socketId: string;
  // Note: team and role removed - now determined by team structure position
}

export interface GameClue {
  word: string;
  number: number;
  givenBy: string; // player id
  timestamp: string;
}

// New Team structure
export interface Team {
  spymaster: GamePlayer;
  operatives: GamePlayer[];
}

export interface CodenamesGame {
  id: string;
  gameCode: string;
  status: GameStatus;
  currentTurn: TeamColor;
  redTeam?: Team;   // undefined if empty
  blueTeam?: Team;  // undefined if empty
  board: CodeCard[];
  currentClue?: GameClue;
  guessesRemaining: number;
  winner?: TeamColor;
  createdAt: string;
  updatedAt: string;
}

export interface GameConfig {
  boardSize: number; // Always 25 for 5x5
  redCards: number;   // 9 or 8
  blueCards: number;  // 8 or 9  
  neutralCards: number; // 7
  assassinCards: number; // 1
}

// Game Lobby Types (team assignment phase) - Updated for new structure
export interface GameLobbyMessage {
  id: string;
  username: string;
  userId: string;
  text: string;
  timestamp: string;
}

export interface GameLobbyPlayer {
  id: string;
  username: string;
  team: TeamColor;
  role: PlayerRole;
  isOnline: boolean;
  isOwner: boolean;
}

export interface GameLobby {
  id: string;
  code: string;
  owner: string;
  players: GameLobbyPlayer[];
  status: 'waiting' | 'playing' | 'finished';
  createdAt: string;
  updatedAt: string;
}

// Socket Events for Game (extends existing socket events)
export interface GameSocketEvents {
  // Game Management
  'game:create': () => void;
  'game:join': (gameId: string) => void;
  'game:start': () => void;
  'game:reset': () => void;
  
  // Team/Role Assignment
  'game:join-team': (team: TeamColor, role: PlayerRole) => void;
  
  // Game Actions
  'game:give-clue': (clue: { word: string; number: number }) => void;
  'game:reveal-card': (cardId: string) => void;
  'game:end-turn': () => void;
  
  // Game State Updates (server to client)
  'game:state-updated': (game: CodenamesGame) => void;
  'game:player-joined': (player: GamePlayer) => void;
  'game:card-revealed': (card: CodeCard) => void;
  'game:clue-given': (clue: GameClue) => void;
  'game:turn-changed': (newTurn: TeamColor) => void;
  'game:game-ended': (winner: TeamColor) => void;
  'game:error': (error: string) => void;
}

// Game Constants
export const GAME_CONFIG = {
  BOARD_SIZE: 25,
  MIN_PLAYERS: 1,
  MAX_PLAYERS: 8,
  STANDARD_SETUP: {
    boardSize: 25,
    redCards: 9,
    blueCards: 8,
    neutralCards: 7,
    assassinCards: 1
  } as GameConfig
};

// Helper functions for new team structure
export const getPlayerTeam = (game: CodenamesGame, playerId: string): TeamColor => {
  if (game.redTeam?.spymaster.id === playerId) return 'red';
  if (game.redTeam?.operatives.some(p => p.id === playerId)) return 'red';
  if (game.blueTeam?.spymaster.id === playerId) return 'blue';
  if (game.blueTeam?.operatives.some(p => p.id === playerId)) return 'blue';
  return 'neutral';
};

export const getPlayerRole = (game: CodenamesGame, playerId: string): PlayerRole => {
  if (game.redTeam?.spymaster.id === playerId || game.blueTeam?.spymaster.id === playerId) {
    return 'spymaster';
  }
  return 'operative';
};

export const getAllPlayers = (game: CodenamesGame): GamePlayer[] => {
  const players: GamePlayer[] = [];
  if (game.redTeam) {
    players.push(game.redTeam.spymaster, ...game.redTeam.operatives);
  }
  if (game.blueTeam) {
    players.push(game.blueTeam.spymaster, ...game.blueTeam.operatives);
  }
  return players;
};

export const isTeamValid = (team?: Team): boolean => {
  console.log(`team: {team}, spymaster: ${team?.spymaster}, operatives: ${team?.operatives.length}`);
  return !!team && !!team.spymaster && team.operatives.length > 0;
};

export const canStartGame = (game: CodenamesGame): boolean => {
  const redValid = isTeamValid(game.redTeam);
  const blueValid = isTeamValid(game.blueTeam);
  
  console.log('🔍 [CANSTART] Red valid:', redValid, 'Blue valid:', blueValid);
  
  // Allow game to start with at least one valid team
  const canStart = redValid || blueValid;
  console.log('🔍 [CANSTART] Final result:', canStart);
  
  return canStart;
};

// Word list for game generation
export const CODENAMES_WORDS = [
  'AFRICA', 'AGENT', 'AIR', 'ALIEN', 'ALPS', 'AMAZON', 'AMBULANCE', 'AMERICA', 'ANGEL', 'ANTARCTICA',
  'APPLE', 'ARM', 'ATLANTIS', 'AUSTRALIA', 'AZTEC', 'BACK', 'BALL', 'BAND', 'BANK', 'BAR',
  'BARK', 'BAT', 'BATTERY', 'BEACH', 'BEAR', 'BEAT', 'BED', 'BEIJING', 'BELL', 'BELT',
  'BERLIN', 'BERMUDA', 'BERRY', 'BILL', 'BLOCK', 'BOARD', 'BOLT', 'BOMB', 'BOND', 'BOOM',
  'BOOT', 'BOTTLE', 'BOW', 'BOX', 'BRIDGE', 'BRUSH', 'BUCK', 'BUFFALO', 'BUG', 'BUGLE',
  'BUTTON', 'CALF', 'CANADA', 'CAP', 'CAPITAL', 'CAR', 'CARD', 'CARROT', 'CASINO', 'CAST',
  'CAT', 'CELL', 'CENTAUR', 'CENTER', 'CHAIR', 'CHANGE', 'CHARGE', 'CHECK', 'CHEST', 'CHICK',
  'CHINA', 'CHOCOLATE', 'CHURCH', 'CIRCLE', 'CLIFF', 'CLOAK', 'CLUB', 'CODE', 'COLD', 'COMIC',
  'COMPOUND', 'COMPUTER', 'CONDUCTOR', 'CONTRACT', 'COOK', 'COPPER', 'COTTON', 'COURT', 'COVER', 'CRANE',
  'CRASH', 'CRICKET', 'CROSS', 'CROWN', 'CYCLE', 'CZECH', 'DANCE', 'DATE', 'DAY', 'DEATH',
  'DECK', 'DEGREE', 'DIAMOND', 'DICE', 'DINOSAUR', 'DISEASE', 'DOCTOR', 'DOG', 'DRAFT', 'DRAGON',
  'DRESS', 'DRILL', 'DROP', 'DUCK', 'DWARF', 'EAGLE', 'EGYPT', 'ENGINE', 'ENGLAND', 'EUROPE',
  'EYE', 'FACE', 'FAIR', 'FALL', 'FAN', 'FENCE', 'FIELD', 'FIGHTER', 'FIGURE', 'FILE',
  'FILM', 'FIRE', 'FISH', 'FLUTE', 'FLY', 'FOOT', 'FORCE', 'FOREST', 'FORK', 'FRANCE',
  'GAME', 'GAS', 'GENIUS', 'GERMANY', 'GHOST', 'GIANT', 'GLASS', 'GLOVE', 'GOLD', 'GRACE',
  'GRASS', 'GREECE', 'GREEN', 'GROUND', 'HAM', 'HAND', 'HAWK', 'HEAD', 'HEART', 'HELICOPTER',
  'HIMALAYAS', 'HOLE', 'HOLLYWOOD', 'HONEY', 'HOOD', 'HOOK', 'HORN', 'HORSE', 'HORSESHOE', 'HOSPITAL',
  'HOTEL', 'ICE', 'ICE_CREAM', 'INDIA', 'IRON', 'IVORY', 'JACK', 'JAM', 'JET', 'JUPITER',
  'KANGAROO', 'KETCHUP', 'KEY', 'KID', 'KING', 'KIWI', 'KNIFE', 'KNIGHT', 'LAB', 'LAP',
  'LASER', 'LAWYER', 'LEAD', 'LEMON', 'LEPRECHAUN', 'LIFE', 'LIGHT', 'LIMOUSINE', 'LINE', 'LINK',
  'LION', 'LITTER', 'LOCH_NESS', 'LOCK', 'LOG', 'LONDON', 'LUCK', 'MAIL', 'MAMMOTH', 'MAPLE',
  'MARBLE', 'MARCH', 'MASS', 'MATCH', 'MERCURY', 'MEXICO', 'MICROSCOPE', 'MILLIONAIRE', 'MINE', 'MINT',
  'MISSILE', 'MODEL', 'MOLE', 'MOON', 'MOSCOW', 'MOUNT', 'MOUSE', 'MOUTH', 'MUG', 'NAIL',
  'NEEDLE', 'NET', 'NEW_YORK', 'NIGHT', 'NINJA', 'NOTE', 'NOVEL', 'NURSE', 'NUT', 'OCTOPUS',
  'OIL', 'OLIVE', 'OLYMPUS', 'OPERA', 'ORANGE', 'ORGAN', 'PALM', 'PAN', 'PANTS', 'PAPER',
  'PARACHUTE', 'PARK', 'PART', 'PASS', 'PASTE', 'PENGUIN', 'PHOENIX', 'PIANO', 'PIE', 'PILOT',
  'PIN', 'PIPE', 'PIRATE', 'PISTOL', 'PIT', 'PITCH', 'PIZZA', 'PLANE', 'PLASTIC', 'PLATE',
  'PLATYPUS', 'PLAY', 'PLOT', 'POINT', 'POISON', 'POLE', 'POLICE', 'POOL', 'PORT', 'POST',
  'POUND', 'PRESS', 'PRINCESS', 'PUMPKIN', 'PUPIL', 'PYRAMID', 'QUEEN', 'RABBIT', 'RACKET', 'RAY',
  'REVOLUTION', 'RING', 'ROBIN', 'ROBOT', 'ROCK', 'ROME', 'ROOT', 'ROSE', 'ROULETTE', 'ROUND',
  'ROW', 'RULER', 'SATELLITE', 'SATURN', 'SCALE', 'SCHOOL', 'SCIENTIST', 'SCORPION', 'SCREEN', 'SCUBA_DIVER',
  'SEAL', 'SERVER', 'SHADOW', 'SHAKESPEARE', 'SHARK', 'SHIP', 'SHOE', 'SHOP', 'SHOT', 'SINK',
  'SKYSCRAPER', 'SLIP', 'SLUG', 'SMUGGLER', 'SNOW', 'SNOWMAN', 'SOCK', 'SOLDIER', 'SOUL', 'SOUND',
  'SPACE', 'SPELL', 'SPIDER', 'SPIKE', 'SPINE', 'SPOT', 'SPRING', 'SPY', 'SQUARE', 'STADIUM',
  'STAFF', 'STAR', 'STATE', 'STICK', 'STOCK', 'STRAW', 'STREAM', 'STRIKE', 'STRING', 'SUB',
  'SUIT', 'SUPERHERO', 'SWING', 'SWITCH', 'TABLE', 'TABLET', 'TAG', 'TANK', 'TAP', 'TEACHER',
  'TELESCOPE', 'TEMPLE', 'THEATER', 'THIEF', 'THUMB', 'TICK', 'TIE', 'TIME', 'TOKYO', 'TOOTH',
  'TORCH', 'TOWER', 'TRACK', 'TRAIN', 'TRIANGLE', 'TRIP', 'TRUCK', 'TRUNK', 'TUBE', 'TURKEY',
  'UNDERTAKER', 'UNICORN', 'VACUUM', 'VAN', 'VET', 'WAKE', 'WALL', 'WAR', 'WASHER', 'WASHINGTON',
  'WATCH', 'WATER', 'WAVE', 'WEB', 'WELL', 'WHALE', 'WHIP', 'WIND', 'WITCH', 'WIZARD',
  'WORM', 'YARD'
];
