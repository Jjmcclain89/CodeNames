#!/usr/bin/env python3
"""
Initial Codenames Web App Project Setup Script
Creates the complete project structure, configurations, and basic files.
"""

import os
import json
import datetime
from pathlib import Path

def create_directory_structure():
    """Create the complete directory structure for the project."""
    directories = [
        # Frontend structure
        "frontend/src/components/Game",
        "frontend/src/components/Room", 
        "frontend/src/components/UI",
        "frontend/src/hooks",
        "frontend/src/context",
        "frontend/src/services",
        "frontend/src/types",
        "frontend/src/utils",
        "frontend/src/constants",
        "frontend/public",
        
        # Backend structure
        "backend/src/routes",
        "backend/src/models",
        "backend/src/services",
        "backend/src/middleware",
        "backend/src/socket",
        "backend/src/utils",
        "backend/src/types",
        "backend/tests",
        
        # Shared types
        "shared/types",
        
        # Python scripts directory
        "python"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def create_package_json_files():
    """Create package.json files for frontend and backend."""
    
    # Frontend package.json
    frontend_package = {
        "name": "codenames-frontend",
        "private": True,
        "version": "0.1.0",
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "tsc && vite build",
            "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
            "preview": "vite preview",
            "test": "vitest",
            "test:ui": "vitest --ui"
        },
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "react-router-dom": "^6.21.0",
            "socket.io-client": "^4.7.4",
            "@hookform/resolvers": "^3.3.2",
            "react-hook-form": "^7.48.2",
            "zod": "^3.22.4",
            "clsx": "^2.1.0"
        },
        "devDependencies": {
            "@types/react": "^18.2.43",
            "@types/react-dom": "^18.2.17",
            "@typescript-eslint/eslint-plugin": "^6.14.0",
            "@typescript-eslint/parser": "^6.14.0",
            "@vitejs/plugin-react": "^4.2.1",
            "eslint": "^8.55.0",
            "eslint-plugin-react-hooks": "^4.6.0",
            "eslint-plugin-react-refresh": "^0.4.5",
            "typescript": "^5.2.2",
            "vite": "^5.0.8",
            "vitest": "^1.1.0",
            "@vitest/ui": "^1.1.0",
            "@testing-library/react": "^14.1.2",
            "@testing-library/jest-dom": "^6.1.5",
            "tailwindcss": "^3.4.0",
            "autoprefixer": "^10.4.16",
            "postcss": "^8.4.32"
        }
    }
    
    # Backend package.json  
    backend_package = {
        "name": "codenames-backend",
        "version": "0.1.0",
        "description": "Backend server for Codenames web app",
        "main": "dist/index.js",
        "scripts": {
            "dev": "nodemon src/index.ts",
            "build": "tsc",
            "start": "node dist/index.js",
            "test": "jest",
            "test:watch": "jest --watch",
            "lint": "eslint src --ext .ts",
            "db:migrate": "prisma migrate dev",
            "db:generate": "prisma generate",
            "db:studio": "prisma studio"
        },
        "dependencies": {
            "express": "^4.18.2",
            "socket.io": "^4.7.4",
            "jsonwebtoken": "^9.0.2",
            "bcryptjs": "^2.4.3",
            "cors": "^2.8.5",
            "dotenv": "^16.3.1",
            "zod": "^3.22.4",
            "@prisma/client": "^5.7.1",
            "helmet": "^7.1.0",
            "express-rate-limit": "^7.1.5"
        },
        "devDependencies": {
            "@types/express": "^4.17.21",
            "@types/jsonwebtoken": "^9.0.5",
            "@types/bcryptjs": "^2.4.6",
            "@types/cors": "^2.8.17",
            "@types/node": "^20.10.5",
            "@typescript-eslint/eslint-plugin": "^6.14.0",
            "@typescript-eslint/parser": "^6.14.0",
            "eslint": "^8.55.0",
            "jest": "^29.7.0",
            "@types/jest": "^29.5.8",
            "supertest": "^6.3.3",
            "@types/supertest": "^6.0.2",
            "nodemon": "^3.0.2",
            "ts-node": "^10.9.2",
            "typescript": "^5.2.2",
            "prisma": "^5.7.1"
        }
    }
    
    with open("frontend/package.json", "w", encoding='utf-8') as f:
        json.dump(frontend_package, f, indent=2)
    print("✓ Created frontend/package.json")
    
    with open("backend/package.json", "w", encoding='utf-8') as f:
        json.dump(backend_package, f, indent=2)
    print("✓ Created backend/package.json")

