#!/usr/bin/env python3
"""
Debug Multiplayer State Issues - Add comprehensive logging to identify
where game state is being reset or why team assignments fail for second player.
"""

def add_comprehensive_logging():
    """Add detailed logging to track multiplayer state issues"""
    
    file_path = "backend/src/index.ts"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔧 Adding comprehensive multiplayer debugging...")
        
        # Add logging to the join-game-room handler to track the timing issue
        old_timeout_section = '''  // CRITICAL: Also ensure the user is added to the actual game state
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
        
        new_timeout_section = '''  // CRITICAL: Also ensure the user is added to the actual game state
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
        
        if old_timeout_section in content:
            content = content.replace(old_timeout_section, new_timeout_section)
            print("✅ Enhanced join-game-room logging")
        else:
            print("⚠️  Could not find exact timeout section to replace")
        
        # Add enhanced logging to the team assignment handler
        old_team_handler = '''socket.on('game:join-team', (team: string, role: string) => {
    try {
      // Get or create game for current room
      // Get user's current room instead of hardcoded GLOBAL
      const currentRoom = userRooms.get(socket.id);
      if (!currentRoom) {
        socket.emit('game:error', 'Not in a game room');
        return;
      }
      const roomCode = currentRoom;
      let game = gameService.getGameForRoom(roomCode);
      
      if (!game) {
        game = gameService.createGameForRoom(roomCode);
        gameService.addPlayerToGame(game.getId(), user.id, user.username, socket.id);
      }

      console.log('🎮 BEFORE team assignment:');
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
      console.log('🎮 Assignment result:', result);
      
      if (result.success) {
        const gameState = game.getGame();
        io.to(roomCode).emit('game:state-updated', gameState);
        console.log('👥 Player', user.username, 'joined', team, 'team as', role);
      } else {
        socket.emit('game:error', result.error || 'Failed to join team');
      }
    } catch (error) {
      console.error('❌ Error joining team:', error);
      socket.emit('game:error', 'Failed to join team');
    }
  });'''
        
        new_team_handler = '''socket.on('game:join-team', (team: string, role: string) => {
    try {
      console.log(`\\n🏆 [TEAM ASSIGNMENT] ${user.username} wants to join ${team} team as ${role}`);
      
      // Get or create game for current room
      const currentRoom = userRooms.get(socket.id);
      console.log(`🏆 [ROOM CHECK] ${user.username} is in room:`, currentRoom);
      
      if (!currentRoom) {
        console.log(`❌ [ROOM ERROR] ${user.username} not in a game room`);
        socket.emit('game:error', 'Not in a game room');
        return;
      }
      
      const roomCode = currentRoom;
      let game = gameService.getGameForRoom(roomCode);
      console.log(`🏆 [GAME LOOKUP] Game exists for room ${roomCode}:`, !!game);
      
      if (!game) {
        console.log(`🏆 [GAME CREATE] Creating new game for ${roomCode} during team assignment`);
        game = gameService.createGameForRoom(roomCode);
        gameService.addPlayerToGame(game.getId(), user.id, user.username, socket.id);
      }

      // Log detailed game state before assignment
      const preState = game.getGame();
      console.log(`🏆 [PRE-ASSIGNMENT] Game ${game.getId()} state:`);
      console.log(`🏆 [PRE-ASSIGNMENT] Total players: ${preState.players.length}`);
      preState.players.forEach((p, i) => {
        console.log(`  ${i+1}. ${p.username} (${p.id}) - ${p.team}/${p.role} - Online: ${p.isOnline}`);
      });
      
      // Check if player exists in game before assignment
      const existingGame = gameService.getGameByPlayer(user.id);
      console.log(`🏆 [PLAYER CHECK] ${user.username} exists in a game:`, !!existingGame);
      
      if (!existingGame) {
        console.log(`❌ [PLAYER ERROR] ${user.username} not found in any game - this should not happen!`);
        // Try to add them
        const addResult = gameService.addPlayerToGame(game.getId(), user.id, user.username, socket.id);
        console.log(`🏆 [PLAYER FIX] Attempted to add ${user.username} to game:`, addResult);
      }
      
      // Attempt team assignment
      console.log(`🏆 [ASSIGNMENT] Calling assignPlayerToTeam for ${user.username}`);
      const result = gameService.assignPlayerToTeam(user.id, team as any, role as any);
      console.log(`🏆 [ASSIGNMENT] Result:`, result);
      
      if (result.success) {
        const gameState = game.getGame();
        console.log(`🏆 [SUCCESS] ${user.username} successfully joined ${team} team as ${role}`);
        console.log(`🏆 [SUCCESS] Broadcasting updated game state to room ${roomCode}`);
        
        // Log final state
        console.log(`🏆 [FINAL STATE] Game now has ${gameState.players.length} players:`);
        gameState.players.forEach((p, i) => {
          console.log(`  ${i+1}. ${p.username} - ${p.team}/${p.role}`);
        });
        
        io.to(roomCode).emit('game:state-updated', gameState);
        console.log(`👥 [BROADCAST COMPLETE] All players in ${roomCode} notified of ${user.username} joining ${team} team`);
      } else {
        console.log(`❌ [ASSIGNMENT FAILED] ${user.username} could not join ${team} team as ${role}: ${result.error}`);
        socket.emit('game:error', result.error || 'Failed to join team');
      }
      
      console.log(`🏆 [TEAM ASSIGNMENT] Completed for ${user.username}\\n`);
    } catch (error) {
      console.error(`❌ [TEAM ASSIGNMENT ERROR] Error for ${user.username}:`, error);
      socket.emit('game:error', 'Failed to join team');
    }
  });'''
        
        if old_team_handler in content:
            content = content.replace(old_team_handler, new_team_handler)
            print("✅ Enhanced team assignment logging")
        else:
            print("⚠️  Could not find exact team handler section to replace")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Comprehensive multiplayer debugging added")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding debugging: {e}")
        return False

