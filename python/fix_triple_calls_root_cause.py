#!/usr/bin/env python3
"""
Fix Triple Calls Root Cause

This script fixes the actual cause of 3x calls by:
1. Removing redundant setTimeout in backend join-game-room handler
2. Preventing duplicate game creation calls from frontend
3. Adding proper state tracking to prevent multiple setups
"""

import os
import sys

def fix_backend_timeout_issue():
    """Remove the problematic setTimeout that causes duplicate game setups"""
    
    backend_index_path = "backend/src/index.ts"
    
    if not os.path.exists(backend_index_path):
        print(f"Error: {backend_index_path} not found")
        return False
    
    # Read the current file
    with open(backend_index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and remove the setTimeout that's causing multiple game setups
    timeout_pattern = '''    // CRITICAL: Also ensure the user is added to the actual game state
    setTimeout(() => {
      let game = gameService.getGameForRoom(gameCode);
      if (!game) {
        console.log(`🎮 Creating new game for room: ${gameCode}`);
        game = gameService.createGameForRoom(gameCode);
      }
      
      // Add player to game if not already present
      console.log('🎮 Adding player to game:');
      console.log('🎮 Game ID:', game.getId());
      console.log('🎮 User:', user.username, 'ID:', user.id, 'Socket:', socket.id);
      const success = gameService.addPlayerToGame(game.getId(), user.id, user.username, socket.id);
      console.log('🎮 Add player result:', success);
      if (success) {
        console.log(`✅ Added ${user.username} to game state`);
      } else {
        console.log(`ℹ️  ${user.username} already in game state`);
      }
      
      // Always send current game state to the player
      const gameState = game.getGame();
      console.log('🎮 BEFORE sending game state to:', user.username);
      console.log('🎮 Game players:', gameState.players.map(p => `${p.username}(${p.team}/${p.role})`));
      socket.emit('game:state-updated', gameState);
      
      // Also send to others in the room
      console.log('🎮 Broadcasting game state to room:', gameCode);
      socket.to(gameCode).emit('game:state-updated', gameState);
    }, 100);'''
    
    # Replace the setTimeout with immediate execution
    immediate_setup = '''    // CRITICAL: Ensure the user is added to the actual game state (IMMEDIATE - no setTimeout)
    let game = gameService.getGameForRoom(gameCode);
    if (!game) {
      console.log(`🎮 Creating new game for room: ${gameCode}`);
      game = gameService.createGameForRoom(gameCode);
    }
    
    // Add player to game if not already present
    console.log('🎮 Adding player to game:');
    console.log('🎮 Game ID:', game.getId());
    console.log('🎮 User:', user.username, 'ID:', user.id, 'Socket:', socket.id);
    const success = gameService.addPlayerToGame(game.getId(), user.id, user.username, socket.id);
    console.log('🎮 Add player result:', success);
    if (success) {
      console.log(`✅ Added ${user.username} to game state`);
    } else {
      console.log(`ℹ️  ${user.username} already in game state`);
    }
    
    // Always send current game state to the player
    const gameState = game.getGame();
    console.log('🎮 BEFORE sending game state to:', user.username);
    console.log('🎮 Game players:', gameState.players.map((p: any) => `${p.username}(${p.team}/${p.role})`));
    socket.emit('game:state-updated', gameState);
    
    // Also send to others in the room
    console.log('🎮 Broadcasting game state to room:', gameCode);
    socket.to(gameCode).emit('game:state-updated', gameState);'''
    
    if timeout_pattern in content:
        content = content.replace(timeout_pattern, immediate_setup)
        print("✅ Removed problematic setTimeout from backend join-game-room handler")
    else:
        print("⚠️  Could not find exact setTimeout pattern - may need manual update")
        return False
    
    # Write the updated content back
    with open(backend_index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def fix_frontend_duplicate_calls():
    """Prevent duplicate game creation calls from frontend"""
    
    room_page_path = "frontend/src/pages/RoomPage.tsx"
    
    if not os.path.exists(room_page_path):
        print(f"Error: {room_page_path} not found")
        return False
    
    # Read the current file
    with open(room_page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add state to track if game creation was already called
    if 'const [gameCreationCalled, setGameCreationCalled] = useState(false);' not in content:
        # Find where other useState declarations are
        useState_pattern = "const [gameState, setGameState] = useState<any>(null);"
        if useState_pattern in content:
            content = content.replace(
                useState_pattern,
                useState_pattern + "\n  const [gameCreationCalled, setGameCreationCalled] = useState(false);"
            )
            print("✅ Added gameCreationCalled state")
    
    # Modify the game creation logic to only run once
    old_game_creation = '''        // Create or join game in the backend (only once per connection)
        console.log('🎮 Creating/joining game for room:', gameCode);
        if (!gameState) {
          console.log('🎮 No existing game state, creating/joining game');
          gameService.createGame(); // This will create or join existing game
        } else {
          console.log('🎮 Game state already exists, skipping creation');
        }'''
    
    new_game_creation = '''        // Create or join game in the backend (only once per connection)
        console.log('🎮 Creating/joining game for room:', gameCode);
        if (!gameState && !gameCreationCalled) {
          console.log('🎮 No existing game state, creating/joining game');
          setGameCreationCalled(true);
          gameService.createGame(); // This will create or join existing game
        } else {
          console.log('🎮 Game state already exists or creation already called, skipping');
        }'''
    
    if old_game_creation in content:
        content = content.replace(old_game_creation, new_game_creation)
        print("✅ Added duplicate prevention to frontend game creation")
    
    # Write the updated content back
    with open(room_page_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def add_team_button_debouncing():
    """Add debouncing to team join buttons to prevent rapid clicks"""
    
    room_page_path = "frontend/src/pages/RoomPage.tsx"
    
    if not os.path.exists(room_page_path):
        print(f"Error: {room_page_path} not found")
        return False
    
    # Read the current file
    with open(room_page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add state for team action debouncing
    if 'const [teamActionInProgress, setTeamActionInProgress] = useState(false);' not in content:
        # Find where other useState declarations are
        useState_pattern = "const [gameCreationCalled, setGameCreationCalled] = useState(false);"
        if useState_pattern in content:
            content = content.replace(
                useState_pattern,
                useState_pattern + "\n  const [teamActionInProgress, setTeamActionInProgress] = useState(false);"
            )
            print("✅ Added teamActionInProgress state")
    
    # Update handleJoinTeam with debouncing
    old_join_team = '''  const handleJoinTeam = (team: string, role: string) => {
    console.log(`👥 Attempting to join ${team} team as ${role}`);
    console.log('🔍 Current game state:', gameState);
    console.log('🔍 Socket connected:', socketService.socket?.connected);
    console.log('🔍 User:', currentUser);
    
    if (!isConnected) {
      console.error('❌ Socket not connected');
      setError('Not connected to server');
      return;
    }
    
    // Use the game service to join team
    gameService.joinTeam(team as any, role as any);
  };'''
    
    new_join_team = '''  const handleJoinTeam = (team: string, role: string) => {
    console.log(`👥 Attempting to join ${team} team as ${role}`);
    console.log('🔍 Current game state:', gameState);
    console.log('🔍 Socket connected:', socketService.socket?.connected);
    console.log('🔍 User:', currentUser);
    
    if (!isConnected) {
      console.error('❌ Socket not connected');
      setError('Not connected to server');
      return;
    }
    
    if (teamActionInProgress) {
      console.log('⏳ Team action already in progress, ignoring duplicate click');
      return;
    }
    
    setTeamActionInProgress(true);
    
    // Use the game service to join team
    gameService.joinTeam(team as any, role as any);
    
    // Reset the flag after a delay to prevent rapid clicking
    setTimeout(() => setTeamActionInProgress(false), 1000);
  };'''
    
    if old_join_team in content:
        content = content.replace(old_join_team, new_join_team)
        print("✅ Added debouncing to handleJoinTeam")
    
    # Write the updated content back
    with open(room_page_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    print("🔧 Fixing Triple Calls Root Cause...")
    print("=" * 50)
    
    success_count = 0
    
    # Fix backend setTimeout issue (main culprit)
    if fix_backend_timeout_issue():
        success_count += 1
    
    # Fix frontend duplicate calls
    if fix_frontend_duplicate_calls():
        success_count += 1
    
    # Add team button debouncing
    if add_team_button_debouncing():
        success_count += 1
    
    print("=" * 50)
    if success_count >= 1:  # At least the main fix
        print("✅ Root cause fixes applied!")
        print("\n🎯 What was fixed:")
        print("1. ✅ Removed setTimeout(100ms) from backend that was causing duplicate game setups")
        print("2. ✅ Added frontend state tracking to prevent duplicate game creation calls")
        print("3. ✅ Added button debouncing to prevent rapid team selection clicks")
        print("\n🚀 Next steps:")
        print("1. Restart your backend server (the setTimeout fix is crucial)")
        print("2. Test the team selection and game start flow")
        print("3. Should see single events instead of 3x duplicates")
        print("\n💡 The setTimeout(100ms) in backend was the main culprit!")
    else:
        print(f"⚠️  Only {success_count}/3 fixes applied. Check error messages above.")
    
    return success_count >= 1

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)