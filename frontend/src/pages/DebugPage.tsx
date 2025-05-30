import React, { useState, useEffect } from 'react';
import authService from '../services/authService';
import socketService from '../services/socketService';

const DebugPage: React.FC = () => {
  const [apiStatus, setApiStatus] = useState<string>('Not tested');
  const [socketStatus, setSocketStatus] = useState<string>('Not connected');
  const [testResults, setTestResults] = useState<string[]>([]);

  const addResult = (message: string) => {
    setTestResults(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
  };

  const testAPI = async () => {
    addResult('🔑 Testing API connection...');
    setApiStatus('Testing...');
    
    try {
      const result = await authService.login('test-user');
      if (result.success) {
        setApiStatus('✅ Connected');
        addResult('🔑 API test successful');
      } else {
        setApiStatus('❌ Failed');
        addResult(`🔑 API test failed: ${result.error}`);
      }
    } catch (error) {
      setApiStatus('❌ Error');
      addResult(`🔑 API test error: ${error}`);
    }
  };

  const testSocket = () => {
    addResult('📡 Testing socket connection...');
    setSocketStatus('Connecting...');
    
    const socket = socketService.connect();
    
    socket.on('connect', () => {
      setSocketStatus('✅ Connected');
      addResult('📡 Socket connected successfully');
    });
    
    socket.on('connect_error', (error) => {
      setSocketStatus('❌ Failed');
      addResult(`📡 Socket connection failed: ${error}`);
    });
  };

  const clearResults = () => {
    setTestResults([]);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold mb-6 text-gray-900">Phase 1 Debug Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <h2 className="text-xl font-semibold mb-4 text-gray-900">API Connection Test</h2>
          <p className="mb-4 text-gray-700">
            Status: <span className="font-mono bg-gray-100 px-2 py-1 rounded text-gray-900">{apiStatus}</span>
          </p>
          <button 
            onClick={testAPI}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition-colors"
          >
            Test API Connection
          </button>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <h2 className="text-xl font-semibold mb-4 text-gray-900">Socket Connection Test</h2>
          <p className="mb-4 text-gray-700">
            Status: <span className="font-mono bg-gray-100 px-2 py-1 rounded text-gray-900">{socketStatus}</span>
          </p>
          <button 
            onClick={testSocket}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded transition-colors"
          >
            Test Socket Connection
          </button>
        </div>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Test Results</h2>
          <button 
            onClick={clearResults}
            className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-sm transition-colors"
          >
            Clear
          </button>
        </div>
        <div className="bg-gray-900 text-green-400 p-4 rounded h-64 overflow-y-auto font-mono text-sm">
          {testResults.length === 0 ? (
            <p className="text-gray-500">No test results yet...</p>
          ) : (
            <div className="space-y-1">
              {testResults.map((result, index) => (
                <div key={index} className="text-green-400">{result}</div>
              ))}
            </div>
          )}
        </div>
      </div>
      
      <div className="mt-6 bg-blue-50 border border-blue-200 p-4 rounded-lg">
        <p className="font-semibold text-blue-900 mb-2">Expected behavior:</p>
        <ul className="list-disc pl-5 mt-2 text-blue-800 space-y-1">
          <li>API test should return a token and user object</li>
          <li>Socket test should establish WebSocket connection</li>
          <li>Check browser console (F12) for detailed logs</li>
          <li>Both tests need backend server running on localhost:3001</li>
        </ul>
      </div>
      
      <div className="mt-4 bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
        <p className="font-semibold text-yellow-900 mb-2">🔧 Debugging Tips:</p>
        <ul className="list-disc pl-5 text-yellow-800 space-y-1">
          <li>If API fails: Check if backend server is running (npm run dev in backend folder)</li>
          <li>If Socket fails: Check CORS settings and port configurations</li>
          <li>Press F12 to open browser console for detailed error messages</li>
          <li>Try the regular login at <a href="/login" className="text-blue-600 underline hover:text-blue-800">/login</a> after tests pass</li>
        </ul>
      </div>
    </div>
  );
};

export default DebugPage;
