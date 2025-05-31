// Frontend Game Types - Re-exports shared types plus UI-specific types
export * from '../../../shared/types/game';

// UI-specific types
export interface GameUIState {
  selectedCard: string | null;
  showSpymasterView: boolean;
  isMyTurn: boolean;
  canGiveClue: boolean;
  canRevealCard: boolean;
  isCurrentPlayerSpymaster: boolean;
  isCurrentPlayerOperative: boolean;
}

export interface ClueInputState {
  word: string;
  number: number;
  isValid: boolean;
}

// Component prop types
export interface CardProps {
  card: import('../../../shared/types/game').CodeCard;
  isSpymaster: boolean;
  onClick?: (cardId: string) => void;
  disabled?: boolean;
  className?: string;
}

export interface GameBoardProps {
  gameState: import('../../../shared/types/game').CodenamesGame;
  currentPlayer: import('../../../shared/types/game').GamePlayer | null;
  onCardClick: (cardId: string) => void;
  onGiveClue: (word: string, number: number) => void;
  onEndTurn: () => void;
  onStartGame: () => void;
  onJoinTeam: (team: import('../../../shared/types/game').TeamColor, role: import('../../../shared/types/game').PlayerRole) => void;
}
