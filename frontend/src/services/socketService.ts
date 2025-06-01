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
  private isConnecting: boolean = false; // Track connection in progress

  get socket(): Socket | null {
    return this._socket;
  }

  connect(): Socket {
    // Track what is calling connect
    console.log('🔌 CONNECT() CALLED');
    console.log('🔌 Call stack:', new Error().stack);
    console.log('🔌 Current socket state:', {
      hasSocket: !!this._socket,
      isConnected: this._socket?.connected,
      isConnecting: this.isConnecting
    });

    // Make socket service accessible for debugging
    (window as any).socketService = this;

    // Check if already connected
    if (this._socket?.connected) {
      console.log('📡 Socket already connected, reusing existing connection');
      return this._socket;
    }

    // Check if connection is in progress
    if (this.isConnecting) {
      console.log('📡 Connection already in progress, waiting...');
      return this._socket!;
    }

    // Check if socket exists but is disconnected
    if (this._socket && !this._socket.connected) {
      console.log('📡 Reconnecting existing socket');
      this._socket.connect();
      return this._socket;
    }

    console.log('📡 Creating new socket connection');
    this.isConnecting = true;

    const socketUrl = import.meta.env.VITE_SOCKET_URL || 'http://localhost:3001';
    console.log('📡 Connecting to socket server:', socketUrl);

    this._socket = io(socketUrl, {
      autoConnect: false,
      transports: ['websocket', 'polling'],
      timeout: 5000,
      forceNew: false, // Don't force new connections
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
      this.isConnecting = false; // Reset connection state
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
      console.log('🔌 Connect event fired - total event listeners:', this._socket?.listeners('connect').length);
      this.isConnecting = false; // Connection completed
      
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
      this.isConnecting = false; // Reset on connection error
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

  get isConnectionReady(): boolean {
    return this._socket?.connected && !this.isConnecting;
  }

  get socketId(): string | undefined {
    return this._socket?.id;
  }
}

// Export singleton instance
export const socketService = new SocketService();
export default socketService;
