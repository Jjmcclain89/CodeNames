import { useEffect, useRef, useState } from 'react';
import socketService, { User, Room, ChatMessage } from '../services/socketService';

export const useSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [currentRoom, setCurrentRoom] = useState<Room | null>(null);
  const [roomUsers, setRoomUsers] = useState<User[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [connectionError, setConnectionError] = useState<string | null>(null);

  // Use refs to store callbacks to avoid re-registering listeners
  const handlersRef = useRef({
    onConnect: () => {
      setIsConnected(true);
      setConnectionError(null);
    },
    onDisconnect: () => {
      setIsConnected(false);
    },
    onAuthenticated: (data: any) => {
      if (data.success) {
        console.log('Authenticated successfully');
      } else {
        console.error('Authentication failed:', data.error);
        setConnectionError(data.error);
      }
    },
    onRoomJoined: (data: any) => {
      setCurrentRoom(data.room);
      setMessages([]); // Clear messages when joining new room
      console.log('Joined room:', data.room.code);
    },
    onRoomCreated: (data: any) => {
      console.log('Room created:', data.room.code);
    },
    onUserJoined: (data: any) => {
      console.log('User joined:', data.username);
    },
    onUserLeft: (data: any) => {
      console.log('User left:', data.username);
    },
    onRoomUsersUpdated: (data: { users: User[] }) => {
      setRoomUsers(data.users);
    },
    onChatMessage: (message: ChatMessage) => {
      setMessages(prev => [...prev, message]);
    },
    onError: (error: any) => {
      console.error('Socket error:', error);
      setConnectionError(error.message);
    }
  });

  useEffect(() => {
    // Don't auto-connect - let App.tsx handle connection
    const socket = socketService.socket;
    if (!socket) {
      console.log('⚠️ useSocket: No socket available, waiting for App.tsx to connect');
      return;
    }
    const handlers = handlersRef.current;

    // Register event listeners
    socketService.onConnect(handlers.onConnect);
    socketService.onDisconnect(handlers.onDisconnect);
    socketService.onAuthenticated(handlers.onAuthenticated);
    socketService.onRoomJoined(handlers.onRoomJoined);
    socketService.onRoomCreated(handlers.onRoomCreated);
    socketService.onUserJoined(handlers.onUserJoined);
    socketService.onUserLeft(handlers.onUserLeft);
    socketService.onRoomUsersUpdated(handlers.onRoomUsersUpdated);
    socketService.onChatMessage(handlers.onChatMessage);
    socketService.onError(handlers.onError);

    return () => {
      // Cleanup listeners
      socketService.off('connect', handlers.onConnect);
      socketService.off('disconnect', handlers.onDisconnect);
      socketService.off('authenticated', handlers.onAuthenticated);
      socketService.off('room-joined', handlers.onRoomJoined);
      socketService.off('room-created', handlers.onRoomCreated);
      socketService.off('user-joined', handlers.onUserJoined);
      socketService.off('user-left', handlers.onUserLeft);
      socketService.off('room-users-updated', handlers.onRoomUsersUpdated);
      socketService.off('chat-message', handlers.onChatMessage);
      socketService.off('error', handlers.onError);
    };
  }, []);

  const authenticate = (token: string) => {
    socketService.authenticate(token);
  };

  const joinRoom = (roomCode: string) => {
    socketService.joinRoom(roomCode);
  };

  const leaveRoom = () => {
    socketService.leaveRoom();
    setCurrentRoom(null);
    setRoomUsers([]);
    setMessages([]);
  };

  const createRoom = (roomName?: string) => {
    socketService.createRoom(roomName);
  };

  const sendMessage = (message: string) => {
    socketService.sendMessage(message);
  };

  return {
    isConnected,
    currentRoom,
    roomUsers,
    messages,
    connectionError,
    authenticate,
    joinRoom,
    leaveRoom,
    createRoom,
    sendMessage
  };
};
