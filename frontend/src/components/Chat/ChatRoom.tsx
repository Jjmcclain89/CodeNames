import React, { useState, useEffect, useRef } from 'react';
import socketService from '../../services/socketService';

interface Message {
  id: string;
  username: string;
  userId: string;
  text: string;
  timestamp: string;
}

interface User {
  id: string;
  username: string;
}

const ChatRoom: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [users, setUsers] = useState<User[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Set up socket listeners
    socketService.onConnect(() => {
      console.log('💬 Chat: Connected to server');
      setIsConnected(true);
    });

    socketService.onDisconnect(() => {
      console.log('💬 Chat: Disconnected from server');
      setIsConnected(false);
    });

    // Listen for authentication success
    socketService.onAuthenticated((data: any) => {
      if (data.success) {
        console.log('💬 Chat: Authenticated successfully');
      }
    });

    // Listen for recent messages
    const handleRecentMessages = (data: { messages: Message[] }) => {
      console.log('💬 Chat: Received recent messages:', data.messages);
      setMessages(data.messages);
    };

    // Listen for new messages
    const handleNewMessage = (message: Message) => {
      console.log('💬 Chat: New message:', message);
      setMessages(prev => [...prev, message]);
    };

    // Listen for user events
    const handleUserJoined = (data: { user: User; message: string }) => {
      console.log('💬 Chat: User joined:', data.user.username);
      // Add system message
      const systemMessage: Message = {
        id: `system_${Date.now()}`,
        username: 'System',
        userId: 'system',
        text: data.message,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, systemMessage]);
    };

    const handleUserLeft = (data: { user: User; message: string }) => {
      console.log('💬 Chat: User left:', data.user.username);
      // Add system message
      const systemMessage: Message = {
        id: `system_${Date.now()}`,
        username: 'System',
        userId: 'system',
        text: data.message,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, systemMessage]);
    };

    const handleRoomUsers = (data: { users: User[] }) => {
      console.log('💬 Chat: Room users updated:', data.users);
      setUsers(data.users);
    };

    // Set up socket listeners
    socketService.socket?.on('recent-messages', handleRecentMessages);
    socketService.socket?.on('new-message', handleNewMessage);
    socketService.socket?.on('user-joined', handleUserJoined);
    socketService.socket?.on('user-left', handleUserLeft);
    socketService.socket?.on('room-users', handleRoomUsers);

    // Cleanup
    return () => {
      socketService.socket?.off('recent-messages', handleRecentMessages);
      socketService.socket?.off('new-message', handleNewMessage);
      socketService.socket?.off('user-joined', handleUserJoined);
      socketService.socket?.off('user-left', handleUserLeft);
      socketService.socket?.off('room-users', handleRoomUsers);
    };
  }, []);

  const sendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newMessage.trim()) return;
    
    console.log('💬 Chat: Sending message:', newMessage);
    socketService.socket?.emit('send-message', { message: newMessage.trim() });
    setNewMessage('');
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div className="bg-white rounded-lg shadow border border-gray-200 h-96 flex flex-col">
      {/* Header */}
      <div className="bg-blue-600 text-white p-3 rounded-t-lg">
        <h3 className="font-semibold">Global Chat Room</h3>
        <div className="text-sm opacity-90">
          {isConnected ? (
            <span className="flex items-center">
              <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
              {users.length} user{users.length !== 1 ? 's' : ''} online
            </span>
          ) : (
            <span className="flex items-center">
              <span className="w-2 h-2 bg-red-400 rounded-full mr-2"></span>
              Disconnected
            </span>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <p>No messages yet...</p>
            <p className="text-sm">Send a message to start the conversation!</p>
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className={`${
              message.username === 'System' ? 'text-center text-gray-500 text-sm' : ''
            }`}>
              {message.username === 'System' ? (
                <em>{message.text}</em>
              ) : (
                <div className="flex flex-col">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-blue-600">{message.username}</span>
                    <span className="text-xs text-gray-500">{formatTime(message.timestamp)}</span>
                  </div>
                  <p className="text-gray-900 mt-1">{message.text}</p>
                </div>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={sendMessage} className="p-3 border-t border-gray-200">
        <div className="flex space-x-2">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
            disabled={!isConnected}
          />
          <button
            type="submit"
            disabled={!isConnected || !newMessage.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white px-4 py-2 rounded-md transition-colors"
          >
            Send
          </button>
        </div>
      </form>

      {/* Online Users */}
      {users.length > 0 && (
        <div className="p-3 border-t border-gray-200 bg-gray-50">
          <p className="text-sm font-medium text-gray-700 mb-2">Online Users:</p>
          <div className="flex flex-wrap gap-2">
            {users.map((user) => (
              <span key={user.id} className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
                {user.username}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatRoom;
