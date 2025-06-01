#!/usr/bin/env python3
import os
from datetime import datetime

def update_session_summary():
    """
    Add the current session summary to SESSION_SUMMARIES.md
    """
    
    session_summary = f"""
## 📅 Session Summary - {datetime.now().strftime('%Y-%m-%d')}

### 🎯 **Session Goal: Fix Multiplayer Team Assignment**

**❌ INCOMPLETE - BLOCKERS REMAIN:**
- **Game State Structure Mismatch**: Backend game state exists but UI can't read team assignments
- **UI/Backend Disconnect**: Debug shows game state loaded but teams show "No players yet"
- **Team Assignment Logic**: Players can't join teams due to data structure issues

**✅ PROGRESS MADE:**
- **Enhanced Debug Tools**: Added comprehensive debug panel showing connection status, game state, and player info
- **Backend Architecture**: Proper room-specific game creation and state management
- **Socket Infrastructure**: Real-time communication and room joining works correctly
- **Error Handling**: Better error messages and connection state management

**🔧 CURRENT STATUS:**
- **Connection**: ✅ Socket connection working properly
- **Room Joining**: ✅ Players can join specific game rooms  
- **Game State Loading**: ✅ Backend creates and loads game state
- **Team Assignment UI**: ❌ UI cannot read/display team assignments from game state
- **Real-time Sync**: ❌ Team changes not propagating between users

### 📂 **Key Files Modified This Session:**
- `backend/src/index.ts` - Multiple fixes for socket handlers and game state management
- `frontend/src/pages/RoomPage.tsx` - Enhanced team assignment UI and game state handling
- Applied 4 Python scripts attempting to fix multiplayer sync issues

### 🎯 **Next Session Priorities:**
1. **Debug Game State Structure**: Examine actual game state object vs expected UI format
2. **Fix Team Assignment Data Flow**: Ensure backend team assignments reach frontend UI
3. **Test End-to-End Team Selection**: First user joins team → second user sees assignment
4. **Validate Game Start Logic**: Teams can start actual Codenames game
5. **Polish Multiplayer Experience**: Smooth team assignment and game flow

### 💡 **Technical Issues to Investigate:**
- **Data Structure Mismatch**: Backend `gameState.players` may not match frontend expectations
- **State Update Timing**: Game state updates may not be triggering UI re-renders properly
- **Room Code Consistency**: Ensure backend and frontend use same room code format
- **Socket Event Propagation**: Verify team assignment events broadcast to all room members

### 🔍 **Debug Evidence:**
- Debug panel shows: "Connected: Yes | Game State: Loaded | Players in Game: 1"
- But team selection UI shows: "No players yet" for both red/blue teams
- Indicates game state exists but UI can't access/parse team data correctly

**Phase 2 Team Assignment: 60% Complete** 🎮  
**Main Blocker: UI/Backend game state data structure mismatch** 🚨

---

"""

    try:
        with open('SESSION_SUMMARIES.md', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        content = "# Session Summaries\n\n"
    
    # Add the new session summary at the top (after the header)
    lines = content.split('\n')
    if lines[0].startswith('# Session Summaries'):
        # Insert after header
        lines.insert(2, session_summary)
    else:
        # Add at the beginning
        lines.insert(0, session_summary)
    
    updated_content = '\n'.join(lines)
    
    with open('SESSION_SUMMARIES.md', 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("✅ Session summary added to SESSION_SUMMARIES.md")
    
    # Also update README.md if it has a session summaries section
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        # Look for existing session summary section
        session_marker = "## 📅 Session Summary -"
        if session_marker in readme_content:
            # Replace the most recent session summary
            lines = readme_content.split('\n')
            new_lines = []
            skip_until_next_section = False
            
            for line in lines:
                if line.startswith(session_marker):
                    if not skip_until_next_section:
                        # This is the first/most recent session summary - replace it
                        new_lines.extend(session_summary.strip().split('\n'))
                        skip_until_next_section = True
                    else:
                        # This is an older session summary - keep it
                        new_lines.append(line)
                        skip_until_next_section = False
                elif skip_until_next_section and (line.startswith('## ') or line.startswith('# ')):
                    # Hit the next major section - stop skipping
                    skip_until_next_section = False
                    new_lines.append(line)
                elif not skip_until_next_section:
                    new_lines.append(line)
            
            updated_readme = '\n'.join(new_lines)
            
            with open('README.md', 'w', encoding='utf-8') as f:
                f.write(updated_readme)
            
            print("✅ Updated README.md with current session summary")
        
    except Exception as e:
        print(f"⚠️  Could not update README.md: {e}")
    
    print("\n🎉 SESSION SUMMARY COMPLETE!")
    print(f"📁 Summary saved to SESSION_SUMMARIES.md")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("\n🔍 KEY FINDING: Game state structure mismatch between backend and frontend")
    print("🎯 NEXT SESSION: Debug game state object format and fix team assignment UI")

if __name__ == "__main__":
    update_session_summary()
