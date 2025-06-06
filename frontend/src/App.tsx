import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import HomePage from './pages/HomePage';
import GamePage from './pages/GamePage';
import DebugPage from './pages/DebugPage';
import GameDebugPage from './pages/GameDebugPage';
import authService from './services/authService';
import socketService from './services/socketService';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    console.log('🔍 APP DEBUG: useEffect triggered');
    console.log('🔍 APP DEBUG: Timestamp:', Date.now());
    
    const initAuth = async () => {
      const token = authService.getToken();
      const savedUser = authService.getUser();
      console.log('🔍 APP DEBUG: Token exists:', !!token);
      console.log('🔍 APP DEBUG: Saved user exists:', !!savedUser);
      
      if (token && savedUser) {
        // Verify token is still valid
        const result = await authService.verifyToken(token);
        console.log('🔍 APP DEBUG: Token verification result:', result.success);
        
        if (result.success) {
          setIsAuthenticated(true);
          setUser(savedUser);
          // Initialize socket connection with token
          console.log('🔌 App.tsx: Initializing socket connection for user:', savedUser.username);
          
          socketService.connect();
          socketService.authenticate(token);
        } else {
          authService.logout();
        }
      }
      setIsLoading(false);
    };
    
    initAuth();
  }, []);

  const handleLogin = (userData: any, token: string) => {
    console.log('🔍 LOGIN DEBUG: handleLogin called for user:', userData.username);
    
    setIsAuthenticated(true);
    setUser(userData);
    // Connect to socket after successful login
    console.log('🔌 App.tsx: Connecting socket after login for:', userData.username);
    socketService.connect();
    socketService.authenticate(token);
  };

  const handleLogout = () => {
    authService.logout();
    socketService.disconnect();
    setIsAuthenticated(false);
    setUser(null);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <Router>
      <div className="App min-h-screen">

        <main>
          <Routes>
            {/* Login Route */}
            <Route
              path="/login"
              element={
                !isAuthenticated ? (
                  <LoginPage onLogin={handleLogin} />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />
            
            {/* Home Route */}
            <Route
              path="/"
              element={
                isAuthenticated ? (
                  <HomePage />
                ) : (
                  <Navigate to="/login" replace />
                )
              }
            />
            
            {/* Game Route - Direct from homepage */}
            <Route
              path="/game/:gameCode"
              element={
                isAuthenticated ? (
                  <GamePage />
                ) : (
                  <Navigate to="/login" replace />
                )
              }
            />
            
            {/* Debug Routes */}
            <Route path="/debug-game" element={<GameDebugPage />} />
            <Route path="/debug" element={<DebugPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
