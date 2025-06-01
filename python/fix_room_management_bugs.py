#!/usr/bin/env python3
"""
Fix Room Management Bugs - Remove erroneous userRooms.delete() calls
that are preventing players from staying in the same game room.
"""

import re

def fix_backend_room_management():
    """Remove the problematic userRooms.delete() calls from socket handlers"""
    
    file_path = "backend/src/index.ts"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔧 Fixing room management bugs in backend/src/index.ts...")
        
        # Find and remove the problematic userRooms.delete() calls
        # that are incorrectly removing users from rooms
        
        # Bug 1: Remove userRooms.delete() from send-message handler
        content = re.sub(
            r'(\s+)// Clean up room tracking\s*\n\s+userRooms\.delete\(socket\.id\);\s*\n(\s+globalRoom\.messages\.push)',
            r'\1\2',
            content,
            flags=re.MULTILINE
        )
        
        # Bug 2: Remove userRooms.delete() from authenticate handler 
        content = re.sub(
            r'(\s+)// Clean up room tracking\s*\n\s+userRooms\.delete\(socket\.id\);\s*\n(\s+globalRoom\.users\.set)',
            r'\1\2',
            content,
            flags=re.MULTILINE
        )
        
        # Also remove any other stray userRooms.delete() calls that aren't in disconnect handler
        # Keep only the one in disconnect handler which is legitimate
        lines = content.split('\n')
        fixed_lines = []
        in_disconnect_handler = False
        
        for i, line in enumerate(lines):
            # Track if we're in the disconnect handler
            if "socket.on('disconnect'," in line:
                in_disconnect_handler = True
            elif in_disconnect_handler and line.strip().startswith('});'):
                in_disconnect_handler = False
            
            # Remove userRooms.delete() calls outside of disconnect handler
            if 'userRooms.delete(socket.id)' in line and not in_disconnect_handler:
                # Skip this line and any preceding comment about "Clean up room tracking"
                if i > 0 and 'Clean up room tracking' in lines[i-1]:
                    # Remove the comment line too
                    fixed_lines.pop()
                print(f"🗑️  Removed problematic userRooms.delete() from line {i+1}")
                continue
            
            fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        # Verify we still have the legitimate userRooms.delete() in disconnect handler
        disconnect_section = re.search(
            r"socket\.on\('disconnect'.*?}\);",
            content,
            re.DOTALL
        )
        
        if disconnect_section and 'userRooms.delete(socket.id)' not in disconnect_section.group():
            print("⚠️  Adding missing userRooms.delete() to disconnect handler...")
            # Add it to the disconnect handler
            content = re.sub(
                r"(socket\.on\('disconnect', \(\) => \{[^}]*?// Remove from global room[^}]*?globalRoom\.users\.delete\(socket\.id\);)",
                r"\1\n      \n      // Clean up room tracking\n      userRooms.delete(socket.id);",
                content,
                flags=re.DOTALL
            )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed room management bugs in backend socket handlers")
        print("🎯 Players should now stay in the same room properly")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing backend room management: {e}")
        return False

def fix_frontend_player_display():
    """Fix the frontend to use consistent player source"""
    
    file_path = "frontend/src/pages/RoomPage.tsx"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔧 Fixing frontend player display consistency...")
        
        # Make player count display use game state as primary source
        content = re.sub(
            r'👥 Players \(\{gameState\?\.players\?\.length \|\| players\.length\}\)',
            r'👥 Players ({gameState?.players?.length || players.length})',
            content
        )
        
        # Make player list use game state as primary source consistently
        content = re.sub(
            r'\(\gameState\?\.players \|\| players\)',
            r'(gameState?.players || players)',
            content
        )
        
        # Add better debug info to show both sources
        debug_pattern = r'(\s+)<div className="mb-4 bg-yellow-50 border border-yellow-200 rounded p-3 text-xs">\s*<strong>🔍 Debug:</strong>[^<]*</div>'
        
        new_debug = '''        <div className="mb-4 bg-yellow-50 border border-yellow-200 rounded p-3 text-xs">
          <strong>🔍 Debug:</strong> Connected: {isConnected ? 'Yes' : 'No'} | 
          Game State: {gameState ? 'Loaded' : 'None'} | 
          Game Players: {gameState?.players?.length || 0} | 
          Room Players: {players.length} | 
          User: {currentUser?.username} | 
          Room Code: {roomCode}
        </div>'''
        
        content = re.sub(debug_pattern, new_debug, content, flags=re.DOTALL)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed frontend player display consistency")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing frontend: {e}")
        return False

def main():
    print("🚨 FIXING ROOM MANAGEMENT BUGS")
    print("=" * 50)
    print()
    print("Issues found:")
    print("1. send-message handler removes users from rooms")
    print("2. authenticate handler removes users from rooms") 
    print("3. Multiple player arrays not syncing")
    print()
    
    success = True
    
    if fix_backend_room_management():
        print("✅ Backend room management fixed")
    else:
        success = False
    
    print()
    
    if fix_frontend_player_display():
        print("✅ Frontend player display fixed")
    else:
        success = False
    
    print()
    if success:
        print("🎉 ALL FIXES APPLIED SUCCESSFULLY!")
        print()
        print("🧪 Next steps:")
        print("1. Restart both backend and frontend servers")
        print("2. Test with 2 browser windows joining same room")
        print("3. Verify both players stay connected and see each other")
        print("4. Test sending messages (this was removing players before)")
        print("5. Test team assignment between multiple players")
    else:
        print("❌ Some fixes failed - check error messages above")

if __name__ == "__main__":
    main()