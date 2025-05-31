# Codenames Web App

A real-time multiplayer implementation of the popular board game Codenames, built with React, Node.js, and Socket.io.

## 🎯 Project Overview

Codenames is a social word game where two teams compete to identify their agents using one-word clues. This web application brings the game online with real-time multiplayer functionality, allowing players to create rooms, join games, and play with friends from anywhere.

### Core Features
- Real-time multiplayer gameplay with WebSocket communication
- Team-based gameplay with spymaster and operative roles
- Room creation and management system
- Responsive design for desktop and mobile
- Spectator mode for watching games
- Custom word lists and game settings

## 🚀 Tech Stack

### Frontend
- **React 18+** with TypeScript
- **Vite** for fast development and building
- **Socket.io-client** for real-time communication
- **Tailwind CSS** for styling
- **React Router** for navigation

### Backend
- **Node.js** with Express.js
- **Socket.io** for WebSocket communication
- **PostgreSQL** with Prisma ORM
- **JWT** for authentication
- **Zod** for schema validation

### Development Tools
- **TypeScript** for type safety
- **Jest** for testing
- **ESLint** for code quality
- **Git** for version control

## 🏗️ Development Approach

This project follows a **socket-first development strategy** to validate the core technical architecture early and avoid building throwaway code.

### Development Phases

#### Phase 0: Project Foundation (Week 1)
- ✅ Repository structure and Git setup
- ✅ Package.json files with core dependencies
- ✅ TypeScript configuration
- 🔄 Database setup and basic server structure

#### Phase 1: Socket Foundation (Week 2) ✅ COMPLETE
**Goal: Two browsers can connect and communicate**
- Backend Socket.io integration with room management
- Frontend socket connection and auth
- Real-time messaging between clients
- Basic user authentication

#### Phase 2: Core Game Logic (Weeks 3-4)
**Goal: Functional multiplayer Codenames game**
- Server-side game state management
- Real-time game synchronization
- Interactive game board
- Complete game mechanics implementation

#### Phase 3: Features & Polish (Weeks 5-7)
**Goal: Feature-complete, polished experience**
- Advanced room management
- UI/UX improvements
- Performance optimization
- Accessibility features

#### Phase 4: Production Ready (Weeks 8-9)
**Goal: Deployed, stable application**
- Security hardening
- Deployment configuration
- Performance monitoring
- Final testing and launch

## 🔧 Setup Instructions

### Prerequisites
- Node.js (v18 or higher)
- PostgreSQL
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd codenames-app
   ```

2. **Install dependencies**
   ```bash
   # Backend dependencies
   cd backend && npm install
   
   # Frontend dependencies
   cd ../frontend && npm install
   ```

3. **Environment setup**
   ```bash
   # Copy environment templates
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   
   # Edit the .env files with your configuration
   ```

4. **Database setup**
   ```bash
   cd backend
   npx prisma migrate dev
   npx prisma generate
   ```

5. **Start development servers**
   ```bash
   # Backend (from backend/ directory)
   npm run dev
   
   # Frontend (from frontend/ directory)
   npm run dev
   ```

The application will be available at:
- Frontend: http://localhost:5173
- Backend: http://localhost:3001


### Development Sessions

For consistent development workflow, see [SESSION_WORKFLOW.md](SESSION_WORKFLOW.md) which includes:
- Session start/end checklists
- Project structure mapping procedures  
- File management guidelines
- Phase-specific workflows
- Troubleshooting common issues

**Quick Start for Each Session:**
```bash
# 1. Map current project structure
python python/directory_mapper.py

