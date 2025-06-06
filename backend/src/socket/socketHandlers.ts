import { Server, Socket } from 'socket.io';
import { PrismaClient } from '@prisma/client';
import jwt from 'jsonwebtoken';
import { gameService } from '../services/gameService';
import { TeamColor, PlayerRole } from '../../../shared/types/game';

interface AuthenticatedSocket extends Socket {
  userId?: string;
  username?: string;
  currentRoom?: string;
}

export const handleSocketConnection = (io: Server, socket: AuthenticatedSocket, prisma: PrismaClient) => {
  console.log(`📡 Socket connected: ${socket.id}`);

  // Authentication (keeping simple version for now)
  socket.on('authenticate', async (token: string) => {
    console.log(`🔐 Authenticating socket: ${socket.id}`);
    
    // ✅ Consistent user ID that matches game players
    socket.userId = `user_${socket.id}`;
    socket.username = `Player_${socket.id.substring(0, 4)}`;
    socket.currentRoom = 'GLOBAL';
    
    // Store userId on the socket object for frontend access
    (socket as any).userId = socket.userId;
    
    socket.join('GLOBAL');
    
    socket.emit('authenticated', { 
      success: true, 
      userId: socket.userId,
      username: socket.username 
    });
    
    console.log(`✅ Socket ${socket.id} authenticated as ${socket.username} with ID ${socket.userId}`);
  });

  // Auth bypass for testing
  socket.on('auth-bypass', (username: string) => {
    console.log('🔓 Auth bypass requested');
    socket.userId = `user_${socket.id}`;
    socket.username = username || `Player_${socket.id.substring(0, 4)}`;
    socket.currentRoom = 'GLOBAL';
    socket.join('GLOBAL');
    
    socket.emit('authenticated', { 
      success: true, 
      userId: socket.userId,
      username: socket.username 
    });
    
    console.log(`✅ Auth bypass successful for ${socket.username}`);
  });

  // Test connection
  socket.on('test-connection', () => {
    console.log('🧪 Test connection from:', socket.username || 'unauthenticated');
    socket.emit('test-response', { 
      message: 'Backend is working!', 
      username: socket.username,
      authenticated: !!socket.userId
    });
  });

  // ✅ PROPER GAME MANAGEMENT - Using gameService

  // Create or join game
  socket.on('game:create', () => {
    if (!socket.userId) {
      socket.emit('game:error', 'Not authenticated');
      return;
    }

    console.log(`🎮 Creating/joining game for ${socket.username}`);
    
    // Create or get existing game for room GLOBAL
    let game = gameService.getGameForRoom('GLOBAL');
    if (!game) {
      game = gameService.createGameForRoom('GLOBAL');
    }

    // Add player to game
    const success = gameService.addPlayerToGame(game.getId(), socket.userId, socket.username!, socket.id);
    
    if (success) {
      const gameState = game.getGame();
      io.to('GLOBAL').emit('game:state-updated', gameState);
      console.log(`✅ ${socket.username} joined game ${game.getId()}`);
    } else {
      socket.emit('game:error', 'Failed to join game');
    }
  });

  // Add test players
  socket.on('game:add-test-players', () => {
    if (!socket.userId) {
      socket.emit('game:error', 'Not authenticated');
      return;
    }

    console.log('🤖 Adding test players...');
    
    const game = gameService.getGameByPlayer(socket.userId);
    if (!game) {
      socket.emit('game:error', 'No game found');
      return;
    }

    // Add test players
    const testPlayers = [
      { id: 'test_red_spy', username: '🔴 Red Spy (AI)', team: 'red' as TeamColor, role: 'spymaster' as PlayerRole },
      { id: 'test_red_op', username: '🔴 Red Op (AI)', team: 'red' as TeamColor, role: 'operative' as PlayerRole },
      { id: 'test_blue_spy', username: '🔵 Blue Spy (AI)', team: 'blue' as TeamColor, role: 'spymaster' as PlayerRole }
    ];

    testPlayers.forEach(testPlayer => {
      game.addPlayer(testPlayer.id, testPlayer.username, 'test-socket');
      game.assignPlayerToTeam(testPlayer.id, testPlayer.team, testPlayer.role);
    });

    const gameState = game.getGame();
    io.to('GLOBAL').emit('game:state-updated', gameState);
    socket.emit('game:test-players-added', { message: 'Test players added!', playersAdded: 3 });
    
    console.log(`✅ Added ${testPlayers.length} test players`);
  });

  // Join team
  socket.on('game:join-team', (team: TeamColor, role: PlayerRole) => {
    if (!socket.userId) {
      socket.emit('game:error', 'Not authenticated');
      return;
    }

    console.log(`👥 ${socket.username} joining ${team} team as ${role}`);

    const result = gameService.assignPlayerToTeam(socket.userId, team, role);
    
    if (result.success) {
      const game = gameService.getGameByPlayer(socket.userId);
      if (game) {
        const gameState = game.getGame();
        io.to('GLOBAL').emit('game:state-updated', gameState);
        console.log(`✅ ${socket.username} joined ${team} team as ${role}`);
      }
    } else {
      socket.emit('game:error', result.error || 'Failed to join team');
    }
  });

  // Start game
  socket.on('game:start', () => {
    if (!socket.userId) {
      socket.emit('game:error', 'Not authenticated');
      return;
    }

    console.log(`🚀 Starting game...`);
    
    const result = gameService.startGame(socket.userId);
    
    if (result.success) {
      const game = gameService.getGameByPlayer(socket.userId);
      if (game) {
        const gameState = game.getGame();
        io.to('GLOBAL').emit('game:state-updated', gameState);
        console.log(`✅ Game started successfully`);
      }
    } else {
      socket.emit('game:error', result.error || 'Failed to start game');
    }
  });

  // ✅ PROPER GAMEPLAY ACTIONS

  // Give clue
  socket.on('game:give-clue', (clueData: { word: string; number: number }) => {
    if (!socket.userId) {
      socket.emit('game:error', 'Not authenticated');
      return;
    }

    console.log(`💡 ${socket.username} giving clue: ${clueData.word} (${clueData.number})`);

    const result = gameService.giveClue(socket.userId, clueData.word, clueData.number);
    
    if (result.success) {
      const game = gameService.getGameByPlayer(socket.userId);
      if (game) {
        const gameState = game.getGame();
        io.to('GLOBAL').emit('game:state-updated', gameState);
        io.to('GLOBAL').emit('game:clue-given', gameState.currentClue);
        console.log(`✅ Clue given: ${clueData.word} (${clueData.number})`);
      }
    } else {
      socket.emit('game:error', result.error || 'Failed to give clue');
    }
  });

  // Reveal card
  socket.on('game:reveal-card', (cardId: string) => {
    if (!socket.userId) {
      socket.emit('game:error', 'Not authenticated');
      return;
    }

    console.log(`🎯 ${socket.username} revealing card: ${cardId}`);

    const result = gameService.revealCard(socket.userId, cardId);
    
    if (result.success) {
      const game = gameService.getGameByPlayer(socket.userId);
      if (game) {
        const gameState = game.getGame();
        io.to('GLOBAL').emit('game:state-updated', gameState);
        io.to('GLOBAL').emit('game:card-revealed', result.card);
        
        if (result.gameEnded && result.winner) {
          io.to('GLOBAL').emit('game:game-ended', result.winner);
          console.log(`🏆 Game ended! Winner: ${result.winner}`);
        } else {
          console.log(`✅ Card revealed: ${result.card?.word} (${result.card?.team})`);
        }
      }
    } else {
      socket.emit('game:error', result.error || 'Failed to reveal card');
    }
  });

  // End turn
  socket.on('game:end-turn', () => {
    if (!socket.userId) {
      socket.emit('game:error', 'Not authenticated');
      return;
    }

    console.log(`⏭️ ${socket.username} ending turn`);

    const result = gameService.endTurn(socket.userId);
    
    if (result.success) {
      const game = gameService.getGameByPlayer(socket.userId);
      if (game) {
        const gameState = game.getGame();
        io.to('GLOBAL').emit('game:state-updated', gameState);
        io.to('GLOBAL').emit('game:turn-changed', gameState.currentTurn);
        console.log(`✅ Turn ended, now ${gameState.currentTurn} team's turn`);
      }
    } else {
      socket.emit('game:error', result.error || 'Failed to end turn');
    }
  });

  // Handle disconnection
  socket.on('disconnect', () => {
    console.log(`📡 Socket disconnected: ${socket.id}`);
    
    if (socket.userId) {
      // Update player offline status but don't remove them
      gameService.updatePlayerOnlineStatus(socket.userId, false);
      
      const game = gameService.getGameByPlayer(socket.userId);
      if (game) {
        const gameState = game.getGame();
        io.to('GLOBAL').emit('game:state-updated', gameState);
      }
    }
  });
};