def create_docker_configuration():
    """Create Docker configuration files."""
    
    # Docker Compose
    docker_compose = """version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: codenames-db
    environment:
      POSTGRES_DB: codenames_dev
      POSTGRES_USER: codenames_user
      POSTGRES_PASSWORD: codenames_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/prisma/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - codenames-network

  redis:
    image: redis:7-alpine
    container_name: codenames-redis
    ports:
      - "6379:6379"
    networks:
      - codenames-network

volumes:
  postgres_data:

networks:
  codenames-network:
    driver: bridge
"""
    
    with open("docker-compose.yml", "w", encoding='utf-8') as f:
        f.write(docker_compose)
    print("✓ Created docker-compose.yml")
    
    # .dockerignore
    dockerignore = """node_modules
npm-debug.log
dist
.git
.gitignore
README.md
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
coverage/
.coverage
*.log
"""
    
    with open(".dockerignore", "w", encoding='utf-8') as f:
        f.write(dockerignore)
    print("✓ Created .dockerignore")

def create_typescript_configs():
    """Create TypeScript configuration files."""
    
    # Frontend TypeScript config
    frontend_tsconfig = {
        "compilerOptions": {
            "target": "ES2020",
            "useDefineForClassFields": True,
            "lib": ["ES2020", "DOM", "DOM.Iterable"],
            "module": "ESNext",
            "skipLibCheck": True,
            "moduleResolution": "bundler",
            "allowImportingTsExtensions": True,
            "resolveJsonModule": True,
            "isolatedModules": True,
            "noEmit": True,
            "jsx": "react-jsx",
            "strict": True,
            "noImplicitAny": True,
            "noImplicitReturns": True,
            "noUncheckedIndexedAccess": True,
            "noUnusedLocals": True,
            "noUnusedParameters": True,
            "noFallthroughCasesInSwitch": True,
            "baseUrl": ".",
            "paths": {
                "@/*": ["./src/*"],
                "@shared/*": ["../shared/*"]
            }
        },
        "include": ["src"],
        "references": [{"path": "./tsconfig.node.json"}]
    }
    
    # Frontend Node TypeScript config
    frontend_tsconfig_node = {
        "compilerOptions": {
            "composite": True,
            "skipLibCheck": True,
            "module": "ESNext",
            "moduleResolution": "bundler",
            "allowSyntheticDefaultImports": True
        },
        "include": ["vite.config.ts"]
    }
    
    # Backend TypeScript config
    backend_tsconfig = {
        "compilerOptions": {
            "target": "ES2020",
            "module": "commonjs",
            "lib": ["ES2020"],
            "outDir": "./dist",
            "rootDir": "./src",
            "strict": True,
            "noImplicitAny": True,
            "noImplicitReturns": True,
            "noUncheckedIndexedAccess": True,
            "esModuleInterop": True,
            "skipLibCheck": True,
            "forceConsistentCasingInFileNames": True,
            "resolveJsonModule": True,
            "declaration": True,
            "declarationMap": True,
            "sourceMap": True,
            "baseUrl": ".",
            "paths": {
                "@/*": ["./src/*"],
                "@shared/*": ["../shared/*"]
            }
        },
        "include": ["src/**/*"],
        "exclude": ["node_modules", "dist", "tests"]
    }
    
    with open("frontend/tsconfig.json", "w", encoding='utf-8') as f:
        json.dump(frontend_tsconfig, f, indent=2)
    print("✓ Created frontend/tsconfig.json")
    
    with open("frontend/tsconfig.node.json", "w", encoding='utf-8') as f:
        json.dump(frontend_tsconfig_node, f, indent=2)
    print("✓ Created frontend/tsconfig.node.json")
    
    with open("backend/tsconfig.json", "w", encoding='utf-8') as f:
        json.dump(backend_tsconfig, f, indent=2)
    print("✓ Created backend/tsconfig.json")

