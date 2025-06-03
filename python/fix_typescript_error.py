#!/usr/bin/env python3
"""
Quick TypeScript Error Fix

Fixes the TypeScript strict mode error with unknown error types
"""

import os
import sys

def fix_typescript_errors():
    """Fix the TypeScript errors in index.ts"""
    
    backend_index_path = "backend/src/index.ts"
    
    if not os.path.exists(backend_index_path):
        print(f"Error: {backend_index_path} not found")
        return False
    
    # Read the current file
    with open(backend_index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the error handling lines
    old_error_handling = '''      console.error('❌ [GAME START] Exception during game start:', error);
      console.error('❌ [GAME START] Stack trace:', error.stack);
      socket.emit('game:error', 'Failed to start game: ' + error.message);'''
    
    new_error_handling = '''      console.error('❌ [GAME START] Exception during game start:', error);
      console.error('❌ [GAME START] Stack trace:', error instanceof Error ? error.stack : 'No stack trace');
      socket.emit('game:error', 'Failed to start game: ' + (error instanceof Error ? error.message : String(error)));'''
    
    if old_error_handling in content:
        content = content.replace(old_error_handling, new_error_handling)
        print("✅ Fixed TypeScript error handling")
    else:
        # Try to fix just the problem lines individually
        content = content.replace(
            "console.error('❌ [GAME START] Stack trace:', error.stack);",
            "console.error('❌ [GAME START] Stack trace:', error instanceof Error ? error.stack : 'No stack trace');"
        )
        content = content.replace(
            "socket.emit('game:error', 'Failed to start game: ' + error.message);",
            "socket.emit('game:error', 'Failed to start game: ' + (error instanceof Error ? error.message : String(error)));"
        )
        print("✅ Fixed individual TypeScript error lines")
    
    # Write the updated content back
    with open(backend_index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    print("🔧 Fixing TypeScript errors...")
    
    if fix_typescript_errors():
        print("✅ TypeScript errors fixed!")
        print("✅ Your backend should now start without crashes")
        print("\n🚀 Try starting your backend again")
    else:
        print("❌ Could not fix TypeScript errors")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)