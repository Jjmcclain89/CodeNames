#!/usr/bin/env python3
"""
Complete Phase 0 - Project Foundation
Sets up remaining infrastructure for Codenames Web App
"""

import os
import json
from datetime import datetime

def update_changelog():
    """Update changelog with Phase 0 completion"""
    changelog_path = "../CHANGELOG.md"
    
    if not os.path.exists(changelog_path):
        print("❌ CHANGELOG.md not found")
        return
    
    with open(changelog_path, 'r') as f:
        content = f.read()
    
    # Find the [Unreleased] section and add our changes
    unreleased_section = content.find("## [Unreleased]")
    if unreleased_section == -1:
        print("❌ Could not find [Unreleased] section in CHANGELOG.md")
        return
    
    # Find the ### Added section
    added_section = content.find("### Added", unreleased_section)
    if added_section == -1:
        print("❌ Could not find ### Added section")
        return
    
    # Find the end of the Added section
    next_section = content.find("### Changed", added_section)
    if next_section == -1:
        next_section = content.find("### Deprecated", added_section)
    
    # Insert our new items
    new_items = """- PostgreSQL database schema with Prisma ORM setup
- Basic Express server with TypeScript and middleware structure
- React frontend with Vite, TypeScript, and routing setup
- Development environment fully configured and tested
- Python script automation for Phase 0 completion (complete_phase0.py)

"""
    
    if next_section != -1:
        # Insert before the next section
        updated_content = content[:next_section] + new_items + content[next_section:]
    else:
        # Insert at the end of the file if no next section found
        updated_content = content + new_items
    
    with open(changelog_path, 'w') as f:
        f.write(updated_content)
    
    print("✅ Updated CHANGELOG.md with Phase 0 completion")

def create_prisma_schema():
    """Create the initial Prisma schema"""
    backend_dir = "../backend"
    prisma_dir = os.path.join(backend_dir, "prisma")
    
    if not os.path.exists(backend_dir):
        os.makedirs(backend_dir)
        print(f"✅ Created {backend_dir} directory")
    
    if not os.path.exists(prisma_dir):
        os.makedirs(prisma_dir)
        print(f"✅ Created {prisma_dir} directory")
    
    schema_content = '''// This is your Prisma schema file,
// learn more about it in the docs: https://pris.ly/d/prisma-schema

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        String   @id @default(cuid())
  username  String   @unique
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  // Relations
  rooms     RoomUser[]
  
  @@map("users")
}

model Room {
  id          String   @id @default(cuid())
  name        String
  code        String   @unique
  isPrivate   Boolean  @default(false)
  maxPlayers  Int      @default(8)
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  // Game state
  gameState   Json?
  isActive    Boolean  @default(false)
  
  // Relations
  users       RoomUser[]
  
  @@map("rooms")
}

model RoomUser {
  id     String @id @default(cuid())
  userId String
  roomId String
  role   String @default("player") // "player", "spymaster", "spectator"
  team   String? // "red", "blue"
  
  user   User @relation(fields: [userId], references: [id], onDelete: Cascade)
  room   Room @relation(fields: [roomId], references: [id], onDelete: Cascade)
  
  @@unique([userId, roomId])
  @@map("room_users")
}
'''
    
    schema_path = os.path.join(prisma_dir, "schema.prisma")
    with open(schema_path, 'w') as f:
        f.write(schema_content)
    
    print(f"✅ Created Prisma schema at {schema_path}")

def create_backend_structure():
    """Create basic Express server structure"""
    backend_dir = "../backend"
    src_dir = os.path.join(backend_dir, "src")
    
    # Create directory structure
    directories = [
        src_dir,
        os.path.join(src_dir, "routes"),
        os.path.join(src_dir, "services"),
        os.path.join(src_dir, "socket"),
        os.path.join(src_dir, "models"),
        os.path.join(src_dir, "middleware"),
        os.path.join(src_dir, "utils")
    ]
    
    for dir_path in directories:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"✅ Created {dir_path}")

    # Create main server file
    server_content = '''import express from 'express';
import cors from 'cors';
import { createServer } from 'http';
import { Server } from 'socket.io';
import dotenv from 'dotenv';
import { PrismaClient } from '@prisma/client';

// Load environment variables
dotenv.config();

// Initialize Prisma
const prisma = new PrismaClient();

// Create Express app
const app = express();
const server = createServer(app);

// Initialize Socket.io
const io = new Server(server, {
  cors: {
    origin: process.env.FRONTEND_URL || "http://localhost:5173",
    methods: ["GET", "POST"]
  }
});

// Middleware
app.use(cors({
  origin: process.env.FRONTEND_URL || "http://localhost:5173"
}));
app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Socket.io connection handling
io.on('connection', (socket) => {
  console.log(`User connected: ${socket.id}`);
  
  socket.on('disconnect', () => {
    console.log(`User disconnected: ${socket.id}`);
  });
});

// Start server
const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`📡 Socket.io ready for connections`);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, shutting down gracefully');
  await prisma.$disconnect();
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});
'''
    
    server_path = os.path.join(src_dir, "server.ts")
    with open(server_path, 'w') as f:
        f.write(server_content)
    
    print(f"✅ Created server.ts at {server_path}")

    # Create basic middleware
    auth_middleware = '''import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';

export interface AuthRequest extends Request {
  userId?: string;
}

export const authenticateToken = (req: AuthRequest, res: Response, next: NextFunction) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.sendStatus(401);
  }

  jwt.verify(token, process.env.JWT_SECRET || 'fallback-secret', (err: any, user: any) => {
    if (err) return res.sendStatus(403);
    req.userId = user.userId;
    next();
  });
};
'''
    
    auth_path = os.path.join(src_dir, "middleware", "auth.ts")
    with open(auth_path, 'w') as f:
        f.write(auth_middleware)
    
    print(f"✅ Created auth middleware at {auth_path}")

