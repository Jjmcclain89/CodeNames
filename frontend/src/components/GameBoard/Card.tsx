import React, { useState } from 'react';
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
    // ✅ Spymasters can see the true colors clearly (more obvious than before)
    switch (team) {
      case 'red':
        return 'bg-red-200 border-red-500 text-red-900 hover:bg-red-300 shadow-md';
      case 'blue':
        return 'bg-blue-200 border-blue-500 text-blue-900 hover:bg-blue-300 shadow-md';
      case 'neutral':
        return 'bg-gray-200 border-gray-500 text-gray-800 hover:bg-gray-300 shadow-md';
      case 'assassin':
        return 'bg-gray-900 border-black text-red-400 hover:bg-black shadow-lg font-bold';
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
  const [showSubmit, setShowSubmit] = useState(false);

  const handleClick = () => {
    if (!disabled && onClick && !card.isRevealed) {
      // ✅ Show submit button inside the card
      setShowSubmit(true);
    }
  };

  const handleSubmit = () => {
    if (onClick) {
      onClick(card.id);
      setShowSubmit(false);
    }
  };

  const handleCancel = () => {
    setShowSubmit(false);
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
        ${showSubmit ? 'ring-4 ring-blue-400 ring-opacity-50' : ''}
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
      {/* Word - hidden when submit buttons are shown */}
      {!showSubmit && (
        <span className="font-semibold text-xs sm:text-sm leading-tight break-words">
          {card.word.replace(/_/g, ' ')}
        </span>
      )}

      {/* ✅ Submit/Cancel buttons - shown when card is clicked */}
      {showSubmit && !card.isRevealed && (
        <div className="flex flex-col gap-2 w-full">
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleSubmit();
            }}
            className="bg-green-500 text-white px-2 py-1 rounded text-xs font-bold hover:bg-green-600 transition-colors"
          >
            ✓ GUESS
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleCancel();
            }}
            className="bg-gray-500 text-white px-2 py-1 rounded text-xs hover:bg-gray-600 transition-colors"
          >
            ✗ Cancel
          </button>
        </div>
      )}

      {/* Revealed indicator */}
      {card.isRevealed && (
        <div className="absolute top-1 right-1 w-2 h-2 bg-white rounded-full opacity-75" />
      )}

      {/* ✅ Spymaster team indicator (only for unrevealed cards) - More visible */}
      {isSpymaster && !card.isRevealed && !showSubmit && (
        <div className="absolute bottom-1 left-1 text-lg opacity-90 bg-white rounded-full p-1 shadow-sm">
          {getTeamEmoji(card.team)}
        </div>
      )}

      {/* Position indicator for debugging (can be removed) */}
      {process.env.NODE_ENV === 'development' && !showSubmit && (
        <div className="absolute top-0 left-0 text-xs opacity-30 bg-black text-white px-1 rounded-br">
          {card.position}
        </div>
      )}
    </div>
  );
};

export default Card;