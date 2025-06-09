import { Server, Socket } from 'socket.io';
import { PrismaClient } from '@prisma/client';
import { gameLobbies } from '../routes/gameLobbies';

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

    // Join team in lobby
    socket.on('lobby:join-team', (data: { lobbyId: string; team: string; role: string }) => {
        console.log('🎯🎯🎯 LOBBY:JOIN-TEAM EVENT RECEIVED via handlers! 🎯🎯🎯');
        console.log('🔍 Raw data received:', JSON.stringify(data, null, 2));
        
        // Debug: Check socket state
        console.log('🔍 Socket ID:', socket.id);
        console.log('🔍 connectedUsers map size:', connectedUsers.size);
        
        const user = connectedUsers.get(socket.id);
        console.log('🔍 User from connectedUsers:', user ? {
            id: user.id,
            username: user.username,
            socketId: user.socketId
        } : 'null');
        
        if (!user) {
            console.log('❌ User not found in connectedUsers map!');
            socket.emit('lobby-error', 'Not authenticated');
            return;
        }

        console.log(`👥 ${user.username} joining ${data.team} team as ${data.role} in lobby ${data.lobbyId}`);

        // Debug: Check gameLobbies
        console.log('🔍 Looking for lobby:', data.lobbyId.toUpperCase());
        console.log('🔍 Available lobbies:', Array.from(gameLobbies.keys()));
        
        const lobby = gameLobbies.get(data.lobbyId.toUpperCase());
        console.log('🔍 Found lobby:', lobby ? {
            id: lobby.id,
            status: lobby.status,
            owner: lobby.owner,
            hasRedTeam: !!lobby.redTeam,
            hasBlueTeam: !!lobby.blueTeam
        } : 'null');
        
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
        console.log('🔍 Created player object:', player);

        // Initialize teams if they don't exist
        if (!lobby.redTeam) {
            console.log('🔧 Initializing red team');
            lobby.redTeam = { operatives: [] };
        }
        if (!lobby.blueTeam) {
            console.log('🔧 Initializing blue team');
            lobby.blueTeam = { operatives: [] };
        }

        // Remove player from any existing team first
        console.log('🔧 Removing player from existing teams...');
        if (lobby.redTeam.spymaster?.id === user.id) {
            lobby.redTeam.spymaster = undefined;
        }
        if (lobby.blueTeam.spymaster?.id === user.id) {
            lobby.blueTeam.spymaster = undefined;
        }
        lobby.redTeam.operatives = lobby.redTeam.operatives.filter((p: any) => p.id !== user.id);
        lobby.blueTeam.operatives = lobby.blueTeam.operatives.filter((p: any) => p.id !== user.id);

        // Add player to new team and role
        console.log(`🔧 Adding player to ${data.team} team as ${data.role}...`);
        if (data.team === 'red') {
            if (data.role === 'spymaster') {
                lobby.redTeam.spymaster = player;
                console.log('✅ Added as red spymaster');
            } else if (data.role === 'operative') {
                lobby.redTeam.operatives.push(player);
                console.log('✅ Added as red operative');
            }
        } else if (data.team === 'blue') {
            if (data.role === 'spymaster') {
                lobby.blueTeam.spymaster = player;
                console.log('✅ Added as blue spymaster');
            } else if (data.role === 'operative') {
                lobby.blueTeam.operatives.push(player);
                console.log('✅ Added as blue operative');
            }
        }

        // Update timestamp
        lobby.updatedAt = new Date().toISOString();
        console.log('🔧 Updated lobby timestamp');

        // Send updated lobby state to all players in the lobby
        console.log(`📤 Broadcasting lobby-updated to room: ${data.lobbyId.toUpperCase()}`);
        
        io.to(data.lobbyId.toUpperCase()).emit('lobby-updated', lobby);
        
        console.log(`✅ ${user.username} joined ${data.team} team as ${data.role}`);
    });

    // 🎯 THE MISSING LEAVE TEAM HANDLER - THIS IS THE FIX!
    socket.on('lobby:leave-team', (data: { lobbyId: string; team: string; role: string }) => {
        console.log('🎯🎯🎯 LOBBY:LEAVE-TEAM EVENT RECEIVED via handlers! 🎯🎯🎯');
        console.log('🎯 Data received:', JSON.stringify(data, null, 2));
        
        const user = connectedUsers.get(socket.id);
        if (!user) {
            console.log('❌ Not authenticated');
            socket.emit('lobby-error', 'Not authenticated');
            return;
        }

        const { lobbyId, team, role } = data;
        console.log(`🚪 ${user.username} leaving ${team} team as ${role} in lobby ${lobbyId}`);

        const lobby = gameLobbies.get(lobbyId.toUpperCase());
        if (!lobby) {
            console.log('❌ Lobby not found:', lobbyId);
            socket.emit('lobby-error', 'Lobby not found');
            return;
        }

        let removed = false;

        // Remove from red team
        if (team === 'red' && lobby.redTeam) {
            console.log('🔍 Checking red team removal...');
            if (role === 'spymaster' && lobby.redTeam.spymaster?.id === user.id) {
                lobby.redTeam.spymaster = undefined;
                removed = true;
                console.log('✅ Removed from red spymaster');
            } else if (role === 'operative') {
                const originalLength = lobby.redTeam.operatives.length;
                lobby.redTeam.operatives = lobby.redTeam.operatives.filter((p: any) => p.id !== user.id);
                removed = lobby.redTeam.operatives.length < originalLength;
                console.log(`✅ Red operatives: ${originalLength} -> ${lobby.redTeam.operatives.length}`);
            }
        }
        
        // Remove from blue team
        if (team === 'blue' && lobby.blueTeam) {
            console.log('🔍 Checking blue team removal...');
            if (role === 'spymaster' && lobby.blueTeam.spymaster?.id === user.id) {
                lobby.blueTeam.spymaster = undefined;
                removed = true;
                console.log('✅ Removed from blue spymaster');
            } else if (role === 'operative') {
                const originalLength = lobby.blueTeam.operatives.length;
                lobby.blueTeam.operatives = lobby.blueTeam.operatives.filter((p: any) => p.id !== user.id);
                removed = lobby.blueTeam.operatives.length < originalLength;
                console.log(`✅ Blue operatives: ${originalLength} -> ${lobby.blueTeam.operatives.length}`);
            }
        }

        if (removed) {
            lobby.updatedAt = new Date().toISOString();
            io.to(lobbyId.toUpperCase()).emit('lobby-updated', lobby);
            console.log(`✅ ${user.username} successfully left ${team} team as ${role}`);
        } else {
            console.log(`❌ Failed to remove ${user.username} from ${team} team as ${role}`);
        }
    });

    // Start game from lobby (OWNER ONLY)
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
            socket.emit('lobby-error', 'Lobby not found');
            return;
        }

        // ✅ OWNERSHIP VALIDATION - Only lobby owner can start the game
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

        if (!redTeamValid && !blueTeamValid) {
            socket.emit('lobby-error', 'Need at least one valid team (spymaster + operatives) to start');
            return;
        }

        // Emit game-started event
        io.to(lobbyId.toUpperCase()).emit('game-started', {
            redirectTo: `/game/${lobbyId.toUpperCase()}`,
            gameId: lobbyId.toUpperCase()
        });
        
        console.log(`✅ Game started successfully for lobby ${lobbyId}`);
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
