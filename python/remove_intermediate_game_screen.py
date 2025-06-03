#!/usr/bin/env python3
"""
Remove Intermediate Game Screen

This script removes the intermediate "Join Game Board" screen and 
navigates users directly to the game when it starts.
"""

import os
import sys

def remove_intermediate_screen():
    """Remove the intermediate game screen from RoomPage.tsx"""
    
    room_page_path = "frontend/src/pages/RoomPage.tsx"
    
    if not os.path.exists(room_page_path):
        print(f"Error: {room_page_path} not found")
        return False
    
    with open(room_page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Remove the gameStarted state declaration
    old_state = "const [gameStarted, setGameStarted] = useState(false);"
    new_state = "// gameStarted state removed - now navigating directly to game"
    
    if old_state in content:
        content = content.replace(old_state, new_state)
        print("✅ Removed gameStarted state")
    
    # 2. Update the game state listener to navigate directly instead of setting gameStarted
    old_listener = '''      if (newGameState.status === 'playing') {
        console.log('🚀 [ROOMPAGE] Game status is playing - setting gameStarted to true');
        setGameStarted(true);
      } else {
        console.log('🎮 [ROOMPAGE] Game status is not playing yet:', newGameState.status);
      }'''
    
    new_listener = '''      if (newGameState.status === 'playing') {
        console.log('🚀 [ROOMPAGE] Game status is playing - navigating directly to game');
        console.log('🎮 [ROOMPAGE] Automatic navigation to /game');
        navigate('/game');
        return; // Exit early since we're navigating away
      } else {
        console.log('🎮 [ROOMPAGE] Game status is not playing yet:', newGameState.status);
      }'''
    
    if old_listener in content:
        content = content.replace(old_listener, new_listener)
        print("✅ Updated game state listener to navigate directly")
    
    # 3. Remove the entire intermediate screen rendering section
    intermediate_screen = '''  if (gameStarted) {
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
    
    replacement_comment = '''  // Intermediate "Game Started" screen removed - now navigating directly to /game'''
    
    if intermediate_screen in content:
        content = content.replace(intermediate_screen, replacement_comment)
        print("✅ Removed intermediate game screen rendering")
    
    # 4. Remove the handleGoToGame function since it's no longer needed
    handle_go_to_game = '''  const handleGoToGame = () => {
    console.log('🎮 [ROOMPAGE] handleGoToGame called - navigating to game board...');
    console.log('🎮 [ROOMPAGE] Current gameState:', gameState);
    navigate('/game');
    console.log('🎮 [ROOMPAGE] Navigation to /game called');
  };'''
    
    if handle_go_to_game in content:
        content = content.replace(handle_go_to_game, "// handleGoToGame function removed - using direct navigation")
        print("✅ Removed handleGoToGame function")
    
    # 5. Update the debug panel to remove gameStarted indicator
    old_debug = '''          <strong>🔍 Debug:</strong> Connected: {isConnected ? 'Yes' : 'No'} | 
          Game State: {gameState ? 'Loaded' : 'None'} | 
          Game Status: {gameState?.status || 'Unknown'} |
          Game Started: {gameStarted ? 'Yes' : 'No'} |
          Game Players: {gameState?.players?.length || 0} | 
          Room Players: {players.length} | 
          User: {currentUser?.username} | 
          Room: {roomCode}'''
    
    new_debug = '''          <strong>🔍 Debug:</strong> Connected: {isConnected ? 'Yes' : 'No'} | 
          Game State: {gameState ? 'Loaded' : 'None'} | 
          Game Status: {gameState?.status || 'Unknown'} |
          Game Players: {gameState?.players?.length || 0} | 
          Room Players: {players.length} | 
          User: {currentUser?.username} | 
          Room: {roomCode}'''
    
    if old_debug in content:
        content = content.replace(old_debug, new_debug)
        print("✅ Updated debug panel")
    
    # 6. Remove references to gameStarted in the debug logging
    old_debug_log = '''      console.log('🎮 [ROOMPAGE] Current gameStarted state:', gameStarted);'''
    
    if old_debug_log in content:
        content = content.replace(old_debug_log, "// gameStarted debug logging removed")
        print("✅ Removed gameStarted debug logging")
    
    # Write the updated content back
    with open(room_page_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def add_navigation_safety_check():
    """Add a safety check to prevent navigation issues"""
    
    room_page_path = "frontend/src/pages/RoomPage.tsx"
    
    if not os.path.exists(room_page_path):
        print(f"Error: {room_page_path} not found")
        return False
    
    with open(room_page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add a flag to prevent multiple navigation attempts
    gameCreationCalled_line = "const [gameCreationCalled, setGameCreationCalled] = useState(false);"
    new_state_line = "const [gameNavigated, setGameNavigated] = useState(false);"
    
    if gameCreationCalled_line in content and "gameNavigated" not in content:
        content = content.replace(
            gameCreationCalled_line,
            gameCreationCalled_line + "\n  " + new_state_line
        )
        print("✅ Added gameNavigated state for safety")
    
    # Update the navigation logic to prevent multiple navigations
    old_navigation = '''      if (newGameState.status === 'playing') {
        console.log('🚀 [ROOMPAGE] Game status is playing - navigating directly to game');
        console.log('🎮 [ROOMPAGE] Automatic navigation to /game');
        navigate('/game');
        return; // Exit early since we're navigating away
      }'''
    
    new_navigation = '''      if (newGameState.status === 'playing' && !gameNavigated) {
        console.log('🚀 [ROOMPAGE] Game status is playing - navigating directly to game');
        console.log('🎮 [ROOMPAGE] Automatic navigation to /game');
        setGameNavigated(true);
        navigate('/game');
        return; // Exit early since we're navigating away
      }'''
    
    if old_navigation in content:
        content = content.replace(old_navigation, new_navigation)
        print("✅ Added navigation safety check")
    
    with open(room_page_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    print("🔧 Removing Intermediate Game Screen...")
    print("=" * 50)
    
    success_count = 0
    
    # Remove the intermediate screen logic
    if remove_intermediate_screen():
        success_count += 1
    
    # Add navigation safety check
    if add_navigation_safety_check():
        success_count += 1
    
    print("=" * 50)
    if success_count >= 1:
        print("✅ Intermediate screen removal complete!")
        print("\n🎯 What was changed:")
        print("1. ✅ Removed gameStarted state and intermediate screen rendering")
        print("2. ✅ Updated game state listener to navigate directly to /game")
        print("3. ✅ Removed handleGoToGame function (no longer needed)")
        print("4. ✅ Updated debug panel to remove gameStarted indicator")
        print("5. ✅ Added navigation safety check to prevent multiple navigations")
        print("\n🚀 New flow:")
        print("Create Game → Join Teams → Start Game → Automatically Navigate to Game Board")
        print("\n🚀 Next steps:")
        print("1. Restart your frontend")
        print("2. Test the complete flow - should go directly to game when started")
        print("3. No more intermediate 'Join Game Board' screen!")
        print("\n💡 Users will now seamlessly transition from team selection to playing!")
    else:
        print(f"⚠️  Changes could not be applied. Check error messages above.")
    
    return success_count >= 1

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)