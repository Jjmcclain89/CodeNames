# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

**Note: This project is developed using WSL (Windows Subsystem for Linux) with Claude Code**

### Backend Development
```bash
cd backend
npm run dev          # Start backend with hot-reload (nodemon)
npm run build        # Compile TypeScript to JavaScript
npm run lint         # Run ESLint on TypeScript files
npm test             # Run Jest tests
npm run db:migrate   # Apply Prisma database migrations
npm run db:generate  # Generate Prisma client
npm run db:studio    # Open Prisma Studio GUI
```

### Frontend Development
```bash
cd frontend
npm run dev          # Start Vite dev server (hot-reload)
npm run build        # TypeScript check + Vite build
npm run lint         # ESLint with TypeScript support
npm test             # Run Vitest tests
npm run test:ui      # Run Vitest with UI
```

### Common Development Workflow
```bash
# Start both servers (run in separate terminals within WSL)
cd backend && npm run dev   # Runs on port 3001
cd frontend && npm run dev  # Runs on port 5173

# Before committing
cd backend && npm run lint
cd frontend && npm run lint
```

## Architecture Overview

### Project Structure
- **Monorepo** with separate `frontend/` and `backend/` directories
- **Shared types** in `shared/types/` for TypeScript consistency
- **Real-time multiplayer** using Socket.io for game synchronization

### Backend Architecture
- **Express + Socket.io** server with TypeScript
- **Game state management** in `services/gameService.ts` - server-authoritative game logic
- **Socket handlers** in `src/index.ts` with room-based event broadcasting
- **In-memory storage** for Phase 1/2 (users, rooms, game states)
- **Prisma ORM** with PostgreSQL (schema defined, not yet implemented)
- **JWT-style tokens** for simple authentication

### Frontend Architecture
- **React 18 + TypeScript** with Vite for fast development
- **Socket.io-client** integration in `services/socketService.ts`
- **Game state synchronization** through socket events
- **Routing**: Direct game access via `/game/:gameCode`
- **Tailwind CSS** for styling

### Key Game Flow
1. User logs in → Gets token → Socket authenticates
2. User creates/joins game → Joins socket room → Receives game state
3. Game actions → Server validates → Broadcasts state to room
4. Real-time sync ensures all players see same game state

### Socket Events Pattern
- Client emits: `game:join-team`, `game:reveal-card`, etc.
- Server validates action in `gameService`
- Server broadcasts: `game:state-updated` to all room members
- Frontend updates UI based on new state

### Current Development Phase
- **Phase 2: Core Game Logic** - Implementing multiplayer Codenames gameplay
- Focus on team assignment, game state management, and real-time synchronization

### Important Implementation Details
- Game state is **server-authoritative** - all game logic validated server-side
- Each game has a unique 6-character room code (e.g., "ABC123")
- Players automatically join "GLOBAL" room on connection for Phase 1 compatibility
- Socket authentication required before any game actions
- Game state includes full board, teams, current turn, and history

### Common Issues & Solutions
- **Socket connection fails**: Check CORS in backend, verify token handling
- **Game state not updating**: Ensure socket room joining and event broadcasting
- **Team assignment issues**: Check player exists in game before assignment
- **Frontend proxy**: Vite proxy configured for `/api` → `http://localhost:3001`