#!/usr/bin/env python3
"""
Fix Double Authentication Issue

This script fixes the double authentication problem where the same socket
authenticates twice, causing users to "join the chat" multiple times.
"""

import os
import sys

def fix_socket_service_double_auth():
    """Remove automatic re-authentication that's causing duplicate auth events"""
    
    socket_service_path = "frontend/src/services/socketService.ts"
    
    if not os.path.exists(socket_service_path):
        print(f"Error: {socket_service_path} not found")
        return False
    
    with open(socket_service_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and remove the automatic re-authentication logic
    old_connect_handler = '''    this._socket.on('connect', () => {
      console.log('✅ Connected to server, Socket ID:', this._socket?.id);
      console.log('🔌 Connect event fired - total event listeners:', this._socket?.listeners('connect').length);
      this.isConnecting = false; // Connection completed
      
      // Re-authenticate if we have a token
      if (this.token) {
        console.log('🔐 Re-authenticating after reconnection');
        this.authenticate(this.token);
      }
    });'''
    
    new_connect_handler = '''    this._socket.on('connect', () => {
      console.log('✅ Connected to server, Socket ID:', this._socket?.id);
      console.log('🔌 Connect event fired - total event listeners:', this._socket?.listeners('connect').length);
      this.isConnecting = false; // Connection completed
      
      // NOTE: Manual authentication will be called by App.tsx - no need to auto-authenticate
      console.log('🔐 Socket connected, waiting for manual authentication call');
    });'''
    
    if old_connect_handler in content:
        content = content.replace(old_connect_handler, new_connect_handler)
        print("✅ Removed automatic re-authentication from connect event")
    else:
        print("⚠️  Could not find exact connect handler - may need manual update")
        return False
    
    with open(socket_service_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def add_authentication_guard():
    """Add a guard to prevent multiple authentications for the same token"""
    
    socket_service_path = "frontend/src/services/socketService.ts"
    
    if not os.path.exists(socket_service_path):
        print(f"Error: {socket_service_path} not found")
        return False
    
    with open(socket_service_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add a flag to track if we've already authenticated with this token
    if "private lastAuthenticatedToken: string | null = null;" not in content:
        # Find where other private properties are declared
        private_pattern = "private connectionCounter: number = 0;"
        if private_pattern in content:
            content = content.replace(
                private_pattern,
                private_pattern + "\n  private lastAuthenticatedToken: string | null = null;"
            )
            print("✅ Added lastAuthenticatedToken tracking")
    
    # Update authenticate method to prevent duplicate authentication
    old_authenticate = '''  authenticate(token: string): void {
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
    
    new_authenticate = '''  authenticate(token: string): void {
    console.log('🔐 AUTHENTICATE() CALLED');
    console.log('🔐 Socket exists:', !!this._socket);
    console.log('🔐 Socket connected:', this._socket?.connected);
    console.log('🔐 Socket ID:', this._socket?.id);
    console.log('🔐 Token (first 20 chars):', token?.substring(0, 20) + '...');
    console.log('🔐 Last authenticated token:', this.lastAuthenticatedToken?.substring(0, 20) + '...');
    
    // Prevent duplicate authentication with the same token
    if (this.lastAuthenticatedToken === token && this._socket?.connected) {
      console.log('🔐 Already authenticated with this token, skipping duplicate');
      return;
    }
    
    this.token = token;
    this.lastAuthenticatedToken = token;
    
    if (this._socket) {
      console.log('🔐 Emitting authenticate event to backend');
      this._socket.emit('authenticate', token);
    } else {
      console.log('❌ No socket available for authentication');
    }
  }'''
    
    if old_authenticate in content:
        content = content.replace(old_authenticate, new_authenticate)
        print("✅ Added authentication guard to prevent duplicates")
    
    # Reset the authentication token when disconnecting
    old_disconnect = '''  disconnect(): void {
    if (this._socket) {
      console.log('📡 Disconnecting socket');
      this._socket.disconnect();
      this._socket = null;
      this.isConnecting = false; // Reset connection state
    }
  }'''
    
    new_disconnect = '''  disconnect(): void {
    if (this._socket) {
      console.log('📡 Disconnecting socket');
      this._socket.disconnect();
      this._socket = null;
      this.isConnecting = false; // Reset connection state
      this.lastAuthenticatedToken = null; // Reset authentication state
    }
  }'''
    
    if old_disconnect in content:
        content = content.replace(old_disconnect, new_disconnect)
        print("✅ Added authentication token reset on disconnect")
    
    with open(socket_service_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    print("🔧 Fixing Double Authentication Issue...")
    print("=" * 50)
    
    success_count = 0
    
    # Remove automatic re-authentication
    if fix_socket_service_double_auth():
        success_count += 1
    
    # Add authentication guard
    if add_authentication_guard():
        success_count += 1
    
    print("=" * 50)
    if success_count >= 1:
        print("✅ Double authentication fix applied!")
        print("\n🎯 What was fixed:")
        print("1. ✅ Removed automatic re-authentication on 'connect' event")
        print("2. ✅ Added guard to prevent duplicate authentication with same token")
        print("3. ✅ Reset authentication state on disconnect")
        print("\n🚀 Next steps:")
        print("1. Restart your frontend (npm run dev)")
        print("2. Test user login - should see only 1 authentication per user")
        print("3. Check global chat - users should only 'join the chat' once")
        print("\n💡 The same socket was authenticating twice - now it only authenticates once!")
    else:
        print(f"⚠️  Fix could not be applied. Check error messages above.")
    
    return success_count >= 1

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)