import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import GameBoard from '../components/GameBoard/GameBoard';
import { gameService } from '../services/gameService';
import { socketService } from '../services/socketService';
import { CodenamesGame, GamePlayer } from '../types/game';

const GamePage: React.FC = () => {
  const navigate = useNavigate();
  const [gameState, setGameState] = useState<CodenamesGame | null>(null);
  const [currentPlayer, setCurrentPlayer] = useState<GamePlayer | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    initializeGame();
    return () => {
      gameService.removeAllGameListeners();
    };
  }, [navigate]);

  const initializeGame = async () => {
    // Check authentication
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    
    if (!token || !user) {
      navigate('/login');
      return;
    }

    const userData = JSON.parse(user);
    
    try {
      // Initialize socket if not connected
      if (!socketService.isConnected) {
        socketService.connect();
      }

      // Set up connection handlers
      socketService.onConnect(() => {
        console.log('🔌 Connected to server');
        setIsConnected(true);
        socketService.authenticate(token);
      });

      socketService.onAuthenticated((data) => {
        if (data.success) {
          console.log('✅ Authenticated successfully');
          setupGameListeners(userData);
          
          // Try to get existing game state or create new one
          initializeGameState();
          setError(null);
        } else {
          console.error('❌ Authentication failed:', data.error);
          setError('Authentication failed');
          navigate('/login');
        }
      });

      socketService.onDisconnect(() => {
        console.log('❌ Disconnected from server');
        setIsConnected(false);
        setError('Disconnected from server');
      });

      // If already connected, authenticate immediately
      if (socketService.isConnected) {
        socketService.authenticate(token);
      }

    } catch (err) {
      console.error('Error initializing game:', err);
      setError('Failed to initialize game');
      setIsLoading(false);
    }
  };

  const setupGameListeners = (user: any) => {
    // Remove existing listeners first
    gameService.removeAllGameListeners();
    
    gameService.onGameStateUpdated((game: CodenamesGame) => {
      console.log('🎮 Game state updated:', game);
      setGameState(game);
      setIsLoading(false);
      
      // Find current player in the game
      const player = game.players.find(p => p.id === user.id || p.username === user.username);
      setCurrentPlayer(player || null);
    });

    gameService.onGameError((error: string) => {
      console.error('🎮 Game error:', error);
      setError(error);
      setTimeout(() => setError(null), 5000);
    });

    gameService.onCardRevealed((card) => {
      console.log('🎯 Card revealed:', card.word, card.team);
    });

    gameService.onClueGiven((clue) => {
      console.log('💡 Clue given:', clue.word, clue.number);
    });

    gameService.onGameEnded((winner) => {
      console.log('🎉 Game ended! Winner:', winner);
    });
  };

  const initializeGameState = () => {
    console.log('🎯 Initializing game state...');
    
    // Try to join existing game or create new one
    setTimeout(() => {
      // First try to request current game state
      socketService.socket?.emit('game:request-state');
      
      // If no response in 2 seconds, create a new game
      setTimeout(() => {
        if (!gameState) {
          console.log('🎮 No existing game found, creating new game...');
          gameService.createGame();
        }
      }, 2000);
    }, 500);
  };

  const handleCardClick = (cardId: string) => {
    gameService.revealCard(cardId);
  };

  const handleGiveClue = (word: string, number: number) => {
    gameService.giveClue(word, number);
  };

  const handleEndTurn = () => {
    gameService.endTurn();
  };

  const handleStartGame = () => {
    gameService.startGame();
  };

  const handleJoinTeam = (team: any, role: any) => {
    gameService.joinTeam(team, role);
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-700">Connecting to game...</h2>
          <p className="text-gray-600 mt-2">Setting up your Codenames experience</p>
          {error && (
            <p className="text-red-600 mt-2">{error}</p>
          )}
          <div className="mt-4 space-y-2">
            <button
              onClick={() => navigate('/')}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              Back to Home
            </button>
            <button
              onClick={() => window.location.reload()}
              className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600 ml-2"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Not connected state
  if (!isConnected) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-700">Connection Lost</h2>
          <p className="text-gray-600 mt-2">Unable to connect to game server</p>
          {error && (
            <p className="text-red-600 mt-2">{error}</p>
          )}
          <div className="mt-4 space-y-2">
            <button
              onClick={() => window.location.reload()}
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
            >
              Try Again
            </button>
            <button
              onClick={() => navigate('/')}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 ml-2"
            >
              Back to Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  // No game state - show setup
  if (!gameState) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center bg-white p-8 rounded-lg shadow-lg max-w-md">
          <h2 className="text-2xl font-semibold text-gray-700 mb-4">🎮 Ready to Play?</h2>
          <p className="text-gray-600 mb-6">No active game found. Create a new game to start playing!</p>
          <div className="space-y-3">
            <button
              onClick={() => gameService.createGame()}
              className="w-full bg-green-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-600"
            >
              🎯 Create New Game
            </button>
            <button
              onClick={() => navigate('/')}
              className="w-full bg-blue-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-600"
            >
              🏠 Back to Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Error Banner */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 relative">
          <span className="block sm:inline">{error}</span>
          <button
            className="absolute top-0 bottom-0 right-0 px-4 py-3"
            onClick={() => setError(null)}
          >
            <span className="text-xl">×</span>
          </button>
        </div>
      )}

      {/* Game Board */}
      <GameBoard
        gameState={gameState}
        currentPlayer={currentPlayer}
        onCardClick={handleCardClick}
        onGiveClue={handleGiveClue}
        onEndTurn={handleEndTurn}
        onStartGame={handleStartGame}
        onJoinTeam={handleJoinTeam}
      />
    </div>
  );
};

export default GamePage;