# 2. Start development based on current phase
# 3. End session with updated structure and summary
```

## 🎮 Game Rules

### Objective
Teams compete to identify their agents (words) on a 5x5 grid using one-word clues from their spymaster.

### Teams & Roles
- **Red Team** and **Blue Team** (8-9 agents each)
- **Spymasters**: Give clues and can see all card colors
- **Field Operatives**: Guess words based on clues

### Special Cards
- **Innocent Bystanders**: 7 neutral cards (end turn if guessed)
- **Assassin**: 1 black card (instant lose if guessed)

### Win Conditions
- Contact all your team's agents first, OR
- Opponent hits the assassin card

## 📁 Project Structure

```
codenames-app/
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API and socket services
│   │   ├── types/          # TypeScript types
│   │   └── utils/          # Utility functions
│   └── package.json
├── backend/
│   ├── src/
│   │   ├── routes/         # Express routes
│   │   ├── services/       # Business logic
│   │   ├── socket/         # Socket.io handlers
│   │   ├── models/         # Data models
│   │   └── middleware/     # Express middleware
│   └── package.json
├── shared/
│   └── types/              # Shared TypeScript types
└── docs/                   # Documentation
```

## 🧪 Testing

```bash
# Backend tests
cd backend && npm test

# Frontend tests
cd frontend && npm test

# Run all tests
npm run test:all
```

## 🚀 Deployment

Deployment instructions will be added as part of Phase 4. The application is designed to be deployed on modern cloud platforms with support for:
- Static frontend hosting
- Node.js backend hosting
- PostgreSQL database
- WebSocket connections

## 📝 Development Workflow

### Commit Strategy
- Commit daily with meaningful progress
- Use conventional commit messages
- Create feature branches for larger changes
- Maintain clean commit history

### Testing Approach
- Manual testing with multiple browser windows
- Automated tests for critical game logic
- Integration testing for socket events
- User testing with friends/family

## 🤝 Contributing

This is currently a solo development project following the development plan outlined above. The codebase is designed with clean architecture and comprehensive documentation to facilitate future collaboration.

## 📄 License

[License information to be added]

## 📞 Support

For questions or issues, please refer to the project documentation or create an issue in the repository.

---

**Current Status**: Phase 1 - Socket Foundation ✅ | Phase 2 - Core Game Logic 🚀

## 📅 Session Summary - 2025-05-31

### 🎯 **Phase 2 Progress: Core Game Logic**

**✅ COMPLETED:**
- **Backend Game Foundation**: Complete game models, services, and socket infrastructure (untested)
- **Frontend Game Components**: GameBoard, Card components, and game service integration  
- **Shared Type System**: Comprehensive game types and interfaces
- **Authentication System**: Socket authentication flow working
- **Debug Infrastructure**: Testing controls and comprehensive logging

**🔧 CURRENT STATUS:**
- **Game Logic**: Implemented but untested (backend)
- **Socket Events**: Game events functional but need refinement
- **UI Components**: Game board and card rendering complete
- **Game State Loading**: Backend not properly sending initial game state to frontend

**❌ BLOCKERS:**
- Game page shows loading spinner indefinitely - backend not sending game state
- Frontend/backend game state synchronization broken
- Actual game mechanics untested (card revealing, clues, win conditions)

### 📂 **Key Files Implemented:**
- `backend/src/models/Game.ts` - Complete Codenames game logic
- `backend/src/services/gameService.ts` - Game state management
- `backend/src/socket/socketHandlers.ts` - Socket event handlers
- `frontend/src/components/GameBoard/GameBoard.tsx` - Main game interface
- `frontend/src/components/GameBoard/Card.tsx` - Game card component
- `frontend/src/services/gameService.ts` - Frontend game service
- `shared/types/game.ts` - Game type definitions

### 🎯 **Next Session Goals:**
1. **Homepage Design**: Create clean UI for game creation/joining flow
2. **Create Game Flow**: Generate game codes and route users to new games
3. **Join Game Flow**: Validate game codes and route users to existing games
4. **Game State Fix**: Repair backend game state transmission (if time permits)
5. **Game Logic Testing**: Test actual Codenames mechanics end-to-end (future priority)

**Note**: Room = Game (simplified architecture focus)

### 💡 **Technical Architecture Ready:**
- ✅ Real-time multiplayer foundation (Socket.io)
- ⚠️ Complete game rule implementation (needs testing)
- ✅ Type-safe frontend/backend communication
- ✅ Game-based architecture (room = game)
- ✅ Authentication and user management

**Phase 2 Core Game Logic: 70% Complete** 🎮

---

