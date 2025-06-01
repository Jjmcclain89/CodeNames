#!/usr/bin/env python3
"""
Add debug logging to track game state when players join/leave teams
"""

import os

def add_debug_logging():
    """Add detailed logging to track game state issues"""
    
    backend_index_path = 'backend/src/index.ts'
    
    if not os.path.exists(backend_index_path):
        print(f"❌ File not found: {backend_index_path}")
        return False
    
    print("🔧 Adding debug logging for game state tracking...")
    
    # Read the current file
    with open(backend_index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add logging to join-game-room when game state is sent
    if "// Always send current game state to the player" in content:
        debug_join_room = '''// Always send current game state to the player
      const gameState = game.getGame();
      console.log('🎮 BEFORE sending game state to:', user.username);
      console.log('🎮 Game players:', gameState.players.map(p => `${p.username}(${p.team}/${p.role})`));
      socket.emit('game:state-updated', gameState);
      
      // Also send to others in the room
      console.log('🎮 Broadcasting game state to room:', gameCode);
      socket.to(gameCode).emit('game:state-updated', gameState);'''
        
        content = content.replace(
            '''// Always send current game state to the player
      const gameState = game.getGame();
      socket.emit('game:state-updated', gameState);
      
      // Also send to others in the room
      socket.to(gameCode).emit('game:state-updated', gameState);''',
            debug_join_room
        )
        print("  ✅ Added debug logging to join-game-room")
    
    # Add logging to game:join-team handler
    if "const result = gameService.assignPlayerToTeam(user.id, team as any, role as any);" in content:
        debug_team_join = '''console.log('🎮 BEFORE team assignment:');
      console.log('🎮 User:', user.username, 'ID:', user.id);
      console.log('🎮 Attempting to join team:', team, 'as', role);
      console.log('🎮 Current room:', currentRoom);
      
      // Check if player exists in game before assignment
      const existingGame = gameService.getGameByPlayer(user.id);
      console.log('🎮 Player exists in game:', !!existingGame);
      if (existingGame) {
        const existingState = existingGame.getGame();
        console.log('🎮 Existing game players:', existingState.players.map(p => `${p.username}(${p.team}/${p.role})`));
      }
      
      const result = gameService.assignPlayerToTeam(user.id, team as any, role as any);
      
      console.log('🎮 AFTER team assignment:');
      console.log('🎮 Assignment result:', result);'''
        
        content = content.replace(
            'const result = gameService.assignPlayerToTeam(user.id, team as any, role as any);',
            debug_team_join
        )
        print("  ✅ Added debug logging to team assignment")
    
    # Add logging to game state broadcast
    if "io.to(currentRoom).emit('game:state-updated', gameState);" in content:
        debug_broadcast = '''const gameState = game.getGame();
        console.log('🎮 Broadcasting updated game state:');
        console.log('🎮 Room:', currentRoom);
        console.log('🎮 Players after assignment:', gameState.players.map(p => `${p.username}(${p.team}/${p.role})`));
        io.to(currentRoom).emit('game:state-updated', gameState);'''
        
        content = content.replace(
            '''const gameState = game.getGame();
        io.to(currentRoom).emit('game:state-updated', gameState);''',
            debug_broadcast
        )
        print("  ✅ Added debug logging to state broadcast")
    
    # Add logging to addPlayerToGame call
    if "const success = gameService.addPlayerToGame(game.getId(), user.id, user.username, socket.id);" in content:
        debug_add_player = '''console.log('🎮 Adding player to game:');
      console.log('🎮 Game ID:', game.getId());
      console.log('🎮 User:', user.username, 'ID:', user.id, 'Socket:', socket.id);
      const success = gameService.addPlayerToGame(game.getId(), user.id, user.username, socket.id);
      console.log('🎮 Add player result:', success);'''
        
        content = content.replace(
            'const success = gameService.addPlayerToGame(game.getId(), user.id, user.username, socket.id);',
            debug_add_player
        )
        print("  ✅ Added debug logging to addPlayerToGame")
    
    # Write the enhanced content back
    with open(backend_index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Successfully added debug logging!")
    print("\n🔧 Debug logging added to:")
    print("  1. join-game-room handler - shows game state when players join")
    print("  2. game:join-team handler - shows before/after team assignment")
    print("  3. State broadcasting - shows what's being sent to clients")
    print("  4. addPlayerToGame calls - shows player addition process")
    
    return True

if __name__ == "__main__":
    success = add_debug_logging()
    if success:
        print("\n🎯 Testing Steps:")
        print("1. Restart backend server: npm run dev")
        print("2. Open browser console to see detailed logs")
        print("3. Test the Player 1 → Player 2 join sequence")
        print("4. Look for patterns in the logs that show when Player 1 gets removed")
        print("\n📋 Look for these patterns:")
        print("  - Does Player 1 disappear when Player 2 joins?")
        print("  - Are there multiple games being created?")
        print("  - Do socket IDs change unexpectedly?")
    else:
        print("\n❌ Debug logging failed - check the file and try again")
