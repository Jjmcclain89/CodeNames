#!/usr/bin/env python3
"""
Fix Prisma-specific connection issues
"""

import subprocess
import os
import datetime
import shutil

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def clear_prisma_cache():
    """Clear Prisma cache and generated files"""
    print("🧹 Clearing Prisma cache...")
    
    # Paths to clear
    paths_to_clear = [
        "backend/node_modules/.prisma",
        "backend/prisma/migrations",
        os.path.expanduser("~/.cache/prisma")
    ]
    
    for path in paths_to_clear:
        if os.path.exists(path):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                print(f"✅ Cleared: {path}")
            except Exception as e:
                print(f"⚠️  Could not clear {path}: {e}")
        else:
            print(f"📁 Path not found (OK): {path}")

def test_env_loading():
    """Test if Prisma can load environment variables"""
    print("\n🔍 Testing Prisma environment variable loading...")
    
    # Try to run prisma db pull to test connection without making changes
    returncode, stdout, stderr = run_command("npx prisma db pull --preview-feature", cwd="backend")
    
    print(f"Return code: {returncode}")
    print(f"Stdout: {stdout}")
    print(f"Stderr: {stderr}")
    
    if returncode == 0:
        print("✅ Prisma can connect to database!")
        return True
    else:
        print("❌ Prisma still cannot connect")
        return False

def recreate_env_file():
    """Recreate the .env file with explicit formatting"""
    print("\n🔧 Recreating .env file with explicit formatting...")
    
    # Make sure we're in the right directory structure
    backend_dir = "backend"
    if not os.path.exists(backend_dir):
        print("❌ Backend directory not found!")
        return False
    
    env_content = """# Database
DATABASE_URL=postgresql://codenames_user:codenames_password@localhost:5432/codenames_dev

# JWT
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_EXPIRES_IN=7d

# Server
PORT=3001
NODE_ENV=development

# CORS
FRONTEND_URL=http://localhost:5173

# Redis (for session management if needed)
REDIS_URL=redis://localhost:6379
"""
    
    try:
        with open(f"{backend_dir}/.env", "w", encoding='utf-8', newline='\n') as f:
            f.write(env_content)
        print("✅ Recreated .env file without quotes")
        return True
    except Exception as e:
        print(f"❌ Error recreating .env file: {e}")
        return False

def verify_prisma_schema():
    """Verify Prisma schema is valid"""
    print("\n🔍 Verifying Prisma schema...")
    
    returncode, stdout, stderr = run_command("npx prisma validate", cwd="backend")
    
    if returncode == 0:
        print("✅ Prisma schema is valid")
        return True
    else:
        print(f"❌ Prisma schema validation failed: {stderr}")
        return False

def reset_database():
    """Reset the database to clean state"""
    print("\n🔄 Resetting database to clean state...")
    
    # Try to reset database
    returncode, stdout, stderr = run_command("npx prisma db push --force-reset", cwd="backend")
    
    if returncode == 0:
        print("✅ Database reset successful")
        return True
    else:
        print(f"❌ Database reset failed: {stderr}")
        return False

def try_alternative_connection():
    """Try connecting with an alternative connection string format"""
    print("\n🔧 Trying alternative connection string...")
    
    # Backup current .env
    try:
        shutil.copy("backend/.env", "backend/.env.backup")
        print("✅ Backed up current .env file")
    except Exception as e:
        print(f"⚠️  Could not backup .env: {e}")
    
    # Try different connection string formats
    alternative_formats = [
        "postgresql://codenames_user:codenames_password@127.0.0.1:5432/codenames_dev",
        "postgres://codenames_user:codenames_password@localhost:5432/codenames_dev",
        "postgresql://codenames_user:codenames_password@host.docker.internal:5432/codenames_dev"
    ]
    
    for i, connection_string in enumerate(alternative_formats):
        print(f"\n🧪 Testing format {i+1}: {connection_string}")
        
        env_content = f"""# Database
DATABASE_URL={connection_string}

# JWT
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_EXPIRES_IN=7d

# Server
PORT=3001
NODE_ENV=development

# CORS
FRONTEND_URL=http://localhost:5173

# Redis (for session management if needed)
REDIS_URL=redis://localhost:6379
"""
        
        try:
            with open("backend/.env", "w", encoding='utf-8', newline='\n') as f:
                f.write(env_content)
            
            # Test connection
            returncode, stdout, stderr = run_command("npx prisma db pull --preview-feature", cwd="backend")
            
            if returncode == 0:
                print(f"✅ Success with connection format {i+1}!")
                return True
            else:
                print(f"❌ Failed with format {i+1}: {stderr}")
                
        except Exception as e:
            print(f"❌ Error testing format {i+1}: {e}")
    
    # Restore backup if all failed
    try:
        shutil.copy("backend/.env.backup", "backend/.env")
        print("📁 Restored original .env file")
    except Exception as e:
        print(f"⚠️  Could not restore .env backup: {e}")
    
    return False

