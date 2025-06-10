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
    // Revealed cards with premium board game styling
    switch (team) {
      case 'red':
        return 'bg-gradient-to-br from-red-600 via-red-500 to-red-700 text-white border-red-800 shadow-2xl shadow-red-500/25';
      case 'blue':
        return 'bg-gradient-to-br from-blue-600 via-blue-500 to-blue-700 text-white border-blue-800 shadow-2xl shadow-blue-500/25';
      case 'neutral':
        return 'bg-gradient-to-br from-slate-500 via-slate-400 to-slate-600 text-white border-slate-700 shadow-2xl shadow-slate-500/25';
      case 'assassin':
        return 'bg-gradient-to-br from-gray-900 via-black to-gray-800 text-red-400 border-red-900 shadow-2xl shadow-red-900/50';
      default:
        return 'bg-gradient-to-br from-stone-300 to-stone-400 text-stone-800 border-stone-500';
    }
  } else if (isSpymaster) {
    // Spymaster view with subtle team colors on premium card base
    switch (team) {
      case 'red':
        return 'bg-gradient-to-br from-slate-700/80 via-red-900/40 to-slate-700/80 border-red-400/50 text-red-200 hover:from-red-800/60 hover:to-red-700/60 shadow-lg hover:shadow-red-500/30 backdrop-blur-sm';
      case 'blue':
        return 'bg-gradient-to-br from-slate-700/80 via-blue-900/40 to-slate-700/80 border-blue-400/50 text-blue-200 hover:from-blue-800/60 hover:to-blue-700/60 shadow-lg hover:shadow-blue-500/30 backdrop-blur-sm';
      case 'neutral':
        return 'bg-gradient-to-br from-slate-700/80 via-slate-600/40 to-slate-700/80 border-slate-400/50 text-slate-200 hover:from-slate-600/80 hover:to-slate-500/80 shadow-lg hover:shadow-slate-500/30 backdrop-blur-sm';
      case 'assassin':
        return 'bg-gradient-to-br from-slate-800/80 via-black-900/60 to-slate-800/80 border-red-500 text-red-300 hover:from-red-900/80 hover:to-red-800/80 shadow-lg hover:shadow-red-600/50 font-bold backdrop-blur-sm';
      default:
        return 'bg-gradient-to-br from-slate-700/80 to-slate-600/80 border-slate-400 text-slate-200 hover:from-slate-600/80 hover:to-slate-500/80 backdrop-blur-sm';
    }
  } else {
    // Regular players see dark card base
    return 'bg-gradient-to-br from-slate-700/80 via-slate-600/60 to-slate-700/80 border-slate-500 text-slate-100 hover:from-slate-600/80 hover:to-slate-600/80 hover:border-slate-400 shadow-lg hover:shadow-slate-500/50 backdrop-blur-sm';
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
        relative w-20 h-20 sm:w-24 sm:h-24 md:w-28 md:h-28 lg:w-32 lg:h-32 p-2 sm:p-3 border-2 rounded-xl flex items-center justify-center
        transition-all duration-300 font-semibold text-center cursor-pointer
        ${colors}
        ${clickable ? 'transform hover:scale-105 hover:shadow-xl hover:-translate-y-1 active:scale-95' : 'cursor-default'}
        ${disabled ? 'opacity-50' : ''}
        ${showSubmit ? 'ring-4 ring-violet-400 ring-opacity-50 scale-105 shadow-xl' : ''}
        ${className}
        backdrop-blur-sm
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
        <span className="font-bold text-xs sm:text-sm md:text-base leading-tight break-words px-1">
          {card.word.replace(/_/g, ' ')}
        </span>
      )}

      {/* Enhanced Submit/Cancel buttons */}
      {showSubmit && !card.isRevealed && (
        <div className="flex flex-col gap-2 w-full">
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleSubmit();
            }}
            className="bg-gradient-to-r from-emerald-600 to-emerald-700 text-white px-2 py-1 rounded-md text-xs font-bold hover:from-emerald-700 hover:to-emerald-800 transition-all duration-200 shadow-lg transform hover:scale-105 border border-emerald-500"
          >
            ✓ GUESS
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleCancel();
            }}
            className="bg-gradient-to-r from-slate-600 to-slate-700 text-white px-2 py-1 rounded-md text-xs hover:from-slate-700 hover:to-slate-800 transition-all duration-200 shadow-lg border border-slate-500"
          >
            ✗ Cancel
          </button>
        </div>
      )}

      {/* Enhanced revealed indicator */}
      {card.isRevealed && (
        <div className="absolute top-1 right-1 w-2 h-2 bg-white rounded-full opacity-90 shadow-sm" />
      )}

      {/* Enhanced spymaster team indicator */}
      {isSpymaster && !card.isRevealed && !showSubmit && (
        <div className="absolute bottom-1 left-1 text-sm bg-gradient-to-br from-slate-600/90 to-slate-700/90 rounded-full p-1 shadow-lg border border-slate-400/50 backdrop-blur-sm">
          {getTeamEmoji(card.team)}
        </div>
      )}
    </div>
  );
};

export default Card;