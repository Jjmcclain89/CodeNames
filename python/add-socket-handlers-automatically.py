#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Add Socket Handlers Automatically
Automatically adds the room-specific socket handlers to backend index.ts
"""

import os
from datetime import datetime

def update_file_content(file_path, new_content):
    """Update file with proper Windows encoding"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def read_file_content(file_path):
    """Read file content safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading {file_path}: {e}"

def main():
    print("🔧 Adding Socket Handlers Automatically to Backend...")
    
    # Read the current backend index.ts
    backend_index_path = 'backend/src/index.ts'
    backend_content = read_file_content(backend_index_path)
    
    if "Error reading" in backend_content:
        print(f"❌ {backend_content}")
        return
    
    # Check if socket handlers are already added
    if 'join-game-room' in backend_content:
        print("✅ Socket handlers already exist in backend index.ts")
        return
    
    print("🔧 Adding room-specific socket handlers...")
    
    # The socket handlers to add
    socket_handlers = '''
  // Room-specific socket handlers
  socket.on('join-game-room', (gameCode: string) => {
    const user = connectedUsers.get(socket.id);
    if (!user) {
      socket.emit('error', { message: 'Not authenticated' });
      return;
    }
    
    console.log(`🎮 User ${user.username} joining game room: ${gameCode}`);
    
    // Leave any previous game rooms
    const rooms = Array.from(socket.rooms);
    rooms.forEach(room => {
      if (room !== socket.id && room !== 'GLOBAL' && room.length === 6) {
        socket.leave(room);
        console.log(`📤 User ${user.username} left room: ${room}`);
      }
    });
    
    // Join the new game room
    socket.join(gameCode);
    
    // Import gameRooms from routes
    const { gameRooms } = require('./routes/games');
    const gameRoom = gameRooms.get(gameCode);
    
    if (gameRoom) {
      // Update player socket ID in game room
      const player = gameRoom.players.find((p: any) => p.username === user.username);
      if (player) {
        player.socketId = socket.id;
      }
      
      // Notify others in the room
      socket.to(gameCode).emit('player-joined-room', {
        player: { username: user.username, id: user.id },
        message: `${user.username} joined the game`,
        playerCount: gameRoom.players.length
      });
      
      // Send current room state to the joining player
      socket.emit('room-state', {
        gameCode: gameCode,
        players: gameRoom.players.map((p: any) => ({
          id: p.id,
          username: p.username,
          joinedAt: p.joinedAt
        })),
        messages: gameRoom.messages.slice(-20)
      });
      
      console.log(`✅ User ${user.username} joined game room ${gameCode}`);
    } else {
      socket.emit('error', { message: 'Game room not found' });
    }
  });

  socket.on('send-room-message', (data: { gameCode: string; message: string }) => {
    const user = connectedUsers.get(socket.id);
    if (!user) {
      socket.emit('error', { message: 'Not authenticated' });
      return;
    }
    
    const { gameCode, message } = data;
    console.log(`💬 Room message from ${user.username} in ${gameCode}: ${message}`);
    
    const { gameRooms } = require('./routes/games');
    const gameRoom = gameRooms.get(gameCode);
    
    if (gameRoom) {
      const roomMessage = {
        id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
        username: user.username,
        userId: user.id,
        text: message,
        timestamp: new Date().toISOString()
      };
      
      // Add to room messages
      gameRoom.messages.push(roomMessage);
      
      // Keep only last 50 messages
      if (gameRoom.messages.length > 50) {
        gameRoom.messages = gameRoom.messages.slice(-50);
      }
      
      // Broadcast to all users in the room
      io.to(gameCode).emit('new-room-message', roomMessage);
    } else {
      socket.emit('error', { message: 'Game room not found' });
    }
  });
'''
    
    # Find the right place to insert the socket handlers
    # Look for the 'send-message' handler and add after it
    lines = backend_content.split('\n')
    new_lines = []
    handlers_added = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        # Look for the end of the send-message handler
        if "socket.on('send-message'" in line:
            # Find the closing of this handler (looking for the next socket.on or socket event)
            j = i + 1
            brace_count = 0
            found_closing = False
            
            while j < len(lines):
                current_line = lines[j]
                new_lines.append(current_line)
                
                # Count braces to find the end of the handler
                brace_count += current_line.count('{') - current_line.count('}')
                
                # If we're back to 0 braces and find the closing }); pattern
                if brace_count <= 0 and '});' in current_line:
                    # Add our socket handlers after this line
                    new_lines.extend(socket_handlers.split('\n'))
                    handlers_added = True
                    found_closing = True
                    i = j
                    break
                
                j += 1
            
            if not found_closing:
                # Fallback: just add after the send-message line
                new_lines.extend(socket_handlers.split('\n'))
                handlers_added = True
        
        i += 1
    
    if not handlers_added:
        print("⚠️ Could not find 'send-message' handler, adding at end of socket handlers...")
        
        # Find the disconnect handler and add before it
        new_lines = []
        for i, line in enumerate(lines):
            if "socket.on('disconnect'" in line:
                # Add our handlers before the disconnect handler
                new_lines.extend(socket_handlers.split('\n'))
                new_lines.append('')
                handlers_added = True
            new_lines.append(line)
    
    if handlers_added:
        updated_content = '\n'.join(new_lines)
        
        if update_file_content(backend_index_path, updated_content):
            print("✅ Added socket handlers to backend/src/index.ts")
        else:
            print("❌ Failed to update backend index.ts")
            return
    else:
        print("❌ Could not find suitable location to add socket handlers")
        return
    
    # Update changelog
    try:
        changelog_path = 'CHANGELOG.md'
        with open(changelog_path, 'r', encoding='utf-8') as f:
            changelog = f.read()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        new_entry = f'- Socket Handlers Automation: Automatically added room socket handlers to backend index.ts ({timestamp})'
        
        if '### Python Scripts Run' in changelog:
            updated_changelog = changelog.replace(
                '### Python Scripts Run',
                f'### Python Scripts Run\n{new_entry}'
            )
            
            with open(changelog_path, 'w', encoding='utf-8') as f:
                f.write(updated_changelog)
            print("✅ Updated CHANGELOG.md")
    except Exception as e:
        print(f"Note: Could not update changelog: {e}")
    
    print(f"\n🎉 Socket Handlers Added Automatically!")
    print("\n🔧 What was added:")
    print("• join-game-room socket handler for room connections")
    print("• send-room-message socket handler for room-specific chat")
    print("• Player tracking and real-time updates")
    print("• Room state synchronization")
    print("\n🎯 Next Steps:")
    print("1. **RESTART your backend server** (to load new socket handlers)")
    print("2. **Restart your frontend server** (to be safe)")
    print("3. **Test multiplayer:**")
    print("   - Create game in browser window 1")
    print("   - Join same code in browser window 2")
    print("   - See both players in room")
    print("   - Test room chat!")
    print("\n💡 You're absolutely right - there was no reason to make this manual!")
    print("🎮 Full multiplayer functionality is now automated and ready!")

if __name__ == "__main__":
    main()
