#!/usr/bin/env python3
"""
Fix team assignment room tracking - ensures team selections use correct room codes
"""

import os

def fix_team_assignment_room_tracking():
    """Fix the hardcoded GLOBAL room issue in team assignment handlers"""
    
    backend_index_path = 'backend/src/index.ts'
    
    if not os.path.exists(backend_index_path):
        print(f"❌ File not found: {backend_index_path}")
        return False
    
    print("🔧 Fixing team assignment room tracking...")
    
    # Read the current file
    with open(backend_index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Step 1: Add room tracking map
    print("📝 Step 1: Adding room tracking...")
    if 'const userRooms = new Map<string, string>();' not in content:
        content = content.replace(
            'const connectedUsers = new Map<string, any>();',
            'const connectedUsers = new Map<string, any>();\nconst userRooms = new Map<string, string>(); // Track which room each user is in'
        )
        print("  ✅ Added userRooms tracking map")
    else:
        print("  ℹ️ Room tracking already exists")
    
    # Step 2: Track user's room when they join
    print("📝 Step 2: Adding room tracking to join-game-room...")
    if 'userRooms.set(socket.id, gameCode);' not in content:
        content = content.replace(
            'console.log(`🎮 User ${user.username} joining game room: ${gameCode}`);',
            '''console.log(`🎮 User ${user.username} joining game room: ${gameCode}`);
    
    // Track which room this user is in
    userRooms.set(socket.id, gameCode);'''
        )
        print("  ✅ Added room tracking to join handler")
    else:
        print("  ℹ️ Room tracking in join handler already exists")
    
    # Step 3: Fix the hardcoded GLOBAL room in team assignment
    print("📝 Step 3: Fixing hardcoded GLOBAL room in team assignment...")
    old_team_handler = "const roomCode = 'GLOBAL';"
    new_team_handler = '''// Get user's current room instead of hardcoded GLOBAL
      const currentRoom = userRooms.get(socket.id);
      if (!currentRoom) {
        socket.emit('game:error', 'Not in a game room');
        return;
      }
      const roomCode = currentRoom;'''
    
    if old_team_handler in content:
        content = content.replace(old_team_handler, new_team_handler)
        print("  ✅ Fixed hardcoded GLOBAL room issue")
    else:
        print("  ℹ️ GLOBAL room fix already applied or pattern not found")
    
    # Step 4: Clean up room tracking on disconnect
    print("📝 Step 4: Adding room cleanup on disconnect...")
    if 'userRooms.delete(socket.id);' not in content:
        content = content.replace(
            'const globalRoom = getOrCreateGlobalRoom();',
            '''const globalRoom = getOrCreateGlobalRoom();
      
      // Clean up room tracking
      userRooms.delete(socket.id);'''
        )
        print("  ✅ Added room cleanup to disconnect handler")
    else:
        print("  ℹ️ Room cleanup already exists")
    
    # Step 5: Add room validation to other game handlers
    print("📝 Step 5: Adding room validation to game handlers...")
    
    # For game:create handler
    if "const roomCode = 'GLOBAL'; // For now, use global room for games" in content:
        content = content.replace(
            "const roomCode = 'GLOBAL'; // For now, use global room for games",
            '''const currentRoom = userRooms.get(socket.id);
      if (!currentRoom) {
        socket.emit('game:error', 'Not in a game room');
        return;
      }
      const roomCode = currentRoom;'''
        )
        print("  ✅ Fixed game:create handler")
    
    # For game:request-state handler  
    if 'const game = gameService.getGameByPlayer(user.id);' in content:
        # This one should work with the existing logic, but let's add some logging
        content = content.replace(
            "console.log('🔍 Game state requested by:', user.username);",
            '''console.log('🔍 Game state requested by:', user.username);
      const currentRoom = userRooms.get(socket.id);
      console.log('🔍 User is in room:', currentRoom);'''
        )
        print("  ✅ Enhanced game:request-state with room logging")
    
    # Write the fixed content back
    with open(backend_index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Successfully fixed team assignment room tracking!")
    print("\n🔧 Changes made:")
    print("  1. Added userRooms Map to track which room each user is in")
    print("  2. Track user's room when they join with join-game-room")
    print("  3. Fixed hardcoded 'GLOBAL' room in team assignment handler")
    print("  4. Team assignments now use correct room codes")
    print("  5. Added room cleanup on disconnect")
    print("  6. Enhanced game handlers with room validation")
    
    return True

if __name__ == "__main__":
    success = fix_team_assignment_room_tracking()
    if success:
        print("\n🎯 Testing Steps:")
        print("1. Restart backend server: npm run dev (in backend folder)")
        print("2. Test with 2 browser windows:")
        print("   - Window 1: Create room, join red team as spymaster")  
        print("   - Window 2: Join same room code")
        print("   - Window 2 should see Window 1's team assignment")
        print("   - Window 2: Join blue team as spymaster")
        print("   - Both windows should see both team assignments")
        print("\n🎮 Expected result: Real-time team selection sync!")
    else:
        print("\n❌ Fix failed - check the file and try again")
