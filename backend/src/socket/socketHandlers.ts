import { Server, Socket } from 'socket.io';
import { PrismaClient } from '@prisma/client';
import { gameLobbies } from '../routes/gameLobbies';
import { gameService } from '../services/gameService';

interface AuthenticatedSocket extends Socket {
  userId?: string;
  username?: string;
  currentRoom?: string;
}

// Get access to users map from index.ts
let externalUsersMap: Map<string, any> | null = null;

// Variables needed for socket handlers (local fallbacks)
const users = new Map<string, any>();
const rooms = new Map<string, any>();
const connectedUsers = new Map<string, any>();
const userRooms = new Map<string, string>();

// Function to sync users map from index.ts
export const setUsersMap = (usersMapFromIndex: Map<string, any>) => {
    externalUsersMap = usersMapFromIndex;
    console.log('📋 socketHandlers.ts received users map with', usersMapFromIndex.size, 'users');
};

// Helper functions
function findUserByToken(token: string) {
    if (!token) {
        return null;
    }

    // Use the shared users map from index.ts
    if (externalUsersMap) {
        for (const [userId, userData] of externalUsersMap.entries()) {
            if (userData.token === token) {
                console.log('✅ Found user in shared users map:', userData.username);
                return userData;
            }
        }
        console.log('❌ User not found in shared users map for token:', token.substring(0, 20) + '...');
    } else {
        console.log('❌ External users map not available!');
    }

    return null;
}

function getOrCreateGlobalRoom() {
    if (!rooms.has('GLOBAL')) {
        const globalRoom = {
            code: 'GLOBAL',
            users: new Map(),
            messages: [],
            createdAt: new Date().toISOString(),
        };
        rooms.set('GLOBAL', globalRoom);
    }
    return rooms.get('GLOBAL');
}

