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
}

const TeamAssignmentPanel: React.FC<TeamAssignmentPanelProps> = ({
  team,
  teamData,
  currentUser,
  onJoinTeam
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
      spymasterButton: 'bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800',
      spymasterTakenButton: 'bg-gradient-to-r from-red-800/60 to-red-900/60 border border-red-500/30',
      addOperativeButton: 'bg-red-700/50 hover:bg-red-600/60 border border-red-500/50',
      textColor: 'text-red-100',
      headerColor: 'text-red-200',
      memberBg: 'bg-red-800/30',
      roleColor: 'text-red-300',
      emptyColor: 'text-red-300/70'
    },
    blue: {
      emoji: '🔵',
      name: 'Blue Team',
      bgGradient: 'bg-gradient-to-br from-blue-900/60 to-blue-800/40',
      borderColor: 'border-blue-500/50',
      titleColor: 'text-blue-200',
      spymasterButton: 'bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800',
      spymasterTakenButton: 'bg-gradient-to-r from-blue-800/60 to-blue-900/60 border border-blue-500/30',
      addOperativeButton: 'bg-blue-700/50 hover:bg-blue-600/60 border border-blue-500/50',
      textColor: 'text-blue-100',
      headerColor: 'text-blue-200',
      memberBg: 'bg-blue-800/30',
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
      <div className="mb-4 flex justify-center">
        <button
          onClick={() => onJoinTeam(team, 'spymaster')}
          className={`w-48 ${hasSpymaster ? config.spymasterTakenButton : config.spymasterButton} disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg font-medium transition-all duration-200 shadow-sm hover:shadow-md`}
          disabled={hasSpymaster}
        >
          {hasSpymaster ? (
            <span className="flex items-center justify-center">
              🕵️ Spymaster: <span className="ml-2 font-bold">{spymaster?.username}</span>
            </span>
          ) : (
            '🕵️ Join as Spymaster'
          )}
        </button>
      </div>
      
      {/* Operatives Section */}
      <div className={`text-sm ${config.textColor}`}>
        <div className={`font-medium mb-3 ${config.headerColor}`}>
          Operatives ({operatives.length}):
        </div>
        
        <div className="space-y-2 flex flex-col items-center">
          {operatives.map((player: Player) => (
            <div key={player.id} className={`w-48 flex items-center justify-center py-2 px-3 ${config.memberBg} rounded-lg`}>
              <span className="text-sm mr-2">👤</span>
              <span className={config.textColor}>{player.username}</span>
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
        
        {operatives.length === 0 && !isCurrentUserOperativeOnThisTeam && (
          <p className={`${config.emptyColor} italic text-center py-2 text-xs`}>
            No operatives yet - click ➕👤 to join!
          </p>
        )}
        
        {operatives.length === 0 && isCurrentUserOperativeOnThisTeam && (
          <p className={`${config.emptyColor} italic text-center py-2 text-xs`}>
            No other operatives on this team yet
          </p>
        )}
      </div>
    </div>
  );
};

export default TeamAssignmentPanel;
