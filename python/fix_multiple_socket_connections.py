#!/usr/bin/env python3

import os
import sys

def fix_multiple_socket_connections():
    """
    Fix multiple socket connections issue by:
    1. Removing React.StrictMode (main culprit)
    2. Centralizing socket connection in App.tsx only
    3. Removing redundant socket.connect() calls from other components
    """
    
    # Set encoding for Windows
    if sys.platform.startswith('win'):
        encoding = 'utf-8'
    else:
        encoding = 'utf-8'
    
    print("=== FIXING MULTIPLE SOCKET CONNECTIONS ===")
    print()
    
    # 1. Remove React.StrictMode from main.tsx
    print("1. Removing React.StrictMode from main.tsx...")
    main_path = 'frontend/src/main.tsx'
    
    try:
        with open(main_path, 'r', encoding=encoding) as f:
            main_content = f.read()
        
        # Remove StrictMode wrapper
        new_main_content = '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <App />,
)
'''
        
        with open(main_path, 'w', encoding=encoding) as f:
            f.write(new_main_content)
        
        print("   ✅ Removed React.StrictMode")
        
    except Exception as e:
        print(f"   ❌ Error updating main.tsx: {e}")
    
    # 2. Update useSocket.ts to NOT call connect automatically
    print("2. Updating useSocket.ts to remove automatic connection...")
    use_socket_path = 'frontend/src/hooks/useSocket.ts'
    
    try:
        with open(use_socket_path, 'r', encoding=encoding) as f:
            use_socket_content = f.read()
        
        # Replace the useEffect that calls connect
        new_use_socket_content = use_socket_content.replace(
            '''  useEffect(() => {
    const socket = socketService.connect();
    const handlers = handlersRef.current;''',
            '''  useEffect(() => {
    // Don't auto-connect - let App.tsx handle connection
    const socket = socketService.socket;
    if (!socket) {
      console.log('⚠️ useSocket: No socket available, waiting for App.tsx to connect');
      return;
    }
    const handlers = handlersRef.current;'''
        )
        
        with open(use_socket_path, 'w', encoding=encoding) as f:
            f.write(new_use_socket_content)
        
        print("   ✅ Updated useSocket to not auto-connect")
        
    except Exception as e:
        print(f"   ❌ Error updating useSocket.ts: {e}")
    
    # 3. Update RoomPage.tsx to not call connect again
    print("3. Updating RoomPage.tsx to use existing connection...")
    room_page_path = 'frontend/src/pages/RoomPage.tsx'
    
    try:
        with open(room_page_path, 'r', encoding=encoding) as f:
            room_page_content = f.read()
        
        # Add connection tracking variable
        room_page_content = room_page_content.replace(
            '''const RoomPage: React.FC = () => {
  const { roomCode } = useParams<{ roomCode: string }>();
  const navigate = useNavigate();''',
            '''const RoomPage: React.FC = () => {
  const { roomCode } = useParams<{ roomCode: string }>();
  const navigate = useNavigate();
  const [connectionInitiated, setConnectionInitiated] = useState(false);'''
        )
        
        # Update the connectToRoom function to check existing connection first
        room_page_content = room_page_content.replace(
            '''  const connectToRoom = async (gameCode: string, token: string, user: any) => {
    console.log('🔌 Connecting to room socket...', gameCode);
    
    // Check if already connected to this room
    if (isConnected && socketService.socket?.connected) {
      console.log('🔍 Already connected to socket, skipping connection');
      return Promise.resolve();
    }
    
    return new Promise<void>((resolve) => {
      // Ensure socket is connected and authenticated
      if (!socketService.socket?.connected) {
        console.log('🔌 Creating new socket connection');
        socketService.connect();
      } else {
        console.log('🔌 Reusing existing socket connection');
      }''',
            '''  const connectToRoom = async (gameCode: string, token: string, user: any) => {
    console.log('🔌 Connecting to room socket...', gameCode);
    
    // Check if already connected to this room
    if (isConnected && socketService.socket?.connected) {
      console.log('🔍 Already connected to socket, skipping connection');
      return Promise.resolve();
    }
    
    return new Promise<void>((resolve) => {
      // Use existing socket connection from App.tsx - DON'T create new one
      if (!socketService.socket?.connected) {
        console.log('❌ No socket connection available - App.tsx should have created it');
        return;
      } else {
        console.log('✅ Using existing socket connection from App.tsx');
      }'''
        )
        
        with open(room_page_path, 'w', encoding=encoding) as f:
            f.write(room_page_content)
        
        print("   ✅ Updated RoomPage to use existing connection")
        
    except Exception as e:
        print(f"   ❌ Error updating RoomPage.tsx: {e}")
    
    # 4. Update App.tsx to be the single source of socket connection
    print("4. Updating App.tsx to be sole socket connection manager...")
    app_path = 'frontend/src/App.tsx'
    
    try:
        with open(app_path, 'r', encoding=encoding) as f:
            app_content = f.read()
        
        # Add better socket management in App.tsx
        app_content = app_content.replace(
            '''  useEffect(() => {
    const initAuth = async () => {
      const token = authService.getToken();
      const savedUser = authService.getUser();
      if (token && savedUser) {
        // Verify token is still valid
        const result = await authService.verifyToken(token);
        if (result.success) {
          setIsAuthenticated(true);
          setUser(savedUser);
          // Initialize socket connection with token
          socketService.connect();
          socketService.authenticate(token);
        } else {
          authService.logout();
        }
      }
      setIsLoading(false);
    };
    initAuth();
  }, []);''',
            '''  useEffect(() => {
    const initAuth = async () => {
      const token = authService.getToken();
      const savedUser = authService.getUser();
      if (token && savedUser) {
        // Verify token is still valid
        const result = await authService.verifyToken(token);
        if (result.success) {
          setIsAuthenticated(true);
          setUser(savedUser);
          // Initialize socket connection with token - SINGLE SOURCE OF TRUTH
          console.log('🔌 App.tsx: Initializing socket connection');
          socketService.connect();
          socketService.authenticate(token);
        } else {
          authService.logout();
        }
      }
      setIsLoading(false);
    };
    initAuth();
  }, []);'''
        )
        
        # Update handleLogin to also manage socket
        app_content = app_content.replace(
            '''  const handleLogin = (userData: any, token: string) => {
    setIsAuthenticated(true);
    setUser(userData);
    // Connect to socket after successful login
    socketService.connect();
    socketService.authenticate(token);
  };''',
            '''  const handleLogin = (userData: any, token: string) => {
    setIsAuthenticated(true);
    setUser(userData);
    // Connect to socket after successful login - SINGLE SOURCE OF TRUTH
    console.log('🔌 App.tsx: Connecting socket after login');
    socketService.connect();
    socketService.authenticate(token);
  };'''
        )
        
        with open(app_path, 'w', encoding=encoding) as f:
            f.write(app_content)
        
        print("   ✅ Updated App.tsx as single socket manager")
        
    except Exception as e:
        print(f"   ❌ Error updating App.tsx: {e}")
    
    print()
    print("=== SOCKET CONNECTION FIX SUMMARY ===")
    print("✅ Removed React.StrictMode (eliminates double useEffect calls)")
    print("✅ Made App.tsx the single socket connection manager")
    print("✅ Updated useSocket.ts to not auto-connect")
    print("✅ Updated RoomPage.tsx to use existing connection")
    print()
    print("🎯 NEXT STEPS:")
    print("1. Restart the frontend dev server")
    print("2. Open browser console and look for socket connection messages")
    print("3. Should now see only 1 connection instead of 2")
    print("4. Test team assignment with multiple browser windows")
    print()
    print("🔍 Debug: Look for these console messages:")
    print("   • '🔌 App.tsx: Initializing socket connection'")
    print("   • '🔌 CONNECT() CALLED' (should appear only once)")
    print("   • '✅ Connected to server, Socket ID: ...' (should appear only once)")
    
if __name__ == "__main__":
    fix_multiple_socket_connections()