def create_environment_files():
    """Create environment configuration files."""
    
    # Backend .env template
    backend_env = """# Database
DATABASE_URL="postgresql://codenames_user:codenames_password@localhost:5432/codenames_dev"

# JWT
JWT_SECRET="your-super-secret-jwt-key-change-this-in-production"
JWT_EXPIRES_IN="7d"

# Server
PORT=3001
NODE_ENV="development"

# CORS
FRONTEND_URL="http://localhost:5173"

# Redis (for session management if needed)
REDIS_URL="redis://localhost:6379"
"""
    
    # Frontend .env template
    frontend_env = """# API Configuration
VITE_API_URL=http://localhost:3001
VITE_WS_URL=http://localhost:3001

# Environment
VITE_NODE_ENV=development
"""
    
    with open("backend/.env.example", "w", encoding='utf-8') as f:
        f.write(backend_env)
    print("✓ Created backend/.env.example")
    
    with open("frontend/.env.example", "w", encoding='utf-8') as f:
        f.write(frontend_env)
    print("✓ Created frontend/.env.example")

def create_gitignore_files():
    """Create .gitignore files."""
    
    # Root .gitignore
    root_gitignore = """# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Build outputs
dist/
build/
coverage/

# Database
*.sqlite
*.db

# Logs
logs
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Docker
docker-compose.override.yml

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.env
.venv

# Prisma
prisma/migrations/
"""
    
    with open(".gitignore", "w", encoding='utf-8') as f:
        f.write(root_gitignore)
    print("✓ Created .gitignore")

def create_basic_configurations():
    """Create basic configuration files for tools."""
    
    # Vite config for frontend
    vite_config = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@shared': path.resolve(__dirname, '../shared')
    }
  },
  server: {
    port: 5173,
    host: true
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts'
  }
})
"""
    
    # Tailwind config
    tailwind_config = """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'game-red': '#DC2626',
        'game-blue': '#2563EB', 
        'game-neutral': '#6B7280',
        'game-assassin': '#1F2937'
      }
    },
  },
  plugins: [],
}
"""
    
    # Prisma schema
    prisma_schema = """generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id          String   @id @default(cuid())
  username    String   @unique
  email       String   @unique
  password    String
  avatarUrl   String?
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
  gamesPlayed Int      @default(0)
  gamesWon    Int      @default(0)
  
  // Relations
  hostedRooms GameRoom[] @relation("RoomHost")
  playerSessions Player[]
  
  @@map("users")
}

model GameRoom {
  id        String   @id @default(cuid())
  name      String
  hostId    String
  isActive  Boolean  @default(true)
  isPrivate Boolean  @default(false)
  maxPlayers Int     @default(8)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  
  // Relations
  host      User     @relation("RoomHost", fields: [hostId], references: [id])
  players   Player[]
  gameState GameState?
  
  @@map("game_rooms")
}

model Player {
  id          String   @id @default(cuid())
  userId      String
  roomId      String
  username    String
  team        String?  // 'red' | 'blue' | 'spectator'
  role        String?  // 'spymaster' | 'operative'
  isConnected Boolean  @default(true)
  joinedAt    DateTime @default(now())
  
  // Relations
  user User     @relation(fields: [userId], references: [id])
  room GameRoom @relation(fields: [roomId], references: [id])
  
  @@unique([userId, roomId])
  @@map("players")
}

