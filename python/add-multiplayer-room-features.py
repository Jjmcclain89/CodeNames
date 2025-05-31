#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Add Multiplayer Room Features
Adds player tracking, room-specific chat, and real-time multiplayer to game rooms
"""

import os
from datetime import datetime

def update_file_content(file_path, new_content):
    """Update file with proper Windows encoding"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    print("🔧 Adding Multiplayer Room Features...")
    
    # 1. Update backend games routes to handle players
    updated_games_routes = '''import express, { Request, Response } from 'express';

const router = express.Router();

// In-memory storage for games and players
const gameRooms = new Map<string, {
  code: string;
  id: string;
  status: string;
  players: Array<{id: string; username: string; socketId?: string; joinedAt: string}>;
  messages: Array<{id: string; username: string; userId: string; text: string; timestamp: string}>;
  createdAt: string;
}>();

// Test endpoint to verify API is working
router.get('/test', (req: Request, res: Response): void => {
  console.log('🧪 API test endpoint hit!');
  res.json({ 
    success: true, 
    message: 'Games API is working!',
    timestamp: new Date().toISOString()
  });
});

// Get game info by code
router.get('/:gameCode', (req: Request, res: Response): void => {
  try {
    const { gameCode } = req.params;
    console.log(`🔍 GET /api/games/${gameCode} - Getting game info...`);
    
    if (!gameCode) {
      res.status(400).json({ 
        success: false,
        error: 'Game code is required' 
      });
      return;
    }
    
    const gameRoom = gameRooms.get(gameCode.toUpperCase());
    
    if (gameRoom) {
      const response = { 
        success: true, 
        game: {
          code: gameRoom.code,
          id: gameRoom.id,
          status: gameRoom.status,
          playerCount: gameRoom.players.length,
          players: gameRoom.players.map(p => ({
            id: p.id,
            username: p.username,
            joinedAt: p.joinedAt
          })),
          messages: gameRoom.messages.slice(-20) // Last 20 messages
        },
        timestamp: new Date().toISOString()
      };
      
      console.log('📤 Sending game info:', response);
      res.json(response);
    } else {
      res.status(404).json({ 
        success: false,
        error: 'Game not found' 
      });
    }
    
  } catch (error) {
    console.error('❌ Error in /api/games/:gameCode:', error);
    res.status(500).json({ 
      success: false,
      error: 'Failed to get game info',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Create a new game
router.post('/create', (req: Request, res: Response): void => {
  try {
    console.log('🎮 POST /api/games/create - Creating new game...');
    console.log('📦 Request body:', req.body);
    
    const { userId, username } = req.body;
    
    // Generate simple 6-character game code
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let gameCode = '';
    for (let i = 0; i < 6; i++) {
      gameCode += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    
    // Create the game room
    const gameRoom = {
      code: gameCode,
      id: `game_${gameCode.toLowerCase()}_${Date.now()}`,
      status: 'waiting',
      players: [],
      messages: [],
      createdAt: new Date().toISOString()
    };
    
    // Add creator as first player if provided
    if (username) {
      gameRoom.players.push({
        id: userId || `user_${Date.now()}`,
        username: username,
        joinedAt: new Date().toISOString()
      });
    }
    
    gameRooms.set(gameCode, gameRoom);
    
    console.log(`✅ Created game room: ${gameCode} with ${gameRoom.players.length} initial players`);
    
    const response = { 
      success: true, 
      gameCode: gameCode,
      message: 'Game created successfully!',
      game: {
        code: gameCode,
        id: gameRoom.id,
        status: gameRoom.status,
        playerCount: gameRoom.players.length
      },
      timestamp: new Date().toISOString()
    };
    
    console.log('📤 Sending response:', response);
    res.json(response);
    
  } catch (error) {
    console.error('❌ Error in /api/games/create:', error);
    res.status(500).json({ 
      success: false,
      error: 'Failed to create game',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Join an existing game
router.post('/join', (req: Request, res: Response): void => {
  try {
    const { gameCode, userId, username } = req.body;
    console.log(`🚪 POST /api/games/join - User ${username} joining game: ${gameCode}`);
    
    if (!gameCode) {
      res.status(400).json({ 
        success: false,
        error: 'Game code is required' 
      });
      return;
    }
    
    const gameRoom = gameRooms.get(gameCode.toUpperCase());
    
    if (!gameRoom) {
      res.status(404).json({ 
        success: false,
        error: 'Game not found' 
      });
      return;
    }
    
    // Add player to game if not already in it
    if (username && !gameRoom.players.find(p => p.username === username)) {
      gameRoom.players.push({
        id: userId || `user_${Date.now()}`,
        username: username,
        joinedAt: new Date().toISOString()
      });
      
      console.log(`✅ Added player ${username} to game ${gameCode}. Total players: ${gameRoom.players.length}`);
    }
    
    const response = { 
      success: true, 
      gameCode: gameCode.toUpperCase(),
      message: 'Joined game successfully!',
      game: {
        code: gameRoom.code,
        id: gameRoom.id,
        status: gameRoom.status,
        playerCount: gameRoom.players.length
      },
      timestamp: new Date().toISOString()
    };
    
    console.log('📤 Sending response:', response);
    res.json(response);
    
  } catch (error) {
    console.error('❌ Error in /api/games/join:', error);
    res.status(500).json({ 
      success: false,
      error: 'Failed to join game',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Export gameRooms for use in socket handlers
export { gameRooms };
export default router;
'''

    # 2. Update backend index.ts to add room-specific socket handlers
    backend_index_additions = '''
// Add these room-specific socket handlers after the existing socket handlers

// Room-specific socket handlers
socket.on('join-game-room', (gameCode: string) => {
  const user = connectedUsers.get(socket.id);
  if (!user) {
    socket.emit('error', { message: 'Not authenticated' });
    return;
  }
  
  console.log(`🎮 User ${user.username} joining game room: ${gameCode}`);
  
  // Leave any previous game rooms
  const rooms = Array.from(socket.rooms);
  rooms.forEach(room => {
    if (room !== socket.id && room !== 'GLOBAL' && room.length === 6) {
      socket.leave(room);
      console.log(`📤 User ${user.username} left room: ${room}`);
    }
  });
  
  // Join the new game room
  socket.join(gameCode);
  
  // Import gameRooms from routes
  const { gameRooms } = require('./routes/games');
  const gameRoom = gameRooms.get(gameCode);
  
  if (gameRoom) {
    // Update player socket ID in game room
    const player = gameRoom.players.find((p: any) => p.username === user.username);
    if (player) {
      player.socketId = socket.id;
    }
    
    // Notify others in the room
    socket.to(gameCode).emit('player-joined-room', {
      player: { username: user.username, id: user.id },
      message: `${user.username} joined the game`,
      playerCount: gameRoom.players.length
    });
    
    // Send current room state to the joining player
    socket.emit('room-state', {
      gameCode: gameCode,
      players: gameRoom.players.map((p: any) => ({
        id: p.id,
        username: p.username,
        joinedAt: p.joinedAt
      })),
      messages: gameRoom.messages.slice(-20)
    });
    
    console.log(`✅ User ${user.username} joined game room ${gameCode}`);
  } else {
    socket.emit('error', { message: 'Game room not found' });
  }
});

socket.on('send-room-message', (data: { gameCode: string; message: string }) => {
  const user = connectedUsers.get(socket.id);
  if (!user) {
    socket.emit('error', { message: 'Not authenticated' });
    return;
  }
  
  const { gameCode, message } = data;
  console.log(`💬 Room message from ${user.username} in ${gameCode}: ${message}`);
  
  const { gameRooms } = require('./routes/games');
  const gameRoom = gameRooms.get(gameCode);
  
  if (gameRoom) {
    const roomMessage = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
      username: user.username,
      userId: user.id,
      text: message,
      timestamp: new Date().toISOString()
    };
    
    // Add to room messages
    gameRoom.messages.push(roomMessage);
    
    // Keep only last 50 messages
    if (gameRoom.messages.length > 50) {
      gameRoom.messages = gameRoom.messages.slice(-50);
    }
    
    // Broadcast to all users in the room
    io.to(gameCode).emit('new-room-message', roomMessage);
  } else {
    socket.emit('error', { message: 'Game room not found' });
  }
});
'''

    # 3. Create updated RoomPage with multiplayer features
    multiplayer_room_page = '''import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { socketService } from '../services/socketService';

interface Player {
  id: string;
  username: string;
  joinedAt: string;
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
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [gameInfo, setGameInfo] = useState<GameInfo | null>(null);
  const [players, setPlayers] = useState<Player[]>([]);
  const [messages, setMessages] = useState<RoomMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const loadGameAndConnect = async () => {
      if (!roomCode) {
        setError('No room code provided');
        setIsLoading(false);
        return;
      }

      try {
        console.log('🎮 Loading game info for room:', roomCode);
        
        // Get user info for joining
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        const token = localStorage.getItem('token');
        
        if (!user.username || !token) {
          setError('Please log in first');
          setIsLoading(false);
          return;
        }

        // First, join the game via API
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

        // Now get game info
        const response = await fetch(`/api/games/${roomCode}`);
        
        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            setGameInfo(data.game);
            setPlayers(data.game.players || []);
            setMessages(data.game.messages || []);
            
            // Connect to socket for real-time updates
            connectToRoom(roomCode, token);
            
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

    loadGameAndConnect();

    // Cleanup on unmount
    return () => {
      if (socketService.socket) {
        socketService.socket.off('player-joined-room');
        socketService.socket.off('room-state');
        socketService.socket.off('new-room-message');
      }
    };
  }, [roomCode]);

  const connectToRoom = (gameCode: string, token: string) => {
    console.log('🔌 Connecting to room socket...', gameCode);
    
    // Ensure socket is connected and authenticated
    if (!socketService.socket?.connected) {
      socketService.connect();
      socketService.authenticate(token);
    }

    // Wait for authentication then join room
    const handleAuth = () => {
      console.log('✅ Socket authenticated, joining room:', gameCode);
      socketService.socket?.emit('join-game-room', gameCode);
      setIsConnected(true);
    };

    if (socketService.socket?.connected) {
      handleAuth();
    } else {
      socketService.socket?.on('authenticated', handleAuth);
    }

    // Listen for room events
    socketService.socket?.on('player-joined-room', (data: any) => {
      console.log('👥 Player joined room:', data);
      setPlayers(prev => {
        // Add player if not already in list
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

  const handleGoBack = () => {
    navigate('/');
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
              onClick={handleGoBack}
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

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto p-6">
        <div className="mb-6 flex justify-between items-center">
          <button 
            onClick={handleGoBack}
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
          {/* Main Game Area */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
              <h1 className="text-3xl font-bold text-gray-900 mb-6">
                Game Room: {roomCode}
              </h1>
              
              {gameInfo && (
                <div className="space-y-4">
                  <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                    <h3 className="font-semibold text-green-900 mb-2">✅ Game Active!</h3>
                    <div className="grid grid-cols-2 gap-4 text-green-800 text-sm">
                      <div>
                        <p><strong>Code:</strong> {gameInfo.code}</p>
                        <p><strong>Status:</strong> {gameInfo.status}</p>
                      </div>
                      <div>
                        <p><strong>Players:</strong> {players.length}</p>
                        <p><strong>Real-time:</strong> {isConnected ? '✅' : '🔄'}</p>
                      </div>
                    </div>
                  </div>
                  
                  {/* Placeholder Game Board */}
                  <div className="bg-gray-50 border border-gray-200 p-6 rounded-lg">
                    <h3 className="font-semibold text-gray-700 mb-4 text-center">🎯 Game Board</h3>
                    <p className="text-gray-600 text-center mb-4">Codenames game mechanics coming in Phase 2!</p>
                    <div className="grid grid-cols-5 gap-2 max-w-lg mx-auto">
                      {Array.from({length: 25}, (_, i) => (
                        <div key={i} className="bg-white border border-gray-300 p-3 text-xs text-center rounded hover:bg-gray-100 cursor-pointer">
                          WORD {i+1}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
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
                  players.map((player) => (
                    <div key={player.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <div>
                        <div className="font-medium text-gray-900">{player.username}</div>
                        <div className="text-xs text-gray-500">
                          Joined {new Date(player.joinedAt).toLocaleTimeString()}
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
              
              {/* Messages */}
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

              {/* Message Input */}
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
'''

    # Update files
    success_count = 0
    
    if update_file_content('backend/src/routes/games.ts', updated_games_routes):
        print("✅ Updated backend games routes with player tracking")
        success_count += 1
    
    if update_file_content('frontend/src/pages/RoomPage.tsx', multiplayer_room_page):
        print("✅ Updated RoomPage with multiplayer features")
        success_count += 1
    
    # Instructions for manually updating backend index.ts
    print(f"\n🔧 Manual Step Required:")
    print(f"Please add these socket handlers to your backend/src/index.ts file:")
    print(f"Add this code right after the existing 'send-message' socket handler:")
    print(f"\n{backend_index_additions}")
    
    # Update changelog
    try:
        changelog_path = 'CHANGELOG.md'
        with open(changelog_path, 'r', encoding='utf-8') as f:
            changelog = f.read()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        new_entry = f'- Multiplayer Room Features: Added player tracking, room chat, and real-time multiplayer ({timestamp})'
        
        if '### Python Scripts Run' in changelog:
            updated_changelog = changelog.replace(
                '### Python Scripts Run',
                f'### Python Scripts Run\n{new_entry}'
            )
            
            with open(changelog_path, 'w', encoding='utf-8') as f:
                f.write(updated_changelog)
            print("✅ Updated CHANGELOG.md")
            success_count += 1
    except Exception as e:
        print(f"Note: Could not update changelog: {e}")
    
    print(f"\n🎉 Multiplayer Room Features Added!")
    print(f"✅ {success_count} files updated successfully")
    print("\n🔧 What was added:")
    print("• Player tracking and storage in game rooms")
    print("• Real-time player list in room page")
    print("• Room-specific chat (separate from global chat)")
    print("• Socket integration for live updates")
    print("• Join game API that adds players to rooms")
    print("\n⚠️ MANUAL STEP REQUIRED:")
    print("Please add the socket handlers shown above to backend/src/index.ts")
    print("Add them after the existing 'send-message' handler")
    print("\n🎯 Next Steps:")
    print("1. Add the socket handlers to backend index.ts (manual step)")
    print("2. Restart both backend and frontend servers")
    print("3. Create a game in one browser window")
    print("4. Join the same game code in a second browser window")
    print("5. You should see both players and be able to chat!")
    print("\n💡 Test with multiple browser windows/tabs for full multiplayer experience!")

if __name__ == "__main__":
    main()
