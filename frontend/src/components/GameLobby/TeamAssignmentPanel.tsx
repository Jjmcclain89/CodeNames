import React from 'react';

interface Player {
  id: string;
  username: string;
  isOnline?: boolean;
  socketId?: string;
}

interface Team {
  spymaster?: Player;
  operatives: Player[];
}

interface TeamAssignmentPanelProps {
  team: 'red' | 'blue';
  teamData?: Team;
  currentUser: any;
  onJoinTeam: (team: string, role: string) => void;
  onLeaveTeam: (team: string, role: string) => void;
}

const TeamAssignmentPanel: React.FC<TeamAssignmentPanelProps> = ({
  team,
  teamData,
  currentUser,
  onJoinTeam,
  onLeaveTeam
}) => {
  const isRed = team === 'red';
  
  // Get team data directly
  const spymaster = teamData?.spymaster;
  const operatives = teamData?.operatives || [];
  const hasSpymaster = !!spymaster;
  
  // Check if current user is already an operative on this team
  const isCurrentUserOperativeOnThisTeam = operatives.some(
    p => p.username === currentUser?.username || p.id === currentUser?.id
  );
  
  const teamConfig = {
    red: {
      emoji: '🔴',
      name: 'Red Team',
      bgGradient: 'bg-gradient-to-br from-red-900/60 to-red-800/40',
      borderColor: 'border-red-500/50',
      titleColor: 'text-red-200',
      spymasterButton: 'bg-red-700/50 hover:bg-red-600/60 border border-red-500/50',
      spymasterTakenButton: 'bg-gradient-to-r from-red-500 to-rose-600 hover:from-red-600 hover:to-rose-700',
      addOperativeButton: 'bg-red-700/50 hover:bg-red-600/60 border border-red-500/50',
      textColor: 'text-red-100',
      headerColor: 'text-red-200',
      memberBg: 'bg-gradient-to-r from-red-500 to-rose-600',
      roleColor: 'text-red-300',
      emptyColor: 'text-red-300/70'
    },
    blue: {
      emoji: '🔵',
      name: 'Blue Team',
      bgGradient: 'bg-gradient-to-br from-blue-900/60 to-blue-800/40',
      borderColor: 'border-blue-500/50',
      titleColor: 'text-blue-200',
      spymasterButton: 'bg-blue-700/50 hover:bg-blue-600/60 border border-blue-500/50',
      spymasterTakenButton: 'bg-gradient-to-r from-blue-500 to-sky-600 hover:from-blue-600 hover:to-sky-700',
      addOperativeButton: 'bg-blue-700/50 hover:bg-blue-600/60 border border-blue-500/50',
      textColor: 'text-blue-100',
      headerColor: 'text-blue-200',
      memberBg: 'bg-gradient-to-r from-blue-500 to-sky-600',
      roleColor: 'text-blue-300',
      emptyColor: 'text-blue-300/70'
    }
  };

  const config = teamConfig[team];

  return (
    <div className={`${config.bgGradient} border-2 ${config.borderColor} rounded-xl p-4 backdrop-blur-sm`}>
      <h3 className={`text-2xl font-semibold ${config.titleColor} mb-4 text-center flex items-center justify-center`}>
        {config.emoji} {config.name}
      </h3>
      
      {/* Spymaster Section */}
      <div className="mb-4">
        <div className={`font-medium mb-3 ${config.headerColor} text-center`}>
          🕵️ Spymaster:
        </div>
        
        <div className="flex justify-center">
          {hasSpymaster ? (
            <div className={`w-48 flex items-center ${config.spymasterTakenButton} rounded-lg overflow-hidden`}>
              <div className="flex rounded-md items-center justify-center w-12 h-8 bg-transparent">
                <span className="text-sm">🕵️</span>
              </div>
              <div className="flex-1 flex pl-4 py-2">
                <span className={config.textColor}>{spymaster?.username}</span>
              </div>
              {(spymaster?.id === currentUser?.id || spymaster?.username === currentUser?.username) && (
                <button
                  onClick={() => onLeaveTeam(team, 'spymaster')}
                  className="flex items-center justify-center w-8 h-8 text-white/70 hover:text-white hover:bg-red-500/20 rounded-r-lg transition-all duration-200"
                  title="Leave team"
                >
                  <span className="text-sm font-bold">✕</span>
                </button>
              )}
            </div>
          ) : (
            <button
              onClick={() => onJoinTeam(team, 'spymaster')}
              className={`w-48 ${config.spymasterButton} text-white px-4 py-2 rounded-lg font-medium transition-all duration-200 shadow-sm hover:shadow-md flex items-center justify-center`}
            >
              <span className="text-sm">🕵️</span>
              <span className="ml-2 text-sm">Join as Spymaster</span>
            </button>
          )}
        </div>
      </div>
      
      {/* Operatives Section */}
      <div className={`text-sm ${config.textColor}`}>
        <div className={`font-medium mb-3 ${config.headerColor}`}>
          Operatives ({operatives.length}):
        </div>
        
        <div className="space-y-2 flex flex-col items-center">
          {operatives.map((player: Player) => (
            <div key={player.id} className={`w-48 flex items-center ${config.memberBg} rounded-lg overflow-hidden`}>
              <div className="flex rounded-md items-center justify-center w-12 h-8 bg-transparent border-white/30">
                <span className="text-sm">👤</span>
              </div>
              <div className="flex-1 flex pl-4 py-2">
                <span className={config.textColor}>{player.username}</span>
              </div>
              {(player.id === currentUser?.id || player.username === currentUser?.username) && (
                <button
                  onClick={() => onLeaveTeam(team, 'operative')}
                  className="flex items-center justify-center w-8 h-8 text-white/70 hover:text-white hover:bg-red-500/20 rounded-r-lg transition-all duration-200"
                  title="Leave team"
                >
                  <span className="text-sm font-bold">✕</span>
                </button>
              )}
            </div>
          ))}
          
          {/* Add Operative Button - Only show if user is not already an operative on this team */}
          {!isCurrentUserOperativeOnThisTeam && (
            <div className="flex justify-center">
              <button
                onClick={() => onJoinTeam(team, 'operative')}
                className={`w-48 ${config.addOperativeButton} text-white px-4 py-2 rounded-lg font-medium transition-all duration-200 shadow-sm hover:shadow-md flex items-center justify-center`}
              >
                <span className="text-sm">➕👤</span>
                <span className="ml-2 text-sm">Join as Operative</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TeamAssignmentPanel;