model GameState {
  id               String   @id @default(cuid())
  roomId           String   @unique
  status           String   @default("waiting") // 'waiting' | 'active' | 'finished'
  currentTurn      String?  // 'red' | 'blue'
  redSpymaster     String?
  blueSpymaster    String?
  currentClue      Json?
  guessesRemaining Int      @default(0)
  redAgentsLeft    Int      @default(9)
  blueAgentsLeft   Int      @default(8)
  winner           String?  // 'red' | 'blue'
  board            Json     // Card array
  turnHistory      Json     @default("[]")
  createdAt        DateTime @default(now())
  updatedAt        DateTime @updatedAt
  
  // Relations
  room GameRoom @relation(fields: [roomId], references: [id])
  
  @@map("game_states")
}
"""
    
    with open("frontend/vite.config.ts", "w", encoding='utf-8') as f:
        f.write(vite_config)
    print("✓ Created frontend/vite.config.ts")
    
    with open("frontend/tailwind.config.js", "w", encoding='utf-8') as f:
        f.write(tailwind_config)
    print("✓ Created frontend/tailwind.config.js")
    
    # Create Prisma directory and schema
    Path("backend/prisma").mkdir(parents=True, exist_ok=True)
    with open("backend/prisma/schema.prisma", "w", encoding='utf-8') as f:
        f.write(prisma_schema)
    print("✓ Created backend/prisma/schema.prisma")

def create_basic_files():
    """Create basic starter files."""
    
    # Frontend index.html
    index_html = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Codenames</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
"""
    
    # Frontend main.tsx
    main_tsx = """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""
    
    # Frontend App.tsx
    app_tsx = """import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { GameContextProvider } from './context/GameContext'
import HomePage from './components/UI/HomePage'
import GamePage from './components/Game/GamePage'
import './App.css'

function App() {
  return (
    <GameContextProvider>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/game/:roomId" element={<GamePage />} />
          </Routes>
        </div>
      </Router>
    </GameContextProvider>
  )
}

export default App
"""
    
    # Backend index.ts
    backend_index = """import express from 'express'
import cors from 'cors'
import helmet from 'helmet'
import dotenv from 'dotenv'
import { createServer } from 'http'
import { Server } from 'socket.io'
import rateLimit from 'express-rate-limit'

// Load environment variables
dotenv.config()

const app = express()
const server = createServer(app)
const io = new Server(server, {
  cors: {
    origin: process.env.FRONTEND_URL || "http://localhost:5173",
    methods: ["GET", "POST"]
  }
})

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
})

// Middleware
app.use(helmet())
app.use(cors({
  origin: process.env.FRONTEND_URL || "http://localhost:5173"
}))
app.use(express.json())
app.use(limiter)

// Basic health check
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() })
})

// Socket.io connection handling
io.on('connection', (socket) => {
  console.log('User connected:', socket.id)
  
  socket.on('disconnect', () => {
    console.log('User disconnected:', socket.id)
  })
})

const PORT = process.env.PORT || 3001

