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

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    
    if (!token || !user) {
      navigate('/login');
      return;
    }

    // Initialize socket connection
    initializeSocket(token, JSON.parse(user));

    // Cleanup on unmount
    return () => {
      gameService.removeAllGameListeners();
    };
  }, [navigate]);

  const initializeSocket = (token: string, user: any) => {
    if (!socketService.isConnected) {
      socketService.connect();
    }

    // Set up socket event listeners
    socketService.onConnect(() => {
      // Make socket accessible for debugging
      (window as any).gamePageSocket = socketService.socket;
      console.log('🔗 Socket assigned to window.gamePageSocket');
      console.log('🔌 Connected to server');
      socketService.authenticate(token);
    });

    socketService.onAuthenticated((data) => {
        console.log('🔌 Socket connection debug info:');
        console.log('  - Socket service:', socketService);
        console.log('  - Socket object:', socketService.socket);
        console.log('  - Socket connected:', socketService.socket?.connected);
        console.log('  - Window assignment:', (window as any).socketService);

      if (data.success) {
        console.log('✅ Authenticated successfully');
        setIsConnected(true);        
        // Auto-join or create game for current room
        setTimeout(() => {
          // gameService.createGame(); // Commented out to prevent loops // This will join existing or create new
        }, 500);
        setError(null);
        
        // Create or join game automatically
        // gameService.createGame(); // Commented out to prevent loops
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

    // Set up game event listeners
    // Remove existing listeners first to prevent duplicates
        gameService.removeAllGameListeners();
        
        setupGameListeners(user);
  };

  const setupGameListeners = (user: any) => {
    gameService.onGameStateUpdated((game: CodenamesGame) => {
      console.log('🎮 Game state updated:', game);
      setGameState(game);
      
      // Find current player in the game
      const player = game.players.find(p => p.id === user.id);
      setCurrentPlayer(player || null);
    });

    gameService.onGameError((error: string) => {
      console.error('🎮 Game error:', error);
      setError(error);
      // Clear error after 5 seconds
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
  
    
    // Test players response
    socketService.socket?.on('game:test-players-added', (data) => {
      console.log('🎉 Test players added:', data);
      alert(`Success! Added ${data.playersAdded} test players`);
    });

    socketService.socket?.on('test-response', (data) => {
      console.log('🧪 Backend test response:', data);
      alert(`Backend responded: ${data.message}`);
    });};

  
  // Testing/Debug methods
  const handleTestMode = () => {
    // Automatically assign current user to blue operative
    handleJoinTeam('blue', 'operative');
    
    // Add test players via socket
    setTimeout(() => {
      socketService.socket?.emit('game:add-test-players');
    }, 100);
  };

  const handleForceStart = () => {
    // Force start game even without full teams
    gameService.startGame();
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

    const handleAddTestPlayers = () => {
    socketService.socket?.emit('game:add-test-players');
  };

  const handleJoinTeam = (team: any, role: any) => {
    gameService.joinTeam(team, role);
  };

  if (!isConnected) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-700">Connecting to game...</h2>
          {error && (
            <p className="text-red-600 mt-2">{error}</p>
          )}
        </div>
      </div>
    );
  }

  if (!gameState) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-pulse rounded-full h-32 w-32 bg-blue-200 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-700">Loading game...</h2>
          {error && (
            <p className="text-red-600 mt-2">{error}</p>
          )}
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
            <span className="text-xl">&times;</span>
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