def install_prisma_fresh():
    """Reinstall Prisma client fresh"""
    print("\n🔄 Reinstalling Prisma client...")
    
    # Remove node_modules/.prisma
    prisma_cache = "backend/node_modules/.prisma"
    if os.path.exists(prisma_cache):
        try:
            shutil.rmtree(prisma_cache)
            print("✅ Removed Prisma cache")
        except Exception as e:
            print(f"⚠️  Could not remove Prisma cache: {e}")
    
    # Reinstall Prisma
    returncode, stdout, stderr = run_command("npm install prisma @prisma/client", cwd="backend")
    
    if returncode == 0:
        print("✅ Prisma reinstalled successfully")
        return True
    else:
        print(f"❌ Prisma reinstall failed: {stderr}")
        return False

def update_changelog():
    """Update changelog"""
    today = datetime.date.today().isoformat()
    
    try:
        with open("CHANGELOG.md", "r", encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        content = ""
    
    # Add to Python Scripts Run section
    if "## Python Scripts Run" in content:
        parts = content.split("## Python Scripts Run")
        if len(parts) >= 2:
            scripts_section = parts[1].split("\n---\n")[0] if "\n---\n" in parts[1] else parts[1].split("\n\n##")[0] if "\n\n##" in parts[1] else parts[1]
            new_scripts_section = scripts_section + f"- `python/fix_prisma_connection.py` - Fixed Prisma database connection issues ({today})\n"
            
            if "\n---\n" in parts[1]:
                rest_of_content = "\n---\n" + parts[1].split("\n---\n", 1)[1]
            elif "\n\n##" in parts[1]:
                rest_of_content = "\n\n##" + parts[1].split("\n\n##", 1)[1]
            else:
                rest_of_content = ""
            
            new_content = parts[0] + "## Python Scripts Run\n" + new_scripts_section + rest_of_content
        else:
            new_content = content + f"\n## Python Scripts Run\n- `python/fix_prisma_connection.py` - Fixed Prisma database connection issues ({today})\n"
    else:
        if "\n---\n" in content:
            parts = content.rsplit("\n---\n", 1)
            new_content = parts[0] + f"\n## Python Scripts Run\n- `python/fix_prisma_connection.py` - Fixed Prisma database connection issues ({today})\n\n---\n" + parts[1]
        else:
            new_content = content + f"\n## Python Scripts Run\n- `python/fix_prisma_connection.py` - Fixed Prisma database connection issues ({today})\n"
    
    with open("CHANGELOG.md", "w", encoding='utf-8') as f:
        f.write(new_content)

def main():
    """Main function to fix Prisma connection issues"""
    print("🔧 Prisma Connection Fixer\n")
    
    try:
        # Step 1: Clear Prisma cache
        clear_prisma_cache()
        
        # Step 2: Verify schema
        schema_ok = verify_prisma_schema()
        
        # Step 3: Try recreating .env without quotes
        env_recreated = recreate_env_file()
        
        # Step 4: Test if this fixes the connection
        if env_recreated:
            connection_ok = test_env_loading()
        else:
            connection_ok = False
        
        # Step 5: If still failing, try alternative connection strings
        if not connection_ok:
            print("\n🔄 Standard connection failed, trying alternatives...")
            connection_ok = try_alternative_connection()
        
        # Step 6: If still failing, try fresh Prisma install
        if not connection_ok:
            print("\n🔄 Alternative connections failed, reinstalling Prisma...")
            install_ok = install_prisma_fresh()
            if install_ok:
                connection_ok = test_env_loading()
        
        # Update changelog
        update_changelog()
        
        print("\n" + "="*50)
        print("PRISMA CONNECTION FIX SUMMARY")
        print("="*50)
        print(f"✅ Schema validation: {'OK' if schema_ok else 'FAILED'}")
        print(f"✅ Environment file: {'OK' if env_recreated else 'FAILED'}")
        print(f"✅ Prisma connection: {'OK' if connection_ok else 'FAILED'}")
        
        if connection_ok:
            print("\n🎉 Prisma connection fixed! You can now run:")
            print("cd backend")
            print("npm run db:generate")
            print("npm run db:migrate")
        else:
            print("\n❌ Prisma connection still failing. Additional steps to try:")
            print("1. Restart Docker containers: docker-compose down && docker-compose up -d")
            print("2. Check if Windows Defender/Antivirus is blocking connections")
            print("3. Try running commands directly: cd backend && npx prisma db push")
            print("4. Check if another service is using port 5432")
        
    except Exception as e:
        print(f"❌ Error during Prisma fix: {e}")
        raise

if __name__ == "__main__":
    main()
