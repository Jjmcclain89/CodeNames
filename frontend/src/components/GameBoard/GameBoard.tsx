import React, { useState, useEffect } from 'react';
import { CodenamesGame, GamePlayer, TeamColor, PlayerRole, isSoloMode, getSoloTeam } from '../../types/game';
import Card from './Card';
import { gameService } from '../../services/gameService';

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
  const [clueWord, setClueWord] = useState('');
  const [clueNumber, setClueNumber] = useState(1);
  const [chatVisible, setChatVisible] = useState(false);
  const [playersVisible, setPlayersVisible] = useState(false);
  const [infoVisible, setInfoVisible] = useState(false);
  const [settingsVisible, setSettingsVisible] = useState(false);

  // Reset clue input when turn changes or clue is given
  useEffect(() => {
    if (gameState.currentClue) {
      setClueWord('');
      setClueNumber(1);
    }
  }, [gameState.currentClue]);

  const stats = gameService.getTeamStats(gameState);
  const isSpymaster = currentPlayer?.role === 'spymaster';
  const isMyTurn = gameService.isPlayerTurn(gameState, currentPlayer);
  const canGiveClue = gameService.canPlayerGiveClue(gameState, currentPlayer);
  const canRevealCard = gameService.canPlayerRevealCard(gameState, currentPlayer);

  // Game action handlers
  const handleCardClick = (cardId: string) => {
    console.log('🎯 Revealing card:', cardId);
    gameService.revealCard(gameState.gameCode, cardId);
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
    return gameState.players.filter(p => p.team === team);
  };

  const hasSpymaster = (team: TeamColor) => {
    return gameState.players.some(p => p.team === team && p.role === 'spymaster');
  };

  // Get board glow effect based on current turn and mode
  const getBoardGlowEffect = () => {
    if (gameState.isSoloMode) {
      // Solo mode - use team color
      if (gameState.soloTeam === 'red') {
        return 'shadow-2xl shadow-red-400 ring-4 ring-red-400/80 shadow-red-500/70 drop-shadow-2xl';
      } else {
        return 'shadow-2xl shadow-blue-400 ring-4 ring-blue-400/80 shadow-blue-500/70 drop-shadow-2xl';
      }
    } else {
      // Classic mode - use current turn
      if (gameState.currentTurn === 'red') {
        return 'shadow-2xl shadow-red-400 ring-4 ring-red-400/80 shadow-red-500/70 drop-shadow-2xl';
      } else {
        return 'shadow-2xl shadow-blue-400 ring-4 ring-blue-400/80 shadow-blue-500/70 drop-shadow-2xl';
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
                disabled={gameState.players.length === 0}
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
        <div className="flex flex-col items-center space-y-4 max-w-4xl w-full">
          
          {/* Icons positioned above the game board */}
          <div className="flex mb-2">
            <div className="flex space-x-2">
              <button
                onClick={() => setChatVisible(!chatVisible)}
                className={`w-10 h-10 rounded-lg shadow-lg border transition-all duration-200 flex items-center justify-center text-sm backdrop-blur-sm ${
                  chatVisible 
                    ? 'bg-gradient-to-br from-emerald-600 to-emerald-700 text-white border-emerald-400/50' 
                    : 'bg-gradient-to-br from-slate-700/80 to-slate-800/80 text-slate-200 border-slate-500/50 hover:from-slate-600/80 hover:to-slate-700/80'
                }`}
                title="Chat"
              >
                💬
              </button>
              <button
                onClick={() => setPlayersVisible(!playersVisible)}
                className={`w-10 h-10 rounded-lg shadow-lg border transition-all duration-200 flex items-center justify-center text-sm backdrop-blur-sm ${
                  playersVisible 
                    ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white border-blue-400/50' 
                    : 'bg-gradient-to-br from-slate-700/80 to-slate-800/80 text-slate-200 border-slate-500/50 hover:from-slate-600/80 hover:to-slate-700/80'
                }`}
                title="Players"
              >
                👥
              </button>
              <button
                onClick={() => setInfoVisible(!infoVisible)}
                className={`w-10 h-10 rounded-lg shadow-lg border transition-all duration-200 flex items-center justify-center text-sm backdrop-blur-sm ${
                  infoVisible 
                    ? 'bg-gradient-to-br from-amber-600 to-amber-700 text-white border-amber-400/50' 
                    : 'bg-gradient-to-br from-slate-700/80 to-slate-800/80 text-slate-200 border-slate-500/50 hover:from-slate-600/80 hover:to-slate-700/80'
                }`}
                title="Info"
              >
                ℹ️
              </button>
              <button
                onClick={() => setSettingsVisible(!settingsVisible)}
                className="w-10 h-10 bg-gradient-to-br from-slate-700/80 to-slate-800/80 rounded-lg shadow-lg border border-slate-600/50 flex items-center justify-center hover:from-slate-600/80 hover:to-slate-700/80 transition-all duration-200 backdrop-blur-sm relative"
                title="Settings"
              >
                <span className="text-slate-200 text-sm">⚙️</span>
                
                {/* Settings Dropdown */}
                {settingsVisible && (
                  <div className="absolute top-12 right-0 bg-gradient-to-br from-slate-800/95 to-slate-900/95 rounded-lg shadow-2xl border border-slate-600/50 p-3 min-w-32 backdrop-blur-lg z-60">
                    <button
                      onClick={() => window.location.href = '/'}
                      className="w-full bg-slate-700 hover:bg-slate-600 text-slate-200 px-3 py-2 rounded-lg text-sm font-medium transition-colors text-left"
                    >
                      🏠 Logout
                    </button>
                  </div>
                )}
              </button>
            </div>
          </div>
          
          {/* Current Clue Display */}
          {gameState.currentClue && (
            <div className="px-6 py-3 bg-gradient-to-r from-violet-900/90 to-indigo-900/90 border border-violet-500/50 rounded-xl shadow-xl backdrop-blur-lg">
              <span className="text-lg font-bold text-violet-100 drop-shadow-lg">
                💡 {gameState.currentClue.word} ({gameState.currentClue.number})
              </span>
              {gameState.guessesRemaining > 0 && (
                <span className="ml-3 text-sm text-violet-300">
                  {gameState.guessesRemaining} left
                </span>
              )}
            </div>
          )}

          {/* THE MAIN 5x5 GAME BOARD with Turn-Based Glow Effect */}
          <div className={`relative bg-gradient-to-br from-slate-800/90 via-slate-700/70 to-slate-800/90 rounded-2xl p-6 transition-all duration-700 ${getBoardGlowEffect()} border-2 border-slate-600/50 backdrop-blur-lg`}>
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
              <div className="grid grid-cols-5 gap-3">
                {gameState.board && Array.isArray(gameState.board) ? gameState.board
                  .sort((a, b) => a.position - b.position)
                  .map((card) => (
                    <Card
                      key={card.id}
                      card={card}
                      isSpymaster={isSpymaster}
                      onClick={canRevealCard ? handleCardClick : undefined}
                      disabled={!canRevealCard}
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
                <input
                  type="number"
                  min="1"
                  max="9"
                  value={clueNumber}
                  onChange={(e) => setClueNumber(parseInt(e.target.value) || 1)}
                  className="w-16 px-3 py-2 bg-slate-700/50 border border-slate-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-violet-400 text-slate-100 text-center"
                />
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
      {gameState.status === 'finished' && gameState.winner && (
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
                onClick={() => window.location.reload()}
                className="flex-1 bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-3 rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all duration-200 font-semibold"
              >
                🔄 New Game
              </button>
              <button
                onClick={() => console.log('Reset game')}
                className="flex-1 bg-gradient-to-r from-emerald-600 to-emerald-700 text-white px-6 py-3 rounded-lg hover:from-emerald-700 hover:to-emerald-800 transition-all duration-200 font-semibold"
              >
                🎮 Play Again
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GameBoard;
