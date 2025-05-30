Codenames Web App - Project Documentation
Project Knowledge
Game Mechanics
Core Codenames Rules

Objective: Teams compete to identify their agents (words) using one-word clues
Teams: Red team (goes first) and Blue team, each with 8-9 agents
Roles:

Spymasters: Give clues, can see all card colors
Field Operatives: Guess words based on clues


Special Cards:

Innocent Bystanders: 7 neutral cards (end turn if guessed)
Assassin: 1 black card (instant lose if guessed)


Game Colors:

Red team: #DC2626 (red-600)
Blue team: #2563EB (blue-600)
Neutral: #6B7280 (gray-500)
Assassin: #1F2937 (gray-800)


Win Conditions:

Contact all your team's agents first
Opponent hits the assassin card



Game Flow

Setup: 25 cards arranged in 5x5 grid with random words
Card Assignment: Random distribution of red/blue/neutral/assassin
Spymaster Selection: One player per team becomes spymaster
Turn Structure:

Spymaster gives clue (one word + number of related cards)
Field operatives discuss and make guesses
Turn ends on wrong guess, passing, or completing all guesses


Game End: First team to find all agents wins, or team that hits assassin loses

Clue Rules

Must be one word only
Cannot be a word on the board
Cannot be a variant/form of a word on the board
Number indicates maximum guesses (can guess fewer)
Can give "unlimited" clues (number = 0)

Technical Architecture
Frontend Technology Stack

Framework: React 18+ with TypeScript
State Management: React Context API or Redux Toolkit
Styling: CSS Modules, Styled Components, or Tailwind CSS
Real-time: Socket.io-client for WebSocket communication
Routing: React Router for navigation
UI Components: Custom components or library (Material-UI, Chakra UI)

Backend Technology Stack

Runtime: Node.js with Express.js
Database: PostgreSQL with Prisma ORM for type-safe database access
Real-time: Socket.io for WebSocket connections and room management
Authentication: JWT tokens with bcrypt for password hashing
Validation: Zod for schema validation and type safety
Environment Variables: dotenv for configuration management
Testing: Jest for unit tests, Supertest for API testing

Real-time Communication

WebSocket Events:

join-room, leave-room
game-start, game-end
give-clue, make-guess
turn-change, game-state-update
chat-message, player-disconnect



API Service Architecture

HTTP Client: Custom service wrapper around fetch API
Authentication: JWT tokens passed in Authorization headers
Error Handling: Centralized error handling with proper status codes
Type Safety: Zod schemas for request/response validation

Data Models
User Object
typescriptinterface User {
  id: string;
  username: string;
  avatarUrl?: string;
  createdAt: Date;
  gamesPlayed: number;
  gamesWon: number;
}
Game Room Object
typescriptinterface GameRoom {
  id: string;
  name: string;
  hostId: string;
  players: Player[];
  gameState: GameState;
  settings: RoomSettings;
  createdAt: Date;
  isActive: boolean;
}

interface RoomSettings {
  maxPlayers: number; // typically 4-8
  turnTimeLimit?: number; // in seconds
  customWordList?: string[];
  isPrivate: boolean;
}
Game State Object
typescriptinterface GameState {
  status: 'waiting' | 'active' | 'finished';
  currentTurn: 'red' | 'blue';
  board: Card[];
  redSpymaster: string; // player ID
  blueSpymaster: string; // player ID
  currentClue?: Clue;
  guessesRemaining: number;
  redAgentsLeft: number;
  blueAgentsLeft: number;
  winner?: 'red' | 'blue';
  turnHistory: TurnHistory[];
}

interface Card {
  id: string;
  word: string;
  type: 'red' | 'blue' | 'neutral' | 'assassin';
  isRevealed: boolean;
  position: number; // 0-24 for 5x5 grid
}

interface Clue {
  word: string;
  number: number;
  spymasterId: string;
  timestamp: Date;
}
Player Object
typescriptinterface Player {
  id: string;
  userId: string;
  username: string;
  team: 'red' | 'blue' | 'spectator';
  role: 'spymaster' | 'operative';
  isConnected: boolean;
  joinedAt: Date;
}
Project Instructions
Development Workflow
Git Branching Strategy (Solo Development)

Main Branch: main - production ready code
Feature Branches: feature/[description] - for new features
Hotfix Branches: hotfix/[issue-description] - for urgent fixes
Experiment Branches: experiment/[idea] - for trying new approaches

Development Process

Create feature branch from main
Implement feature with tests
Run full test suite locally
Merge to main when feature is complete
Tag releases with semantic versioning
Keep commit history clean with meaningful messages

