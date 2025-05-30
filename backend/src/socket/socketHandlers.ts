import { Server, Socket } from 'socket.io';
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
