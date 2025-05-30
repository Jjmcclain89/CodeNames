#!/usr/bin/env python3
"""
Directory Structure Mapper for Codenames Project
Generates a comprehensive directory tree to help track project structure
"""

import os
import json
from datetime import datetime

def should_ignore(path, ignore_patterns):
    """Check if a path should be ignored based on common patterns"""
    ignore_list = [
        'node_modules', '.git', 'dist', 'build', '.next', 
        '.vscode', '.idea', '__pycache__', '.pytest_cache',
        'coverage', '.nyc_output', '.env.local', '.env.production',
        '.DS_Store', 'Thumbs.db', '*.log', '.cache', 'temp', 'tmp'
    ]
    ignore_list.extend(ignore_patterns)
    
    for pattern in ignore_list:
        if pattern in path or path.endswith(pattern.replace('*', '')):
            return True
    return False

def generate_tree(root_path, max_depth=4, ignore_patterns=None):
    """Generate directory tree structure"""
    if ignore_patterns is None:
        ignore_patterns = []
    
    tree = {
        'name': os.path.basename(root_path) or root_path,
        'type': 'directory',
        'path': root_path,
        'children': []
    }
    
    def build_tree(current_path, current_depth=0):
        if current_depth >= max_depth:
            return None
            
        items = []
        try:
            for item in sorted(os.listdir(current_path)):
                item_path = os.path.join(current_path, item)
                
                if should_ignore(item_path, ignore_patterns):
                    continue
                
                if os.path.isdir(item_path):
                    subtree = build_tree(item_path, current_depth + 1)
                    if subtree:
                        items.append({
                            'name': item,
                            'type': 'directory',
                            'path': item_path,
                            'children': subtree
                        })
                    else:
                        items.append({
                            'name': item,
                            'type': 'directory',
                            'path': item_path,
                            'children': ['...'] if current_depth + 1 >= max_depth else []
                        })
                else:
                    # Get file size
                    try:
                        size = os.path.getsize(item_path)
                        size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
                    except:
                        size_str = "unknown"
                    
                    items.append({
                        'name': item,
                        'type': 'file',
                        'path': item_path,
                        'size': size_str
                    })
        except PermissionError:
            pass
        
        return items
    
    tree['children'] = build_tree(root_path)
    return tree

def print_tree(tree_data, prefix="", is_last=True, show_size=True):
    """Print the tree in a readable format"""
    if tree_data['type'] == 'directory':
        print(f"{prefix}{'└── ' if is_last else '├── '}{tree_data['name']}/")
        new_prefix = prefix + ("    " if is_last else "│   ")
        
        children = tree_data.get('children', [])
        if children == ['...']:
            print(f"{new_prefix}└── ...")
        else:
            for i, child in enumerate(children):
                child_is_last = i == len(children) - 1
                print_tree(child, new_prefix, child_is_last, show_size)
    else:
        size_info = f" ({tree_data.get('size', 'unknown')})" if show_size else ""
        print(f"{prefix}{'└── ' if is_last else '├── '}{tree_data['name']}{size_info}")

def save_structure_json(tree_data, output_file):
    """Save the tree structure as JSON for programmatic use"""
    with open(output_file, 'w') as f:
        json.dump(tree_data, f, indent=2)

def generate_file_list(tree_data, file_types=None):
    """Generate a flat list of files matching specific types"""
    if file_types is None:
        file_types = ['.ts', '.tsx', '.js', '.jsx', '.json', '.md', '.env']
    
    files = []
    
    def extract_files(node):
        if node['type'] == 'file':
            for ext in file_types:
                if node['name'].endswith(ext):
                    files.append(node['path'])
                    break
        elif node['type'] == 'directory' and 'children' in node:
            for child in node['children']:
                if isinstance(child, dict):
                    extract_files(child)
    
    extract_files(tree_data)
    return sorted(files)

def main():
    """Main function to generate directory structure"""
    root_path = os.getcwd()
    print(f"🗂️  Mapping directory structure for: {root_path}")
    print(f"📅 Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Generate tree structure
    tree = generate_tree(root_path, max_depth=4)
    
    # Print the tree
    print_tree(tree)
    
    print("\n" + "=" * 60)
    
    # Generate file lists for key file types
    important_files = generate_file_list(tree, ['.ts', '.tsx', '.js', '.jsx'])
    config_files = generate_file_list(tree, ['.json', '.env', '.example'])
    doc_files = generate_file_list(tree, ['.md', '.txt'])
    
    print(f"\n📁 Key Source Files ({len(important_files)} found):")
    for file in important_files[:20]:  # Show first 20
        rel_path = os.path.relpath(file, root_path)
        print(f"   {rel_path}")
    if len(important_files) > 20:
        print(f"   ... and {len(important_files) - 20} more files")
    
    print(f"\n⚙️  Configuration Files ({len(config_files)} found):")
    for file in config_files:
        rel_path = os.path.relpath(file, root_path)
        print(f"   {rel_path}")
    
    print(f"\n📄 Documentation Files ({len(doc_files)} found):")
    for file in doc_files:
        rel_path = os.path.relpath(file, root_path)
        print(f"   {rel_path}")
    
    # Save JSON structure for programmatic access
    json_output = os.path.join(root_path, 'project_structure.json')
    save_structure_json(tree, json_output)
    print(f"\n💾 Full structure saved to: project_structure.json")
    
    # Update changelog
    changelog_path = os.path.join(root_path, 'CHANGELOG.md')
    if os.path.exists(changelog_path):
        try:
            with open(changelog_path, 'r') as f:
                content = f.read()
            
            # Add entry to unreleased section
            script_entry = f"""- **Python Script**: Directory structure mapper - Generated comprehensive project file tree and structure analysis ({datetime.now().strftime('%Y-%m-%d')})"""
            
            if '### Added' in content and '## [Unreleased]' in content:
                # Find the Added section under Unreleased
                lines = content.split('\n')
                new_lines = []
                in_unreleased = False
                added_entry = False
                
                for line in lines:
                    new_lines.append(line)
                    if '## [Unreleased]' in line:
                        in_unreleased = True
                    elif line.startswith('## [') and '## [Unreleased]' not in line:
                        in_unreleased = False
                    elif in_unreleased and '### Added' in line and not added_entry:
                        new_lines.append(script_entry)
                        added_entry = True
                
                with open(changelog_path, 'w') as f:
                    f.write('\n'.join(new_lines))
                
                print(f"✅ Updated CHANGELOG.md with script entry")
            else:
                print("⚠️  Could not automatically update CHANGELOG.md")
        except Exception as e:
            print(f"⚠️  Error updating changelog: {e}")
    
    print("\n🎯 Next Steps:")
    print("   1. Review the file structure above")
    print("   2. Share specific files you need for debugging")
    print("   3. Use relative paths from project root")
    print("   4. Check project_structure.json for complete details")

if __name__ == "__main__":
    main()
