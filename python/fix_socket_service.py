#!/usr/bin/env python3
"""
Fix socketService to prevent multiple connections and improve connection handling
"""

import os

def fix_socket_service():
    """Fix socketService to handle connections properly"""
    
    socket_service_path = 'frontend/src/services/socketService.ts'
    
    if not os.path.exists(socket_service_path):
        print(f"❌ File not found: {socket_service_path}")
        return False
    
    print("🔧 Fixing socketService multiple connection issues...")
    
    # Read the current file
    with open(socket_service_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add connection state tracking
    if 'private token: string | null = null;' in content:
        content = content.replace(
            'private token: string | null = null;',
            '''private token: string | null = null;
  private isConnecting: boolean = false; // Track connection in progress'''
        )
        print("  ✅ Added isConnecting state tracking")
    
    # Fix the connect method to prevent multiple connections
    old_connect = '''  connect(): Socket {
    // Make socket service accessible for debugging
    (window as any).socketService = this;

    if (this._socket?.connected) {
      console.log('📡 Socket already connected');
      return this._socket;
    }

    const socketUrl = import.meta.env.VITE_SOCKET_URL || 'http://localhost:3001';
    console.log('📡 Connecting to socket server:', socketUrl);

    this._socket = io(socketUrl, {
      autoConnect: false,
      transports: ['websocket', 'polling'],
      timeout: 5000,
      forceNew: true,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000
    });

    this.setupEventListeners();
    this._socket.connect();

    return this._socket;
  }'''
    
    new_connect = '''  connect(): Socket {
    // Make socket service accessible for debugging
    (window as any).socketService = this;

    // Check if already connected
    if (this._socket?.connected) {
      console.log('📡 Socket already connected, reusing existing connection');
      return this._socket;
    }

    // Check if connection is in progress
    if (this.isConnecting) {
      console.log('📡 Connection already in progress, waiting...');
      return this._socket!;
    }

    // Check if socket exists but is disconnected
    if (this._socket && !this._socket.connected) {
      console.log('📡 Reconnecting existing socket');
      this._socket.connect();
      return this._socket;
    }

    console.log('📡 Creating new socket connection');
    this.isConnecting = true;

    const socketUrl = import.meta.env.VITE_SOCKET_URL || 'http://localhost:3001';
    console.log('📡 Connecting to socket server:', socketUrl);

    this._socket = io(socketUrl, {
      autoConnect: false,
      transports: ['websocket', 'polling'],
      timeout: 5000,
      forceNew: false, // Don't force new connections
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000
    });

    this.setupEventListeners();
    this._socket.connect();

    return this._socket;
  }'''
    
    if old_connect in content:
        content = content.replace(old_connect, new_connect)
        print("  ✅ Fixed connect() method to prevent multiple connections")
    
    # Update setupEventListeners to handle connection state
    old_setup = '''  private setupEventListeners(): void {
    if (!this._socket) return;

    this._socket.on('connect', () => {
      console.log('✅ Connected to server, Socket ID:', this._socket?.id);
      // Re-authenticate if we have a token
      if (this.token) {
        console.log('🔐 Re-authenticating after reconnection');
        this.authenticate(this.token);
      }
    });'''
    
    new_setup = '''  private setupEventListeners(): void {
    if (!this._socket) return;

    this._socket.on('connect', () => {
      console.log('✅ Connected to server, Socket ID:', this._socket?.id);
      this.isConnecting = false; // Connection completed
      
      // Re-authenticate if we have a token
      if (this.token) {
        console.log('🔐 Re-authenticating after reconnection');
        this.authenticate(this.token);
      }
    });'''
    
    if old_setup in content:
        content = content.replace(old_setup, new_setup)
        print("  ✅ Updated setupEventListeners to track connection state")
    
    # Update disconnect method to reset connection state
    old_disconnect = '''  disconnect(): void {
    if (this._socket) {
      console.log('📡 Disconnecting socket');
      this._socket.disconnect();
      this._socket = null;
    }
  }'''
    
    new_disconnect = '''  disconnect(): void {
    if (this._socket) {
      console.log('📡 Disconnecting socket');
      this._socket.disconnect();
      this._socket = null;
      this.isConnecting = false; // Reset connection state
    }
  }'''
    
    if old_disconnect in content:
        content = content.replace(old_disconnect, new_disconnect)
        print("  ✅ Updated disconnect() to reset connection state")
    
    # Add connection error handling to reset state
    if "this._socket.on('connect_error', (error) => {" in content:
        old_error = '''    this._socket.on('connect_error', (error) => {
      console.error('🚫 Socket connection error:', error);
    });'''
        
        new_error = '''    this._socket.on('connect_error', (error) => {
      console.error('🚫 Socket connection error:', error);
      this.isConnecting = false; // Reset on connection error
    });'''
        
        content = content.replace(old_error, new_error)
        print("  ✅ Added connection error state reset")
    
    # Add method to check if connection is ready
    if 'get isConnected(): boolean {' in content:
        content = content.replace(
            '''get isConnected(): boolean {
    return this._socket?.connected || false;
  }''',
            '''get isConnected(): boolean {
    return this._socket?.connected || false;
  }

  get isConnectionReady(): boolean {
    return this._socket?.connected && !this.isConnecting;
  }'''
        )
        print("  ✅ Added isConnectionReady getter")
    
    # Write the fixed content back
    with open(socket_service_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Fixed socketService connection issues!")
    print("\n🔧 Changes made:")
    print("  1. Added isConnecting state to prevent duplicate connection attempts")
    print("  2. Removed forceNew: true to allow connection reuse")
    print("  3. Added proper connection state management")
    print("  4. Added connection error handling")
    print("  5. Added isConnectionReady getter for better state checking")
    
    return True

if __name__ == "__main__":
    success = fix_socket_service()
    if success:
        print("\n🎯 Expected Results:")
        print("1. Only ONE socket connection per browser tab")
        print("2. Proper connection state tracking")
        print("3. No duplicate connections during reconnects")
        print("4. Clean connection logs")
        print("\n🧪 Test Steps:")
        print("1. Run both frontend and backend fixes")
        print("2. Restart backend server")
        print("3. Open browser console and watch connection logs")
        print("4. Should see single 'Creating new socket connection' message")
        print("5. Test team assignment with 2 players")
    else:
        print("\n❌ SocketService fix failed - check the file and try again")
