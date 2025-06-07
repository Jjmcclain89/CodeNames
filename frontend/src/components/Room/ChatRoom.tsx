import React from 'react';

interface Player {
  id: string;
  username: string;
  team?: string;
  role?: string;
  isOnline?: boolean;
}

interface RoomMessage {
  id: string;
  username: string;
  userId: string;
  text: string;
  timestamp: string;
}

interface ChatRoomProps {
  players: Player[];
  messages: RoomMessage[];
  newMessage: string;
  setNewMessage: (message: string) => void;
  isConnected: boolean;
  onSendMessage: () => void;
  onKeyPress: (e: React.KeyboardEvent) => void;
}

const ChatRoom: React.FC<ChatRoomProps> = ({
  players,
  messages,
  newMessage,
  setNewMessage,
  isConnected,
  onSendMessage,
  onKeyPress
}) => {
  return (
    <div className="space-y-6">
      {/* Players List */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-4">
        <h3 className="font-semibold text-gray-900 mb-4">
          👥 Players ({players.length})
        </h3>
        <div className="space-y-2">
          {players.length > 0 ? (
            players.map((player: any) => (
              <div key={player.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <div>
                  <div className="font-medium text-gray-900 flex items-center">
                    {player.username}
                    {player.team && player.team !== 'neutral' && (
                      <span className={`ml-2 text-xs px-2 py-1 rounded ${player.team === 'red' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'}`}>
                        {player.team === 'red' ? '🔴' : '🔵'} {player.role === 'spymaster' ? '👑' : '🕵️'}
                      </span>
                    )}
                  </div>
                </div>
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              </div>
            ))
          ) : (
            <div className="text-gray-500 text-sm text-center py-4">
              No players yet
            </div>
          )}
        </div>
      </div>

      {/* Room Chat */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-4">
        <h3 className="font-semibold text-gray-900 mb-4">💬 Room Chat</h3>
        
        <div className="h-64 overflow-y-auto border border-gray-200 rounded p-2 mb-4 bg-gray-50">
          {messages.length > 0 ? (
            messages.map((message) => (
              <div key={message.id} className="mb-2 text-sm">
                <span className="font-medium text-blue-600">{message.username}:</span>
                <span className="text-gray-800 ml-1">{message.text}</span>
                <div className="text-xs text-gray-500">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ))
          ) : (
            <div className="text-gray-500 text-center py-8">
              No messages yet. Start the conversation!
            </div>
          )}
        </div>

        <div className="flex space-x-2">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={onKeyPress}
            placeholder={isConnected ? "Type a message..." : "Connecting..."}
            disabled={!isConnected}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          />
          <button
            onClick={onSendMessage}
            disabled={!newMessage.trim() || !isConnected}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white px-4 py-2 rounded text-sm"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatRoom;
