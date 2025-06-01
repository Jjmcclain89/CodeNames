#!/usr/bin/env python3
"""
Fix Frontend Player Display - Simple string replacement approach
"""

def fix_frontend_player_display():
    """Fix the frontend to use consistent player source"""
    
    file_path = "frontend/src/pages/RoomPage.tsx"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔧 Fixing frontend player display consistency...")
        
        # Find and replace the debug section with better info
        old_debug = '''        <div className="mb-4 bg-yellow-50 border border-yellow-200 rounded p-3 text-xs">
          <strong>🔍 Debug:</strong> Connected: {isConnected ? 'Yes' : 'No'} | 
          Game State: {gameState ? 'Loaded' : 'None'} | 
          Players in Game: {gameState?.players?.length || 0} | 
          User: {currentUser?.username}
        </div>'''
        
        new_debug = '''        <div className="mb-4 bg-yellow-50 border border-yellow-200 rounded p-3 text-xs">
          <strong>🔍 Debug:</strong> Connected: {isConnected ? 'Yes' : 'No'} | 
          Game State: {gameState ? 'Loaded' : 'None'} | 
          Game Players: {gameState?.players?.length || 0} | 
          Room Players: {players.length} | 
          User: {currentUser?.username} | 
          Room: {roomCode}
        </div>'''
        
        if old_debug in content:
            content = content.replace(old_debug, new_debug)
            print("✅ Updated debug info to show both player sources")
        else:
            print("ℹ️  Debug section not found in expected format, skipping")
        
        # Ensure we're consistently using gameState.players as primary source
        # Look for the players list section and make sure it's using gameState first
        
        # Find the players section
        players_section_start = content.find('👥 Players (')
        if players_section_start != -1:
            # Find the end of this line
            line_end = content.find(')', players_section_start) + 1
            current_line = content[players_section_start:line_end]
            
            # Replace with consistent format
            new_line = '👥 Players ({gameState?.players?.length || players.length})'
            content = content.replace(current_line, new_line)
            print("✅ Fixed player count display")
        
        # Also ensure the player mapping uses gameState as primary
        old_map = '(gameState?.players || players).map((player: any) =>'
        new_map = '(gameState?.players || players).map((player: any) =>'
        
        if old_map in content:
            print("✅ Player mapping already correct")
        else:
            # Try to find variations and fix them
            variations = [
                '(players || gameState?.players).map((player: any) =>',
                'players.map((player: any) =>',
                'gameState.players.map((player: any) =>'
            ]
            
            for old_variation in variations:
                if old_variation in content:
                    content = content.replace(old_variation, new_map)
                    print(f"✅ Fixed player mapping from: {old_variation}")
                    break
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Frontend player display consistency fixed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing frontend: {e}")
        return False

def main():
    print("🔧 FIXING FRONTEND DISPLAY CONSISTENCY")
    print("=" * 45)
    
    if fix_frontend_player_display():
        print("\n🎉 FRONTEND FIXES APPLIED!")
        print("\n🧪 Test Steps:")
        print("1. Restart frontend: npm run dev")
        print("2. Open 2 browser windows")
        print("3. Both join same room code")
        print("4. Check debug info shows both players")
        print("5. Send chat messages (shouldn't disconnect)")
        print("6. Try team assignment between players")
    else:
        print("\n❌ Frontend fixes failed")

if __name__ == "__main__":
    main()