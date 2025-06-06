import os
import json
from pathlib import Path

def map_directory_structure(root_path=".", max_depth=4):
    """
    Create a comprehensive map of the project structure.
    Returns both a tree view and a flat file list.
    """
    
    # Files to ignore
    ignore_patterns = {
        'node_modules', '.git', '.next', 'dist', 'build', '__pycache__',
        '.env', '.env.local', '.DS_Store', 'Thumbs.db', '.vscode',
        '.idea', '*.log', '.cache', 'coverage', '.nyc_output'
    }
    
    # Extensions to track
    important_extensions = {
        '.ts', '.tsx', '.js', '.jsx', '.json', '.md', '.txt',
        '.py', '.sql', '.env.example', '.gitignore', '.yml', '.yaml'
    }
    
    structure = {}
    file_list = []
    
    def should_ignore(path_name):
        for pattern in ignore_patterns:
            if pattern in str(path_name) or str(path_name).endswith(pattern.replace('*', '')):
                return True
        return False
    
    def build_tree(current_path, current_depth=0):
        if current_depth > max_depth:
            return {}
        
        tree = {}
        
        try:
            for item in sorted(Path(current_path).iterdir()):
                if should_ignore(item.name):
                    continue
                
                relative_path = str(item.relative_to(Path(root_path)))
                
                if item.is_file():
                    # Track important files
                    if any(item.name.endswith(ext) for ext in important_extensions):
                        tree[item.name] = "FILE"
                        file_list.append({
                            'path': relative_path,
                            'name': item.name,
                            'size': item.stat().st_size,
                            'extension': item.suffix
                        })
                elif item.is_dir():
                    # Recursively map directories
                    subtree = build_tree(item, current_depth + 1)
                    if subtree:  # Only include non-empty directories
                        tree[item.name] = subtree
        except PermissionError:
            pass
        
        return tree
    
    structure = build_tree(root_path)
    
    return structure, file_list

def format_tree(tree, indent=0):
    """Format the tree structure for display"""
    result = []
    for name, content in tree.items():
        prefix = "  " * indent
        if content == "FILE":
            result.append(f"{prefix}📄 {name}")
        else:
            result.append(f"{prefix}📁 {name}/")
            result.extend(format_tree(content, indent + 1))
    return result

def analyze_project_status(file_list):
    """Analyze the project status based on files present"""
    analysis = {
        'backend_status': 'NOT_FOUND',
        'frontend_status': 'NOT_FOUND',
        'config_files': [],
        'missing_critical': [],
        'phase_indicators': []
    }
    
    # Check for backend files
    backend_files = [f for f in file_list if 'backend' in f['path']]
    if backend_files:
        analysis['backend_status'] = 'FOUND'
        if any('index.ts' in f['name'] or 'server.ts' in f['name'] for f in backend_files):
            analysis['backend_status'] = 'CONFIGURED'
    
    # Check for frontend files
    frontend_files = [f for f in file_list if 'frontend' in f['path']]
    if frontend_files:
        analysis['frontend_status'] = 'FOUND'
        if any('App.tsx' in f['name'] or 'main.tsx' in f['name'] for f in frontend_files):
            analysis['frontend_status'] = 'CONFIGURED'
    
    # Check for config files
    config_patterns = ['package.json', 'tsconfig.json', 'vite.config', '.env.example']
    for pattern in config_patterns:
        matching_files = [f for f in file_list if pattern in f['name']]
        if matching_files:
            analysis['config_files'].extend([f['path'] for f in matching_files])
    
    # Check for critical missing files
    critical_files = [
        'backend/package.json',
        'frontend/package.json',
        'backend/src/index.ts',
        'frontend/src/App.tsx'
    ]
    
    for critical in critical_files:
        if not any(critical in f['path'] for f in file_list):
            analysis['missing_critical'].append(critical)
    
    # Phase indicators
    if any('socket' in f['path'].lower() or 'socket' in f['name'].lower() for f in file_list):
        analysis['phase_indicators'].append('Phase 1: Socket Foundation')
    
    if any('game' in f['path'].lower() or 'game' in f['name'].lower() for f in file_list):
        analysis['phase_indicators'].append('Phase 2: Core Game Logic')
    
    return analysis

