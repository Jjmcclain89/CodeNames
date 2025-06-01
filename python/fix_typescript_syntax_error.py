#!/usr/bin/env python3
"""
Fix TypeScript Syntax Error in gameService.ts
"""

def fix_gameservice_syntax():
    """Fix the syntax error in gameService.ts"""
    
    file_path = "backend/src/services/gameService.ts"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔧 Fixing TypeScript syntax error in gameService.ts...")
        
        # Find and remove the malformed method
        lines = content.split('\n')
        fixed_lines = []
        skip_lines = False
        
        for i, line in enumerate(lines):
            # If we find the broken method declaration, start skipping
            if 'createFreshGameForRoom(roomCode: string): CodenamesGameModel {' in line and not line.strip().startswith('//'):
                print(f"🗑️  Found broken method at line {i+1}, removing it")
                skip_lines = True
                continue
            
            # Skip lines until we find the end of the broken method
            if skip_lines:
                if line.strip() == '}' and not line.strip().startswith('//'):
                    skip_lines = False
                    continue
                else:
                    continue
            
            fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        # Now properly add the method in the right place
        # Find the end of the createGameForRoom method
        create_method_end = -1
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if 'createGameForRoom(roomCode: string): CodenamesGameModel {' in line:
                # Find the matching closing brace
                brace_count = 0
                for j in range(i, len(lines)):
                    if '{' in lines[j]:
                        brace_count += lines[j].count('{')
                    if '}' in lines[j]:
                        brace_count -= lines[j].count('}')
                        if brace_count == 0:
                            create_method_end = j
                            break
                break
        
        if create_method_end != -1:
            # Insert the new method after the createGameForRoom method
            new_method = [
                '',
                '  // Method to explicitly create a fresh game (for reset/restart scenarios)',
                '  createFreshGameForRoom(roomCode: string): CodenamesGameModel {',
                '    console.log(`🎮 Creating fresh game for room: ${roomCode} (deleting any existing)`);',
                '    this.deleteGameForRoom(roomCode);',
                '',
                '    const gameModel = new CodenamesGameModel(roomCode);',
                '    this.games.set(gameModel.getId(), {',
                '      model: gameModel,',
                '      lastActivity: new Date()',
                '    });',
                '',
                '    return gameModel;',
                '  }'
            ]
            
            lines = lines[:create_method_end+1] + new_method + lines[create_method_end+1:]
            content = '\n'.join(lines)
            print("✅ Added createFreshGameForRoom method properly")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing syntax: {e}")
        return False

def verify_syntax():
    """Verify the file has valid TypeScript syntax"""
    
    file_path = "backend/src/services/gameService.ts"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔍 Verifying TypeScript syntax...")
        
        # Check for common syntax issues
        issues = []
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            # Check for method declarations without proper class context
            if 'createFreshGameForRoom(' in line and not line.strip().startswith('//'):
                # Should be indented and inside class
                if not line.startswith('  ') or line.startswith('createFresh'):
                    issues.append(f"Line {i+1}: Method not properly indented/declared")
        
        if issues:
            print("❌ Found syntax issues:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print("✅ No obvious syntax issues found")
            return True
            
    except Exception as e:
        print(f"❌ Error verifying syntax: {e}")
        return False

def main():
    print("🔧 FIXING TYPESCRIPT SYNTAX ERROR")
    print("=" * 40)
    
    if fix_gameservice_syntax():
        print("✅ Syntax error fixed")
        
        if verify_syntax():
            print("✅ File appears syntactically correct")
            print("\n🔄 Try restarting the backend server now:")
            print("  cd backend && npm run dev")
        else:
            print("⚠️  Still some syntax issues - may need manual review")
    else:
        print("❌ Failed to fix syntax error")
        print("\n🛠️  Manual fix needed:")
        print("1. Open backend/src/services/gameService.ts")
        print("2. Look for broken 'createFreshGameForRoom' method around line 94")
        print("3. Remove any malformed method declarations")
        print("4. The main fix (join-or-create pattern) should still work")

if __name__ == "__main__":
    main()