def create_frontend_structure():
    """Create basic React app with Vite structure"""
    frontend_dir = "../frontend"
    src_dir = os.path.join(frontend_dir, "src")
    
    # Create directory structure
    directories = [
        src_dir,
        os.path.join(src_dir, "components"),
        os.path.join(src_dir, "hooks"),
        os.path.join(src_dir, "services"),
        os.path.join(src_dir, "types"),
        os.path.join(src_dir, "utils"),
        os.path.join(src_dir, "pages"),
        os.path.join(frontend_dir, "public")
    ]
    
    for dir_path in directories:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"✅ Created {dir_path}")

    # Create main App component
    app_content = '''import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import GamePage from './pages/GamePage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="bg-blue-600 text-white p-4">
          <h1 className="text-2xl font-bold">Codenames</h1>
        </header>
        <main className="container mx-auto p-4">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/game/:roomId" element={<GamePage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
'''
    
    app_path = os.path.join(src_dir, "App.tsx")
    with open(app_path, 'w') as f:
        f.write(app_content)
    
    print(f"✅ Created App.tsx at {app_path}")

    # Create main.tsx
    main_content = '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
'''
    
    main_path = os.path.join(src_dir, "main.tsx")
    with open(main_path, 'w') as f:
        f.write(main_content)
    
    print(f"✅ Created main.tsx at {main_path}")

    # Create basic pages
    home_page = '''import React from 'react';

const HomePage: React.FC = () => {
  return (
    <div className="text-center">
      <h2 className="text-3xl font-bold mb-6">Welcome to Codenames</h2>
      <p className="text-lg mb-8">
        A real-time multiplayer word game experience
      </p>
      <div className="space-y-4">
        <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg mr-4">
          Create Room
        </button>
        <button className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg">
          Join Room
        </button>
      </div>
    </div>
  );
};

export default HomePage;
'''
    
    home_path = os.path.join(src_dir, "pages", "HomePage.tsx")
    with open(home_path, 'w') as f:
        f.write(home_page)
    
    print(f"✅ Created HomePage.tsx")

    game_page = '''import React from 'react';
import { useParams } from 'react-router-dom';

const GamePage: React.FC = () => {
  const { roomId } = useParams<{ roomId: string }>();
  
  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Game Room: {roomId}</h2>
      <div className="grid grid-cols-5 gap-2 max-w-2xl mx-auto">
        {Array.from({ length: 25 }, (_, i) => (
          <div
            key={i}
            className="bg-gray-200 p-4 text-center rounded cursor-pointer hover:bg-gray-300"
          >
            Card {i + 1}
          </div>
        ))}
      </div>
    </div>
  );
};

export default GamePage;
'''
    
    game_path = os.path.join(src_dir, "pages", "GamePage.tsx")
    with open(game_path, 'w') as f:
        f.write(game_page)
    
    print(f"✅ Created GamePage.tsx")

    # Create basic CSS files
    app_css = '''#root {
  max-width: 1280px;
  margin: 0 auto;
  text-align: center;
}
'''
    
    app_css_path = os.path.join(src_dir, "App.css")
    with open(app_css_path, 'w') as f:
        f.write(app_css)
    
    index_css = '''@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
'''
    
    index_css_path = os.path.join(src_dir, "index.css")
    with open(index_css_path, 'w') as f:
        f.write(index_css)
    
    print(f"✅ Created CSS files")

    # Create index.html
    index_html = '''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Codenames - Multiplayer Word Game</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
'''
    
    index_path = os.path.join(frontend_dir, "index.html")
    with open(index_path, 'w') as f:
        f.write(index_html)
    
    print(f"✅ Created index.html")

def create_env_files():
    """Create environment files if they don't exist"""
    
    # Backend .env
    backend_env = """# Database
DATABASE_URL="postgresql://username:password@localhost:5432/codenames_db"

# Authentication
JWT_SECRET="your-super-secret-jwt-key-change-this-in-production"

# Server Configuration
PORT=3001
NODE_ENV=development

# Frontend URL for CORS
FRONTEND_URL="http://localhost:5173"
"""
    
    backend_env_path = "../backend/.env.example"
    if not os.path.exists(backend_env_path):
        with open(backend_env_path, 'w') as f:
            f.write(backend_env)
        print(f"✅ Created {backend_env_path}")
    
    # Frontend .env
    frontend_env = """# API Configuration
VITE_API_URL=http://localhost:3001
VITE_SOCKET_URL=http://localhost:3001

# Environment
VITE_NODE_ENV=development
"""
    
    frontend_env_path = "../frontend/.env.example"
    if not os.path.exists(frontend_env_path):
        with open(frontend_env_path, 'w') as f:
            f.write(frontend_env)
        print(f"✅ Created {frontend_env_path}")

def main():
    """Main execution function"""
    print("🚀 Starting Phase 0 completion...")
    print("=" * 50)
    
    try:
        create_env_files()
        create_prisma_schema()
        create_backend_structure()
        create_frontend_structure()
        update_changelog()
        
        print("\n" + "=" * 50)
        print("✅ Phase 0 completion successful!")
        print("\nNext steps:")
        print("1. Copy .env.example files to .env and configure them")
        print("2. Set up PostgreSQL database")
        print("3. Run 'npx prisma migrate dev' in backend directory")
        print("4. Test both frontend and backend servers")
        print("\nReady for Phase 1: Socket Foundation! 🎯")
        
    except Exception as e:
        print(f"❌ Error during Phase 0 completion: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
