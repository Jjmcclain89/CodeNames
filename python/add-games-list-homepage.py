#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Add Games List to Homepage
Adds a "Browse Games" section showing all active games with player counts
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
    print("🔧 Adding Games List to Homepage...")
    
    # 1. First, add the API endpoint to list all games
    games_routes_path = 'backend/src/routes/games.ts'
    games_content = read_file_content(games_routes_path)
    
    if "Error reading" not in games_content and 'router.get(\'/\'' not in games_content:
        print("📡 Adding /api/games endpoint to list all games...")
        
        # Add the list all games endpoint
        lines = games_content.split('\n')
        new_lines = []
        endpoint_added = False
        
        for line in lines:
            new_lines.append(line)
            
            # Add after the test endpoint
            if 'router.get(\'/test\'' in line and not endpoint_added:
                # Find the end of the test endpoint
                j = len(new_lines) - 1
                while j < len(lines) and '});' not in lines[j]:
                    if j + 1 < len(lines):
                        new_lines.append(lines[j + 1])
                        j += 1
                    else:
                        break
                
                # Add the new endpoint after the test endpoint
                new_endpoint = '''
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
                
                new_lines.extend(new_endpoint.split('\n'))
                endpoint_added = True
                
                # Skip the lines we already added
                while j + 1 < len(lines) and '});' not in lines[j]:
                    j += 1
                
                # Continue from after the test endpoint
                continue
        
        if endpoint_added:
            updated_games_content = '\n'.join(new_lines)
            if update_file_content(games_routes_path, updated_games_content):
                print("✅ Added games list endpoint to backend")
            else:
                print("❌ Failed to update games routes")
        else:
            print("⚠️ Could not find suitable location for games list endpoint")
    
    # 2. Update the HomePage with games list
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
      const response = await fetch('/api/games');
      const data = await response.json();
      
      if (data.success) {
        setGames(data.games || []);
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
      console.log('🔗 URL: /api/games/create');
      
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

  const handleJoinGameFromList = (gameCode: string) => {
    setRoomCode(gameCode);
    handleJoinRoom();
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
            {/* Create/Join Game */}
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

            {/* Browse Games */}
            <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-gray-900">🎮 Browse Active Games</h2>
                <button 
                  onClick={loadGamesList}
                  disabled={isLoadingGames}
                  className="text-blue-600 hover:text-blue-800 text-sm"
                >
                  {isLoadingGames ? '🔄 Loading...' : '🔄 Refresh'}
                </button>
              </div>
              
              {games.length > 0 ? (
                <div className="space-y-3">
                  {games.map((game) => (
                    <div key={game.code} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border">
                      <div className="flex-1">
                        <div className="flex items-center space-x-4">
                          <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded font-mono font-bold">
                            {game.code}
                          </div>
                          <div className="text-sm text-gray-600">
                            <span className="font-medium">{game.playerCount} player{game.playerCount !== 1 ? 's' : ''}</span>
                            <span className="mx-2">•</span>
                            <span>{getTimeAgo(game.lastActivity)}</span>
                          </div>
                        </div>
                        {game.players.length > 0 && (
                          <div className="mt-2 text-xs text-gray-500">
                            Players: {game.players.join(', ')}
                          </div>
                        )}
                      </div>
                      <button
                        onClick={() => handleJoinGameFromList(game.code)}
                        className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded text-sm font-medium"
                      >
                        Join
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <p className="text-lg">No active games</p>
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

          {/* Right side - Chat and Status */}
          <div className="space-y-6">
            {/* Status */}
            <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
              <h3 className="font-semibold text-green-900 mb-2">🎯 Connection Status</h3>
              <div className="text-green-800 space-y-1">
                <p>✅ Frontend running</p>
                <p>🔄 Backend test: Click "Test Backend Direct"</p>
                <p>🔄 Proxy test: Click "Test Proxy"</p>
                <p className="mt-2 font-semibold">Both should pass before creating games!</p>
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
            <p>• <strong>Share Code:</strong> Give the code to friends so they can join</p>
            <p>• <strong>Browse Games:</strong> See all active games and join directly</p>
            <p>• <strong>Join Game:</strong> Enter a code you received or click "Join" on any active game</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
'''

    # Update the HomePage
    if update_file_content('frontend/src/pages/HomePage.tsx', updated_homepage):
        print("✅ Updated HomePage with games list")
    
    # Update changelog
    try:
        changelog_path = 'CHANGELOG.md'
        with open(changelog_path, 'r', encoding='utf-8') as f:
            changelog = f.read()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        new_entry = f'- Games List Homepage: Added browse active games section with player counts and join buttons ({timestamp})'
        
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
    
    print(f"\n🎉 Games List Added to Homepage!")
    print("\n🔧 What was added:")
    print("• Browse Active Games section showing all current games")
    print("• Player counts and activity timestamps for each game")
    print("• Direct join buttons for each game")
    print("• Auto-refresh every 10 seconds + manual refresh button")
    print("• Player names shown for each game")
    print("• Backend API endpoint GET /api/games to list all games")
    print("\n🎯 Features:")
    print("• See all active games without needing codes")
    print("• Player count and last activity time")
    print("• One-click join from the games list")
    print("• Automatic updates of game list")
    print("• Empty state when no games exist")
    print("\n💡 Now players can discover and join games easily!")
    print("🚀 Perfect addition to complete the multiplayer experience!")

if __name__ == "__main__":
    main()
