import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface RoomListItem {
  code: string;
  id: string;
  status: string;
  playerCount: number;
  players: string[];
  createdAt: string;
  lastActivity: string;
}

interface GameLobbyProps {
  className?: string;
}

const GameLobby: React.FC<GameLobbyProps> = ({ className = '' }) => {
  // Game lobby state
  const [roomCode, setRoomCode] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [isJoining, setIsJoining] = useState(false);
  const [error, setError] = useState('');
  const [rooms, setRooms] = useState<RoomListItem[]>([]);
  const [isLoadingRooms, setIsLoadingRooms] = useState(false);
  const navigate = useNavigate();

  // Load games list on component mount and refresh periodically
  useEffect(() => {
    loadRoomsList();
    
    // Refresh rooms list every 10 seconds
    const interval = setInterval(loadRoomsList, 10000);
    
    return () => clearInterval(interval);
  }, []);

  const loadRoomsList = async () => {
    setIsLoadingRooms(true);
    try {
      console.log('📋 Loading rooms list...');
      const response = await fetch('/api/rooms');
      const data = await response.json();
      
      if (data.success) {
        setRooms(data.rooms || []);
        console.log(`✅ Loaded ${data.rooms?.length || 0} rooms`);
      } else {
        console.error('Failed to load rooms list:', data.error);
      }
    } catch (err) {
      console.error('Error loading rooms list:', err);
    }
    setIsLoadingRooms(false);
  };

  // Better error handling function
  const handleApiResponse = async (response: Response) => {
    const contentType = response.headers.get('content-type');
    
    if (!response.ok) {
      if (!contentType?.includes('application/json')) {
        const text = await response.text();
        throw new Error(`HTTP ${response.status}: Server returned HTML instead of JSON. Check if backend is running and proxy is configured.`);
      }
    }
    
    if (contentType?.includes('application/json')) {
      return await response.json();
    } else {
      const text = await response.text();
      throw new Error(`Expected JSON but got: ${contentType}. Response: ${text.substring(0, 100)}...`);
    }
  };

  const handleCreateRoom = async () => {
    setIsCreating(true);
    setError('');
    
    try {
      console.log('🎮 Creating game...');
      
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      
      const response = await fetch('/api/rooms/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          userId: user.id || `user_${Date.now()}`,
          username: user.username || 'Anonymous',
          debug: true 
        })
      });

      const data = await handleApiResponse(response);
      
      if (data.success && data.roomCode) {
        console.log('🎉 Navigating to room:', data.roomCode);
        // Refresh games list before navigating
        loadRoomsList();
        navigate(`/room/${data.roomCode}`);
      } else {
        setError(data.error || 'Failed to create game');
      }
    } catch (err: any) {
      console.error('💥 Error creating game:', err);
      setError(err.message);
    }
    
    setIsCreating(false);
  };

  const handleJoinRoom = async () => {
    if (!roomCode.trim()) {
      setError('Please enter a room code');
      return;
    }
    
    setIsJoining(true);
    setError('');

    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      
      const response = await fetch('/api/rooms/join', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          roomCode: roomCode.trim().toUpperCase(),
          userId: user.id || `user_${Date.now()}`,
          username: user.username || 'Anonymous'
        })
      });

      const data = await handleApiResponse(response);
      
      if (data.success && data.roomCode) {
        console.log('🎉 Navigating to room:', data.roomCode);
        navigate(`/room/${data.roomCode}`);
      } else {
        setError(data.error || 'Failed to join game');
      }
    } catch (err: any) {
      console.error('💥 Error joining game:', err);
      setError(err.message);
    }
    
    setIsJoining(false);
  };

  const handleJoinGameFromList = async (gameCode: string) => {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      
      const response = await fetch('/api/rooms/join', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          roomCode: gameCode,
          userId: user.id || `user_${Date.now()}`,
          username: user.username || 'Anonymous'
        })
      });

      const data = await handleApiResponse(response);
      
      if (data.success) {
        
        
        navigate(`/room/${gameCode}`);
        
      } else {
        setError(data.error || 'Failed to join game');
      }
    } catch (err: any) {
      console.error('💥 Error joining game from list:', err);
      setError(err.message);
    }
  };

  const handleRoomCodeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setRoomCode(e.target.value.toUpperCase());
    if (error) setError('');
  };

  const getTimeAgo = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now.getTime() - time.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };

  return (
    <div className={`${className}`}>
      <div className="bg-gradient-to-br from-slate-800/90 to-slate-900/90 rounded-2xl shadow-2xl border border-slate-600/50 p-8 backdrop-blur-lg">

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-900/50 border border-red-500/50 rounded-lg">
            <p className="text-red-200">{error}</p>
          </div>
        )}

        {/* Active Rooms List - Main Focus */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-semibold text-slate-100 flex items-center">
              <span className="text-2xl mr-3">🎯</span>
              Active Rooms
            </h3>
            <button 
              onClick={loadRoomsList}
              disabled={isLoadingRooms}
              className="text-blue-400 hover:text-blue-300 font-medium flex items-center space-x-2 transition-colors duration-200"
            >
              <span>{isLoadingRooms ? '🔄 Loading...' : '🔄 Refresh'}</span>
            </button>
          </div>
          
          {/* Games List Container */}
          <div className="p-6 min-h-[300px]">
            {rooms.length > 0 ? (
              <div className="space-y-4">
                {rooms.map((room) => (
                  <div key={room.code} className="flex items-center justify-between p-4 hover:bg-slate-700/20 transition-all duration-200 rounded-lg group">
                    <div className="flex-1">
                      <div className="flex items-center space-x-6">
                        <div className="bg-gradient-to-r from-violet-600 to-indigo-600 text-white px-3 py-2 rounded-lg font-mono font-bold text-lg shadow-lg">
                          {room.code}
                        </div>
                        <div className="text-slate-300">
                          <div className="flex items-center space-x-4 mb-1">
                            <span className="font-semibold text-slate-200">{room.playerCount} player{room.playerCount !== 1 ? 's' : ''}</span>
                            <span className="text-sm text-slate-400">•</span>
                            <span className="text-sm">{getTimeAgo(room.lastActivity)}</span>
                            <span className="text-sm text-slate-400">•</span>
                            <span className="text-emerald-400 capitalize font-medium">{room.status}</span>
                          </div>
                          {room.players.length > 0 && (
                            <div className="text-sm text-slate-400">
                              <span className="font-medium">Players:</span> {room.players.join(', ')}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => handleJoinGameFromList(room.code)}
                      className="bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800 text-white px-6 py-2 rounded-lg font-semibold transition-all duration-200 shadow-lg hover:shadow-emerald-500/25"
                    >
                      Join Room
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-20 text-slate-400">
                <div className="text-5xl mb-4">🎮</div>
                <p className="text-lg font-semibold text-slate-300">No active rooms</p>
                <p className="text-slate-400 mt-2">Create the first room to get started!</p>
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions - Create & Join */}
        <div className="border-t border-slate-600/30 pt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Join with Code - Left Side */}
          <div className="p-6 hover:bg-slate-700/10 transition-all duration-200 rounded-xl">
            <h4 className="text-lg font-semibold text-slate-100 mb-4 flex items-center">
              <span className="text-xl mr-2">🚪</span>
              Join with Code
            </h4>
            <div className="space-y-3">
              <input
                type="text"
                value={roomCode}
                onChange={handleRoomCodeChange}
                className="w-full px-3 py-2 bg-slate-700/60 border border-slate-500/50 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-slate-100 backdrop-blur-sm uppercase text-center font-mono placeholder-slate-400"
                placeholder="ABCD12"
                maxLength={6}
                disabled={isJoining}
              />
              <button 
                onClick={handleJoinRoom}
                disabled={isJoining || !roomCode.trim()}
                className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-slate-600 disabled:to-slate-700 text-white py-2 px-4 rounded-lg font-semibold transition-all duration-200 shadow-lg hover:shadow-blue-500/25"
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

          {/* Create New Room - Right Side */}
          <div className="p-6 hover:bg-slate-700/10 transition-all duration-200 rounded-xl">
            <h4 className="text-lg font-semibold text-slate-100 mb-4 flex items-center">
              <span className="text-xl mr-2">🎮</span>
              Create New Room
            </h4>
            <div className="text-center">
              <button 
                onClick={handleCreateRoom}
                disabled={isCreating}
                className="w-full bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800 disabled:from-slate-600 disabled:to-slate-700 text-white py-2 px-4 rounded-lg font-semibold transition-all duration-200 shadow-lg hover:shadow-emerald-500/25"
              >
                {isCreating ? (
                  <span className="flex items-center justify-center">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                    Creating...
                  </span>
                ) : (
                  'Create'
                )}
              </button>
            </div>
          </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GameLobby;