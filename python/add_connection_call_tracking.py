#!/usr/bin/env python3
"""
Add debug logging to track what is calling socketService.connect()
"""

import os

def add_connection_call_tracking():
    """Add debug logging to track connection calls"""
    
    socket_service_path = 'frontend/src/services/socketService.ts'
    
    if not os.path.exists(socket_service_path):
        print(f"❌ File not found: {socket_service_path}")
        return False
    
    print("🔧 Adding connection call tracking to socketService...")
    
    # Read the current file
    with open(socket_service_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add call tracking to the connect method
    old_connect_start = '''  connect(): Socket {
    // Make socket service accessible for debugging
    (window as any).socketService = this;

    // Check if already connected
    if (this._socket?.connected) {
      console.log('📡 Socket already connected, reusing existing connection');
      return this._socket;
    }'''
    
    new_connect_start = '''  connect(): Socket {
    // Track what is calling connect
    console.log('🔌 CONNECT() CALLED');
    console.log('🔌 Call stack:', new Error().stack);
    console.log('🔌 Current socket state:', {
      hasSocket: !!this._socket,
      isConnected: this._socket?.connected,
      isConnecting: this.isConnecting
    });

    // Make socket service accessible for debugging
    (window as any).socketService = this;

    // Check if already connected
    if (this._socket?.connected) {
      console.log('📡 Socket already connected, reusing existing connection');
      return this._socket;
    }'''
    
    if old_connect_start in content:
        content = content.replace(old_connect_start, new_connect_start)
        print("  ✅ Added connection call tracking")
    else:
        print("  ⚠️ Could not find connect method start to patch")
    
    # Add tracking to setupEventListeners connect event
    old_connect_event = '''    this._socket.on('connect', () => {
      console.log('✅ Connected to server, Socket ID:', this._socket?.id);
      this.isConnecting = false; // Connection completed
      
      // Re-authenticate if we have a token
      if (this.token) {
        console.log('🔐 Re-authenticating after reconnection');
        this.authenticate(this.token);
      }
    });'''
    
    new_connect_event = '''    this._socket.on('connect', () => {
      console.log('✅ Connected to server, Socket ID:', this._socket?.id);
      console.log('🔌 Connect event fired - total event listeners:', this._socket?.listeners('connect').length);
      this.isConnecting = false; // Connection completed
      
      // Re-authenticate if we have a token
      if (this.token) {
        console.log('🔐 Re-authenticating after reconnection');
        this.authenticate(this.token);
      }
    });'''
    
    if old_connect_event in content:
        content = content.replace(old_connect_event, new_connect_event)
        print("  ✅ Added connect event tracking")
    
    # Write the enhanced content back
    with open(socket_service_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Added connection call tracking!")
    print("\n🔧 Debug features added:")
    print("  1. Stack trace showing what code calls connect()")
    print("  2. Socket state logging before each connect attempt")
    print("  3. Event listener count tracking")
    
    return True

if __name__ == "__main__":
    success = add_connection_call_tracking()
    if success:
        print("\n🎯 Testing Steps:")
        print("1. Refresh the homepage")
        print("2. Open browser console immediately")
        print("3. Look for '🔌 CONNECT() CALLED' messages")
        print("4. Check the stack traces to see what's calling connect")
        print("5. Report findings - what code is calling connect() twice?")
        print("\n📋 What to look for:")
        print("  - How many '🔌 CONNECT() CALLED' messages appear")
        print("  - What files/functions are in the stack traces")
        print("  - Whether it's React StrictMode, ChatRoom, or something else")
    else:
        print("\n❌ Call tracking failed - check the file and try again")
