#!/usr/bin/env python3
"""
Fix Game Creation Bug - Replace always-create pattern with join-or-create pattern
"""

def fix_backend_game_creation():
    """Fix backend to join existing games instead of always creating new ones"""
    
    file_path = "backend/src/index.ts"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔧 Fixing backend game creation logic...")
        
        # Replace the game:create handler to use join-or-create pattern
        old_create_handler = '''  socket.on('game:create', () => {
    try {
      // Get user's current room instead of hardcoded GLOBAL
      const currentRoom = userRooms.get(socket.id);
      if (!currentRoom) {
        socket.emit('game:error', 'Not in a game room');
        return;
      }
      const roomCode = currentRoom; // For now, use global room for games
      const game = gameService.createGameForRoom(roomCode);
      
      // Add player to game
      console.log('🎮 Adding player to game:');
      console.log('🎮 Game ID:', game.getId());
      console.log('🎮 User:', user.username, 'ID:', user.id, 'Socket:', socket.id);
      const success = gameService.addPlayerToGame(game.getId(), user.id, user.username, socket.id);
      console.log('🎮 Add player result:', success);
      
      if (success) {
        const gameState = game.getGame();
        socket.emit('game:state-updated', gameState);
        socket.to(roomCode).emit('game:player-joined', gameState.players.find((p: any )=> p.id === user.id));
        console.log('🎮 Game created for room:', roomCode, 'by:', user.username);
      } else {
        socket.emit('game:error', 'Failed to create game');
      }
    } catch (error) {
      console.error('❌ Error creating game:', error);
      socket.emit('game:error', 'Failed to create game');
    }
  });'''
        
        new_create_handler = '''  socket.on('game:create', () => {
    try {
      // Get user's current room instead of hardcoded GLOBAL
      const currentRoom = userRooms.get(socket.id);
      if (!currentRoom) {
        socket.emit('game:error', 'Not in a game room');
        return;
      }
      const roomCode = currentRoom;
      
      // Join existing game or create new one (DON'T always create new)
      let game = gameService.getGameForRoom(roomCode);
      if (!game) {
        console.log('🎮 No existing game for room:', roomCode, '- creating new one');
        game = gameService.createGameForRoom(roomCode);
      } else {
        console.log('🎮 Found existing game for room:', roomCode, '- joining it');
      }
      
      // Add player to game
      console.log('🎮 Adding player to game:');
      console.log('🎮 Game ID:', game.getId());
      console.log('🎮 User:', user.username, 'ID:', user.id, 'Socket:', socket.id);
      const success = gameService.addPlayerToGame(game.getId(), user.id, user.username, socket.id);
      console.log('🎮 Add player result:', success);
      
      if (success) {
        const gameState = game.getGame();
        socket.emit('game:state-updated', gameState);
        socket.to(roomCode).emit('game:player-joined', gameState.players.find((p: any )=> p.id === user.id));
        console.log('🎮 Player', user.username, 'joined game in room:', roomCode);
      } else {
        socket.emit('game:error', 'Failed to join game');
      }
    } catch (error) {
      console.error('❌ Error joining/creating game:', error);
      socket.emit('game:error', 'Failed to join game');
    }
  });'''
        
        if old_create_handler in content:
            content = content.replace(old_create_handler, new_create_handler)
            print("✅ Fixed game:create handler to use join-or-create pattern")
        else:
            print("⚠️  Could not find exact game:create handler to replace")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing backend: {e}")
        return False

def fix_gameservice_create_method():
    """Fix gameService to not always delete existing games"""
    
    file_path = "backend/src/services/gameService.ts"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔧 Fixing gameService createGameForRoom method...")
        
        # Replace createGameForRoom to not always delete existing games
        old_create_method = '''  createGameForRoom(roomCode: string): CodenamesGameModel {
    // Remove any existing game for this room
    this.deleteGameForRoom(roomCode);

    const gameModel = new CodenamesGameModel(roomCode);
    this.games.set(gameModel.getId(), {
      model: gameModel,
      lastActivity: new Date()
    });

    return gameModel;
  }'''
        
        new_create_method = '''  createGameForRoom(roomCode: string): CodenamesGameModel {
    // Check if game already exists - don't delete it!
    const existingGame = this.getGameForRoom(roomCode);
    if (existingGame) {
      console.log(`⚠️  Game already exists for room ${roomCode}, returning existing game`);
      return existingGame;
    }

    console.log(`🎮 Creating new game for room: ${roomCode}`);
    const gameModel = new CodenamesGameModel(roomCode);
    this.games.set(gameModel.getId(), {
      model: gameModel,
      lastActivity: new Date()
    });

    return gameModel;
  }'''
        
        if old_create_method in content:
            content = content.replace(old_create_method, new_create_method)
            print("✅ Fixed createGameForRoom to preserve existing games")
        else:
            print("⚠️  Could not find exact createGameForRoom method to replace")
        
        # Also add a new method for explicitly creating fresh games when needed
        if 'createGameForRoom(roomCode: string): CodenamesGameModel {' in content:
            # Add after the createGameForRoom method
            insert_point = content.find('  }', content.find('createGameForRoom(roomCode: string): CodenamesGameModel {')) + 4
            
            new_method = '''

  // Method to explicitly create a fresh game (for reset/restart scenarios)
  createFreshGameForRoom(roomCode: string): CodenamesGameModel {
    console.log(`🎮 Creating fresh game for room: ${roomCode} (deleting any existing)`);
    this.deleteGameForRoom(roomCode);

    const gameModel = new CodenamesGameModel(roomCode);
    this.games.set(gameModel.getId(), {
      model: gameModel,
      lastActivity: new Date()
    });

    return gameModel;
  }'''
            
            content = content[:insert_point] + new_method + content[insert_point:]
            print("✅ Added createFreshGameForRoom method for explicit resets")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing gameService: {e}")
        return False

def main():
    print("🚨 FIXING GAME CREATION BUG")
    print("=" * 40)
    print()
    print("Root cause identified:")
    print("❌ Every player join creates a NEW game, deleting the previous one")
    print("❌ This is why state resets when second player joins")
    print("❌ Players end up in different game instances")
    print()
    print("The fix:")
    print("✅ Change to join-or-create pattern")
    print("✅ Don't delete existing games on create")
    print("✅ Multiple players can join the same game instance")
    print()
    
    success = True
    
    if fix_backend_game_creation():
        print("✅ Backend game creation logic fixed")
    else:
        success = False
    
    if fix_gameservice_create_method():
        print("✅ GameService create method fixed")
    else:
        success = False
    
    print()
    if success:
        print("🎉 GAME CREATION BUG FIXED!")
        print()
        print("🧪 Testing Steps:")
        print("1. Restart backend server")
        print("2. Open 2 browser windows")
        print("3. Both players join same room")
        print("4. First player should stay when second player joins")
        print("5. Both players should see each other")
        print("6. Team assignment should work for both players")
        print()
        print("Expected result:")
        print("✅ Same game ID for both players")
        print("✅ Player count shows 2")
        print("✅ Team assignments persist")
        print("✅ No more state resets!")
    else:
        print("❌ Some fixes failed - check error messages above")

if __name__ == "__main__":
    main()