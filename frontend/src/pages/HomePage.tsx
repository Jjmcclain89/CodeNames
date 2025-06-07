import React from 'react';
import { socketService } from '../services/socketService';
import ChatRoom from '../components/Chat/ChatRoom';
import GameLobby from '../components/GameLobby';

const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-900 overflow-hidden relative">
      {/* Background Pattern - Matching GameBoard */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-blue-400 via-transparent to-transparent"></div>
        <div className="absolute inset-0 bg-[linear-gradient(45deg,_transparent_25%,_rgba(255,255,255,0.02)_25%,_rgba(255,255,255,0.02)_50%,_transparent_50%,_transparent_75%,_rgba(255,255,255,0.02)_75%)] bg-[length:60px_60px]"></div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto p-6">
        {/* Hero Section with Title */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 via-violet-400 to-indigo-400 bg-clip-text text-transparent mb-4 drop-shadow-lg">
            Welcome to Codenames Online!
          </h1>
          <p className="text-l text-slate-300 max-w-2xl mx-auto">
            Play Codenames with your friends online! Create a game or join an existing one to start your spy mission.
          </p>
        </div>
        
        {/* Game Lobby Component */}
        <GameLobby className="mb-8" />
      </div>
    </div>
  );
};

export default HomePage;