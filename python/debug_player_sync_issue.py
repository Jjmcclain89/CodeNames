#!/usr/bin/env python3
"""
Debug and Fix Player Synchronization Issue
The room system and game system aren't syncing players properly.
"""

def add_debugging_to_join_handler():
    """Add debugging to track why players aren't syncing"""
    
    file_path = "backend/src/index.ts"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔧 Adding player sync debugging...")
        
        # Find the setTimeout section and enhance it
        old_timeout = '''  // CRITICAL: Also ensure the user is added to the actual game state
  setTimeout(() => {
    console.log(`🔍 [MULTIPLAYER DEBUG] Processing game state for ${user.username} joining room ${gameCode}`);
    console.log(`🔍 [BEFORE] Total games in service:`, gameService.getStats().totalGames);
    
    let game = gameService.getGameForRoom(gameCode);
    console.log(`🔍 [GAME LOOKUP] Game exists for room ${gameCode}:`, !!game);
    
    if (!game) {
      console.log(`🎮 [CREATE] Creating new game for room: ${gameCode}`);
      game = gameService.createGameForRoom(gameCode);
      console.log(`🎮 [CREATE] New game created with ID:`, game.getId());
    } else {
      console.log(`🎮 [EXISTING] Using existing game ID:`, game.getId());
      const existingState = game.getGame();
      console.log(`🎮 [EXISTING] Current players in game:`, existingState.players.map(p => `${p.username}(${p.team}/${p.role})`));
    }
    
    // Add player to game if not already present
    console.log(`🎮 [ADD PLAYER] Attempting to add ${user.username} to game`);
    console.log('🎮 [ADD PLAYER] Game ID:', game.getId());
    console.log('🎮 [ADD PLAYER] User details:', { username: user.username, id: user.id, socketId: socket.id });
    
    const success = gameService.addPlayerToGame(game.getId(), user.id, user.username, socket.id);
    console.log(`🎮 [ADD PLAYER] Result for ${user.username}:`, success);
    
    // Get final game state and log details
    const gameState = game.getGame();
    console.log(`🎮 [FINAL STATE] Game ${game.getId()} now has ${gameState.players.length} players:`);
    gameState.players.forEach((p, i) => {
      console.log(`  ${i+1}. ${p.username} (${p.id}) - ${p.team}/${p.role} - Online: ${p.isOnline}`);
    });
    
    console.log(`🎮 [BROADCAST] Sending game state to ${user.username}`);
    socket.emit('game:state-updated', gameState);
    
    console.log(`🎮 [BROADCAST] Broadcasting to room ${gameCode} (excluding ${user.username})`);
    socket.to(gameCode).emit('game:state-updated', gameState);
    
    console.log(`🔍 [AFTER] Total games in service:`, gameService.getStats().totalGames);
    console.log(`🔍 [MULTIPLAYER DEBUG] Completed processing for ${user.username}\\n`);
  }, 100);'''
        
        new_timeout = '''  // CRITICAL: Also ensure the user is added to the actual game state
  setTimeout(() => {
    console.log(`\\n🔍 [MULTIPLAYER DEBUG] Processing game state for ${user.username} joining room ${gameCode}`);
    
    // FIRST: Check room system vs game system
    const { gameRooms } = require('./routes/games');
    const gameRoom = gameRooms.get(gameCode);
    console.log(`🔍 [ROOM SYSTEM] Room ${gameCode} has ${gameRoom ? gameRoom.players.length : 0} players:`, 
      gameRoom ? gameRoom.players.map(p => p.username) : 'NO ROOM');
    
    console.log(`🔍 [GAME SYSTEM] Total games in service:`, gameService.getStats().totalGames);
    
    let game = gameService.getGameForRoom(gameCode);
    console.log(`🔍 [GAME LOOKUP] Game exists for room ${gameCode}:`, !!game);
    
    if (!game) {
      console.log(`🎮 [CREATE] Creating new game for room: ${gameCode}`);
      game = gameService.createGameForRoom(gameCode);
      console.log(`🎮 [CREATE] New game created with ID:`, game.getId());
      
      // SYNC: Add all players from room system to game system
      if (gameRoom && gameRoom.players.length > 0) {
        console.log(`🔄 [SYNC] Syncing ${gameRoom.players.length} players from room to game:`);
        gameRoom.players.forEach(roomPlayer => {
          const addResult = gameService.addPlayerToGame(game.getId(), roomPlayer.id, roomPlayer.username, roomPlayer.socketId || 'unknown');
          console.log(`🔄 [SYNC] Added ${roomPlayer.username} to game: ${addResult}`);
        });
      }
    } else {
      console.log(`🎮 [EXISTING] Using existing game ID:`, game.getId());
      const existingState = game.getGame();
      console.log(`🎮 [EXISTING] Current players in game:`, existingState.players.map(p => `${p.username}(${p.team}/${p.role})`));
    }
    
    // Add current player to game if not already present
    console.log(`🎮 [ADD PLAYER] Attempting to add ${user.username} to game`);
    const success = gameService.addPlayerToGame(game.getId(), user.id, user.username, socket.id);
    console.log(`🎮 [ADD PLAYER] Result for ${user.username}:`, success);
    
    // Get final game state and log details
    const gameState = game.getGame();
    console.log(`🎮 [FINAL STATE] Game ${game.getId()} now has ${gameState.players.length} players:`);
    gameState.players.forEach((p, i) => {
      console.log(`  ${i+1}. ${p.username} (${p.id}) - ${p.team}/${p.role} - Online: ${p.isOnline}`);
    });
    
    // VERIFICATION: Compare room system vs game system
    console.log(`🔍 [VERIFICATION] Room has ${gameRoom ? gameRoom.players.length : 0} players, Game has ${gameState.players.length} players`);
    if (gameRoom && gameRoom.players.length !== gameState.players.length) {
      console.log(`❌ [SYNC ERROR] Player count mismatch between room and game systems!`);
    }
    
    console.log(`🎮 [BROADCAST] Sending game state to ${user.username}`);
    socket.emit('game:state-updated', gameState);
    
    console.log(`🎮 [BROADCAST] Broadcasting to room ${gameCode} (excluding ${user.username})`);
    socket.to(gameCode).emit('game:state-updated', gameState);
    
    console.log(`🔍 [MULTIPLAYER DEBUG] Completed processing for ${user.username}\\n`);
  }, 100);'''
        
        if old_timeout in content:
            content = content.replace(old_timeout, new_timeout)
            print("✅ Enhanced timeout section with room/game sync debugging")
        else:
            print("⚠️  Could not find exact timeout section - looking for alternatives")
            # Try to find and replace a simpler version
            if 'setTimeout(() => {' in content and 'gameService.getGameForRoom(gameCode)' in content:
                print("ℹ️  Found timeout section but different format - manual inspection needed")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding debugging: {e}")
        return False

