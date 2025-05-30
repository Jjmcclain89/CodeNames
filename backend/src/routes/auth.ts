import express from 'express';
import jwt from 'jsonwebtoken';
import { z } from 'zod';

const router = express.Router();

// Request validation schemas
const loginSchema = z.object({
  username: z.string().min(1, 'Username is required').max(50, 'Username too long')
});

const verifySchema = z.object({
  token: z.string().min(1, 'Token is required')
});

// Login endpoint
router.post('/login', async (req, res) => {
  try {
    console.log('🔑 Login attempt:', req.body);
    
    // Validate request body
    const { username } = loginSchema.parse(req.body);
    
    // For Phase 1, we'll create a simple user without database
    const user = {
      id: `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      username: username.trim(),
      createdAt: new Date().toISOString()
    };
    
    // Generate JWT token
    const token = jwt.sign(
      { userId: user.id, username: user.username },
      process.env.JWT_SECRET || 'dev-secret-key',
      { expiresIn: '24h' }
    );
    
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
    
    if (error instanceof z.ZodError) {
      return res.status(400).json({
        success: false,
        error: 'Invalid input',
        details: error.errors
      });
    }
    
    res.status(500).json({
      success: false,
      error: 'Login failed',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Token verification endpoint
router.post('/verify', async (req, res) => {
  try {
    console.log('🔍 Token verification attempt');
    
    // Validate request body
    const { token } = verifySchema.parse(req.body);
    
    // Verify JWT token
    const decoded = jwt.verify(
      token, 
      process.env.JWT_SECRET || 'dev-secret-key'
    ) as any;
    
    console.log('✅ Token verification successful for:', decoded.username);
    
    res.json({
      success: true,
      user: {
        id: decoded.userId,
        username: decoded.username
      }
    });
    
  } catch (error) {
    console.error('❌ Token verification error:', error);
    
    if (error instanceof jwt.JsonWebTokenError) {
      return res.status(401).json({
        success: false,
        error: 'Invalid token'
      });
    }
    
    if (error instanceof z.ZodError) {
      return res.status(400).json({
        success: false,
        error: 'Invalid input',
        details: error.errors
      });
    }
    
    res.status(500).json({
      success: false,
      error: 'Token verification failed',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Test endpoint for debugging
router.get('/test', (req, res) => {
  console.log('🧪 Auth test endpoint called');
  res.json({
    success: true,
    message: 'Auth routes are working!',
    timestamp: new Date().toISOString(),
    endpoints: [
      'POST /api/auth/login',
      'POST /api/auth/verify',
      'GET /api/auth/test'
    ]
  });
});

export default router;
