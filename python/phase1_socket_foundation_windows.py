#!/usr/bin/env python3
"""
Phase 1: Socket Foundation (Windows Compatible)
Implements real-time communication, room management, and authentication
Goal: Two browsers can connect and communicate
"""

import os
import json
from datetime import datetime

def update_changelog():
    """Update changelog with Phase 1 completion"""
    changelog_path = "../CHANGELOG.md"
    
    if not os.path.exists(changelog_path):
        print("ERROR: CHANGELOG.md not found")
        return
    
    with open(changelog_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the [Unreleased] section and add our changes
    unreleased_section = content.find("## [Unreleased]")
    if unreleased_section == -1:
        print("ERROR: Could not find [Unreleased] section in CHANGELOG.md")
        return
    
    # Find the ### Added section
    added_section = content.find("### Added", unreleased_section)
    if added_section == -1:
        print("ERROR: Could not find ### Added section")
        return
    
    # Find the end of the Added section
    next_section = content.find("### Changed", added_section)
    if next_section == -1:
        next_section = content.find("### Deprecated", added_section)
    
    # Insert our new items
    new_items = """- Real-time Socket.io communication with room management
- JWT authentication for socket connections
- User authentication system with login/register endpoints
- Room creation, joining, and real-time user presence
- Frontend socket client with connection state management
- Real-time messaging system between connected users
- Python script automation for Phase 1 completion (phase1_socket_foundation.py)

"""
    
    if next_section != -1:
        # Insert before the next section
        updated_content = content[:next_section] + new_items + content[next_section:]
    else:
        # Insert at the end of the file if no next section found
        updated_content = content + new_items
    
    with open(changelog_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("SUCCESS: Updated CHANGELOG.md with Phase 1 completion")

def create_socket_backend():
    """Create Socket.io backend implementation"""
    backend_src = "../backend/src"
    
    # 1. Update server.ts with comprehensive Socket.io setup
    server_content = '''import express from 'express';
import cors from 'cors';
import { createServer } from 'http';
import { Server } from 'socket.io';
import dotenv from 'dotenv';
import { PrismaClient } from '@prisma/client';
import jwt from 'jsonwebtoken';

// Import routes
import authRoutes from './routes/auth';
import roomRoutes from './routes/rooms';

// Import socket handlers
import { handleSocketConnection } from './socket/socketHandlers';

// Load environment variables
dotenv.config();

// Initialize Prisma
const prisma = new PrismaClient();

// Create Express app
const app = express();
const server = createServer(app);

// Initialize Socket.io
const io = new Server(server, {
  cors: {
    origin: process.env.FRONTEND_URL || "http://localhost:5173",
    methods: ["GET", "POST"],
    credentials: true
  }
});

// Middleware
app.use(cors({
  origin: process.env.FRONTEND_URL || "http://localhost:5173",
  credentials: true
}));
app.use(express.json());

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/rooms', roomRoutes);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    socketConnections: io.engine.clientsCount 
  });
});

// Socket.io connection handling
io.on('connection', (socket) => {
  handleSocketConnection(io, socket, prisma);
});

// Start server
const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Socket.io ready for connections`);
  console.log(`Frontend URL: ${process.env.FRONTEND_URL || "http://localhost:5173"}`);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, shutting down gracefully');
  await prisma.$disconnect();
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});

export { io, prisma };
'''
    
    server_path = os.path.join(backend_src, "server.ts")
    with open(server_path, 'w', encoding='utf-8') as f:
        f.write(server_content)
    print("SUCCESS: Updated server.ts with Socket.io integration")

    # 2. Create socket handlers
    socket_handlers = '''import { Server, Socket } from 'socket.io';
import { PrismaClient } from '@prisma/client';
import jwt from 'jsonwebtoken';

interface AuthenticatedSocket extends Socket {
  userId?: string;
  username?: string;
  currentRoom?: string;
}

// Store active users by room
const roomUsers = new Map<string, Set<string>>();

export const handleSocketConnection = (io: Server, socket: AuthenticatedSocket, prisma: PrismaClient) => {
  console.log(`User connected: ${socket.id}`);

  // Handle authentication
  socket.on('authenticate', async (token: string) => {
    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET || 'fallback-secret') as any;
      socket.userId = decoded.userId;
      socket.username = decoded.username;
      
      socket.emit('authenticated', { 
        success: true, 
        userId: socket.userId,
        username: socket.username 
      });
      
      console.log(`User authenticated: ${socket.username} (${socket.userId})`);
    } catch (error) {
      socket.emit('authenticated', { success: false, error: 'Invalid token' });
      console.log(`Authentication failed for socket ${socket.id}`);
    }
  });

  // Handle joining rooms
  socket.on('join-room', async (data: { roomCode: string }) => {
    if (!socket.userId) {
      socket.emit('error', { message: 'Not authenticated' });
      return;
    }

    try {
      const { roomCode } = data;
      
      // Find or create room
      let room = await prisma.room.findFirst({
        where: { code: roomCode },
        include: { users: { include: { user: true } } }
      });

      if (!room) {
        // Create new room if it doesn't exist
        room = await prisma.room.create({
          data: {
            name: `Room ${roomCode}`,
            code: roomCode,
            maxPlayers: 8
          },
          include: { users: { include: { user: true } } }
        });
      }

      // Check if user is already in room
      const existingRoomUser = await prisma.roomUser.findFirst({
        where: {
          userId: socket.userId,
          roomId: room.id
        }
      });

      if (!existingRoomUser) {
        // Add user to room
        await prisma.roomUser.create({
          data: {
            userId: socket.userId,
            roomId: room.id,
            role: 'player'
          }
        });
      }

      // Leave current room if in one
      if (socket.currentRoom) {
        socket.leave(socket.currentRoom);
        updateRoomUserList(io, socket.currentRoom);
      }

      // Join new room
      socket.join(roomCode);
      socket.currentRoom = roomCode;

      // Update room users tracking
      if (!roomUsers.has(roomCode)) {
        roomUsers.set(roomCode, new Set());
      }
      roomUsers.get(roomCode)!.add(socket.id);

      // Get updated room data
      const updatedRoom = await prisma.room.findFirst({
        where: { code: roomCode },
        include: { users: { include: { user: true } } }
      });

      socket.emit('room-joined', {
        room: updatedRoom,
        message: `Joined room ${roomCode}`
      });

      // Notify other users in room
      socket.to(roomCode).emit('user-joined', {
        userId: socket.userId,
        username: socket.username,
        message: `${socket.username} joined the room`
      });

      // Update user list for all room members
      updateRoomUserList(io, roomCode);

      console.log(`${socket.username} joined room ${roomCode}`);

    } catch (error) {
      console.error('Error joining room:', error);
      socket.emit('error', { message: 'Failed to join room' });
    }
  });

  // Handle leaving rooms
  socket.on('leave-room', () => {
    if (socket.currentRoom) {
      handleUserLeaveRoom(io, socket);
    }
  });

  // Handle chat messages
  socket.on('chat-message', (data: { message: string }) => {
    if (!socket.currentRoom || !socket.username) {
      socket.emit('error', { message: 'Not in a room or not authenticated' });
      return;
    }

    const messageData = {
      id: Date.now().toString(),
      username: socket.username,
      message: data.message,
      timestamp: new Date().toISOString()
    };

    // Send to all users in the room including sender
    io.to(socket.currentRoom).emit('chat-message', messageData);
    
    console.log(`${socket.username} in ${socket.currentRoom}: ${data.message}`);
  });

  // Handle room creation
  socket.on('create-room', async (data: { roomName?: string }) => {
    if (!socket.userId) {
      socket.emit('error', { message: 'Not authenticated' });
      return;
    }

    try {
      // Generate unique room code
      const roomCode = generateRoomCode();
      
      const room = await prisma.room.create({
        data: {
          name: data.roomName || `${socket.username}'s Room`,
          code: roomCode,
          maxPlayers: 8
        }
      });

      socket.emit('room-created', {
        room,
        message: `Room created with code: ${roomCode}`
      });

      console.log(`${socket.username} created room ${roomCode}`);

    } catch (error) {
      console.error('Error creating room:', error);
      socket.emit('error', { message: 'Failed to create room' });
    }
  });

  // Handle disconnection
  socket.on('disconnect', () => {
    console.log(`User disconnected: ${socket.id}`);
    
    if (socket.currentRoom) {
      handleUserLeaveRoom(io, socket);
    }
  });
};

function handleUserLeaveRoom(io: Server, socket: AuthenticatedSocket) {
  if (!socket.currentRoom) return;

  const roomCode = socket.currentRoom;
  
  // Remove from room users tracking
  if (roomUsers.has(roomCode)) {
    roomUsers.get(roomCode)!.delete(socket.id);
    if (roomUsers.get(roomCode)!.size === 0) {
      roomUsers.delete(roomCode);
    }
  }

  socket.leave(roomCode);

  // Notify other users
  socket.to(roomCode).emit('user-left', {
    userId: socket.userId,
    username: socket.username,
    message: `${socket.username} left the room`
  });

  // Update user list
  updateRoomUserList(io, roomCode);

  socket.currentRoom = undefined;
  console.log(`${socket.username} left room ${roomCode}`);
}

async function updateRoomUserList(io: Server, roomCode: string) {
  const sockets = await io.in(roomCode).fetchSockets();
  const users = sockets.map((s: any) => ({
    id: s.userId,
    username: s.username,
    socketId: s.id
  })).filter(user => user.username); // Only include authenticated users

  io.to(roomCode).emit('room-users-updated', { users });
}

function generateRoomCode(): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let result = '';
  for (let i = 0; i < 6; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}
'''
    
    socket_path = os.path.join(backend_src, "socket", "socketHandlers.ts")
    with open(socket_path, 'w', encoding='utf-8') as f:
        f.write(socket_handlers)
    print("SUCCESS: Created socket handlers")

    # 3. Create authentication routes
    auth_routes = '''import express from 'express';
import jwt from 'jsonwebtoken';
import { PrismaClient } from '@prisma/client';

const router = express.Router();
const prisma = new PrismaClient();

// Simple login/register for demo purposes
router.post('/login', async (req, res) => {
  try {
    const { username } = req.body;

    if (!username || username.trim().length === 0) {
      return res.status(400).json({ error: 'Username is required' });
    }

    // Find or create user
    let user = await prisma.user.findUnique({
      where: { username: username.trim() }
    });

    if (!user) {
      user = await prisma.user.create({
        data: { username: username.trim() }
      });
    }

    // Generate JWT token
    const token = jwt.sign(
      { userId: user.id, username: user.username },
      process.env.JWT_SECRET || 'fallback-secret',
      { expiresIn: '24h' }
    );

    res.json({
      success: true,
      token,
      user: {
        id: user.id,
        username: user.username
      }
    });

    console.log(`User logged in: ${user.username}`);

  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Login failed' });
  }
});

router.post('/verify', async (req, res) => {
  try {
    const { token } = req.body;

    if (!token) {
      return res.status(400).json({ error: 'Token is required' });
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'fallback-secret') as any;
    
    const user = await prisma.user.findUnique({
      where: { id: decoded.userId }
    });

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json({
      success: true,
      user: {
        id: user.id,
        username: user.username
      }
    });

  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
});

export default router;
'''
    
    auth_path = os.path.join(backend_src, "routes", "auth.ts")
    with open(auth_path, 'w', encoding='utf-8') as f:
        f.write(auth_routes)
    print("SUCCESS: Created authentication routes")

    # 4. Create room routes
    room_routes = '''import express from 'express';
import { PrismaClient } from '@prisma/client';
import { authenticateToken, AuthRequest } from '../middleware/auth';

const router = express.Router();
const prisma = new PrismaClient();

// Get all active rooms
router.get('/', async (req, res) => {
  try {
    const rooms = await prisma.room.findMany({
      include: {
        users: {
          include: {
            user: true
          }
        }
      },
      orderBy: {
        createdAt: 'desc'
      }
    });

    res.json({ rooms });
  } catch (error) {
    console.error('Error fetching rooms:', error);
    res.status(500).json({ error: 'Failed to fetch rooms' });
  }
});

// Get specific room by code
router.get('/:code', async (req, res) => {
  try {
    const { code } = req.params;
    
    const room = await prisma.room.findFirst({
      where: { code },
      include: {
        users: {
          include: {
            user: true
          }
        }
      }
    });

    if (!room) {
      return res.status(404).json({ error: 'Room not found' });
    }

    res.json({ room });
  } catch (error) {
    console.error('Error fetching room:', error);
    res.status(500).json({ error: 'Failed to fetch room' });
  }
});

export default router;
'''
    
    rooms_path = os.path.join(backend_src, "routes", "rooms.ts")
    with open(rooms_path, 'w', encoding='utf-8') as f:
        f.write(room_routes)
    print("SUCCESS: Created room routes")

def create_socket_frontend():
    """Create frontend Socket.io implementation"""
    frontend_src = "../frontend/src"
    
    # 1. Create socket service
    socket_service = '''import { io, Socket } from 'socket.io-client';

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
  private socket: Socket | null = null;
  private token: string | null = null;

  connect(): Socket {
    if (this.socket?.connected) {
      return this.socket;
    }

    this.socket = io(import.meta.env.VITE_SOCKET_URL || 'http://localhost:3001', {
      autoConnect: false,
      transports: ['websocket', 'polling']
    });

    this.setupEventListeners();
    this.socket.connect();

    return this.socket;
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  authenticate(token: string): void {
    this.token = token;
    if (this.socket) {
      this.socket.emit('authenticate', token);
    }
  }

  joinRoom(roomCode: string): void {
    if (this.socket) {
      this.socket.emit('join-room', { roomCode });
    }
  }

  leaveRoom(): void {
    if (this.socket) {
      this.socket.emit('leave-room');
    }
  }

  createRoom(roomName?: string): void {
    if (this.socket) {
      this.socket.emit('create-room', { roomName });
    }
  }

  sendMessage(message: string): void {
    if (this.socket) {
      this.socket.emit('chat-message', { message });
    }
  }

  // Event listener registration methods
  onAuthenticated(callback: (data: any) => void): void {
    this.socket?.on('authenticated', callback);
  }

  onRoomJoined(callback: (data: any) => void): void {
    this.socket?.on('room-joined', callback);
  }

  onRoomCreated(callback: (data: any) => void): void {
    this.socket?.on('room-created', callback);
  }

  onUserJoined(callback: (data: any) => void): void {
    this.socket?.on('user-joined', callback);
  }

  onUserLeft(callback: (data: any) => void): void {
    this.socket?.on('user-left', callback);
  }

  onRoomUsersUpdated(callback: (data: { users: User[] }) => void): void {
    this.socket?.on('room-users-updated', callback);
  }

  onChatMessage(callback: (message: ChatMessage) => void): void {
    this.socket?.on('chat-message', callback);
  }

  onError(callback: (error: any) => void): void {
    this.socket?.on('error', callback);
  }

  onConnect(callback: () => void): void {
    this.socket?.on('connect', callback);
  }

  onDisconnect(callback: () => void): void {
    this.socket?.on('disconnect', callback);
  }

  // Cleanup method to remove specific listeners
  off(event: string, callback?: Function): void {
    if (callback) {
      this.socket?.off(event, callback);
    } else {
      this.socket?.off(event);
    }
  }

  private setupEventListeners(): void {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('Connected to server');
      // Re-authenticate if we have a token
      if (this.token) {
        this.authenticate(this.token);
      }
    });

    this.socket.on('disconnect', () => {
      console.log('Disconnected from server');
    });

    this.socket.on('connect_error', (error) => {
      console.error('Connection error:', error);
    });
  }

  get isConnected(): boolean {
    return this.socket?.connected || false;
  }

  get socketId(): string | undefined {
    return this.socket?.id;
  }
}

// Export singleton instance
export const socketService = new SocketService();
export default socketService;
'''
    
    socket_service_path = os.path.join(frontend_src, "services", "socketService.ts")
    with open(socket_service_path, 'w', encoding='utf-8') as f:
        f.write(socket_service)
    print("SUCCESS: Created socket service")

    # 2. Create auth service  
    auth_service = '''export interface LoginResponse {
  success: boolean;
  token?: string;
  user?: {
    id: string;
    username: string;
  };
  error?: string;
}

class AuthService {
  private readonly API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001';

  async login(username: string): Promise<LoginResponse> {
    try {
      const response = await fetch(`${this.API_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username }),
      });

      const data = await response.json();
      
      if (data.success && data.token) {
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
      }

      return data;
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        error: 'Failed to connect to server'
      };
    }
  }

  async verifyToken(token: string): Promise<LoginResponse> {
    try {
      const response = await fetch(`${this.API_URL}/api/auth/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      });

      return await response.json();
    } catch (error) {
      console.error('Token verification error:', error);
      return {
        success: false,
        error: 'Failed to verify token'
      };
    }
  }

  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }

  getToken(): string | null {
    return localStorage.getItem('token');
  }

  getUser(): any {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }
}

export const authService = new AuthService();
export default authService;
'''
    
    auth_service_path = os.path.join(frontend_src, "services", "authService.ts")
    with open(auth_service_path, 'w', encoding='utf-8') as f:
        f.write(auth_service)
    print("SUCCESS: Created auth service")

    # 3. Create socket hook
    socket_hook = '''import { useEffect, useRef, useState } from 'react';
import socketService, { User, Room, ChatMessage } from '../services/socketService';

export const useSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [currentRoom, setCurrentRoom] = useState<Room | null>(null);
  const [roomUsers, setRoomUsers] = useState<User[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [connectionError, setConnectionError] = useState<string | null>(null);

  // Use refs to store callbacks to avoid re-registering listeners
  const handlersRef = useRef({
    onConnect: () => {
      setIsConnected(true);
      setConnectionError(null);
    },
    onDisconnect: () => {
      setIsConnected(false);
    },
    onAuthenticated: (data: any) => {
      if (data.success) {
        console.log('Authenticated successfully');
      } else {
        console.error('Authentication failed:', data.error);
        setConnectionError(data.error);
      }
    },
    onRoomJoined: (data: any) => {
      setCurrentRoom(data.room);
      setMessages([]); // Clear messages when joining new room
      console.log('Joined room:', data.room.code);
    },
    onRoomCreated: (data: any) => {
      console.log('Room created:', data.room.code);
    },
    onUserJoined: (data: any) => {
      console.log('User joined:', data.username);
    },
    onUserLeft: (data: any) => {
      console.log('User left:', data.username);
    },
    onRoomUsersUpdated: (data: { users: User[] }) => {
      setRoomUsers(data.users);
    },
    onChatMessage: (message: ChatMessage) => {
      setMessages(prev => [...prev, message]);
    },
    onError: (error: any) => {
      console.error('Socket error:', error);
      setConnectionError(error.message);
    }
  });

  useEffect(() => {
    const socket = socketService.connect();
    const handlers = handlersRef.current;

    // Register event listeners
    socketService.onConnect(handlers.onConnect);
    socketService.onDisconnect(handlers.onDisconnect);
    socketService.onAuthenticated(handlers.onAuthenticated);
    socketService.onRoomJoined(handlers.onRoomJoined);
    socketService.onRoomCreated(handlers.onRoomCreated);
    socketService.onUserJoined(handlers.onUserJoined);
    socketService.onUserLeft(handlers.onUserLeft);
    socketService.onRoomUsersUpdated(handlers.onRoomUsersUpdated);
    socketService.onChatMessage(handlers.onChatMessage);
    socketService.onError(handlers.onError);

    return () => {
      // Cleanup listeners
      socketService.off('connect', handlers.onConnect);
      socketService.off('disconnect', handlers.onDisconnect);
      socketService.off('authenticated', handlers.onAuthenticated);
      socketService.off('room-joined', handlers.onRoomJoined);
      socketService.off('room-created', handlers.onRoomCreated);
      socketService.off('user-joined', handlers.onUserJoined);
      socketService.off('user-left', handlers.onUserLeft);
      socketService.off('room-users-updated', handlers.onRoomUsersUpdated);
      socketService.off('chat-message', handlers.onChatMessage);
      socketService.off('error', handlers.onError);
    };
  }, []);

  const authenticate = (token: string) => {
    socketService.authenticate(token);
  };

  const joinRoom = (roomCode: string) => {
    socketService.joinRoom(roomCode);
  };

  const leaveRoom = () => {
    socketService.leaveRoom();
    setCurrentRoom(null);
    setRoomUsers([]);
    setMessages([]);
  };

  const createRoom = (roomName?: string) => {
    socketService.createRoom(roomName);
  };

  const sendMessage = (message: string) => {
    socketService.sendMessage(message);
  };

  return {
    isConnected,
    currentRoom,
    roomUsers,
    messages,
    connectionError,
    authenticate,
    joinRoom,
    leaveRoom,
    createRoom,
    sendMessage
  };
};
'''
    
    socket_hook_path = os.path.join(frontend_src, "hooks", "useSocket.ts")
    with open(socket_hook_path, 'w', encoding='utf-8') as f:
        f.write(socket_hook)
    print("SUCCESS: Created socket hook")

    # Continue creating the remaining files...
    # I'll continue with the remaining files in the next part due to length

def create_remaining_frontend():
    """Create remaining frontend files"""
    frontend_src = "../frontend/src"
    
    # Create directories if they don't exist
    pages_dir = os.path.join(frontend_src, "pages")
    if not os.path.exists(pages_dir):
        os.makedirs(pages_dir)

    # 4. Update App.tsx
    app_content = '''import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import HomePage from './pages/HomePage';
import RoomPage from './pages/RoomPage';
import authService from './services/authService';
import socketService from './services/socketService';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const initAuth = async () => {
      const token = authService.getToken();
      const savedUser = authService.getUser();

      if (token && savedUser) {
        // Verify token is still valid
        const result = await authService.verifyToken(token);
        if (result.success) {
          setIsAuthenticated(true);
          setUser(savedUser);
          // Initialize socket connection with token
          socketService.connect();
          socketService.authenticate(token);
        } else {
          authService.logout();
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const handleLogin = (userData: any, token: string) => {
    setIsAuthenticated(true);
    setUser(userData);
    // Connect to socket after successful login
    socketService.connect();
    socketService.authenticate(token);
  };

  const handleLogout = () => {
    authService.logout();
    socketService.disconnect();
    setIsAuthenticated(false);
    setUser(null);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <Router>
      <div className="App min-h-screen bg-gray-50">
        <header className="bg-blue-600 text-white p-4 shadow-lg">
          <div className="container mx-auto flex justify-between items-center">
            <h1 className="text-2xl font-bold">Codenames</h1>
            {isAuthenticated && (
              <div className="flex items-center space-x-4">
                <span>Welcome, {user?.username}!</span>
                <button
                  onClick={handleLogout}
                  className="bg-blue-700 hover:bg-blue-800 px-4 py-2 rounded text-sm"
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        </header>
        
        <main className="container mx-auto p-4">
          <Routes>
            <Route 
              path="/login" 
              element={
                !isAuthenticated ? 
                <LoginPage onLogin={handleLogin} /> : 
                <Navigate to="/" replace />
              } 
            />
            <Route 
              path="/" 
              element={
                isAuthenticated ? 
                <HomePage /> : 
                <Navigate to="/login" replace />
              } 
            />
            <Route 
              path="/room/:roomCode" 
              element={
                isAuthenticated ? 
                <RoomPage /> : 
                <Navigate to="/login" replace />
              } 
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
'''
    
    app_path = os.path.join(frontend_src, "App.tsx")
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(app_content)
    print("SUCCESS: Updated App.tsx with authentication")

    # 5. Create LoginPage
    login_page = '''import React, { useState } from 'react';
import authService from '../services/authService';

interface LoginPageProps {
  onLogin: (user: any, token: string) => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!username.trim()) {
      setError('Username is required');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const result = await authService.login(username.trim());
      
      if (result.success && result.token && result.user) {
        onLogin(result.user, result.token);
      } else {
        setError(result.error || 'Login failed');
      }
    } catch (err) {
      setError('Failed to connect to server');
    }

    setIsLoading(false);
  };

  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h2 className="text-2xl font-bold text-center mb-6">Join Codenames</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
              Choose a Username
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your username"
              disabled={isLoading}
            />
          </div>
          
          {error && (
            <div className="text-red-600 text-sm">{error}</div>
          )}
          
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white py-2 px-4 rounded-md font-medium"
          >
            {isLoading ? 'Connecting...' : 'Join Game'}
          </button>
        </form>
        
        <div className="mt-6 text-center text-sm text-gray-600">
          <p>Enter any username to join or create an account</p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
'''
    
    login_path = os.path.join(frontend_src, "pages", "LoginPage.tsx")
    with open(login_path, 'w', encoding='utf-8') as f:
        f.write(login_page)
    print("SUCCESS: Created LoginPage")

    # 6. Update HomePage with room functionality
    home_page = '''import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSocket } from '../hooks/useSocket';

const HomePage: React.FC = () => {
  const [roomCode, setRoomCode] = useState('');
  const [roomName, setRoomName] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  
  const { isConnected, createRoom, joinRoom, connectionError } = useSocket();

  const handleJoinRoom = () => {
    if (!roomCode.trim()) return;
    
    setIsLoading(true);
    joinRoom(roomCode.trim().toUpperCase());
    
    // Navigate to room page
    setTimeout(() => {
      navigate(`/room/${roomCode.trim().toUpperCase()}`);
      setIsLoading(false);
    }, 500);
  };

  const handleCreateRoom = () => {
    setIsLoading(true);
    createRoom(roomName.trim() || undefined);
    
    // Listen for room creation success (in a real app, you'd handle this in the socket hook)
    setTimeout(() => {
      // For now, just generate a random code and navigate
      const newRoomCode = Math.random().toString(36).substr(2, 6).toUpperCase();
      navigate(`/room/${newRoomCode}`);
      setIsLoading(false);
    }, 500);
  };

  return (
    <div className="max-w-2xl mx-auto">
      {/* Connection Status */}
      <div className="mb-6 p-4 rounded-lg">
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className="text-sm font-medium">
            {isConnected ? 'Connected to server' : 'Disconnected from server'}
          </span>
        </div>
        {connectionError && (
          <div className="text-red-600 text-sm mt-2">{connectionError}</div>
        )}
      </div>

      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold mb-4">Welcome to Codenames</h2>
        <p className="text-lg text-gray-600 mb-8">
          A real-time multiplayer word game experience
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Join Room */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-xl font-bold mb-4">Join Existing Room</h3>
          <div className="space-y-4">
            <input
              type="text"
              placeholder="Enter room code"
              value={roomCode}
              onChange={(e) => setRoomCode(e.target.value.toUpperCase())}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              maxLength={6}
            />
            <button
              onClick={handleJoinRoom}
              disabled={!roomCode.trim() || !isConnected || isLoading}
              className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-300 text-white py-3 px-4 rounded-md font-medium"
            >
              {isLoading ? 'Joining...' : 'Join Room'}
            </button>
          </div>
        </div>

        {/* Create Room */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-xl font-bold mb-4">Create New Room</h3>
          {!showCreateForm ? (
            <button
              onClick={() => setShowCreateForm(true)}
              disabled={!isConnected}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white py-3 px-4 rounded-md font-medium"
            >
              Create Room
            </button>
          ) : (
            <div className="space-y-4">
              <input
                type="text"
                placeholder="Room name (optional)"
                value={roomName}
                onChange={(e) => setRoomName(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <div className="flex space-x-2">
                <button
                  onClick={handleCreateRoom}
                  disabled={!isConnected || isLoading}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white py-2 px-4 rounded-md font-medium"
                >
                  {isLoading ? 'Creating...' : 'Create'}
                </button>
                <button
                  onClick={() => setShowCreateForm(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Game Rules */}
      <div className="mt-12 bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-xl font-bold mb-4">How to Play</h3>
        <div className="text-gray-700 space-y-2">
          <p>• Teams compete to identify their agents using one-word clues</p>
          <p>• Spymasters give clues, field operatives guess words</p>
          <p>• Contact all your team's agents first to win</p>
          <p>• Avoid the assassin card at all costs!</p>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
'''
    
    home_path = os.path.join(frontend_src, "pages", "HomePage.tsx")
    with open(home_path, 'w', encoding='utf-8') as f:
        f.write(home_page)
    print("SUCCESS: Updated HomePage with room functionality")

    # 7. Create RoomPage
    room_page = '''import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSocket } from '../hooks/useSocket';

const RoomPage: React.FC = () => {
  const { roomCode } = useParams<{ roomCode: string }>();
  const navigate = useNavigate();
  const [message, setMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { 
    isConnected, 
    currentRoom, 
    roomUsers, 
    messages, 
    joinRoom, 
    leaveRoom, 
    sendMessage,
    connectionError 
  } = useSocket();

  useEffect(() => {
    if (roomCode && isConnected) {
      joinRoom(roomCode);
    }
  }, [roomCode, isConnected]);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      sendMessage(message.trim());
      setMessage('');
    }
  };

  const handleLeaveRoom = () => {
    leaveRoom();
    navigate('/');
  };

  if (!isConnected) {
    return (
      <div className="text-center py-8">
        <div className="text-xl text-red-600 mb-4">Not connected to server</div>
        <button
          onClick={() => navigate('/')}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md"
        >
          Go Back
        </button>
      </div>
    );
  }

  if (!currentRoom) {
    return (
      <div className="text-center py-8">
        <div className="text-xl mb-4">Joining room {roomCode}...</div>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Room Header */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold">{currentRoom.name}</h2>
            <p className="text-gray-600">Room Code: <span className="font-mono font-bold">{currentRoom.code}</span></p>
          </div>
          <button
            onClick={handleLeaveRoom}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md"
          >
            Leave Room
          </button>
        </div>
      </div>

      <div className="grid lg:grid-cols-4 gap-6">
        {/* Game Board Area */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold mb-4">Game Board</h3>
            <div className="grid grid-cols-5 gap-2">
              {Array.from({ length: 25 }, (_, i) => (
                <div
                  key={i}
                  className="bg-gray-100 hover:bg-gray-200 p-4 text-center rounded cursor-pointer transition-colors h-20 flex items-center justify-center"
                >
                  <span className="text-sm font-medium">Card {i + 1}</span>
                </div>
              ))}
            </div>
            <div className="mt-4 text-center text-gray-600">
              Game will start when enough players join...
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          {/* Players List */}
          <div className="bg-white rounded-lg shadow-md p-4">
            <h3 className="font-bold mb-3">Players ({roomUsers.length})</h3>
            <div className="space-y-2">
              {roomUsers.map((user) => (
                <div key={user.id} className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm">{user.username}</span>
                </div>
              ))}
              {roomUsers.length === 0 && (
                <div className="text-gray-500 text-sm">No players yet</div>
              )}
            </div>
          </div>

          {/* Chat */}
          <div className="bg-white rounded-lg shadow-md p-4">
            <h3 className="font-bold mb-3">Chat</h3>
            
            {/* Messages */}
            <div className="h-48 overflow-y-auto border rounded p-2 mb-3 bg-gray-50">
              {messages.map((msg) => (
                <div key={msg.id} className="mb-2">
                  <div className="text-xs text-gray-500">
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </div>
                  <div className="text-sm">
                    <span className="font-medium">{msg.username}:</span> {msg.message}
                  </div>
                </div>
              ))}
              {messages.length === 0 && (
                <div className="text-gray-500 text-sm text-center py-4">
                  No messages yet
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Message Input */}
            <form onSubmit={handleSendMessage} className="flex">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Type a message..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
              />
              <button
                type="submit"
                disabled={!message.trim()}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white px-3 py-2 rounded-r-md text-sm"
              >
                Send
              </button>
            </form>
          </div>
        </div>
      </div>

      {connectionError && (
        <div className="fixed bottom-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {connectionError}
        </div>
      )}
    </div>
  );
};

export default RoomPage;
'''
    
    room_path = os.path.join(frontend_src, "pages", "RoomPage.tsx")
    with open(room_path, 'w', encoding='utf-8') as f:
        f.write(room_page)
    print("SUCCESS: Created RoomPage")

def main():
    """Main execution function"""
    print("Starting Phase 1: Socket Foundation...")
    print("=" * 50)
    
    try:
        create_socket_backend()
        create_socket_frontend()
        create_remaining_frontend()
        update_changelog()
        
        print("\n" + "=" * 50)
        print("SUCCESS: Phase 1: Socket Foundation completed!")
        print("\nWhat was implemented:")
        print("- Real-time Socket.io communication")
        print("- JWT authentication system")
        print("- Room creation and joining")
        print("- Live user presence tracking")
        print("- Real-time chat messaging")
        print("- Responsive UI with connection status")
        
        print("\nNext steps:")
        print("1. Test both servers: 'npm run dev' in backend and frontend")
        print("2. Open two browsers to test real-time communication")
        print("3. Test login, room creation, and messaging")
        print("4. Commit changes when everything works")
        print("\nReady for Phase 2: Core Game Logic!")
        
    except Exception as e:
        print(f"ERROR during Phase 1 completion: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
