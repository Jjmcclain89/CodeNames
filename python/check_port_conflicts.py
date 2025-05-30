#!/usr/bin/env python3
"""
Check for port conflicts and fix Docker port mapping
"""

import subprocess
import socket
import datetime

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def check_port_usage():
    """Check what's using ports 5432 and 6379"""
    print("🔍 Checking port usage...")
    
    ports_to_check = [5432, 6379]
    
    for port in ports_to_check:
        print(f"\n--- Port {port} ---")
        
        # Try to connect to see if port is in use
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"✅ Port {port} is in use (something is listening)")
            
            # Check what's using it (Windows)
            returncode, stdout, stderr = run_command(f"netstat -ano | findstr :{port}")
            if returncode == 0 and stdout:
                print("Process details:")
                print(stdout.strip())
                
                # Try to get process name
                lines = stdout.strip().split('\n')
                for line in lines:
                    if f":{port}" in line and "LISTENING" in line:
                        parts = line.split()
                        if len(parts) > 4:
                            pid = parts[-1]
                            returncode2, stdout2, stderr2 = run_command(f"tasklist /FI \"PID eq {pid}\"")
                            if returncode2 == 0:
                                print(f"Process name: {stdout2}")
            else:
                print("Could not identify the process using this port")
        else:
            print(f"❌ Port {port} is not in use")

def check_docker_port_mapping():
    """Check Docker container port mappings"""
    print("\n🐳 Checking Docker container port mappings...")
    
    returncode, stdout, stderr = run_command("docker ps --format \"table {{.Names}}\\t{{.Ports}}\"")
    
    if returncode == 0:
        print("Current Docker containers and their ports:")
        print(stdout)
    else:
        print(f"Error checking Docker containers: {stderr}")

def fix_docker_compose_ports():
    """Create alternative docker-compose with different ports"""
    print("\n🔧 Creating alternative docker-compose configuration...")
    
    # Alternative docker-compose with different ports
    docker_compose_alt = """services:
  postgres:
    image: postgres:15-alpine
    container_name: codenames-db
    environment:
      POSTGRES_DB: codenames_dev
      POSTGRES_USER: codenames_user
      POSTGRES_PASSWORD: codenames_password
    ports:
      - "5433:5432"  # Changed from 5432 to 5433
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - codenames-network

  redis:
    image: redis:7-alpine
    container_name: codenames-redis
    ports:
      - "6380:6379"  # Changed from 6379 to 6380
    networks:
      - codenames-network

volumes:
  postgres_data:

networks:
  codenames-network:
    driver: bridge
"""
    
    # Write alternative compose file
    with open("docker-compose.alt.yml", "w", encoding='utf-8') as f:
        f.write(docker_compose_alt)
    
    print("✅ Created docker-compose.alt.yml with ports 5433 and 6380")
    
    # Create alternative .env file
    alt_env = """# Database
DATABASE_URL=postgresql://codenames_user:codenames_password@localhost:5433/codenames_dev

# JWT
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_EXPIRES_IN=7d

# Server
PORT=3001
NODE_ENV=development

# CORS
FRONTEND_URL=http://localhost:5173

# Redis (for session management if needed)
REDIS_URL=redis://localhost:6380
"""
    
    with open("backend/.env.alt", "w", encoding='utf-8') as f:
        f.write(alt_env)
    
    print("✅ Created backend/.env.alt with alternative ports")

def restart_with_alternative_ports():
    """Restart Docker containers with alternative ports"""
    print("\n🔄 Restarting with alternative ports...")
    
    # Stop current containers
    print("Stopping current containers...")
    run_command("docker-compose down")
    
    # Start with alternative configuration
    print("Starting with alternative ports...")
    returncode, stdout, stderr = run_command("docker-compose -f docker-compose.alt.yml up -d")
    
    if returncode == 0:
        print("✅ Containers started with alternative ports!")
        print("📝 Don't forget to copy .env.alt to .env:")
        print("   copy backend\\.env.alt backend\\.env")
        return True
    else:
        print(f"❌ Error starting containers: {stderr}")
        return False