def main():
    print("🗂️  CODENAMES PROJECT STRUCTURE MAPPER")
    print("=" * 50)
    
    # Generate timestamp for filename
    timestamp = __import__('datetime').datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_file = f"project_structure.txt"
    
    try:
        # Map the project structure
        structure, file_list = map_directory_structure()
        
        # Prepare output content
        output_lines = []
        output_lines.append("🗂️  CODENAMES PROJECT STRUCTURE MAPPER")
        output_lines.append("=" * 50)
        
        # Tree structure
        output_lines.append("\n📊 PROJECT TREE:")
        tree_lines = format_tree(structure)
        output_lines.extend(tree_lines)
        
        # File statistics
        output_lines.append(f"\n📈 PROJECT STATISTICS:")
        output_lines.append(f"Total files tracked: {len(file_list)}")
        
        # Group by extension
        extensions = {}
        for file in file_list:
            ext = file['extension'] or 'no_extension'
            extensions[ext] = extensions.get(ext, 0) + 1
        
        output_lines.append("\nFile types:")
        for ext, count in sorted(extensions.items()):
            output_lines.append(f"  {ext}: {count} files")
        
        # Project analysis
        output_lines.append(f"\n🔍 PROJECT ANALYSIS:")
        analysis = analyze_project_status(file_list)
        
        output_lines.append(f"Backend Status: {analysis['backend_status']}")
        output_lines.append(f"Frontend Status: {analysis['frontend_status']}")
        
        if analysis['phase_indicators']:
            output_lines.append(f"Detected Phases: {', '.join(analysis['phase_indicators'])}")
        
        if analysis['missing_critical']:
            output_lines.append(f"⚠️  Missing Critical Files:")
            for missing in analysis['missing_critical']:
                output_lines.append(f"  - {missing}")
        
        if analysis['config_files']:
            output_lines.append(f"\n📋 Configuration Files Found:")
            for config in analysis['config_files']:
                output_lines.append(f"  - {config}")
        
        # Key directories summary
        output_lines.append(f"\n📁 KEY DIRECTORIES:")
        key_dirs = set()
        for file in file_list:
            parts = Path(file['path']).parts
            if len(parts) > 0:
                key_dirs.add(parts[0])
            if len(parts) > 1:
                key_dirs.add(f"{parts[0]}/{parts[1]}")
        
        for dir_path in sorted(key_dirs):
            dir_files = [f for f in file_list if f['path'].startswith(dir_path)]
            output_lines.append(f"  {dir_path}: {len(dir_files)} files")
        
        # Detailed file list
        output_lines.append(f"\n📋 DETAILED FILE LIST:")
        for file in sorted(file_list, key=lambda x: x['path']):
            size_kb = file['size'] / 1024 if file['size'] > 0 else 0
            output_lines.append(f"  {file['path']} ({size_kb:.1f}KB)")
        
        output_lines.append(f"\n✅ Project structure mapping complete!")
        output_lines.append(f"📅 Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        
        # Display summary to console
        print(f"\n📊 PROJECT SUMMARY:")
        print(f"Total files tracked: {len(file_list)}")
        print(f"Backend Status: {analysis['backend_status']}")
        print(f"Frontend Status: {analysis['frontend_status']}")
        
        if analysis['phase_indicators']:
            print(f"Detected Phases: {', '.join(analysis['phase_indicators'])}")
        
        if analysis['missing_critical']:
            print(f"⚠️  Missing Critical Files: {len(analysis['missing_critical'])}")
        
        print(f"\n✅ Full project structure saved to: {output_file}")
        print(f"📅 Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Error mapping project structure: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()