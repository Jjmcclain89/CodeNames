#!/usr/bin/env python3
"""
Fix database connection issues - verify Docker containers and database credentials
"""

import subprocess
import time
import datetime
import os

def run_command(command, capture_output=True):
    """Run a shell command and return the result"""
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(command, shell=True)
            return result.returncode, "", ""
    except Exception as e:
        return 1, "", str(e)

def check_docker_containers():
    """Check if Docker containers are running properly"""
    print("🔍 Checking Docker containers...")
    
    returncode, stdout, stderr = run_command("docker-compose ps")
    
    if returncode != 0:
        print(f"❌ Error checking containers: {stderr}")
        return False
    
    print("Docker containers status:")
    print(stdout)
    
    # Check if both containers are running
    if "codenames-db" in stdout and "Up" in stdout:
        print("✅ PostgreSQL container is running")
        postgres_running = True
    else:
        print("❌ PostgreSQL container is not running properly")
        postgres_running = False
    
    if "codenames-redis" in stdout and "Up" in stdout:
        print("✅ Redis container is running")
    else:
        print("❌ Redis container is not running properly")
    
    return postgres_running

def check_env_file():
    """Check if the .env file has correct database credentials"""
    print("\n🔍 Checking .env file...")
    
    env_path = "backend/.env"
    
    if not os.path.exists(env_path):
        print("❌ backend/.env file doesn't exist!")
        return False
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("Current .env file contents:")
        print("=" * 50)
        print(content)
        print("=" * 50)
        
        # Check if DATABASE_URL exists and is correct
        correct_database_url = 'DATABASE_URL="postgresql://codenames_user:codenames_password@localhost:5432/codenames_dev"'
        
        if "DATABASE_URL" in content:
            print("✅ DATABASE_URL found in .env file")
            if "codenames_user:codenames_password@localhost:5432/codenames_dev" in content:
                print("✅ Database credentials appear correct")
                return True
            else:
                print("❌ Database credentials in .env don't match expected values")
                return False
        else:
            print("❌ DATABASE_URL not found in .env file")
            return False
            
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

def fix_env_file():
    """Create or fix the .env file with correct database credentials"""
    print("\n🔧 Fixing .env file...")
    
    correct_env_content = '''# Database
DATABASE_URL="postgresql://codenames_user:codenames_password@localhost:5432/codenames_dev"

# JWT
JWT_SECRET="your-super-secret-jwt-key-change-this-in-production"
JWT_EXPIRES_IN="7d"

# Server
PORT=3001
NODE_ENV="development"

# CORS
FRONTEND_URL="http://localhost:5173"

# Redis (for session management if needed)
REDIS_URL="redis://localhost:6379"
'''
    
    try:
        with open("backend/.env", "w", encoding='utf-8') as f:
            f.write(correct_env_content)
        print("✅ Updated backend/.env with correct credentials")
        return True
    except Exception as e:
        print(f"❌ Error writing .env file: {e}")
        return False

def wait_for_postgres():
    """Wait for PostgreSQL to be fully ready"""
    print("\n⏳ Waiting for PostgreSQL to be fully ready...")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        print(f"Attempt {attempt + 1}/{max_attempts}...")
        
        # Try to connect to postgres using docker exec
        returncode, stdout, stderr = run_command(
            'docker exec codenames-db pg_isready -h localhost -p 5432 -U codenames_user'
        )
        
        if returncode == 0:
            print("✅ PostgreSQL is ready!")
            return True
        
        time.sleep(2)
    
    print("❌ PostgreSQL didn't become ready within expected time")
    return False

def restart_containers():
    """Restart Docker containers to ensure clean state"""
    print("\n🔄 Restarting Docker containers...")
    
    # Stop containers
    print("Stopping containers...")
    returncode, stdout, stderr = run_command("docker-compose down")
    if returncode != 0:
        print(f"Warning: Error stopping containers: {stderr}")
    
    # Wait a moment
    time.sleep(3)
    
    # Start containers
    print("Starting containers...")
    returncode, stdout, stderr = run_command("docker-compose up -d")
    if returncode != 0:
        print(f"❌ Error starting containers: {stderr}")
        return False
    
    print("✅ Containers restarted")
    return True