def find_postgres_services():
    """Find any existing PostgreSQL services"""
    print("\n🔍 Checking for existing PostgreSQL services...")
    
    # Check Windows services
    returncode, stdout, stderr = run_command("sc query | findstr -i postgres")
    if returncode == 0 and stdout:
        print("Found PostgreSQL Windows services:")
        print(stdout)
    else:
        print("No PostgreSQL Windows services found")
    
    # Check for common PostgreSQL installations
    common_postgres_ports = [5432, 5433, 5434]
    for port in common_postgres_ports:
        returncode, stdout, stderr = run_command(f"netstat -an | findstr :{port}")
        if returncode == 0 and stdout:
            print(f"Something is listening on PostgreSQL port {port}:")
            print(stdout.strip())

def update_changelog():
    """Update changelog"""
    today = datetime.date.today().isoformat()
    
    try:
        with open("CHANGELOG.md", "r", encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        content = ""
    
    if "## Python Scripts Run" in content:
        parts = content.split("## Python Scripts Run")
        if len(parts) >= 2:
            scripts_section = parts[1].split("\n---\n")[0] if "\n---\n" in parts[1] else parts[1].split("\n\n##")[0] if "\n\n##" in parts[1] else parts[1]
            new_scripts_section = scripts_section + f"- `python/check_port_conflicts.py` - Checked for port conflicts and created alternative configuration ({today})\n"
            
            if "\n---\n" in parts[1]:
                rest_of_content = "\n---\n" + parts[1].split("\n---\n", 1)[1]
            elif "\n\n##" in parts[1]:
                rest_of_content = "\n\n##" + parts[1].split("\n\n##", 1)[1]
            else:
                rest_of_content = ""
            
            new_content = parts[0] + "## Python Scripts Run\n" + new_scripts_section + rest_of_content
        else:
            new_content = content + f"\n## Python Scripts Run\n- `python/check_port_conflicts.py` - Checked for port conflicts and created alternative configuration ({today})\n"
    else:
        if "\n---\n" in content:
            parts = content.rsplit("\n---\n", 1)
            new_content = parts[0] + f"\n## Python Scripts Run\n- `python/check_port_conflicts.py` - Checked for port conflicts and created alternative configuration ({today})\n\n---\n" + parts[1]
        else:
            new_content = content + f"\n## Python Scripts Run\n- `python/check_port_conflicts.py` - Checked for port conflicts and created alternative configuration ({today})\n"
    
    with open("CHANGELOG.md", "w", encoding='utf-8') as f:
        f.write(new_content)

def main():
    """Main function to check and fix port conflicts"""
    print("🔍 Port Conflict Checker and Fixer\n")
    
    try:
        # Step 1: Check current port usage
        check_port_usage()
        
        # Step 2: Check Docker port mappings
        check_docker_port_mapping()
        
        # Step 3: Look for existing PostgreSQL services
        find_postgres_services()
        
        # Step 4: Create alternative configuration
        fix_docker_compose_ports()
        
        print("\n" + "="*60)
        print("PORT CONFLICT RESOLUTION OPTIONS")
        print("="*60)
        print("\n🎯 OPTION 1: Use alternative ports (RECOMMENDED)")
        print("   1. Run: docker-compose down")
        print("   2. Run: docker-compose -f docker-compose.alt.yml up -d")
        print("   3. Run: copy backend\\.env.alt backend\\.env")
        print("   4. Continue with your Prisma setup")
        
        print("\n🎯 OPTION 2: Stop conflicting service")
        print("   If you have PostgreSQL installed locally:")
        print("   1. Stop the PostgreSQL Windows service")
        print("   2. Run: docker-compose up -d")
        print("   3. Continue with original setup")
        
        print("\n🎯 OPTION 3: Automatic switch to alternative")
        print("   Type 'yes' to automatically switch to alternative ports")
        
        choice = input("\nSwitch to alternative ports automatically? (yes/no): ").lower().strip()
        
        if choice in ['yes', 'y']:
            success = restart_with_alternative_ports()
            if success:
                print("\n✅ Switched to alternative ports successfully!")
                print("Now copy the alternative .env file:")
                print("copy backend\\.env.alt backend\\.env")
        
        update_changelog()
        
    except Exception as e:
        print(f"❌ Error during port conflict check: {e}")
        raise

if __name__ == "__main__":
    main()
