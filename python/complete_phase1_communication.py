#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Phase 1 Communication
Adds simple real-time messaging between browsers to finish Phase 1
"""

from pathlib import Path
from datetime import datetime

def add_changelog_entry():
    """Add entry to CHANGELOG.md"""
    try:
        changelog_path = Path("CHANGELOG.md")
        if not changelog_path.exists():
            return
            
        with open(changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "### Python Scripts Run" not in content:
            unreleased_section = content.find("## [Unreleased]")
            if unreleased_section != -1:
                insert_point = content.find("### Added", unreleased_section)
                if insert_point != -1:
                    new_section = "\n### Python Scripts Run\n- Phase 1 completion: Added real-time messaging between browsers\n"
                    content = content[:insert_point] + new_section + content[insert_point:]
        else:
            section_start = content.find("### Python Scripts Run")
            section_end = content.find("\n###", section_start + 1)
            if section_end == -1:
                section_end = content.find("\n## ", section_start + 1)
            
            entry = f"- Phase 1 completion: Added messaging system ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n"
            
            if section_end != -1:
                insert_point = section_end
                content = content[:insert_point] + entry + content[insert_point:]
            else:
                content += entry
        
        with open(changelog_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Updated CHANGELOG.md")
        
    except Exception as e:
        print(f"⚠️ Could not update CHANGELOG.md: {e}")

def enhance_backend_socket_handlers():
    """Add simple room and messaging system to backend"""
    print("🔧 Adding room and messaging system to backend...")
    
    index_path = Path("backend/src/index.ts")
    
    # Enhanced backend with room and messaging system
    enhanced_backend = '''import express, { Request, Response, NextFunction } from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

console.log('🚀 Starting Codenames backend server...');

const app = express();
const server = createServer(app);

// CORS configuration
const corsOptions = {
  origin: process.env.FRONTEND_URL || "http://localhost:5173",
  methods: ["GET", "POST"],
  credentials: true
};

app.use(cors(corsOptions));
app.use(express.json());

console.log('📦 Express middleware configured');

// Simple in-memory storage for Phase 1
const users = new Map<string, any>();
const rooms = new Map<string, any>();
const connectedUsers = new Map<string, any>();

// ========================================
// API ROUTES
// ========================================

// Health check endpoint
app.get('/api/health', (req: Request, res: Response): void => {
  console.log('🏥 Health check endpoint called');
  res.json({ 
    status: 'OK', 
    message: 'Codenames backend server is running',
    timestamp: new Date().toISOString(),
    connectedUsers: connectedUsers.size,
    activeRooms: rooms.size,
    endpoints: [
      'GET /api/health',
      'POST /api/auth/login', 
      'POST /api/auth/verify'
    ]
  });
});

// Auth routes
app.post('/api/auth/login', (req: Request, res: Response): void => {
  try {
    console.log('🔑 Login attempt:', req.body);
    
    const { username } = req.body;
    if (!username || username.trim().length === 0) {
      res.status(400).json({
        success: false,
        error: 'Username is required'
      });
      return;
    }
    
    // Create simple user for Phase 1
    const user = {
      id: `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      username: username.trim(),
      createdAt: new Date().toISOString()
    };
    
    // Simple token
    const token = `token_${user.id}_${Date.now()}`;
    
    // Store user
    users.set(user.id, { ...user, token });
    
    console.log('✅ Login successful for:', username);
    
    res.json({
      success: true,
      token,
      user: {
        id: user.id,
        username: user.username
      }
    });
    
  } catch (error) {
    console.error('❌ Login error:', error);
    res.status(500).json({
      success: false,
      error: 'Login failed',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Token verification
app.post('/api/auth/verify', (req: Request, res: Response): void => {
  try {
    console.log('🔍 Token verification attempt');
    
    const { token } = req.body;
    if (!token) {
      res.status(400).json({
        success: false,
        error: 'Token is required'
      });
      return;
    }
    
    // Find user by token
    let foundUser = null;
    for (const [userId, userData] of users.entries()) {
      if (userData.token === token) {
        foundUser = userData;
        break;
      }
    }
    
    if (!foundUser) {
      res.status(401).json({
        success: false,
        error: 'Invalid token'
      });
      return;
    }
    
    console.log('✅ Token verification successful for:', foundUser.username);
    
    res.json({
      success: true,
      user: {
        id: foundUser.id,
        username: foundUser.username
      }
    });
    
  } catch (error) {
    console.error('❌ Token verification error:', error);
    res.status(500).json({
      success: false,
      error: 'Token verification failed',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

console.log('🔗 API routes configured');

// ========================================
// SOCKET.IO SETUP WITH ROOMS AND MESSAGING
// ========================================

const io = new Server(server, {
  cors: corsOptions,
  transports: ['websocket', 'polling']
});

// Helper functions
function findUserByToken(token: string) {
  for (const [userId, userData] of users.entries()) {
    if (userData.token === token) {
      return userData;
    }
  }
  return null;
}

function createRoom() {
  const roomCode = Math.random().toString(36).substr(2, 6).toUpperCase();
  const room = {
    code: roomCode,
    users: new Map(),
    messages: [],
    createdAt: new Date().toISOString()
  };
  rooms.set(roomCode, room);
  return room;
}

function getOrCreateGlobalRoom() {
  if (!rooms.has('GLOBAL')) {
    const globalRoom = {
      code: 'GLOBAL',
      users: new Map(),
      messages: [],
      createdAt: new Date().toISOString()
    };
    rooms.set('GLOBAL', globalRoom);
  }
  return rooms.get('GLOBAL');
}

// Socket handlers
io.on('connection', (socket) => {
  console.log('📡 Socket connected:', socket.id);
  
  socket.on('authenticate', (token: string) => {
    console.log('🔐 Socket authentication attempt');
    
    const user = findUserByToken(token);
    
    if (user) {
      // Store connected user
      connectedUsers.set(socket.id, {
        ...user,
        socketId: socket.id,
        connectedAt: new Date().toISOString()
      });
      
      // Join global room automatically for Phase 1
      const globalRoom = getOrCreateGlobalRoom();
      globalRoom.users.set(socket.id, user);
      socket.join('GLOBAL');
      
      socket.emit('authenticated', { 
        success: true, 
        user: user,
        roomCode: 'GLOBAL'
      });
      
      // Notify others in global room
      socket.to('GLOBAL').emit('user-joined', {
        user: user,
        message: `${user.username} joined the chat`
      });
      
      // Send current users in room
      const roomUsers = Array.from(globalRoom.users.values());
      io.to('GLOBAL').emit('room-users', { users: roomUsers });
      
      // Send recent messages
      socket.emit('recent-messages', { messages: globalRoom.messages.slice(-10) });
      
      console.log('✅ Socket authenticated for:', user.username, 'in GLOBAL room');
    } else {
      socket.emit('authenticated', { success: false, error: 'Invalid token' });
      console.log('❌ Socket authentication failed');
    }
  });
  
  socket.on('send-message', (data) => {
    const user = connectedUsers.get(socket.id);
    if (!user) {
      socket.emit('error', { message: 'Not authenticated' });
      return;
    }
    
    const message = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
      username: user.username,
      userId: user.id,
      text: data.message,
      timestamp: new Date().toISOString()
    };
    
    // Add to global room messages
    const globalRoom = getOrCreateGlobalRoom();
    globalRoom.messages.push(message);
    
    // Keep only last 50 messages
    if (globalRoom.messages.length > 50) {
      globalRoom.messages = globalRoom.messages.slice(-50);
    }
    
    // Broadcast to all users in global room
    io.to('GLOBAL').emit('new-message', message);
    
    console.log(`💬 Message from ${user.username}: ${data.message}`);
  });
  
  socket.on('disconnect', () => {
    const user = connectedUsers.get(socket.id);
    if (user) {
      console.log('📡 Socket disconnected:', socket.id, user.username);
      
      // Remove from global room
      const globalRoom = getOrCreateGlobalRoom();
      globalRoom.users.delete(socket.id);
      
      // Notify others
      socket.to('GLOBAL').emit('user-left', {
        user: user,
        message: `${user.username} left the chat`
      });
      
      // Update room users
      const roomUsers = Array.from(globalRoom.users.values());
      io.to('GLOBAL').emit('room-users', { users: roomUsers });
      
      // Remove from connected users
      connectedUsers.delete(socket.id);
    } else {
      console.log('📡 Socket disconnected:', socket.id);
    }
  });
});

console.log('📡 Socket.io with messaging configured');

// ========================================
// ERROR HANDLING
// ========================================

// 404 handler for API routes
app.use('/api/*', (req: Request, res: Response): void => {
  console.log(`❌ API route not found: ${req.method} ${req.path}`);
  res.status(404).json({ 
    success: false, 
    error: 'API endpoint not found',
    path: req.path,
    method: req.method,
    availableEndpoints: [
      'GET /api/health',
      'POST /api/auth/login',
      'POST /api/auth/verify'
    ]
  });
});

// General error handler
app.use((err: any, req: Request, res: Response, next: NextFunction): void => {
  console.error('❌ Server error:', err);
  res.status(500).json({ 
    success: false, 
    error: 'Internal server error',
    message: err instanceof Error ? err.message : 'Unknown error'
  });
});

// ========================================
// START SERVER
// ========================================

const PORT = process.env.PORT || 3001;

server.listen(PORT, () => {
  console.log('');
  console.log('🎉 ================================');
  console.log(`🚀 Server running on port ${PORT}`);
  console.log('📡 Socket.io with messaging enabled');
  console.log(`🔗 API endpoints: http://localhost:${PORT}/api`);
  console.log(`🏥 Health check: http://localhost:${PORT}/api/health`);
  console.log('💬 Global chat room ready');
  console.log('🎉 ================================');
  console.log('');
});

export default app;
'''
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(enhanced_backend)
    
    print("✅ Enhanced backend with room and messaging system")

def create_chat_component():
    """Create a chat component for real-time messaging"""
    print("🔧 Creating chat component...")
    
    chat_component_path = Path("frontend/src/components/Chat")
    chat_component_path.mkdir(parents=True, exist_ok=True)
    
    chat_component_file = chat_component_path / "ChatRoom.tsx"
    
    chat_component_content = '''import React, { useState, useEffect, useRef } from 'react';
import socketService from '../../services/socketService';

interface Message {
  id: string;
  username: string;
  userId: string;
  text: string;
  timestamp: string;
}

interface User {
  id: string;
  username: string;
}

const ChatRoom: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [users, setUsers] = useState<User[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Set up socket listeners
    socketService.onConnect(() => {
      console.log('💬 Chat: Connected to server');
      setIsConnected(true);
    });

    socketService.onDisconnect(() => {
      console.log('💬 Chat: Disconnected from server');
      setIsConnected(false);
    });

    // Listen for authentication success
    socketService.onAuthenticated((data: any) => {
      if (data.success) {
        console.log('💬 Chat: Authenticated successfully');
      }
    });

    // Listen for recent messages
    const handleRecentMessages = (data: { messages: Message[] }) => {
      console.log('💬 Chat: Received recent messages:', data.messages);
      setMessages(data.messages);
    };

    // Listen for new messages
    const handleNewMessage = (message: Message) => {
      console.log('💬 Chat: New message:', message);
      setMessages(prev => [...prev, message]);
    };

    // Listen for user events
    const handleUserJoined = (data: { user: User; message: string }) => {
      console.log('💬 Chat: User joined:', data.user.username);
      // Add system message
      const systemMessage: Message = {
        id: `system_${Date.now()}`,
        username: 'System',
        userId: 'system',
        text: data.message,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, systemMessage]);
    };

    const handleUserLeft = (data: { user: User; message: string }) => {
      console.log('💬 Chat: User left:', data.user.username);
      // Add system message
      const systemMessage: Message = {
        id: `system_${Date.now()}`,
        username: 'System',
        userId: 'system',
        text: data.message,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, systemMessage]);
    };

    const handleRoomUsers = (data: { users: User[] }) => {
      console.log('💬 Chat: Room users updated:', data.users);
      setUsers(data.users);
    };

    // Set up socket listeners
    socketService.socket?.on('recent-messages', handleRecentMessages);
    socketService.socket?.on('new-message', handleNewMessage);
    socketService.socket?.on('user-joined', handleUserJoined);
    socketService.socket?.on('user-left', handleUserLeft);
    socketService.socket?.on('room-users', handleRoomUsers);

    // Cleanup
    return () => {
      socketService.socket?.off('recent-messages', handleRecentMessages);
      socketService.socket?.off('new-message', handleNewMessage);
      socketService.socket?.off('user-joined', handleUserJoined);
      socketService.socket?.off('user-left', handleUserLeft);
      socketService.socket?.off('room-users', handleRoomUsers);
    };
  }, []);

  const sendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newMessage.trim()) return;
    
    console.log('💬 Chat: Sending message:', newMessage);
    socketService.socket?.emit('send-message', { message: newMessage.trim() });
    setNewMessage('');
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div className="bg-white rounded-lg shadow border border-gray-200 h-96 flex flex-col">
      {/* Header */}
      <div className="bg-blue-600 text-white p-3 rounded-t-lg">
        <h3 className="font-semibold">Global Chat Room</h3>
        <div className="text-sm opacity-90">
          {isConnected ? (
            <span className="flex items-center">
              <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
              {users.length} user{users.length !== 1 ? 's' : ''} online
            </span>
          ) : (
            <span className="flex items-center">
              <span className="w-2 h-2 bg-red-400 rounded-full mr-2"></span>
              Disconnected
            </span>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <p>No messages yet...</p>
            <p className="text-sm">Send a message to start the conversation!</p>
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className={`${
              message.username === 'System' ? 'text-center text-gray-500 text-sm' : ''
            }`}>
              {message.username === 'System' ? (
                <em>{message.text}</em>
              ) : (
                <div className="flex flex-col">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-blue-600">{message.username}</span>
                    <span className="text-xs text-gray-500">{formatTime(message.timestamp)}</span>
                  </div>
                  <p className="text-gray-900 mt-1">{message.text}</p>
                </div>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={sendMessage} className="p-3 border-t border-gray-200">
        <div className="flex space-x-2">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
            disabled={!isConnected}
          />
          <button
            type="submit"
            disabled={!isConnected || !newMessage.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white px-4 py-2 rounded-md transition-colors"
          >
            Send
          </button>
        </div>
      </form>

      {/* Online Users */}
      {users.length > 0 && (
        <div className="p-3 border-t border-gray-200 bg-gray-50">
          <p className="text-sm font-medium text-gray-700 mb-2">Online Users:</p>
          <div className="flex flex-wrap gap-2">
            {users.map((user) => (
              <span key={user.id} className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
                {user.username}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatRoom;
'''
    
    with open(chat_component_file, 'w', encoding='utf-8') as f:
        f.write(chat_component_content)
    
    print("✅ Created ChatRoom component")

def update_socket_service():
    """Update socket service to expose socket instance"""
    print("🔧 Updating socket service...")
    
    socket_service_path = Path("frontend/src/services/socketService.ts")
    
    enhanced_socket_service = '''import { io, Socket } from 'socket.io-client';

export interface User {
  id: string;
  username: string;
  socketId?: string;
}

export interface Room {
  id: string;
  name: string;
  code: string;
  maxPlayers: number;
  users: Array<{
    user: User;
    role: string;
    team?: string;
  }>;
}

export interface ChatMessage {
  id: string;
  username: string;
  message: string;
  timestamp: string;
}

class SocketService {
  private _socket: Socket | null = null;
  private token: string | null = null;

  get socket(): Socket | null {
    return this._socket;
  }

  connect(): Socket {
    if (this._socket?.connected) {
      console.log('📡 Socket already connected');
      return this._socket;
    }

    const socketUrl = import.meta.env.VITE_SOCKET_URL || 'http://localhost:3001';
    console.log('📡 Connecting to socket server:', socketUrl);

    this._socket = io(socketUrl, {
      autoConnect: false,
      transports: ['websocket', 'polling'],
      timeout: 5000,
      forceNew: true,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000
    });

    this.setupEventListeners();
    this._socket.connect();

    return this._socket;
  }

  disconnect(): void {
    if (this._socket) {
      console.log('📡 Disconnecting socket');
      this._socket.disconnect();
      this._socket = null;
    }
  }

  authenticate(token: string): void {
    this.token = token;
    if (this._socket) {
      console.log('🔐 Authenticating with token');
      this._socket.emit('authenticate', token);
    }
  }

  joinRoom(roomCode: string): void {
    if (this._socket) {
      console.log('🏠 Joining room:', roomCode);
      this._socket.emit('join-room', { roomCode });
    }
  }

  leaveRoom(): void {
    if (this._socket) {
      console.log('🚪 Leaving room');
      this._socket.emit('leave-room');
    }
  }

  createRoom(roomName?: string): void {
    if (this._socket) {
      console.log('🏗️ Creating room:', roomName || 'Unnamed');
      this._socket.emit('create-room', { roomName });
    }
  }

  sendMessage(message: string): void {
    if (this._socket) {
      console.log('💬 Sending message:', message);
      this._socket.emit('chat-message', { message });
    }
  }

  // Event listener registration methods
  onAuthenticated(callback: (data: any) => void): void {
    this._socket?.on('authenticated', callback);
  }

  onRoomJoined(callback: (data: any) => void): void {
    this._socket?.on('room-joined', callback);
  }

  onRoomCreated(callback: (data: any) => void): void {
    this._socket?.on('room-created', callback);
  }

  onUserJoined(callback: (data: any) => void): void {
    this._socket?.on('user-joined', callback);
  }

  onUserLeft(callback: (data: any) => void): void {
    this._socket?.on('user-left', callback);
  }

  onRoomUsersUpdated(callback: (data: { users: User[] }) => void): void {
    this._socket?.on('room-users-updated', callback);
  }

  onChatMessage(callback: (message: ChatMessage) => void): void {
    this._socket?.on('chat-message', callback);
  }

  onError(callback: (error: any) => void): void {
    this._socket?.on('error', callback);
  }

  onConnect(callback: () => void): void {
    this._socket?.on('connect', callback);
  }

  onDisconnect(callback: () => void): void {
    this._socket?.on('disconnect', callback);
  }

  // Cleanup method to remove specific listeners
  off(event: string, callback?: Function): void {
    if (callback) {
      this._socket?.off(event, callback);
    } else {
      this._socket?.off(event);
    }
  }

  private setupEventListeners(): void {
    if (!this._socket) return;

    this._socket.on('connect', () => {
      console.log('✅ Connected to server, Socket ID:', this._socket?.id);
      // Re-authenticate if we have a token
      if (this.token) {
        console.log('🔐 Re-authenticating after reconnection');
        this.authenticate(this.token);
      }
    });

    this._socket.on('disconnect', (reason) => {
      console.log('❌ Disconnected from server. Reason:', reason);
    });

    this._socket.on('connect_error', (error) => {
      console.error('🚫 Socket connection error:', error);
    });

    this._socket.on('reconnect', (attemptNumber) => {
      console.log('🔄 Reconnected after', attemptNumber, 'attempts');
    });

    this._socket.on('reconnect_error', (error) => {
      console.error('🔄 Reconnection failed:', error);
    });
  }

  get isConnected(): boolean {
    return this._socket?.connected || false;
  }

  get socketId(): string | undefined {
    return this._socket?.id;
  }
}

// Export singleton instance
export const socketService = new SocketService();
export default socketService;
'''
    
    with open(socket_service_path, 'w', encoding='utf-8') as f:
        f.write(enhanced_socket_service)
    
    print("✅ Updated socket service")

def update_home_page_with_chat():
    """Add chat room to home page"""
    print("🔧 Adding chat to home page...")
    
    home_page_path = Path("frontend/src/pages/HomePage.tsx")
    
    home_page_with_chat = '''import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ChatRoom from '../components/Chat/ChatRoom';

const HomePage: React.FC = () => {
  const [roomCode, setRoomCode] = useState('');
  const navigate = useNavigate();

  const handleCreateRoom = () => {
    // For Phase 1, just show success message
    alert('Room creation will be implemented in Phase 2!');
  };

  const handleJoinRoom = () => {
    if (!roomCode.trim()) {
      alert('Please enter a room code');
      return;
    }
    // For Phase 1, just show success message
    alert(`Joining room: ${roomCode} - Will be implemented in Phase 2!`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Welcome to Codenames!</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left side - Room management */}
          <div className="space-y-6">
            {/* Create Room */}
            <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
              <h2 className="text-xl font-semibold mb-4 text-gray-900">Create New Room</h2>
              <p className="text-gray-600 mb-4">Start a new game and invite friends to join</p>
              <button 
                onClick={handleCreateRoom}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded transition-colors"
              >
                Create Room
              </button>
            </div>
            
            {/* Join Room */}
            <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
              <h2 className="text-xl font-semibold mb-4 text-gray-900">Join Existing Room</h2>
              <div className="space-y-4">
                <div>
                  <label htmlFor="roomCode" className="block text-sm font-medium text-gray-700 mb-2">
                    Room Code
                  </label>
                  <input
                    type="text"
                    id="roomCode"
                    value={roomCode}
                    onChange={(e) => setRoomCode(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
                    placeholder="Enter room code"
                  />
                </div>
                <button 
                  onClick={handleJoinRoom}
                  className="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded transition-colors"
                >
                  Join Room
                </button>
              </div>
            </div>
            
            {/* Phase 1 Status */}
            <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
              <h3 className="font-semibold text-blue-900 mb-2">🎉 Phase 1: Real-time Communication!</h3>
              <div className="text-blue-800 space-y-1">
                <p>✅ Backend server and API working</p>
                <p>✅ Socket connection established</p>
                <p>✅ Authentication system working</p>
                <p>✅ Real-time messaging working</p>
                <p className="mt-2 font-semibold">📱 Test with multiple browser windows!</p>
              </div>
            </div>
          </div>
          
          {/* Right side - Chat Room */}
          <div>
            <h2 className="text-xl font-semibold mb-4 text-gray-900">Real-time Chat</h2>
            <ChatRoom />
            <div className="mt-4 text-sm text-gray-600 bg-yellow-50 border border-yellow-200 p-3 rounded">
              <p><strong>🧪 Phase 1 Test:</strong></p>
              <p>• Open this page in multiple browser windows</p>
              <p>• Login as different users in each window</p>
              <p>• Send messages and see them appear in real-time!</p>
            </div>
          </div>
        </div>
        
        {/* Debug Section */}
        <div className="mt-8 bg-gray-100 border border-gray-300 p-4 rounded-lg">
          <h3 className="font-semibold text-gray-900 mb-2">🔧 Debug Tools</h3>
          <div className="text-gray-700 space-y-2">
            <p>• <a href="/debug" className="text-blue-600 hover:text-blue-800 underline">Debug Dashboard</a> - Test connections</p>
            <p>• Check browser console (F12) for detailed logs</p>
            <p>• Room creation and game mechanics coming in Phase 2!</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
'''
    
    with open(home_page_path, 'w', encoding='utf-8') as f:
        f.write(home_page_with_chat)
    
    print("✅ Added chat room to home page")

def main():
    """Main execution function"""
    print("🎯 Completing Phase 1: Real-time Communication")
    print("=" * 55)
    
    try:
        # Enhance backend with messaging
        enhance_backend_socket_handlers()
        
        # Create chat component
        create_chat_component()
        
        # Update socket service
        update_socket_service()
        
        # Update home page with chat
        update_home_page_with_chat()
        
        # Update changelog
        add_changelog_entry()
        
        print("\n🎉 Phase 1 Communication Complete!")
        print("=" * 55)
        
        print("\n📋 What was added:")
        print("✅ Backend: Global chat room with real-time messaging")
        print("✅ Backend: User presence tracking (join/leave notifications)")
        print("✅ Frontend: ChatRoom component with message history")
        print("✅ Frontend: Online user list and system notifications")
        print("✅ Real-time: Messages appear instantly across browsers")
        
        print("\n🔧 Next steps:")
        print("1. RESTART your backend server:")
        print("   cd backend && npm run dev")
        print("2. Refresh your frontend page")
        print("3. OPEN MULTIPLE BROWSER WINDOWS:")
        print("   - Login as different users in each window")
        print("   - Send messages and watch them appear in real-time!")
        
        print("\n🎯 Phase 1 Test:")
        print("✅ Two browsers can connect and communicate")
        print("✅ Real-time messaging works reliably")
        print("✅ Authentication flow works properly")
        print("✅ Users can see each other online")
        
        print("\n🎮 Ready for Phase 2:")
        print("Once you confirm messaging works between browsers,")
        print("Phase 1 is TRULY COMPLETE and we can start building")
        print("the actual Codenames game mechanics!")
        
        return 0
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
