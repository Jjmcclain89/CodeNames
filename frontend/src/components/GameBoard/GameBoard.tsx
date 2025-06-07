import React, { useState, useEffect } from 'react';
import { CodenamesGame, GamePlayer, TeamColor, PlayerRole } from '../../types/game';
import Card from './Card';
import { gameService } from '../../services/gameService';

interface GameBoardProps {
  gameState: CodenamesGame;
  currentPlayer: GamePlayer | null;
  onCardClick: (cardId: string) => void;
  onGiveClue: (word: string, number: number) => void;
  onEndTurn: () => void;
  onStartGame: () => void;
  onJoinTeam: (team: TeamColor, role: PlayerRole) => void;
}

export const GameBoard: React.FC<GameBoardProps> = ({
  gameState,
  currentPlayer,
  onCardClick,
  onGiveClue,
  onEndTurn,
  onStartGame,
  onJoinTeam
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

  const handleGiveClue = () => {
    if (clueWord.trim() && clueNumber >= 1 && clueNumber <= 9) {
      onGiveClue(clueWord.trim(), clueNumber);
    }
  };

  const getPlayersByTeam = (team: TeamColor) => {
    return gameState.players.filter(p => p.team === team);
  };

  const hasSpymaster = (team: TeamColor) => {
    return gameState.players.some(p => p.team === team && p.role === 'spymaster');
  };

  // Get board glow effect based on current turn - ENHANCED for visibility
  const getBoardGlowEffect = () => {
    if (gameState.currentTurn === 'red') {
      return 'shadow-2xl shadow-red-400 ring-4 ring-red-400/80 shadow-red-500/70 drop-shadow-2xl';
    } else {
      return 'shadow-2xl shadow-blue-400 ring-4 ring-blue-400/80 shadow-blue-500/70 drop-shadow-2xl';
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
            {/* Banner removed for cleaner look */}
            
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
                    onClick={() => onJoinTeam('red', 'spymaster')}
                    className="w-full bg-red-500 text-white px-4 py-3 rounded-lg font-semibold hover:bg-red-600 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
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
                <div className="text-sm text-slate-300">
                  <div className="font-medium mb-2">Team Members:</div>
                  {getPlayersByTeam('red').length === 0 ? (
                    <p className="text-slate-400 italic">No players yet</p>
                  ) : (
                    getPlayersByTeam('red').map(player => (
                      <div key={player.id} className="flex justify-between items-center py-1">
                        <span>{player.username}</span>
                        <span className="text-red-400 font-medium">
                          {player.role === 'spymaster' ? '👑' : '🕵️'} {player.role}
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
                    onClick={() => onJoinTeam('blue', 'spymaster')}
                    className="w-full bg-blue-500 text-white px-4 py-3 rounded-lg font-semibold hover:bg-blue-600 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
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
                <div className="text-sm text-slate-300">
                  <div className="font-medium mb-2">Team Members:</div>
                  {getPlayersByTeam('blue').length === 0 ? (
                    <p className="text-slate-400 italic">No players yet</p>
                  ) : (
                    getPlayersByTeam('blue').map(player => (
                      <div key={player.id} className="flex justify-between items-center py-1">
                        <span>{player.username}</span>
                        <span className="text-blue-400 font-medium">
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
                      onClick={canRevealCard ? onCardClick : undefined}
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

          {canRevealCard && (
            <div className="bg-gradient-to-br from-slate-800/90 to-slate-900/90 rounded-xl shadow-xl p-4 text-center backdrop-blur-lg border border-slate-600/50">
              <p className="text-slate-200 mb-3">
                🎯 Click a card to guess ({gameState.guessesRemaining} left)
              </p>
              <button
                onClick={onEndTurn}
                className="bg-gradient-to-r from-orange-500 to-orange-600 text-white px-6 py-2 rounded-lg hover:from-orange-600 hover:to-orange-700 transition-colors font-semibold shadow-lg"
              >
                ⏭️ End Turn
              </button>
            </div>
          )}

          {!isMyTurn && currentPlayer && currentPlayer.team !== 'neutral' && (
            <div className="bg-gradient-to-br from-slate-800/90 to-slate-900/90 rounded-xl p-4 text-center max-w-md backdrop-blur-lg border border-slate-600/50">
              <p className="text-slate-300">
                ⏳ Waiting for {gameState.currentTurn === 'red' ? '🔴' : '🔵'} team...
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Side Panels */}
      {playersVisible && (
        <div className="fixed right-4 top-20 bottom-4 w-72 bg-gradient-to-br from-slate-800/95 to-slate-900/95 rounded-xl shadow-2xl border border-slate-600/50 p-4 z-40 flex flex-col backdrop-blur-xl">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-slate-100">👥 Players ({gameState.players.length})</h3>
            <button 
              onClick={() => setPlayersVisible(false)}
              className="text-slate-400 hover:text-slate-200 transition-colors"
            >
              ✕
            </button>
          </div>
          <div className="space-y-2 overflow-y-auto">
            {gameState.players.map((player) => (
              <div key={player.id} className="flex items-center justify-between p-2 bg-slate-700/50 rounded-lg">
                <div>
                  <div className="font-medium text-slate-100">{player.username}</div>
                  <div className={`text-xs ${player.team === 'red' ? 'text-red-400' : 'text-blue-400'}`}>
                    {player.team === 'red' ? '🔴' : '🔵'} {player.role === 'spymaster' ? '👑' : '🕵️'}
                  </div>
                </div>
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              </div>
            ))}
          </div>
        </div>
      )}

      {chatVisible && (
        <div className="fixed right-4 top-20 bottom-4 w-72 bg-gradient-to-br from-slate-800/95 to-slate-900/95 rounded-xl shadow-2xl border border-slate-600/50 p-4 z-40 flex flex-col backdrop-blur-xl">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-slate-100">💬 Chat</h3>
            <button 
              onClick={() => setChatVisible(false)}
              className="text-slate-400 hover:text-slate-200 transition-colors"
            >
              ✕
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto border border-slate-600 rounded-lg p-3 mb-4 bg-slate-700/30">
            <div className="space-y-2 text-sm">
              <div className="text-slate-400 text-center py-4">
                Chat functionality can be integrated here
              </div>
            </div>
          </div>

          <div className="flex space-x-2">
            <input
              type="text"
              placeholder="Type a message..."
              className="flex-1 px-3 py-2 bg-slate-700/50 border border-slate-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-violet-400 text-slate-100 placeholder-slate-400 text-sm"
            />
            <button className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200">
              Send
            </button>
          </div>
        </div>
      )}

      {infoVisible && (
        <div className="fixed right-4 top-20 w-72 bg-gradient-to-br from-slate-800/95 to-slate-900/95 rounded-xl shadow-2xl border border-slate-600/50 p-4 z-40 backdrop-blur-xl">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-amber-200">ℹ️ Game Info</h3>
            <button 
              onClick={() => setInfoVisible(false)}
              className="text-slate-400 hover:text-slate-200 transition-colors"
            >
              ✕
            </button>
          </div>
          <div className="space-y-3 text-sm">
            <div>
              <span className="text-slate-400">Game Code:</span>
              <span className="ml-2 font-mono text-amber-300">{gameState.gameCode || 'DEMO'}</span>
            </div>
            <div>
              <span className="text-slate-400">Status:</span>
              <span className="ml-2 text-emerald-400">{gameState.status}</span>
            </div>
            <div>
              <span className="text-slate-400">Current Turn:</span>
              <span className={`ml-2 ${gameState.currentTurn === 'red' ? 'text-red-400' : 'text-blue-400'}`}>
                {gameState.currentTurn === 'red' ? '🔴' : '🔵'} {gameState.currentTurn}
              </span>
            </div>
            <div className="pt-2 border-t border-slate-600">
              <div className="text-amber-200 font-medium mb-2">Team Scores:</div>
              <div className="flex justify-between items-center">
                <span className="text-red-400">🔴 Red:</span>
                <span className="text-red-300 font-medium">{stats.red.remaining} left</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-blue-400">🔵 Blue:</span>
                <span className="text-blue-300 font-medium">{stats.blue.remaining} left</span>
              </div>
            </div>
            {currentPlayer && (
              <div className="pt-2 border-t border-slate-600">
                <div className="text-amber-200 font-medium mb-2">Your Info:</div>
                <div>
                  <span className="text-slate-400">Name:</span>
                  <span className="ml-2 text-amber-300">{currentPlayer.username}</span>
                </div>
                <div>
                  <span className="text-slate-400">Team:</span>
                  <span className={`ml-2 ${currentPlayer.team === 'red' ? 'text-red-400' : 'text-blue-400'}`}>
                    {currentPlayer.team}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400">Role:</span>
                  <span className="ml-2 text-slate-300">{currentPlayer.role}</span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Game Over Modal */}
      {gameState.status === 'finished' && gameState.winner && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-8 max-w-md w-full mx-4 shadow-2xl border border-slate-600">
            <h2 className="text-4xl font-bold text-center mb-4 text-amber-100">🎉 Game Over! 🎉</h2>
            <div className={`text-3xl font-bold text-center mb-6 ${gameState.winner === 'red' ? 'text-red-400' : 'text-blue-400'}`}>
              {gameState.winner === 'red' ? '🔴' : '🔵'} {gameState.winner.charAt(0).toUpperCase() + gameState.winner.slice(1)} Team Wins!
            </div>
            <div className="flex gap-4">
              <button
                onClick={() => window.location.reload()}
                className="flex-1 bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-3 rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all duration-200 font-semibold"
              >
                🔄 New Game
              </button>
              <button
                onClick={() => gameService.resetGame()}
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