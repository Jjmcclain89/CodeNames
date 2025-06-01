#!/usr/bin/env python3
"""
Fix the real issue: prevent multiple socket connections from being created
"""

import os

def fix_multiple_connections():
    """Fix multiple socket connections being created for the same user"""
    
    room_page_path = 'frontend/src/pages/RoomPage.tsx'
    
    if not os.path.exists(room_page_path):
        print(f"❌ File not found: {room_page_path}")
        return False
    
    print("🔧 Fixing multiple socket connections...")
    
    # Read the current file
    with open(room_page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add connection state tracking
    connection_state_add = '''  const [isConnected, setIsConnected] = useState(false);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [gameStarted, setGameStarted] = useState(false);
  const [gameState, setGameState] = useState<any>(null);
  const [connectionInitiated, setConnectionInitiated] = useState(false); // Prevent multiple connections'''
    
    if '[gameState, setGameState] = useState<any>(null);' in content:
        content = content.replace(
            '[gameState, setGameState] = useState<any>(null);',
            '''[gameState, setGameState] = useState<any>(null);
  const [connectionInitiated, setConnectionInitiated] = useState(false); // Prevent multiple connections'''
        )
        print("  ✅ Added connection tracking state")
    
    # Fix the main useEffect to run only once and prevent multiple connections
    old_useeffect = '''useEffect(() => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    setCurrentUser(user);
    loadGameAndConnect();
    
    // Cleanup on unmount
    return () => {
      gameService.removeAllGameListeners();
      if (socketService.socket) {
        socketService.socket.off('player-joined-room');
        socketService.socket.off('room-state');
        socketService.socket.off('new-room-message');
      }
    };
  }, [roomCode]);'''
    
    new_useeffect = '''useEffect(() => {
    if (!roomCode || connectionInitiated) {
      console.log('🔍 Skipping connection - already initiated or no room code');
      return;
    }
    
    console.log('🔌 Starting connection process for room:', roomCode);
    setConnectionInitiated(true);
    
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    setCurrentUser(user);
    loadGameAndConnect();
    
    // Cleanup on unmount
    return () => {
      console.log('🧹 Cleaning up connections');
      gameService.removeAllGameListeners();
      if (socketService.socket) {
        socketService.socket.off('player-joined-room');
        socketService.socket.off('room-state');
        socketService.socket.off('new-room-message');
      }
      setConnectionInitiated(false);
    };
  }, [roomCode]); // Only depend on roomCode'''
    
    if old_useeffect in content:
        content = content.replace(old_useeffect, new_useeffect)
        print("  ✅ Fixed useEffect to prevent multiple connections")
    
    # Fix connectToRoom to check if already connected
    if 'const connectToRoom = async (gameCode: string, token: string, user: any) => {' in content:
        old_connect = '''const connectToRoom = async (gameCode: string, token: string, user: any) => {
    console.log('🔌 Connecting to room socket...', gameCode);
    
    return new Promise<void>((resolve) => {
      // Ensure socket is connected and authenticated
      if (!socketService.socket?.connected) {
        socketService.connect();
      }'''
        
        new_connect = '''const connectToRoom = async (gameCode: string, token: string, user: any) => {
    console.log('🔌 Connecting to room socket...', gameCode);
    
    // Check if already connected to this room
    if (isConnected && socketService.socket?.connected) {
      console.log('🔍 Already connected to socket, skipping connection');
      return Promise.resolve();
    }
    
    return new Promise<void>((resolve) => {
      // Ensure socket is connected and authenticated
      if (!socketService.socket?.connected) {
        console.log('🔌 Creating new socket connection');
        socketService.connect();
      } else {
        console.log('🔌 Reusing existing socket connection');
      }'''
        
        if old_connect in content:
            content = content.replace(old_connect, new_connect)
            print("  ✅ Added connection state checking to connectToRoom")
    
    # Fix game creation to only happen once
    if "gameService.createGame(); // This will create or join existing game" in content:
        old_game_create = '''        // Create or join game in the backend
        console.log('🎮 Creating/joining game for room:', gameCode);
        gameService.createGame(); // This will create or join existing game'''
        
        new_game_create = '''        // Create or join game in the backend (only once per connection)
        console.log('🎮 Creating/joining game for room:', gameCode);
        if (!gameState) {
          console.log('🎮 No existing game state, creating/joining game');
          gameService.createGame(); // This will create or join existing game
        } else {
          console.log('🎮 Game state already exists, skipping creation');
        }'''
        
        content = content.replace(old_game_create, new_game_create)
        print("  ✅ Added game state checking to prevent duplicate creation")
    
    # Write the fixed content back
    with open(room_page_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Fixed multiple socket connections!")
    print("\n🔧 Changes made:")
    print("  1. Added connectionInitiated flag to prevent multiple useEffect runs")
    print("  2. Added connection state checking in connectToRoom")
    print("  3. Added game state checking to prevent duplicate game creation")
    print("  4. Improved logging to track connection process")
    
    return True

if __name__ == "__main__":
    success = fix_multiple_connections()
    if success:
        print("\n🎯 Expected Results:")
        print("1. Only ONE socket connection per user per room")
        print("2. Only ONE game created per room")
        print("3. Clean console logs without duplicates")
        print("4. Stable player state when multiple users join")
        print("\n🧪 Test Steps:")
        print("1. Restart backend server")
        print("2. Check console - should see single connection messages")
        print("3. Player 1: Create room and join team")
        print("4. Player 2: Join room - Player 1 should stay on team")
        print("5. Both players can select teams without conflicts")
    else:
        print("\n❌ Multiple connection fix failed - check the file and try again")
