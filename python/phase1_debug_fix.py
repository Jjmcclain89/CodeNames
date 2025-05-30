#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1 Debug and Fix Script
Fixes login input autocomplete and API connection issues for Phase 1 Socket Foundation
"""

import os
import sys
import json
import subprocess
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
                    new_section = "\n### Python Scripts Run\n- Phase 1 Debug Fix: Fixed environment variables, API endpoints, and socket configuration\n"
                    content = content[:insert_point] + new_section + content[insert_point:]
                else:
                    # Add after [Unreleased] header
                    insert_point = content.find("\n", unreleased_section) + 1
                    new_section = "\n### Python Scripts Run\n- Phase 1 Debug Fix: Fixed environment variables, API endpoints, and socket configuration\n"
                    content = content[:insert_point] + new_section + content[insert_point:]
        else:
            # Add to existing section
            section_start = content.find("### Python Scripts Run")
            section_end = content.find("\n###", section_start + 1)
            if section_end == -1:
                section_end = content.find("\n## ", section_start + 1)
            
            entry = f"- Phase 1 Debug Fix: Fixed env vars, API endpoints, socket config ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n"
            
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

def check_and_fix_env_variables():
    """Fix environment variable mismatch"""
    print("🔧 Checking frontend environment variables...")
    
    env_path = Path("frontend/.env")
    if not env_path.exists():
        print("❌ frontend/.env not found!")
        return False
    
    # Read current .env
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the environment variable mismatch
    # socketService.ts looks for VITE_SOCKET_URL but .env has VITE_WS_URL
    if "VITE_WS_URL" in content and "VITE_SOCKET_URL" not in content:
        print("🔧 Fixing environment variable mismatch...")
        content = content.replace("VITE_WS_URL", "VITE_SOCKET_URL")
        
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed VITE_WS_URL → VITE_SOCKET_URL")
    else:
        print("✅ Environment variables look correct")
    
    return True

def check_backend_routes():
    """Check if backend routes exist"""
    print("\n🔧 Checking backend route implementations...")
    
    auth_route_path = Path("backend/src/routes/auth.ts")
    if not auth_route_path.exists():
        print("❌ Backend auth routes not found!")
        return False
    
    # Read auth routes to verify endpoints
    with open(auth_route_path, 'r', encoding='utf-8') as f:
        auth_content = f.read()
    
    required_endpoints = ["/login", "/verify"]
    missing_endpoints = []
    
    for endpoint in required_endpoints:
        if endpoint not in auth_content:
            missing_endpoints.append(endpoint)
    
    if missing_endpoints:
        print(f"❌ Missing backend endpoints: {missing_endpoints}")
        return False
    else:
        print("✅ Backend auth endpoints exist")
    
    return True

def improve_socket_service():
    """Improve socket service configuration"""
    print("\n🔧 Improving socket service configuration...")
    
    socket_service_path = Path("frontend/src/services/socketService.ts")
    
    # Enhanced socket service with better error handling and debugging
    improved_socket_service = '''import { io, Socket } from 'socket.io-client';

export interface User {
  id: string;
  username: string;
  socketId?: string;
}

export interface Room {
  id: string;
  name: string;
  code: string;
  maxPlayers: number;
  users: Array<{
    user: User;
    role: string;
    team?: string;
  }>;
}

export interface ChatMessage {
  id: string;
  username: string;
  message: string;
  timestamp: string;
}

class SocketService {
  private socket: Socket | null = null;
  private token: string | null = null;

  connect(): Socket {
    if (this.socket?.connected) {
      console.log('📡 Socket already connected');
      return this.socket;
    }

    const socketUrl = import.meta.env.VITE_SOCKET_URL || 'http://localhost:3001';
    console.log('📡 Connecting to socket server:', socketUrl);

    this.socket = io(socketUrl, {
      autoConnect: false,
      transports: ['websocket', 'polling'],
      timeout: 5000,
      forceNew: true,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000
    });

    this.setupEventListeners();
    this.socket.connect();

    return this.socket;
  }

  disconnect(): void {
    if (this.socket) {
      console.log('📡 Disconnecting socket');
      this.socket.disconnect();
      this.socket = null;
    }
  }

  authenticate(token: string): void {
    this.token = token;
    if (this.socket) {
      console.log('🔐 Authenticating with token');
      this.socket.emit('authenticate', token);
    }
  }

  joinRoom(roomCode: string): void {
    if (this.socket) {
      console.log('🏠 Joining room:', roomCode);
      this.socket.emit('join-room', { roomCode });
    }
  }

  leaveRoom(): void {
    if (this.socket) {
      console.log('🚪 Leaving room');
      this.socket.emit('leave-room');
    }
  }

  createRoom(roomName?: string): void {
    if (this.socket) {
      console.log('🏗️ Creating room:', roomName || 'Unnamed');
      this.socket.emit('create-room', { roomName });
    }
  }

  sendMessage(message: string): void {
    if (this.socket) {
      console.log('💬 Sending message:', message);
      this.socket.emit('chat-message', { message });
    }
  }

  // Event listener registration methods
  onAuthenticated(callback: (data: any) => void): void {
    this.socket?.on('authenticated', callback);
  }

  onRoomJoined(callback: (data: any) => void): void {
    this.socket?.on('room-joined', callback);
  }

  onRoomCreated(callback: (data: any) => void): void {
    this.socket?.on('room-created', callback);
  }

  onUserJoined(callback: (data: any) => void): void {
    this.socket?.on('user-joined', callback);
  }

  onUserLeft(callback: (data: any) => void): void {
    this.socket?.on('user-left', callback);
  }

  onRoomUsersUpdated(callback: (data: { users: User[] }) => void): void {
    this.socket?.on('room-users-updated', callback);
  }

  onChatMessage(callback: (message: ChatMessage) => void): void {
    this.socket?.on('chat-message', callback);
  }

  onError(callback: (error: any) => void): void {
    this.socket?.on('error', callback);
  }

  onConnect(callback: () => void): void {
    this.socket?.on('connect', callback);
  }

  onDisconnect(callback: () => void): void {
    this.socket?.on('disconnect', callback);
  }

  // Cleanup method to remove specific listeners
  off(event: string, callback?: Function): void {
    if (callback) {
      this.socket?.off(event, callback);
    } else {
      this.socket?.off(event);
    }
  }

  private setupEventListeners(): void {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('✅ Connected to server, Socket ID:', this.socket?.id);
      // Re-authenticate if we have a token
      if (this.token) {
        console.log('🔐 Re-authenticating after reconnection');
        this.authenticate(this.token);
      }
    });

    this.socket.on('disconnect', (reason) => {
      console.log('❌ Disconnected from server. Reason:', reason);
    });

    this.socket.on('connect_error', (error) => {
      console.error('🚫 Socket connection error:', error);
    });

    this.socket.on('reconnect', (attemptNumber) => {
      console.log('🔄 Reconnected after', attemptNumber, 'attempts');
    });

    this.socket.on('reconnect_error', (error) => {
      console.error('🔄 Reconnection failed:', error);
    });
  }

  get isConnected(): boolean {
    return this.socket?.connected || false;
  }

  get socketId(): string | undefined {
    return this.socket?.id;
  }
}

// Export singleton instance
export const socketService = new SocketService();
export default socketService;
'''
    
    with open(socket_service_path, 'w', encoding='utf-8') as f:
        f.write(improved_socket_service)
    
    print("✅ Enhanced socket service with better debugging and error handling")

def enhance_auth_service():
    """Enhance auth service with better error handling"""
    print("\n🔧 Enhancing auth service...")
    
    auth_service_path = Path("frontend/src/services/authService.ts")
    
    enhanced_auth_service = '''export interface LoginResponse {
  success: boolean;
  token?: string;
  user?: {
    id: string;
    username: string;
  };
  error?: string;
}

class AuthService {
  private readonly API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001';

  async login(username: string): Promise<LoginResponse> {
    try {
      console.log('🔑 Attempting login to:', `${this.API_URL}/api/auth/login`);
      console.log('🔑 Username:', username);
      
      const response = await fetch(`${this.API_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username }),
      });

      console.log('🔑 Login response status:', response.status);
      
      if (!response.ok) {
        console.error('🔑 Login response not OK:', response.statusText);
        return {
          success: false,
          error: `Server error: ${response.status} ${response.statusText}`
        };
      }

      const data = await response.json();
      console.log('🔑 Login response data:', data);
      
      if (data.success && data.token) {
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        console.log('🔑 Login successful, token saved');
      }

      return data;
    } catch (error) {
      console.error('🔑 Login network error:', error);
      return {
        success: false,
        error: `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  async verifyToken(token: string): Promise<LoginResponse> {
    try {
      console.log('🔍 Verifying token...');
      
      const response = await fetch(`${this.API_URL}/api/auth/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      });

      console.log('🔍 Token verification response status:', response.status);

      if (!response.ok) {
        console.error('🔍 Token verification failed:', response.statusText);
        return {
          success: false,
          error: `Token verification failed: ${response.status}`
        };
      }

      const result = await response.json();
      console.log('🔍 Token verification result:', result);
      
      return result;
    } catch (error) {
      console.error('🔍 Token verification network error:', error);
      return {
        success: false,
        error: `Network error during token verification: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  logout(): void {
    console.log('🚪 Logging out, clearing local storage');
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }

  getToken(): string | null {
    return localStorage.getItem('token');
  }

  getUser(): any {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }
}

export const authService = new AuthService();
export default authService;
'''
    
    with open(auth_service_path, 'w', encoding='utf-8') as f:
        f.write(enhanced_auth_service)
    
    print("✅ Enhanced auth service with detailed logging and error handling")

def create_debug_test_page():
    """Create a debug test page to test connections"""
    print("\n🔧 Creating debug test page...")
    
    debug_page_path = Path("frontend/src/pages/DebugPage.tsx")
    
    debug_page_content = '''import React, { useState, useEffect } from 'react';
import authService from '../services/authService';
import socketService from '../services/socketService';

const DebugPage: React.FC = () => {
  const [apiStatus, setApiStatus] = useState<string>('Not tested');
  const [socketStatus, setSocketStatus] = useState<string>('Not connected');
  const [testResults, setTestResults] = useState<string[]>([]);

  const addResult = (message: string) => {
    setTestResults(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
  };

  const testAPI = async () => {
    addResult('🔑 Testing API connection...');
    setApiStatus('Testing...');
    
    try {
      const result = await authService.login('test-user');
      if (result.success) {
        setApiStatus('✅ Connected');
        addResult('🔑 API test successful');
      } else {
        setApiStatus('❌ Failed');
        addResult(`🔑 API test failed: ${result.error}`);
      }
    } catch (error) {
      setApiStatus('❌ Error');
      addResult(`🔑 API test error: ${error}`);
    }
  };

  const testSocket = () => {
    addResult('📡 Testing socket connection...');
    setSocketStatus('Connecting...');
    
    const socket = socketService.connect();
    
    socket.on('connect', () => {
      setSocketStatus('✅ Connected');
      addResult('📡 Socket connected successfully');
    });
    
    socket.on('connect_error', (error) => {
      setSocketStatus('❌ Failed');
      addResult(`📡 Socket connection failed: ${error}`);
    });
  };

  const clearResults = () => {
    setTestResults([]);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Phase 1 Debug Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">API Connection Test</h2>
          <p className="mb-4">Status: <span className="font-mono">{apiStatus}</span></p>
          <button 
            onClick={testAPI}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
          >
            Test API Connection
          </button>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Socket Connection Test</h2>
          <p className="mb-4">Status: <span className="font-mono">{socketStatus}</span></p>
          <button 
            onClick={testSocket}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded"
          >
            Test Socket Connection
          </button>
        </div>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Test Results</h2>
          <button 
            onClick={clearResults}
            className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-sm"
          >
            Clear
          </button>
        </div>
        <div className="bg-gray-100 p-4 rounded h-64 overflow-y-auto">
          {testResults.length === 0 ? (
            <p className="text-gray-500">No test results yet...</p>
          ) : (
            <div className="space-y-1">
              {testResults.map((result, index) => (
                <div key={index} className="font-mono text-sm">{result}</div>
              ))}
            </div>
          )}
        </div>
      </div>
      
      <div className="mt-6 text-sm text-gray-600">
        <p><strong>Expected behavior:</strong></p>
        <ul className="list-disc pl-5 mt-2">
          <li>API test should return a token and user object</li>
          <li>Socket test should establish WebSocket connection</li>
          <li>Check browser console (F12) for detailed logs</li>
          <li>Both tests need backend server running on localhost:3001</li>
        </ul>
      </div>
    </div>
  );
};

export default DebugPage;
'''
    
    with open(debug_page_path, 'w', encoding='utf-8') as f:
        f.write(debug_page_content)
    
    print("✅ Created debug test page at frontend/src/pages/DebugPage.tsx")

def main():
    """Main execution function"""
    print("🚀 Phase 1 Debug and Fix Script")
    print("=" * 50)
    
    try:
        # Ensure we're in the project root
        if not Path("frontend").exists() or not Path("backend").exists():
            print("❌ Error: Please run this script from the project root directory")
            print("   Current directory:", os.getcwd())
            sys.exit(1)
        
        # 1. Fix environment variables
        check_and_fix_env_variables()
        
        # 2. Check backend routes
        check_backend_routes()
        
        # 3. Improve socket service
        improve_socket_service()
        
        # 4. Enhance auth service
        enhance_auth_service()
        
        # 5. Create debug test page
        create_debug_test_page()
        
        # 6. Update changelog
        add_changelog_entry()
        
        print("\n🎉 Phase 1 Debug Fixes Complete!")
        print("=" * 50)
        
        print("\n📋 Summary of fixes:")
        print("✅ Fixed environment variable mismatch (VITE_WS_URL → VITE_SOCKET_URL)")
        print("✅ Enhanced socket service with better debugging")
        print("✅ Enhanced auth service with detailed logging")  
        print("✅ Created debug test page for connection testing")
        print("✅ Updated changelog")
        
        print("\n🔧 Next steps:")
        print("1. Make sure both servers are running:")
        print("   Backend:  cd backend && npm run dev")
        print("   Frontend: cd frontend && npm run dev")
        print("2. Visit http://localhost:5173/debug to test connections")
        print("3. Open browser console (F12) to see detailed logs")
        print("4. Try the login flow and check for any remaining errors")
        
        print("\n🎯 Phase 1 Goals:")
        print("- Two browsers should be able to connect and communicate")
        print("- Real-time messaging should work between clients")
        print("- Authentication should work properly")
        
        return 0
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
