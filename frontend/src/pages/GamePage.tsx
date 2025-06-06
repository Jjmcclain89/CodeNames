import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { socketService } from '../services/socketService';
import { gameService } from '../services/gameService';
import GameBoard from '../components/GameBoard/GameBoard';

interface Player {
  id: string;
  username: string;
  team?: string;
  role?: string;
  isOnline?: boolean;
}

interface GameMessage {
  id: string;
  username: string;
  userId: string;
  text: string;
  timestamp: string;
}

const GamePage: React.FC = () => {
  const { gameCode } = useParams<{ gameCode: string }>();
  const navigate = useNavigate();
  const [connectionInitiated, setConnectionInitiated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [gameState, setGameState] = useState<any>(null);
  const [messages, setMessages] = useState<GameMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [teamActionInProgress, setTeamActionInProgress] = useState(false);
  const [reconnectionStatus, setReconnectionStatus] = useState<string | null>(null);

  useEffect(() => {
    if (!gameCode || connectionInitiated) {
      console.log('🔍 Skipping connection - already initiated or no game code');
      return;
    }
    
    console.log('🔌 Starting connection process for game:', gameCode);
    setConnectionInitiated(true);
    
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    setCurrentUser(user);
    loadGameAndConnect();
    
    // Cleanup on unmount
    return () => {
      console.log('🧹 Cleaning up connections');
      gameService.removeAllGameListeners();
      if (socketService.socket) {
        socketService.socket.off('player-joined-game');
        socketService.socket.off('new-game-message');
      }
      setConnectionInitiated(false);
    };
  }, [gameCode]);


  // ✅ Auto-rejoin team if we got disconnected and lost team assignment
  const checkAndAutoRejoinTeam = (gameState: any) => {
    if (!gameState || !gameCode) return;
    
    const currentPlayer = getCurrentUserPlayer();
    const storedAssignment = localStorage.getItem('lastTeamAssignment');
    
    if (storedAssignment) {
      try {
        const assignment = JSON.parse(storedAssignment);
        const isForThisGame = assignment.gameCode === gameCode.toUpperCase();
        const isRecent = (Date.now() - assignment.timestamp) < 30 * 60 * 1000; // 30 minutes
        
        if (isForThisGame && isRecent) {
          // Check if we're missing from our team or assigned as neutral
          const shouldBeOnTeam = assignment.team;
          const shouldBeRole = assignment.role;
          
          if (!currentPlayer || currentPlayer.team === 'neutral' || currentPlayer.team !== shouldBeOnTeam) {
            console.log('🔄 Detected team assignment loss - auto-rejoining...');
            console.log('🔄 Should be:', shouldBeOnTeam, shouldBeRole);
            console.log('🔄 Currently:', currentPlayer?.team || 'not found', currentPlayer?.role || 'not found');
            
            // Auto-rejoin the team
            setTimeout(() => {
              console.log('🔄 Auto-rejoining team:', shouldBeOnTeam, shouldBeRole);
              handleJoinTeam(shouldBeOnTeam, shouldBeRole);
            }, 1000);
          }
        }
      } catch (e) {
        console.error('Error parsing stored team assignment:', e);
      }
    }
  };

  const loadGameAndConnect = async () => {
    console.log('🏠 [GAMEPAGE] loadGameAndConnect called for game:', gameCode);
    
    if (!gameCode) {
      console.log('❌ [GAMEPAGE] No game code provided');
      setError('No game code provided');
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

      // STEP 1: Try to load existing game first (CORRECT APPROACH)
      console.log('🏠 [GAMEPAGE] Attempting to load existing game:', gameCode.toUpperCase());
      const gameInfoResponse = await fetch(`/api/games/${gameCode.toUpperCase()}`);
      
      if (gameInfoResponse.ok) {
        // Game exists - load it
        const gameData = await gameInfoResponse.json();
        console.log('🏠 [GAMEPAGE] Game exists - loading:', gameData);
        
        if (gameData.success) {
          // Check if user is already in the game
          const isUserInGame = gameData.game.players.some((p: any) => p.id === user.id);
          
          if (!isUserInGame) {
            // User not in game - try to join it
            console.log('🏠 [GAMEPAGE] User not in game - attempting to join');
            const joinResponse = await fetch('/api/games/join', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({ 
                gameCode: gameCode.toUpperCase(),
                userId: user.id,
                username: user.username
              })
            });

            if (!joinResponse.ok) {
              const joinData = await joinResponse.json();
              throw new Error(joinData.error || 'Failed to join game');
            }
            
            console.log('✅ [GAMEPAGE] Successfully joined existing game');
          } else {
            console.log('✅ [GAMEPAGE] User already in game - proceeding');
          }
          
          // Connect to socket and set up game
          await connectToGame(gameCode, token, user);
          console.log('✅ [GAMEPAGE] Game loaded and connected successfully');
          
        } else {
          throw new Error(gameData.error || 'Failed to load game information');
        }
        
      } else if (gameInfoResponse.status === 404) {
        // Game doesn't exist
        setError('Game not found - the game code may be invalid or expired');
        setIsLoading(false);
        return;
        
      } else {
        // Other error loading game
        throw new Error('Failed to load game information');
      }
      
    } catch (err: any) {
      console.error('❌ [GAMEPAGE] Error loading game:', err);
      setError(err.message || 'Unable to connect to game server');
      setIsLoading(false);
      return;
    }
    
    setIsLoading(false);
  };

  const connectToGame = async (gameCode: string, token: string, user: any) => {
    console.log('🔌 Connecting to game socket...', gameCode);
    
    if (isConnected && socketService.socket?.connected) {
      console.log('🔍 Already connected to socket, skipping connection');
      return Promise.resolve();
    }
    
    return new Promise<void>((resolve) => {
      if (!socketService.socket?.connected) {
        console.log('❌ No socket connection available');
        return;
      }

      const handleAuth = () => {
        console.log('✅ [GAMEPAGE] Socket authenticated, joining game:', gameCode);
        socketService.socket?.emit('join-game-room', gameCode);
        setIsConnected(true);
        
        setupGameListeners(user);
        resolve();
      };

      if (socketService.socket?.connected) {
        socketService.onAuthenticated((data: any) => {
          if (data.success) {
            handleAuth();
          }
        });
        
        socketService.authenticate(token);
        
        if (socketService.socket?.connected && !isConnected) {
          handleAuth();
        }
      }

      // Listen for game events
      socketService.socket?.on('player-joined-game', (data: any) => {
        console.log('👥 Player joined game:', data);
      });

      socketService.socket?.on('new-game-message', (message: GameMessage) => {
        console.log('💬 New game message:', message);
        setMessages(prev => [...prev, message]);
      });
    });
  };

  const setupGameListeners = (user: any) => {
    console.log('🎮 Setting up game listeners for:', user.username);
    
    gameService.removeAllGameListeners();
    
    gameService.onGameStateUpdated((newGameState: any) => {
      console.log('🎮 [GAMEPAGE] Game state updated:', newGameState);
      setGameState(newGameState);
      setIsLoading(false);
      
      // ✅ Auto-rejoin temporarily disabled
      // checkAndAutoRejoinTeam(newGameState);
    });

    gameService.onGameError((error: string) => {
      console.error('🎮 Game error:', error);
      setError(error);
      setTimeout(() => setError(''), 3000);
    });
    
    // ✅ Add specific game action listeners
    if (socketService.socket) {
      // Listen for clue given events
      socketService.socket.on('game:clue-given', (clue: any) => {
        console.log('💡 Clue given event received:', clue);
        // Game state should update automatically, but we can show a toast
      });
      
      // Listen for card revealed events
      socketService.socket.on('game:card-revealed', (card: any) => {
        console.log('🎯 Card revealed event received:', card);
        // Game state should update automatically
      });
      
      // Listen for turn changed events
      socketService.socket.on('game:turn-changed', (newTurn: string) => {
        console.log('⏭️ Turn changed event received:', newTurn);
        // Game state should update automatically
      });
      
      // Listen for game ended events
      socketService.socket.on('game:game-ended', (winner: string) => {
        console.log('🏆 Game ended event received, winner:', winner);
        // Could show a victory modal here
      });
    }
  };

  const sendMessage = () => {
    if (!newMessage.trim() || !isConnected || !gameCode) return;

    console.log('📤 Sending game message:', newMessage);
    socketService.socket?.emit('send-game-message', {
      gameCode: gameCode.toUpperCase(),
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

  // ✅ Simple, reliable team join function
  const handleJoinTeam = (team: string, role: string) => {
    console.log(`👥 Attempting to join ${team} team as ${role}`);
    
    // Basic checks
    if (teamActionInProgress) {
      console.log('⏳ Team action already in progress');
      return;
    }
    
    setTeamActionInProgress(true);
    setError('');
    
    try {
      // Store team assignment for potential recovery
      const teamAssignment = { team, role, gameCode: gameCode?.toUpperCase(), timestamp: Date.now() };
      localStorage.setItem('lastTeamAssignment', JSON.stringify(teamAssignment));
      console.log('💾 Stored team assignment:', teamAssignment);
      
      // Simple socket check and emit
      if (socketService && socketService.socket) {
        if (!socketService.socket.connected) {
          console.log('🔌 Socket not connected, trying to connect...');
          const token = localStorage.getItem('token');
          if (token) {
            socketService.connect();
            socketService.authenticate(token);
          }
        }
        
        // Emit the event regardless - let the backend handle it
        console.log('📡 Emitting game:join-team event');
        socketService.socket.emit('game:join-team', team, role);
        
      } else {
        throw new Error('Socket service not available');
      }
      
    } catch (error) {
      console.error('❌ Error in team join:', error);
      setError('Failed to join team - please refresh page');
    }
    
    // Reset action flag after a short delay
    const timeoutId = setTimeout(() => {
      setTeamActionInProgress(false);
      clearTimeout(timeoutId);
    }, 2000);
  };


  const handleStartGame = () => {
    console.log('🚀 Starting Codenames game...');
    if (!isConnected) {
      setError('Not connected to server');
      return;
    }
    gameService.startGame();
  };

  const canStartGame = () => {
    if (!gameState || !gameState.players) return false;
    
    const redPlayers = gameState.players.filter((p: any) => p.team === 'red');
    const bluePlayers = gameState.players.filter((p: any) => p.team === 'blue');
    
    return redPlayers.length > 0 && bluePlayers.length > 0;
  };

  const getCurrentUserPlayer = () => {
    if (!gameState || !gameState.players) return null;
    
    // ✅ Enhanced player matching with debug logging
    console.log('🔍 Finding current user player...');
    console.log('🔍 Current user:', currentUser);
    console.log('🔍 Game players:', gameState.players.map(p => ({ id: p.id, username: p.username })));
    
    // Try multiple matching strategies
    let player = null;
    
    // Strategy 1: Match by username (original)
    player = gameState.players.find((p: any) => p.username === currentUser?.username);
    if (player) {
      console.log('✅ Found player by username:', player.username);
      return player;
    }
    
    // Strategy 2: Match by user ID
    player = gameState.players.find((p: any) => p.id === currentUser?.id);
    if (player) {
      console.log('✅ Found player by user ID:', player.username);
      return player;
    }
    
    // Strategy 3: Check if there's only one real player (not test players)
    const realPlayers = gameState.players.filter((p: any) => !p.id.startsWith('test_'));
    if (realPlayers.length === 1) {
      console.log('✅ Found single real player:', realPlayers[0].username);
      return realPlayers[0];
    }
    
    console.log('❌ No matching player found');
    return null;
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
          <div className="text-xl text-gray-900 mb-4">Loading Codenames Game...</div>
          <div className="text-gray-600">Game Code: {gameCode}</div>
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
          <div className="text-red-600 text-xl mb-4">Game Error</div>
          <div className="text-gray-600 mb-6">
            <p>Game Code: <strong>{gameCode}</strong></p>
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

  // Show team assignment if game is waiting or in setup
  if (!gameState || gameState.status === 'waiting' || gameState.status === 'setup') {
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
                Players: <span className="font-semibold text-blue-600">{gameState?.players?.length || 0}</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Game Setup Area */}
            <div className="lg:col-span-2 space-y-6">
              <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
                <h1 className="text-3xl font-bold text-gray-900 mb-6">
                  Codenames Game: {gameCode}
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
                        Need players on both teams to start
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
                  👥 Players ({gameState?.players?.length || 0})
                </h3>
                <div className="space-y-2">
                  {gameState?.players?.length > 0 ? (
                    gameState.players.map((player: any) => (
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

              {/* Game Chat */}
              <div className="bg-white rounded-lg shadow border border-gray-200 p-4">
                <h3 className="font-semibold text-gray-900 mb-4">💬 Game Chat</h3>
                
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
              <p>Share this game code with friends: <span className="bg-blue-100 px-2 py-1 rounded font-mono font-bold">{gameCode}</span></p>
              <p className="text-sm mt-1">They can join by entering this code on the homepage!</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show actual game board if game is playing
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Codenames Game</h1>
            <div className="text-sm text-gray-600">
              Game: {gameCode} | Current Turn: {gameState.currentTurn} team
            </div>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={() => navigate('/')}
              className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded text-sm"
            >
              Back to Home
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6">
        {/* Game Status */}
        <div className="mb-6 bg-white rounded-lg shadow p-4">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Game Status</h2>
            <div className="text-sm text-gray-600">
              Status: <span className="font-semibold text-green-600">{gameState.status}</span>
            </div>
          </div>
          
          {/* Players */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-red-50 border border-red-200 rounded p-3">
              <h3 className="font-semibold text-red-700 mb-2">🔴 Red Team</h3>
              {gameState.players.filter((p: any) => p.team === 'red').map((player: any) => (
                <div key={player.id} className="text-sm">
                  {player.username} ({player.role})
                </div>
              ))}
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded p-3">
              <h3 className="font-semibold text-blue-700 mb-2">🔵 Blue Team</h3>
              {gameState.players.filter((p: any) => p.team === 'blue').map((player: any) => (
                <div key={player.id} className="text-sm">
                  {player.username} ({player.role})
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Game Board */}
        <div className="bg-white rounded-lg shadow p-6">
          {/* ✅ Clean Turn Indicator - Shows specific player's turn */}
          {(() => {
            const currentPlayer = getCurrentUserPlayer();
            const isMyTurn = currentPlayer && currentPlayer.team === gameState.currentTurn;
            const isSpymaster = currentPlayer && currentPlayer.role === 'spymaster';
            const canGiveClue = isMyTurn && isSpymaster && !gameState.currentClue;
            const canGuess = isMyTurn && !isSpymaster && gameState.currentClue && gameState.guessesRemaining > 0;
            
            // Find who should be acting right now
            let activePlayer = null;
            if (!gameState.currentClue) {
              // Need spymaster to give clue
              activePlayer = gameState.players.find(p => p.team === gameState.currentTurn && p.role === 'spymaster');
            } else if (gameState.guessesRemaining > 0) {
              // Operatives should be guessing - could be any operative on current team
              const operatives = gameState.players.filter(p => p.team === gameState.currentTurn && p.role === 'operative');
              activePlayer = operatives[0]; // For now, just show first operative
            }
            
            return (
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">Game Board</h2>
                <div className="text-sm text-gray-600">
                  {activePlayer ? (
                    <span>
                      <span className={`font-medium ${activePlayer.team === 'red' ? 'text-red-600' : 'text-blue-600'}`}>
                        {activePlayer.username}
                      </span>
                      <span className="text-gray-500 ml-1">
                        ({activePlayer.team} {activePlayer.role})
                      </span>
                      {isMyTurn && <span className="ml-2 text-blue-600 font-medium">← Your turn</span>}
                    </span>
                  ) : (
                    <span className="text-gray-500">Game in progress</span>
                  )}
                </div>
              </div>
            );
          })()}
          
          {/* ✅ Reconnection Status */}
          {reconnectionStatus && (
            <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg text-center">
              <div className="flex items-center justify-center space-x-2">
                <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                <span className="text-blue-700 font-medium">{reconnectionStatus}</span>
              </div>
            </div>
          )}
          
          {/* Current Clue Display */}
          {gameState.currentClue && (
            <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-center">
              <span className="text-lg font-semibold text-gray-700">💡 Current Clue: </span>
              <span className="text-2xl font-bold text-yellow-700">
                {gameState.currentClue.word} ({gameState.currentClue.number})
              </span>
            </div>
          )}
          
          {gameState.board && (
            <GameBoard 
              gameState={gameState} 
              currentPlayer={getCurrentUserPlayer()}
              onCardClick={(cardId) => {
                console.log('🎯 Card clicked:', cardId);
                if (!isConnected) {
                  setError('Not connected to server');
                  return;
                }
                // ✅ Emit socket event for card reveal
                console.log('🎯 Emitting game:reveal-card event');
                socketService.socket?.emit('game:reveal-card', cardId);
              }}
              onGiveClue={(word, number) => {
                console.log('💡 Clue given:', word, number);
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
                // ✅ Emit socket event for giving clue
                console.log('💡 Emitting game:give-clue event');
                socketService.socket?.emit('game:give-clue', { word: word.trim(), number });
              }}
              onEndTurn={() => {
                console.log('⏭️ End turn');
                if (!isConnected) {
                  setError('Not connected to server');
                  return;
                }
                // ✅ Emit socket event for ending turn
                console.log('⏭️ Emitting game:end-turn event');
                socketService.socket?.emit('game:end-turn');
              }}
              onStartGame={() => {
                console.log('🚀 Start game');
                handleStartGame();
              }}
              onJoinTeam={(team, role) => {
                console.log('👥 Join team:', team, role);
                handleJoinTeam(team, role);
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default GamePage;
