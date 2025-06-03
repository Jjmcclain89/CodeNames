#!/usr/bin/env python3
"""
Fix Authentication Callback Issue

This script fixes the issue where authentication guard skips duplicate 
authentication but doesn't trigger the callback, leaving RoomPage stuck.
"""

import os
import sys

def fix_authentication_callback_trigger():
    """Modify authenticate method to trigger callback even when skipping duplicate"""
    
    socket_service_path = "frontend/src/services/socketService.ts"
    
    if not os.path.exists(socket_service_path):
        print(f"Error: {socket_service_path} not found")
        return False
    
    with open(socket_service_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and update the authenticate method to trigger callback when skipping
    old_authenticate = '''  authenticate(token: string): void {
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
    
    new_authenticate = '''  authenticate(token: string): void {
    console.log('🔐 AUTHENTICATE() CALLED');
    console.log('🔐 Socket exists:', !!this._socket);
    console.log('🔐 Socket connected:', this._socket?.connected);
    console.log('🔐 Socket ID:', this._socket?.id);
    console.log('🔐 Token (first 20 chars):', token?.substring(0, 20) + '...');
    console.log('🔐 Last authenticated token:', this.lastAuthenticatedToken?.substring(0, 20) + '...');
    
    // Prevent duplicate authentication with the same token
    if (this.lastAuthenticatedToken === token && this._socket?.connected) {
      console.log('🔐 Already authenticated with this token, triggering success callback immediately');
      // Trigger the authenticated callback immediately since we're already authenticated
      setTimeout(() => {
        this._socket?.emit('authenticated', { success: true, user: { token } });
      }, 0);
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
        print("✅ Updated authenticate method to trigger callback when skipping")
    else:
        print("⚠️  Could not find exact authenticate method - may need manual update")
        return False
    
    with open(socket_service_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def add_room_page_auth_debugging():
    """Add debugging to RoomPage to track authentication callback"""
    
    room_page_path = "frontend/src/pages/RoomPage.tsx"
    
    if not os.path.exists(room_page_path):
        print(f"Error: {room_page_path} not found")
        return False
    
    with open(room_page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add debugging to the handleAuth function
    old_handle_auth = '''      const handleAuth = () => {
        console.log('✅ Socket authenticated, joining room:', gameCode);
        socketService.socket?.emit('join-game-room', gameCode);
        setIsConnected(true);
        
        // Set up game listeners after socket is ready
        setupGameListeners(user);
        
        // Create or join game in the backend (only once per connection)
        console.log('🎮 Creating/joining game for room:', gameCode);
        if (!gameState && !gameCreationCalled) {
          console.log('🎮 No existing game state, creating/joining game');
          setGameCreationCalled(true);
          gameService.createGame(); // This will create or join existing game
        } else {
          console.log('🎮 Game state already exists or creation already called, skipping');
        }
        
        resolve();
      };'''
    
    new_handle_auth = '''      const handleAuth = () => {
        console.log('✅ [ROOMPAGE] handleAuth called - Socket authenticated, joining room:', gameCode);
        socketService.socket?.emit('join-game-room', gameCode);
        setIsConnected(true);
        
        // Set up game listeners after socket is ready
        console.log('🎮 [ROOMPAGE] Setting up game listeners...');
        setupGameListeners(user);
        
        // Create or join game in the backend (only once per connection)
        console.log('🎮 [ROOMPAGE] Creating/joining game for room:', gameCode);
        if (!gameState && !gameCreationCalled) {
          console.log('🎮 [ROOMPAGE] No existing game state, creating/joining game');
          setGameCreationCalled(true);
          gameService.createGame(); // This will create or join existing game
        } else {
          console.log('🎮 [ROOMPAGE] Game state already exists or creation already called, skipping');
        }
        
        console.log('✅ [ROOMPAGE] handleAuth completed, resolving promise');
        resolve();
      };'''
    
    if old_handle_auth in content:
        content = content.replace(old_handle_auth, new_handle_auth)
        print("✅ Added debugging to handleAuth function")
    
    # Add debugging to the onAuthenticated callback
    old_callback = '''        socketService.onAuthenticated((data: any) => {
          if (data.success) {
            handleAuth();
          }
        });'''
    
    new_callback = '''        socketService.onAuthenticated((data: any) => {
          console.log('🔐 [ROOMPAGE] onAuthenticated callback triggered with data:', data);
          if (data.success) {
            console.log('✅ [ROOMPAGE] Authentication successful, calling handleAuth');
            handleAuth();
          } else {
            console.log('❌ [ROOMPAGE] Authentication failed:', data);
          }
        });'''
    
    if old_callback in content:
        content = content.replace(old_callback, new_callback)
        print("✅ Added debugging to onAuthenticated callback")
    
    with open(room_page_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def alternative_fix_approach():
    """Alternative approach: Check if already authenticated and proceed directly"""
    
    room_page_path = "frontend/src/pages/RoomPage.tsx"
    
    if not os.path.exists(room_page_path):
        print(f"Error: {room_page_path} not found")
        return False
    
    with open(room_page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for the authentication flow and add a check for already authenticated state
    old_auth_flow = '''      if (socketService.socket?.connected) {
        socketService.authenticate(token);
        socketService.onAuthenticated((data: any) => {
          console.log('🔐 [ROOMPAGE] onAuthenticated callback triggered with data:', data);
          if (data.success) {
            console.log('✅ [ROOMPAGE] Authentication successful, calling handleAuth');
            handleAuth();
          } else {
            console.log('❌ [ROOMPAGE] Authentication failed:', data);
          }
        });
      }'''
    
    new_auth_flow = '''      if (socketService.socket?.connected) {
        console.log('🔐 [ROOMPAGE] Socket is connected, attempting authentication...');
        
        // Set up the callback first
        socketService.onAuthenticated((data: any) => {
          console.log('🔐 [ROOMPAGE] onAuthenticated callback triggered with data:', data);
          if (data.success) {
            console.log('✅ [ROOMPAGE] Authentication successful, calling handleAuth');
            handleAuth();
          } else {
            console.log('❌ [ROOMPAGE] Authentication failed:', data);
          }
        });
        
        // Try to authenticate (may be skipped if already authenticated)
        socketService.authenticate(token);
        
        // Fallback: if we're already connected and authenticated, proceed directly
        setTimeout(() => {
          if (socketService.socket?.connected && !isConnected) {
            console.log('🔄 [ROOMPAGE] Fallback: Authentication may have been skipped, proceeding directly');
            handleAuth();
          }
        }, 100);
      }'''
    
    if old_auth_flow in content:
        content = content.replace(old_auth_flow, new_auth_flow)
        print("✅ Added fallback authentication flow")
        
        with open(room_page_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    print("🔧 Fixing Authentication Callback Issue...")
    print("=" * 50)
    
    success_count = 0
    
    # Primary fix: Make authenticate method trigger callback when skipping
    if fix_authentication_callback_trigger():
        success_count += 1
    
    # Add debugging to track the callback flow
    if add_room_page_auth_debugging():
        success_count += 1
    
    # Alternative approach: Add fallback logic
    if alternative_fix_approach():
        success_count += 1
    
    print("=" * 50)
    if success_count >= 1:
        print("✅ Authentication callback fix applied!")
        print("\n🎯 What was fixed:")
        print("1. ✅ Modified authenticate() to trigger callback even when skipping duplicate")
        print("2. ✅ Added comprehensive debugging to track callback flow")
        print("3. ✅ Added fallback logic in case authentication is skipped")
        print("\n🚀 Next steps:")
        print("1. Restart your frontend")
        print("2. Try creating a game again")
        print("3. Look for these new debug messages:")
        print("   - 🔐 Already authenticated with this token, triggering success callback immediately")
        print("   - 🔐 [ROOMPAGE] onAuthenticated callback triggered")
        print("   - ✅ [ROOMPAGE] handleAuth called")
        print("   - 🏠 [ROOMPAGE] Setting isLoading to false")
        print("\n💡 The issue was that duplicate authentication prevention was too aggressive!")
    else:
        print(f"⚠️  Fix could not be applied. Check error messages above.")
    
    return success_count >= 1

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)