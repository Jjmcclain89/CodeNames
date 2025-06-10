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

  const loadGameAndConnect = async () => {
    
    
    if (!gameId) {
      
      setError('No game ID provided');
      setIsLoading(false);
      return;
    }

    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const token = localStorage.getItem('token');
      
      
      
      if (!user.username || !token) {
        
        setError('Please log in first');
        setIsLoading(false);
        return;
      }

      // Load game state
      
      const gameResponse = await fetch(`/api/games/${gameId}`);
      
      
      
      if (gameResponse.ok) {
        const gameData = await gameResponse.json();
        
        
        if (gameData.success) {
          
          
          
          
          setGameState(gameData.game);
          
          // Allow waiting games to proceed (they'll show team setup)
          // Only reject if the game is in an invalid state
          if (gameData.game.status === 'finished') {
            console.log('🏁 Game is finished, proceeding to show results');
          } else if (gameData.game.status === 'waiting') {
            console.log('⏳ Game is in waiting/setup state, will show team selection');
          } else {
            console.log(`🎮 Game status: ${gameData.game.status}`);
          }
          
          
          // Connect to game socket
          await connectToGame(gameId, token, user);
          
          setIsLoading(false);
        } else {
          
          throw new Error(gameData.error || 'Failed to load game');
        }
      } else if (gameResponse.status === 404) {
        
        setError('Game not found');
        setIsLoading(false);
        return;
      } else {
        
        throw new Error('Failed to load game');
      }
      
    } catch (err: any) {
      
      setError(err.message || 'Unable to connect to game');
      setIsLoading(false);
    }
  };

  const connectToGame = async (gameId: string, token: string, user: any) => {
    if (isConnected && socketService.socket?.connected) {
      return Promise.resolve();
    }
    
    return new Promise<void>((resolve) => {
      if (!socketService.socket?.connected) {
        console.log('❌ No socket connection available');
        return;
      }

      const handleAuth = () => {
        socketService.socket?.emit('join-game', gameId);
        setIsConnected(true);
        setupGameListeners();
        resolve();
      };

      socketService.onAuthenticated((data: any) => {
        if (data.success) handleAuth();
      });
      
      socketService.authenticate(token);
      
      if (socketService.socket?.connected && !isConnected) {
        handleAuth();
      }
    });
  };

  const setupGameListeners = () => {
    gameService.removeAllGameListeners();
    
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