import React from 'react';
import { CodeCard, TeamColor } from '../../types/game';

interface CardProps {
  card: CodeCard;
  isSpymaster: boolean;
  onClick?: (cardId: string) => void;
  disabled?: boolean;
  className?: string;
}

const getCardColors = (team: TeamColor, isRevealed: boolean, isSpymaster: boolean) => {
  if (isRevealed) {
    // Revealed cards show their true colors
    switch (team) {
      case 'red':
        return 'bg-red-500 text-white border-red-600 shadow-lg';
      case 'blue':
        return 'bg-blue-500 text-white border-blue-600 shadow-lg';
      case 'neutral':
        return 'bg-gray-400 text-white border-gray-500 shadow-lg';
      case 'assassin':
        return 'bg-black text-white border-gray-800 shadow-lg';
      default:
        return 'bg-gray-300 text-gray-800 border-gray-400';
    }
  } else if (isSpymaster) {
    // Spymasters can see the true colors with subtle hints
    switch (team) {
      case 'red':
        return 'bg-red-50 border-red-300 text-red-800 hover:bg-red-100';
      case 'blue':
        return 'bg-blue-50 border-blue-300 text-blue-800 hover:bg-blue-100';
      case 'neutral':
        return 'bg-gray-50 border-gray-300 text-gray-700 hover:bg-gray-100';
      case 'assassin':
        return 'bg-gray-800 border-gray-900 text-white hover:bg-gray-700';
      default:
        return 'bg-white border-gray-300 text-gray-800 hover:bg-gray-100';
    }
  } else {
    // Regular players see neutral cards
    return 'bg-yellow-50 border-yellow-200 text-gray-800 hover:bg-yellow-100';
  }
};

const getTeamEmoji = (team: TeamColor) => {
  switch (team) {
    case 'red': return '🔴';
    case 'blue': return '🔵';
    case 'neutral': return '⚪';
    case 'assassin': return '💀';
    default: return '';
  }
};

export const Card: React.FC<CardProps> = ({ 
  card, 
  isSpymaster, 
  onClick, 
  disabled = false,
  className = ''
}) => {
  const handleClick = () => {
    if (!disabled && onClick && !card.isRevealed) {
      onClick(card.id);
    }
  };

  const colors = getCardColors(card.team, card.isRevealed, isSpymaster);
  const clickable = !disabled && onClick && !card.isRevealed;

  return (
    <div
      className={`
        relative w-full aspect-square p-3 border-2 rounded-lg flex items-center justify-center
        transition-all duration-200 text-sm font-medium text-center
        ${colors}
        ${clickable ? 'cursor-pointer transform hover:scale-105 active:scale-95' : 'cursor-default'}
        ${disabled ? 'opacity-50' : ''}
        ${className}
      `}
      onClick={handleClick}
      role={clickable ? 'button' : 'text'}
      tabIndex={clickable ? 0 : -1}
      onKeyDown={(e) => {
        if ((e.key === 'Enter' || e.key === ' ') && clickable) {
          e.preventDefault();
          handleClick();
        }
      }}
    >
      {/* Word */}
      <span className="font-semibold text-xs sm:text-sm leading-tight break-words">
        {card.word.replace(/_/g, ' ')}
      </span>

      {/* Revealed indicator */}
      {card.isRevealed && (
        <div className="absolute top-1 right-1 w-2 h-2 bg-white rounded-full opacity-75" />
      )}

      {/* Spymaster team indicator (only for unrevealed cards) */}
      {isSpymaster && !card.isRevealed && (
        <div className="absolute bottom-1 left-1 text-xs opacity-70">
          {getTeamEmoji(card.team)}
        </div>
      )}

      {/* Position indicator for debugging (can be removed) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="absolute top-0 left-0 text-xs opacity-30 bg-black text-white px-1 rounded-br">
          {card.position}
        </div>
      )}
    </div>
  );
};

export default Card;
