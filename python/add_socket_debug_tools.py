#!/usr/bin/env python3
"""
Add socket debugging tools to the homepage
"""

import os

def add_socket_debug_tools():
    """Add comprehensive socket debugging tools to HomePage"""
    
    home_page_path = 'frontend/src/pages/HomePage.tsx'
    
    if not os.path.exists(home_page_path):
        print(f"❌ File not found: {home_page_path}")
        return False
    
    print("🔧 Adding socket debugging tools to HomePage...")
    
    # Read the current file
    with open(home_page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add socket service import if not present
    if "import { socketService }" not in content:
        # Find the imports section and add socketService
        if "import React" in content:
            content = content.replace(
                "import React",
                "import React, { useState, useEffect }\nimport { socketService }"
            )
        else:
            # Add at the top if no React import found
            content = "import React, { useState, useEffect } from 'react';\nimport { socketService } from '../services/socketService';\n\n" + content
        print("  ✅ Added socketService import")
    
    # Add useState and useEffect if not present
    if "useState" not in content:
        content = content.replace(
            "import React",
            "import React, { useState, useEffect }"
        )
    
    # Add debug state at the start of the component
    if "const HomePage: React.FC = () => {" in content:
        debug_state = '''const HomePage: React.FC = () => {
  // Debug state for socket monitoring
  const [socketDebug, setSocketDebug] = useState({
    isConnected: false,
    socketId: '',
    connectionCount: 0,
    connectionHistory: [] as string[],
    lastActivity: '',
    socketInstance: null as any
  });
  
  // Update socket debug info
  useEffect(() => {
    const updateDebugInfo = () => {
      const socket = socketService.socket;
      setSocketDebug(prev => ({
        ...prev,
        isConnected: socketService.isConnected,
        socketId: socket?.id || 'Not connected',
        socketInstance: socket,
        lastActivity: new Date().toLocaleTimeString()
      }));
    };
    
    // Update every second
    const interval = setInterval(updateDebugInfo, 1000);
    
    // Set up socket event listeners for debugging
    if (socketService.socket) {
      socketService.socket.on('connect', () => {
        setSocketDebug(prev => ({
          ...prev,
          connectionCount: prev.connectionCount + 1,
          connectionHistory: [...prev.connectionHistory, `Connected at ${new Date().toLocaleTimeString()}`].slice(-10)
        }));
      });
      
      socketService.socket.on('disconnect', () => {
        setSocketDebug(prev => ({
          ...prev,
          connectionHistory: [...prev.connectionHistory, `Disconnected at ${new Date().toLocaleTimeString()}`].slice(-10)
        }));
      });
    }
    
    // Initial update
    updateDebugInfo();
    
    return () => {
      clearInterval(interval);
    };
  }, []);'''
        
        content = content.replace(
            "const HomePage: React.FC = () => {",
            debug_state
        )
        print("  ✅ Added socket debug state and monitoring")
    
    # Find the existing state declarations and add after them
    existing_state_pattern = r'(const \[.*?, set.*?\] = useState.*?;)'
    existing_states = []
    
    # Add debug panel to the JSX - find the return statement
    if "return (" in content:
        # Find the main container div and add debug panel at the top
        debug_panel_jsx = '''        {/* Socket Debug Panel */}
        <div className="mb-6 bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4">
          <h2 className="text-lg font-bold text-yellow-800 mb-3">🔧 Socket Debug Panel</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
            <div className="bg-white p-3 rounded border">
              <h3 className="font-semibold text-gray-700 mb-2">Connection Status</h3>
              <div className={`px-2 py-1 rounded text-white text-center ${socketDebug.isConnected ? 'bg-green-500' : 'bg-red-500'}`}>
                {socketDebug.isConnected ? '✅ Connected' : '❌ Disconnected'}
              </div>
              <div className="mt-2 text-xs text-gray-600">
                Socket ID: {socketDebug.socketId}
              </div>
            </div>
            
            <div className="bg-white p-3 rounded border">
              <h3 className="font-semibold text-gray-700 mb-2">Connection Stats</h3>
              <div className="space-y-1">
                <div>Total Connections: <span className="font-mono font-bold text-blue-600">{socketDebug.connectionCount}</span></div>
                <div>Last Activity: <span className="font-mono text-xs">{socketDebug.lastActivity}</span></div>
                <div>Socket Instance: {socketDebug.socketInstance ? '✅ Exists' : '❌ Null'}</div>
              </div>
            </div>
            
            <div className="bg-white p-3 rounded border">
              <h3 className="font-semibold text-gray-700 mb-2">Debug Actions</h3>
              <div className="space-y-2">
                <button 
                  onClick={() => {
                    console.log('🔍 Socket Service Debug:', socketService);
                    console.log('🔍 Current Socket:', socketService.socket);
                    console.log('🔍 Window.socketService:', (window as any).socketService);
                  }}
                  className="w-full bg-blue-500 text-white px-2 py-1 rounded text-xs hover:bg-blue-600"
                >
                  Log Socket Info
                </button>
                <button 
                  onClick={() => {
                    socketService.connect();
                    console.log('🔌 Manual connection attempt');
                  }}
                  className="w-full bg-green-500 text-white px-2 py-1 rounded text-xs hover:bg-green-600"
                >
                  Connect Socket
                </button>
                <button 
                  onClick={() => {
                    socketService.disconnect();
                    console.log('🔌 Manual disconnect');
                  }}
                  className="w-full bg-red-500 text-white px-2 py-1 rounded text-xs hover:bg-red-600"
                >
                  Disconnect Socket
                </button>
              </div>
            </div>
          </div>
          
          {socketDebug.connectionHistory.length > 0 && (
            <div className="mt-4 bg-white p-3 rounded border">
              <h3 className="font-semibold text-gray-700 mb-2">Connection History</h3>
              <div className="max-h-32 overflow-y-auto">
                {socketDebug.connectionHistory.map((event, index) => (
                  <div key={index} className="text-xs text-gray-600 font-mono">
                    {event}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>'''
        
        # Find the first div after return and add debug panel
        if '<div className="min-h-screen bg-gray-50">' in content:
            content = content.replace(
                '<div className="min-h-screen bg-gray-50">',
                '''<div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto p-6">
''' + debug_panel_jsx
            )
            print("  ✅ Added socket debug panel to JSX")
        else:
            print("  ⚠️ Could not find main container div to add debug panel")
    
    # Write the enhanced content back
    with open(home_page_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Added socket debugging tools to HomePage!")
    print("\n🔧 Debug tools added:")
    print("  1. Real-time connection status indicator")
    print("  2. Socket ID display") 
    print("  3. Connection count tracker")
    print("  4. Connection history log")
    print("  5. Manual connect/disconnect buttons")
    print("  6. Console logging buttons for detailed inspection")
    
    return True

if __name__ == "__main__":
    success = add_socket_debug_tools()
    if success:
        print("\n🎯 Testing Instructions:")
        print("1. Go to the homepage")
        print("2. Watch the Socket Debug Panel")
        print("3. Use 'Log Socket Info' button to inspect socket in console")
        print("4. Try creating a room and watch connection count")
        print("5. Check if multiple connections are being created")
        print("\n📋 What to look for:")
        print("  - Connection count should stay at 1")
        print("  - Socket ID should remain consistent")
        print("  - No rapid connection/disconnection cycles")
        print("  - Console logs should show single socket instance")
    else:
        print("\n❌ Debug tools failed to add - check the file and try again")
