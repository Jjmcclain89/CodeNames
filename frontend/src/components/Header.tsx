import React from 'react';
import { useNavigate } from 'react-router-dom';

interface HeaderProps {
  user: {
    id: string;
    username: string;
  };
  onLogout: () => void;
}

const Header: React.FC<HeaderProps> = ({ user, onLogout }) => {
  const navigate = useNavigate();
  
  const handleLogoClick = () => {
    navigate('/');
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50 h-16">
      {/* Translucent background with glass effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-slate-900/80 via-slate-800/75 to-indigo-900/80 backdrop-blur-md border-b border-slate-600/30">
        {/* Subtle shine effect */}
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent"></div>
      </div>
      
      {/* Header content */}
      <div className="relative h-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between">
        {/* Left side - Clickable Logo/Title */}
        <div className="flex items-center space-x-3">
          <button
            onClick={handleLogoClick}
            className="text-2xl font-bold bg-gradient-to-r from-blue-400 via-violet-400 to-indigo-400 bg-clip-text text-transparent hover:scale-105 hover:drop-shadow-lg transition-all duration-200 cursor-pointer focus:outline-none rounded-lg px-2 py-1"
          >
            Codenames
          </button>
        </div>
        
        {/* Right side - User info and logout */}
        <div className="flex items-center space-x-4">
          {/* User greeting */}
          <div className="hidden sm:flex items-center space-x-2 text-slate-300">
            <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
            <span className="text-sm">Welcome, <span className="font-semibold text-white">{user.username}</span></span>
          </div>
          
          {/* Mobile user indicator */}
          <div className="sm:hidden flex items-center space-x-2 text-slate-300">
            <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
            <span className="text-sm font-semibold text-white">{user.username}</span>
          </div>
          
          {/* Logout button */}
          <button
            onClick={onLogout}
            className="group flex items-center space-x-2 bg-red-600/20 hover:bg-red-600/30 border border-red-500/30 hover:border-red-400/50 text-red-400 hover:text-red-300 px-3 py-2 rounded-lg transition-all duration-200 backdrop-blur-sm"
          >
            <svg 
              className="w-4 h-4 group-hover:rotate-12 transition-transform duration-200" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            <span className="text-sm font-medium hidden sm:block">Logout</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;