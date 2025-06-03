#!/usr/bin/env python3
"""
Debug Game State Transition Issue

This script adds debugging to track why the frontend isn't transitioning
from "team selection" to "game started" when the backend successfully
starts the game.
"""

import os
import sys

def debug_room_page_game_state_updates():
    """Add debugging to RoomPage to track game state updates"""
    
    room_page_path = "frontend/src/pages/RoomPage.tsx"
    
    if not os.path.exists(room_page_path):
        print(f"Error: {room_page_path} not found")
        return False
    
    with open(room_page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add debugging to the setupGameListeners function
    old_setup_listeners = '''    // Listen for game state updates
    gameService.onGameStateUpdated((newGameState: any) => {
      console.log('🎮 Game state updated in room:', newGameState);
      setGameState(newGameState);
      
      if (newGameState.status === 'playing') {
        setGameStarted(true);
      }
      
      // Update players with team/role info from game state
      if (newGameState.players) {
        console.log('👥 Updating players from game state:', newGameState.players);
        setPlayers(newGameState.players);
      }
    });'''
    
    new_setup_listeners = '''    // Listen for game state updates
    gameService.onGameStateUpdated((newGameState: any) => {
      console.log('🎮 [ROOMPAGE] Game state updated in room:', newGameState);
      console.log('🎮 [ROOMPAGE] New game status:', newGameState.status);
      console.log('🎮 [ROOMPAGE] Current gameStarted state:', gameStarted);
      
      setGameState(newGameState);
      
      if (newGameState.status === 'playing') {
        console.log('🚀 [ROOMPAGE] Game status is playing - setting gameStarted to true');
        setGameStarted(true);
      } else {
        console.log('🎮 [ROOMPAGE] Game status is not playing yet:', newGameState.status);
      }
      
      // Update players with team/role info from game state
      if (newGameState.players) {
        console.log('👥 [ROOMPAGE] Updating players from game state:', newGameState.players);
        setPlayers(newGameState.players);
      }
    });'''
    
    if old_setup_listeners in content:
        content = content.replace(old_setup_listeners, new_setup_listeners)
        print("✅ Added debugging to game state update listener")
    
    # Add debugging to the gameStarted conditional rendering
    old_game_started_check = '''  if (gameStarted) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center bg-white p-8 rounded-lg shadow border border-gray-200 max-w-md">
          <div className="text-green-600 text-xl mb-4">🎉 Game Started!</div>
          <div className="text-gray-600 mb-6">
            <p>The Codenames game has begun.</p>
            <p className="mt-2 text-sm">Click below to join the game board.</p>
          </div>
          <button 
            onClick={handleGoToGame}
            className="w-full bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded text-lg font-semibold"
          >
            🎮 Join Game Board
          </button>
        </div>
      </div>
    );
  }'''
    
    new_game_started_check = '''  if (gameStarted) {
    console.log('🎉 [ROOMPAGE] Rendering game started screen');
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center bg-white p-8 rounded-lg shadow border border-gray-200 max-w-md">
          <div className="text-green-600 text-xl mb-4">🎉 Game Started!</div>
          <div className="text-gray-600 mb-6">
            <p>The Codenames game has begun.</p>
            <p className="mt-2 text-sm">Click below to join the game board.</p>
          </div>
          <button 
            onClick={handleGoToGame}
            className="w-full bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded text-lg font-semibold"
          >
            🎮 Join Game Board
          </button>
        </div>
      </div>
    );
  }'''
    
    if old_game_started_check in content:
        content = content.replace(old_game_started_check, new_game_started_check)
        print("✅ Added debugging to game started conditional")
    
    # Add debugging to handleGoToGame
    old_handle_go_to_game = '''  const handleGoToGame = () => {
    console.log('🎮 Navigating to game board...');
    navigate('/game');
  };'''
    
    new_handle_go_to_game = '''  const handleGoToGame = () => {
    console.log('🎮 [ROOMPAGE] handleGoToGame called - navigating to game board...');
    console.log('🎮 [ROOMPAGE] Current gameState:', gameState);
    navigate('/game');
    console.log('🎮 [ROOMPAGE] Navigation to /game called');
  };'''
    
    if old_handle_go_to_game in content:
        content = content.replace(old_handle_go_to_game, new_handle_go_to_game)
        print("✅ Added debugging to handleGoToGame")
    
    # Add a debug panel to the main UI to show current state
    debug_panel = '''        {/* Enhanced Debug Info */}
        <div className="mb-4 bg-yellow-50 border border-yellow-200 rounded p-3 text-xs">
          <strong>🔍 Debug:</strong> Connected: {isConnected ? 'Yes' : 'No'} | 
          Game State: {gameState ? 'Loaded' : 'None'} | 
          Game Status: {gameState?.status || 'Unknown'} |
          Game Started: {gameStarted ? 'Yes' : 'No'} |
          Game Players: {gameState?.players?.length || 0} | 
          Room Players: {players.length} | 
          User: {currentUser?.username} | 
          Room: {roomCode}
        </div>'''
    
    old_debug_panel = '''        {/* Debug Info */}
        <div className="mb-4 bg-yellow-50 border border-yellow-200 rounded p-3 text-xs">
          <strong>🔍 Debug:</strong> Connected: {isConnected ? 'Yes' : 'No'} | 
          Game State: {gameState ? 'Loaded' : 'None'} | 
          Game Players: {gameState?.players?.length || 0} | 
          Room Players: {players.length} | 
          User: {currentUser?.username} | 
          Room: {roomCode}
        </div>'''
    
    if old_debug_panel in content:
        content = content.replace(old_debug_panel, debug_panel)
        print("✅ Enhanced debug panel with game status info")
    
    with open(room_page_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def debug_game_service_events():
    """Add debugging to gameService to track socket events"""
    
    game_service_path = "frontend/src/services/gameService.ts"
    
    if not os.path.exists(game_service_path):
        print(f"Error: {game_service_path} not found")
        return False
    
    with open(game_service_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add debugging to onGameStateUpdated
    old_on_game_state = '''  onGameStateUpdated(callback: (game: CodenamesGame) => void): void {
    socketService.socket?.on('game:state-updated', callback);
  }'''
    
    new_on_game_state = '''  onGameStateUpdated(callback: (game: CodenamesGame) => void): void {
    console.log('🎮 [GAMESERVICE] Registering game:state-updated listener');
    
    const wrappedCallback = (game: CodenamesGame) => {
      console.log('🎮 [GAMESERVICE] game:state-updated event received:', game);
      console.log('🎮 [GAMESERVICE] Game status in event:', game.status);
      console.log('🎮 [GAMESERVICE] Game players count:', game.players?.length);
      callback(game);
    };
    
    socketService.socket?.on('game:state-updated', wrappedCallback);
  }'''
    
    if old_on_game_state in content:
        content = content.replace(old_on_game_state, new_on_game_state)
        print("✅ Added debugging to onGameStateUpdated listener")
    
    # Add debugging to startGame method
    old_start_game = '''  startGame(): void {
    socketService.socket?.emit('game:start');
  }'''
    
    new_start_game = '''  startGame(): void {
    console.log('🚀 [GAMESERVICE] Emitting game:start event to backend');
    socketService.socket?.emit('game:start');
    console.log('🚀 [GAMESERVICE] game:start event emitted');
  }'''
    
    if old_start_game in content:
        content = content.replace(old_start_game, new_start_game)
        print("✅ Added debugging to startGame method")
    
    with open(game_service_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def check_game_page_exists():
    """Check if GamePage exists and is working"""
    
    game_page_path = "frontend/src/pages/GamePage.tsx"
    
    if not os.path.exists(game_page_path):
        print(f"❌ GamePage.tsx not found at {game_page_path}")
        return False
    
    with open(game_page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if it's a minimal/placeholder page
    if len(content) < 500:
        print(f"⚠️  GamePage.tsx exists but appears to be minimal/placeholder ({len(content)} chars)")
    else:
        print(f"✅ GamePage.tsx exists and appears complete ({len(content)} chars)")
    
    return True

def main():
    print("🔧 Debugging Game State Transition Issue...")
    print("=" * 50)
    
    success_count = 0
    
    # Check if GamePage exists
    if check_game_page_exists():
        success_count += 1
    
    # Add debugging to RoomPage state updates
    if debug_room_page_game_state_updates():
        success_count += 1
    
    # Add debugging to gameService events
    if debug_game_service_events():
        success_count += 1
    
    print("=" * 50)
    if success_count >= 2:
        print("✅ Game state transition debugging added!")
        print("\n🎯 What was added:")
        print("1. ✅ Comprehensive debugging to game state update flow")
        print("2. ✅ Enhanced debug panel showing game status and gameStarted state")
        print("3. ✅ Socket event tracking in gameService")
        print("4. ✅ Navigation debugging for game board transition")
        print("\n🚀 Next steps:")
        print("1. Restart your frontend")
        print("2. Get 4 users in teams and click 'Start Game'")
        print("3. Watch for these debug messages:")
        print("   - 🎮 [GAMESERVICE] game:state-updated event received")
        print("   - 🎮 [ROOMPAGE] New game status: playing")
        print("   - 🚀 [ROOMPAGE] Game status is playing - setting gameStarted to true")
        print("   - 🎉 [ROOMPAGE] Rendering game started screen")
        print("\n🔍 What to look for:")
        print("- Is the 'game:state-updated' event being received?")
        print("- Does the game status show 'playing' in the debug panel?") 
        print("- Does 'Game Started: Yes' appear in the debug panel?")
        print("- If gameStarted=Yes but still stuck, then GamePage has issues")
    else:
        print(f"⚠️  Only {success_count}/3 fixes applied. Check error messages above.")
    
    return success_count >= 2

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)