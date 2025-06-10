import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { socketService } from '../services/socketService';
import { gameService } from '../services/gameService';
import GameBoard from '../components/GameBoard/GameBoard';

const GamePage: React.FC = () => {
  const { gameId } = useParams<{ gameId: string }>();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [gameState, setGameState] = useState<any>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [currentUser, setCurrentUser] = useState<any>(null);
    const [isUnauthorized, setIsUnauthorized] = useState(false);
    const [redirectCountdown, setRedirectCountdown] = useState(5);

  useEffect(() => {
    if (!gameId) return;
    
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    setCurrentUser(user);
    loadGameAndConnect();
    
    return () => {
      gameService.removeAllGameListeners();
      if (socketService.socket) {
        socketService.socket.off('game:state-updated');
        socketService.socket.off('game:clue-given');
        socketService.socket.off('game:card-revealed');
        socketService.socket.off('game:turn-changed');
        socketService.socket.off('game:game-ended');
      }
    };
  }, [gameId]);


  const handleManualRejoin = () => {
    if (gameId && socketService.socket?.connected) {
      console.log('🔄 Manually requesting rejoin for game:', gameId);
      socketService.socket.emit('rejoin-game', gameId);
    }
  };

  const loadGameAndConnect = async () => {
    console.log('🎮 [LOAD] Starting loadGameAndConnect for game:', gameId);
    
    if (!gameId) {
      console.log('❌ [LOAD] No game ID provided');
      setError('No game ID provided');
      setIsLoading(false);
      return;
    }

    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const token = localStorage.getItem('token');
      
      if (!user.username || !token) {
        console.log('❌ [LOAD] No user or token');
        setError('Please log in first');
        setIsLoading(false);
        return;
      }

      console.log('🔐 [LOAD] Checking game access authorization...');
      console.log("🔐 [LOAD] User:", user.username, user.id);
      console.log("🔐 [LOAD] Token length:", token?.length);
      
      // First check if user has access to this game
      try {
        const accessResponse = await fetch(`/api/games/${gameId}/access`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        console.log('🔐 [LOAD] Access check status:', accessResponse.status);
        console.log('🔐 [LOAD] Access response headers:', Object.fromEntries(accessResponse.headers.entries()));
        
        if (accessResponse.status === 403) {
          console.log('❌ [LOAD] User not authorized for this game');
          setIsUnauthorized(true);
          setIsLoading(false);
          return;
        } else if (accessResponse.status === 404) {
          console.log('❌ [LOAD] Game not found');
          setError('Game not found');
          setIsLoading(false);
          return;
        } else if (accessResponse.status === 401) {
          console.log('❌ [LOAD] Invalid token');
          setError('Please log in again');
          setIsLoading(false);
          return;
        }
      } catch (accessError) {
        console.log('⚠️ [LOAD] Access check failed, trying direct game load');
      }

            console.log('🔍 [FRONTEND] === GAME LOADING DEBUG ===');
      console.log('🔍 [FRONTEND] Game ID from URL:', gameId);
      console.log('🔍 [FRONTEND] User:', user.username, user.id);
      console.log('🔍 [FRONTEND] Token exists:', !!token);
      console.log('🔍 [FRONTEND] About to fetch from API...');
      console.log('📡 [LOAD] Loading game data...');
      
      // Load game data
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      try {
        const gameResponse = await fetch(`/api/games/${gameId}`, {
          signal: controller.signal
        });
        clearTimeout(timeoutId);
        
                console.log('🔍 [FRONTEND] API Response details:');
        console.log('  - Status:', gameResponse.status);
        console.log('  - Status Text:', gameResponse.statusText);
        console.log('  - URL:', gameResponse.url);
        
        if (!gameResponse.ok) {
          const errorText = await gameResponse.text();
          console.log('  - Error body:', errorText);
        }
        
        if (gameResponse.ok) {
          const gameData = await gameResponse.json();
          
          if (gameData.success && gameData.game) {
            console.log('✅ [LOAD] Game loaded, status:', gameData.game.status);
            setGameState(gameData.game);
            setIsLoading(false);
            
            // Connect to socket in background
            console.log('🔌 [LOAD] Starting socket connection...');
            connectToGame(gameId, token, user).catch((error) => {
              console.log('⚠️ [LOAD] Socket connection failed:', error);
            });
            
            console.log('✅ [LOAD] Loading complete');
          } else {
            throw new Error(gameData.error || 'Failed to load game data');
          }
        } else if (gameResponse.status === 404) {
          console.log('❌ [LOAD] Game not found (404)');
          setError('Game not found');
          setIsLoading(false);
          return;
        } else {
          throw new Error(`Server error: ${gameResponse.status}`);
        }
      } catch (fetchError: any) {
        clearTimeout(timeoutId);
        if (fetchError.name === 'AbortError') {
          throw new Error('Request timed out - server may be slow');
        }
        throw fetchError;
      }
      
    } catch (err: any) {
      console.error('❌ [LOAD] Error in loadGameAndConnect:', err);
      setError(err.message || 'Unable to connect to game');
      setIsLoading(false);
    }
  };

  const connectToGame = async (gameId: string, token: string, user: any): Promise<void> => {
    console.log('🔌 [SOCKET] Starting connectToGame...');
    
    return new Promise<void>((resolve) => {
      // Shorter timeout for better UX - 2 seconds max
      const connectionTimeout = setTimeout(() => {
        console.log('⏰ [SOCKET] Quick timeout, continuing without waiting');
        resolve(); // Always resolve to continue loading
      }, 2000); // Reduced from 5000 to 2000
      
      if (!socketService.socket?.connected) {
        console.log('❌ [SOCKET] No socket connection, continuing anyway');
        clearTimeout(connectionTimeout);
        resolve(); // Don't block the game start
        return;
      }

      const handleAuth = () => {
        console.log('✅ [SOCKET] Authentication successful, joining game...');
        socketService.socket?.emit('join-game', gameId);
        setIsConnected(true);
        setupGameListeners();
        clearTimeout(connectionTimeout);
        resolve();
      };

      const handleAuthFailed = (data: any) => {
        console.log('❌ [SOCKET] Authentication failed, continuing anyway:', data.error);
        clearTimeout(connectionTimeout);
        resolve(); // Don't block the game start
      };

      // Set up one-time listeners
      socketService.socket.once('authenticated', (data: any) => {
        if (data.success) {
          handleAuth();
        } else {
          handleAuthFailed(data);
        }
      });
      
      console.log('🔑 [SOCKET] Sending authentication...');
      socketService.authenticate(token);
      
      // For game start, resolve immediately if already authenticated
      if (socketService.isConnected) {
        console.log('🔌 [SOCKET] Already connected, resolving immediately');
        clearTimeout(connectionTimeout);
        handleAuth();
      }
    });
  };

  const setupGameListeners = () => {
    gameService.removeAllGameListeners();    
    // 🔐 Socket authorization error handling
    if (socketService.socket) {
      socketService.socket.on('game:error', (data: any) => {
        console.log('🔐 [SOCKET] Game error received:', data);
        if (data.code === 'NOT_AUTHORIZED') {
          console.log('❌ [SOCKET] Not authorized for this game');
          setIsUnauthorized(true);
          setIsLoading(false);
        } else {
          setError(data.error || 'Game error occurred');
        }
      });
    }
    
    gameService.onGameStateUpdated((newGameState: any) => {
      console.log('🎮 Game state updated:', newGameState);
      
      // 🔍 DEBUG: Check clue in received game state
      console.log('🔍 [STATE UPDATE] Current clue in new state:', newGameState.currentClue);
      console.log('🔍 [STATE UPDATE] Guesses remaining:', newGameState.guessesRemaining);
      console.log('🔍 [STATE UPDATE] Before setting state, old clue was:', gameState?.currentClue);
      
      // 🔍 DEBUG: Check solo mode status
      console.log('🔍 [SOLO MODE DEBUG] isSoloMode:', newGameState.isSoloMode);
      console.log('🔍 [SOLO MODE DEBUG] soloTeam:', newGameState.soloTeam);
      console.log('🔍 [SOLO MODE DEBUG] Red team:', newGameState.redTeam ? 'exists' : 'null');
      console.log('🔍 [SOLO MODE DEBUG] Blue team:', newGameState.blueTeam ? 'exists' : 'null');
      
      setGameState(newGameState);
      
      console.log('🔍 [STATE UPDATE] State should now be updated with clue');
    });

    gameService.onGameError((error: string) => {
      console.error('🎮 Game error:', error);
      setError(error);
      setTimeout(() => setError(''), 3000);
    });
    
    
    // 🔄 Auto-rejoin event listeners
    if (socketService.socket) {
      socketService.socket.on('game:auto-rejoined', (data: any) => {
        console.log('🔄 Auto-rejoined game:', data.gameCode);
        console.log('📡 Game state restored:', data.gameState);
        setGameState(data.gameState);
        setIsConnected(true);
      });
      
      socketService.socket.on('game:rejoined', (data: any) => {
        console.log('🔄 Manually rejoined game:', data.gameId);
        setGameState(data.gameState);
      });
    }

    if (socketService.socket) {
      socketService.socket.on('game:clue-given', (clue: any) => {
        console.log('💡 Clue given:', clue);
        console.log('🔍 [CLUE EVENT] Current gameState.currentClue before this event:', gameState?.currentClue);
        console.log('🔍 [CLUE EVENT] This might be redundant if game:state-updated is working');
      });
      
      socketService.socket.on('game:card-revealed', (card: any) => {
        console.log('🎯 Card revealed:', card);
      });
      
      socketService.socket.on('game:turn-changed', (newTurn: string) => {
        console.log('⏭️ Turn changed:', newTurn);
      });
      
      socketService.socket.on('game:game-ended', (winner: string) => {
        console.log('🏆 Game ended, winner:', winner);
      });
    }
  };

  const getCurrentUserPlayer = () => {
    if (!gameState || !currentUser) return null;
    
    // Check red team spymaster
    if (gameState.redTeam?.spymaster && 
        (gameState.redTeam.spymaster.username === currentUser.username || 
         gameState.redTeam.spymaster.id === currentUser.id)) {
      return {
        ...gameState.redTeam.spymaster,
        team: 'red' as const,
        role: 'spymaster' as const
      };
    }
    
    // Check red team operatives
    if (gameState.redTeam?.operatives) {
      const redOperative = gameState.redTeam.operatives.find((p: any) => 
        p.username === currentUser.username || p.id === currentUser.id
      );
      if (redOperative) {
        return {
          ...redOperative,
          team: 'red' as const,
          role: 'operative' as const
        };
      }
    }
    
    // Check blue team spymaster
    if (gameState.blueTeam?.spymaster && 
        (gameState.blueTeam.spymaster.username === currentUser.username || 
         gameState.blueTeam.spymaster.id === currentUser.id)) {
      return {
        ...gameState.blueTeam.spymaster,
        team: 'blue' as const,
        role: 'spymaster' as const
      };
    }
    
    // Check blue team operatives
    if (gameState.blueTeam?.operatives) {
      const blueOperative = gameState.blueTeam.operatives.find((p: any) => 
        p.username === currentUser.username || p.id === currentUser.id
      );
      if (blueOperative) {
        return {
          ...blueOperative,
          team: 'blue' as const,
          role: 'operative' as const
        };
      }
    }
    
    return null;
  };

  // Loading State
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center">
        <div className="text-center bg-white p-8 rounded-2xl shadow-xl">
          <div className="text-2xl font-bold text-gray-900 mb-4">🎮 Loading Game...</div>
          <div className="text-gray-600 mb-6">Game: <span className="font-mono bg-gray-100 px-2 py-1 rounded">{gameId}</span></div>
          <div className="flex justify-center">
            <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
          </div>
        </div>
      </div>
    );
  }

  // Unauthorized Access State
  if (isUnauthorized) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-900 flex items-center justify-center relative">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-red-400 via-transparent to-transparent"></div>
          <div className="absolute inset-0 bg-[linear-gradient(45deg,_transparent_25%,_rgba(255,255,255,0.02)_25%,_rgba(255,255,255,0.02)_50%,_transparent_50%,_transparent_75%,_rgba(255,255,255,0.02)_75%)] bg-[length:60px_60px]"></div>
        </div>
        
        <div className="text-center bg-gradient-to-br from-slate-800/90 to-slate-900/90 p-8 rounded-2xl shadow-2xl border border-red-500/50 backdrop-blur-lg max-w-md mx-4">
          <div className="text-red-400 text-4xl font-bold mb-4">🚫</div>
          <div className="text-red-400 text-2xl font-bold mb-4">Access Denied</div>
          <div className="text-slate-300 mb-6">
            <p className="mb-2">You are not authorized to access this game.</p>
            <p className="text-amber-300 font-mono bg-slate-700/50 px-2 py-1 rounded">Game: {gameId}</p>
            <p className="mt-4 text-slate-400 text-sm">
              You can only access games that you have joined or created.
            </p>
          </div>
          
          {/* Countdown */}
          <div className="mb-6 p-3 bg-amber-900/30 border border-amber-500/50 rounded-lg">
            <p className="text-amber-300 text-sm">
              Redirecting to home in <span className="font-bold text-amber-200">{redirectCountdown}</span> seconds...
            </p>
          </div>
          
          <div className="space-y-3">
            <button 
              onClick={() => navigate('/')}
              className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white px-6 py-3 rounded-lg font-semibold transition-all duration-200 shadow-lg"
            >
              🏠 Go to Home Now
            </button>
            <button 
              onClick={() => navigate('/lobby')}
              className="w-full bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white px-6 py-3 rounded-lg font-semibold transition-all duration-200 shadow-lg"
            >
              🎮 Join a Game
            </button>
            <button 
              onClick={() => window.location.reload()}
              className="w-full bg-gradient-to-r from-slate-600 to-slate-700 hover:from-slate-700 hover:to-slate-800 text-white px-6 py-3 rounded-lg font-semibold transition-all duration-200 shadow-lg"
            >
              🔄 Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

    // Error State
  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center">
        <div className="text-center bg-white p-8 rounded-2xl shadow-xl max-w-md">
          <div className="text-red-600 text-2xl font-bold mb-4">🚨 Game Error</div>
          <div className="text-gray-600 mb-6">
            <p>Game: <span className="font-mono bg-gray-100 px-2 py-1 rounded font-bold">{gameId}</span></p>
            <p className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg text-sm">{error}</p>
          </div>
          <div className="space-y-3">
            <button 
              onClick={() => navigate('/')}
              className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white px-6 py-3 rounded-lg font-semibold transition-all duration-200 shadow-lg"
            >
              🏠 Go Back to Home
            </button>
            <button 
              onClick={handleManualRejoin}
              className="w-full bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white px-6 py-3 rounded-lg font-semibold transition-all duration-200 shadow-lg"
            >
              🔄 Try to Rejoin Game
            </button>
            <button 
              onClick={() => window.location.reload()}
              className="w-full bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-700 hover:to-gray-800 text-white px-6 py-3 rounded-lg font-semibold transition-all duration-200 shadow-lg"
            >
              🔄 Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Game State - Render the actual game
  if (gameState) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-900 relative">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-blue-400 via-transparent to-transparent"></div>
          <div className="absolute inset-0 bg-[linear-gradient(45deg,_transparent_25%,_rgba(255,255,255,0.02)_25%,_rgba(255,255,255,0.02)_50%,_transparent_50%,_transparent_75%,_rgba(255,255,255,0.02)_75%)] bg-[length:60px_60px]"></div>
        </div>

        {/* Game Content */}
        <div className="relative z-10">
          {/* Error Display */}
          {error && (
            <div className="mb-6 mx-4 p-4 bg-red-900/50 border border-red-500/50 rounded-lg">
              <p className="text-red-200">{error}</p>
            </div>
          )}

          {/* Game Board */}
          <GameBoard 
            gameState={gameState}
            currentPlayer={getCurrentUserPlayer()}
            isConnected={isConnected}
          />
        </div>
      </div>
    );
  }

  // Fallback - should not reach here
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center pt-16">
      <div className="text-center">
        <div className="text-2xl font-bold text-gray-900 mb-4">🎮 Codenames</div>
        <p className="text-gray-600">Game not found</p>
      </div>
    </div>
  );
};

export default GamePage;