import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import HomePage from './pages/HomePage';
import RoomPage from './pages/RoomPage';
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
  }, []);
  const handleLogin = (userData: any, token: string) => {
    setIsAuthenticated(true);
    setUser(userData);
    // Connect to socket after successful login
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
      <div className="App min-h-screen bg-gray-50">
        <header className="bg-blue-600 text-white p-4 shadow-lg">
          <div className="container mx-auto flex justify-between items-center">
            <h1 className="text-2xl font-bold">Codenames</h1>
            {isAuthenticated && (
              <div className="flex items-center space-x-4">
                <span>Welcome, {user?.username}!</span>
                <button
                  onClick={handleLogout}
                  className="bg-blue-700 hover:bg-blue-800 px-4 py-2 rounded text-sm"
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        </header>
        <main className="container mx-auto p-4">
          <Routes>
            <Route
              path="/login"
              element={
                !isAuthenticated ?
                <LoginPage onLogin={handleLogin} /> :
                <Navigate to="/" replace />
              }
            />
            <Route
              path="/"
              element={
                isAuthenticated ?
                <HomePage /> :
                <Navigate to="/login" replace />
              }
            />
            <Route
              path="/room/:roomCode"
              element={
                isAuthenticated ?
                <RoomPage /> :
                <Navigate to="/login" replace />
              }
            />
            <Route path="/game" element={<GamePage />} />
            <Route path="/debug-game" element={<GameDebugPage />} />
                      <Route
              path="/debug"
              element={<DebugPage />}
            />
            </Routes>
        </main>
      </div>
    </Router>
  );
}
export default App;
