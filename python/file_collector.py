#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Collector for Phase 1 Debugging
Collects all the frontend files needed to debug Phase 1 socket foundation issues
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def add_changelog_entry():
    """Add entry to CHANGELOG.md"""
    try:
        changelog_path = Path("CHANGELOG.md")
        if not changelog_path.exists():
            print("Warning: CHANGELOG.md not found")
            return
            
        # Read current changelog
        with open(changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the Python Scripts section
        if "### Python Scripts Run" not in content:
            # Add the section if it doesn't exist
            unreleased_section = content.find("## [Unreleased]")
            if unreleased_section != -1:
                insert_point = content.find("### Added", unreleased_section)
                if insert_point != -1:
                    new_section = "\n### Python Scripts Run\n- File collector script: Gathered Phase 1 frontend files for debugging\n"
                    content = content[:insert_point] + new_section + content[insert_point:]
                else:
                    # Add after [Unreleased] header
                    insert_point = content.find("\n", unreleased_section) + 1
                    new_section = "\n### Python Scripts Run\n- File collector script: Gathered Phase 1 frontend files for debugging\n"
                    content = content[:insert_point] + new_section + content[insert_point:]
        else:
            # Add to existing section
            section_start = content.find("### Python Scripts Run")
            section_end = content.find("\n###", section_start + 1)
            if section_end == -1:
                section_end = content.find("\n## ", section_start + 1)
            
            entry = f"- File collector script: Gathered Phase 1 frontend files for debugging ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n"
            
            if section_end != -1:
                insert_point = section_end
                content = content[:insert_point] + entry + content[insert_point:]
            else:
                content += entry
        
        # Write back to changelog
        with open(changelog_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Updated CHANGELOG.md")
        
    except Exception as e:
        print(f"⚠️ Could not update CHANGELOG.md: {e}")

def read_file_safely(file_path):
    """Read a file safely with proper encoding"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"
    except Exception as e:
        return f"Error reading file: {e}"

def collect_phase1_files():
    """Collect all files needed for Phase 1 debugging"""
    
    # Files needed for Phase 1 debugging
    required_files = [
        "frontend/src/pages/LoginPage.tsx",
        "frontend/src/services/authService.ts", 
        "frontend/src/services/socketService.ts",
        "frontend/src/App.tsx",
        "frontend/src/hooks/useSocket.ts",
        "frontend/.env",
        "python/fix_login_input.py"
    ]
    
    print("🔍 Collecting Phase 1 Frontend Files for Debugging")
    print("=" * 60)
    
    output_content = []
    missing_files = []
    
    for file_path in required_files:
        full_path = Path(file_path)
        
        if full_path.exists():
            print(f"✅ Found: {file_path}")
            content = read_file_safely(full_path)
            
            output_content.append(f"""
{'='*80}
FILE: {file_path}
SIZE: {full_path.stat().st_size} bytes
{'='*80}

{content}

""")
        else:
            print(f"❌ Missing: {file_path}")
            missing_files.append(file_path)
    
    # Create consolidated output file
    output_file = Path("python/phase1_files_collected.txt")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"""Phase 1 Frontend Files Collection
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Purpose: Debug login input autocomplete and API connection issues for Phase 1 Socket Foundation

{'='*80}
COLLECTION SUMMARY
{'='*80}

Files Collected: {len(required_files) - len(missing_files)}/{len(required_files)}
Missing Files: {len(missing_files)}

""")
        
        if missing_files:
            f.write("Missing Files:\n")
            for missing in missing_files:
                f.write(f"- {missing}\n")
            f.write("\n")
        
        f.write("".join(output_content))
    
    print(f"\n📁 All file contents saved to: {output_file}")
    print(f"📊 Collected {len(required_files) - len(missing_files)}/{len(required_files)} files")
    
    if missing_files:
        print(f"\n⚠️ Missing {len(missing_files)} files:")
        for missing in missing_files:
            print(f"   - {missing}")
        print("\nYou may need to create these files or check their locations.")
    
    print(f"\n🎯 Next steps:")
    print(f"   1. Review the collected file: {output_file}")
    print(f"   2. Upload this file to Claude for Phase 1 debugging")
    print(f"   3. Run any fixes identified")
    
    return output_file, missing_files

if __name__ == "__main__":
    try:
        # Ensure we're in the project root
        if not Path("frontend").exists() or not Path("backend").exists():
            print("❌ Error: Please run this script from the project root directory")
            print("   Current directory:", os.getcwd())
            sys.exit(1)
        
        # Collect the files
        output_file, missing_files = collect_phase1_files()
        
        # Update changelog
        add_changelog_entry()
        
        print(f"\n🚀 File collection complete!")
        print(f"   Output file: {output_file}")
        print(f"   Ready for Phase 1 debugging session!")
        
    except KeyboardInterrupt:
        print("\n❌ Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)