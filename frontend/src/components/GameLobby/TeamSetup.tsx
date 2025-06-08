import React from 'react';
import TeamAssignmentPanel from './TeamAssignmentPanel';

interface Player {
  id: string;
  username: string;
  isOnline: boolean;
  socketId: string;
}

interface Team {
  spymaster?: Player;
  operatives: Player[];
}

interface GameState {
  id: string;
  gameCode: string;
  status: string;
  redTeam?: Team;
  blueTeam?: Team;
}

interface TeamSetupProps {
  lobbyId: string;
  gameState: GameState | null;
  currentUser: any;
  isConnected: boolean;
  isCreating: boolean;
  onJoinTeam: (team: string, role: string) => void;
  onStartGame: () => void;
  canStartGame: () => boolean;
}

const TeamSetup: React.FC<TeamSetupProps> = ({
  lobbyId,
  gameState,
  currentUser,
  isConnected,
  isCreating,
  onJoinTeam,
  onStartGame,
  canStartGame
}) => {
  // Helper function to get current user's team info for display purposes
  const getCurrentUserPlayer = () => {
    if (!gameState || !currentUser) return null;
    
    // Check red team
    if (gameState.redTeam) {
      if (gameState.redTeam.spymaster?.id === currentUser.id || 
          gameState.redTeam.spymaster?.username === currentUser.username) {
        return { ...gameState.redTeam.spymaster, team: 'red', role: 'spymaster' };
      }
      const redOperative = gameState.redTeam.operatives.find(p => 
        p.id === currentUser.id || p.username === currentUser.username
      );
      if (redOperative) {
        return { ...redOperative, team: 'red', role: 'operative' };
      }
    }
    
    // Check blue team
    if (gameState.blueTeam) {
      if (gameState.blueTeam.spymaster?.id === currentUser.id || 
          gameState.blueTeam.spymaster?.username === currentUser.username) {
        return { ...gameState.blueTeam.spymaster, team: 'blue', role: 'spymaster' };
      }
      const blueOperative = gameState.blueTeam.operatives.find(p => 
        p.id === currentUser.id || p.username === currentUser.username
      );
      if (blueOperative) {
        return { ...blueOperative, team: 'blue', role: 'operative' };
      }
    }
    
    return null;
  };

  const userPlayer = getCurrentUserPlayer();

  return (
    <div className="bg-gradient-to-br from-slate-800/90 to-slate-900/90 rounded-2xl shadow-2xl border border-slate-600/50 p-8 backdrop-blur-lg">      
      {/* Team Assignment Section */}
      <div className="space-y-8">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-slate-100 mb-2">🕵️ Choose Your Role</h2>
        </div>

        {/* Team Selection Grid - Pass team objects directly */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <TeamAssignmentPanel
            team="red"
            teamData={gameState?.redTeam}
            currentUser={currentUser}
            onJoinTeam={onJoinTeam}
          />
          
          <TeamAssignmentPanel
            team="blue"
            teamData={gameState?.blueTeam}
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
              Need at least one valid team (spymaster + operatives)
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default TeamSetup;
