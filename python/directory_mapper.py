import os
import sys

def map_directory_structure(root_path='.', max_depth=4, current_depth=0):
    """Maps the project directory structure with file details, ignoring unnecessary folders."""
    
    # Folders to ignore
    ignore_folders = {
        'node_modules', '.git', 'dist', 'build', '.next', 
        '__pycache__', '.vscode', '.idea', 'coverage',
        'logs', 'tmp', 'temp'
    }
    
    # File extensions to ignore
    ignore_extensions = {'.log', '.tmp', '.cache'}
    
    items = []
    if current_depth >= max_depth:
        return items
    
    try:
        for item in sorted(os.listdir(root_path)):
            if item.startswith('.') and item not in {'.env.example', '.gitignore', '.env.template'}:
                continue
                
            # Skip ignored folders
            if item in ignore_folders:
                continue
                
            item_path = os.path.join(root_path, item)
            relative_path = os.path.relpath(item_path, '.')
            
            if os.path.isdir(item_path):
                # Directory
                indent = "  " * current_depth
                items.append(f"{indent}{item}/")
                
                # Recursively map subdirectories
                subdirectory_items = map_directory_structure(
                    item_path, max_depth, current_depth + 1
                )
                items.extend(subdirectory_items)
            else:
                # File - check if we should ignore it
                _, ext = os.path.splitext(item)
                if ext in ignore_extensions:
                    continue
                    
                indent = "  " * current_depth
                try:
                    size = os.path.getsize(item_path)
                    if size < 1024:
                        size_str = f"{size}B"
                    elif size < 1024 * 1024:
                        size_str = f"{size // 1024}KB"
                    else:
                        size_str = f"{size // (1024 * 1024)}MB"
                    
                    items.append(f"{indent}{item} ({size_str})")
                except OSError:
                    items.append(f"{indent}{item} (size unknown)")
    
    except PermissionError:
        pass
    except FileNotFoundError:
        pass
    
    return items

def update_changelog():
    """Update changelog with script execution info."""
    try:
        changelog_path = "CHANGELOG.md"
        if os.path.exists(changelog_path):
            with open(changelog_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find Python Scripts section
            if "## Python Scripts Run" not in content:
                # Add section if it doesn't exist
                content += "\n\n## Python Scripts Run\n"
            
            # Add new entry
            new_entry = "- directory_mapper.py: Generated clean project structure to project_structure.txt (ignored node_modules)\n"
            
            # Insert after the Python Scripts Run header
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip() == "## Python Scripts Run":
                    lines.insert(i + 1, new_entry)
                    break
            
            # Write back
            with open(changelog_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
                
    except Exception as e:
        pass  # Silently fail if changelog update doesn't work

def main():
    output_file = "project_structure.txt"
    
    structure = map_directory_structure()
    
    # Create output content
    output_content = []
    output_content.append("CODENAMES PROJECT STRUCTURE (Clean)")
    output_content.append("=" * 50)
    output_content.extend(structure)
    output_content.append("\n" + "=" * 50)
    output_content.append(f"Total items: {len(structure)}")
    
    # Write to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_content))
        print(f"Project structure saved to {output_file}")
    except Exception as e:
        print(f"Error writing to file: {e}")
        # Fallback to console output
        for line in output_content:
            print(line)
    
    # Update changelog
    update_changelog()

if __name__ == "__main__":
    main()
