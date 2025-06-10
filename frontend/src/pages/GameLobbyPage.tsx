import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { socketService } from '../services/socketService';
import { LobbyChat, TeamSetup } from '../components/GameLobby';

interface Player {
  id: string;
  username: string;
  isOnline: boolean;
  socketId: string;
}

interface GameLobbyMessage {
  id: string;
  username: string;
  userId: string;
  text: string;
  timestamp: string;
}

const GameLobbyPage: React.FC = () => {
  const { lobbyId } = useParams<{ lobbyId: string }>();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [lobbyState, setLobbyState] = useState<any>(null);
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [messages, setMessages] = useState<GameLobbyMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    if (!lobbyId) return;
    
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    setCurrentUser(user);
    loadLobbyAndConnect();
    
    return () => {
      if (socketService.socket) {
        socketService.socket.off('player-joined-lobby');
        socketService.socket.off('player-left-lobby');
        socketService.socket.off('new-lobby-message');
        socketService.socket.off('lobby-updated');
        socketService.socket.off('game-created');
        socketService.socket.off('game-started');
      }
    };
  }, [lobbyId]);

  const loadLobbyAndConnect = async () => {
    if (!lobbyId) {
      setError('No lobby ID provided');
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

      // Load lobby info
      const lobbyResponse = await fetch(`/api/gamelobbies/${lobbyId.toUpperCase()}`);
      
      if (lobbyResponse.ok) {
        const lobbyData = await lobbyResponse.json();
        if (lobbyData.success) {
          setLobbyState(lobbyData.gameLobby);
          setGameState(lobbyData.gameLobby);
        }
      } else if (lobbyResponse.status === 404) {
        setError('Game lobby not found - the lobby code may be invalid or expired');
        setIsLoading(false);
        return;
      }

      // Connect to socket and join lobby
      await connectToLobby(lobbyId, token, user);
      setIsLoading(false);
      
    } catch (err: any) {
      console.error('❌ Error loading game lobby:', err);
      setError(err.message || 'Unable to connect to game lobby');
      setIsLoading(false);
    }
  };

  const connectToLobby = async (lobbyId: string, token: string, user: any) => {
    if (isConnected && socketService.socket?.connected) {
      return Promise.resolve();
    }
    
    return new Promise<void>((resolve) => {
      if (!socketService.socket?.connected) {
        console.log('❌ No socket connection available');
        return;
      }

      const handleAuth = () => {
        socketService.socket?.emit('join-lobby', lobbyId);
        setIsConnected(true);
        setupLobbyListeners();
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

  const setupLobbyListeners = () => {
    if (!socketService.socket) return;

    // Player events
    socketService.socket.on('player-joined-lobby', (data: any) => {
      console.log('👥 Player joined lobby:', data);
      // Player join/leave events will be handled by lobby-updated event
      // No need to manually update gameState here
    });

    socketService.socket.on('player-left-lobby', (data: any) => {
      console.log('👥 Player left lobby:', data);
      // Player join/leave events will be handled by lobby-updated event
      // No need to manually update gameState here
    });

    // Lobby updates
    socketService.socket.on('lobby-updated', (lobbyData: any) => {
      console.log('🎮 Lobby updated:', lobbyData);
      console.log('🎮 Updated lobby:', lobbyData);
      setLobbyState(lobbyData);
      setGameState(lobbyData);
      
      // Log team assignments for debugging
      if (lobbyData.redTeam || lobbyData.blueTeam) {
        console.log('Red team:', lobbyData.redTeam ? {
          spymaster: lobbyData.redTeam.spymaster?.username,
          operatives: lobbyData.redTeam.operatives?.map((p: any) => p.username)
        } : 'empty');
        console.log('Blue team:', lobbyData.blueTeam ? {
          spymaster: lobbyData.blueTeam.spymaster?.username,
          operatives: lobbyData.blueTeam.operatives?.map((p: any) => p.username)
        } : 'empty');
      }
    });

    // Chat
    socketService.socket.on('new-lobby-message', (message: GameLobbyMessage) => {
      setMessages(prev => [...prev, message]);
    });

    // Game creation
    socketService.socket.on('game-created', (data: any) => {
      console.log('🎮 Game created, navigating to:', data.gameId);
      navigate(`/game/${data.gameId}`);
    });
    // Game started (redirect from backend)
    socketService.socket.on('game-started', (data: any) => {
      console.log('🎮 Game started, redirecting to:', data.redirectTo);
      navigate(data.redirectTo);
    });
  };

  const handleJoinTeam = (team: string, role: string) => {
    if (!isConnected) {
      setError('Not connected to server');
      return;
    }

    socketService.socket?.emit('lobby:join-team', {
      lobbyId: lobbyId?.toUpperCase(),
      team,
      role
    });
  };

  const handleSimpleTest = () => {
    console.log('🧪 Frontend: Sending SIMPLE_TEST event');
    socketService.socket?.emit('SIMPLE_TEST', {});
    
    setTimeout(() => {
      console.log('🧪 Frontend: Sending lobby:leave-team event');
      socketService.socket?.emit('lobby:leave-team', {
        lobbyId: lobbyId?.toUpperCase(),
        team: 'red',
        role: 'operative'
      });
    }, 1000);
  };

  const handleLeaveTeam = (team: string, role: string) => {
    console.log(`🚪 Leaving ${team} team as ${role}`);
    
    if (!isConnected) {
      setError('Not connected to server');
      return;
    }

    socketService.socket?.emit('lobby:leave-team', {
      lobbyId: lobbyId?.toUpperCase(),
      team,
      role
    });
    
    console.log(`📤 Sent leave team event for ${team}/${role}`);
  };

  const handleStartGame = async () => {
    // Check ownership first
    if (!isLobbyOwner()) {
      setError('Only the lobby owner can start the game');
      return;
    }

    if (!canStartGame()) {
      setError('Need at least one valid team (spymaster + operatives) and no invalid teams');
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
      socketService.socket?.emit('lobby:start-game', {
        lobbyId: lobbyId?.toUpperCase()
      });

    } catch (err: any) {
      console.error('❌ Error starting game:', err);
      setError(err.message || 'Failed to start game');
    } finally {
      setIsCreating(false);
    }
  };

  const canStartGame = () => {
    if (!gameState) return false;
    
    // Check if at least one team is valid (has spymaster + operatives)
    const redTeamValid = gameState.redTeam && 
                        gameState.redTeam.spymaster && 
                        gameState.redTeam.operatives.length > 0;
                        
    const blueTeamValid = gameState.blueTeam && 
                         gameState.blueTeam.spymaster && 
                         gameState.blueTeam.operatives.length > 0;
    
    // Rule 1: At least one team must be valid
    const hasValidTeam = redTeamValid || blueTeamValid;
    
    // Rule 2: No teams can be invalid (if team exists, it must be valid)
    // A team exists if it has a spymaster or operatives
    const redTeamExists = gameState.redTeam && 
                         (gameState.redTeam.spymaster || gameState.redTeam.operatives.length > 0);
    const blueTeamExists = gameState.blueTeam && 
                          (gameState.blueTeam.spymaster || gameState.blueTeam.operatives.length > 0);
    
    const redTeamInvalid = redTeamExists && !redTeamValid;
    const blueTeamInvalid = blueTeamExists && !blueTeamValid;
    const hasInvalidTeam = redTeamInvalid || blueTeamInvalid;
    
    return hasValidTeam && !hasInvalidTeam;
  };
  const isLobbyOwner = () => {
    if (!currentUser || !lobbyState) return false;
    return currentUser.id === lobbyState.owner;
  };

  const getOwnerUsername = () => {
    if (!lobbyState) return 'Owner';
    
    // Try to find owner username from current players in the lobby
    const allPlayers = [
      ...(lobbyState.redTeam ? [lobbyState.redTeam.spymaster, ...lobbyState.redTeam.operatives] : []),
      ...(lobbyState.blueTeam ? [lobbyState.blueTeam.spymaster, ...lobbyState.blueTeam.operatives] : [])
    ].filter(Boolean);
    
    const owner = allPlayers.find(player => player && player.id === lobbyState.owner);
    return owner ? owner.username : 'Owner';
  };

  const sendMessage = () => {
    if (!newMessage.trim() || !isConnected || !lobbyId) return;

    socketService.socket?.emit('send-lobby-message', {
      lobbyId: lobbyId.toUpperCase(),
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

  // Loading State - Dark Theme
  if (isLoading) {
    return (
      <div className="pt-16 min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-900 flex items-center justify-center relative">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-blue-400 via-transparent to-transparent"></div>
          <div className="absolute inset-0 bg-[linear-gradient(45deg,_transparent_25%,_rgba(255,255,255,0.02)_25%,_rgba(255,255,255,0.02)_50%,_transparent_50%,_transparent_75%,_rgba(255,255,255,0.02)_75%)] bg-[length:60px_60px]"></div>
        </div>
        
        <div className="text-center bg-gradient-to-br from-slate-800/90 to-slate-900/90 p-8 rounded-2xl shadow-2xl border border-slate-600/50 backdrop-blur-lg max-w-md mx-4">
          <div className="text-2xl font-bold text-slate-100 mb-4">🎮 Loading Game Lobby...</div>
          <div className="text-slate-300 mb-6">
            Lobby: <span className="font-mono bg-slate-700/50 px-2 py-1 rounded text-amber-300">{lobbyId}</span>
          </div>
          <div className="flex justify-center">
            <div className="w-12 h-12 border-4 border-slate-600 border-t-blue-500 rounded-full animate-spin"></div>
          </div>
        </div>
      </div>
    );
  }

  // Error State - Dark Theme
  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-900 flex items-center justify-center relative">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-blue-400 via-transparent to-transparent"></div>
          <div className="absolute inset-0 bg-[linear-gradient(45deg,_transparent_25%,_rgba(255,255,255,0.02)_25%,_rgba(255,255,255,0.02)_50%,_transparent_50%,_transparent_75%,_rgba(255,255,255,0.02)_75%)] bg-[length:60px_60px]"></div>
        </div>
        
        <div className="text-center bg-gradient-to-br from-slate-800/90 to-slate-900/90 p-8 rounded-2xl shadow-2xl border border-slate-600/50 backdrop-blur-lg max-w-md mx-4">
          <div className="text-red-400 text-2xl font-bold mb-4">🚨 Lobby Error</div>
          <div className="text-slate-300 mb-6">
            <p>Lobby: <span className="font-mono bg-slate-700/50 px-2 py-1 rounded font-bold text-amber-300">{lobbyId}</span></p>
            <p className="mt-3 p-3 bg-red-900/30 border border-red-500/50 rounded-lg text-sm text-red-200">{error}</p>
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
              className="w-full bg-gradient-to-r from-slate-600 to-slate-700 hover:from-slate-700 hover:to-slate-800 text-white px-6 py-3 rounded-lg font-semibold transition-all duration-200 shadow-lg"
            >
              🔄 Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-900 relative">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-blue-400 via-transparent to-transparent"></div>
        <div className="absolute inset-0 bg-[linear-gradient(45deg,_transparent_25%,_rgba(255,255,255,0.02)_25%,_rgba(255,255,255,0.02)_50%,_transparent_50%,_transparent_75%,_rgba(255,255,255,0.02)_75%)] bg-[length:60px_60px]"></div>
      </div>

      <div className="relative z-10 max-w-6xl mx-auto p-6">
        {/* Header Section */}
        <div className="mb-6 text-center">
          <div className="flex justify-center items-center space-x-6 text-sm">
            <div className="text-slate-300">
              Game: <span className="font-semibold text-white">
                {lobbyId}
              </span>
            </div>
            <div className="text-slate-300">
              Status: <span className={`font-semibold ${isConnected ? 'text-emerald-400' : 'text-amber-400'}`}>
                {isConnected ? 'Connected' : 'Connecting...'}
              </span>
            </div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-900/30 border border-red-500/50 rounded-lg backdrop-blur-sm">
            <p className="text-red-200">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Lobby Setup Area */}
          <div className="lg:col-span-2 space-y-6">
            <TeamSetup
              lobbyId={lobbyId || ''}
              gameState={gameState}
              currentUser={currentUser}
              isConnected={isConnected}
              isCreating={isCreating}
              isLobbyOwner={isLobbyOwner()}
              onJoinTeam={handleJoinTeam}
              onLeaveTeam={handleLeaveTeam}
              onStartGame={handleStartGame}
              canStartGame={canStartGame}
              ownerUsername={getOwnerUsername()}
            />
          </div>

          {/* Sidebar - Chat and Players */}
          <div>
            <LobbyChat
              players={gameState ? [
                ...(gameState.redTeam ? [gameState.redTeam.spymaster, ...gameState.redTeam.operatives] : []),
                ...(gameState.blueTeam ? [gameState.blueTeam.spymaster, ...gameState.blueTeam.operatives] : [])
              ] : []}
              messages={messages}
              newMessage={newMessage}
              setNewMessage={setNewMessage}
              isConnected={isConnected}
              onSendMessage={sendMessage}
              onKeyPress={handleKeyPress}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default GameLobbyPage;