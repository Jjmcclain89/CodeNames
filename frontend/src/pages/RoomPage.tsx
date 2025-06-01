import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { socketService } from '../services/socketService';
import { gameService } from '../services/gameService';

interface Player {
  id: string;
  username: string;
  joinedAt: string;
  team?: string;
  role?: string;
}

interface RoomMessage {
  id: string;
  username: string;
  userId: string;
  text: string;
  timestamp: string;
}

interface GameInfo {
  code: string;
  id: string;
  status: string;
  playerCount: number;
  players: Player[];
  messages: RoomMessage[];
}

const RoomPage: React.FC = () => {
  const { roomCode } = useParams<{ roomCode: string }>();
  const navigate = useNavigate();
  const [connectionInitiated, setConnectionInitiated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [gameInfo, setGameInfo] = useState<GameInfo | null>(null);
  const [players, setPlayers] = useState<Player[]>([]);
  const [messages, setMessages] = useState<RoomMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [gameStarted, setGameStarted] = useState(false);
  const [gameState, setGameState] = useState<any>(null);

  useEffect(() => {
    if (!roomCode || connectionInitiated) {
      console.log('🔍 Skipping connection - already initiated or no room code');
      return;
    }
    
    console.log('🔌 Starting connection process for room:', roomCode);
    setConnectionInitiated(true);
    
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    setCurrentUser(user);
    loadGameAndConnect();
    
    // Cleanup on unmount
    return () => {
      console.log('🧹 Cleaning up connections');
      gameService.removeAllGameListeners();
      if (socketService.socket) {
        socketService.socket.off('player-joined-room');
        socketService.socket.off('room-state');
        socketService.socket.off('new-room-message');
      }
      setConnectionInitiated(false);
    };
  }, [roomCode]); // Only depend on roomCode

  const loadGameAndConnect = async () => {
    if (!roomCode) {
      setError('No room code provided');
      setIsLoading(false);
      return;
    }

    try {
      console.log('🎮 Loading game info for room:', roomCode);
      
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const token = localStorage.getItem('token');
      
      if (!user.username || !token) {
        setError('Please log in first');
        setIsLoading(false);
        return;
      }

      // Join the game via API
      const joinResponse = await fetch('/api/games/join', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          gameCode: roomCode.toUpperCase(),
          userId: user.id,
          username: user.username
        })
      });

      if (!joinResponse.ok) {
        throw new Error('Failed to join game');
      }

      // Get game info
      const response = await fetch(`/api/games/${roomCode}`);
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setGameInfo(data.game);
          setPlayers(data.game.players || []);
          setMessages(data.game.messages || []);
          
          // Connect to socket and set up game
          await connectToRoom(roomCode, token, user);
          console.log('✅ Game info loaded:', data.game);
        } else {
          throw new Error(data.error || 'Game not found');
        }
      } else if (response.status === 404) {
        setError('Game not found - the game code may be invalid or expired');
      } else {
        throw new Error('Failed to load game information');
      }
    } catch (err: any) {
      console.error('Error loading game:', err);
      setError(err.message || 'Unable to connect to game server');
    }
    
    setIsLoading(false);
  };

  const connectToRoom = async (gameCode: string, token: string, user: any) => {
    console.log('🔌 Connecting to room socket...', gameCode);
    
    // Check if already connected to this room
    if (isConnected && socketService.socket?.connected) {
      console.log('🔍 Already connected to socket, skipping connection');
      return Promise.resolve();
    }
    
    return new Promise<void>((resolve) => {
      // Use existing socket connection from App.tsx - DON'T create new one
      if (!socketService.socket?.connected) {
        console.log('❌ No socket connection available - App.tsx should have created it');
        return;
      } else {
        console.log('✅ Using existing socket connection from App.tsx');
      }

      const handleAuth = () => {
        console.log('✅ Socket authenticated, joining room:', gameCode);
        socketService.socket?.emit('join-game-room', gameCode);
        setIsConnected(true);
        
        // Set up game listeners after socket is ready
        setupGameListeners(user);
        
        // Create or join game in the backend (only once per connection)
        console.log('🎮 Creating/joining game for room:', gameCode);
        if (!gameState) {
          console.log('🎮 No existing game state, creating/joining game');
          gameService.createGame(); // This will create or join existing game
        } else {
          console.log('🎮 Game state already exists, skipping creation');
        }
        
        resolve();
      };

      if (socketService.socket?.connected) {
        socketService.authenticate(token);
        socketService.onAuthenticated((data: any) => {
          if (data.success) {
            handleAuth();
          }
        });
      } else {
        socketService.onConnect(() => {
          socketService.authenticate(token);
          socketService.onAuthenticated((data: any) => {
            if (data.success) {
              handleAuth();
            }
          });
        });
      }

      // Listen for room events
      socketService.socket?.on('player-joined-room', (data: any) => {
        console.log('👥 Player joined room:', data);
        setPlayers(prev => {
          if (!prev.find(p => p.username === data.player.username)) {
            return [...prev, {
              id: data.player.id,
              username: data.player.username,
              joinedAt: new Date().toISOString()
            }];
          }
          return prev;
        });
      });

      socketService.socket?.on('room-state', (data: any) => {
        console.log('🎯 Room state received:', data);
        setPlayers(data.players || []);
        setMessages(data.messages || []);
      });

      socketService.socket?.on('new-room-message', (message: RoomMessage) => {
        console.log('💬 New room message:', message);
        setMessages(prev => [...prev, message]);
      });
    });
  };

  const setupGameListeners = (user: any) => {
    console.log('🎮 Setting up game listeners for:', user.username);
    
    // Remove existing listeners first
    gameService.removeAllGameListeners();
    
    // Listen for game state updates
    gameService.onGameStateUpdated((newGameState: any) => {
      console.log('🎮 Game state updated in room:', newGameState);
      setGameState(newGameState);
      
      if (newGameState.status === 'playing') {
        setGameStarted(true);
      }
      
      // Update players with team/role info from game state
      if (newGameState.players) {
        console.log('👥 Updating players from game state:', newGameState.players);
        setPlayers(newGameState.players);
      }
    });

    gameService.onGameError((error: string) => {
      console.error('🎮 Game error:', error);
      setError(error);
      setTimeout(() => setError(''), 3000);
    });
  };

  const sendMessage = () => {
    if (!newMessage.trim() || !isConnected || !roomCode) return;

    console.log('📤 Sending room message:', newMessage);
    socketService.socket?.emit('send-room-message', {
      gameCode: roomCode.toUpperCase(),
      message: newMessage.trim()
    });

    setNewMessage('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleJoinTeam = (team: string, role: string) => {
    console.log(`👥 Attempting to join ${team} team as ${role}`);
    console.log('🔍 Current game state:', gameState);
    console.log('🔍 Socket connected:', socketService.socket?.connected);
    console.log('🔍 User:', currentUser);
    
    if (!isConnected) {
      console.error('❌ Socket not connected');
      setError('Not connected to server');
      return;
    }
    
    // Use the game service to join team
    gameService.joinTeam(team as any, role as any);
  };

  const handleStartGame = () => {
    console.log('🚀 Starting Codenames game...');
    if (!isConnected) {
      setError('Not connected to server');
      return;
    }
    gameService.startGame();
  };

  const handleGoToGame = () => {
    console.log('🎮 Navigating to game board...');
    navigate('/game');
  };

  const canStartGame = () => {
    if (!gameState || !gameState.players) return false;
    
    const redPlayers = gameState.players.filter((p: any) => p.team === 'red');
    const bluePlayers = gameState.players.filter((p: any) => p.team === 'blue');
    const redSpymaster = redPlayers.find((p: any) => p.role === 'spymaster');
    const blueSpymaster = bluePlayers.find((p: any) => p.role === 'spymaster');
    
    return redSpymaster && blueSpymaster && redPlayers.length >= 2 && bluePlayers.length >= 2;
  };

  const getCurrentUserPlayer = () => {
    if (!gameState || !gameState.players) return null;
    return gameState.players.find((p: any) => p.username === currentUser?.username);
  };

  const getTeamPlayers = (team: string) => {
    if (!gameState || !gameState.players) return [];
    return gameState.players.filter((p: any) => p.team === team);
  };

  const hasSpymaster = (team: string) => {
    const teamPlayers = getTeamPlayers(team);
    return teamPlayers.some((p: any) => p.role === 'spymaster');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-xl text-gray-900 mb-4">Loading game...</div>
          <div className="text-gray-600">Room Code: {roomCode}</div>
          <div className="mt-4">
            <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center bg-white p-8 rounded-lg shadow border border-gray-200 max-w-md">
          <div className="text-red-600 text-xl mb-4">Connection Error</div>
          <div className="text-gray-600 mb-6">
            <p>Room Code: <strong>{roomCode}</strong></p>
            <p className="mt-2 text-sm">{error}</p>
          </div>
          <div className="space-y-3">
            <button 
              onClick={() => navigate('/')}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded"
            >
              Go Back to Home
            </button>
            <button 
              onClick={() => window.location.reload()}
              className="w-full bg-gray-600 hover:bg-gray-700 text-white px-6 py-2 rounded"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (gameStarted) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center bg-white p-8 rounded-lg shadow border border-gray-200 max-w-md">
          <div className="text-green-600 text-xl mb-4">🎉 Game Started!</div>
          <div className="text-gray-600 mb-6">
            <p>The Codenames game has begun.</p>
            <p className="mt-2 text-sm">Click below to join the game board.</p>
          </div>
          <button 
            onClick={handleGoToGame}
            className="w-full bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded text-lg font-semibold"
          >
            🎮 Join Game Board
          </button>
        </div>
      </div>
    );
  }

  const userPlayer = getCurrentUserPlayer();

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto p-6">
        <div className="mb-6 flex justify-between items-center">
          <button 
            onClick={() => navigate('/')}
            className="text-blue-600 hover:text-blue-800 flex items-center"
          >
            ← Back to Home
          </button>
          <div className="flex items-center space-x-4 text-sm">
            <div className="text-gray-600">
              Status: <span className={`font-semibold ${isConnected ? 'text-green-600' : 'text-yellow-600'}`}>
                {isConnected ? 'Connected' : 'Connecting...'}
              </span>
            </div>
            <div className="text-gray-600">
              Players: <span className="font-semibold text-blue-600">{players.length}</span>
            </div>
          </div>
        </div>

        {/* Debug Info */}
        <div className="mb-4 bg-yellow-50 border border-yellow-200 rounded p-3 text-xs">
          <strong>🔍 Debug:</strong> Connected: {isConnected ? 'Yes' : 'No'} | 
          Game State: {gameState ? 'Loaded' : 'None'} | 
          Game Players: {gameState?.players?.length || 0} | 
          Room Players: {players.length} | 
          User: {currentUser?.username} | 
          Room: {roomCode}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Game Setup Area */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
              <h1 className="text-3xl font-bold text-gray-900 mb-6">
                Game Room: {roomCode}
              </h1>
              
              {/* Team Assignment Section */}
              <div className="space-y-6">
                <div className="text-center">
                  <h2 className="text-2xl font-semibold text-gray-900 mb-2">🕵️ Choose Your Team</h2>
                  <p className="text-gray-600">Select your team and role to get ready for the game!</p>
                </div>

                {/* Current User Status */}
                {userPlayer && (
                  <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
                    <p className="text-center text-blue-900">
                      You are: <span className="font-semibold">{userPlayer.username}</span>
                      {userPlayer.team && userPlayer.team !== 'neutral' && (
                        <span className={`ml-2 font-bold ${userPlayer.team === 'red' ? 'text-red-600' : 'text-blue-600'}`}>
                          • {userPlayer.team === 'red' ? '🔴' : '🔵'} {userPlayer.team} team 
                          ({userPlayer.role === 'spymaster' ? '👑 Spymaster' : '🕵️ Operative'})
                        </span>
                      )}
                    </p>
                  </div>
                )}

                {/* Team Selection Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Red Team */}
                  <div className="bg-red-50 border-2 border-red-200 rounded-lg p-6">
                    <h3 className="text-2xl font-semibold text-red-700 mb-4 text-center">
                      🔴 Red Team
                    </h3>
                    <div className="space-y-3 mb-4">
                      <button
                        onClick={() => handleJoinTeam('red', 'spymaster')}
                        className="w-full bg-red-500 text-white px-4 py-3 rounded-lg font-semibold hover:bg-red-600 transition-colors disabled:bg-gray-400"
                        disabled={hasSpymaster('red')}
                      >
                        {hasSpymaster('red') ? '👑 Spymaster Taken' : '👑 Join as Spymaster'}
                      </button>
                      <button
                        onClick={() => handleJoinTeam('red', 'operative')}
                        className="w-full bg-red-400 text-white px-4 py-3 rounded-lg font-semibold hover:bg-red-500 transition-colors"
                      >
                        🕵️ Join as Operative
                      </button>
                    </div>
                    <div className="text-sm text-gray-700">
                      <div className="font-medium mb-2">Team Members:</div>
                      {getTeamPlayers('red').length === 0 ? (
                        <p className="text-gray-500 italic">No players yet</p>
                      ) : (
                        getTeamPlayers('red').map((player: any) => (
                          <div key={player.id} className="flex justify-between items-center py-1">
                            <span>{player.username}</span>
                            <span className="text-red-600 font-medium">
                              {player.role === 'spymaster' ? '👑' : '🕵️'} {player.role}
                            </span>
                          </div>
                        ))
                      )}
                    </div>
                  </div>

                  {/* Blue Team */}
                  <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6">
                    <h3 className="text-2xl font-semibold text-blue-700 mb-4 text-center">
                      🔵 Blue Team
                    </h3>
                    <div className="space-y-3 mb-4">
                      <button
                        onClick={() => handleJoinTeam('blue', 'spymaster')}
                        className="w-full bg-blue-500 text-white px-4 py-3 rounded-lg font-semibold hover:bg-blue-600 transition-colors disabled:bg-gray-400"
                        disabled={hasSpymaster('blue')}
                      >
                        {hasSpymaster('blue') ? '👑 Spymaster Taken' : '👑 Join as Spymaster'}
                      </button>
                      <button
                        onClick={() => handleJoinTeam('blue', 'operative')}
                        className="w-full bg-blue-400 text-white px-4 py-3 rounded-lg font-semibold hover:bg-blue-500 transition-colors"
                      >
                        🕵️ Join as Operative
                      </button>
                    </div>
                    <div className="text-sm text-gray-700">
                      <div className="font-medium mb-2">Team Members:</div>
                      {getTeamPlayers('blue').length === 0 ? (
                        <p className="text-gray-500 italic">No players yet</p>
                      ) : (
                        getTeamPlayers('blue').map((player: any) => (
                          <div key={player.id} className="flex justify-between items-center py-1">
                            <span>{player.username}</span>
                            <span className="text-blue-600 font-medium">
                              {player.role === 'spymaster' ? '👑' : '🕵️'} {player.role}
                            </span>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </div>

                {/* Start Game Button */}
                <div className="text-center">
                  <button
                    onClick={handleStartGame}
                    disabled={!canStartGame()}
                    className="bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-colors"
                  >
                    {canStartGame() ? '🚀 Start Codenames Game' : '⏳ Waiting for Teams'}
                  </button>
                  {!canStartGame() && (
                    <p className="text-sm text-gray-600 mt-2">
                      Need: Both teams with spymasters and at least 2 players each
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar - Players and Chat */}
          <div className="space-y-6">
            {/* Players List */}
            <div className="bg-white rounded-lg shadow border border-gray-200 p-4">
              <h3 className="font-semibold text-gray-900 mb-4">
                👥 Players ({gameState?.players?.length || players.length})
              </h3>
              <div className="space-y-2">
                {(gameState?.players || players).length > 0 ? (
                  (gameState?.players || players).map((player: any) => (
                    <div key={player.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <div>
                        <div className="font-medium text-gray-900 flex items-center">
                          {player.username}
                          {player.team && player.team !== 'neutral' && (
                            <span className={`ml-2 text-xs px-2 py-1 rounded ${player.team === 'red' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'}`}>
                              {player.team === 'red' ? '🔴' : '🔵'} {player.role === 'spymaster' ? '👑' : '🕵️'}
                            </span>
                          )}
                        </div>
                        <div className="text-xs text-gray-500">
                          {player.joinedAt ? `Joined ${new Date(player.joinedAt).toLocaleTimeString()}` : 'In game'}
                        </div>
                      </div>
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    </div>
                  ))
                ) : (
                  <div className="text-gray-500 text-sm text-center py-4">
                    No players yet
                  </div>
                )}
              </div>
            </div>

            {/* Room Chat */}
            <div className="bg-white rounded-lg shadow border border-gray-200 p-4">
              <h3 className="font-semibold text-gray-900 mb-4">💬 Room Chat</h3>
              
              <div className="h-64 overflow-y-auto border border-gray-200 rounded p-2 mb-4 bg-gray-50">
                {messages.length > 0 ? (
                  messages.map((message) => (
                    <div key={message.id} className="mb-2 text-sm">
                      <span className="font-medium text-blue-600">{message.username}:</span>
                      <span className="text-gray-800 ml-1">{message.text}</span>
                      <div className="text-xs text-gray-500">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-gray-500 text-center py-8">
                    No messages yet. Start the conversation!
                  </div>
                )}
              </div>

              <div className="flex space-x-2">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={isConnected ? "Type a message..." : "Connecting..."}
                  disabled={!isConnected}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                />
                <button
                  onClick={sendMessage}
                  disabled={!newMessage.trim() || !isConnected}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white px-4 py-2 rounded text-sm"
                >
                  Send
                </button>
              </div>
            </div>
          </div>
        </div>
        
        {/* Invite Section */}
        <div className="mt-6 bg-blue-50 border border-blue-200 p-4 rounded-lg">
          <h3 className="font-semibold text-blue-900 mb-2">📱 Invite Friends</h3>
          <div className="text-blue-800">
            <p>Share this game code with friends: <span className="bg-blue-100 px-2 py-1 rounded font-mono font-bold">{roomCode}</span></p>
            <p className="text-sm mt-1">They can join by entering this code on the homepage!</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RoomPage;