def add_gameservice_debugging():
    """Add debugging to the game service to track state changes"""
    
    file_path = "backend/src/services/gameService.ts"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔧 Adding game service debugging...")
        
        # Add logging to the assignPlayerToTeam method
        old_assign_method = '''  assignPlayerToTeam(playerId: string, team: TeamColor, role: PlayerRole): { success: boolean; error?: string } {
    const game = this.getGameByPlayer(playerId);
    if (!game) {
      return { success: false, error: 'Player not in any game' };
    }

    const success = game.assignPlayerToTeam(playerId, team, role);
    return { 
      success, 
      error: success ? undefined : 'Cannot assign to team - team may already have a spymaster' 
    };
  }'''
        
        new_assign_method = '''  assignPlayerToTeam(playerId: string, team: TeamColor, role: PlayerRole): { success: boolean; error?: string } {
    console.log(`🎯 [GAMESERVICE] assignPlayerToTeam called for player ${playerId} to join ${team} as ${role}`);
    
    const game = this.getGameByPlayer(playerId);
    if (!game) {
      console.log(`❌ [GAMESERVICE] Player ${playerId} not found in any game`);
      console.log(`🎯 [GAMESERVICE] Current player-game mappings:`, Array.from(this.playerGameMap.entries()));
      return { success: false, error: 'Player not in any game' };
    }

    console.log(`🎯 [GAMESERVICE] Found game ${game.getId()} for player ${playerId}`);
    const preState = game.getGame();
    console.log(`🎯 [GAMESERVICE] Pre-assignment game state:`, preState.players.map(p => `${p.username}(${p.team}/${p.role})`));
    
    const success = game.assignPlayerToTeam(playerId, team, role);
    
    const postState = game.getGame();
    console.log(`🎯 [GAMESERVICE] Post-assignment game state:`, postState.players.map(p => `${p.username}(${p.team}/${p.role})`));
    console.log(`🎯 [GAMESERVICE] Assignment result: ${success}`);
    
    return { 
      success, 
      error: success ? undefined : 'Cannot assign to team - team may already have a spymaster' 
    };
  }'''
        
        if old_assign_method in content:
            content = content.replace(old_assign_method, new_assign_method)
            print("✅ Enhanced assignPlayerToTeam logging")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding gameService debugging: {e}")
        return False

def main():
    print("🔍 ADDING COMPREHENSIVE MULTIPLAYER DEBUGGING")
    print("=" * 55)
    print()
    print("This will add detailed logging to help identify:")
    print("1. Game state reset issues when second player joins")
    print("2. Team assignment failures")
    print("3. Player synchronization problems")
    print("4. Race conditions in multiplayer state")
    print()
    
    success = True
    
    if add_comprehensive_logging():
        print("✅ Backend socket debugging added")
    else:
        success = False
    
    if add_gameservice_debugging():
        print("✅ Game service debugging added")
    else:
        success = False
    
    print()
    if success:
        print("🎉 DEBUGGING ADDED SUCCESSFULLY!")
        print()
        print("🧪 Testing Steps:")
        print("1. Restart backend server")
        print("2. Open 2 browser windows")
        print("3. Both players join same room")
        print("4. First player joins a team")
        print("5. Second player tries to join a team")
        print("6. Check backend console for detailed logs")
        print()
        print("🔍 Look for these log patterns:")
        print("  - [MULTIPLAYER DEBUG] when players join")
        print("  - [TEAM ASSIGNMENT] when joining teams")
        print("  - [GAMESERVICE] for state management")
        print("  - Any error messages or unexpected behavior")
    else:
        print("❌ Some debugging additions failed")

if __name__ == "__main__":
    main()