export const handleSocketConnection = (io: Server, socket: AuthenticatedSocket, prisma: PrismaClient) => {
    console.log('📡 Socket connected via socketHandlers.ts:', socket.id);

    // Authentication handler
    socket.on('authenticate', (token: string) => {
        console.log('🔐 AUTHENTICATION REQUEST via socketHandlers.ts');
        console.log('🔐 Socket ID:', socket.id);
        console.log('🔐 Token received:', token ? token.substring(0, 20) + '...' : 'null');
        console.log('🔐 External users map available:', !!externalUsersMap);
        console.log('🔐 External users map size:', externalUsersMap ? externalUsersMap.size : 'N/A');
        
        const user = findUserByToken(token);
        console.log('🔐 findUserByToken result:', user ? {
            id: user.id,
            username: user.username
        } : 'null');

        if (user) {
            // Store connected user in THIS socketHandlers.ts connectedUsers map
            const connectedUser = {
                ...user,
                socketId: socket.id,
                connectedAt: new Date().toISOString(),
            };
            
            connectedUsers.set(socket.id, connectedUser);
            console.log('✅ Stored user in connectedUsers map:', connectedUser.username);
            console.log('✅ connectedUsers map now has', connectedUsers.size, 'users');

            // Join global room automatically
            const globalRoom = getOrCreateGlobalRoom();
            globalRoom.users.set(socket.id, user);
            socket.join('GLOBAL');

            socket.emit('authenticated', {
                success: true,
                user: user,
                lobbyCode: 'GLOBAL',
            });

            // Notify others in global room
            socket.to('GLOBAL').emit('user-joined', {
                user: user,
                message: `${user.username} joined the chat`,
            });

            // Send current users in room
            const roomUsers = Array.from(globalRoom.users.values());
            io.to('GLOBAL').emit('room-users', { users: roomUsers });

            // Send recent messages
            socket.emit('recent-messages', {
                messages: globalRoom.messages.slice(-10),
            });

            console.log('✅ Authentication completed successfully for:', user.username);
        } else {
            console.log('❌ Authentication failed - user not found');
            socket.emit('authenticated', {
                success: false,
                error: 'Invalid token',
            });
        }
    });

    // Global chat message handler
    socket.on('send-message', (data: any) => {
        const user = connectedUsers.get(socket.id);
        if (!user) {
            socket.emit('error', { message: 'Not authenticated' });
            return;
        }

        const message = {
            id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
            username: user.username,
            userId: user.id,
            text: data.message,
            timestamp: new Date().toISOString(),
        };

        const globalRoom = getOrCreateGlobalRoom();
        globalRoom.messages.push(message);

        if (globalRoom.messages.length > 50) {
            globalRoom.messages = globalRoom.messages.slice(-50);
        }

        io.to('GLOBAL').emit('new-message', message);
        console.log(`💬 Message from ${user.username}: ${data.message}`);
    });

    // Join lobby
    socket.on('join-lobby', (lobbyCode: string) => {
        const user = connectedUsers.get(socket.id);
        if (!user) {
            socket.emit('lobby-error', 'Not authenticated');
            return;
        }

        console.log(`🏠 User ${user.username} joining lobby: ${lobbyCode}`);

        // Leave any previous rooms (except GLOBAL)
        const socketRooms = Array.from(socket.rooms) as string[];
        socketRooms.forEach((room) => {
            if (room !== socket.id && room !== 'GLOBAL' && room.length === 6) {
                socket.leave(room);
            }
        });

        // Join the new room
        socket.join(lobbyCode.toUpperCase());
        userRooms.set(socket.id, lobbyCode.toUpperCase());

        // Notify others in room
        socket.to(lobbyCode.toUpperCase()).emit('player-joined-lobby', {
            player: { username: user.username, id: user.id },
            message: `${user.username} joined the room`,
        });

        // Emit current lobby state if it exists
        const lobby = gameLobbies.get(lobbyCode.toUpperCase());
        if (lobby) {
            socket.emit('lobby-updated', lobby);
        }
    });


    // Join game room (for active games)
    socket.on('join-game', (gameId: string) => {
        const user = connectedUsers.get(socket.id);
        console.log('🔍 User found:', user ? user.username : 'null');
        if (!user) {
            console.log('❌ User not authenticated for reveal card');
            socket.emit('game:error', 'Not authenticated');
            return;
        }

        console.log(`🎮 User ${user.username} joining game: ${gameId}`);

        // Leave any previous rooms (except GLOBAL)
        const socketRooms = Array.from(socket.rooms) as string[];
        socketRooms.forEach((room) => {
            if (room !== socket.id && room !== 'GLOBAL' && room.length === 6) {
                socket.leave(room);
            }
        });

        // Join the game room
        const gameRoomCode = gameId.toUpperCase();
        socket.join(gameRoomCode);
        userRooms.set(socket.id, gameRoomCode);

        console.log(`✅ ${user.username} joined game room: ${gameRoomCode}`);

        // Send current game state if it exists
        const game = gameService.getGameByCode(gameRoomCode);
        if (game) {
            const gameState = game.getGame();
            socket.emit('game:state-updated', gameState);
            console.log(`📡 Sent current game state to ${user.username}`);
        } else {
            console.log(`❌ Game ${gameRoomCode} not found`);
            socket.emit('game:error', 'Game not found');
        }
    });

    // Join team in lobby
    socket.on('lobby:join-team', (data: { lobbyId: string; team: string; role: string }) => {
        console.log('🎯🎯🎯 LOBBY:JOIN-TEAM EVENT RECEIVED via handlers! 🎯🎯🎯');
        console.log('🔍 Raw data received:', JSON.stringify(data, null, 2));
        
        const user = connectedUsers.get(socket.id);
        if (!user) {
            console.log('❌ User not found in connectedUsers map!');
            socket.emit('lobby-error', 'Not authenticated');
            return;
        }

        console.log(`👥 ${user.username} joining ${data.team} team as ${data.role} in lobby ${data.lobbyId}`);

        const lobby = gameLobbies.get(data.lobbyId.toUpperCase());
        if (!lobby) {
            console.log('❌ Lobby not found!');
            socket.emit('lobby-error', 'Lobby not found');
            return;
        }

        const player = {
            id: user.id,
            username: user.username,
            isOnline: true,
            socketId: socket.id,
        };

        // Initialize teams if they don't exist
        if (!lobby.redTeam) {
            lobby.redTeam = { operatives: [] };
        }
        if (!lobby.blueTeam) {
            lobby.blueTeam = { operatives: [] };
        }

        // Remove player from any existing team first
        if (lobby.redTeam.spymaster?.id === user.id) {
            lobby.redTeam.spymaster = undefined;
        }
        if (lobby.blueTeam.spymaster?.id === user.id) {
            lobby.blueTeam.spymaster = undefined;
        }
        lobby.redTeam.operatives = lobby.redTeam.operatives.filter((p: any) => p.id !== user.id);
        lobby.blueTeam.operatives = lobby.blueTeam.operatives.filter((p: any) => p.id !== user.id);

        // Add player to new team and role
        if (data.team === 'red') {
            if (data.role === 'spymaster') {
                lobby.redTeam.spymaster = player;
            } else if (data.role === 'operative') {
                lobby.redTeam.operatives.push(player);
            }
        } else if (data.team === 'blue') {
            if (data.role === 'spymaster') {
                lobby.blueTeam.spymaster = player;
            } else if (data.role === 'operative') {
                lobby.blueTeam.operatives.push(player);
            }
        }

        lobby.updatedAt = new Date().toISOString();
        io.to(data.lobbyId.toUpperCase()).emit('lobby-updated', lobby);
        console.log(`✅ ${user.username} joined ${data.team} team as ${data.role}`);
    });

    // Leave team in lobby
    socket.on('lobby:leave-team', (data: { lobbyId: string; team: string; role: string }) => {
        console.log('🎯🎯🎯 LOBBY:LEAVE-TEAM EVENT RECEIVED via handlers! 🎯🎯🎯');
        
        const user = connectedUsers.get(socket.id);
        if (!user) {
            socket.emit('lobby-error', 'Not authenticated');
            return;
        }

        const { lobbyId, team, role } = data;
        const lobby = gameLobbies.get(lobbyId.toUpperCase());
        if (!lobby) {
            socket.emit('lobby-error', 'Lobby not found');
            return;
        }

        let removed = false;

        // Remove from red team
        if (team === 'red' && lobby.redTeam) {
            if (role === 'spymaster' && lobby.redTeam.spymaster?.id === user.id) {
                lobby.redTeam.spymaster = undefined;
                removed = true;
            } else if (role === 'operative') {
                const originalLength = lobby.redTeam.operatives.length;
                lobby.redTeam.operatives = lobby.redTeam.operatives.filter((p: any) => p.id !== user.id);
                removed = lobby.redTeam.operatives.length < originalLength;
            }
        }
        
        // Remove from blue team
        if (team === 'blue' && lobby.blueTeam) {
            if (role === 'spymaster' && lobby.blueTeam.spymaster?.id === user.id) {
                lobby.blueTeam.spymaster = undefined;
                removed = true;
            } else if (role === 'operative') {
                const originalLength = lobby.blueTeam.operatives.length;
                lobby.blueTeam.operatives = lobby.blueTeam.operatives.filter((p: any) => p.id !== user.id);
                removed = lobby.blueTeam.operatives.length < originalLength;
            }
        }

        if (removed) {
            lobby.updatedAt = new Date().toISOString();
            io.to(lobbyId.toUpperCase()).emit('lobby-updated', lobby);
            console.log(`✅ ${user.username} successfully left ${team} team as ${role}`);
        }
    });

    // Start game from lobby
    socket.on('lobby:start-game', (data: { lobbyId: string }) => {
        console.log('🚀 lobby:start-game via handlers');
        
        const user = connectedUsers.get(socket.id);
        if (!user) {
            socket.emit('lobby-error', 'Not authenticated');
            return;
        }

        const { lobbyId } = data;
        console.log(`🚀 ${user.username} attempting to start game in lobby ${lobbyId}`);

        const lobby = gameLobbies.get(lobbyId.toUpperCase());
        if (!lobby) {
            console.log('❌ Lobby not found:', lobbyId);
            socket.emit('lobby-error', 'Lobby not found');
            return;
        }

        // Only lobby owner can start the game
        if (lobby.owner !== user.id) {
            console.log(`❌ ${user.username} (${user.id}) tried to start game but is not owner (${lobby.owner})`);
            socket.emit('lobby-error', 'Only the lobby owner can start the game');
            return;
        }

        // Validate teams
        const redTeamValid = lobby.redTeam && 
                            lobby.redTeam.spymaster && 
                            lobby.redTeam.operatives.length > 0;
                            
        const blueTeamValid = lobby.blueTeam && 
                             lobby.blueTeam.spymaster && 
                             lobby.blueTeam.operatives.length > 0;

        console.log('🔍 Team validation:');
        console.log(`  Red team valid: ${redTeamValid}`);
        console.log(`  Blue team valid: ${blueTeamValid}`);

        if (!redTeamValid && !blueTeamValid) {
            console.log('❌ No valid teams found');
            socket.emit('lobby-error', 'Need at least one valid team (spymaster + operatives) to start');
            return;
        }

        // Create actual game in gameService
        try {
            console.log(`🎮 Creating game for lobby ${lobbyId}`);
            
            // Create or get the game for this room
            const game = gameService.createGameForRoom(lobbyId.toUpperCase());
            console.log(`🎮 Game created with ID: ${game.getId()}`);
            
            // Transfer lobby teams to game
            if (lobby.redTeam || lobby.blueTeam) {
                console.log('🔄 Converting and transferring lobby teams to game...');
                
                // Convert lobby teams to game teams
                const convertedRedTeam = (lobby.redTeam && lobby.redTeam.spymaster) ? {
                    spymaster: {
                        id: lobby.redTeam.spymaster.id,
                        username: lobby.redTeam.spymaster.username,
                        isOnline: lobby.redTeam.spymaster.isOnline,
                        socketId: lobby.redTeam.spymaster.socketId || '',
                    },
                    operatives: lobby.redTeam.operatives.map((p: any) => ({
                        id: p.id,
                        username: p.username,
                        isOnline: p.isOnline,
                        socketId: p.socketId || '',
                    }))
                } : undefined;
                
                const convertedBlueTeam = (lobby.blueTeam && lobby.blueTeam.spymaster) ? {
                    spymaster: {
                        id: lobby.blueTeam.spymaster.id,
                        username: lobby.blueTeam.spymaster.username,
                        isOnline: lobby.blueTeam.spymaster.isOnline,
                        socketId: lobby.blueTeam.spymaster.socketId || '',
                    },
                    operatives: lobby.blueTeam.operatives.map((p: any) => ({
                        id: p.id,
                        username: p.username,
                        isOnline: p.isOnline,
                        socketId: p.socketId || '',
                    }))
                } : undefined;
                
                game.setTeams(convertedRedTeam, convertedBlueTeam);
                console.log('✅ Teams transferred successfully');
                
                // Add all players to gameService playerGameMap
                console.log('🔗 Adding players to gameService playerGameMap...');
                
                // Add red team players
                if (convertedRedTeam) {
                    if (convertedRedTeam.spymaster) {
                        gameService.addPlayerToGame(game.getId(), convertedRedTeam.spymaster.id, convertedRedTeam.spymaster.username, convertedRedTeam.spymaster.socketId);
                        console.log(`  Added red spymaster: ${convertedRedTeam.spymaster.username}`);
                    }
                    convertedRedTeam.operatives.forEach((operative: any) => {
                        gameService.addPlayerToGame(game.getId(), operative.id, operative.username, operative.socketId);
                        console.log(`  Added red operative: ${operative.username}`);
                    });
                }
                
                // Add blue team players
                if (convertedBlueTeam) {
                    if (convertedBlueTeam.spymaster) {
                        gameService.addPlayerToGame(game.getId(), convertedBlueTeam.spymaster.id, convertedBlueTeam.spymaster.username, convertedBlueTeam.spymaster.socketId);
                        console.log(`  Added blue spymaster: ${convertedBlueTeam.spymaster.username}`);
                    }
                    convertedBlueTeam.operatives.forEach((operative: any) => {
                        gameService.addPlayerToGame(game.getId(), operative.id, operative.username, operative.socketId);
                        console.log(`  Added blue operative: ${operative.username}`);
                    });
                }
                
                console.log('✅ All players added to gameService');
            }
            
            // Start the game
            console.log('🎮 Starting the game...');
            const startResult = game.startGame();
            console.log(`🎮 Game start result: ${startResult}`);
            
            if (!startResult) {
                throw new Error('Game.startGame() returned false');
            }
            
            // Final verification
            const finalGameState = game.getGame();
            console.log('🎮 Final game state:');
            console.log(`  Game status: ${finalGameState?.status}`);
            
            if (finalGameState?.status === 'playing') {
                console.log(`✅ Game ${lobbyId} started successfully with status 'playing'`);
                
                // Emit game-started event
                io.to(lobbyId.toUpperCase()).emit('game-started', {
                    redirectTo: `/game/${lobbyId.toUpperCase()}`,
                    gameId: lobbyId.toUpperCase()
                });
                
                // 🔒 CLOSE LOBBY: Mark lobby as closed now that game has started
                const lobbyToClose = gameLobbies.get(lobbyId.toUpperCase());
                if (lobbyToClose) {
                    lobbyToClose.status = 'closed';
                    lobbyToClose.updatedAt = new Date().toISOString();
                    console.log(`🔒 Marked lobby ${lobbyId} as closed after game start`);
                    
                    // 📡 BROADCAST: Notify all users that this lobby is now closed
                    io.to('GLOBAL').emit('lobby:closed', {
                        lobbyCode: lobbyId.toUpperCase(),
                        message: `Lobby ${lobbyId} has started a game`
                    });
                    console.log(`📡 Broadcasted lobby:closed for ${lobbyId} to all users`);
                }
                
                console.log(`✅ Game started successfully for lobby ${lobbyId}`);
            } else {
                throw new Error(`Game status is '${finalGameState?.status}', expected 'playing'`);
            }
            
        } catch (error: any) {
            console.error(`❌ Error creating game for lobby ${lobbyId}:`, error);
            socket.emit('lobby-error', `Failed to start game: ${error.message || 'Unknown error'}`);
        }
    });

    // =================
    // GAME ACTION HANDLERS
    // =================
    
    // Give clue handler
    socket.on('game:give-clue', (data: { gameId: string; word: string; number: number }) => {
        console.log('🎯 game:give-clue received:', data);
        
        const user = connectedUsers.get(socket.id);
        console.log('🔍 User found:', user ? user.username : 'null');
        if (!user) {
            console.log('❌ User not authenticated for reveal card');
            socket.emit('game:error', 'Not authenticated');
            return;
        }

        const { gameId, word, number } = data;
        if (!gameId || !word || !number) {
            socket.emit('game:error', 'Missing required parameters');
            return;
        }

        try {
            // Find game directly by gameId (much cleaner!)
            const game = gameService.getGameByCode(gameId.toUpperCase());
            console.log('🔍 Game lookup result:', game ? 'found' : 'not found');
            if (!game) {
                console.log(`❌ Game not found: ${gameId}`);
                socket.emit('game:error', 'Game not found');
                return;
            }

            // Call giveClue on the game object directly
            const clueResult = game.giveClue(user.id, word, number);
            
            if (clueResult) {
                const gameState = game.getGame();
                console.log(`✅ Clue given successfully: ${word} (${number})`);
                
                // 🔍 DEBUG: Check game state after clue
                console.log('🔍 [CLUE DEBUG] Game state after giving clue:');
                console.log('  Current clue:', gameState.currentClue);
                console.log('  Guesses remaining:', gameState.guessesRemaining);
                console.log('  Current turn:', gameState.currentTurn);
                console.log('  Game status:', gameState.status);
                
                // Broadcast updated game state to all players in the room
                console.log(`📡 Broadcasting game:state-updated to room: ${gameId.toUpperCase()}`);
                io.to(gameId.toUpperCase()).emit('game:state-updated', gameState);
                
                // Also emit specific clue-given event
                console.log(`💡 Broadcasting game:clue-given to room: ${gameId.toUpperCase()}`);
                io.to(gameId.toUpperCase()).emit('game:clue-given', gameState.currentClue);
            } else {
                console.log(`❌ Failed to give clue`);
                socket.emit('game:error', 'Failed to give clue');
            }
        } catch (error: any) {
            console.error('❌ Error in game:give-clue handler:', error);
            socket.emit('game:error', 'Internal error giving clue');
        }
    });

    // Reveal card handler
    socket.on('game:reveal-card', (data: { gameId: string; cardId: string }) => {
        console.log('🎯 game:reveal-card received:', data);
        console.log('🔍 Socket ID:', socket.id);
        console.log('🔍 Socket rooms:', Array.from(socket.rooms));
        console.log('🎯 game:reveal-card received:', data);
        
        const user = connectedUsers.get(socket.id);
        console.log('🔍 User found:', user ? user.username : 'null');
        if (!user) {
            console.log('❌ User not authenticated for reveal card');
            socket.emit('game:error', 'Not authenticated');
            return;
        }

        const { gameId, cardId } = data;
        if (!gameId || !cardId) {
            socket.emit('game:error', 'Missing required parameters');
            return;
        }

        try {
            // Find game directly by gameId
            const game = gameService.getGameByCode(gameId.toUpperCase());
            console.log('🔍 Game lookup result:', game ? 'found' : 'not found');
            if (!game) {
                console.log(`❌ Game not found: ${gameId}`);
                socket.emit('game:error', 'Game not found');
                return;
            }

            console.log('🔍 About to call game.revealCard with:', { userId: user.id, cardId });
            const result = game.revealCard(user.id, cardId);
            console.log('🔍 game.revealCard result:', result);
            
            if (result.success) {
                const gameState = game.getGame();
                console.log(`✅ Card revealed successfully: ${cardId}`);
                
                // Broadcast updated game state to all players
                io.to(gameId.toUpperCase()).emit('game:state-updated', gameState);
                
                // Emit specific card-revealed event
                if (result.card) {
                    io.to(gameId.toUpperCase()).emit('game:card-revealed', result.card);
                }
                
                // Check for game end
                if (result.gameEnded && result.winner) {
                    console.log(`🏆 Game ended! Winner: ${result.winner}`);
                    io.to(gameId.toUpperCase()).emit('game:game-ended', result.winner);
                }
            } else {
                console.log(`❌ Failed to reveal card`);
                socket.emit('game:error', 'Failed to reveal card');
            }
        } catch (error: any) {
            console.error('❌ Error in game:reveal-card handler:', error);
            socket.emit('game:error', 'Internal error revealing card');
        }
    });

    // End turn handler
    socket.on('game:end-turn', (data: { gameId: string }) => {
        console.log('🎯 game:end-turn received:', data);
        
        const user = connectedUsers.get(socket.id);
        console.log('🔍 User found:', user ? user.username : 'null');
        if (!user) {
            console.log('❌ User not authenticated for reveal card');
            socket.emit('game:error', 'Not authenticated');
            return;
        }

        const { gameId } = data;
        if (!gameId) {
            socket.emit('game:error', 'Missing required parameters');
            return;
        }

        try {
            // Find game directly by gameId
            const game = gameService.getGameByCode(gameId.toUpperCase());
            console.log('🔍 Game lookup result:', game ? 'found' : 'not found');
            if (!game) {
                console.log(`❌ Game not found: ${gameId}`);
                socket.emit('game:error', 'Game not found');
                return;
            }

            // Call endTurn on the game object (no parameters needed)
            const turnResult = game.endTurn();
            
            if (turnResult) {
                const gameState = game.getGame();
                console.log(`✅ Turn ended successfully, now ${gameState.currentTurn} team's turn`);
                
                // Broadcast updated game state
                io.to(gameId.toUpperCase()).emit('game:state-updated', gameState);
                
                // Emit turn change event
                io.to(gameId.toUpperCase()).emit('game:turn-changed', gameState.currentTurn);
            } else {
                console.log(`❌ Failed to end turn`);
                socket.emit('game:error', 'Failed to end turn');
            }
        } catch (error: any) {
            console.error('❌ Error in game:end-turn handler:', error);
            socket.emit('game:error', 'Internal error ending turn');
        }
    });

    // Handle disconnection
    socket.on('disconnect', () => {
        const user = connectedUsers.get(socket.id);
        if (user) {
            console.log('📡 Socket disconnected via handlers:', socket.id, user.username);

            // Remove from global room
            const globalRoom = getOrCreateGlobalRoom();
            userRooms.delete(socket.id);
            globalRoom.users.delete(socket.id);

            // Notify others
            socket.to('GLOBAL').emit('user-left', {
                user: user,
                message: `${user.username} left the chat`,
            });

            // Update room users
            const roomUsers = Array.from(globalRoom.users.values());
            io.to('GLOBAL').emit('room-users', { users: roomUsers });

            connectedUsers.delete(socket.id);
        } else {
            console.log('📡 Socket disconnected via handlers:', socket.id, '(unauthenticated)');
        }
    });

    // Handle authentication timeout
    setTimeout(() => {
        if (!connectedUsers.has(socket.id)) {
            console.log('⚠️ Socket', socket.id, 'connected but not authenticated after 5 seconds');
        }
    }, 5000);
};
