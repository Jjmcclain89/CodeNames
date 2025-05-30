#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add Debug Route to App.tsx
Adds the debug page route for Phase 1 testing
"""

from pathlib import Path

def add_debug_route():
    """Add debug route to App.tsx"""
    app_path = Path("frontend/src/App.tsx")
    
    if not app_path.exists():
        print("❌ App.tsx not found!")
        return False
    
    # Read current App.tsx
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add DebugPage import if not present
    if "DebugPage" not in content:
        import_line = "import DebugPage from './pages/DebugPage';"
        
        # Find where to insert the import (after other page imports)
        room_import_pos = content.find("import RoomPage")
        if room_import_pos != -1:
            insert_pos = content.find('\n', room_import_pos) + 1
            content = content[:insert_pos] + import_line + '\n' + content[insert_pos:]
        else:
            print("❌ Could not find RoomPage import to add DebugPage import")
            return False
    
    # Add debug route if not present
    if 'path="/debug"' not in content:
        debug_route = '''            <Route 
              path="/debug" 
              element={<DebugPage />} 
            />'''
        
        # Find where to insert the route (before the last closing Routes tag)
        routes_end_pos = content.rfind('</Routes>')
        if routes_end_pos != -1:
            content = content[:routes_end_pos] + debug_route + '\n            ' + content[routes_end_pos:]
        else:
            print("❌ Could not find </Routes> to add debug route")
            return False
    
    # Write back to App.tsx
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Added debug route to App.tsx")
    return True

def main():
    """Main execution"""
    print("Adding debug route to App.tsx...")
    
    if add_debug_route():
        print("✅ Debug route added successfully!")
        print("   You can now visit: http://localhost:5173/debug")
    else:
        print("❌ Failed to add debug route")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
