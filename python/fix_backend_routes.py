#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Backend API Routes
Checks and fixes API route mounting issues causing 404 errors
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def add_changelog_entry():
    """Add entry to CHANGELOG.md"""
    try:
        changelog_path = Path("CHANGELOG.md")
        if not changelog_path.exists():
            print("Warning: CHANGELOG.md not found")
            return
            
        # Read current changelog
        with open(changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the Python Scripts section
        if "### Python Scripts Run" not in content:
            # Add the section if it doesn't exist
            unreleased_section = content.find("## [Unreleased]")
            if unreleased_section != -1:
                insert_point = content.find("### Added", unreleased_section)
                if insert_point != -1:
                    new_section = "\n### Python Scripts Run\n- Backend route fix: Fixed API route mounting and 404 errors\n"
                    content = content[:insert_point] + new_section + content[insert_point:]
                else:
                    # Add after [Unreleased] header
                    insert_point = content.find("\n", unreleased_section) + 1
                    new_section = "\n### Python Scripts Run\n- Backend route fix: Fixed API route mounting and 404 errors\n"
                    content = content[:insert_point] + new_section + content[insert_point:]
        else:
            # Add to existing section
            section_start = content.find("### Python Scripts Run")
            section_end = content.find("\n###", section_start + 1)
            if section_end == -1:
                section_end = content.find("\n## ", section_start + 1)
            
            entry = f"- Backend route fix: Fixed API route mounting and 404s ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n"
            
            if section_end != -1:
                insert_point = section_end
                content = content[:insert_point] + entry + content[insert_point:]
            else:
                content += entry
        
        # Write back to changelog
        with open(changelog_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Updated CHANGELOG.md")
        
    except Exception as e:
        print(f"⚠️ Could not update CHANGELOG.md: {e}")

def read_file_safely(file_path):
    """Read a file safely with proper encoding"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def check_backend_structure():
    """Check current backend file structure"""
    print("🔍 Checking backend structure...")
    
    backend_files = {
        "server.ts": Path("backend/src/server.ts"),
        "index.ts": Path("backend/src/index.ts"), 
        "auth.ts": Path("backend/src/routes/auth.ts"),
        "rooms.ts": Path("backend/src/routes/rooms.ts")
    }
    
    found_files = {}
    missing_files = []
    
    for name, path in backend_files.items():
        if path.exists():
            found_files[name] = path
            print(f"✅ Found: {name}")
        else:
            missing_files.append(name)
            print(f"❌ Missing: {name}")
    
    return found_files, missing_files

def fix_main_server_file():
    """Fix the main server entry point to properly mount routes"""
    print("\n🔧 Fixing main server file...")
    
    # Check which file is the main entry point
    server_path = Path("backend/src/server.ts")
    index_path = Path("backend/src/index.ts")
    
    main_file_path = None
    if server_path.exists():
        main_file_path = server_path
        print("Using server.ts as main file")
    elif index_path.exists():
        main_file_path = index_path
        print("Using index.ts as main file")
    else:
        print("❌ No main server file found!")
        return False
    
    # Create a proper server setup with routes mounted
    fixed_server_content = '''import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'path';

// Import routes
import authRoutes from './routes/auth';
import roomRoutes from './routes/rooms';

// Import socket handlers
import { setupSocketHandlers } from './socket/socketHandlers';

// Load environment variables
dotenv.config();

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

// API Routes - This is the key fix!
app.use('/api/auth', authRoutes);
app.use('/api/rooms', roomRoutes);

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    message: 'Codenames backend server is running',
    timestamp: new Date().toISOString()
  });
});

// Socket.io setup
const io = new Server(server, {
  cors: corsOptions,
  transports: ['websocket', 'polling']
});

// Setup socket event handlers
setupSocketHandlers(io);

// Error handling middleware
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Server error:', err);
  res.status(500).json({ 
    success: false, 
    error: 'Internal server error',
    message: err.message 
  });
});

// 404 handler for API routes
app.use('/api/*', (req, res) => {
  console.log(`❌ API route not found: ${req.method} ${req.path}`);
  res.status(404).json({ 
    success: false, 
    error: 'API endpoint not found',
    path: req.path,
    method: req.method
  });
});

const PORT = process.env.PORT || 3001;

server.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`📡 Socket.io enabled`);
  console.log(`🔗 API endpoints available at http://localhost:${PORT}/api`);
  console.log(`🏥 Health check: http://localhost:${PORT}/api/health`);
});

export default app;
'''
    
    # Write the fixed server file
    with open(main_file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_server_content)
    
    print(f"✅ Fixed {main_file_path.name} with proper route mounting")
    return True

def enhance_auth_routes():
    """Enhance auth routes with better error handling"""
    print("\n🔧 Enhancing auth routes...")
    
    auth_path = Path("backend/src/routes/auth.ts")
    if not auth_path.exists():
        print("❌ Auth routes file not found!")
        return False
    
    # Enhanced auth routes
    enhanced_auth_routes = '''import express from 'express';
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
'''
    
    with open(auth_path, 'w', encoding='utf-8') as f:
        f.write(enhanced_auth_routes)
    
    print("✅ Enhanced auth routes with better error handling and logging")
    return True

def create_backend_package_json_check():
    """Check if backend has all required dependencies"""
    print("\n🔧 Checking backend dependencies...")
    
    package_json_path = Path("backend/package.json")
    if not package_json_path.exists():
        print("❌ Backend package.json not found!")
        return False
    
    # Read package.json
    with open(package_json_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_deps = ['express', 'socket.io', 'cors', 'jsonwebtoken', 'zod', 'dotenv']
    missing_deps = []
    
    for dep in required_deps:
        if f'"{dep}"' not in content:
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"⚠️ Missing dependencies: {missing_deps}")
        print("Run: npm install " + " ".join(missing_deps))
    else:
        print("✅ All required dependencies found")
    
    return True

def main():
    """Main execution function"""
    print("🔧 Fixing Backend API Routes")
    print("=" * 40)
    
    try:
        # Ensure we're in the project root
        if not Path("backend").exists():
            print("❌ Error: Please run this script from the project root directory")
            sys.exit(1)
        
        # Check backend structure
        found_files, missing_files = check_backend_structure()
        
        # Fix main server file
        if not fix_main_server_file():
            print("❌ Failed to fix main server file")
            return 1
        
        # Enhance auth routes
        if not enhance_auth_routes():
            print("❌ Failed to enhance auth routes")
            return 1
        
        # Check dependencies
        create_backend_package_json_check()
        
        # Update changelog
        add_changelog_entry()
        
        print("\n🎉 Backend API Routes Fixed!")
        print("=" * 40)
        
        print("\n📋 Changes made:")
        print("✅ Fixed main server file to properly mount API routes")
        print("✅ Enhanced auth routes with better error handling")
        print("✅ Added health check endpoint (/api/health)")
        print("✅ Added test endpoint (/api/auth/test)")
        print("✅ Improved error logging and debugging")
        
        print("\n🔧 Next steps:")
        print("1. Restart your backend server:")
        print("   cd backend && npm run dev")
        print("2. Test the health check: http://localhost:3001/api/health")
        print("3. Go back to debug page and test API connection")
        print("4. Check backend console for detailed logs")
        
        print("\n🎯 Expected results:")
        print("- API test should now succeed")
        print("- You should see detailed logs in backend console")
        print("- Health check should return server status")
        
        return 0
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
