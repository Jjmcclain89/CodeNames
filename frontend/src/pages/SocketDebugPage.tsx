import React, { useEffect, useState } from 'react';
import { socketService } from '../services/socketService';

const SocketDebugPage: React.FC = () => {
  const [socketInfo, setSocketInfo] = useState<any>({});
  const [connectionHistory, setConnectionHistory] = useState<string[]>([]);

  useEffect(() => {
    const updateSocketInfo = () => {
      const info = {
        hasSocket: !!socketService.socket,
        isConnected: socketService.socket?.connected,
        socketId: socketService.socket?.id,
        timestamp: new Date().toLocaleTimeString()
      };
      setSocketInfo(info);
      
      const historyEntry = `${info.timestamp}: Socket ${info.socketId || 'none'} - Connected: ${info.isConnected}`;
      setConnectionHistory(prev => [...prev.slice(-10), historyEntry]);
    };

    // Update every second
    const interval = setInterval(updateSocketInfo, 1000);
    updateSocketInfo(); // Initial update

    return () => clearInterval(interval);
  }, []);

  const handleForceConnect = () => {
    console.log('🔧 DEBUG: Force connecting socket...');
    socketService.connect();
  };

  const handleForceDisconnect = () => {
    console.log('🔧 DEBUG: Force disconnecting socket...');
    socketService.disconnect();
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Socket Debug Console</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Current Socket State</h2>
            <div className="space-y-2 text-sm font-mono">
              <div>Has Socket: <span className={socketInfo.hasSocket ? 'text-green-600' : 'text-red-600'}>{String(socketInfo.hasSocket)}</span></div>
              <div>Connected: <span className={socketInfo.isConnected ? 'text-green-600' : 'text-red-600'}>{String(socketInfo.isConnected)}</span></div>
              <div>Socket ID: <span className="text-blue-600">{socketInfo.socketId || 'none'}</span></div>
              <div>Last Update: <span className="text-gray-600">{socketInfo.timestamp}</span></div>
            </div>
            
            <div className="mt-4 space-x-2">
              <button 
                onClick={handleForceConnect}
                className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded text-sm"
              >
                Force Connect
              </button>
              <button 
                onClick={handleForceDisconnect}
                className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded text-sm"
              >
                Force Disconnect
              </button>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Connection History</h2>
            <div className="h-64 overflow-y-auto bg-gray-50 p-3 rounded text-xs font-mono">
              {connectionHistory.length > 0 ? (
                connectionHistory.map((entry, index) => (
                  <div key={index} className="mb-1">{entry}</div>
                ))
              ) : (
                <div className="text-gray-500">No connection history yet...</div>
              )}
            </div>
          </div>
        </div>

        <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="font-semibold text-yellow-800 mb-2">Debug Instructions</h3>
          <div className="text-sm text-yellow-700">
            <p>1. Open browser console to see detailed socket logs</p>
            <p>2. Monitor the connection history above for patterns</p>
            <p>3. Look for multiple socket connections or reconnections</p>
            <p>4. Check if Socket ID changes unexpectedly</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SocketDebugPage;