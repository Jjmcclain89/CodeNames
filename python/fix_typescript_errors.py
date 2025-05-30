#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix TypeScript Errors
Fixes TypeScript compilation errors in backend
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
                    new_section = "\n### Python Scripts Run\n- TypeScript fix: Fixed compilation errors in backend\n"
                    content = content[:insert_point] + new_section + content[insert_point:]
        else:
            section_start = content.find("### Python Scripts Run")
            section_end = content.find("\n###", section_start + 1)
            if section_end == -1:
                section_end = content.find("\n## ", section_start + 1)
            
            entry = f"- TypeScript fix: Fixed compilation errors ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n"
            
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

def fix_backend_typescript():
    """Fix TypeScript compilation errors"""
    print("🔧 Fixing TypeScript compilation errors...")
    
    index_path = Path("backend/src/index.ts")
    
    # TypeScript-compliant server code
    fixed_server_content = '''import express, { Request, Response, NextFunction } from 'express';
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

// ========================================
// API ROUTES - INLINE FOR DEBUGGING
// ========================================

// Health check endpoint
app.get('/api/health', (req: Request, res: Response): void => {
  console.log('🏥 Health check endpoint called');
  res.json({ 
    status: 'OK', 
    message: 'Codenames backend server is running',
    timestamp: new Date().toISOString(),
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
    
    // Simple token (not JWT for now, just for Phase 1)
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
// SOCKET.IO SETUP
// ========================================

const io = new Server(server, {
  cors: corsOptions,
  transports: ['websocket', 'polling']
});

// Simple socket handlers for Phase 1
io.on('connection', (socket) => {
  console.log('📡 Socket connected:', socket.id);
  
  socket.on('authenticate', (token: string) => {
    console.log('🔐 Socket authentication attempt with token:', token);
    
    // Find user by token
    let foundUser = null;
    for (const [userId, userData] of users.entries()) {
      if (userData.token === token) {
        foundUser = userData;
        break;
      }
    }
    
    if (foundUser) {
      socket.emit('authenticated', { success: true, user: foundUser });
      console.log('✅ Socket authenticated for:', foundUser.username);
    } else {
      socket.emit('authenticated', { success: false, error: 'Invalid token' });
      console.log('❌ Socket authentication failed');
    }
  });
  
  socket.on('disconnect', () => {
    console.log('📡 Socket disconnected:', socket.id);
  });
});

console.log('📡 Socket.io configured');

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
  console.log('📡 Socket.io enabled');
  console.log(`🔗 API endpoints: http://localhost:${PORT}/api`);
  console.log(`🏥 Health check: http://localhost:${PORT}/api/health`);
  console.log('🎉 ================================');
  console.log('');
});

export default app;
'''
    
    # Write the fixed server file
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(fixed_server_content)
    
    print("✅ Fixed TypeScript compilation errors")

def main():
    """Main execution function"""
    print("🔧 Fixing TypeScript Compilation Errors")
    print("=" * 45)
    
    try:
        # Fix the TypeScript errors
        fix_backend_typescript()
        
        # Update changelog
        add_changelog_entry()
        
        print("\n🎉 TypeScript Errors Fixed!")
        print("=" * 45)
        
        print("\n📋 What was fixed:")
        print("✅ Added explicit return types for all route handlers")
        print("✅ Fixed error type handling in catch blocks")
        print("✅ Added proper TypeScript types for Express parameters")
        print("✅ Added explicit return statements where needed")
        print("✅ Imported proper types from Express")
        
        print("\n🔧 Next steps:")
        print("1. RESTART your backend server:")
        print("   cd backend && npm run dev")
        print("2. Should start without TypeScript errors")
        print("3. Look for the startup success messages")
        print("4. Test health check: http://localhost:3001/api/health")
        
        print("\n🎯 Expected results:")
        print("- No TypeScript compilation errors")
        print("- Server starts successfully with logs")
        print("- Health check returns JSON response")
        print("- API test on debug page should work")
        
        return 0
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
