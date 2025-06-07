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
          
          // Verify this is an active game (not waiting room)
          if (gameData.game.status === 'waiting' || gameData.game.status === 'setup') {
            
            setError('Game has not started yet. Please wait in the room.');
            setIsLoading(false);
            return;
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
      setGameState(newGameState);
    });

    gameService.onGameError((error: string) => {
      console.error('🎮 Game error:', error);
      setError(error);
      setTimeout(() => setError(''), 3000);
    });
    
    if (socketService.socket) {
      socketService.socket.on('game:clue-given', (clue: any) => {
        console.log('💡 Clue given:', clue);
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
    if (!gameState || !gameState.players) return null;
    
    return gameState.players.find((p: any) => 
      p.username === currentUser?.username || p.id === currentUser?.id
    );
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
              className="w-full bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
            >
              🏠 Go Back to Home
            </button>
            <button 
              onClick={() => window.location.reload()}
              className="w-full bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
            >
              🔄 Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Main Game UI - Only show if game is active
  if (gameState && gameState.status === 'playing') {
    return (
      <GameBoard 
        gameState={gameState} 
        currentPlayer={getCurrentUserPlayer()}
        onCardClick={(cardId) => {
          if (!isConnected) {
            setError('Not connected to server');
            return;
          }
          socketService.socket?.emit('game:reveal-card', cardId);
        }}
        onGiveClue={(word, number) => {
          if (!isConnected) {
            setError('Not connected to server');
            return;
          }
          if (!word.trim()) {
            setError('Please enter a clue word');
            return;
          }
          if (number < 1 || number > 9) {
            setError('Number must be between 1 and 9');
            return;
          }
          socketService.socket?.emit('game:give-clue', { word: word.trim(), number });
        }}
        onEndTurn={() => {
          if (!isConnected) {
            setError('Not connected to server');
            return;
          }
          socketService.socket?.emit('game:end-turn');
        }}
        onStartGame={() => {
          // No longer needed - games start from room
        }}
        onJoinTeam={() => {
          // No longer needed - team assignment happens in room
        }}
      />
    );
  }

  // Fallback if game state is invalid
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center">
      <div className="text-center bg-white p-8 rounded-2xl shadow-xl max-w-md">
        <div className="text-yellow-600 text-2xl font-bold mb-4">⚠️ Invalid Game State</div>
        <div className="text-gray-600 mb-6">
          <p>This game is not ready for play.</p>
          <p className="text-sm mt-2">Game Status: {gameState?.status || 'Unknown'}</p>
          <p className="text-xs mt-2 font-mono bg-gray-100 p-2 rounded">
            Debug: isLoading={isLoading ? 'true' : 'false'}, 
            error="{error}", 
            gameState={gameState ? 'exists' : 'null'}
          </p>
        </div>
        <button 
          onClick={() => navigate('/')}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
        >
          🏠 Go Back to Home
        </button>
      </div>
    </div>
  );
};

export default GamePage;