def test_database_connection():
    """Test database connection using Docker exec"""
    print("\n🧪 Testing database connection...")
    
    # Try to connect and list databases
    returncode, stdout, stderr = run_command(
        'docker exec codenames-db psql -h localhost -U codenames_user -d codenames_dev -c "\\l"'
    )
    
    if returncode == 0:
        print("✅ Database connection test successful!")
        print("Available databases:")
        print(stdout)
        return True
    else:
        print(f"❌ Database connection test failed: {stderr}")
        return False

def update_changelog():
    """Update changelog with database fix"""
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
            new_scripts_section = scripts_section + f"- `python/fix_database_connection.py` - Fixed PostgreSQL connection and credentials ({today})\n"
            
            if "\n---\n" in parts[1]:
                rest_of_content = "\n---\n" + parts[1].split("\n---\n", 1)[1]
            elif "\n\n##" in parts[1]:
                rest_of_content = "\n\n##" + parts[1].split("\n\n##", 1)[1]
            else:
                rest_of_content = ""
            
            new_content = parts[0] + "## Python Scripts Run\n" + new_scripts_section + rest_of_content
        else:
            new_content = content + f"\n## Python Scripts Run\n- `python/fix_database_connection.py` - Fixed PostgreSQL connection and credentials ({today})\n"
    else:
        if "\n---\n" in content:
            parts = content.rsplit("\n---\n", 1)
            new_content = parts[0] + f"\n## Python Scripts Run\n- `python/fix_database_connection.py` - Fixed PostgreSQL connection and credentials ({today})\n\n---\n" + parts[1]
        else:
            new_content = content + f"\n## Python Scripts Run\n- `python/fix_database_connection.py` - Fixed PostgreSQL connection and credentials ({today})\n"
    
    with open("CHANGELOG.md", "w", encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Updated CHANGELOG.md")

def main():
    """Main troubleshooting function"""
    print("🔧 Database Connection Troubleshooter\n")
    
    try:
        # Step 1: Check if containers are running
        containers_ok = check_docker_containers()
        
        # Step 2: Check .env file
        env_ok = check_env_file()
        
        # Step 3: Fix .env file if needed
        if not env_ok:
            env_ok = fix_env_file()
        
        # Step 4: Restart containers if needed
        if not containers_ok:
            containers_ok = restart_containers()
        
        # Step 5: Wait for PostgreSQL to be ready
        if containers_ok:
            postgres_ready = wait_for_postgres()
        else:
            postgres_ready = False
        
        # Step 6: Test database connection
        if postgres_ready:
            connection_ok = test_database_connection()
        else:
            connection_ok = False
        
        # Update changelog
        update_changelog()
        
        print("\n" + "="*50)
        print("TROUBLESHOOTING SUMMARY")
        print("="*50)
        print(f"✅ Docker containers: {'OK' if containers_ok else 'FAILED'}")
        print(f"✅ .env file: {'OK' if env_ok else 'FAILED'}")
        print(f"✅ PostgreSQL ready: {'OK' if postgres_ready else 'FAILED'}")
        print(f"✅ Database connection: {'OK' if connection_ok else 'FAILED'}")
        
        if connection_ok:
            print("\n🎉 Database connection fixed! You can now run:")
            print("cd backend")
            print("npm run db:generate")
            print("npm run db:migrate")
        else:
            print("\n❌ Some issues remain. You may need to:")
            print("1. Check Docker Desktop is fully running")
            print("2. Try: docker-compose down && docker-compose up -d")
            print("3. Wait a few minutes for PostgreSQL to fully initialize")
            print("4. Check for port conflicts on 5432")
        
    except Exception as e:
        print(f"❌ Error during troubleshooting: {e}")
        raise

if __name__ == "__main__":
    main()
