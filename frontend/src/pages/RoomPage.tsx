import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { socketService } from '../services/socketService';

interface Player {
  id: string;
  username: string;
  team?: string;
  role?: string;
  isOnline?: boolean;
}

interface RoomMessage {
  id: string;
  username: string;
  userId: string;
  text: string;
  timestamp: string;
}

const RoomPage: React.FC = () => {
  const { roomId } = useParams<{ roomId: string }>();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [roomState, setRoomState] = useState<any>(null);
  const [players, setPlayers] = useState<Player[]>([]);
  const [messages, setMessages] = useState<RoomMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    if (!roomId) return;
    
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    setCurrentUser(user);
    loadRoomAndConnect();
    
    return () => {
      if (socketService.socket) {
        socketService.socket.off('player-joined-room');
        socketService.socket.off('player-left-room');
        socketService.socket.off('new-room-message');
        socketService.socket.off('room-updated');
        socketService.socket.off('game-created');
      }
    };
  }, [roomId]);

  const loadRoomAndConnect = async () => {
    if (!roomId) {
      setError('No room ID provided');
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

      // Load room info
      const roomResponse = await fetch(`/api/rooms/${roomId.toUpperCase()}`);
      
      if (roomResponse.ok) {
        const roomData = await roomResponse.json();
        if (roomData.success) {
          setRoomState(roomData.room);
          setPlayers(roomData.room.players || []);
        }
      } else if (roomResponse.status === 404) {
        setError('Room not found - the room code may be invalid or expired');
        setIsLoading(false);
        return;
      }

      // Connect to socket and join room
      await connectToRoom(roomId, token, user);
      setIsLoading(false);
      
    } catch (err: any) {
      console.error('❌ Error loading room:', err);
      setError(err.message || 'Unable to connect to room');
      setIsLoading(false);
    }
  };

  const connectToRoom = async (roomId: string, token: string, user: any) => {
    if (isConnected && socketService.socket?.connected) {
      return Promise.resolve();
    }
    
    return new Promise<void>((resolve) => {
      if (!socketService.socket?.connected) {
        console.log('❌ No socket connection available');
        return;
      }

      const handleAuth = () => {
        socketService.socket?.emit('join-room', roomId);
        setIsConnected(true);
        setupRoomListeners();
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

  const setupRoomListeners = () => {
    if (!socketService.socket) return;

    // Player events
    socketService.socket.on('player-joined-room', (data: any) => {
      console.log('👥 Player joined room:', data);
      setPlayers(prev => [...prev.filter(p => p.id !== data.player.id), data.player]);
    });

    socketService.socket.on('player-left-room', (data: any) => {
      console.log('👥 Player left room:', data);
      setPlayers(prev => prev.filter(p => p.id !== data.player.id));
    });

    // Room updates
    socketService.socket.on('room-updated', (roomData: any) => {
      console.log('🏠 Room updated:', roomData);
      console.log('🏠 Updated room players:', roomData.players?.length || 0);
      setRoomState(roomData);
      setPlayers(roomData.players || []);
      
      // Log team assignments for debugging
      if (roomData.players) {
        roomData.players.forEach((p: any, i: number) => {
          console.log(`  ${i+1}. ${p.username} - ${p.team}/${p.role}`);
        });
      }
    });

    // Chat
    socketService.socket.on('new-room-message', (message: RoomMessage) => {
      setMessages(prev => [...prev, message]);
    });

    // Game creation
    socketService.socket.on('game-created', (data: any) => {
      console.log('🎮 Game created, navigating to:', data.gameId);
      navigate(`/game/${data.gameId}`);
    });
  };

  const handleJoinTeam = (team: string, role: string) => {
    if (!isConnected) {
      setError('Not connected to server');
      return;
    }

    socketService.socket?.emit('room:join-team', {
      roomId: roomId?.toUpperCase(),
      team,
      role
    });
  };

  const handleStartGame = async () => {
    if (!canStartGame()) {
      setError('Need players on both teams to start');
      return;
    }

    setIsCreating(true);
    setError('');

    try {
      if (!isConnected) {
        setError('Not connected to server');
        return;
      }

      // Emit start game event - backend will create game and navigate all players
      socketService.socket?.emit('room:start-game', {
        roomId: roomId?.toUpperCase()
      });

    } catch (err: any) {
      console.error('❌ Error starting game:', err);
      setError(err.message || 'Failed to start game');
    } finally {
      setIsCreating(false);
    }
  };

  const canStartGame = () => {
    if (!players) return false;
    
    const redPlayers = players.filter(p => p.team === 'red');
    const bluePlayers = players.filter(p => p.team === 'blue');
    
    return redPlayers.length > 0 && bluePlayers.length > 0;
  };

  const getCurrentUserPlayer = () => {
    return players.find(p => p.username === currentUser?.username || p.id === currentUser?.id);
  };

  const getTeamPlayers = (team: string) => {
    return players.filter(p => p.team === team);
  };

  const hasSpymaster = (team: string) => {
    return getTeamPlayers(team).some(p => p.role === 'spymaster');
  };

  const sendMessage = () => {
    if (!newMessage.trim() || !isConnected || !roomId) return;

    socketService.socket?.emit('send-room-message', {
      roomId: roomId.toUpperCase(),
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

  // Loading State
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center">
        <div className="text-center bg-white p-8 rounded-2xl shadow-xl">
          <div className="text-2xl font-bold text-gray-900 mb-4">🏠 Loading Room...</div>
          <div className="text-gray-600 mb-6">Room: <span className="font-mono bg-gray-100 px-2 py-1 rounded">{roomId}</span></div>
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
          <div className="text-red-600 text-2xl font-bold mb-4">🚨 Room Error</div>
          <div className="text-gray-600 mb-6">
            <p>Room: <span className="font-mono bg-gray-100 px-2 py-1 rounded font-bold">{roomId}</span></p>
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

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Room Setup Area */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
              <h1 className="text-3xl font-bold text-gray-900 mb-6">
                🏠 Room: {roomId}
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
                    disabled={!canStartGame() || isCreating}
                    className="bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-colors"
                  >
                    {isCreating ? (
                      <span className="flex items-center justify-center">
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                        Creating Game...
                      </span>
                    ) : canStartGame() ? (
                      '🚀 Start Codenames Game'
                    ) : (
                      '⏳ Waiting for Teams'
                    )}
                  </button>
                  {!canStartGame() && !isCreating && (
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
                👥 Players ({players.length})
              </h3>
              <div className="space-y-2">
                {players.length > 0 ? (
                  players.map((player: any) => (
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
            <p>Share this room code with friends: <span className="bg-blue-100 px-2 py-1 rounded font-mono font-bold">{roomId}</span></p>
            <p className="text-sm mt-1">They can join by entering this code on the homepage!</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RoomPage;