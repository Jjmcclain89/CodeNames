import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSocket } from '../hooks/useSocket';

const RoomPage: React.FC = () => {
  const { roomCode } = useParams<{ roomCode: string }>();
  const navigate = useNavigate();
  const [message, setMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { 
    isConnected, 
    currentRoom, 
    roomUsers, 
    messages, 
    joinRoom, 
    leaveRoom, 
    sendMessage,
    connectionError 
  } = useSocket();

  useEffect(() => {
    if (roomCode && isConnected) {
      joinRoom(roomCode);
    }
  }, [roomCode, isConnected]);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      sendMessage(message.trim());
      setMessage('');
    }
  };

  const handleLeaveRoom = () => {
    leaveRoom();
    navigate('/');
  };

  if (!isConnected) {
    return (
      <div className="text-center py-8">
        <div className="text-xl text-red-600 mb-4">Not connected to server</div>
        <button
          onClick={() => navigate('/')}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md"
        >
          Go Back
        </button>
      </div>
    );
  }

  if (!currentRoom) {
    return (
      <div className="text-center py-8">
        <div className="text-xl mb-4">Joining room {roomCode}...</div>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Room Header */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold">{currentRoom.name}</h2>
            <p className="text-gray-600">Room Code: <span className="font-mono font-bold">{currentRoom.code}</span></p>
          </div>
          <button
            onClick={handleLeaveRoom}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md"
          >
            Leave Room
          </button>
        </div>
      </div>

      <div className="grid lg:grid-cols-4 gap-6">
        {/* Game Board Area */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold mb-4">Game Board</h3>
            <div className="grid grid-cols-5 gap-2">
              {Array.from({ length: 25 }, (_, i) => (
                <div
                  key={i}
                  className="bg-gray-100 hover:bg-gray-200 p-4 text-center rounded cursor-pointer transition-colors h-20 flex items-center justify-center"
                >
                  <span className="text-sm font-medium">Card {i + 1}</span>
                </div>
              ))}
            </div>
            <div className="mt-4 text-center text-gray-600">
              Game will start when enough players join...
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          {/* Players List */}
          <div className="bg-white rounded-lg shadow-md p-4">
            <h3 className="font-bold mb-3">Players ({roomUsers.length})</h3>
            <div className="space-y-2">
              {roomUsers.map((user) => (
                <div key={user.id} className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm">{user.username}</span>
                </div>
              ))}
              {roomUsers.length === 0 && (
                <div className="text-gray-500 text-sm">No players yet</div>
              )}
            </div>
          </div>

          {/* Chat */}
          <div className="bg-white rounded-lg shadow-md p-4">
            <h3 className="font-bold mb-3">Chat</h3>
            
            {/* Messages */}
            <div className="h-48 overflow-y-auto border rounded p-2 mb-3 bg-gray-50">
              {messages.map((msg) => (
                <div key={msg.id} className="mb-2">
                  <div className="text-xs text-gray-500">
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </div>
                  <div className="text-sm">
                    <span className="font-medium">{msg.username}:</span> {msg.message}
                  </div>
                </div>
              ))}
              {messages.length === 0 && (
                <div className="text-gray-500 text-sm text-center py-4">
                  No messages yet
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Message Input */}
            <form onSubmit={handleSendMessage} className="flex">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Type a message..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
              />
              <button
                type="submit"
                disabled={!message.trim()}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white px-3 py-2 rounded-r-md text-sm"
              >
                Send
              </button>
            </form>
          </div>
        </div>
      </div>

      {connectionError && (
        <div className="fixed bottom-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {connectionError}
        </div>
      )}
    </div>
  );
};

export default RoomPage;
