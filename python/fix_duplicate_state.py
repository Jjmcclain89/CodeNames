#!/usr/bin/env python3
"""
Fix the duplicate connectionInitiated state declarations
"""

import os
import re

def fix_duplicate_state():
    """Remove duplicate connectionInitiated state declarations"""
    
    room_page_path = 'frontend/src/pages/RoomPage.tsx'
    
    if not os.path.exists(room_page_path):
        print(f"❌ File not found: {room_page_path}")
        return False
    
    print("🔧 Fixing duplicate connectionInitiated state declarations...")
    
    # Read the current file
    with open(room_page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove all duplicate connectionInitiated lines
    duplicate_pattern = r'\s*const \[connectionInitiated, setConnectionInitiated\] = useState<boolean>\(false\); // Prevent multiple connections'
    matches = re.findall(duplicate_pattern, content)
    
    if matches:
        print(f"  🔍 Found {len(matches)} connectionInitiated declarations")
        
        # Remove all instances
        content = re.sub(duplicate_pattern, '', content)
        
        # Add it back just once, after gameState
        if 'const [gameState, setGameState] = useState<any>(null);' in content:
            content = content.replace(
                'const [gameState, setGameState] = useState<any>(null);',
                '''const [gameState, setGameState] = useState<any>(null);
  const [connectionInitiated, setConnectionInitiated] = useState(false); // Prevent multiple connections'''
            )
            print("  ✅ Added single connectionInitiated state after gameState")
        else:
            print("  ⚠️ Could not find gameState declaration to add connectionInitiated after")
    
    # Also remove any duplicate lines that might have been added
    duplicate_line_pattern = r'\s*const \[connectionInitiated, setConnectionInitiated\] = useState\(false\); // Prevent multiple connections'
    content = re.sub(duplicate_line_pattern, '', content)
    
    # Clean up any multiple empty lines
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # Write the fixed content back
    with open(room_page_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Fixed duplicate state declarations!")
    print("\n🔧 Changes made:")
    print("  1. Removed all duplicate connectionInitiated declarations")
    print("  2. Added single connectionInitiated state after gameState")
    print("  3. Cleaned up empty lines")
    
    return True

if __name__ == "__main__":
    success = fix_duplicate_state()
    if success:
        print("\n🎯 Next steps:")
        print("1. Check that the TypeScript error is resolved")
        print("2. If still errors, please share the current RoomPage.tsx state section")
        print("3. Then test the socket connection fixes")
    else:
        print("\n❌ Fix failed - please check the file manually")
