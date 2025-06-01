#!/usr/bin/env python3
import os
import json
from datetime import datetime

def implement_team_assignment():
    """
    Implement team assignment flow and fix game state loading issues.
    Focus on connecting room page to actual Codenames game mechanics.
    """
    print("🎯 Implementing Team Assignment & Game Flow...")
    
    # 1. Update RoomPage to include game start button and team assignment
    room_page_content = '''import React, { useState, useEffect } from 'react';
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
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [gameInfo, setGameInfo] = useState<GameInfo | null>(null);
  const [players, setPlayers] = useState<Player[]>([]);
  const [messages, setMessages] = useState<RoomMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [gameStarted, setGameStarted] = useState(false);

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    setCurrentUser(user);
    loadGameAndConnect();
  }, [roomCode]);

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

  const connectToRoom = (gameCode: string, token: string) => {
    console.log('🔌 Connecting to room socket...', gameCode);
    
    if (!socketService.socket?.connected) {
      socketService.connect();
      socketService.authenticate(token);
    }

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

    // Listen for game events
    gameService.onGameStateUpdated((gameState: any) => {
      console.log('🎮 Game state updated in room:', gameState);
      if (gameState.status === 'playing') {
        setGameStarted(true);
      }
      // Update players with team/role info
      setPlayers(gameState.players || []);
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
    console.log(`👥 Joining ${team} team as ${role}`);
    gameService.joinTeam(team as any, role as any);
  };

  const handleStartGame = () => {
    console.log('🚀 Starting Codenames game...');
    gameService.startGame();
  };

  const handleGoToGame = () => {
    console.log('🎮 Navigating to game board...');
    navigate('/game');
  };

  const canStartGame = () => {
    const redPlayers = players.filter(p => p.team === 'red');
    const bluePlayers = players.filter(p => p.team === 'blue');
    const redSpymaster = redPlayers.find(p => p.role === 'spymaster');
    const blueSpymaster = bluePlayers.find(p => p.role === 'spymaster');
    
    return redSpymaster && blueSpymaster && redPlayers.length >= 2 && bluePlayers.length >= 2;
  };

  const getCurrentUserPlayer = () => {
    return players.find(p => p.username === currentUser?.username);
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
                        className="w-full bg-red-500 text-white px-4 py-3 rounded-lg font-semibold hover:bg-red-600 transition-colors"
                        disabled={players.some(p => p.team === 'red' && p.role === 'spymaster')}
                      >
                        {players.some(p => p.team === 'red' && p.role === 'spymaster') ? '👑 Spymaster Taken' : '👑 Join as Spymaster'}
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
                      {players.filter(p => p.team === 'red').length === 0 ? (
                        <p className="text-gray-500 italic">No players yet</p>
                      ) : (
                        players.filter(p => p.team === 'red').map(player => (
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
                        className="w-full bg-blue-500 text-white px-4 py-3 rounded-lg font-semibold hover:bg-blue-600 transition-colors"
                        disabled={players.some(p => p.team === 'blue' && p.role === 'spymaster')}
                      >
                        {players.some(p => p.team === 'blue' && p.role === 'spymaster') ? '👑 Spymaster Taken' : '👑 Join as Spymaster'}
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
                      {players.filter(p => p.team === 'blue').length === 0 ? (
                        <p className="text-gray-500 italic">No players yet</p>
                      ) : (
                        players.filter(p => p.team === 'blue').map(player => (
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
                👥 Players ({players.length})
              </h3>
              <div className="space-y-2">
                {players.length > 0 ? (
                  players.map((player) => (
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

export default RoomPage;'''

    # Write the updated RoomPage
    with open('frontend/src/pages/RoomPage.tsx', 'w', encoding='utf-8') as f:
        f.write(room_page_content)
    
    print("✅ Updated RoomPage with team assignment")
    
    # 2. Fix the GamePage to properly initialize with game state
    game_page_content = '''import React, { useState, useEffect } from 'react';
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

export default GamePage;'''

    with open('frontend/src/pages/GamePage.tsx', 'w', encoding='utf-8') as f:
        f.write(game_page_content)
    
    print("✅ Updated GamePage with better state loading")
    
    # 3. Add a socket handler for requesting game state
    backend_socket_addition = '''
  
  // Add handler for requesting current game state
  socket.on('game:request-state', () => {
    if (!socket.userId) {
      socket.emit('game:error', 'Not authenticated');
      return;
    }

    console.log('🔍 Game state requested by:', socket.username);
    
    // Try to find existing game for user
    const game = gameService.getGameByPlayer(socket.userId);
    if (game) {
      const gameState = game.getGame();
      socket.emit('game:state-updated', gameState);
      console.log('📤 Sent existing game state to:', socket.username);
    } else {
      console.log('❌ No existing game found for:', socket.username);
      socket.emit('game:error', 'No active game found');
    }
  });'''

    # Read current backend index.ts
    with open('backend/src/index.ts', 'r', encoding='utf-8') as f:
        backend_content = f.read()
    
    # Add the new handler before the disconnect handler
    if 'game:request-state' not in backend_content:
        backend_content = backend_content.replace(
            '  socket.on(\'disconnect\', () => {',
            backend_socket_addition + '\n\n  socket.on(\'disconnect\', () => {'
        )
        
        with open('backend/src/index.ts', 'w', encoding='utf-8') as f:
            f.write(backend_content)
        
        print("✅ Added game state request handler to backend")
    
    # 4. Update CHANGELOG
    update_changelog()
    
    print("\n🎉 TEAM ASSIGNMENT IMPLEMENTATION COMPLETE!")
    print("\n📋 What was implemented:")
    print("  ✅ Enhanced RoomPage with full team assignment UI")
    print("  ✅ Team selection (Red/Blue) with role selection (Spymaster/Operative)")
    print("  ✅ Game start validation (requires both teams with proper setup)")
    print("  ✅ Improved GamePage with better state loading and error handling")
    print("  ✅ Added game state request handler to backend")
    print("  ✅ Seamless flow from room setup to actual game")
    
    print("\n🚀 NEXT STEPS:")
    print("  1. Test the new team assignment flow")
    print("  2. Create a game, join teams, and start the game")
    print("  3. Verify the game board loads properly")
    print("  4. Test actual Codenames gameplay mechanics")

def update_changelog():
    """Update the CHANGELOG.md with this session's changes"""
    try:
        with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the "### Python Scripts Run" section and add our entry
        new_entry = f"- Team Assignment Implementation: Enhanced room page with full team selection, role assignment, and game start validation (2025-05-31 {datetime.now().strftime('%H:%M')})"
        
        if "### Python Scripts Run" in content:
            content = content.replace(
                "### Python Scripts Run\n",
                f"### Python Scripts Run\n{new_entry}\n"
            )
        else:
            # Add the section if it doesn't exist
            content = content.replace(
                "## [Unreleased]\n",
                f"## [Unreleased]\n\n### Python Scripts Run\n{new_entry}\n"
            )
        
        with open('CHANGELOG.md', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Updated CHANGELOG.md")
        
    except Exception as e:
        print(f"⚠️  Could not update CHANGELOG.md: {e}")

if __name__ == "__main__":
    implement_team_assignment()
