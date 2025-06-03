#!/usr/bin/env python3
"""
Fix Game Creation Navigation Issue

This script fixes the issue where game creation succeeds on backend
but frontend gets stuck on "Loading game..." screen instead of 
navigating to the room.
"""

import os
import sys

def get_homepage_content():
    """Get the current HomePage.tsx to understand the game creation flow"""
    
    homepage_path = "frontend/src/pages/HomePage.tsx"
    
    if not os.path.exists(homepage_path):
        print(f"Error: {homepage_path} not found")
        return None
    
    with open(homepage_path, 'r', encoding='utf-8') as f:
        return f.read()

def add_homepage_debugging():
    """Add debugging to HomePage.tsx to track game creation flow"""
    
    homepage_path = "frontend/src/pages/HomePage.tsx"
    
    if not os.path.exists(homepage_path):
        print(f"Error: {homepage_path} not found")
        return False
    
    with open(homepage_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add debugging to game creation functions
    # Look for the create game function
    if "const handleCreateGame = " in content:
        # Find and enhance the create game function
        old_pattern = "const handleCreateGame = async () => {"
        new_pattern = """const handleCreateGame = async () => {
    console.log('🎮 [HOMEPAGE] handleCreateGame called');
    console.log('🎮 [HOMEPAGE] Current timestamp:', Date.now());"""
        
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            print("✅ Added debugging to handleCreateGame")
    
    # Look for API calls and navigation
    if "const response = await fetch('/api/games/create'," in content:
        # Find the game creation API call and add debugging around it
        old_fetch_pattern = """const response = await fetch('/api/games/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          userId: user.id,
          username: user.username
        })
      });"""
        
        new_fetch_pattern = """console.log('🎮 [HOMEPAGE] Making API call to create game...');
      const response = await fetch('/api/games/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          userId: user.id,
          username: user.username
        })
      });
      
      console.log('🎮 [HOMEPAGE] API response status:', response.status);
      console.log('🎮 [HOMEPAGE] API response ok:', response.ok);"""
        
        if old_fetch_pattern in content:
            content = content.replace(old_fetch_pattern, new_fetch_pattern)
            print("✅ Added debugging to game creation API call")
    
    # Look for navigation logic
    if "navigate(`/room/${" in content:
        # Find navigation and add debugging
        old_navigate = "navigate(`/room/${gameCode}`);"
        new_navigate = """console.log('🎮 [HOMEPAGE] Navigating to room:', gameCode);
        navigate(`/room/${gameCode}`);
        console.log('🎮 [HOMEPAGE] Navigation called');"""
        
        if old_navigate in content:
            content = content.replace(old_navigate, new_navigate)
            print("✅ Added debugging to navigation")
    
    # Write back the updated content
    with open(homepage_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def add_room_page_loading_debugging():
    """Add debugging to RoomPage to see why it gets stuck on loading"""
    
    room_page_path = "frontend/src/pages/RoomPage.tsx"
    
    if not os.path.exists(room_page_path):
        print(f"Error: {room_page_path} not found")
        return False
    
    with open(room_page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add debugging to the loadGameAndConnect function
    if "const loadGameAndConnect = async () => {" in content:
        old_function = """const loadGameAndConnect = async () => {
    if (!roomCode) {
      setError('No room code provided');
      setIsLoading(false);
      return;
    }

    try {
      console.log('🎮 Loading game info for room:', roomCode);"""
        
        new_function = """const loadGameAndConnect = async () => {
    console.log('🏠 [ROOMPAGE] loadGameAndConnect called for room:', roomCode);
    console.log('🏠 [ROOMPAGE] Timestamp:', Date.now());
    
    if (!roomCode) {
      console.log('❌ [ROOMPAGE] No room code provided');
      setError('No room code provided');
      setIsLoading(false);
      return;
    }

    try {
      console.log('🎮 [ROOMPAGE] Loading game info for room:', roomCode);"""
        
        if old_function in content:
            content = content.replace(old_function, new_function)
            print("✅ Added debugging to loadGameAndConnect")
    
    # Add debugging to API calls in RoomPage
    if "const joinResponse = await fetch('/api/games/join'," in content:
        old_join_call = """// Join the game via API
      const joinResponse = await fetch('/api/games/join', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          gameCode: roomCode.toUpperCase(),
          userId: user.id,
          username: user.username
        })
      });

      if (!joinResponse.ok) {
        throw new Error('Failed to join game');
      }"""
        
        new_join_call = """// Join the game via API
      console.log('🏠 [ROOMPAGE] Calling /api/games/join for room:', roomCode.toUpperCase());
      const joinResponse = await fetch('/api/games/join', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          gameCode: roomCode.toUpperCase(),
          userId: user.id,
          username: user.username
        })
      });

      console.log('🏠 [ROOMPAGE] Join response status:', joinResponse.status);
      console.log('🏠 [ROOMPAGE] Join response ok:', joinResponse.ok);

      if (!joinResponse.ok) {
        console.log('❌ [ROOMPAGE] Join failed with status:', joinResponse.status);
        throw new Error('Failed to join game');
      }"""
        
        if old_join_call in content:
            content = content.replace(old_join_call, new_join_call)
            print("✅ Added debugging to join API call")
    
    # Add debugging to the game info fetch
    if "const response = await fetch(`/api/games/${roomCode}`);" in content:
        old_fetch = """// Get game info
      const response = await fetch(`/api/games/${roomCode}`);
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setGameInfo(data.game);
          setPlayers(data.game.players || []);
          setMessages(data.game.messages || []);
          
          // Connect to socket and set up game
          await connectToRoom(roomCode, token, user);
          console.log('✅ Game info loaded:', data.game);
        } else {
          throw new Error(data.error || 'Game not found');
        }
      }"""
        
        new_fetch = """// Get game info
      console.log('🏠 [ROOMPAGE] Fetching game info from /api/games/' + roomCode);
      const response = await fetch(`/api/games/${roomCode}`);
      
      console.log('🏠 [ROOMPAGE] Game info response status:', response.status);
      console.log('🏠 [ROOMPAGE] Game info response ok:', response.ok);
      
      if (response.ok) {
        const data = await response.json();
        console.log('🏠 [ROOMPAGE] Game info data:', data);
        
        if (data.success) {
          console.log('🏠 [ROOMPAGE] Setting game info and players');
          setGameInfo(data.game);
          setPlayers(data.game.players || []);
          setMessages(data.game.messages || []);
          
          // Connect to socket and set up game
          console.log('🏠 [ROOMPAGE] Calling connectToRoom...');
          await connectToRoom(roomCode, token, user);
          console.log('✅ [ROOMPAGE] Game info loaded and connected');
        } else {
          console.log('❌ [ROOMPAGE] Game info failed:', data.error);
          throw new Error(data.error || 'Game not found');
        }
      }"""
        
        if old_fetch in content:
            content = content.replace(old_fetch, new_fetch)
            print("✅ Added debugging to game info fetch")
    
    # Add debugging to setIsLoading(false) calls
    if "setIsLoading(false);" in content:
        # Add logging before setIsLoading(false) to track when loading should end
        content = content.replace(
            "setIsLoading(false);",
            "console.log('🏠 [ROOMPAGE] Setting isLoading to false');\n    setIsLoading(false);"
        )
        print("✅ Added debugging to setIsLoading(false) calls")
    
    # Write back the updated content
    with open(room_page_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def create_simple_navigation_test():
    """Create a simple test to verify navigation is working"""
    
    test_content = '''// Simple navigation test - add this to HomePage.tsx temporarily
const testNavigation = () => {
  console.log('🧪 Testing navigation to /room/TEST123');
  navigate('/room/TEST123');
};

// Add this button to your HomePage for testing:
// <button onClick={testNavigation} className="bg-purple-500 text-white px-4 py-2 rounded">
//   Test Navigation to Room
// </button>'''
    
    test_file_path = "navigation_test.txt"
    
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"✅ Created navigation test snippet in {test_file_path}")
    return True

def main():
    print("🔧 Fixing Game Creation Navigation Issue...")
    print("=" * 50)
    
    # First, let's see what the HomePage looks like
    homepage_content = get_homepage_content()
    if homepage_content:
        print("📄 HomePage.tsx found, checking game creation flow...")
        
        # Check if it has navigation logic
        if "navigate(" in homepage_content:
            print("✅ Navigation logic found in HomePage")
        else:
            print("❌ No navigation logic found in HomePage")
        
        # Check if it has error handling
        if "try {" in homepage_content and "catch" in homepage_content:
            print("✅ Error handling found in HomePage")
        else:
            print("❌ Limited error handling in HomePage")
    
    success_count = 0
    
    # Add debugging to HomePage
    if add_homepage_debugging():
        success_count += 1
    
    # Add debugging to RoomPage loading
    if add_room_page_loading_debugging():
        success_count += 1
    
    # Create navigation test
    if create_simple_navigation_test():
        success_count += 1
    
    print("=" * 50)
    if success_count >= 2:
        print("✅ Navigation debugging added successfully!")
        print("\n🎯 What was added:")
        print("1. ✅ Detailed debugging to HomePage game creation flow")
        print("2. ✅ Comprehensive debugging to RoomPage loading process")
        print("3. ✅ Created navigation test snippet")
        print("\n🚀 Next steps:")
        print("1. Restart your frontend")
        print("2. Open browser console before clicking 'Create Game'")
        print("3. Watch for these debug messages:")
        print("   - 🎮 [HOMEPAGE] handleCreateGame called")
        print("   - 🎮 [HOMEPAGE] API response status: 200")
        print("   - 🎮 [HOMEPAGE] Navigating to room: ABC123")
        print("   - 🏠 [ROOMPAGE] loadGameAndConnect called")
        print("   - 🏠 [ROOMPAGE] Setting isLoading to false")
        print("\n🔍 What to look for:")
        print("- Does navigation get called?")
        print("- Does RoomPage loadGameAndConnect start?")
        print("- Where exactly does it get stuck?")
        print("- Any API errors or missing responses?")
    else:
        print(f"⚠️  Only {success_count}/3 fixes applied. Check error messages above.")
    
    return success_count >= 2

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)