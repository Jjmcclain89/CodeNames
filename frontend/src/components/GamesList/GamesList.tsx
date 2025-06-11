import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { socketService } from '../../services/socketService';

interface GameLobbyListItem {
  code: string;
  id: string;
  status: string;
  playerCount: number;
  players: string[];
  ownerUsername: string;
  createdAt: string;
  lastActivity: string;
}

interface GamesListProps {
  className?: string;
}

// 🔒 Note: Closed lobbies are automatically filtered out by the backend API
// Only 'waiting' lobbies appear in this list

const GamesList: React.FC<GamesListProps> = ({ className = '' }) => {
  // Games list state
  const [lobbyCode, setLobbyCode] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [isJoining, setIsJoining] = useState(false);
  const [error, setError] = useState('');
  const [gameLobbies, setGameLobbies] = useState<GameLobbyListItem[]>([]);
  const [isLoadingLobbies, setIsLoadingLobbies] = useState(false);
  const navigate = useNavigate();

  // Load game lobbies from backend
  const loadGameLobbiesList = async () => {
    try {
      setIsLoadingLobbies(true);
      setError('');
      const response = await fetch('/api/gameLobbies');
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.success) {
        setGameLobbies(data.gameLobbies || []);
      } else {
        throw new Error(data.error || 'Failed to load game lobbies');
      }
    } catch (err) {
      console.error('❌ Error loading game lobbies:', err);
      setError(err instanceof Error ? err.message : 'Failed to load game lobbies');
      setGameLobbies([]);
    } finally {
      // Add 1-second delay before hiding spinner
      setTimeout(() => {
        setIsLoadingLobbies(false);
      }, 500);
    }
  };

  // Create a new game lobby
  const handleCreateGameLobby = async () => {
    try {
      setIsCreating(true);
      setError('');
      
      // Get user info from localStorage (assuming auth service stores it there)
      const userStr = localStorage.getItem('user');
      const user = userStr ? JSON.parse(userStr) : null;
      
      const response = await fetch('/api/gameLobbies/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId: user?.id || 'anonymous',
          username: user?.username || 'Anonymous'
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.success) {
        // Navigate to the new lobby (real-time update will show it to others)
        navigate(`/lobby/${data.lobbyCode}`);
        
        // Optional: Refresh list after a short delay in case user navigates back quickly
        setTimeout(() => {
          loadGameLobbiesList();
        }, 1000);
      } else {
        throw new Error(data.error || 'Failed to create game lobby');
      }
    } catch (err) {
      console.error('❌ Error creating game lobby:', err);
      setError(err instanceof Error ? err.message : 'Failed to create game lobby');
    } finally {
      setIsCreating(false);
    }
  };

  // Join game with code input
  const handleJoinGameLobby = async () => {
    if (!lobbyCode.trim()) return;
    
    try {
      setIsJoining(true);
      setError('');
      
      // Get user info from localStorage
      const userStr = localStorage.getItem('user');
      const user = userStr ? JSON.parse(userStr) : null;
      
      const response = await fetch('/api/gameLobbies/join', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          lobbyCode: lobbyCode.trim().toUpperCase(),
          userId: user?.id || 'anonymous',
          username: user?.username || 'Anonymous'
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.success) {
        navigate(`/lobby/${data.lobbyCode}`);
      } else {
        throw new Error(data.error || 'Failed to join game lobby');
      }
    } catch (err) {
      console.error('❌ Error joining game lobby:', err);
      setError(err instanceof Error ? err.message : 'Failed to join game lobby');
    } finally {
      setIsJoining(false);
    }
  };

  // Join game from lobby list
  const handleJoinGameFromList = async (code: string) => {
    if (!code.trim()) return;
    
    try {
      setIsJoining(true);
      setError('');
      
      // Get user info from localStorage
      const userStr = localStorage.getItem('user');
      const user = userStr ? JSON.parse(userStr) : null;
      
      const response = await fetch('/api/gameLobbies/join', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          lobbyCode: code.trim().toUpperCase(),
          userId: user?.id || 'anonymous',
          username: user?.username || 'Anonymous'
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.success) {
        navigate(`/lobby/${data.lobbyCode}`);
      } else {
        throw new Error(data.error || 'Failed to join game lobby');
      }
    } catch (err) {
      console.error('❌ Error joining game lobby:', err);
      setError(err instanceof Error ? err.message : 'Failed to join game lobby');
    } finally {
      setIsJoining(false);
    }
  };

  // Handle lobby code input change
  const handleLobbyCodeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.toUpperCase().slice(0, 6);
    setLobbyCode(value);
  };

  // Load game lobbies list on component mount and setup real-time updates
  useEffect(() => {
    loadGameLobbiesList();
    
    // Setup socket connection for real-time updates
    if (!socketService.socket?.connected) {
      const token = localStorage.getItem('token');
      if (token) {
        socketService.connect();
        socketService.authenticate(token);
      }
    }
    
    // Setup socket listeners for real-time lobby updates
    const setupSocketListeners = () => {
      if (socketService.socket) {
        // Listen for new lobbies being created
        socketService.socket.on('lobby:created', (data: any) => {
          console.log('📡 RECEIVED lobby:created event:', data);
          
          // Skip if this is for the current user (they're navigating away)
          const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
          if (data.creatorId && data.creatorId === currentUser.id) {
            console.log('📡 Skipping lobby:created for current user (they are navigating)');
            return;
          }
          
          if (data.lobby) {
            setGameLobbies(prev => {
              // Check for duplicates before adding
              const exists = prev.find(lobby => lobby.code === data.lobby.code);
              if (exists) {
                console.log('📡 Lobby', data.lobby.code, 'already exists in list, skipping duplicate');
                return prev;
              }
              
              console.log('📡 Adding new lobby to list:', data.lobby.code);
              const newList = [data.lobby, ...prev];
              console.log('📡 Updated list length:', newList.length);
              return newList;
            });
          } else {
            console.error('❌ lobby:created event missing lobby data');
          }
        });
        
        // Listen for lobbies being closed (games started)
        socketService.socket.on('lobby:closed', (data: any) => {
          console.log('📡 Lobby closed:', data);
          setGameLobbies(prev => prev.filter(lobby => lobby.code !== data.lobbyCode));
        });
        
        // Listen for lobbies being deleted (empty)
        socketService.socket.on('lobby:deleted', (data: any) => {
          console.log('📡 Lobby deleted:', data);
          setGameLobbies(prev => prev.filter(lobby => lobby.code !== data.lobbyCode));
        });
        
        console.log('📡 Socket listeners setup for real-time lobby updates');
        console.log('📡 Socket ID:', socketService.socket?.id);
        console.log('📡 Socket connected:', socketService.socket?.connected);
        // console.log('📡 Socket rooms:', socketService.socket?.rooms);
      }
    };
    
    // Setup listeners immediately if connected, or when authenticated
    if (socketService.socket?.connected) {
      setupSocketListeners();
    } else {
      socketService.onAuthenticated(() => {
        setupSocketListeners();
      });
    }
    
    // Reduced polling to 30 seconds as backup (since we have real-time updates)
    const interval = setInterval(loadGameLobbiesList, 30000);
    
    return () => {
      clearInterval(interval);
      // Cleanup socket listeners to prevent multiple registrations
      if (socketService.socket) {
        socketService.socket.off('lobby:created');
        socketService.socket.off('lobby:closed');
        socketService.socket.off('lobby:deleted');
        console.log('🧹 Cleaned up socket listeners for GamesList');
      }
    };
  }, []);

  // Refresh lobby list when user returns to page (e.g., after creating a lobby)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        console.log('📱 Page became visible, refreshing lobby list');
        loadGameLobbiesList();
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  // Main component return - THIS is where the JSX goes!
  return (
    <div className={`${className}`}>
      <div className="bg-gradient-to-br from-slate-800/90 to-slate-900/90 rounded-lg sm:rounded-2xl shadow-2xl border border-slate-600/50 p-3 sm:p-6 lg:p-8 backdrop-blur-lg lg:h-[80vh] flex flex-col lg:flex-row lg:gap-8">

        {/* Error Display */}
        {error && (
          <div className="mb-6 lg:mb-0 lg:absolute lg:top-4 lg:left-4 lg:right-4 lg:z-10 p-4 bg-red-900/50 border border-red-500/50 rounded-lg">
            <p className="text-red-200">{error}</p>
          </div>
        )}

        {/* Left Column: Create Game & Join with Code (Desktop) */}
        <div className="lg:w-80 lg:flex-shrink-0 flex flex-col space-y-6">
          {/* Create New Game Button */}
          <div>
            <button 
              onClick={handleCreateGameLobby}
              disabled={isCreating}
              className="w-full bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800 disabled:from-slate-600 disabled:to-slate-700 text-white py-3 px-6 rounded-lg font-semibold transition-all duration-200 shadow-lg hover:shadow-emerald-500/25 text-lg"
            >
              {isCreating ? (
                <span className="flex items-center justify-center">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-3"></div>
                  Creating Game...
                </span>
              ) : (
                <span className="flex items-center justify-center">
                  <span className="text-xl mr-2">🎮</span>
                  Create New Game
                </span>
              )}
            </button>
          </div>

          {/* Join with Code */}
          <div className="border-t border-slate-600/30 pt-6 lg:border-t-0 lg:pt-0">
            <div className="p-3 sm:p-4 lg:p-6 hover:bg-slate-700/10 transition-all duration-200 rounded-lg sm:rounded-xl">
              <h4 className="text-base sm:text-lg font-semibold text-slate-100 mb-3 flex items-center">
                <span className="text-xl mr-2">🚪</span>
                Join Game with Code:
              </h4>
              <div className="flex items-center gap-3">
                <input
                  type="text"
                  value={lobbyCode}
                  onChange={handleLobbyCodeChange}
                  className="flex-1 px-3 py-2 bg-slate-700/60 border border-slate-500/50 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-slate-100 backdrop-blur-sm uppercase text-center font-mono placeholder-slate-400"
                  placeholder="ABCD12"
                  maxLength={6}
                  disabled={isJoining}
                />
                <button 
                  onClick={handleJoinGameLobby}
                  disabled={isJoining || !lobbyCode.trim()}
                  className="flex-shrink-0 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-slate-600 disabled:to-slate-700 text-white py-2 px-4 rounded-lg font-semibold transition-all duration-200 shadow-lg hover:shadow-blue-500/25"
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
          </div>
        </div>

        {/* Right Column: Active Game Lobbies */}
        <div className="flex-1 flex flex-col h-auto">
          <div className="flex justify-between items-center mb-3 sm:mb-4 lg:mb-6">
            <h3 className="text-lg sm:text-xl font-semibold text-slate-100">
              Active Game Lobbies <span className="text-sm text-slate-400">({gameLobbies.length})</span>
            </h3>
            <button 
              onClick={loadGameLobbiesList}
              disabled={isLoadingLobbies}
              className="text-blue-400 hover:text-blue-300 font-medium flex items-center space-x-2 transition-colors duration-200 disabled:opacity-50"
            >
              {isLoadingLobbies ? (
                <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <span>🔄</span>
              )}
            </button>
          </div>
          
          <div className="p-2 sm:p-4 lg:p-6 lg:flex-1 lg:overflow-y-auto lg:min-h-0">
            {gameLobbies.length > 0 ? (
              <div className="grid gap-4">
                {gameLobbies.map((lobby) => (
                  <div key={lobby.code} className="border-2 border-slate-300/60 rounded-lg bg-gradient-to-br from-slate-200/20 via-slate-300/15 to-slate-400/20 p-3 sm:p-4 shadow-lg shadow-slate-500/30 backdrop-blur-sm hover:shadow-xl hover:shadow-slate-400/40 transition-all duration-300 hover:border-slate-200/80">
                    {/* Title Section */}
                    <div className="flex items-center justify-between mb-3">
                      {/* Left: User's Game */}
                      <h3 className="text-lg font-semibold text-slate-100">
                        {lobby.ownerUsername}'s Game
                      </h3>
                      
                      {/* Right: ID */}
                      <div className="text-sm text-slate-400 font-mono">
                        ID:{lobby.code}
                      </div>
                    </div>

                    {/* Players Info */}
                    <div className="text-sm text-slate-300 mb-2 text-left">
                      <span className="font-medium">Players:</span> {lobby.players.length > 0 ? lobby.players.join(', ') : 'None'}
                    </div>
                    
                    <hr className="border-slate-300/40 mb-4" />
                    
                    {/* Join Game Button */}
                    <div className="border border-slate-300/40 rounded bg-slate-100/5">
                      <button
                        onClick={() => handleJoinGameFromList(lobby.code)}
                        className="w-full py-1.5 px-4 text-white font-semibold hover:bg-blue-500/20 hover:text-white transition-all duration-200 bg-blue-500/10 border border-blue-400/40 hover:border-blue-500/60"
                      >
                        Join Game
                      </button>
                    </div>
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
      </div>
    </div>
  );
};

export default GamesList;