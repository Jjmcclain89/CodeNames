import express from 'express';
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
