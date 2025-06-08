import React from 'react';

interface Player {
  id: string;
  username: string;
  team?: string;
  role?: string;
  isOnline?: boolean;
}

interface TeamSetupProps {
  lobbyId: string;
  players: Player[];
  currentUser: any;
  isConnected: boolean;
  isCreating: boolean;
  onJoinTeam: (team: string, role: string) => void;
  onStartGame: () => void;
  canStartGame: () => boolean;
}

const TeamSetup: React.FC<TeamSetupProps> = ({
  lobbyId,
  players,
  currentUser,
  isConnected,
  isCreating,
  onJoinTeam,
  onStartGame,
  canStartGame
}) => {
  const getCurrentUserPlayer = () => {
    return players.find(p => p.username === currentUser?.username || p.id === currentUser?.id);
  };

  const getTeamPlayers = (team: string) => {
    return players.filter(p => p.team === team);
  };

  const hasSpymaster = (team: string) => {
    return getTeamPlayers(team).some(p => p.role === 'spymaster');
  };

  const userPlayer = getCurrentUserPlayer();

  return (
    <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">
        🎮 Game Lobby: {lobbyId}
      </h1>
      
      {/* Team Assignment Section */}
      <div className="space-y-6">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">🕵️ Choose Your Team</h2>
          <p className="text-gray-600">Select your team and role to get ready for the game!</p>
        </div>

        {/* Current User Status */}
        {userPlayer && (
          <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
            <p className="text-center text-blue-900">
              You are: <span className="font-semibold">{userPlayer.username}</span>
              {userPlayer.team && userPlayer.team !== 'neutral' && (
                <span className={`ml-2 font-bold ${userPlayer.team === 'red' ? 'text-red-600' : 'text-blue-600'}`}>
                  • {userPlayer.team === 'red' ? '🔴' : '🔵'} {userPlayer.team} team 
                  ({userPlayer.role === 'spymaster' ? '👑 Spymaster' : '🕵️ Operative'})
                </span>
              )}
            </p>
          </div>
        )}

        {/* Team Selection Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Red Team */}
          <div className="bg-red-50 border-2 border-red-200 rounded-lg p-6">
            <h3 className="text-2xl font-semibold text-red-700 mb-4 text-center">
              🔴 Red Team
            </h3>
            <div className="space-y-3 mb-4">
              <button
                onClick={() => onJoinTeam('red', 'spymaster')}
                className="w-full bg-red-500 text-white px-4 py-3 rounded-lg font-semibold hover:bg-red-600 transition-colors disabled:bg-gray-400"
                disabled={hasSpymaster('red')}
              >
                {hasSpymaster('red') ? '👑 Spymaster Taken' : '👑 Join as Spymaster'}
              </button>
              <button
                onClick={() => onJoinTeam('red', 'operative')}
                className="w-full bg-red-400 text-white px-4 py-3 rounded-lg font-semibold hover:bg-red-500 transition-colors"
              >
                🕵️ Join as Operative
              </button>
            </div>
            <div className="text-sm text-gray-700">
              <div className="font-medium mb-2">Team Members:</div>
              {getTeamPlayers('red').length === 0 ? (
                <p className="text-gray-500 italic">No players yet</p>
              ) : (
                getTeamPlayers('red').map((player: any) => (
                  <div key={player.id} className="flex justify-between items-center py-1">
                    <span>{player.username}</span>
                    <span className="text-red-600 font-medium">
                      {player.role === 'spymaster' ? '👑' : '🕵️'} {player.role}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Blue Team */}
          <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6">
            <h3 className="text-2xl font-semibold text-blue-700 mb-4 text-center">
              🔵 Blue Team
            </h3>
            <div className="space-y-3 mb-4">
              <button
                onClick={() => onJoinTeam('blue', 'spymaster')}
                className="w-full bg-blue-500 text-white px-4 py-3 rounded-lg font-semibold hover:bg-blue-600 transition-colors disabled:bg-gray-400"
                disabled={hasSpymaster('blue')}
              >
                {hasSpymaster('blue') ? '👑 Spymaster Taken' : '👑 Join as Spymaster'}
              </button>
              <button
                onClick={() => onJoinTeam('blue', 'operative')}
                className="w-full bg-blue-400 text-white px-4 py-3 rounded-lg font-semibold hover:bg-blue-500 transition-colors"
              >
                🕵️ Join as Operative
              </button>
            </div>
            <div className="text-sm text-gray-700">
              <div className="font-medium mb-2">Team Members:</div>
              {getTeamPlayers('blue').length === 0 ? (
                <p className="text-gray-500 italic">No players yet</p>
              ) : (
                getTeamPlayers('blue').map((player: any) => (
                  <div key={player.id} className="flex justify-between items-center py-1">
                    <span>{player.username}</span>
                    <span className="text-blue-600 font-medium">
                      {player.role === 'spymaster' ? '👑' : '🕵️'} {player.role}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Start Game Button */}
        <div className="text-center">
          <button
            onClick={onStartGame}
            disabled={!canStartGame() || isCreating}
            className="bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-colors"
          >
            {isCreating ? (
              <span className="flex items-center justify-center">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                Creating Game...
              </span>
            ) : canStartGame() ? (
              '🚀 Start Codenames Game'
            ) : (
              '⏳ Waiting for Teams'
            )}
          </button>
          {!canStartGame() && !isCreating && (
            <p className="text-sm text-gray-600 mt-2">
              Need players on both teams to start
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default TeamSetup;
