import React from 'react';

interface Player {
  id: string;
  username: string;
  team?: string;
  role?: string;
  isOnline?: boolean;
}

interface GameLobbyMessage {
  id: string;
  username: string;
  userId: string;
  text: string;
  timestamp: string;
}

interface LobbyChatProps {
  players: Player[];
  messages: GameLobbyMessage[];
  newMessage: string;
  setNewMessage: (message: string) => void;
  isConnected: boolean;
  onSendMessage: () => void;
  onKeyPress: (e: React.KeyboardEvent) => void;
}

const LobbyChat: React.FC<LobbyChatProps> = ({
  players,
  messages,
  newMessage,
  setNewMessage,
  isConnected,
  onSendMessage,
  onKeyPress
}) => {
  return (
    <div className="bg-gradient-to-br from-slate-800/90 to-slate-900/90 rounded-xl shadow-xl border border-slate-600/50 p-4 backdrop-blur-lg">
      <h3 className="font-semibold text-slate-100 mb-4 flex items-center">
        <span className="text-xl mr-2">💬</span>
        Lobby Chat
      </h3>
      
      <div className="overflow-y-auto border border-slate-600/50 rounded-lg p-3 mb-4 bg-slate-700/30 backdrop-blur-sm scrollbar-thin scrollbar-thumb-slate-600 scrollbar-track-slate-800">
        {messages.length > 0 ? (
          messages.map((message) => (
            <div key={message.id} className="mb-3 p-2 rounded-lg bg-slate-600/20 border border-slate-600/20">
              <div className="text-sm">
                <span className="font-medium text-blue-300">{message.username}:</span>
                <span className="text-slate-200 ml-2">{message.text}</span>
              </div>
              <div className="text-xs text-slate-500 mt-1">
                {new Date(message.timestamp).toLocaleTimeString()}
              </div>
            </div>
          ))
        ) : (
          <div className="text-slate-400 text-center py-12 flex flex-col items-center">
            <div className="text-3xl mb-2">💬</div>
            <div className="text-sm">No messages yet</div>
            <div className="text-xs text-slate-500 mt-1">Start the conversation!</div>
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
          className="flex-1 px-3 py-2 bg-slate-700/60 border border-slate-500/50 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-slate-100 placeholder-slate-400 text-sm backdrop-blur-sm"
        />
        <button
          onClick={onSendMessage}
          disabled={!newMessage.trim() || !isConnected}
          className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-slate-600 disabled:to-slate-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 shadow-lg"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default LobbyChat;