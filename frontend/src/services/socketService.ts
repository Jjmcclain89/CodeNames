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
  private isConnecting: boolean = false;
  private connectionCounter: number = 0;
  private lastAuthenticatedToken: string | null = null;

  get socket(): Socket | null {
    return this._socket;
  }

  connect(): Socket {
    this.connectionCounter++;
    console.log('🔌 CONNECT() CALLED #' + this.connectionCounter);

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

    // Dynamic socket URL
    const currentHost = window.location.hostname;
    const isLocalhost = currentHost === 'localhost' || currentHost === '127.0.0.1';
    const socketPort = '3001';
    
    let socketUrl;
    if (import.meta.env.VITE_SOCKET_URL) {
      socketUrl = import.meta.env.VITE_SOCKET_URL;
    } else if (isLocalhost) {
      socketUrl = `http://localhost:${socketPort}`;
    } else {
      socketUrl = `http://${currentHost}:${socketPort}`;
    }

    this._socket = io(socketUrl, {
      autoConnect: false,
      transports: ['websocket', 'polling'],
      timeout: 5000,
      forceNew: false,
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
      this.isConnecting = false;
      this.lastAuthenticatedToken = null;
    }
  }

  authenticate(token: string): void {
    console.log('🔐 [SERVICE] authenticate called, socket connected:', this._socket?.connected);
    
    // Prevent duplicate authentication with the same token
    if (this.lastAuthenticatedToken === token && this._socket?.connected) {
      console.log('🔐 Already authenticated with this token');
      this._socket?.emit('authenticated', { success: true, user: { token } });
      return;
    }
    
    this.token = token;
    this.lastAuthenticatedToken = token;
    
    if (this._socket) {
      console.log('🔐 Emitting authenticate event to backend');
      this._socket.emit('authenticate', token);
    } else {
      console.log('❌ No socket available for authentication');
    }
  }

  // Event listener registration methods
  onAuthenticated(callback: (data: any) => void): void {
    this._socket?.on('authenticated', callback);
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
      this.isConnecting = false;
    });

    this._socket.on('disconnect', (reason) => {
      console.log('❌ Disconnected from server. Reason:', reason);
    });

    this._socket.on('connect_error', (error) => {
      console.error('🚫 Socket connection error:', error);
      this.isConnecting = false;
    });
  }

  get isConnected(): boolean {
    return this._socket?.connected || false;
  }

  get isAuthenticated(): boolean {
    return !!this.lastAuthenticatedToken && this.isConnected;
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
