#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fix Frontend Proxy Configuration
Adds proper proxy configuration so frontend can reach backend APIs
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
    print("🔧 Fixing Frontend Proxy Configuration...")
    
    # First, let's check and update the Vite config
    vite_config_path = 'frontend/vite.config.ts'
    
    print("📁 Checking frontend/vite.config.ts...")
    
    # Read current vite config
    vite_content = read_file_content(vite_config_path)
    
    if "Error reading" in vite_content:
        print(f"❌ {vite_content}")
        return
    
    # Check if proxy is already configured
    if 'proxy' in vite_content:
        print("✅ Proxy configuration already exists in vite.config.ts")
    else:
        print("🔧 Adding proxy configuration to vite.config.ts...")
        
        # Create updated vite config with proxy
        updated_vite_config = '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
'''
        
        if update_file_content(vite_config_path, updated_vite_config):
            print("✅ Updated vite.config.ts with proxy configuration")
        else:
            print("❌ Failed to update vite.config.ts")
    
    # Also update the HomePage to test the backend directly first
    homepage_with_direct_test = '''import React, { useState } from 'react';
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
            <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
              <h3 className="font-semibold text-blue-900 mb-2">🎯 Connection Status</h3>
              <div className="text-blue-800 space-y-1">
                <p>✅ Frontend running (you can see this page)</p>
                <p>🔄 Backend test: Click "Test Backend Direct"</p>
                <p>🔄 Proxy test: Click "Test Proxy"</p>
                <p className="mt-2 font-semibold">Both should pass before creating games!</p>
              </div>
            </div>
          </div>
          
          {/* Right side - Chat Room */}
          <div>
            <h2 className="text-xl font-semibold mb-4 text-gray-900">Global Chat</h2>
            <ChatRoom />
            <div className="mt-4 text-sm text-gray-600 bg-blue-50 border border-blue-200 p-3 rounded">
              <p><strong>💬 Global Chat:</strong></p>
              <p>• If chat works, backend connection is good</p>
              <p>• If chat fails, backend may not be running</p>
            </div>
          </div>
        </div>
        
        {/* Debug Instructions */}
        <div className="mt-8 bg-gray-100 border border-gray-300 p-4 rounded-lg">
          <h3 className="font-semibold text-gray-900 mb-2">🔍 Debugging Steps</h3>
          <div className="text-gray-700 space-y-2">
            <p>• <strong>Step 1:</strong> Click "Test Backend Direct" - tests backend directly</p>
            <p>• <strong>Step 2:</strong> If Step 1 fails, check if backend is running on port 3001</p>
            <p>• <strong>Step 3:</strong> If Step 1 passes, restart frontend and click "Test Proxy"</p>
            <p>• <strong>Step 4:</strong> If both pass, try "Create Game"</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
'''

    if update_file_content('frontend/src/pages/HomePage.tsx', homepage_with_direct_test):
        print("✅ Updated HomePage with direct backend testing")
    
    # Update changelog
    try:
        changelog_path = 'CHANGELOG.md'
        with open(changelog_path, 'r', encoding='utf-8') as f:
            changelog = f.read()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        new_entry = f'- Frontend Proxy Fix: Added Vite proxy configuration and direct backend testing ({timestamp})'
        
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
    
    print(f"\n🎉 Frontend Proxy Fix Complete!")
    print("\n🔧 What was fixed:")
    print("• Added Vite proxy configuration to forward /api/* to backend")
    print("• Added direct backend testing to diagnose connection issues")
    print("• Enhanced debugging tools in HomePage")
    print("\n🎯 Next Steps:")
    print("1. **RESTART your frontend server** (to load new proxy config)")
    print("2. Click 'Test Backend Direct' - should pass if backend is running")
    print("3. Click 'Test Proxy' - should pass after frontend restart")
    print("4. Try 'Create Game' once both tests pass")
    print("\n💡 The issue was missing proxy configuration!")

if __name__ == "__main__":
    main()
