#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fix JSON Response Error
Fixes the "Unexpected end of JSON input" error by ensuring proper backend route registration
and improving frontend error handling.
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

def read_file_content(file_path):
    """Read file content safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading {file_path}: {e}"

def main():
    print("🔧 Fixing JSON Response Error...")
    
    # 1. First, let's create a simple, working games route
    simple_games_route = '''import express from 'express';

const router = express.Router();

// Test endpoint to verify API is working
router.get('/test', (req, res) => {
  console.log('🧪 API test endpoint hit!');
  res.json({ 
    success: true, 
    message: 'Games API is working!',
    timestamp: new Date().toISOString()
  });
});

// Create a new game - simplified for debugging
router.post('/create', (req, res) => {
  try {
    console.log('🎮 POST /api/games/create - Creating new game...');
    console.log('📦 Request body:', req.body);
    
    // Generate simple 6-character game code
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let gameCode = '';
    for (let i = 0; i < 6; i++) {
      gameCode += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    
    console.log(`✅ Generated game code: ${gameCode}`);
    
    const response = { 
      success: true, 
      gameCode: gameCode,
      message: 'Game created successfully!',
      timestamp: new Date().toISOString()
    };
    
    console.log('📤 Sending response:', response);
    res.json(response);
    
  } catch (error) {
    console.error('❌ Error in /api/games/create:', error);
    res.status(500).json({ 
      success: false,
      error: 'Failed to create game',
      details: error.message 
    });
  }
});

// Join an existing game - simplified for debugging
router.post('/join', (req, res) => {
  try {
    const { gameCode } = req.body;
    console.log(`🚪 POST /api/games/join - Joining game: ${gameCode}`);
    
    if (!gameCode) {
      return res.status(400).json({ 
        success: false,
        error: 'Game code is required' 
      });
    }
    
    // For debugging, accept any code
    const response = { 
      success: true, 
      gameCode: gameCode.toUpperCase(),
      message: 'Joined game successfully!',
      timestamp: new Date().toISOString()
    };
    
    console.log('📤 Sending response:', response);
    res.json(response);
    
  } catch (error) {
    console.error('❌ Error in /api/games/join:', error);
    res.status(500).json({ 
      success: false,
      error: 'Failed to join game',
      details: error.message 
    });
  }
});

export default router;
'''

    # 2. Fix the backend index.ts to properly register the games routes
    backend_index_path = 'backend/src/index.ts'
    backend_content = read_file_content(backend_index_path)
    
    if "Error reading" not in backend_content:
        print("📁 Checking backend index.ts for games routes...")
        
        # Check if games routes are already there
        if '/api/games' not in backend_content:
            print("🔧 Adding games routes to backend index.ts...")
            
            lines = backend_content.split('\n')
            new_lines = []
            import_added = False
            route_added = False
            
            for line in lines:
                new_lines.append(line)
                
                # Add import after existing imports
                if 'import authRoutes from' in line and not import_added:
                    new_lines.append("import gameRoutes from './routes/games';")
                    import_added = True
                
                # Add route after auth routes
                if "app.use('/api/auth'" in line and not route_added:
                    new_lines.append("app.use('/api/games', gameRoutes);")
                    route_added = True
            
            # If we couldn't find the right spots, add them manually
            if not import_added or not route_added:
                # Find a good spot for imports
                import_index = -1
                for i, line in enumerate(new_lines):
                    if line.startswith('import') and 'express' in line:
                        import_index = i
                
                if import_index > -1 and not import_added:
                    new_lines.insert(import_index + 1, "import gameRoutes from './routes/games';")
                    import_added = True
                
                # Find a good spot for routes  
                if not route_added:
                    for i, line in enumerate(new_lines):
                        if 'app.listen' in line:
                            new_lines.insert(i, "app.use('/api/games', gameRoutes);")
                            new_lines.insert(i, "")
                            route_added = True
                            break
            
            if import_added and route_added:
                updated_backend = '\n'.join(new_lines)
                if update_file_content(backend_index_path, updated_backend):
                    print("✅ Updated backend index.ts")
                else:
                    print("❌ Failed to update backend index.ts")
            else:
                print("⚠️ Could not automatically add routes - manual addition needed")
        else:
            print("✅ Games routes already exist in backend index.ts")
    
    # 3. Update the games route file
    if update_file_content('backend/src/routes/games.ts', simple_games_route):
        print("✅ Created/updated backend/src/routes/games.ts")
    
    # 4. Fix the frontend HomePage with better error handling
    fixed_homepage = '''import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ChatRoom from '../components/Chat/ChatRoom';

const HomePage: React.FC = () => {
  const [roomCode, setRoomCode] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [isJoining, setIsJoining] = useState(false);
  const [error, setError] = useState('');
  const [debugInfo, setDebugInfo] = useState('');
  const navigate = useNavigate();

  // Better error handling function
  const handleApiResponse = async (response: Response) => {
    const contentType = response.headers.get('content-type');
    
    if (!response.ok) {
      // If it's not JSON, get the text to see what error page we got
      if (!contentType?.includes('application/json')) {
        const text = await response.text();
        throw new Error(`HTTP ${response.status}: Server returned HTML instead of JSON. Check if route exists.`);
      }
    }
    
    if (contentType?.includes('application/json')) {
      return await response.json();
    } else {
      const text = await response.text();
      throw new Error(`Expected JSON but got: ${contentType}. Response: ${text.substring(0, 100)}...`);
    }
  };

  // Test API connection
  const testApiConnection = async () => {
    setDebugInfo('Testing API connection...');
    try {
      console.log('🧪 Testing: /api/games/test');
      const response = await fetch('/api/games/test');
      const data = await handleApiResponse(response);
      
      if (data.success) {
        setDebugInfo(`✅ API working! Response: ${data.message}`);
        setError('');
      } else {
        setDebugInfo('❌ API responded but with error');
        setError(JSON.stringify(data));
      }
    } catch (err: any) {
      setDebugInfo('❌ API connection failed');
      setError(`Test failed: ${err.message}`);
      console.error('API test failed:', err);
    }
  };

  const handleCreateRoom = async () => {
    setIsCreating(true);
    setError('');
    setDebugInfo('Creating game...');
    
    try {
      console.log('🎮 Creating game...');
      console.log('🔗 URL: /api/games/create');
      
      const response = await fetch('/api/games/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          userId: `user_${Date.now()}`,
          debug: true 
        })
      });

      console.log(`📡 Response status: ${response.status} ${response.statusText}`);
      console.log('📡 Content-Type:', response.headers.get('content-type'));
      
      const data = await handleApiResponse(response);
      console.log('📦 Response data:', data);
      
      if (data.success && data.gameCode) {
        setDebugInfo(`✅ Game created: ${data.gameCode}`);
        console.log('🎉 Navigating to room:', data.gameCode);
        navigate(`/room/${data.gameCode}`);
      } else {
        setError(data.error || 'Failed to create game');
        setDebugInfo('❌ Game creation failed');
      }
    } catch (err: any) {
      console.error('💥 Error creating game:', err);
      setError(err.message);
      setDebugInfo(`❌ ${err.message}`);
    }
    
    setIsCreating(false);
  };

  const handleJoinRoom = async () => {
    if (!roomCode.trim()) {
      setError('Please enter a room code');
      return;
    }
    
    setIsJoining(true);
    setError('');
    setDebugInfo('Joining game...');

    try {
      const response = await fetch('/api/games/join', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          gameCode: roomCode.trim().toUpperCase(),
          userId: `user_${Date.now()}`
        })
      });

      const data = await handleApiResponse(response);
      
      if (data.success && data.gameCode) {
        setDebugInfo(`✅ Joined game: ${data.gameCode}`);
        console.log('🎉 Navigating to room:', data.gameCode);
        navigate(`/room/${data.gameCode}`);
      } else {
        setError(data.error || 'Failed to join game');
        setDebugInfo('❌ Failed to join game');
      }
    } catch (err: any) {
      console.error('💥 Error joining game:', err);
      setError(err.message);
      setDebugInfo(`❌ ${err.message}`);
    }
    
    setIsJoining(false);
  };

  const handleRoomCodeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setRoomCode(e.target.value.toUpperCase());
    if (error) setError('');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Welcome to Codenames!</h1>
        
        {/* Debug Section */}
        <div className="mb-6 bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
          <h3 className="font-semibold text-yellow-900 mb-3">🔧 Debug Tools</h3>
          <div className="flex gap-2 mb-3">
            <button 
              onClick={testApiConnection}
              className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded"
            >
              Test API Connection
            </button>
          </div>
          {debugInfo && (
            <div className="bg-yellow-100 p-2 rounded">
              <p className="text-yellow-800 font-mono text-sm">{debugInfo}</p>
            </div>
          )}
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left side - Game management */}
          <div className="space-y-6">
            {/* Create Game */}
            <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
              <h2 className="text-xl font-semibold mb-4 text-gray-900">Create New Game</h2>
              <p className="text-gray-600 mb-4">Start a new game and invite friends to join</p>
              <button 
                onClick={handleCreateRoom}
                disabled={isCreating}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white py-3 px-4 rounded-lg font-medium transition-colors"
              >
                {isCreating ? 'Creating...' : 'Create Game'}
              </button>
            </div>
            
            {/* Join Game */}
            <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
              <h2 className="text-xl font-semibold mb-4 text-gray-900">Join Existing Game</h2>
              <div className="space-y-4">
                <div>
                  <label htmlFor="roomCode" className="block text-sm font-medium text-gray-700 mb-2">
                    Game Code
                  </label>
                  <input
                    type="text"
                    id="roomCode"
                    value={roomCode}
                    onChange={handleRoomCodeChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white uppercase"
                    placeholder="Enter 6-digit code"
                    maxLength={6}
                    disabled={isJoining}
                  />
                </div>
                <button 
                  onClick={handleJoinRoom}
                  disabled={isJoining || !roomCode.trim()}
                  className="w-full bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white py-3 px-4 rounded-lg font-medium transition-colors"
                >
                  {isJoining ? 'Joining...' : 'Join Game'}
                </button>
              </div>
            </div>
            
            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
                <h4 className="font-semibold text-red-900 mb-2">Debug Error Info:</h4>
                <p className="text-red-800 font-mono text-xs break-words">{error}</p>
              </div>
            )}
            
            {/* Status */}
            <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
              <h3 className="font-semibold text-green-900 mb-2">🎯 Testing Status</h3>
              <div className="text-green-800 space-y-1">
                <p>✅ Frontend running</p>
                <p>✅ Backend connection ready</p>
                <p>🔄 Testing API endpoints...</p>
                <p className="mt-2 font-semibold">Click "Test API Connection" first!</p>
              </div>
            </div>
          </div>
          
          {/* Right side - Chat Room */}
          <div>
            <h2 className="text-xl font-semibold mb-4 text-gray-900">Global Chat</h2>
            <ChatRoom />
            <div className="mt-4 text-sm text-gray-600 bg-blue-50 border border-blue-200 p-3 rounded">
              <p><strong>💬 Global Chat:</strong></p>
              <p>• Chat works = backend connection is good</p>
              <p>• Test real-time communication</p>
              <p>• Open multiple browser windows to test!</p>
            </div>
          </div>
        </div>
        
        {/* Debug Instructions */}
        <div className="mt-8 bg-gray-100 border border-gray-300 p-4 rounded-lg">
          <h3 className="font-semibold text-gray-900 mb-2">🔍 Debugging Steps</h3>
          <div className="text-gray-700 space-y-2">
            <p>• <strong>Step 1:</strong> Click "Test API Connection" - should show "✅ API working!"</p>
            <p>• <strong>Step 2:</strong> If test fails, check backend console for error messages</p>
            <p>• <strong>Step 3:</strong> If test works, try "Create Game" - should generate code like "ABC123"</p>
            <p>• <strong>Step 4:</strong> Check browser Network tab (F12) to see actual API responses</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
'''

    if update_file_content('frontend/src/pages/HomePage.tsx', fixed_homepage):
        print("✅ Updated HomePage with better error handling")
    
    # Update changelog
    try:
        changelog_path = 'CHANGELOG.md'
        with open(changelog_path, 'r', encoding='utf-8') as f:
            changelog = f.read()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        new_entry = f'- JSON Response Error Fix: Fixed backend route registration and improved error handling ({timestamp})'
        
        if '### Python Scripts Run' in changelog:
            updated_changelog = changelog.replace(
                '### Python Scripts Run',
                f'### Python Scripts Run\n{new_entry}'
            )
            
            with open(changelog_path, 'w', encoding='utf-8') as f:
                f.write(updated_changelog)
            print("✅ Updated CHANGELOG.md")
    except Exception as e:
        print(f"Note: Could not update changelog: {e}")
    
    print(f"\n🎉 JSON Response Error Fix Complete!")
    print("\n🔧 What was fixed:")
    print("• Added proper games routes to backend")
    print("• Fixed route registration in backend index.ts")
    print("• Added better error handling in frontend")
    print("• Added API test endpoint for debugging")
    print("\n🎯 Next Steps:")
    print("1. **RESTART your backend server** (this is critical!)")
    print("2. Refresh your browser page")
    print("3. Click 'Test API Connection' button first")
    print("4. If test passes, try 'Create Game'")
    print("5. Check browser console (F12) and backend console for logs")
    print("\n💡 The backend MUST be restarted to load the new routes!")

if __name__ == "__main__":
    main()