server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`)
  console.log(`Socket.io server ready`)
})
"""
    
    with open("frontend/index.html", "w", encoding='utf-8') as f:
        f.write(index_html)
    print("✓ Created frontend/index.html")
    
    with open("frontend/src/main.tsx", "w", encoding='utf-8') as f:
        f.write(main_tsx)
    print("✓ Created frontend/src/main.tsx")
    
    with open("frontend/src/App.tsx", "w", encoding='utf-8') as f:
        f.write(app_tsx)
    print("✓ Created frontend/src/App.tsx")
    
    with open("backend/src/index.ts", "w", encoding='utf-8') as f:
        f.write(backend_index)
    print("✓ Created backend/src/index.ts")

def create_css_files():
    """Create basic CSS files."""
    
    index_css = """@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
  line-height: 1.5;
  font-weight: 400;

  color-scheme: light dark;
  color: rgba(255, 255, 255, 0.87);
  background-color: #242424;

  font-synthesis: none;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  -webkit-text-size-adjust: 100%;
}

body {
  margin: 0;
  padding: 0;
  min-height: 100vh;
}

#root {
  min-height: 100vh;
}

/* Game-specific styles */
.game-card {
  @apply transition-all duration-200 ease-in-out;
}

.game-card:hover {
  @apply transform scale-105 shadow-lg;
}

.game-card-red {
  @apply bg-game-red text-white;
}

.game-card-blue {
  @apply bg-game-blue text-white;
}

.game-card-neutral {
  @apply bg-game-neutral text-white;
}

.game-card-assassin {
  @apply bg-game-assassin text-white;
}
"""
    
    app_css = """.App {
  text-align: center;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.game-board {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 1rem;
  max-width: 600px;
  margin: 0 auto;
  padding: 1rem;
}

.game-card {
  aspect-ratio: 1.5;
  border: 2px solid #ccc;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  text-transform: uppercase;
  transition: all 0.2s ease;
}

.game-card:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}
"""
    
    with open("frontend/src/index.css", "w", encoding='utf-8') as f:
        f.write(index_css)
    print("✓ Created frontend/src/index.css")
    
    with open("frontend/src/App.css", "w", encoding='utf-8') as f:
        f.write(app_css)
    print("✓ Created frontend/src/App.css")

def update_changelog():
    """Update the changelog with setup information."""
    
    today = datetime.date.today().isoformat()
    
    changelog_entry = f"""
## [0.1.0] - {today}

### Added
- Complete project structure setup with frontend, backend, and shared directories
- Docker configuration for PostgreSQL and Redis development databases
- TypeScript configurations with strict settings for both frontend and backend
- Package.json files with all necessary dependencies for React and Node.js
- Prisma ORM setup with PostgreSQL schema for users, game rooms, and game state
- Vite configuration for React frontend with path aliases
- Tailwind CSS setup with custom game colors
- Basic Express server with Socket.io integration
- Environment configuration templates
- Git ignore files and Docker ignore configuration
- Basic React components structure and routing setup
- JWT authentication foundation
- Rate limiting and security middleware setup

### Changed
- N/A (Initial setup)

### Security
- Added Helmet middleware for security headers
- Implemented rate limiting for API endpoints
- Set up CORS configuration
- JWT token structure for authentication

---

## Python Scripts Run
- `python/setup_project.py` - Initial project structure and configuration setup ({today})

---
"""
    
    # Read existing changelog
    try:
        with open("CHANGELOG.md", "r", encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        content = ""
    
    # Find the unreleased section and replace it
    if "## [Unreleased]" in content:
        parts = content.split("## [Unreleased]")
        if len(parts) >= 2:
            # Keep everything before [Unreleased] and add our entry
            new_content = parts[0] + "## [Unreleased]\n\n### Added\n\n### Changed\n\n### Deprecated\n\n### Removed\n\n### Fixed\n\n### Security\n\n---\n" + changelog_entry + "\n".join(parts[1].split("---")[1:])
        else:
            new_content = content + changelog_entry
    else:
        new_content = content + changelog_entry
    
    with open("CHANGELOG.md", "w", encoding='utf-8') as f:
        f.write(new_content)
    print("✓ Updated CHANGELOG.md")

def create_placeholder_components():
    """Create placeholder component files to complete the structure."""
    
    # Create some basic placeholder files
    files_to_create = [
        ("frontend/src/components/UI/HomePage.tsx", """import React from 'react'

const HomePage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold text-center mb-8">Codenames</h1>
      <div className="text-center">
        <p className="mb-4">Welcome to Codenames!</p>
        <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
          Create Game
        </button>
      </div>
    </div>
  )
}

export default HomePage
"""),
        ("frontend/src/components/Game/GamePage.tsx", """import React from 'react'

const GamePage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-4">Game Room</h1>
      <div className="game-board">
        {/* Game board will go here */}
        <p>Game board placeholder</p>
      </div>
    </div>
  )
}

export default GamePage
"""),
        ("frontend/src/context/GameContext.tsx", """import React, { createContext, useContext, ReactNode } from 'react'

interface GameContextType {
  // Game state will go here
}

const GameContext = createContext<GameContextType | undefined>(undefined)

export const useGameContext = () => {
  const context = useContext(GameContext)
  if (context === undefined) {
    throw new Error('useGameContext must be used within a GameContextProvider')
  }
  return context
}

interface GameContextProviderProps {
  children: ReactNode
}

export const GameContextProvider: React.FC<GameContextProviderProps> = ({ children }) => {
  const value: GameContextType = {
    // Game state implementation will go here
  }

  return (
    <GameContext.Provider value={value}>
      {children}
    </GameContext.Provider>
  )
}
"""),
        ("shared/types/index.ts", """// Shared type definitions between frontend and backend

export interface User {
  id: string;
  username: string;
  avatarUrl?: string;
  createdAt: Date;
  gamesPlayed: number;
  gamesWon: number;
}

export interface GameRoom {
  id: string;
  name: string;
  hostId: string;
  players: Player[];
  gameState: GameState;
  settings: RoomSettings;
  createdAt: Date;
  isActive: boolean;
}

export interface RoomSettings {
  maxPlayers: number;
  turnTimeLimit?: number;
  customWordList?: string[];
  isPrivate: boolean;
}

export interface GameState {
  status: 'waiting' | 'active' | 'finished';
  currentTurn: 'red' | 'blue';
  board: Card[];
  redSpymaster: string;
  blueSpymaster: string;
  currentClue?: Clue;
  guessesRemaining: number;
  redAgentsLeft: number;
  blueAgentsLeft: number;
  winner?: 'red' | 'blue';
  turnHistory: TurnHistory[];
}

export interface Card {
  id: string;
  word: string;
  type: 'red' | 'blue' | 'neutral' | 'assassin';
  isRevealed: boolean;
  position: number;
}

export interface Clue {
  word: string;
  number: number;
  spymasterId: string;
  timestamp: Date;
}

export interface Player {
  id: string;
  userId: string;
  username: string;
  team: 'red' | 'blue' | 'spectator';
  role: 'spymaster' | 'operative';
  isConnected: boolean;
  joinedAt: Date;
}

export interface TurnHistory {
  clue: Clue;
  guesses: string[];
  team: 'red' | 'blue';
  timestamp: Date;
}
"""),
        ("frontend/postcss.config.js", """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
""")
    ]
    
    for file_path, content in files_to_create:
        with open(file_path, "w", encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Created {file_path}")

def main():
    """Main setup function."""
    print("Setting up Codenames Web App project structure...\n")
    
    try:
        create_directory_structure()
        print()
        
        create_package_json_files()
        print()
        
        create_docker_configuration()
        print()
        
        create_typescript_configs()
        print()
        
        create_environment_files()
        print()
        
        create_gitignore_files()
        print()
        
        create_basic_configurations()
        print()
        
        create_basic_files()
        print()
        
        create_css_files()
        print()
        
        create_placeholder_components()
        print()
        
        update_changelog()
        print()
        
        print("Project setup completed successfully!")
        print("\nNext steps:")
        print("1. Run 'docker-compose up -d' to start PostgreSQL and Redis")
        print("2. Copy .env.example files to .env in both frontend and backend directories")
        print("3. Install dependencies:")
        print("   - Frontend: cd frontend && npm install")
        print("   - Backend: cd backend && npm install")
        print("4. Generate Prisma client: cd backend && npm run db:generate")
        print("5. Run database migrations: cd backend && npm run db:migrate")
        print("6. Start development servers:")
        print("   - Backend: cd backend && npm run dev")
        print("   - Frontend: cd frontend && npm run dev")
        print("\nThis would be a good time to make your first commit!")
        
    except Exception as e:
        print(f"Error during setup: {e}")
        raise

if __name__ == "__main__":
    main()
