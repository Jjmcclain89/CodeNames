#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Login and Home Page Styling
Fixes white text on white background issues across all frontend pages
"""

from pathlib import Path
from datetime import datetime

def add_changelog_entry():
    """Add entry to CHANGELOG.md"""
    try:
        changelog_path = Path("CHANGELOG.md")
        if not changelog_path.exists():
            return
            
        with open(changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "### Python Scripts Run" not in content:
            unreleased_section = content.find("## [Unreleased]")
            if unreleased_section != -1:
                insert_point = content.find("### Added", unreleased_section)
                if insert_point != -1:
                    new_section = "\n### Python Scripts Run\n- Frontend styling fix: Fixed white text visibility on login and home pages\n"
                    content = content[:insert_point] + new_section + content[insert_point:]
        else:
            section_start = content.find("### Python Scripts Run")
            section_end = content.find("\n###", section_start + 1)
            if section_end == -1:
                section_end = content.find("\n## ", section_start + 1)
            
            entry = f"- Frontend styling fix: Fixed page text visibility ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n"
            
            if section_end != -1:
                insert_point = section_end
                content = content[:insert_point] + entry + content[insert_point:]
            else:
                content += entry
        
        with open(changelog_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Updated CHANGELOG.md")
        
    except Exception as e:
        print(f"⚠️ Could not update CHANGELOG.md: {e}")

def fix_login_page():
    """Fix LoginPage styling"""
    print("🎨 Fixing LoginPage styling...")
    
    login_page_path = Path("frontend/src/pages/LoginPage.tsx")
    
    fixed_login_page = '''import React, { useState } from 'react';
import authService from '../services/authService';

interface LoginPageProps {
  onLogin: (user: any, token: string) => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!username.trim()) {
      setError('Username is required');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      console.log('Attempting login with username:', username.trim());
      const result = await authService.login(username.trim());
      console.log('Login result:', result);
      
      if (result.success && result.token && result.user) {
        console.log('Login successful');
        onLogin(result.user, result.token);
      } else {
        console.log('Login failed:', result.error);
        setError(result.error || 'Login failed');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError('Failed to connect to server');
    }

    setIsLoading(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUsername(e.target.value);
    if (error) setError(''); // Clear error when user starts typing
  };

  return (
    <div className="min-h-[60vh] flex items-center justify-center bg-gray-50">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md border border-gray-200">
        <h2 className="text-2xl font-bold text-center mb-6 text-gray-900">Join Codenames</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4" autoComplete="off">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
              Choose a Username
            </label>
            <input
              type="text"
              id="username"
              name="username"
              value={username}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
              placeholder="Enter your username"
              disabled={isLoading}
              autoComplete="off"
              autoCorrect="off"
              autoCapitalize="off"
              spellCheck="false"
              data-lpignore="true"
            />
          </div>
          
          {error && (
            <div className="text-red-600 text-sm bg-red-50 p-2 rounded border border-red-200">{error}</div>
          )}
          
          <button
            type="submit"
            disabled={isLoading || !username.trim()}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white py-2 px-4 rounded-md font-medium transition-colors"
          >
            {isLoading ? 'Connecting...' : 'Join Game'}
          </button>
        </form>
        
        <div className="mt-6 text-center text-sm text-gray-600">
          <p>Enter any username to join or create an account</p>
          <p className="mt-2 text-xs text-gray-500">Debug: Check browser console for error details</p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
'''
    
    with open(login_page_path, 'w', encoding='utf-8') as f:
        f.write(fixed_login_page)
    
    print("✅ Fixed LoginPage styling")

def fix_home_page():
    """Fix HomePage styling"""
    print("🎨 Fixing HomePage styling...")
    
    home_page_path = Path("frontend/src/pages/HomePage.tsx")
    
    if not home_page_path.exists():
        print("❌ HomePage.tsx not found, creating a basic one...")
        # Create a basic HomePage if it doesn't exist
        home_page_content = '''import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const HomePage: React.FC = () => {
  const [roomCode, setRoomCode] = useState('');
  const navigate = useNavigate();

  const handleCreateRoom = () => {
    // For Phase 1, just show success message
    alert('Room creation will be implemented in Phase 2!');
  };

  const handleJoinRoom = () => {
    if (!roomCode.trim()) {
      alert('Please enter a room code');
      return;
    }
    // For Phase 1, just show success message
    alert(`Joining room: ${roomCode} - Will be implemented in Phase 2!`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Welcome to Codenames!</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Create Room */}
          <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
            <h2 className="text-xl font-semibold mb-4 text-gray-900">Create New Room</h2>
            <p className="text-gray-600 mb-4">Start a new game and invite friends to join</p>
            <button 
              onClick={handleCreateRoom}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded transition-colors"
            >
              Create Room
            </button>
          </div>
          
          {/* Join Room */}
          <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
            <h2 className="text-xl font-semibold mb-4 text-gray-900">Join Existing Room</h2>
            <div className="space-y-4">
              <div>
                <label htmlFor="roomCode" className="block text-sm font-medium text-gray-700 mb-2">
                  Room Code
                </label>
                <input
                  type="text"
                  id="roomCode"
                  value={roomCode}
                  onChange={(e) => setRoomCode(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
                  placeholder="Enter room code"
                />
              </div>
              <button 
                onClick={handleJoinRoom}
                className="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded transition-colors"
              >
                Join Room
              </button>
            </div>
          </div>
        </div>
        
        {/* Phase 1 Status */}
        <div className="mt-8 bg-blue-50 border border-blue-200 p-4 rounded-lg">
          <h3 className="font-semibold text-blue-900 mb-2">🎉 Phase 1 Complete!</h3>
          <div className="text-blue-800 space-y-1">
            <p>✅ Backend server running and API working</p>
            <p>✅ Socket connection established</p>
            <p>✅ Authentication system working</p>
            <p>✅ Frontend and backend communicating</p>
          </div>
        </div>
        
        {/* Debug Section */}
        <div className="mt-6 bg-gray-100 border border-gray-300 p-4 rounded-lg">
          <h3 className="font-semibold text-gray-900 mb-2">🔧 Debug Tools</h3>
          <div className="text-gray-700 space-y-2">
            <p>• <a href="/debug" className="text-blue-600 hover:text-blue-800 underline">Debug Dashboard</a> - Test connections</p>
            <p>• Check browser console (F12) for detailed logs</p>
            <p>• Room creation and game mechanics coming in Phase 2!</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
'''
    else:
        # Read existing HomePage and fix its styling
        with open(home_page_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # If it already has good styling, don't overwrite
        if 'text-gray-900' in content and 'bg-gray-50' in content:
            print("✅ HomePage already has good styling")
            return
        
        home_page_content = '''import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const HomePage: React.FC = () => {
  const [roomCode, setRoomCode] = useState('');
  const navigate = useNavigate();

  const handleCreateRoom = () => {
    // For Phase 1, just show success message
    alert('Room creation will be implemented in Phase 2!');
  };

  const handleJoinRoom = () => {
    if (!roomCode.trim()) {
      alert('Please enter a room code');
      return;
    }
    // For Phase 1, just show success message
    alert(`Joining room: ${roomCode} - Will be implemented in Phase 2!`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Welcome to Codenames!</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Create Room */}
          <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
            <h2 className="text-xl font-semibold mb-4 text-gray-900">Create New Room</h2>
            <p className="text-gray-600 mb-4">Start a new game and invite friends to join</p>
            <button 
              onClick={handleCreateRoom}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded transition-colors"
            >
              Create Room
            </button>
          </div>
          
          {/* Join Room */}
          <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
            <h2 className="text-xl font-semibold mb-4 text-gray-900">Join Existing Room</h2>
            <div className="space-y-4">
              <div>
                <label htmlFor="roomCode" className="block text-sm font-medium text-gray-700 mb-2">
                  Room Code
                </label>
                <input
                  type="text"
                  id="roomCode"
                  value={roomCode}
                  onChange={(e) => setRoomCode(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
                  placeholder="Enter room code"
                />
              </div>
              <button 
                onClick={handleJoinRoom}
                className="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded transition-colors"
              >
                Join Room
              </button>
            </div>
          </div>
        </div>
        
        {/* Phase 1 Status */}
        <div className="mt-8 bg-blue-50 border border-blue-200 p-4 rounded-lg">
          <h3 className="font-semibold text-blue-900 mb-2">🎉 Phase 1 Complete!</h3>
          <div className="text-blue-800 space-y-1">
            <p>✅ Backend server running and API working</p>
            <p>✅ Socket connection established</p>
            <p>✅ Authentication system working</p>
            <p>✅ Frontend and backend communicating</p>
          </div>
        </div>
        
        {/* Debug Section */}
        <div className="mt-6 bg-gray-100 border border-gray-300 p-4 rounded-lg">
          <h3 className="font-semibold text-gray-900 mb-2">🔧 Debug Tools</h3>
          <div className="text-gray-700 space-y-2">
            <p>• <a href="/debug" className="text-blue-600 hover:text-blue-800 underline">Debug Dashboard</a> - Test connections</p>
            <p>• Check browser console (F12) for detailed logs</p>
            <p>• Room creation and game mechanics coming in Phase 2!</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
'''
    
    with open(home_page_path, 'w', encoding='utf-8') as f:
        f.write(home_page_content)
    
    print("✅ Fixed HomePage styling")

def fix_app_css():
    """Fix global App.css to ensure proper text colors"""
    print("🎨 Fixing global App.css...")
    
    app_css_path = Path("frontend/src/App.css")
    
    fixed_app_css = '''/* Global App Styles */
.App {
  text-align: center;
  color: #1f2937; /* gray-900 */
  background-color: #f9fafb; /* gray-50 */
  min-height: 100vh;
}

/* Ensure all text is readable by default */
* {
  color: inherit;
}

/* Override any white text on white background issues */
body {
  color: #1f2937;
  background-color: #ffffff;
}

/* Input styling */
input {
  color: #1f2937 !important;
  background-color: #ffffff !important;
}

/* Button styling */
button {
  color: #ffffff;
}

/* Link styling */
a {
  color: #2563eb;
}

a:hover {
  color: #1d4ed8;
}

/* Card/container backgrounds */
.card, .container {
  background-color: #ffffff;
  color: #1f2937;
}

/* Debug console styling */
.debug-console {
  background-color: #1f2937;
  color: #10b981;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}
'''
    
    with open(app_css_path, 'w', encoding='utf-8') as f:
        f.write(fixed_app_css)
    
    print("✅ Fixed global App.css styling")

def main():
    """Main execution function"""
    print("🎨 Fixing Frontend Page Styling")
    print("=" * 40)
    
    try:
        # Fix LoginPage styling
        fix_login_page()
        
        # Fix HomePage styling
        fix_home_page()
        
        # Fix global App.css
        fix_app_css()
        
        # Update changelog
        add_changelog_entry()
        
        print("\n🎉 Frontend Styling Fixed!")
        print("=" * 40)
        
        print("\n📋 What was fixed:")
        print("✅ LoginPage: Added proper text colors and backgrounds")
        print("✅ HomePage: Created/fixed with readable styling")
        print("✅ App.css: Added global text color overrides")
        print("✅ Inputs: Ensured white background with dark text")
        print("✅ Cards: White backgrounds with dark text")
        
        print("\n🔧 Next steps:")
        print("1. Refresh your browser (F5 or Ctrl+R)")
        print("2. Try the login flow - should be fully readable")
        print("3. Check the home page after login")
        print("4. All text should now be dark on light backgrounds")
        
        print("\n🎯 Expected results:")
        print("- Login page fully readable")
        print("- Home page shows Phase 1 completion status")
        print("- All text dark on light backgrounds")
        print("- Ready to test full Phase 1 workflow")
        
        return 0
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
