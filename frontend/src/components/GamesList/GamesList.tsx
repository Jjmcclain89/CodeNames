import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface GameLobbyListItem {
  code: string;
  id: string;
  status: string;
  playerCount: number;
  players: string[];
  createdAt: string;
  lastActivity: string;
}

interface GamesListProps {
  className?: string;
}

const GamesList: React.FC<GamesListProps> = ({ className = '' }) => {
  // Games list state
  const [lobbyCode, setLobbyCode] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [isJoining, setIsJoining] = useState(false);
  const [error, setError] = useState('');
  const [gameLobbies, setGameLobbies] = useState<GameLobbyListItem[]>([]);
  const [isLoadingLobbies, setIsLoadingLobbies] = useState(false);
  const navigate = useNavigate();

  // Load game lobbies list on component mount and refresh periodically
  useEffect(() => {
    loadGameLobbiesList();
    
    // Refresh lobbies list every 10 seconds
    const interval = setInterval(loadGameLobbiesList, 10000);
    
    return () => clearInterval(interval);
  }, []);

  const loadGameLobbiesList = async () => {
    setIsLoadingLobbies(true);
    try {
      console.log('📋 Loading game lobbies list...');
      const response = await fetch('/api/gamelobbies');
      const data = await response.json();
      
      if (data.success) {
        setGameLobbies(data.gameLobbies || []);
        console.log(`✅ Loaded ${data.gameLobbies?.length || 0} game lobbies`);
      } else {
        console.error('Failed to load game lobbies list:', data.error);
      }
    } catch (err) {
      console.error('Error loading game lobbies list:', err);
    }
    setIsLoadingLobbies(false);
  };

  // Better error handling function
  const handleApiResponse = async (response: Response) => {
    const contentType = response.headers.get('content-type');
    
    if (!response.ok) {
      if (!contentType?.includes('application/json')) {
        const text = await response.text();
        throw new Error(`HTTP ${response.status}: Server returned HTML instead of JSON. Check if backend is running and proxy is configured.`);
      }
    }
    
    if (contentType?.includes('application/json')) {
      return await response.json();
    } else {
      const text = await response.text();
      throw new Error(`Expected JSON but got: ${contentType}. Response: ${text.substring(0, 100)}...`);
    }
  };

  const handleCreateGameLobby = async () => {
    setIsCreating(true);
    setError('');
    
    try {
      console.log('🎮 Creating game lobby...');
      
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      
      const response = await fetch('/api/gamelobbies/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          userId: user.id || `user_${Date.now()}`,
          username: user.username || 'Anonymous',
          debug: true 
        })
      });

      const data = await handleApiResponse(response);
      
      if (data.success && data.lobbyCode) {
        console.log('🎉 Navigating to game lobby:', data.lobbyCode);
        // Refresh games list before navigating
        loadGameLobbiesList();
        navigate(`/lobby/${data.lobbyCode}`);
      } else {
        setError(data.error || 'Failed to create game lobby');
      }
    } catch (err: any) {
      console.error('💥 Error creating game lobby:', err);
      setError(err.message);
    }
    
    setIsCreating(false);
  };

  const handleJoinGameLobby = async () => {
    if (!lobbyCode.trim()) {
      setError('Please enter a lobby code');
      return;
    }
    
    setIsJoining(true);
    setError('');

    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      
      const response = await fetch('/api/gamelobbies/join', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          lobbyCode: lobbyCode.trim().toUpperCase(),
          userId: user.id || `user_${Date.now()}`,
          username: user.username || 'Anonymous'
        })
      });

      const data = await handleApiResponse(response);
      
      if (data.success && data.lobbyCode) {
        console.log('🎉 Navigating to game lobby:', data.lobbyCode);
        navigate(`/lobby/${data.lobbyCode}`);
      } else {
        setError(data.error || 'Failed to join game lobby');
      }
    } catch (err: any) {
      console.error('💥 Error joining game lobby:', err);
      setError(err.message);
    }
    
    setIsJoining(false);
  };

  const handleJoinGameFromList = async (gameCode: string) => {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      
      const response = await fetch('/api/gamelobbies/join', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          lobbyCode: gameCode,
          userId: user.id || `user_${Date.now()}`,
          username: user.username || 'Anonymous'
        })
      });

      const data = await handleApiResponse(response);
      
      if (data.success) {
        navigate(`/lobby/${gameCode}`);
      } else {
        setError(data.error || 'Failed to join game lobby');
      }
    } catch (err: any) {
      console.error('💥 Error joining game lobby from list:', err);
      setError(err.message);
    }
  };

  const handleLobbyCodeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLobbyCode(e.target.value.toUpperCase());
    if (error) setError('');
  };

  const getTimeAgo = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now.getTime() - time.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };

  return (
    <div className={`${className}`}>
      <div className="bg-gradient-to-br from-slate-800/90 to-slate-900/90 rounded-2xl shadow-2xl border border-slate-600/50 p-8 backdrop-blur-lg">

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-900/50 border border-red-500/50 rounded-lg">
            <p className="text-red-200">{error}</p>
          </div>
        )}

        {/* Active Game Lobbies List - Main Focus */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-semibold text-slate-100 flex items-center">
              <span className="text-2xl mr-3">🎯</span>
              Active Game Lobbies
            </h3>
            <button 
              onClick={loadGameLobbiesList}
              disabled={isLoadingLobbies}
              className="text-blue-400 hover:text-blue-300 font-medium flex items-center space-x-2 transition-colors duration-200"
            >
              <span>{isLoadingLobbies ? '🔄 Loading...' : '🔄 Refresh'}</span>
            </button>
          </div>
          
          {/* Game Lobbies List Container */}
          <div className="p-6 min-h-[300px]">
            {gameLobbies.length > 0 ? (
              <div className="space-y-4">
                {gameLobbies.map((lobby) => (
                  <div key={lobby.code} className="flex items-center justify-between p-4 hover:bg-slate-700/20 transition-all duration-200 rounded-lg group">
                    <div className="flex-1">
                      <div className="flex items-center space-x-6">
                        <div className="bg-gradient-to-r from-violet-600 to-indigo-600 text-white px-3 py-2 rounded-lg font-mono font-bold text-lg shadow-lg">
                          {lobby.code}
                        </div>
                        <div className="text-slate-300">
                          <div className="flex items-center space-x-4 mb-1">
                            <span className="font-semibold text-slate-200">{lobby.playerCount} player{lobby.playerCount !== 1 ? 's' : ''}</span>
                            <span className="text-sm text-slate-400">•</span>
                            <span className="text-sm">{getTimeAgo(lobby.lastActivity)}</span>
                            <span className="text-sm text-slate-400">•</span>
                            <span className="text-emerald-400 capitalize font-medium">{lobby.status}</span>
                          </div>
                          {lobby.players.length > 0 && (
                            <div className="text-sm text-slate-400">
                              <span className="font-medium">Players:</span> {lobby.players.join(', ')}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => handleJoinGameFromList(lobby.code)}
                      className="bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800 text-white px-6 py-2 rounded-lg font-semibold transition-all duration-200 shadow-lg hover:shadow-emerald-500/25"
                    >
                      Join Lobby
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-20 text-slate-400">
                <div className="text-5xl mb-4">🎮</div>
                <p className="text-lg font-semibold text-slate-300">No active game lobbies</p>
                <p className="text-slate-400 mt-2">Create the first lobby to get started!</p>
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions - Create & Join */}
        <div className="border-t border-slate-600/30 pt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Join with Code - Left Side */}
          <div className="p-6 hover:bg-slate-700/10 transition-all duration-200 rounded-xl">
            <h4 className="text-lg font-semibold text-slate-100 mb-4 flex items-center">
              <span className="text-xl mr-2">🚪</span>
              Join with Code
            </h4>
            <div className="space-y-3">
              <input
                type="text"
                value={lobbyCode}
                onChange={handleLobbyCodeChange}
                className="w-full px-3 py-2 bg-slate-700/60 border border-slate-500/50 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-slate-100 backdrop-blur-sm uppercase text-center font-mono placeholder-slate-400"
                placeholder="ABCD12"
                maxLength={6}
                disabled={isJoining}
              />
              <button 
                onClick={handleJoinGameLobby}
                disabled={isJoining || !lobbyCode.trim()}
                className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-slate-600 disabled:to-slate-700 text-white py-2 px-4 rounded-lg font-semibold transition-all duration-200 shadow-lg hover:shadow-blue-500/25"
              >
                {isJoining ? (
                  <span className="flex items-center justify-center">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                    Joining...
                  </span>
                ) : (
                  'Join'
                )}
              </button>
            </div>
          </div>

          {/* Create New Game Lobby - Right Side */}
          <div className="p-6 hover:bg-slate-700/10 transition-all duration-200 rounded-xl">
            <h4 className="text-lg font-semibold text-slate-100 mb-4 flex items-center">
              <span className="text-xl mr-2">🎮</span>
              Create New Lobby
            </h4>
            <div className="text-center">
              <button 
                onClick={handleCreateGameLobby}
                disabled={isCreating}
                className="w-full bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800 disabled:from-slate-600 disabled:to-slate-700 text-white py-2 px-4 rounded-lg font-semibold transition-all duration-200 shadow-lg hover:shadow-emerald-500/25"
              >
                {isCreating ? (
                  <span className="flex items-center justify-center">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                    Creating...
                  </span>
                ) : (
                  'Create'
                )}
              </button>
            </div>
          </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GamesList;