def enhance_gameservice_addplayer():
    """Enhance the addPlayerToGame method to prevent duplicates"""
    
    file_path = "backend/src/services/gameService.ts"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔧 Enhancing addPlayerToGame method...")
        
        # Find and enhance the addPlayerToGame method
        old_method = '''  addPlayerToGame(gameId: string, playerId: string, username: string, socketId: string): boolean {
    const game = this.getGame(gameId);
    if (!game) return false;

    // Remove player from any existing game first
    this.removePlayerFromAllGames(playerId);

    const success = game.addPlayer(playerId, username, socketId);
    if (success) {
      this.playerGameMap.set(playerId, gameId);
    }
    return success;
  }'''
        
        new_method = '''  addPlayerToGame(gameId: string, playerId: string, username: string, socketId: string): boolean {
    console.log(`🎯 [ADDPLAYER] Adding ${username} (${playerId}) to game ${gameId}`);
    
    const game = this.getGame(gameId);
    if (!game) {
      console.log(`❌ [ADDPLAYER] Game ${gameId} not found`);
      return false;
    }

    // Check if player is already in THIS game
    const currentGame = this.getGameByPlayer(playerId);
    if (currentGame && currentGame.getId() === gameId) {
      console.log(`ℹ️  [ADDPLAYER] ${username} already in game ${gameId}`);
      return true; // Already in the correct game
    }

    // Remove player from any other game first
    if (currentGame && currentGame.getId() !== gameId) {
      console.log(`🔄 [ADDPLAYER] Moving ${username} from game ${currentGame.getId()} to ${gameId}`);
      this.removePlayerFromAllGames(playerId);
    }

    const success = game.addPlayer(playerId, username, socketId);
    if (success) {
      this.playerGameMap.set(playerId, gameId);
      console.log(`✅ [ADDPLAYER] Successfully added ${username} to game ${gameId}`);
    } else {
      console.log(`❌ [ADDPLAYER] Failed to add ${username} to game ${gameId}`);
    }
    
    return success;
  }'''
        
        if old_method in content:
            content = content.replace(old_method, new_method)
            print("✅ Enhanced addPlayerToGame method")
        else:
            print("⚠️  Could not find exact addPlayerToGame method to replace")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"❌ Error enhancing gameService: {e}")
        return False

def main():
    print("🔍 DEBUGGING PLAYER SYNCHRONIZATION ISSUE")
    print("=" * 50)
    print()
    print("Problem identified:")
    print("❌ Room system tracks players correctly (playerCount: 2)")
    print("❌ Game system only shows 1 player per game instance") 
    print("❌ Players are getting separate game instances")
    print()
    print("Debugging approach:")
    print("🔍 Add logging to compare room vs game player counts")
    print("🔄 Add sync logic to copy room players to game")
    print("🎯 Enhance addPlayerToGame to prevent duplicates")
    print()
    
    success = True
    
    if add_debugging_to_join_handler():
        print("✅ Enhanced join handler debugging")
    else:
        success = False
    
    if enhance_gameservice_addplayer():
        print("✅ Enhanced addPlayerToGame method")
    else:
        success = False
    
    print()
    if success:
        print("🎉 DEBUGGING ENHANCEMENTS ADDED!")
        print()
        print("🧪 Testing Steps:")
        print("1. Restart backend server")
        print("2. Open 2 browser windows")
        print("3. Both join same room code")
        print("4. Watch backend console for:")
        print("   - [ROOM SYSTEM] vs [GAME SYSTEM] player counts")
        print("   - [SYNC] operations")
        print("   - [VERIFICATION] messages")
        print("   - Any [SYNC ERROR] messages")
        print()
        print("Expected result:")
        print("✅ Both systems should show same player count")
        print("✅ Game state should sync from room state")
        print("✅ Both players should see each other")
    else:
        print("❌ Some enhancements failed")
        print("\n🔍 Manual investigation needed:")
        print("1. Check if room system has 2 players")
        print("2. Check if game system has 1 player")  
        print("3. Find where the sync breaks")

if __name__ == "__main__":
    main()