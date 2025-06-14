import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CodenamesGame, GamePlayer, TeamColor, PlayerRole, isSoloMode, getSoloTeam, getAllPlayers } from '../../shared/types/game';
import Card from './Card';
import { gameService } from '../../services/gameService';
import { socketService } from '../../services/socketService';

interface GameBoardProps {
  gameState: CodenamesGame;
  currentPlayer: GamePlayer | null;
  isConnected: boolean;
}

export const GameBoard: React.FC<GameBoardProps> = ({
  gameState,
  currentPlayer,
  isConnected
}) => {
  const navigate = useNavigate();
  const [clueWord, setClueWord] = useState('');
  const [clueNumber, setClueNumber] = useState(1);
  const [selectedCardId, setSelectedCardId] = useState<string | null>(null);
  const [showGameOverModal, setShowGameOverModal] = useState(true);
  const [actionDialog, setActionDialog] = useState<{
    show: boolean;
    message: string;
    fadeOut: boolean;
  }>({ show: false, message: '', fadeOut: false });

  // Reset clue input when turn changes or clue is given
  useEffect(() => {
    if (gameState.currentClue) {
      setClueWord('');
      setClueNumber(1);
    }
  }, [gameState.currentClue]);

  // Socket listeners for tracking actions
  useEffect(() => {
    if (!socketService.socket) return;
    
    const handleClueGiven = (clue: any) => {
      console.log('💡 Clue given:', clue);
      
      // Find the actual spymaster username from current game state
      const currentTurnSpymaster = gameState.currentTurn === 'red' 
        ? gameState.redTeam?.spymaster 
        : gameState.blueTeam?.spymaster;
      const spymasterName = currentTurnSpymaster?.username || 'Spymaster';
      
      // Show dialog notification
      showActionDialog(`${spymasterName} has given the clue ${clue.word} (${clue.number})`);
    };
    
    const handleCardRevealed = (data: any) => {
      console.log('🎯 Card revealed:', data);
      
      // Try to find the username from the current player or socket data
      let username = 'Player';
      if (data.username && !data.username.includes('user_')) {
        username = data.username;
      } else if (currentPlayer?.username) {
        username = currentPlayer.username;
      } else if (data.revealedBy && !data.revealedBy.includes('user_')) {
        username = data.revealedBy;
      }
      
      // Determine word team color
      const wordTeam = data.team || data.card?.team;
      const teamColor = wordTeam === 'red' ? 'red' : 
                       wordTeam === 'blue' ? 'blue' : 
                       wordTeam === 'assassin' ? 'the assassin' : 'neutral';
      const word = data.word || data.card?.word;
      
      // Show dialog notification
      showActionDialog(`${username} has guessed ${word}. It was a ${teamColor} word.`);
    };
    
    socketService.socket.on('game:clue-given', handleClueGiven);
    socketService.socket.on('game:card-revealed', handleCardRevealed);
    
    return () => {
      if (socketService.socket) {
        socketService.socket.off('game:clue-given', handleClueGiven);
        socketService.socket.off('game:card-revealed', handleCardRevealed);
      }
    };
  }, []);

  const stats = gameService.getTeamStats(gameState);
  const isSpymaster = currentPlayer?.role === 'spymaster';
  const isMyTurn = gameService.isPlayerTurn(gameState, currentPlayer);
  const canGiveClue = gameService.canPlayerGiveClue(gameState, currentPlayer);
  const canRevealCard = gameService.canPlayerRevealCard(gameState, currentPlayer);

  // Game action handlers
  const handleCardSelect = (cardId: string) => {
    setSelectedCardId(cardId);
  };

  const handleCardSubmit = (cardId: string) => {
    console.log('🎯 Revealing card:', cardId);
    gameService.revealCard(gameState.gameCode, cardId);
    setSelectedCardId(null);
  };

  const handleGiveClue = () => {
    if (clueWord.trim() && clueNumber >= 1 && clueNumber <= 9) {
      console.log('🎯 Giving clue:', clueWord.trim(), clueNumber);
      gameService.giveClue(gameState.gameCode, clueWord.trim(), clueNumber);
    }
  };

  const handleEndTurn = () => {
    console.log('🎯 Ending turn');
    gameService.endTurn(gameState.gameCode);
  };

  const handleStartGame = () => {
    console.log('🎯 Starting game');
    gameService.startGame();
  };

  const handleJoinTeam = (team: TeamColor, role: PlayerRole) => {
    console.log('Join team:', team, role);
    // TODO: Implement via socket
  };

  const getPlayersByTeam = (team: TeamColor) => {
    const allPlayers = getAllPlayers(gameState); return allPlayers.filter((p: any) => p.team === team);
  };

  const hasSpymaster = (team: TeamColor) => {
    const allPlayers = getAllPlayers(gameState); return allPlayers.some((p: any) => p.team === team && p.role === 'spymaster');
  };

  // Get board glow effect based on current turn
  const getBoardGlowEffect = () => {
    if (gameState.currentTurn === 'red') {
      return 'shadow-2xl shadow-red-400 ring-4 ring-red-400/80 shadow-red-500/70 drop-shadow-2xl';
    } else {
      return 'shadow-2xl shadow-blue-400 ring-4 ring-blue-400/80 shadow-blue-500/70 drop-shadow-2xl';
    }
  };


  // Show action dialog with auto-fade
  const showActionDialog = (message: string) => {
    setActionDialog({ show: true, message, fadeOut: false });
    
    // Start fade out after 2 seconds
    setTimeout(() => {
      setActionDialog(prev => ({ ...prev, fadeOut: true }));
    }, 2000);
    
    // Hide completely after fade animation
    setTimeout(() => {
      setActionDialog({ show: false, message: '', fadeOut: false });
    }, 2500);
  };

  // Get current game state message for info bar
  const getInfoMessage = () => {
    const currentTurnSpymaster = gameState.currentTurn === 'red' 
      ? gameState.redTeam?.spymaster 
      : gameState.blueTeam?.spymaster;
    const spymasterName = currentTurnSpymaster?.username || 'Spymaster';
    const isActiveSpymaster = currentPlayer && currentTurnSpymaster && 
      (currentPlayer.id === currentTurnSpymaster.id || currentPlayer.username === currentTurnSpymaster.username);

    // Handle solo mode
    if (gameState.isSoloMode) {
      const soloTeamSpymaster = gameState.soloTeam === 'red' 
        ? gameState.redTeam?.spymaster 
        : gameState.blueTeam?.spymaster;
      const isActiveSpymasterSolo = currentPlayer && soloTeamSpymaster && 
        (currentPlayer.id === soloTeamSpymaster.id || currentPlayer.username === soloTeamSpymaster.username);
      
      if (gameState.currentClue) {
        return (
          <span className="text-lg font-bold text-violet-100 drop-shadow-lg">
            Clue: <span className="text-xl font-extrabold text-amber-300">{gameState.currentClue.word} ({gameState.currentClue.number})</span> - Please make a guess
          </span>
        );
      } else {
        if (isActiveSpymasterSolo) {
          return (
            <span className="text-lg font-bold text-violet-100 drop-shadow-lg">
              💡 It's your turn to give a clue!
            </span>
          );
        } else {
          return (
            <span className="text-lg font-bold text-violet-100 drop-shadow-lg">
              ⏳ Waiting for {soloTeamSpymaster?.username || 'Spymaster'} to give a clue
            </span>
          );
        }
      }
    } else {
      // Classic multiplayer mode
      if (gameState.currentClue) {
        return (
          <span className="text-lg font-bold text-violet-100 drop-shadow-lg">
            Clue: <span className="text-xl font-extrabold text-amber-300">{gameState.currentClue.word} ({gameState.currentClue.number})</span> - Please make a guess
          </span>
        );
      } else {
        if (isActiveSpymaster) {
          return (
            <span className="text-lg font-bold text-violet-100 drop-shadow-lg">
              💡 It's your turn to give a clue!
            </span>
          );
        } else {
          return (
            <span className="text-lg font-bold text-violet-100 drop-shadow-lg">
              ⏳ Waiting for {spymasterName} to give a clue
            </span>
          );
        }
      }
    }
  };

  if (gameState.status === 'waiting') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-900 p-4 relative">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-blue-400 via-transparent to-transparent"></div>
          <div className="absolute inset-0 bg-[linear-gradient(45deg,_transparent_25%,_rgba(255,255,255,0.02)_25%,_rgba(255,255,255,0.02)_50%,_transparent_50%,_transparent_75%,_rgba(255,255,255,0.02)_75%)] bg-[length:60px_60px]"></div>
        </div>
        
        <div className="flex flex-col items-center justify-center min-h-screen">
          <div className="bg-gradient-to-br from-slate-800/90 to-slate-900/90 rounded-xl shadow-2xl border border-slate-600/50 p-8 max-w-4xl w-full backdrop-blur-lg relative z-10">
            
            {/* Current Player Status */}
            {currentPlayer && (
              <div className="text-center mb-6 p-4 bg-slate-700/50 rounded-lg border border-slate-600/50">
                <p className="text-lg text-slate-200">
                  Welcome, <span className="font-semibold text-amber-200">{currentPlayer.username}</span>!
                </p>
                {currentPlayer.team !== 'neutral' && (
                  <p className="text-sm text-slate-300">
                    You are on the{' '}
                    <span className={`font-semibold ${currentPlayer.team === 'red' ? 'text-red-400' : 'text-blue-400'}`}>
                      {currentPlayer.team}
                    </span>{' '}
                    team as a <span className="font-semibold">{currentPlayer.role}</span>
                  </p>
                )}
              </div>
            )}
            
            {/* Team Selection */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              {/* Red Team */}
              <div className="bg-gradient-to-br from-red-900/60 to-red-800/40 border-2 border-red-500/50 rounded-lg p-6 backdrop-blur-sm">
                <h3 className="text-2xl font-semibold text-red-200 mb-4 text-center">
                  🔴 Red Team
                </h3>
                <div className="space-y-3 mb-4">
                  <button
                    onClick={() => handleJoinTeam('red', 'spymaster')}
                    className="w-full bg-red-500 text-white px-4 py-3 rounded-lg font-semibold hover:bg-red-600 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
                    disabled={hasSpymaster('red')}
                  >
                    {hasSpymaster('red') ? '📻 Spymaster Taken' : '📻 Join as Spymaster'}
                  </button>
                  <button
                    onClick={() => handleJoinTeam('red', 'operative')}
                    className="w-full bg-red-400 text-white px-4 py-3 rounded-lg font-semibold hover:bg-red-500 transition-colors"
                  >
                    🕵️ Join as Operative
                  </button>
                </div>
                <div className="text-sm text-slate-300">
                  <div className="font-medium mb-2">Team Members:</div>
                  {getPlayersByTeam('red').length === 0 ? (
                    <p className="text-slate-400 italic">No players yet</p>
                  ) : (
                    getPlayersByTeam('red').map(player => (
                      <div key={player.id} className="flex justify-between items-center py-1">
                        <span>{player.username}</span>
                        <span className="text-red-400 font-medium">
                          {player.role === 'spymaster' ? '📻' : '🕵️'} {player.role}
                        </span>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Blue Team */}
              <div className="bg-gradient-to-br from-blue-900/60 to-blue-800/40 border-2 border-blue-500/50 rounded-lg p-6 backdrop-blur-sm">
                <h3 className="text-2xl font-semibold text-blue-200 mb-4 text-center">
                  🔵 Blue Team
                </h3>
                <div className="space-y-3 mb-4">
                  <button
                    onClick={() => handleJoinTeam('blue', 'spymaster')}
                    className="w-full bg-blue-500 text-white px-4 py-3 rounded-lg font-semibold hover:bg-blue-600 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
                    disabled={hasSpymaster('blue')}
                  >
                    {hasSpymaster('blue') ? '📻 Spymaster Taken' : '📻 Join as Spymaster'}
                  </button>
                  <button
                    onClick={() => handleJoinTeam('blue', 'operative')}
                    className="w-full bg-blue-400 text-white px-4 py-3 rounded-lg font-semibold hover:bg-blue-500 transition-colors"
                  >
                    🕵️ Join as Operative
                  </button>
                </div>
                <div className="text-sm text-slate-300">
                  <div className="font-medium mb-2">Team Members:</div>
                  {getPlayersByTeam('blue').length === 0 ? (
                    <p className="text-slate-400 italic">No players yet</p>
                  ) : (
                    getPlayersByTeam('blue').map(player => (
                      <div key={player.id} className="flex justify-between items-center py-1">
                        <span>{player.username}</span>
                        <span className="text-blue-400 font-medium">
                          {player.role === 'spymaster' ? '📻' : '🕵️'} {player.role}
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
                onClick={handleStartGame}
                className="bg-gradient-to-r from-emerald-600 to-emerald-700 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:from-emerald-700 hover:to-emerald-800 transition-all duration-200 disabled:from-slate-600 disabled:to-slate-700 disabled:cursor-not-allowed shadow-lg"
                disabled={getAllPlayers(gameState).length === 0}
              >
                🚀 Start Game
              </button>
              <p className="text-sm text-slate-400 mt-3">
                Need players on both teams to start
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-900 overflow-hidden relative">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-blue-400 via-transparent to-transparent"></div>
        <div className="absolute inset-0 bg-[linear-gradient(45deg,_transparent_25%,_rgba(255,255,255,0.02)_25%,_rgba(255,255,255,0.02)_50%,_transparent_50%,_transparent_75%,_rgba(255,255,255,0.02)_75%)] bg-[length:60px_60px]"></div>
      </div>

      {/* Centered Layout Container */}
      <div className="min-h-screen flex justify-center p-4">
        <div className="flex flex-col items-center space-y-4 w-full sm:max-w-4xl">
          
          {/* General Info Display */}
          <div className="px-6 py-3 bg-gradient-to-r from-violet-900/90 to-indigo-900/90 border border-violet-500/50 rounded-xl shadow-xl backdrop-blur-lg">
            <div className="text-center">
              {getInfoMessage()}
              {gameState.currentClue && gameState.guessesRemaining > 0 && (
                <div className="mt-2 text-sm text-violet-300">
                  {gameState.guessesRemaining} guess{gameState.guessesRemaining !== 1 ? 'es' : ''} remaining
                </div>
              )}
            </div>
          </div>

          {/* THE MAIN 5x5 GAME BOARD with Turn-Based Glow Effect */}
          <div className={`relative w-full bg-gradient-to-br from-slate-800/90 via-slate-700/70 to-slate-800/90 rounded-2xl p-2 sm:p-4 md:p-6 transition-all duration-700 ${getBoardGlowEffect()} border-2 border-slate-600/50 backdrop-blur-lg`}>
            
            {/* Action Dialog */}
            {actionDialog.show && (
              <div className={`absolute inset-0 flex items-center justify-center z-50 transition-all duration-500 ${
                actionDialog.fadeOut ? 'opacity-0 scale-95 rotate-1' : 'opacity-100 scale-100 -rotate-1'
              }`}>
                <div className="bg-gradient-to-br from-violet-900/70 to-indigo-900/70 border-2 border-violet-400/40 rounded-2xl px-8 py-6 shadow-2xl backdrop-blur-md max-w-lg mx-4 transform -rotate-1 hover:rotate-0 transition-transform duration-300">
                  <div className="text-center text-lg font-bold text-violet-50 drop-shadow-lg leading-relaxed">
                    {actionDialog.message}
                  </div>
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-violet-400/60 rounded-full shadow-lg"></div>
                  <div className="absolute -bottom-1 -left-1 w-2 h-2 bg-indigo-400/60 rounded-full shadow-lg"></div>
                </div>
              </div>
            )}
            {/* Board Game Texture with Turn Indicator */}
            <div className="absolute inset-0 rounded-2xl bg-[radial-gradient(circle_at_30%_20%,_rgba(139,69,19,0.1)_0%,_transparent_50%)] pointer-events-none"></div>
            <div className="absolute inset-0 rounded-2xl bg-[linear-gradient(45deg,_transparent_30%,_rgba(160,82,45,0.05)_30%,_rgba(160,82,45,0.05)_70%,_transparent_70%)] bg-[length:20px_20px] pointer-events-none"></div>
            {/* Turn Indicator Overlay */}
            <div className={`absolute inset-0 rounded-2xl pointer-events-none transition-all duration-700 ${
              gameState.currentTurn === 'red' 
                ? 'bg-gradient-to-br from-red-500/10 via-transparent to-red-500/5' 
                : 'bg-gradient-to-br from-blue-500/10 via-transparent to-blue-500/5'
            }`}></div>
            <div className="relative z-10">
              <div className="grid grid-cols-5 gap-1 sm:gap-2 md:gap-3 w-full">
                {gameState.board && Array.isArray(gameState.board) ? gameState.board
                  .sort((a, b) => a.position - b.position)
                  .map((card) => (
                    <Card
                      key={card.id}
                      card={card}
                      isSpymaster={isSpymaster}
                      onSelect={canRevealCard ? handleCardSelect : undefined}
                      onSubmit={canRevealCard ? handleCardSubmit : undefined}
                      disabled={!canRevealCard}
                      showSubmit={selectedCardId === card.id}
                    />
                  )) : (
                    <div className="text-center text-white">
                      <div className="text-xl mb-2">⚠️ Board not loaded</div>
                      <div className="text-sm opacity-75">Game board data is missing</div>
                    </div>
                  )}
              </div>
            </div>
          </div>

          {/* Team Scores and Game Status */}
          <div className="mb-4 flex flex-wrap justify-center gap-2 max-w-2xl mx-auto">
            {/* Red Team Score */}
            <div className="bg-gradient-to-br from-red-600/80 to-red-700/80 border border-red-400/50 rounded-lg px-4 py-2 backdrop-blur-sm shadow-lg">
              <div className="text-xl font-bold text-white text-center">
                {gameState.board ? gameState.board.filter(card => card.team === 'red' && !card.isRevealed).length : 0}
              </div>
              <div className="text-xs text-red-100 text-center whitespace-nowrap">
                Red Words Remaining
              </div>
            </div>

            {/* Blue Team Score */}
            <div className="bg-gradient-to-br from-blue-600/80 to-blue-700/80 border border-blue-400/50 rounded-lg px-4 py-2 backdrop-blur-sm shadow-lg">
              <div className="text-xl font-bold text-white text-center">
                {gameState.board ? gameState.board.filter(card => card.team === 'blue' && !card.isRevealed).length : 0}
              </div>
              <div className="text-xs text-blue-100 text-center whitespace-nowrap">
                Blue Words Remaining
              </div>
            </div>

            {/* Current Turn Guesses (Classic Mode) */}
            {!gameState.isSoloMode && gameState.currentClue && gameState.guessesRemaining > 0 && (
              <div className="bg-gradient-to-br from-slate-600/80 to-slate-700/80 border border-slate-400/50 rounded-lg px-4 py-2 backdrop-blur-sm shadow-lg">
                <div className="text-xl font-bold text-white text-center">
                  {gameState.guessesRemaining}
                </div>
                <div className="text-xs text-slate-200 text-center whitespace-nowrap">
                  Guesses Left
                </div>
              </div>
            )}

            {/* Solo Mode: Clues Remaining */}
            {gameState.isSoloMode && (
              <div className="bg-gradient-to-br from-slate-600/80 to-slate-700/80 border border-slate-400/50 rounded-lg px-4 py-2 backdrop-blur-sm shadow-lg">
                <div className="text-xl font-bold text-white text-center">
                  {gameState.soloCluesRemaining || 0}
                </div>
                <div className="text-xs text-slate-200 text-center whitespace-nowrap">
                  Clues Remaining
                </div>
              </div>
            )}

            {/* Solo Mode: Turn Guesses */}
            {gameState.isSoloMode && gameState.currentClue && gameState.soloTurnGuessesRemaining && gameState.soloTurnGuessesRemaining > 0 && (
              <div className="bg-gradient-to-br from-slate-600/80 to-slate-700/80 border border-slate-400/50 rounded-lg px-4 py-2 backdrop-blur-sm shadow-lg">
                <div className="text-xl font-bold text-white text-center">
                  {gameState.soloTurnGuessesRemaining}
                </div>
                <div className="text-xs text-slate-200 text-center whitespace-nowrap">
                  Guesses Remaining
                </div>
              </div>
            )}
          </div>

          {/* Controls Below Board */}
          {canGiveClue && (
            <div className="bg-gradient-to-br from-slate-800/90 to-slate-900/90 rounded-xl shadow-xl p-4 w-full max-w-2xl backdrop-blur-lg border border-slate-600/50">
              <div className="flex items-end space-x-3">
                <div className="flex-1">
                  <input
                    type="text"
                    value={clueWord}
                    onChange={(e) => setClueWord(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-700/50 border border-slate-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-violet-400 text-slate-100 placeholder-slate-400"
                    placeholder="Clue word..."
                    required
                  />
                </div>
                <div className="flex items-center">
                  <button
                    type="button"
                    onClick={() => setClueNumber(Math.max(1, clueNumber - 1))}
                    className="px-2 py-2 bg-slate-600/50 border border-slate-500 rounded-l-lg hover:bg-slate-500/50 focus:outline-none focus:ring-2 focus:ring-violet-400 text-slate-100 text-sm font-bold"
                  >
                    −
                  </button>
                  <input
                    type="number"
                    min="1"
                    max="9"
                    value={clueNumber}
                    onChange={(e) => setClueNumber(parseInt(e.target.value) || 1)}
                    className="w-12 px-2 py-2 bg-slate-700/50 border-t border-b border-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-400 text-slate-100 text-center"
                  />
                  <button
                    type="button"
                    onClick={() => setClueNumber(Math.min(9, clueNumber + 1))}
                    className="px-2 py-2 bg-slate-600/50 border border-slate-500 rounded-r-lg hover:bg-slate-500/50 focus:outline-none focus:ring-2 focus:ring-violet-400 text-slate-100 text-sm font-bold"
                  >
                    +
                  </button>
                </div>
                <button
                  onClick={handleGiveClue}
                  className="bg-gradient-to-r from-emerald-600 to-emerald-700 text-white px-6 py-2 rounded-lg hover:from-emerald-700 hover:to-emerald-800 transition-all duration-200 font-semibold shadow-lg"
                >
                  Give Clue
                </button>
              </div>
            </div>
          )}

          {/* Solo Mode Controls */}
          {gameState.isSoloMode && canRevealCard && (
            <div className="bg-gradient-to-br from-slate-800/90 to-slate-900/90 rounded-xl shadow-xl p-4 text-center backdrop-blur-lg border border-slate-600/50">
              <p className="text-slate-200 mb-3">
                🎯 Click a card to reveal it ({gameState.soloTurnGuessesRemaining || 0} guesses this turn, {gameState.soloCluesRemaining || 0} clues left)
              </p>
              <div className="text-sm text-slate-400 mb-3">
                <span className="text-emerald-400">✅ Your team: No penalty</span> • 
                <span className="text-yellow-400"> ⚪ Neutral: End turn</span> • 
                <span className="text-red-400"> ❌ Enemy: End turn + lose clue</span> • 
                <span className="text-red-600"> 💀 Assassin: Game over</span>
              </div>
            </div>
          )}
          
          {/* Classic Mode Controls */}
          {!gameState.isSoloMode && canRevealCard && (
            <div className="bg-gradient-to-br from-slate-800/90 to-slate-900/90 rounded-xl shadow-xl p-4 text-center backdrop-blur-lg border border-slate-600/50">
              <p className="text-slate-200 mb-3">
                🎯 Click a card to guess ({gameState.guessesRemaining} left)
              </p>
              <button
                onClick={handleEndTurn}
                className="bg-gradient-to-r from-orange-500 to-orange-600 text-white px-6 py-2 rounded-lg hover:from-orange-600 hover:to-orange-700 transition-colors font-semibold shadow-lg"
              >
                ⏭️ End Turn
              </button>
            </div>
          )}

          {!gameState.isSoloMode && !isMyTurn && currentPlayer && currentPlayer.team !== 'neutral' && (
            <div className="bg-gradient-to-br from-slate-800/90 to-slate-900/90 rounded-xl p-4 text-center max-w-md backdrop-blur-lg border border-slate-600/50">
              <p className="text-slate-300">
                ⏳ Waiting for {gameState.currentTurn === 'red' ? '🔴' : '🔵'} team...
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Game Over Modal */}
      {gameState.status === 'finished' && gameState.winner && showGameOverModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-8 max-w-md w-full mx-4 shadow-2xl border border-slate-600">
            {gameState.isSoloMode ? (
              // Solo mode results
              gameState.winner === gameState.soloTeam ? (
                <>
                  <h2 className="text-4xl font-bold text-center mb-4 text-emerald-100">🎉 Victory! 🎉</h2>
                  <div className="text-2xl font-bold text-center mb-6 text-emerald-400">
                    You found all your team's words!
                  </div>
                </>
              ) : gameState.winner === 'assassin' ? (
                <>
                  <h2 className="text-4xl font-bold text-center mb-4 text-red-100">💀 Game Over 💀</h2>
                  <div className="text-2xl font-bold text-center mb-6 text-red-400">
                    You hit the assassin!
                  </div>
                </>
              ) : (
                <>
                  <h2 className="text-4xl font-bold text-center mb-4 text-yellow-100">😔 Out of Clues 😔</h2>
                  <div className="text-2xl font-bold text-center mb-6 text-yellow-400">
                    You ran out of clues!
                  </div>
                </>
              )
            ) : (
              // Classic mode results
              <>
                <h2 className="text-4xl font-bold text-center mb-4 text-amber-100">🎉 Game Over! 🎉</h2>
                <div className={`text-3xl font-bold text-center mb-6 ${gameState.winner === 'red' ? 'text-red-400' : 'text-blue-400'}`}>
                  {gameState.winner === 'red' ? '🔴' : '🔵'} {gameState.winner.charAt(0).toUpperCase() + gameState.winner.slice(1)} Team Wins!
                </div>
              </>
            )}
            <div className="flex gap-4">
              <button
                onClick={() => setShowGameOverModal(false)}
                className="flex-1 bg-gradient-to-r from-slate-600 to-slate-700 text-white px-6 py-3 rounded-lg hover:from-slate-700 hover:to-slate-800 transition-all duration-200 font-semibold"
              >
                👁️ Back to Board
              </button>
              <button
                onClick={() => navigate('/')}
                className="flex-1 bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-3 rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all duration-200 font-semibold"
              >
                🏠 Go to Homepage
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GameBoard;