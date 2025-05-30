import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ChatRoom from '../components/Chat/ChatRoom';

const HomePage: React.FC = () => {
  const [roomCode, setRoomCode] = useState('');
  const navigate = useNavigate();

  const handleCreateRoom = () => {
    // For Phase 1, just show success message
    alert('Room creation will be implemented in Phase 2!');
  };

  const handleJoinRoom = () => {
    if (!roomCode.trim()) {
      alert('Please enter a room code');
      return;
    }
    // For Phase 1, just show success message
    alert(`Joining room: ${roomCode} - Will be implemented in Phase 2!`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Welcome to Codenames!</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left side - Room management */}
          <div className="space-y-6">
            {/* Create Room */}
            <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
              <h2 className="text-xl font-semibold mb-4 text-gray-900">Create New Room</h2>
              <p className="text-gray-600 mb-4">Start a new game and invite friends to join</p>
              <button 
                onClick={handleCreateRoom}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded transition-colors"
              >
                Create Room
              </button>
            </div>
            
            {/* Join Room */}
            <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
              <h2 className="text-xl font-semibold mb-4 text-gray-900">Join Existing Room</h2>
              <div className="space-y-4">
                <div>
                  <label htmlFor="roomCode" className="block text-sm font-medium text-gray-700 mb-2">
                    Room Code
                  </label>
                  <input
                    type="text"
                    id="roomCode"
                    value={roomCode}
                    onChange={(e) => setRoomCode(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
                    placeholder="Enter room code"
                  />
                </div>
                <button 
                  onClick={handleJoinRoom}
                  className="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded transition-colors"
                >
                  Join Room
                </button>
              </div>
            </div>
            
            {/* Phase 1 Status */}
            <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
              <h3 className="font-semibold text-blue-900 mb-2">🎉 Phase 1: Real-time Communication!</h3>
              <div className="text-blue-800 space-y-1">
                <p>✅ Backend server and API working</p>
                <p>✅ Socket connection established</p>
                <p>✅ Authentication system working</p>
                <p>✅ Real-time messaging working</p>
                <p className="mt-2 font-semibold">📱 Test with multiple browser windows!</p>
              </div>
            </div>
          </div>
          
          {/* Right side - Chat Room */}
          <div>
            <h2 className="text-xl font-semibold mb-4 text-gray-900">Real-time Chat</h2>
            <ChatRoom />
            <div className="mt-4 text-sm text-gray-600 bg-yellow-50 border border-yellow-200 p-3 rounded">
              <p><strong>🧪 Phase 1 Test:</strong></p>
              <p>• Open this page in multiple browser windows</p>
              <p>• Login as different users in each window</p>
              <p>• Send messages and see them appear in real-time!</p>
            </div>
          </div>
        </div>
        
        {/* Debug Section */}
        <div className="mt-8 bg-gray-100 border border-gray-300 p-4 rounded-lg">
          <h3 className="font-semibold text-gray-900 mb-2">🔧 Debug Tools</h3>
          <div className="text-gray-700 space-y-2">
            <p>• <a href="/debug" className="text-blue-600 hover:text-blue-800 underline">Debug Dashboard</a> - Test connections</p>
            <p>• Check browser console (F12) for detailed logs</p>
            <p>• Room creation and game mechanics coming in Phase 2!</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
