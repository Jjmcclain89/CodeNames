import React, { useState, useEffect } from 'react';
import { socketService } from '../services/socketService';

const GameDebugPage: React.FC = () => {
  const [logs, setLogs] = useState<string[]>(['Debug page loaded...']);
  const [status, setStatus] = useState({ message: 'Ready to test...', type: 'info' });
  const [isConnected, setIsConnected] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const addLog = (message: string) => {
    const time = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, `[${time}] ${message}`]);
  };

  const updateStatus = (message: string, type: 'info' | 'success' | 'error' = 'info') => {
    setStatus({ message, type });
  };

  const clearLogs = () => {
    setLogs(['Debug page loaded...']);
  };

  useEffect(() => {
    // Check localStorage on component mount
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    
    if (token && user) {
      addLog('✅ Found authentication in localStorage');
      addLog(`   Token: ${token.substring(0, 20)}...`);
      addLog(`   User: ${user}`);
    } else {
      addLog('❌ No authentication found in localStorage');
      addLog('   Please login first at /login');
    }
  }, []);

  const testConnection = () => {
    addLog('🔌 Testing socket connection...');
    updateStatus('Connecting...', 'info');
    
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    
    if (!token || !user) {
      addLog('❌ No authentication found - please login first');
      updateStatus('Not authenticated - login first', 'error');
      return;
    }
    
    if (socketService.isConnected) {
      addLog('✅ Socket already connected');
      addLog(`   Socket ID: ${socketService.socketId}`);
      setIsConnected(true);
      updateStatus('Already connected', 'success');
      return;
    }
    
    // Connect socket
    socketService.connect();
    
    socketService.onConnect(() => {
      addLog('✅ Socket connected successfully');
      addLog(`   Socket ID: ${socketService.socketId}`);
      setIsConnected(true);
      updateStatus('Connected to server', 'success');
    });
    
    socketService.onDisconnect(() => {
      addLog('❌ Socket disconnected');
      setIsConnected(false);
      setIsAuthenticated(false);
      updateStatus('Disconnected', 'error');
    });
    
    socketService.socket?.on('connect_error', (error: any) => {
      addLog(`❌ Connection error: ${error}`);
      updateStatus('Connection failed', 'error');
    });
  };

  const testAuthentication = () => {
    if (!isConnected) {
      addLog('❌ Socket not connected - run connection test first');
      return;
    }
    
    addLog('🔐 Testing authentication...');
    
    const token = localStorage.getItem('token');
    if (!token) {
      addLog('❌ No token found');
      return;
    }
    
    socketService.onAuthenticated((data: any) => {
      if (data.success) {
        addLog('✅ Authentication successful');
        addLog(`   User: ${data.user?.username || 'Unknown'}`);
        setIsAuthenticated(true);
        updateStatus('Authenticated successfully', 'success');
      } else {
        addLog(`❌ Authentication failed: ${data.error}`);
        updateStatus('Authentication failed', 'error');
      }
    });
    
    socketService.authenticate(token);
  };

  const testGameCreate = () => {
    if (!isConnected || !isAuthenticated) {
      addLog('❌ Socket not connected or not authenticated - run tests 1 & 2 first');
      return;
    }
    
    addLog('🎮 Testing game creation...');
    
    // Listen for game events
    socketService.socket?.on('game:state-updated', (gameState: any) => {
      addLog('✅ Game state received!');
      addLog(`   Game ID: ${gameState.id}`);
      addLog(`   Status: ${gameState.status}`);
      addLog(`   Players: ${gameState.players.length}`);
      updateStatus('Game created successfully!', 'success');
    });
    
    socketService.socket?.on('game:error', (error: string) => {
      addLog(`❌ Game error: ${error}`);
      updateStatus('Game creation failed', 'error');
    });
    
    // Try to create game
    socketService.socket?.emit('game:create');
  };

  const testGameJoinTeam = () => {
    if (!isConnected || !isAuthenticated) {
      addLog('❌ Socket not connected or not authenticated');
      return;
    }
    
    addLog('👥 Testing team join...');
    
    socketService.socket?.on('game:state-updated', (gameState: any) => {
      addLog('✅ Team join successful - game state updated');
    });
    
    socketService.socket?.emit('game:join-team', 'red', 'spymaster');
  };

  const getStatusClass = () => {
    switch (status.type) {
      case 'success': return 'bg-green-100 border-green-400 text-green-700';
      case 'error': return 'bg-red-100 border-red-400 text-red-700';
      default: return 'bg-blue-100 border-blue-400 text-blue-700';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h1 className="text-3xl font-bold mb-6 text-gray-800">🔍 Game Debug Tool</h1>
          <p className="text-gray-600 mb-6">
            This page tests the socket connection and game events to diagnose issues.
          </p>

          {/* Status */}
          <div className={`p-4 rounded-lg border mb-6 ${getStatusClass()}`}>
            {status.message}
          </div>

          {/* Test Buttons */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
            <button
              onClick={testConnection}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
            >
              1. Test Connection
            </button>
            <button
              onClick={testAuthentication}
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition-colors"
              disabled={!isConnected}
            >
              2. Test Auth
            </button>
            <button
              onClick={testGameCreate}
              className="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600 transition-colors"
              disabled={!isAuthenticated}
            >
              3. Test Game Create
            </button>
            <button
              onClick={testGameJoinTeam}
              className="bg-orange-500 text-white px-4 py-2 rounded hover:bg-orange-600 transition-colors"
              disabled={!isAuthenticated}
            >
              4. Test Join Team
            </button>
            <button
              onClick={clearLogs}
              className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600 transition-colors"
            >
              Clear Log
            </button>
            <a
              href="/game"
              className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition-colors text-center"
            >
              Go to Game
            </a>
          </div>

          {/* Connection Status */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className={`p-3 rounded-lg ${isConnected ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
              🔌 Socket: {isConnected ? 'Connected' : 'Disconnected'}
            </div>
            <div className={`p-3 rounded-lg ${isAuthenticated ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
              🔐 Auth: {isAuthenticated ? 'Authenticated' : 'Not Authenticated'}
            </div>
          </div>

          {/* Log Area */}
          <div className="bg-gray-100 border rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm">
            {logs.map((log, index) => (
              <div key={index} className="mb-1">
                {log}
              </div>
            ))}
          </div>

          {/* Instructions */}
          <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h3 className="font-semibold text-yellow-800 mb-2">🎯 How to Use:</h3>
            <ol className="text-yellow-700 text-sm space-y-1">
              <li>1. Make sure you're logged in (should show ✅ authentication found)</li>
              <li>2. Click "Test Connection" to connect to socket</li>
              <li>3. Click "Test Auth" to authenticate with backend</li>
              <li>4. Click "Test Game Create" to test game creation</li>
              <li>5. If all tests pass, "Go to Game" should work!</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GameDebugPage;
