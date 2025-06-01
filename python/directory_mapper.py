import os
import sys

def map_directory_structure():
    """
    Maps the current project directory structure and saves it to a file.
    Handles Windows encoding issues properly.
    """
    
    # Ensure we can handle Unicode characters properly on Windows
    if sys.platform.startswith('win'):
        # For Windows, use UTF-8 encoding
        encoding = 'utf-8'
    else:
        encoding = 'utf-8'
    
    project_root = '.'
    output_file = 'project_structure.txt'
    
    # Files and directories to ignore
    ignore_patterns = {
        'node_modules', '.git', 'dist', 'build', '.next', 
        'coverage', '.nyc_output', '.pytest_cache', '__pycache__',
        '.env', '.env.local', '.env.development', '.env.production',
        'logs', '*.log', '.DS_Store', 'Thumbs.db',
        '.vscode', '.idea', '*.swp', '*.swo'
    }
    
    def should_ignore(name):
        """Check if file/directory should be ignored"""
        return any(pattern in name or name.endswith(pattern.replace('*', '')) 
                  for pattern in ignore_patterns)
    
    def get_structure(path, prefix="", max_depth=4, current_depth=0):
        """Recursively get directory structure"""
        if current_depth > max_depth:
            return []
        
        items = []
        try:
            entries = sorted(os.listdir(path))
        except PermissionError:
            return [f"{prefix}[Permission Denied]"]
        
        for entry in entries:
            if should_ignore(entry):
                continue
                
            entry_path = os.path.join(path, entry)
            is_dir = os.path.isdir(entry_path)
            
            if is_dir:
                items.append(f"{prefix}{entry}/")
                # Recursively get subdirectory contents
                sub_items = get_structure(
                    entry_path, 
                    prefix + "  ", 
                    max_depth, 
                    current_depth + 1
                )
                items.extend(sub_items)
            else:
                # Show file size for important files
                try:
                    size = os.path.getsize(entry_path)
                    if size > 1024:
                        size_str = f" ({size // 1024}KB)"
                    else:
                        size_str = f" ({size}B)"
                except:
                    size_str = ""
                
                items.append(f"{prefix}{entry}{size_str}")
        
        return items
    
    print("Mapping project directory structure...")
    
    try:
        structure = get_structure(project_root)
        
        # Create output content
        output_lines = [
            "=== CODENAMES PROJECT STRUCTURE ===",
            f"Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Root: {os.path.abspath(project_root)}",
            "",
            "Structure:",
            ""
        ]
        output_lines.extend(structure)
        
        # Write to file with proper encoding
        with open(output_file, 'w', encoding=encoding, errors='replace') as f:
            for line in output_lines:
                # Clean any problematic characters for Windows
                clean_line = line.encode('ascii', errors='replace').decode('ascii')
                f.write(clean_line + '\n')
        
        print(f"Project structure saved to: {output_file}")
        print(f"Total items mapped: {len(structure)}")
        
        # Also print key information to console
        print("\n=== KEY PROJECT INFO ===")
        for line in output_lines[:20]:  # Show first 20 lines
            print(line.encode('ascii', errors='replace').decode('ascii'))
        
        if len(output_lines) > 20:
            print(f"... and {len(output_lines) - 20} more lines in {output_file}")
            
    except Exception as e:
        print(f"Error mapping directory: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    map_directory_structure()
