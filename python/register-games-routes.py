#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Register Games Routes
Adds the missing import and app.use() statements to register games routes in backend index.ts
"""

import os
from datetime import datetime

def update_file_content(file_path, new_content):
    """Update file with proper Windows encoding"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    print("🔧 Registering Games Routes in Backend...")
    
    # Read the current backend index.ts
    backend_index_path = 'backend/src/index.ts'
    try:
        with open(backend_index_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading {backend_index_path}: {e}")
        return
    
    # Find where to add the import and route
    lines = content.split('\n')
    new_lines = []
    
    import_added = False
    route_added = False
    endpoints_updated = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # Add import after the gameService import
        if 'import { gameService }' in line and not import_added:
            new_lines.append('import gameRoutes from \'./routes/games\';')
            import_added = True
            print("✅ Added games routes import")
        
        # Add route registration after the health check endpoint but before the game socket handlers
        if 'console.log(\'🔗 API routes configured\');' in line and not route_added:
            # Insert the games routes before this line
            new_lines.insert(-1, '')
            new_lines.insert(-1, '// Games routes')
            new_lines.insert(-1, 'app.use(\'/api/games\', gameRoutes);')
            new_lines.insert(-1, '')
            route_added = True
            print("✅ Added games routes registration")
        
        # Update the 404 handler to include games endpoints
        if 'availableEndpoints: [' in line and not endpoints_updated:
            # Find the closing bracket and add games endpoints
            j = i + 1
            while j < len(lines) and ']' not in lines[j]:
                new_lines.append(lines[j])
                j += 1
            
            # Add games endpoints before closing bracket
            if j < len(lines):
                new_lines.append('      \'GET /api/games/test\',')
                new_lines.append('      \'POST /api/games/create\',')
                new_lines.append('      \'POST /api/games/join\',')
                new_lines.append(lines[j])  # The closing bracket line
                endpoints_updated = True
                print("✅ Updated 404 handler endpoints list")
            
            # Skip the lines we already processed
            i = j
    
    # If we couldn't find the perfect spots, add them manually
    if not import_added:
        print("⚠️ Could not auto-add import - adding manually")
        # Add after other imports
        for i, line in enumerate(new_lines):
            if line.startswith('import { gameService }'):
                new_lines.insert(i + 1, 'import gameRoutes from \'./routes/games\';')
                import_added = True
                break
    
    if not route_added:
        print("⚠️ Could not auto-add route - adding manually")
        # Add after health check
        for i, line in enumerate(new_lines):
            if 'Health check endpoint' in line:
                # Find the end of the health check endpoint
                j = i
                while j < len(new_lines) and '});' not in new_lines[j]:
                    j += 1
                if j < len(new_lines):
                    new_lines.insert(j + 1, '')
                    new_lines.insert(j + 2, '// Games routes')
                    new_lines.insert(j + 3, 'app.use(\'/api/games\', gameRoutes);')
                    new_lines.insert(j + 4, '')
                    route_added = True
                    break
    
    # Write the updated content
    updated_content = '\n'.join(new_lines)
    
    if update_file_content(backend_index_path, updated_content):
        print("✅ Updated backend/src/index.ts")
        
        # Show what we added
        if import_added and route_added:
            print("\n🎯 Added to backend/src/index.ts:")
            print("• import gameRoutes from './routes/games';")
            print("• app.use('/api/games', gameRoutes);")
            if endpoints_updated:
                print("• Updated 404 handler endpoints list")
        else:
            print("⚠️ Some additions may have failed - check the file manually")
    else:
        print("❌ Failed to update backend/src/index.ts")
        return
    
    # Update changelog
    try:
        changelog_path = 'CHANGELOG.md'
        with open(changelog_path, 'r', encoding='utf-8') as f:
            changelog = f.read()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        new_entry = f'- Register Games Routes: Added missing import and app.use() for games routes in backend ({timestamp})'
        
        if '### Python Scripts Run' in changelog:
            updated_changelog = changelog.replace(
                '### Python Scripts Run',
                f'### Python Scripts Run\n{new_entry}'
            )
            
            with open(changelog_path, 'w', encoding='utf-8') as f:
                f.write(updated_changelog)
            print("✅ Updated CHANGELOG.md")
    except Exception as e:
        print(f"Note: Could not update changelog: {e}")
    
    print(f"\n🎉 Games Routes Registration Complete!")
    print("\n🔧 What was fixed:")
    print("• Added: import gameRoutes from './routes/games';")
    print("• Added: app.use('/api/games', gameRoutes);")
    print("• Updated 404 handler to list games endpoints")
    print("\n🎯 Next Steps:")
    print("1. **RESTART your backend server** (critical!)")
    print("2. Test: http://localhost:3001/api/games/test in browser")
    print("3. Click 'Test API Connection' on homepage")
    print("4. Try 'Create Game' - should work now!")
    print("\n💡 The routes exist but weren't registered with Express!")
    
    print("\n🧪 Quick test URLs:")
    print("• http://localhost:3001/api/health")
    print("• http://localhost:3001/api/games/test")

if __name__ == "__main__":
    main()
