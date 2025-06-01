#!/usr/bin/env python3
import os
import re
from datetime import datetime

def fix_backend_types():
    """
    Fix TypeScript errors in backend by removing problematic code and adding properly typed handler
    """
    print("🔧 Fixing backend TypeScript errors...")
    
    # Read the current backend index.ts
    try:
        with open('backend/src/index.ts', 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading backend file: {e}")
        return
    
    # Remove the problematic code that was added
    problematic_section = '''
  // Add handler for requesting current game state
  socket.on('game:request-state', () => {
    if (!socket.userId) {
      socket.emit('game:error', 'Not authenticated');
      return;
    }

    console.log('🔍 Game state requested by:', socket.username);
    
    // Try to find existing game for user
    const game = gameService.getGameByPlayer(socket.userId);
    if (game) {
      const gameState = game.getGame();
      socket.emit('game:state-updated', gameState);
      console.log('📤 Sent existing game state to:', socket.username);
    } else {
      console.log('❌ No existing game found for:', socket.username);
      socket.emit('game:error', 'No active game found');
    }
  });'''
    
    # Remove the problematic section
    content = content.replace(problematic_section, '')
    
    # Now add the properly typed handler inside the addGameHandlers function
    # Find the addGameHandlers function and add the handler there
    add_game_handlers_pattern = r'(function addGameHandlers\(socket: any, io: any\) \{[\s\S]*?)(  socket\.on\(\'game:reset\'[\s\S]*?\}\);)'
    
    replacement_handler = '''  socket.on('game:request-state', () => {
    try {
      if (!user) {
        socket.emit('game:error', 'Not authenticated');
        return;
      }

      console.log('🔍 Game state requested by:', user.username);
      
      // Try to find existing game for user
      const game = gameService.getGameByPlayer(user.id);
      if (game) {
        const gameState = game.getGame();
        socket.emit('game:state-updated', gameState);
        console.log('📤 Sent existing game state to:', user.username);
      } else {
        console.log('❌ No existing game found for:', user.username);
        socket.emit('game:error', 'No active game found');
      }
    } catch (error) {
      console.error('❌ Error handling game state request:', error);
      socket.emit('game:error', 'Failed to get game state');
    }
  });

\\2'''
    
    # Add the handler to the addGameHandlers function
    content = re.sub(add_game_handlers_pattern, f'\\1{replacement_handler}', content, flags=re.MULTILINE)
    
    # Write the corrected content back
    try:
        with open('backend/src/index.ts', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Fixed TypeScript errors in backend")
    except Exception as e:
        print(f"❌ Error writing backend file: {e}")
        return
    
    # Update changelog
    update_changelog()
    
    print("\n🎉 BACKEND FIX COMPLETE!")
    print("✅ Removed problematic socket handlers")
    print("✅ Added properly typed game state request handler")
    print("✅ Backend should now compile without errors")
    print("\n🚀 Try starting the backend server again!")

def update_changelog():
    """Update the CHANGELOG.md with this session's changes"""
    try:
        with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the "### Python Scripts Run" section and add our entry
        new_entry = f"- Backend TypeScript Fix: Fixed socket handler typing errors and added proper game state request handler (2025-05-31 {datetime.now().strftime('%H:%M')})"
        
        if "### Python Scripts Run" in content:
            content = content.replace(
                "### Python Scripts Run\n",
                f"### Python Scripts Run\n{new_entry}\n"
            )
        else:
            # Add the section if it doesn't exist
            content = content.replace(
                "## [Unreleased]\n",
                f"## [Unreleased]\n\n### Python Scripts Run\n{new_entry}\n"
            )
        
        with open('CHANGELOG.md', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Updated CHANGELOG.md")
        
    except Exception as e:
        print(f"⚠️  Could not update CHANGELOG.md: {e}")

if __name__ == "__main__":
    fix_backend_types()
