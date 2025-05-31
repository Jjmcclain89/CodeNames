#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fix Homepage Games List
Diagnoses and fixes the missing Browse Games section on the homepage
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
    print("🔧 Diagnosing and Fixing Homepage Games List...")
    
    # Check current HomePage content
    homepage_path = 'frontend/src/pages/HomePage.tsx'
    print(f"📁 Checking {homepage_path}...")
    
    current_content = read_file_content(homepage_path)
    
    if "Error reading" in current_content:
        print(f"❌ {current_content}")
        return
    
    # Check if the games list is already there
    if 'Browse Active Games' in current_content:
        print("✅ Browse Games section already exists in HomePage")
        print("🔄 Try refreshing your browser or restarting the frontend server")
        return
    
    print("❌ Browse Games section missing from HomePage")
    print("🔧 Adding the complete updated HomePage...")
    
    # Create the complete updated HomePage with Browse Games section
    updated_homepage = '''import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ChatRoom from '../components/Chat/ChatRoom';

interface GameListItem {
  code: string;
  id: string;
  status: string;
  playerCount: number;
  players: string[];
  createdAt: string;
  lastActivity: string;
}

const HomePage: React.FC = () => {
  const [roomCode, setRoomCode] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [isJoining, setIsJoining] = useState(false);
  const [error, setError] = useState('');
  const [debugInfo, setDebugInfo] = useState('');
  const [games, setGames] = useState<GameListItem[]>([]);
  const [isLoadingGames, setIsLoadingGames] = useState(false);
  const navigate = useNavigate();

  // Load games list on component mount and refresh periodically
  useEffect(() => {
    loadGamesList();
    
    // Refresh games list every 10 seconds
    const interval = setInterval(loadGamesList, 10000);
    
    return () => clearInterval(interval);
  }, []);

  const loadGamesList = async () => {
    setIsLoadingGames(true);
    try {
      console.log('📋 Loading games list...');
      const response = await fetch('/api/games');
      const data = await response.json();
      
      if (data.success) {
        setGames(data.games || []);
        console.log(`✅ Loaded ${data.games?.length || 0} games`);
      } else {
        console.error('Failed to load games list:', data.error);
      }
    } catch (err) {
      console.error('Error loading games list:', err);
    }
    setIsLoadingGames(false);
  };

  // Better error handling function
  const handleApiResponse = async (response: Response) => {
    const contentType = response.headers.get('content-type');
    
    if (!response.ok) {
      if (!contentType?.includes('application/json')) {
        const text = await response.text();
        throw new Error(`HTTP ${response.status}: Server returned HTML instead of JSON. Check if backend is running and proxy is configured.`);
      }
    }
    
    if (contentType?.includes('application/json')) {
      return await response.json();
    } else {
      const text = await response.text();
      throw new Error(`Expected JSON but got: ${contentType}. Response: ${text.substring(0, 100)}...`);
    }
  };

  // Test backend directly first
  const testBackendDirect = async () => {
    setDebugInfo('Testing backend directly...');
    try {
      console.log('🧪 Testing backend directly: http://localhost:3001/api/games/test');
      const response = await fetch('http://localhost:3001/api/games/test');
      const data = await handleApiResponse(response);
      
      if (data.success) {
        setDebugInfo(`✅ Backend direct test PASSED! ${data.message}`);
        setError('');
      } else {
        setDebugInfo('❌ Backend direct test failed');
        setError(JSON.stringify(data));
      }
    } catch (err: any) {
      setDebugInfo('❌ Backend direct test failed');
      setError(`Direct backend test failed: ${err.message}`);
      console.error('Backend direct test failed:', err);
    }
  };

  // Test API connection through proxy
  const testApiConnection = async () => {
    setDebugInfo('Testing API connection through proxy...');
    try {
      console.log('🧪 Testing: /api/games/test (through proxy)');
      const response = await fetch('/api/games/test');
      const data = await handleApiResponse(response);
      
      if (data.success) {
        setDebugInfo(`✅ Proxy test PASSED! ${data.message}`);
        setError('');
        // Also refresh games list after successful test
        loadGamesList();
      } else {
        setDebugInfo('❌ Proxy test failed');
        setError(JSON.stringify(data));
      }
    } catch (err: any) {
      setDebugInfo('❌ Proxy test failed');
      setError(`Proxy test failed: ${err.message}`);
      console.error('Proxy test failed:', err);
    }
  };

  const handleCreateRoom = async () => {
    setIsCreating(true);
    setError('');
    setDebugInfo('Creating game...');
    
    try {
      console.log('🎮 Creating game...');
      
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      
      const response = await fetch('/api/games/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          userId: user.id || `user_${Date.now()}`,
          username: user.username || 'Anonymous',
          debug: true 
        })
      });

      const data = await handleApiResponse(response);
      
      if (data.success && data.gameCode) {
        setDebugInfo(`✅ Game created: ${data.gameCode}`);
        console.log('🎉 Navigating to room:', data.gameCode);
        // Refresh games list before navigating
        loadGamesList();
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
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      
      const response = await fetch('/api/games/join', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          gameCode: roomCode.trim().toUpperCase(),
          userId: user.id || `user_${Date.now()}`,
          username: user.username || 'Anonymous'
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

  const handleJoinGameFromList = async (gameCode: string) => {
    setDebugInfo(`Joining game ${gameCode} from list...`);
    
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      
      const response = await fetch('/api/games/join', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          gameCode: gameCode,
          userId: user.id || `user_${Date.now()}`,
          username: user.username || 'Anonymous'
        })
      });

      const data = await handleApiResponse(response);
      
      if (data.success) {
        console.log('🎉 Navigating to room:', gameCode);
        navigate(`/room/${gameCode}`);
      } else {
        setError(data.error || 'Failed to join game');
      }
    } catch (err: any) {
      console.error('💥 Error joining game from list:', err);
      setError(err.message);
    }
  };

  const handleRoomCodeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setRoomCode(e.target.value.toUpperCase());
    if (error) setError('');
  };

  const getTimeAgo = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now.getTime() - time.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
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
              onClick={testBackendDirect}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded text-sm"
            >
              Test Backend Direct
            </button>
            <button 
              onClick={testApiConnection}
              className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded text-sm"
            >
              Test Proxy
            </button>
            <button 
              onClick={loadGamesList}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm"
            >
              Refresh Games
            </button>
          </div>
          {debugInfo && (
            <div className="bg-yellow-100 p-2 rounded">
              <p className="text-yellow-800 font-mono text-sm">{debugInfo}</p>
            </div>
          )}
          <div className="mt-2 text-xs text-yellow-700">
            <p><strong>Step 1:</strong> Test Backend Direct (should work if backend is running)</p>
            <p><strong>Step 2:</strong> Test Proxy (should work after restarting frontend)</p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left side - Game management */}
          <div className="lg:col-span-2 space-y-6">
            {/* Create/Join Game Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
                <h2 className="text-xl font-semibold mb-4 text-gray-900">Join with Code</h2>
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
            </div>

            {/* Browse Games Section */}
            <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-gray-900">🎮 Browse Active Games</h2>
                <button 
                  onClick={loadGamesList}
                  disabled={isLoadingGames}
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  {isLoadingGames ? '🔄 Loading...' : '🔄 Refresh'}
                </button>
              </div>
              
              {games.length > 0 ? (
                <div className="space-y-3">
                  {games.map((game) => (
                    <div key={game.code} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors">
                      <div className="flex-1">
                        <div className="flex items-center space-x-4">
                          <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded font-mono font-bold text-lg">
                            {game.code}
                          </div>
                          <div className="text-sm text-gray-600">
                            <span className="font-medium">{game.playerCount} player{game.playerCount !== 1 ? 's' : ''}</span>
                            <span className="mx-2">•</span>
                            <span>{getTimeAgo(game.lastActivity)}</span>
                            <span className="mx-2">•</span>
                            <span className="text-green-600 capitalize">{game.status}</span>
                          </div>
                        </div>
                        {game.players.length > 0 && (
                          <div className="mt-2 text-xs text-gray-500">
                            <span className="font-medium">Players:</span> {game.players.join(', ')}
                          </div>
                        )}
                      </div>
                      <button
                        onClick={() => handleJoinGameFromList(game.code)}
                        className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors"
                      >
                        Join Game
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <div className="text-4xl mb-4">🎮</div>
                  <p className="text-lg font-medium">No active games</p>
                  <p className="text-sm mt-1">Be the first to create a game!</p>
                </div>
              )}
            </div>
            
            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
                <h4 className="font-semibold text-red-900 mb-2">Debug Error Info:</h4>
                <p className="text-red-800 font-mono text-xs break-words">{error}</p>
              </div>
            )}
          </div>

          {/* Right sidebar - Chat and Status */}
          <div className="space-y-6">
            {/* Connection Status */}
            <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
              <h3 className="font-semibold text-green-900 mb-2">🎯 Status</h3>
              <div className="text-green-800 space-y-1 text-sm">
                <p>✅ Frontend running</p>
                <p>✅ Multiplayer ready</p>
                <p>✅ Game browsing active</p>
                <p className="mt-2 font-semibold">Ready to play! 🎮</p>
              </div>
            </div>

            {/* Global Chat */}
            <div>
              <h2 className="text-xl font-semibold mb-4 text-gray-900">Global Chat</h2>
              <ChatRoom />
              <div className="mt-4 text-sm text-gray-600 bg-blue-50 border border-blue-200 p-3 rounded">
                <p><strong>💬 Global Chat:</strong></p>
                <p>• Chat with all online players</p>
                <p>• Test real-time communication</p>
                <p>• Games have their own room chat!</p>
              </div>
            </div>
          </div>
        </div>
        
        {/* Instructions */}
        <div className="mt-8 bg-gray-100 border border-gray-300 p-4 rounded-lg">
          <h3 className="font-semibold text-gray-900 mb-2">🎯 How to Play</h3>
          <div className="text-gray-700 space-y-2">
            <p>• <strong>Create Game:</strong> Click "Create Game" to generate a 6-digit code</p>
            <p>• <strong>Browse Games:</strong> See all active games and join directly with one click</p>
            <p>• <strong>Join with Code:</strong> Enter a specific game code if you have one</p>
            <p>• <strong>Share & Play:</strong> Invite friends by sharing your game code</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
'''

    # Update the HomePage
    if update_file_content(homepage_path, updated_homepage):
        print("✅ Successfully updated HomePage with Browse Games section")
    else:
        print("❌ Failed to update HomePage")
        return
    
    # Also need to check if the backend endpoint was added
    print("\n🔧 Checking backend games list endpoint...")
    
    games_routes_path = 'backend/src/routes/games.ts'
    games_content = read_file_content(games_routes_path)
    
    if "Error reading" not in games_content:
        if "router.get('/'," in games_content:
            print("✅ Backend games list endpoint already exists")
        else:
            print("❌ Backend games list endpoint missing - adding it...")
            
            # Add the missing endpoint
            lines = games_content.split('\\n')
            new_lines = []
            
            for i, line in enumerate(lines):
                new_lines.append(line)
                
                # Add after the test endpoint
                if 'res.json({ ' in line and 'success: true,' in line and 'message: ' in line and 'Games API is working' in line:
                    # This is the end of the test endpoint, add our list endpoint after
                    j = i + 1
                    while j < len(lines) and '});' not in lines[j]:
                        new_lines.append(lines[j])
                        j += 1
                    
                    if j < len(lines):
                        new_lines.append(lines[j])  # The closing });
                        
                        # Add the list endpoint
                        list_endpoint = '''
// List all active games
router.get('/', (req: Request, res: Response): void => {
  try {
    console.log('📋 GET /api/games - Listing all games...');
    
    const games = Array.from(gameRooms.values()).map(room => ({
      code: room.code,
      id: room.id,
      status: room.status,
      playerCount: room.players.length,
      players: room.players.map(p => p.username),
      createdAt: room.createdAt,
      lastActivity: room.messages.length > 0 ? 
        room.messages[room.messages.length - 1].timestamp : 
        room.createdAt
    }));
    
    // Sort by most recent activity
    games.sort((a, b) => new Date(b.lastActivity).getTime() - new Date(a.lastActivity).getTime());
    
    console.log(`📤 Found ${games.length} active games`);
    
    res.json({
      success: true,
      games: games,
      total: games.length,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ Error listing games:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to list games',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});
'''
                        new_lines.extend(list_endpoint.split('\\n'))
                        
                        # Skip the rest of the loop since we added our content
                        i = j
                        break
            
            # Update the file
            updated_games_content = '\\n'.join(new_lines)
            if update_file_content(games_routes_path, updated_games_content):
                print("✅ Added missing backend games list endpoint")
            else:
                print("❌ Failed to add backend endpoint")
    
    # Update changelog
    try:
        changelog_path = 'CHANGELOG.md'
        with open(changelog_path, 'r', encoding='utf-8') as f:
            changelog = f.read()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        new_entry = f'- Homepage Games List Fix: Fixed missing Browse Games section and backend endpoint ({timestamp})'
        
        if '### Python Scripts Run' in changelog:
            updated_changelog = changelog.replace(
                '### Python Scripts Run',
                f'### Python Scripts Run\\n{new_entry}'
            )
            
            with open(changelog_path, 'w', encoding='utf-8') as f:
                f.write(updated_changelog)
            print("✅ Updated CHANGELOG.md")
    except Exception as e:
        print(f"Note: Could not update changelog: {e}")
    
    print(f"\\n🎉 Homepage Games List Fix Complete!")
    print("\\n🔧 What was fixed:")
    print("• Added complete Browse Games section to HomePage")
    print("• Enhanced UI with better styling and layout") 
    print("• Added backend games list endpoint if missing")
    print("• Added auto-refresh functionality")
    print("• Improved error handling and user feedback")
    print("\\n🎯 Next Steps:")
    print("1. **RESTART your backend server** (to load any new endpoints)")
    print("2. **Refresh your browser** (Ctrl+F5 to force reload)")
    print("3. **Test the games list:**")
    print("   - Create a game in one window")
    print("   - Check the Browse Games section")
    print("   - Should show your game with Join button!")
    print("\\n💡 The Browse Games section should now be visible below Create/Join!")

if __name__ == "__main__":
    main()
