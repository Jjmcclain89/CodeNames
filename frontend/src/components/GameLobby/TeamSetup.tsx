import React from 'react';
import TeamAssignmentPanel from './TeamAssignmentPanel';

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
    <div className="bg-gradient-to-br from-slate-800/90 to-slate-900/90 rounded-2xl shadow-2xl border border-slate-600/50 p-8 backdrop-blur-lg">      
      {/* Team Assignment Section */}
      <div className="space-y-8">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-slate-100 mb-2">🕵️ Choose Your Role</h2>
        </div>

        {/* Team Selection Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <TeamAssignmentPanel
            team="red"
            players={getTeamPlayers('red')}
            hasSpymaster={hasSpymaster('red')}
            currentUser={currentUser}
            onJoinTeam={onJoinTeam}
          />
          
          <TeamAssignmentPanel
            team="blue"
            players={getTeamPlayers('blue')}
            hasSpymaster={hasSpymaster('blue')}
            currentUser={currentUser}
            onJoinTeam={onJoinTeam}
          />
        </div>

        {/* Start Game Button */}
        <div className="text-center pt-4">
          <button
            onClick={onStartGame}
            disabled={!canStartGame() || isCreating}
            className="bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800 disabled:from-slate-600 disabled:to-slate-700 text-white px-8 py-4 rounded-xl text-lg font-semibold transition-all duration-200 shadow-xl hover:shadow-emerald-500/25"
          >
            {isCreating ? (
              <span className="flex items-center justify-center">
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-3"></div>
                Creating Game...
              </span>
            ) : canStartGame() ? (
              '🚀 Start Codenames Game'
            ) : (
              '⏳ Waiting for Teams'
            )}
          </button>
          {!canStartGame() && !isCreating && (
            <p className="text-sm text-slate-400 mt-3">
              Need players on both teams to start
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default TeamSetup;