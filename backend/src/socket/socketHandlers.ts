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

// Variables needed for socket handlers
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


// Helper function to check if lobby is empty and delete it
function checkAndDeleteEmptyLobby(lobbyCode: string, io: Server): boolean {
    try {
        const lobby = gameLobbies.get(lobbyCode.toUpperCase());
        if (!lobby) {
            console.log(`🔍 checkAndDeleteEmptyLobby: Lobby ${lobbyCode} not found`);
            return false;
        }

        // Count total players in both teams
        let totalPlayers = 0;
        
        if (lobby.redTeam) {
            if (lobby.redTeam.spymaster) totalPlayers++;
            totalPlayers += (lobby.redTeam.operatives || []).length;
        }
        
        if (lobby.blueTeam) {
            if (lobby.blueTeam.spymaster) totalPlayers++;
            totalPlayers += (lobby.blueTeam.operatives || []).length;
        }

        console.log(`🔍 checkAndDeleteEmptyLobby: Lobby ${lobbyCode} has ${totalPlayers} players`);

        // If lobby is empty, delete it
        if (totalPlayers === 0) {
            console.log(`🗑️ Deleting empty lobby: ${lobbyCode}`);
            gameLobbies.delete(lobbyCode.toUpperCase());
            
            // Broadcast lobby deletion to all users
            io.to('GLOBAL').emit('lobby:deleted', {
                lobbyCode: lobbyCode.toUpperCase(),
                message: `Lobby ${lobbyCode} was deleted (no players remaining)`
            });
            
            return true;
        }
        
        return false;
    } catch (error) {
        console.error(`❌ Error in checkAndDeleteEmptyLobby for ${lobbyCode}:`, error);
        return false;
    }
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
    console.log('📡 Socket connected:', socket.id);

    // Authentication handler
    socket.on('authenticate', (token: string) => {
        console.log('🔐 Authentication request from socket:', socket.id);
        
        const user = findUserByToken(token);

        if (user) {
            const connectedUser = {
                ...user,
                socketId: socket.id,
                connectedAt: new Date().toISOString(),
            };
            
            connectedUsers.set(socket.id, connectedUser);
            console.log('✅ User authenticated:', connectedUser.username);

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

            console.log('✅ Authentication completed for:', user.username);
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

        const previousRoom = userRooms.get(socket.id);
        console.log(`🏠 [JOIN-LOBBY] User ${user.username} joining lobby: ${lobbyCode}`);
        console.log(`🏠 [JOIN-LOBBY] Previous room: ${previousRoom}`);

        // Leave any previous rooms (except GLOBAL)
        const socketRooms = Array.from(socket.rooms) as string[];
        console.log(`🏠 [JOIN-LOBBY] Current socket rooms: ${socketRooms}`);
        
        socketRooms.forEach((room) => {
            if (room !== socket.id && room !== 'GLOBAL' && room.length === 6) {
                console.log(`🏠 [JOIN-LOBBY] Leaving previous room: ${room}`);
                socket.leave(room);
            }
        });

        // Join the new room
        const upperLobbyCode = lobbyCode.toUpperCase();
        socket.join(upperLobbyCode);
        userRooms.set(socket.id, upperLobbyCode);
        
        console.log(`🏠 [JOIN-LOBBY] Joined room: ${upperLobbyCode}`);
        console.log(`🏠 [JOIN-LOBBY] Updated userRooms mapping for ${socket.id}: ${upperLobbyCode}`);

        // Notify others in room
        socket.to(upperLobbyCode).emit('player-joined-lobby', {
            player: { username: user.username, id: user.id },
            message: `${user.username} joined the room`,
        });

        // Emit current lobby state if it exists
        const lobby = gameLobbies.get(upperLobbyCode);
        if (lobby) {
            console.log(`🏠 [JOIN-LOBBY] Sending lobby state to ${user.username}`);
            socket.emit('lobby-updated', lobby);
        } else {
            console.log(`🏠 [JOIN-LOBBY] No lobby found for code: ${upperLobbyCode}`);
        }
    });

    // Leave lobby
    socket.on('leave-lobby', (data: { lobbyId: string }) => {
        const user = connectedUsers.get(socket.id);
        if (!user) {
            socket.emit('lobby-error', 'Not authenticated');
            return;
        }

        const { lobbyId } = data;
        const upperLobbyId = lobbyId.toUpperCase();
        
        console.log(`🚪 [LEAVE-LOBBY] User ${user.username} leaving lobby: ${upperLobbyId}`);

        const lobby = gameLobbies.get(upperLobbyId);
        if (!lobby) {
            console.log(`⚠️ [LEAVE-LOBBY] Lobby ${upperLobbyId} not found - user may have already left`);
            return;
        }

        let removedFromTeams = false;

        // Remove user from teams if they're on them
        if (lobby.redTeam) {
            if (lobby.redTeam.spymaster?.id === user.id) {
                lobby.redTeam.spymaster = undefined;
                removedFromTeams = true;
                console.log(`🔄 [LEAVE-LOBBY] Removed ${user.username} from red spymaster`);
            }
            const originalLength = lobby.redTeam.operatives.length;
            lobby.redTeam.operatives = lobby.redTeam.operatives.filter((p: any) => p.id !== user.id);
            if (lobby.redTeam.operatives.length < originalLength) {
                removedFromTeams = true;
                console.log(`🔄 [LEAVE-LOBBY] Removed ${user.username} from red operatives`);
            }
        }

        if (lobby.blueTeam) {
            if (lobby.blueTeam.spymaster?.id === user.id) {
                lobby.blueTeam.spymaster = undefined;
                removedFromTeams = true;
                console.log(`🔄 [LEAVE-LOBBY] Removed ${user.username} from blue spymaster`);
            }
            const originalLength = lobby.blueTeam.operatives.length;
            lobby.blueTeam.operatives = lobby.blueTeam.operatives.filter((p: any) => p.id !== user.id);
            if (lobby.blueTeam.operatives.length < originalLength) {
                removedFromTeams = true;
                console.log(`🔄 [LEAVE-LOBBY] Removed ${user.username} from blue operatives`);
            }
        }

        // Remove user from socket room
        socket.leave(upperLobbyId);
        
        // Remove from userRooms tracking
        if (userRooms.get(socket.id) === upperLobbyId) {
            userRooms.delete(socket.id);
            console.log(`🔄 [LEAVE-LOBBY] Removed ${user.username} from room tracking`);
        }

        // Notify others in lobby that user left
        socket.to(upperLobbyId).emit('player-left-lobby', {
            player: { username: user.username, id: user.id },
            message: `${user.username} left the lobby`,
        });

        // Check how many players are still in the lobby room
        const socketsInRoom = io.sockets.adapter.rooms.get(upperLobbyId);
        const remainingPlayerCount = socketsInRoom ? socketsInRoom.size : 0;
        
        console.log(`🔍 [LEAVE-LOBBY] Players remaining in room ${upperLobbyId}: ${remainingPlayerCount}`);

        if (remainingPlayerCount === 0) {
            // No players left in lobby - delete it
            console.log(`🗑️ [LEAVE-LOBBY] Deleting empty lobby: ${upperLobbyId}`);
            gameLobbies.delete(upperLobbyId);
            
            // Broadcast lobby deletion to global room
            io.to('GLOBAL').emit('lobby:deleted', {
                lobbyCode: upperLobbyId,
                message: `Lobby ${upperLobbyId} was deleted (no players remaining)`
            });
        } else {
            // Update lobby timestamp and notify remaining players if user was on teams
            if (removedFromTeams) {
                lobby.updatedAt = new Date().toISOString();
                io.to(upperLobbyId).emit('lobby-updated', lobby);
                console.log(`📡 [LEAVE-LOBBY] Sent lobby-updated to ${remainingPlayerCount} remaining players`);
            }
        }

        // Return user to global room
        socket.join('GLOBAL');
        userRooms.set(socket.id, 'GLOBAL');
        
        console.log(`✅ [LEAVE-LOBBY] ${user.username} successfully left lobby ${upperLobbyId}`);
    });

    // Join game room (for active games)
    socket.on('join-game', (gameId: string) => {
        const user = connectedUsers.get(socket.id);
        if (!user) {
            console.log('❌ User not authenticated for join-game');
            socket.emit('game:error', 'Not authenticated');
            return;
        }

        console.log(`🎮 User ${user.username} joining game: ${gameId}`);

        // Get the game first
        const game = gameService.getGameByCode(gameId.toUpperCase());
        if (!game) {
            console.log(`❌ Game ${gameId} not found`);
            socket.emit('game:error', 'Game not found');
            return;
        }

        // Check authorization
        let isAuthorized = gameService.isUserAuthorizedForGame(user.id, gameId.toUpperCase());
        
        // Fallback: If user is in the game teams but not authorized, authorize them
        if (!isAuthorized) {
            console.log('🔧 Checking if user should have access...');
            const gameState = game.getGame();
            let shouldHaveAccess = false;
            
            if (gameState.redTeam) {
                if (gameState.redTeam.spymaster?.id === user.id) shouldHaveAccess = true;
                if (gameState.redTeam.operatives?.some((p: any) => p.id === user.id)) shouldHaveAccess = true;
            }
            
            if (gameState.blueTeam) {
                if (gameState.blueTeam.spymaster?.id === user.id) shouldHaveAccess = true;
                if (gameState.blueTeam.operatives?.some((p: any) => p.id === user.id)) shouldHaveAccess = true;
            }
            
            if (shouldHaveAccess) {
                console.log(`🔧 Authorizing ${user.username} for game access`);
                gameService.authorizeUserForGame(user.id, gameId.toUpperCase());
                isAuthorized = true;
            }
        }

        if (!isAuthorized) {
            console.log(`❌ ${user.username} not authorized for game ${gameId}`);
            socket.emit('game:error', {
                error: 'You are not authorized to access this game',
                code: 'NOT_AUTHORIZED',
                gameId: gameId
            });
            return;
        }

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

        // Send current game state
        const gameState = game.getGame();
        socket.emit('game:state-updated', gameState);
        console.log(`📡 Sent current game state to ${user.username}`);
    });

    // Join team in lobby
    socket.on('lobby:join-team', (data: { lobbyId: string; team: string; role: string }) => {
        console.log('👥 LOBBY:JOIN-TEAM EVENT RECEIVED');
        
        const user = connectedUsers.get(socket.id);
        if (!user) {
            socket.emit('lobby-error', 'Not authenticated');
            return;
        }

        console.log(`👥 ${user.username} joining ${data.team} team as ${data.role} in lobby ${data.lobbyId}`);

        const lobby = gameLobbies.get(data.lobbyId.toUpperCase());
        if (!lobby) {
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
        console.log(`🔍 [LEAVE-TEAM] Event received:`, data);
        
        const user = connectedUsers.get(socket.id);
        if (!user) {
            console.log(`❌ [LEAVE-TEAM] User not authenticated for socket ${socket.id}`);
            socket.emit('lobby-error', 'Not authenticated');
            return;
        }

        console.log(`🔍 [LEAVE-TEAM] User: ${user.username} (${user.id})`);

        const { lobbyId, team, role } = data;
        
        // *** CRITICAL DEBUGGING: Check room mismatch ***
        const userCurrentRoom = userRooms.get(socket.id);
        const requestedLobby = lobbyId.toUpperCase();
        
        console.log(`🔍 [LEAVE-TEAM] *** ROOM MISMATCH CHECK ***`);
        console.log(`🔍 [LEAVE-TEAM] Frontend requested lobby: ${requestedLobby}`);
        console.log(`🔍 [LEAVE-TEAM] Backend user room: ${userCurrentRoom}`);
        console.log(`🔍 [LEAVE-TEAM] Socket rooms: ${Array.from(socket.rooms)}`);
        console.log(`🔍 [LEAVE-TEAM] Match? ${userCurrentRoom === requestedLobby}`);
        
        if (userCurrentRoom !== requestedLobby) {
            console.log(`🚨 [LEAVE-TEAM] CRITICAL: Room mismatch detected!`);
            console.log(`🚨 [LEAVE-TEAM] User is in room ${userCurrentRoom} but trying to affect ${requestedLobby}`);
            console.log(`🚨 [LEAVE-TEAM] This will cause frontend to freeze - fixing by using user's actual room`);
            
            // Option 1: Use the user's actual room instead
            const actualLobbyId = userCurrentRoom || lobbyId;
            console.log(`🔧 [LEAVE-TEAM] Using actual user room: ${actualLobbyId}`);
            
            // Update the lobbyId to match where the user actually is
            data.lobbyId = actualLobbyId;
        }
        const lobby = gameLobbies.get(data.lobbyId.toUpperCase());
        if (!lobby) {
            console.log(`❌ [LEAVE-TEAM] Lobby ${data.lobbyId} not found`);
            socket.emit('lobby-error', 'Lobby not found');
            return;
        }

        console.log(`🔍 [LEAVE-TEAM] Lobby found: ${data.lobbyId}`);
        console.log(`🔍 [LEAVE-TEAM] Current lobby state:`, {
            redTeam: lobby.redTeam ? {
                spymaster: lobby.redTeam.spymaster ? `${lobby.redTeam.spymaster.username} (${lobby.redTeam.spymaster.id})` : 'none',
                operatives: lobby.redTeam.operatives.map((p: any) => `${p.username} (${p.id})`)
            } : 'none',
            blueTeam: lobby.blueTeam ? {
                spymaster: lobby.blueTeam.spymaster ? `${lobby.blueTeam.spymaster.username} (${lobby.blueTeam.spymaster.id})` : 'none',
                operatives: lobby.blueTeam.operatives.map((p: any) => `${p.username} (${p.id})`)
            } : 'none'
        });

        let removed = false;

        // Remove from red team
        if (team === 'red' && lobby.redTeam) {
            console.log(`🔍 [LEAVE-TEAM] Checking red team for ${role}`);
            
            if (role === 'spymaster' && lobby.redTeam.spymaster?.id === user.id) {
                console.log(`🔍 [LEAVE-TEAM] Removing ${user.username} as red spymaster`);
                lobby.redTeam.spymaster = undefined;
                removed = true;
            } else if (role === 'operative') {
                console.log(`🔍 [LEAVE-TEAM] Checking red operatives for ${user.username} (${user.id})`);
                const originalLength = lobby.redTeam.operatives.length;
                console.log(`🔍 [LEAVE-TEAM] Original operatives count: ${originalLength}`);
                
                lobby.redTeam.operatives = lobby.redTeam.operatives.filter((p: any) => {
                    const keep = p.id !== user.id;
                    console.log(`🔍 [LEAVE-TEAM] Operative ${p.username} (${p.id}) - keep: ${keep}`);
                    return keep;
                });
                
                console.log(`🔍 [LEAVE-TEAM] New operatives count: ${lobby.redTeam.operatives.length}`);
                removed = lobby.redTeam.operatives.length < originalLength;
            }
        }
        
        // Remove from blue team
        if (team === 'blue' && lobby.blueTeam) {
            console.log(`🔍 [LEAVE-TEAM] Checking blue team for ${role}`);
            
            if (role === 'spymaster' && lobby.blueTeam.spymaster?.id === user.id) {
                console.log(`🔍 [LEAVE-TEAM] Removing ${user.username} as blue spymaster`);
                lobby.blueTeam.spymaster = undefined;
                removed = true;
            } else if (role === 'operative') {
                console.log(`🔍 [LEAVE-TEAM] Checking blue operatives for ${user.username} (${user.id})`);
                const originalLength = lobby.blueTeam.operatives.length;
                console.log(`🔍 [LEAVE-TEAM] Original operatives count: ${originalLength}`);
                
                lobby.blueTeam.operatives = lobby.blueTeam.operatives.filter((p: any) => {
                    const keep = p.id !== user.id;
                    console.log(`🔍 [LEAVE-TEAM] Operative ${p.username} (${p.id}) - keep: ${keep}`);
                    return keep;
                });
                
                console.log(`🔍 [LEAVE-TEAM] New operatives count: ${lobby.blueTeam.operatives.length}`);
                removed = lobby.blueTeam.operatives.length < originalLength;
            }
        }

        console.log(`🔍 [LEAVE-TEAM] Was user removed? ${removed}`);

        if (removed) {
            lobby.updatedAt = new Date().toISOString();
            
            // DON'T delete lobby when players leave teams - they're still in the lobby!
            // Lobbies should only be deleted when players disconnect/leave the lobby entirely.
            
            console.log(`📡 [LEAVE-TEAM] Emitting lobby-updated to room ${data.lobbyId.toUpperCase()}`);
            io.to(data.lobbyId.toUpperCase()).emit('lobby-updated', lobby);
            console.log(`📡 [LEAVE-TEAM] Successfully sent lobby-updated for ${data.lobbyId}`);
            console.log(`✅ [LEAVE-TEAM] ${user.username} successfully left ${team} team as ${role}`)
        } else {
            console.log(`⚠️ [LEAVE-TEAM] User ${user.username} (${user.id}) was not found in ${team} team as ${role}`);
            console.log(`🔍 [LEAVE-TEAM] This could mean:`);
            console.log(`🔍 [LEAVE-TEAM] 1. User is not currently in that team/role`);
            console.log(`🔍 [LEAVE-TEAM] 2. User ID mismatch`);
            console.log(`🔍 [LEAVE-TEAM] 3. Team doesn't exist`);
            
            // Send the current lobby state anyway so frontend doesn't freeze
            console.log(`📡 [LEAVE-TEAM] Sending current lobby state to prevent freeze`);
            io.to(data.lobbyId.toUpperCase()).emit('lobby-updated', lobby);
        }
    });

    // Start game from lobby
    socket.on('lobby:start-game', (data: { lobbyId: string }) => {
        console.log('🚀 lobby:start-game received');
        
        const user = connectedUsers.get(socket.id);
        if (!user) {
            socket.emit('lobby-error', 'Not authenticated');
            return;
        }

        const { lobbyId } = data;
        console.log(`🚀 ${user.username} attempting to start game in lobby ${lobbyId}`);

        const lobby = gameLobbies.get(data.lobbyId.toUpperCase());
        if (!lobby) {
            console.log('❌ Lobby not found:', lobbyId);
            socket.emit('lobby-error', 'Lobby not found');
            return;
        }

        // Only lobby owner can start the game
        if (lobby.owner !== user.id) {
            console.log(`❌ ${user.username} tried to start game but is not owner`);
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

        if (!redTeamValid && !blueTeamValid) {
            console.log('❌ No valid teams found');
            socket.emit('lobby-error', 'Need at least one valid team (spymaster + operatives) to start');
            return;
        }

        // Create actual game in gameService
        try {
            console.log(`🎮 Creating game for lobby ${lobbyId}`);
            
            const game = gameService.createGameForRoom(lobbyId.toUpperCase());
            const gameId = game.getId();
            console.log(`🎮 Game created with ID: ${gameId}`);            
            // 🔍 DETAILED GAME CREATION DEBUG
            console.log('🔍 [GAME-CREATE] === DETAILED DEBUG INFO ===');
            console.log('🔍 [GAME-CREATE] Game ID:', gameId);
            console.log('🔍 [GAME-CREATE] Game Code:', game.getGameCode());
            console.log('🔍 [GAME-CREATE] Game Status:', game.getStatus());
            
            // Test if we can immediately find the game
            const testLookup = gameService.getGameByCode(lobbyId.toUpperCase());
            console.log('🔍 [GAME-CREATE] Immediate lookup test:', testLookup ? 'FOUND' : 'NOT FOUND');
            
            if (testLookup) {
                console.log('🔍 [GAME-CREATE] Test lookup game ID:', testLookup.getId());
                console.log('🔍 [GAME-CREATE] Test lookup game code:', testLookup.getGameCode());
            }
            
            // Check gameService internal state
            const stats = gameService.getStats();
            console.log('🔍 [GAME-CREATE] GameService stats:', stats);
            
            // 🔐 AUTHORIZE ALL PLAYERS for the new game
            console.log('🔐 Authorizing all lobby players for game:', gameId);
            
            if (lobby.redTeam) {
                if (lobby.redTeam.spymaster) {
                    gameService.authorizeUserForGame(lobby.redTeam.spymaster.id, gameId);
                    console.log(`🔐 Authorized red spymaster: ${lobby.redTeam.spymaster.username}`);
                }
                lobby.redTeam.operatives.forEach((operative: any) => {
                    gameService.authorizeUserForGame(operative.id, gameId);
                    console.log(`🔐 Authorized red operative: ${operative.username}`);
                });
            }
            
            if (lobby.blueTeam) {
                if (lobby.blueTeam.spymaster) {
                    gameService.authorizeUserForGame(lobby.blueTeam.spymaster.id, gameId);
                    console.log(`🔐 Authorized blue spymaster: ${lobby.blueTeam.spymaster.username}`);
                }
                lobby.blueTeam.operatives.forEach((operative: any) => {
                    gameService.authorizeUserForGame(operative.id, gameId);
                    console.log(`🔐 Authorized blue operative: ${operative.username}`);
                });
            }
            
            console.log('✅ All lobby players authorized for game:', gameId);
            
            // Transfer lobby teams to game
            if (lobby.redTeam || lobby.blueTeam) {
                console.log('🔄 Transferring lobby teams to game...');
                
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
            }
            
            // Start the game
            console.log('🎮 Starting the game...');
            const startResult = game.startGame();
            
            if (startResult) {
                const gameState = game.getGame();
                console.log(`✅ Game ${lobbyId} started successfully with status: ${gameState.status}`);
                
                // Emit game-started event
                io.to(lobbyId.toUpperCase()).emit('game-started', {
                    redirectTo: `/game/${lobbyId.toUpperCase()}`,
                    gameId: lobbyId.toUpperCase()
                });
                
                // Close lobby
                const lobbyToClose = gameLobbies.get(lobbyId.toUpperCase());
                if (lobbyToClose) {
                    lobbyToClose.status = 'closed';
                    lobbyToClose.updatedAt = new Date().toISOString();
                    console.log(`🔒 Marked lobby ${lobbyId} as closed`);
                    
                    io.to('GLOBAL').emit('lobby:closed', {
                        lobbyCode: lobbyId.toUpperCase(),
                        message: `Lobby ${lobbyId} has started a game`
                    });
                }
                
                console.log(`✅ Game started successfully for lobby ${lobbyId}`);
            } else {
                throw new Error('Game start failed');
            }
            
        } catch (error: any) {
            console.error(`❌ Error creating game for lobby ${lobbyId}:`, error);
            socket.emit('lobby-error', `Failed to start game: ${error.message || 'Unknown error'}`);
        }
    });

    // Game action handlers
    socket.on('game:give-clue', (data: { gameId: string; word: string; number: number }) => {
        const user = connectedUsers.get(socket.id);
        if (!user) {
            socket.emit('game:error', 'Not authenticated');
            return;
        }

        const { gameId, word, number } = data;
        const game = gameService.getGameByCode(gameId.toUpperCase());
        if (!game) {
            socket.emit('game:error', 'Game not found');
            return;
        }

        const clueResult = game.giveClue(user.id, word, number);
        if (clueResult) {
            const gameState = game.getGame();
            io.to(gameId.toUpperCase()).emit('game:state-updated', gameState);
            io.to(gameId.toUpperCase()).emit('game:clue-given', gameState.currentClue);
        } else {
            socket.emit('game:error', 'Failed to give clue');
        }
    });

    socket.on('game:reveal-card', (data: { gameId: string; cardId: string }) => {
        const user = connectedUsers.get(socket.id);
        if (!user) {
            socket.emit('game:error', 'Not authenticated');
            return;
        }

        const { gameId, cardId } = data;
        const game = gameService.getGameByCode(gameId.toUpperCase());
        if (!game) {
            socket.emit('game:error', 'Game not found');
            return;
        }

        const result = game.revealCard(user.id, cardId);
        if (result.success) {
            const gameState = game.getGame();
            io.to(gameId.toUpperCase()).emit('game:state-updated', gameState);
            
            if (result.card) {
                io.to(gameId.toUpperCase()).emit('game:card-revealed', result.card);
            }
            
            if (result.gameEnded && result.winner) {
                io.to(gameId.toUpperCase()).emit('game:game-ended', result.winner);
            }
        } else {
            socket.emit('game:error', 'Failed to reveal card');
        }
    });

    socket.on('game:end-turn', (data: { gameId: string }) => {
        const user = connectedUsers.get(socket.id);
        if (!user) {
            socket.emit('game:error', 'Not authenticated');
            return;
        }

        const { gameId } = data;
        const game = gameService.getGameByCode(gameId.toUpperCase());
        if (!game) {
            socket.emit('game:error', 'Game not found');
            return;
        }

        const turnResult = game.endTurn();
        if (turnResult) {
            const gameState = game.getGame();
            io.to(gameId.toUpperCase()).emit('game:state-updated', gameState);
            io.to(gameId.toUpperCase()).emit('game:turn-changed', gameState.currentTurn);
        } else {
            socket.emit('game:error', 'Failed to end turn');
        }
    });

    // Handle disconnection
    socket.on('disconnect', () => {
        const user = connectedUsers.get(socket.id);
        if (user) {
            console.log('📡 Socket disconnected:', socket.id, user.username);

            // Check if user was in a lobby and remove them from teams
            const userRoom = userRooms.get(socket.id);
            if (userRoom && userRoom !== 'GLOBAL' && userRoom.length === 6) {
                const lobby = gameLobbies.get(userRoom);
                if (lobby) {
                    let removedFromLobby = false;
                    
                    // Remove from red team
                    if (lobby.redTeam) {
                        if (lobby.redTeam.spymaster?.socketId === socket.id) {
                            lobby.redTeam.spymaster = undefined;
                            removedFromLobby = true;
                        }
                        const originalLength = lobby.redTeam.operatives.length;
                        lobby.redTeam.operatives = lobby.redTeam.operatives.filter((p: any) => p.socketId !== socket.id);
                        if (lobby.redTeam.operatives.length < originalLength) {
                            removedFromLobby = true;
                        }
                    }
                    
                    // Remove from blue team
                    if (lobby.blueTeam) {
                        if (lobby.blueTeam.spymaster?.socketId === socket.id) {
                            lobby.blueTeam.spymaster = undefined;
                            removedFromLobby = true;
                        }
                        const originalLength = lobby.blueTeam.operatives.length;
                        lobby.blueTeam.operatives = lobby.blueTeam.operatives.filter((p: any) => p.socketId !== socket.id);
                        if (lobby.blueTeam.operatives.length < originalLength) {
                            removedFromLobby = true;
                        }
                    }
                    
                    if (removedFromLobby) {
                        console.log(`🚪 Removed disconnected user ${user.username} from lobby ${userRoom}`);
                        lobby.updatedAt = new Date().toISOString();
                        
                        // Check if lobby is now empty and delete it
                        const wasDeleted = checkAndDeleteEmptyLobby(userRoom, io);
                        
                        if (!wasDeleted) {
                            // Only emit lobby-updated if lobby wasn't deleted
                            io.to(userRoom).emit('lobby-updated', lobby);
                        }
                    }
                }
            }

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
            console.log('📡 Socket disconnected:', socket.id, '(unauthenticated)');
        }
    });
};
