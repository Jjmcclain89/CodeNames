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

  const handleGiveClue = (e: React.FormEvent) => {
    e.preventDefault();
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

  if (gameState.status === 'waiting') {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-4xl w-full">
          <h1 className="text-4xl font-bold text-center mb-8 text-gray-800">
            🕵️ Codenames 🔍
          </h1>
          {/* ✅ Enhanced Debug Info */}
          <div className="bg-gray-100 border rounded-lg p-4 mb-6 text-sm">
            <h4 className="font-semibold mb-2">🔍 Debug Info:</h4>
            <div>Game Status: <span className="font-mono">{gameState.status}</span></div>
            <div>Current Turn: <span className="font-mono">{gameState.currentTurn}</span></div>
            <div>Player Count: <span className="font-mono">{gameState.players.length}</span></div>
            <div>Current Player: <span className="font-mono">{currentPlayer?.username || 'None'}</span></div>
            <div>Current Player Team: <span className="font-mono">{currentPlayer?.team || 'None'}</span></div>
            <div>Current Player Role: <span className="font-mono">{currentPlayer?.role || 'None'}</span></div>
            <div>Is My Turn: <span className="font-mono">{isMyTurn ? 'YES' : 'NO'}</span></div>
            <div>Can Give Clue: <span className="font-mono">{canGiveClue ? 'YES' : 'NO'}</span></div>
            <div>Can Reveal Card: <span className="font-mono">{canRevealCard ? 'YES' : 'NO'}</span></div>
            <div>Socket User ID: <span className="font-mono">{(window as any).socketService?.socket?.userId || 'None'}</span></div>
            <div>Players: {gameState.players.map((p: any) => (
              <div key={p.id} className="ml-4">
                {p.username} (ID: {p.id}) - {p.team}/{p.role}
              </div>
            ))}</div>
          </div>

          
          {/* Current Player Status */}
          {currentPlayer && (
            <div className="text-center mb-6 p-4 bg-blue-50 rounded-lg">
              <p className="text-lg">
                Welcome, <span className="font-semibold">{currentPlayer.username}</span>!
              </p>
              {currentPlayer.team !== 'neutral' && (
                <p className="text-sm text-gray-600">
                  You are on the{' '}
                  <span className={`font-semibold ${currentPlayer.team === 'red' ? 'text-red-600' : 'text-blue-600'}`}>
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
            <div className="bg-red-50 border-2 border-red-200 rounded-lg p-6">
              <h3 className="text-2xl font-semibold text-red-700 mb-4 text-center">
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
              <div className="text-sm text-gray-700">
                <div className="font-medium mb-2">Team Members:</div>
                {getPlayersByTeam('red').length === 0 ? (
                  <p className="text-gray-500 italic">No players yet</p>
                ) : (
                  getPlayersByTeam('red').map(player => (
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
              <div className="text-sm text-gray-700">
                <div className="font-medium mb-2">Team Members:</div>
                {getPlayersByTeam('blue').length === 0 ? (
                  <p className="text-gray-500 italic">No players yet</p>
                ) : (
                  getPlayersByTeam('blue').map(player => (
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

          {/* 🔧 DEBUG TESTING CONTROLS */}
          <div className="bg-yellow-100 border-2 border-yellow-400 rounded-lg p-4 mb-6">
            <h3 className="text-lg font-bold text-yellow-800 mb-3">🔧 Testing Mode</h3>
            <div className="space-y-2">
              <button
                onClick={() => {
                  console.log('🧪 Testing socket connection...');
                  
                  const windowSocket = (window as any).socketService;
                  console.log('Socket service object:', windowSocket);
                  console.log('Socket object:', windowSocket?.socket);
                  console.log('Socket connected:', windowSocket?.socket?.connected);
                  console.log('Socket ID:', windowSocket?.socket?.id);
                  
                  if (windowSocket?.socket?.connected) {
                    windowSocket.socket.emit('test-connection');
                    console.log('✅ Sent test-connection event');
                  } else {
                    console.error('❌ Socket not connected');
                  }
                }}
                className="w-full bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 font-semibold"
              >
                🧪 Test Socket Connection
              </button>
              <button
                onClick={() => {
                  console.log('🔧 Adding test players...');
                  console.log('Socket service:', (window as any).socketService);
                  
                  const socketService = (window as any).socketService;
                  if (socketService && socketService.socket && socketService.socket.connected) {
                    socketService.socket.emit('game:add-test-players');
                    console.log('✅ Emitted game:add-test-players event');
                  } else {
                    console.error('❌ Socket not available or not connected');
                    alert('Socket not connected. Try refreshing the page.');
                  }
                }}
                className="w-full bg-yellow-500 text-white px-4 py-2 rounded-lg hover:bg-yellow-600 font-semibold"
              >
                👥 Add Test Players (3 AI Players)
              </button>
              <button
                onClick={() => {
                  console.log('🚀 Force starting game...');
                  onStartGame();
                }}
                className="w-full bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600 font-semibold"
              >
                🚀 Force Start Game
              </button>
              <button
                onClick={() => {
                  console.log('🔵 Joining blue team...');
                  onJoinTeam('blue', 'operative');
                }}
                className="w-full bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 font-semibold"
              >
                🔵 Join Blue Team (You)
              </button>
            </div>
            <p className="text-sm text-yellow-700 mt-2">
              💡 Step 1: Join Blue Team, Step 2: Add Test Players, Step 3: Force Start
            </p>
          </div>

          {/* Start Game Button */}
          <div className="text-center">
            <button
              onClick={onStartGame}
              className="bg-green-500 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-green-600 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
              disabled={gameState.players.length === 0}
            >
              🚀 Start Game
            </button>
            <p className="text-sm text-gray-600 mt-3">
              Use testing controls above for solo testing
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Game Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex flex-col lg:flex-row justify-between items-center gap-6">
            {/* Team Scores */}
            <div className="flex gap-8">
              <div className="text-center">
                <div className="text-lg font-semibold text-red-600">🔴 Red Team</div>
                <div className="text-3xl font-bold text-red-700">{stats.red.remaining}</div>
                <div className="text-sm text-gray-600">cards left</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-semibold text-blue-600">🔵 Blue Team</div>
                <div className="text-3xl font-bold text-blue-700">{stats.blue.remaining}</div>
                <div className="text-sm text-gray-600">cards left</div>
              </div>
            </div>

            {/* Current Turn */}
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-700">Current Turn</div>
              <div className={`text-2xl font-bold ${gameState.currentTurn === 'red' ? 'text-red-600' : 'text-blue-600'}`}>
                {gameState.currentTurn === 'red' ? '🔴' : '🔵'} {gameState.currentTurn.charAt(0).toUpperCase() + gameState.currentTurn.slice(1)}
              </div>
              {gameState.guessesRemaining > 0 && (
                <div className="text-sm text-gray-600">{gameState.guessesRemaining} guesses left</div>
              )}
            </div>

            {/* Player Info */}
            {currentPlayer && (
              <div className="text-center">
                <div className="text-lg font-semibold text-gray-700">You are</div>
                <div className={`text-xl font-bold ${currentPlayer.team === 'red' ? 'text-red-600' : 'text-blue-600'}`}>
                  {currentPlayer.team === 'red' ? '🔴' : '🔵'} {currentPlayer.team.charAt(0).toUpperCase() + currentPlayer.team.slice(1)}
                </div>
                <div className="text-sm text-gray-600">
                  {currentPlayer.role === 'spymaster' ? '👑' : '🕵️'} {currentPlayer.role}
                </div>
              </div>
            )}
          </div>

          {/* Current Clue */}
          {gameState.currentClue && (
            <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="text-center">
                <span className="text-lg font-semibold text-gray-700">💡 Current Clue: </span>
                <span className="text-2xl font-bold text-yellow-700">
                  {gameState.currentClue.word} ({gameState.currentClue.number})
                </span>
              </div>
            </div>
          )}

          {/* ✅ Turn Indicator - Clear message for current player */}
          {gameState.status === 'playing' && currentPlayer && isMyTurn && (
            <div className={`mt-4 p-4 border-2 rounded-lg text-center ${
              currentPlayer.team === 'red' ? 'bg-red-100 border-red-400' : 'bg-blue-100 border-blue-400'
            }`}>
              <div className="text-2xl font-bold mb-2">
                🎯 IT'S YOUR TURN!
              </div>
              <div className="text-lg">
                {canGiveClue && (
                  <span className="text-green-700 font-semibold">
                    💡 Give a clue to your team below ⬇️
                  </span>
                )}
                {canRevealCard && (
                  <span className="text-blue-700 font-semibold">
                    🎯 Click a card to guess! ({gameState.guessesRemaining} guesses left)
                  </span>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Game Controls */}
        {gameState.status === 'playing' && currentPlayer && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            {canGiveClue && (
              <form onSubmit={handleGiveClue} className="flex flex-col sm:flex-row gap-4 items-end">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    💡 Clue Word
                  </label>
                  <input
                    type="text"
                    value={clueWord}
                    onChange={(e) => setClueWord(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
                    placeholder="Enter one word clue..."
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    🔢 Number
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="9"
                    value={clueNumber}
                    onChange={(e) => setClueNumber(parseInt(e.target.value) || 1)}
                    className="w-24 px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
                  />
                </div>
                <button
                  type="submit"
                  className="bg-green-500 text-white px-6 py-3 rounded-md hover:bg-green-600 transition-colors font-semibold"
                >
                  Give Clue
                </button>
              </form>
            )}

            {canRevealCard && (
              <div className="text-center">
                <p className="text-lg text-gray-700 mb-4">
                  🎯 Click on a card to reveal it ({gameState.guessesRemaining} guesses remaining)
                </p>
                <button
                  onClick={onEndTurn}
                  className="bg-orange-500 text-white px-6 py-3 rounded-md hover:bg-orange-600 transition-colors font-semibold"
                >
                  ⏭️ End Turn
                </button>
              </div>
            )}

            {!isMyTurn && currentPlayer && currentPlayer.team !== 'neutral' && (
              <div className="text-center p-4 bg-gray-100 rounded-lg">
                <div className="text-lg text-gray-600 mb-2">
                  ⏳ Waiting for {gameState.currentTurn === 'red' ? '🔴' : '🔵'} {gameState.currentTurn} team's turn...
                </div>
                <div className="text-sm text-gray-500">
                  {gameState.currentClue ? (
                    `${gameState.currentTurn} operatives are guessing (${gameState.guessesRemaining} guesses left)`
                  ) : (
                    `Waiting for ${gameState.currentTurn} spymaster to give a clue`
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Game Board */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="grid grid-cols-5 gap-3">
            {gameState.board
              .sort((a, b) => a.position - b.position)
              .map((card) => (
                <Card
                  key={card.id}
                  card={card}
                  isSpymaster={isSpymaster}
                  onClick={canRevealCard ? onCardClick : undefined}
                  disabled={!canRevealCard}
                />
              ))}
          </div>
        </div>

        {/* Game Over Modal */}
        {gameState.status === 'finished' && gameState.winner && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
              <h2 className="text-4xl font-bold text-center mb-4">🎉 Game Over! 🎉</h2>
              <div className={`text-3xl font-bold text-center mb-6 ${gameState.winner === 'red' ? 'text-red-600' : 'text-blue-600'}`}>
                {gameState.winner === 'red' ? '🔴' : '🔵'} {gameState.winner.charAt(0).toUpperCase() + gameState.winner.slice(1)} Team Wins!
              </div>
              <div className="flex gap-4">
                <button
                  onClick={() => window.location.reload()}
                  className="flex-1 bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-colors font-semibold"
                >
                  🔄 New Game
                </button>
                <button
                  onClick={() => gameService.resetGame()}
                  className="flex-1 bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 transition-colors font-semibold"
                >
                  🎮 Play Again
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default GameBoard;
