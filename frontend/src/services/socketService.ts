import { io, Socket } from 'socket.io-client';

export interface User {
  id: string;
  username: string;
  socketId?: string;
}

export interface Room {
  id: string;
  name: string;
  code: string;
  maxPlayers: number;
  users: Array<{
    user: User;
    role: string;
    team?: string;
  }>;
}

export interface ChatMessage {
  id: string;
  username: string;
  message: string;
  timestamp: string;
}

class SocketService {
  private _socket: Socket | null = null;
  private token: string | null = null;

  get socket(): Socket | null {
    return this._socket;
  }

  connect(): Socket {
    // Make socket service accessible for debugging
    (window as any).socketService = this;

    if (this._socket?.connected) {
      console.log('📡 Socket already connected');
      return this._socket;
    }

    const socketUrl = import.meta.env.VITE_SOCKET_URL || 'http://localhost:3001';
    console.log('📡 Connecting to socket server:', socketUrl);

    this._socket = io(socketUrl, {
      autoConnect: false,
      transports: ['websocket', 'polling'],
      timeout: 5000,
      forceNew: true,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000
    });

    this.setupEventListeners();
    this._socket.connect();

    return this._socket;
  }

  disconnect(): void {
    if (this._socket) {
      console.log('📡 Disconnecting socket');
      this._socket.disconnect();
      this._socket = null;
    }
  }

  authenticate(token: string): void {
    this.token = token;
    if (this._socket) {
      console.log('🔐 Authenticating with token');
      this._socket.emit('authenticate', token);
    }
  }

  joinRoom(roomCode: string): void {
    if (this._socket) {
      console.log('🏠 Joining room:', roomCode);
      this._socket.emit('join-room', { roomCode });
    }
  }

  leaveRoom(): void {
    if (this._socket) {
      console.log('🚪 Leaving room');
      this._socket.emit('leave-room');
    }
  }

  createRoom(roomName?: string): void {
    if (this._socket) {
      console.log('🏗️ Creating room:', roomName || 'Unnamed');
      this._socket.emit('create-room', { roomName });
    }
  }

  sendMessage(message: string): void {
    if (this._socket) {
      console.log('💬 Sending message:', message);
      this._socket.emit('chat-message', { message });
    }
  }

  // Event listener registration methods
  onAuthenticated(callback: (data: any) => void): void {
    this._socket?.on('authenticated', callback);
  }

  onRoomJoined(callback: (data: any) => void): void {
    this._socket?.on('room-joined', callback);
  }

  onRoomCreated(callback: (data: any) => void): void {
    this._socket?.on('room-created', callback);
  }

  onUserJoined(callback: (data: any) => void): void {
    this._socket?.on('user-joined', callback);
  }

  onUserLeft(callback: (data: any) => void): void {
    this._socket?.on('user-left', callback);
  }

  onRoomUsersUpdated(callback: (data: { users: User[] }) => void): void {
    this._socket?.on('room-users-updated', callback);
  }

  onChatMessage(callback: (message: ChatMessage) => void): void {
    this._socket?.on('chat-message', callback);
  }

  onError(callback: (error: any) => void): void {
    this._socket?.on('error', callback);
  }

  onConnect(callback: () => void): void {
    this._socket?.on('connect', callback);
  }

  onDisconnect(callback: () => void): void {
    this._socket?.on('disconnect', callback);
  }

  // Cleanup method to remove specific listeners
  off(event: string, callback?: Function): void {
    if (callback) {
      this._socket?.off(event, callback);
    } else {
      this._socket?.off(event);
    }
  }

  private setupEventListeners(): void {
    if (!this._socket) return;

    this._socket.on('connect', () => {
      console.log('✅ Connected to server, Socket ID:', this._socket?.id);
      // Re-authenticate if we have a token
      if (this.token) {
        console.log('🔐 Re-authenticating after reconnection');
        this.authenticate(this.token);
      }
    });

    this._socket.on('disconnect', (reason) => {
      console.log('❌ Disconnected from server. Reason:', reason);
    });

    this._socket.on('connect_error', (error) => {
      console.error('🚫 Socket connection error:', error);
    });

    this._socket.on('reconnect', (attemptNumber) => {
      console.log('🔄 Reconnected after', attemptNumber, 'attempts');
    });

    this._socket.on('reconnect_error', (error) => {
      console.error('🔄 Reconnection failed:', error);
    });
  }

  get isConnected(): boolean {
    return this._socket?.connected || false;
  }

  get socketId(): string | undefined {
    return this._socket?.id;
  }
}

// Export singleton instance
export const socketService = new SocketService();
export default socketService;
