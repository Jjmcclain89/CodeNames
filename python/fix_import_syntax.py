#!/usr/bin/env python3
"""
Fix the malformed import statement in HomePage.tsx
"""

import os

def fix_import_syntax():
    """Fix the malformed import statements"""
    
    home_page_path = 'frontend/src/pages/HomePage.tsx'
    
    if not os.path.exists(home_page_path):
        print(f"❌ File not found: {home_page_path}")
        return False
    
    print("🔧 Fixing import syntax error...")
    
    # Read the current file
    with open(home_page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Show the problematic imports
    lines = content.split('\n')
    print("🔍 Current import lines:")
    for i, line in enumerate(lines[:10]):
        if 'import' in line:
            print(f"  Line {i+1}: {line}")
    
    # Fix the malformed import statements
    # Remove any duplicate or malformed imports
    content = content.replace(
        'import React, { useState, useEffect }\nimport { socketService }, { useState, useEffect } from \'react\';',
        'import React, { useState, useEffect } from \'react\';\nimport { socketService } from \'../services/socketService\';'
    )
    
    # Also try alternative patterns
    content = content.replace(
        'import React, { useState, useEffect }\nimport { socketService }',
        'import React, { useState, useEffect } from \'react\';\nimport { socketService }'
    )
    
    # Fix any other malformed patterns
    content = content.replace(
        'import { socketService }, { useState, useEffect } from \'react\';',
        'import { socketService } from \'../services/socketService\';'
    )
    
    # Ensure proper React import
    if 'import React, { useState, useEffect } from \'react\';' not in content:
        # Find and fix React import
        content = content.replace(
            'import React, { useState, useEffect }',
            'import React, { useState, useEffect } from \'react\';'
        )
    
    # Ensure socketService import exists and is correct
    if 'import { socketService }' not in content:
        # Add socketService import after React import
        content = content.replace(
            'import React, { useState, useEffect } from \'react\';',
            'import React, { useState, useEffect } from \'react\';\nimport { socketService } from \'../services/socketService\';'
        )
    
    # Clean up any duplicate React imports
    import_lines = []
    other_lines = []
    in_imports = True
    
    for line in content.split('\n'):
        if line.strip().startswith('import '):
            if in_imports:
                import_lines.append(line)
            else:
                other_lines.append(line)
        else:
            if line.strip() == '':
                if in_imports:
                    import_lines.append(line)
                else:
                    other_lines.append(line)
            else:
                in_imports = False
                other_lines.append(line)
    
    # Deduplicate and fix imports
    clean_imports = []
    seen_imports = set()
    
    for line in import_lines:
        if line.strip() and line not in seen_imports:
            seen_imports.add(line)
            clean_imports.append(line)
    
    # Ensure we have the required imports
    has_react = any('import React' in line for line in clean_imports)
    has_socket = any('socketService' in line for line in clean_imports)
    has_navigate = any('useNavigate' in line for line in clean_imports)
    has_chatroom = any('ChatRoom' in line for line in clean_imports)
    
    final_imports = []
    if has_react:
        final_imports.extend([line for line in clean_imports if 'import React' in line])
    else:
        final_imports.append('import React, { useState, useEffect } from \'react\';')
    
    if has_socket:
        final_imports.extend([line for line in clean_imports if 'socketService' in line])
    else:
        final_imports.append('import { socketService } from \'../services/socketService\';')
    
    # Add other imports
    for line in clean_imports:
        if 'import React' not in line and 'socketService' not in line:
            final_imports.append(line)
    
    # Reconstruct the file
    content = '\n'.join(final_imports) + '\n\n' + '\n'.join(other_lines)
    
    # Write the fixed content back
    with open(home_page_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Fixed import syntax!")
    
    # Show the fixed imports
    with open(home_page_path, 'r', encoding='utf-8') as f:
        fixed_content = f.read()
    
    fixed_lines = fixed_content.split('\n')
    print("\n📝 Fixed import lines:")
    for i, line in enumerate(fixed_lines[:10]):
        if 'import' in line or line.strip() == '':
            print(f"  Line {i+1}: {line}")
        elif line.strip() and not line.startswith('import'):
            break
    
    return True

if __name__ == "__main__":
    success = fix_import_syntax()
    if success:
        print("\n🎯 Next steps:")
        print("1. Check if the TypeScript error is resolved")
        print("2. Go to homepage and look for the Socket Debug Panel")
        print("3. If still errors, share the first 10 lines of HomePage.tsx")
    else:
        print("\n❌ Import fix failed - please check the file manually")
