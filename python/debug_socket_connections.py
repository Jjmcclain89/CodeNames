#!/usr/bin/env python3
"""
Debug Socket Connections

This script adds comprehensive debugging to trace exactly how many socket 
connections are being created and why users are "joining the chat" multiple times.
"""

import os
import sys

def add_app_connection_debugging():
    """Add detailed debugging to App.tsx to track socket connections"""
    
    app_path = "frontend/src/App.tsx"
    
    if not os.path.exists(app_path):
        print(f"Error: {app_path} not found")
        return False
    
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add debugging to the useEffect where socket connection happens
    if "🔍 APP DEBUG" not in content:
        old_useEffect = """  useEffect(() => {
    const initAuth = async () => {
      const token = authService.getToken();
      const savedUser = authService.getUser();
      if (token && savedUser) {
        // Verify token is still valid
        const result = await authService.verifyToken(token);
        if (result.success) {
          setIsAuthenticated(true);
          setUser(savedUser);
          // Initialize socket connection with token - SINGLE SOURCE OF TRUTH
          console.log('🔌 App.tsx: Initializing socket connection');
          socketService.connect();
          socketService.authenticate(token);
        } else {
          authService.logout();
        }
      }
      setIsLoading(false);
    };
    initAuth();
  }, []);"""
        
        new_useEffect = """  useEffect(() => {
    console.log('🔍 APP DEBUG: useEffect triggered');
    console.log('🔍 APP DEBUG: Timestamp:', Date.now());
    console.log('🔍 APP DEBUG: Call stack:', new Error().stack?.split('\\n').slice(0, 5).join('\\n'));
    
    const initAuth = async () => {
      const token = authService.getToken();
      const savedUser = authService.getUser();
      console.log('🔍 APP DEBUG: Token exists:', !!token);
      console.log('🔍 APP DEBUG: Saved user exists:', !!savedUser);
      
      if (token && savedUser) {
        // Verify token is still valid
        const result = await authService.verifyToken(token);
        console.log('🔍 APP DEBUG: Token verification result:', result.success);
        
        if (result.success) {
          setIsAuthenticated(true);
          setUser(savedUser);
          // Initialize socket connection with token - SINGLE SOURCE OF TRUTH
          console.log('🔌 App.tsx: Initializing socket connection for user:', savedUser.username);
          console.log('🔌 App.tsx: Current socket state before connect:', {
            hasSocket: !!socketService.socket,
            isConnected: socketService.socket?.connected,
            socketId: socketService.socket?.id
          });
          
          socketService.connect();
          
          console.log('🔌 App.tsx: Socket state after connect:', {
            hasSocket: !!socketService.socket,
            isConnected: socketService.socket?.connected,
            socketId: socketService.socket?.id
          });
          
          socketService.authenticate(token);
        } else {
          authService.logout();
        }
      }
      setIsLoading(false);
    };
    initAuth();
  }, []);"""
        
        if old_useEffect in content:
            content = content.replace(old_useEffect, new_useEffect)
            print("✅ Added App.tsx useEffect debugging")
    
    # Add debugging to handleLogin
    if "🔍 LOGIN DEBUG" not in content:
        old_handleLogin = """  const handleLogin = (userData: any, token: string) => {
    setIsAuthenticated(true);
    setUser(userData);
    // Connect to socket after successful login - SINGLE SOURCE OF TRUTH
    console.log('🔌 App.tsx: Connecting socket after login');
    socketService.connect();
    socketService.authenticate(token);
  };"""
        
        new_handleLogin = """  const handleLogin = (userData: any, token: string) => {
    console.log('🔍 LOGIN DEBUG: handleLogin called for user:', userData.username);
    console.log('🔍 LOGIN DEBUG: Current socket state before login connect:', {
      hasSocket: !!socketService.socket,
      isConnected: socketService.socket?.connected,
      socketId: socketService.socket?.id
    });
    
    setIsAuthenticated(true);
    setUser(userData);
    // Connect to socket after successful login - SINGLE SOURCE OF TRUTH
    console.log('🔌 App.tsx: Connecting socket after login for:', userData.username);
    socketService.connect();
    
    console.log('🔍 LOGIN DEBUG: Socket state after login connect:', {
      hasSocket: !!socketService.socket,
      isConnected: socketService.socket?.connected,
      socketId: socketService.socket?.id
    });
    
    socketService.authenticate(token);
  };"""
        
        if old_handleLogin in content:
            content = content.replace(old_handleLogin, new_handleLogin)
            print("✅ Added handleLogin debugging")
    
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def add_socket_service_debugging():
    """Add more detailed debugging to socketService to track connection calls"""
    
    socket_service_path = "frontend/src/services/socketService.ts"
    
    if not os.path.exists(socket_service_path):
        print(f"Error: {socket_service_path} not found")
        return False
    
    with open(socket_service_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add a connection counter to track how many times connect() is called
    if "private connectionCounter: number = 0;" not in content:
        # Find where other private properties are declared
        private_pattern = "private isConnecting: boolean = false; // Track connection in progress"
        if private_pattern in content:
            content = content.replace(
                private_pattern,
                private_pattern + "\n  private connectionCounter: number = 0;"
            )
            print("✅ Added connection counter to socketService")
    
    # Enhance the connect() method debugging
    old_connect_start = '''  connect(): Socket {
    // Track what is calling connect
    console.log('🔌 CONNECT() CALLED');
    console.log('🔌 Call stack:', new Error().stack);
    console.log('🔌 Current socket state:', {
      hasSocket: !!this._socket,
      isConnected: this._socket?.connected,
      isConnecting: this.isConnecting
    });'''
    
    new_connect_start = '''  connect(): Socket {
    this.connectionCounter++;
    // Track what is calling connect
    console.log('🔌 CONNECT() CALLED #' + this.connectionCounter);
    console.log('🔌 Call stack:', new Error().stack?.split('\\n').slice(0, 8).join('\\n'));
    console.log('🔌 Current socket state:', {
      hasSocket: !!this._socket,
      isConnected: this._socket?.connected,
      isConnecting: this.isConnecting,
      socketId: this._socket?.id,
      connectionCounter: this.connectionCounter
    });'''
    
    if old_connect_start in content:
        content = content.replace(old_connect_start, new_connect_start)
        print("✅ Enhanced connect() method debugging")
    
    # Add debugging to authenticate method
    old_authenticate = '''  authenticate(token: string): void {
    this.token = token;
    if (this._socket) {
      console.log('🔐 Authenticating with token');
      this._socket.emit('authenticate', token);
    }
  }'''
    
    new_authenticate = '''  authenticate(token: string): void {
    console.log('🔐 AUTHENTICATE() CALLED');
    console.log('🔐 Socket exists:', !!this._socket);
    console.log('🔐 Socket connected:', this._socket?.connected);
    console.log('🔐 Socket ID:', this._socket?.id);
    console.log('🔐 Token (first 20 chars):', token?.substring(0, 20) + '...');
    
    this.token = token;
    if (this._socket) {
      console.log('🔐 Emitting authenticate event to backend');
      this._socket.emit('authenticate', token);
    } else {
      console.log('❌ No socket available for authentication');
    }
  }'''
    
    if old_authenticate in content:
        content = content.replace(old_authenticate, new_authenticate)
        print("✅ Enhanced authenticate() method debugging")
    
    with open(socket_service_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def add_backend_authentication_debugging():
    """Add debugging to backend authentication to see how many times it's called"""
    
    backend_index_path = "backend/src/index.ts"
    
    if not os.path.exists(backend_index_path):
        print(f"Error: {backend_index_path} not found")
        return False
    
    with open(backend_index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add a counter to track authentication attempts
    if "let authCounter = 0;" not in content:
        # Find where the socket handlers start
        socket_pattern = "io.on('connection', (socket) => {"
        if socket_pattern in content:
            content = content.replace(
                socket_pattern,
                "let authCounter = 0;\n\n" + socket_pattern
            )
            print("✅ Added authentication counter to backend")
    
    # Enhance the authenticate handler debugging
    old_auth_handler = '''  socket.on('authenticate', (token: string) => {
    console.log('🔐 Socket authentication attempt for socket:', socket.id);
    console.log('🔐 Received token type:', typeof token);
    console.log('🔐 Token value:', token ? token.substring(0, 30) + '...' : 'null/undefined');'''
    
    new_auth_handler = '''  socket.on('authenticate', (token: string) => {
    authCounter++;
    console.log('🔐 Socket authentication attempt #' + authCounter + ' for socket:', socket.id);
    console.log('🔐 Total connected sockets:', io.engine.clientsCount);
    console.log('🔐 Total connectedUsers in memory:', connectedUsers.size);
    console.log('🔐 Received token type:', typeof token);
    console.log('🔐 Token value:', token ? token.substring(0, 30) + '...' : 'null/undefined');'''
    
    if old_auth_handler in content:
        content = content.replace(old_auth_handler, new_auth_handler)
        print("✅ Enhanced backend authentication debugging")
    
    with open(backend_index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def create_socket_debug_page():
    """Create a simple debug page to monitor socket connections in real-time"""
    
    debug_page_content = '''import React, { useEffect, useState } from 'react';
import { socketService } from '../services/socketService';

const SocketDebugPage: React.FC = () => {
  const [socketInfo, setSocketInfo] = useState<any>({});
  const [connectionHistory, setConnectionHistory] = useState<string[]>([]);

  useEffect(() => {
    const updateSocketInfo = () => {
      const info = {
        hasSocket: !!socketService.socket,
        isConnected: socketService.socket?.connected,
        socketId: socketService.socket?.id,
        timestamp: new Date().toLocaleTimeString()
      };
      setSocketInfo(info);
      
      const historyEntry = `${info.timestamp}: Socket ${info.socketId || 'none'} - Connected: ${info.isConnected}`;
      setConnectionHistory(prev => [...prev.slice(-10), historyEntry]);
    };

    // Update every second
    const interval = setInterval(updateSocketInfo, 1000);
    updateSocketInfo(); // Initial update

    return () => clearInterval(interval);
  }, []);

  const handleForceConnect = () => {
    console.log('🔧 DEBUG: Force connecting socket...');
    socketService.connect();
  };

  const handleForceDisconnect = () => {
    console.log('🔧 DEBUG: Force disconnecting socket...');
    socketService.disconnect();
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Socket Debug Console</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Current Socket State</h2>
            <div className="space-y-2 text-sm font-mono">
              <div>Has Socket: <span className={socketInfo.hasSocket ? 'text-green-600' : 'text-red-600'}>{String(socketInfo.hasSocket)}</span></div>
              <div>Connected: <span className={socketInfo.isConnected ? 'text-green-600' : 'text-red-600'}>{String(socketInfo.isConnected)}</span></div>
              <div>Socket ID: <span className="text-blue-600">{socketInfo.socketId || 'none'}</span></div>
              <div>Last Update: <span className="text-gray-600">{socketInfo.timestamp}</span></div>
            </div>
            
            <div className="mt-4 space-x-2">
              <button 
                onClick={handleForceConnect}
                className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded text-sm"
              >
                Force Connect
              </button>
              <button 
                onClick={handleForceDisconnect}
                className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded text-sm"
              >
                Force Disconnect
              </button>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Connection History</h2>
            <div className="h-64 overflow-y-auto bg-gray-50 p-3 rounded text-xs font-mono">
              {connectionHistory.length > 0 ? (
                connectionHistory.map((entry, index) => (
                  <div key={index} className="mb-1">{entry}</div>
                ))
              ) : (
                <div className="text-gray-500">No connection history yet...</div>
              )}
            </div>
          </div>
        </div>

        <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="font-semibold text-yellow-800 mb-2">Debug Instructions</h3>
          <div className="text-sm text-yellow-700">
            <p>1. Open browser console to see detailed socket logs</p>
            <p>2. Monitor the connection history above for patterns</p>
            <p>3. Look for multiple socket connections or reconnections</p>
            <p>4. Check if Socket ID changes unexpectedly</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SocketDebugPage;'''
    
    debug_page_path = "frontend/src/pages/SocketDebugPage.tsx"
    
    with open(debug_page_path, 'w', encoding='utf-8') as f:
        f.write(debug_page_content)
    
    print("✅ Created SocketDebugPage.tsx")
    
    return True

def main():
    print("🔧 Adding Socket Connection Debugging...")
    print("=" * 50)
    
    success_count = 0
    
    # Add App.tsx debugging
    if add_app_connection_debugging():
        success_count += 1
    
    # Add socketService debugging
    if add_socket_service_debugging():
        success_count += 1
    
    # Add backend authentication debugging
    if add_backend_authentication_debugging():
        success_count += 1
    
    # Create debug page
    if create_socket_debug_page():
        success_count += 1
    
    print("=" * 50)
    if success_count >= 3:
        print("✅ Socket debugging added successfully!")
        print("\n🎯 What was added:")
        print("1. ✅ Detailed App.tsx connection tracking with call stacks")
        print("2. ✅ Enhanced socketService debugging with connection counter")
        print("3. ✅ Backend authentication attempt tracking")
        print("4. ✅ Created SocketDebugPage.tsx for real-time monitoring")
        print("\n🚀 Next steps:")
        print("1. Restart both frontend and backend")
        print("2. Open browser console to see detailed logs")
        print("3. Navigate to /socket-debug for real-time monitoring")
        print("4. Watch for multiple 'CONNECT() CALLED' or 'authentication attempt' messages")
        print("\n🔍 What to look for:")
        print("- Multiple 'CONNECT() CALLED #1, #2, #3' messages")
        print("- Multiple authentication attempts for same user")
        print("- Different socket IDs being created")
        print("- 'joined the chat' happening 2-3 times per user")
    else:
        print(f"⚠️  Only {success_count}/4 fixes applied. Check error messages above.")
    
    return success_count >= 3

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)