Testing Requirements

Unit Tests: Minimum 80% code coverage
Integration Tests: All API endpoints
E2E Tests: Critical user journeys
Game Logic Tests: Complete game scenarios
Real-time Tests: WebSocket event handling

Coding Standards
TypeScript Configuration
json{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "noImplicitReturns": true,
    "noUncheckedIndexedAccess": true
  }
}
File Organization
codenames-app/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Game/
│   │   │   ├── Room/
│   │   │   └── UI/
│   │   ├── hooks/
│   │   ├── context/
│   │   ├── services/
│   │   ├── types/
│   │   ├── utils/
│   │   └── constants/
│   ├── public/
│   └── package.json
├── backend/
│   ├── src/
│   │   ├── routes/
│   │   ├── models/
│   │   ├── services/
│   │   ├── middleware/
│   │   ├── socket/
│   │   ├── utils/
│   │   └── types/
│   ├── tests/
│   └── package.json
└── shared/
    └── types/
Naming Conventions

Components: PascalCase (GameBoard.tsx)
Hooks: camelCase with "use" prefix (useGameState.ts)
Constants: SCREAMING_SNAKE_CASE (MAX_PLAYERS)
Utilities: camelCase (generateGameId.ts)
Types: PascalCase with Interface/Type suffix (GameStateType)

Documentation Requirements

Components: JSDoc comments with prop descriptions
Functions: Clear parameter and return type documentation
Complex Logic: Inline comments explaining business rules
API Endpoints: OpenAPI/Swagger documentation

Common Tasks
Adding New Features

Create feature branch from develop
Update type definitions in types/ directory
Implement backend API endpoints with validation
Add corresponding frontend components/hooks
Write comprehensive tests
Update documentation
Test integration with existing features

Database Migrations

Create migration file with timestamp
Write both up and down migrations
Test migration on development database
Update data models and types
Coordinate deployment with team

Adding New WebSocket Events

Define event types in shared types file
Implement server-side event handlers with JWT authentication
Add client-side event listeners
Update game state management
Add error handling for disconnections
Test with multiple clients

Authentication Flow
typescript// Socket.io connection with JWT
const socket = io('http://localhost:3001', {
  auth: {
    token: localStorage.getItem('accessToken')
  }
});

// Server-side authentication middleware
io.use((socket, next) => {
  const token = socket.handshake.auth.token;
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    socket.userId = decoded.userId;
    next();
  } catch (err) {
    next(new Error('Authentication error'));
  }
});
Handling Game States
typescript// Example state transition
const handleCardGuess = (cardId: string) => {
  const card = findCardById(cardId);
  
  // Validate guess is allowed
  if (!canMakeGuess(gameState, currentPlayer)) {
    throw new Error('Invalid guess attempt');
  }
  
  // Update card and game state
  const updatedState = {
    ...gameState,
    board: revealCard(gameState.board, cardId),
    guessesRemaining: calculateRemainingGuesses(card, gameState)
  };
  
  // Check win conditions
  const winner = checkWinCondition(updatedState);
  if (winner) {
    updatedState.status = 'finished';
    updatedState.winner = winner;
  }
  
  // Broadcast state update
  broadcastGameState(roomId, updatedState);
};
Solo Development Organization
Project Management

Task Tracking: Use GitHub Issues or a simple todo list
Feature Planning: Break down features into small, manageable tasks
Progress Tracking: Regular commits with descriptive messages
Milestone Planning: Set realistic deadlines for major features

Development Phases

Phase 1: Basic game mechanics and local multiplayer
Phase 2: WebSocket integration for real-time play
Phase 3: Room management and player matching
Phase 4: UI polish and responsive design
Phase 5: Deployment and performance optimization

Decision Documentation

Keep a simple DECISIONS.md file for architectural choices
Document why certain technologies or patterns were chosen
Note trade-offs and alternatives considered
Review decisions periodically as the project grows

Development & Testing
Local Development Setup

Backend: npm run dev with nodemon for auto-restart
Frontend: npm run dev with Vite for hot module replacement
Database: Local PostgreSQL or MongoDB instance
Environment: Separate .env files for different configurations

Testing Strategy

Backend: Jest for unit tests, Supertest for API integration tests
Frontend: React Testing Library for component tests
E2E: Playwright or Cypress for full user journey tests
Game Logic: Comprehensive tests for all game rules and edge cases

Performance Considerations

WebSocket Optimization: Efficient event handling and state updates
Memory Management: Proper cleanup of game rooms and player sessions
Database Queries: Indexed queries and connection pooling
Frontend Performance: Code splitting and lazy loading