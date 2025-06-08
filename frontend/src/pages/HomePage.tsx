import React from 'react';
import { socketService } from '../services/socketService';
import ChatRoom from '../components/Chat/ChatRoom';
import GamesList from '../components/GamesList';

const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen lg:h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-900 overflow-hidden relative flex flex-col">
      {/* Background Pattern - Matching GameBoard */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-blue-400 via-transparent to-transparent"></div>
        <div className="absolute inset-0 bg-[linear-gradient(45deg,_transparent_25%,_rgba(255,255,255,0.02)_25%,_rgba(255,255,255,0.02)_50%,_transparent_50%,_transparent_75%,_rgba(255,255,255,0.02)_75%)] bg-[length:60px_60px]"></div>
      </div>

      <div className="relative z-10 px-2 sm:px-4 lg:px-6 lg:max-w-7xl lg:mx-auto flex-1 flex flex-col h-full lg:py-4">
        {/* Hero Section with Title */}
        <div className="text-center mb-2 sm:mb-6 lg:mb-4 px-2 flex-shrink-0">
          <h1 className="mt-4 text-4xl font-bold bg-gradient-to-r from-blue-400 via-violet-400 to-indigo-400 bg-clip-text text-transparent mb-4 drop-shadow-lg">
            <span className="sm:hidden">Codenames Online!</span>
            <span className="hidden sm:inline">Welcome to Codenames Online!</span>
          </h1>
          <p className="text-l text-slate-300 max-w-2xl mx-auto hidden sm:block">
            Play Codenames with your friends online! Create a game lobby or join an existing one to start your spy mission.
          </p>
        </div>
        
        {/* Games List Component */}
        <GamesList className="flex-1 min-h-0" />
      </div>
    </div>
  );
};

export default HomePage;
