import express, { Request, Response } from 'express';

const router = express.Router();

// Define proper TypeScript interfaces
interface RoomPlayer {
  id: string;
  username: string;
  team: string;
  role: string;
  isOnline: boolean;
  isOwner: boolean;
}

interface Room {
  id: string;
  code: string;
  owner: string;
  players: RoomPlayer[];
  status: string;
  createdAt: string;
  updatedAt: string;
}

// In-memory storage for rooms (separate from games)
const rooms = new Map<string, Room>();

// Generate room code
function generateRoomCode(): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let code = '';
  for (let i = 0; i < 6; i++) {
    code += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  
  if (rooms.has(code)) {
    return generateRoomCode(); // Try again if exists
  }
  
  return code;
}

// Create room
router.post('/create', (req: Request, res: Response): void => {
  try {
    console.log('🏠 Creating new room...');
    
    const { userId, username } = req.body;
    const roomCode = generateRoomCode();
    
    const room: Room = {
      id: roomCode,
      code: roomCode,
      owner: userId || 'anonymous',
      players: [],
      status: 'waiting',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    // Add creator as first player
    if (username && userId) {
      room.players.push({
        id: userId,
        username,
        team: 'neutral',
        role: 'operative',
        isOnline: true,
        isOwner: true
      });
    }
    
    rooms.set(roomCode, room);
    
    console.log(`✅ Created room: ${roomCode}`);
    
    res.json({ 
      success: true, 
      roomCode: roomCode,
      message: 'Room created successfully!',
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ Error creating room:', error);
    res.status(500).json({ 
      success: false,
      error: 'Failed to create room',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Join room
router.post('/join', (req: Request, res: Response): void => {
  try {
    const { roomCode, userId, username } = req.body;
    console.log(`🚪 User ${username} joining room: ${roomCode}`);
    
    if (!roomCode) {
      res.status(400).json({ 
        success: false,
        error: 'Room code is required' 
      });
      return;
    }
    
    const room = rooms.get(roomCode.toUpperCase());
    
    if (!room) {
      res.status(404).json({ 
        success: false,
        error: 'Room not found' 
      });
      return;
    }
    
    // Add player to room if not already there
    if (username && userId) {
      const existingPlayer = room.players.find((p: RoomPlayer) => p.id === userId);
      if (!existingPlayer) {
        room.players.push({
          id: userId,
          username,
          team: 'neutral',
          role: 'operative',
          isOnline: true,
          isOwner: false
        });
        room.updatedAt = new Date().toISOString();
        console.log(`✅ Added ${username} to room ${roomCode}`);
      }
    }
    
    res.json({ 
      success: true, 
      roomCode: roomCode.toUpperCase(),
      message: 'Joined room successfully!',
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ Error joining room:', error);
    res.status(500).json({ 
      success: false,
      error: 'Failed to join room',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Get room info
router.get('/:roomCode', (req: Request, res: Response): void => {
  try {
    const { roomCode } = req.params;
    console.log(`🔍 Getting room info: ${roomCode}`);
    
    if (!roomCode) {
      res.status(400).json({ 
        success: false,
        error: 'Room code is required' 
      });
      return;
    }
    
    const room = rooms.get(roomCode.toUpperCase());
    
    if (room) {
      res.json({ 
        success: true, 
        room: room,
        timestamp: new Date().toISOString()
      });
    } else {
      res.status(404).json({ 
        success: false,
        error: 'Room not found' 
      });
    }
    
  } catch (error) {
    console.error('❌ Error getting room info:', error);
    res.status(500).json({ 
      success: false,
      error: 'Failed to get room info',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// List all rooms
router.get('/', (req: Request, res: Response): void => {
  try {
    console.log('📋 Listing all rooms...');
    
    const activeRooms = Array.from(rooms.values()).map(room => ({
      code: room.code,
      id: room.id,
      status: room.status,
      playerCount: room.players.length,
      players: room.players.map((p: RoomPlayer) => p.username),
      createdAt: room.createdAt,
      lastActivity: room.updatedAt
    }));
    
    // Sort by most recent activity
    activeRooms.sort((a, b) => 
      new Date(b.lastActivity).getTime() - new Date(a.lastActivity).getTime()
    );
    
    res.json({
      success: true,
      rooms: activeRooms,
      total: rooms.size,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ Error listing rooms:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to list rooms',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

export default router;
export { rooms, Room, RoomPlayer };