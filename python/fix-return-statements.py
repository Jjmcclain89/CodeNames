#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fix Return Statements
Fixes the "Not all code paths return a value" TypeScript error by adding explicit returns
"""

import os
from datetime import datetime

def update_file_content(file_path, new_content):
    """Update file with proper Windows encoding"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    print("🔧 Fixing Return Statements in Games Routes...")
    
    # Create games.ts with explicit return statements everywhere
    fixed_games_routes = '''import express, { Request, Response } from 'express';

const router = express.Router();

// Test endpoint to verify API is working
router.get('/test', (req: Request, res: Response): void => {
  console.log('🧪 API test endpoint hit!');
  res.json({ 
    success: true, 
    message: 'Games API is working!',
    timestamp: new Date().toISOString()
  });
});

// Create a new game - simplified for debugging
router.post('/create', (req: Request, res: Response): void => {
  try {
    console.log('🎮 POST /api/games/create - Creating new game...');
    console.log('📦 Request body:', req.body);
    
    // Generate simple 6-character game code
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let gameCode = '';
    for (let i = 0; i < 6; i++) {
      gameCode += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    
    console.log(`✅ Generated game code: ${gameCode}`);
    
    const response = { 
      success: true, 
      gameCode: gameCode,
      message: 'Game created successfully!',
      timestamp: new Date().toISOString()
    };
    
    console.log('📤 Sending response:', response);
    res.json(response);
    
  } catch (error) {
    console.error('❌ Error in /api/games/create:', error);
    res.status(500).json({ 
      success: false,
      error: 'Failed to create game',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Join an existing game - simplified for debugging
router.post('/join', (req: Request, res: Response): void => {
  try {
    const { gameCode } = req.body;
    console.log(`🚪 POST /api/games/join - Joining game: ${gameCode}`);
    
    if (!gameCode) {
      res.status(400).json({ 
        success: false,
        error: 'Game code is required' 
      });
      return;
    }
    
    // For debugging, accept any code
    const response = { 
      success: true, 
      gameCode: gameCode.toUpperCase(),
      message: 'Joined game successfully!',
      timestamp: new Date().toISOString()
    };
    
    console.log('📤 Sending response:', response);
    res.json(response);
    
  } catch (error) {
    console.error('❌ Error in /api/games/join:', error);
    res.status(500).json({ 
      success: false,
      error: 'Failed to join game',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

export default router;
'''

    # Update the games routes file
    games_route_path = 'backend/src/routes/games.ts'
    if update_file_content(games_route_path, fixed_games_routes):
        print("✅ Fixed return statements in backend/src/routes/games.ts")
    else:
        print("❌ Failed to fix games routes file")
        return
    
    # Update changelog
    try:
        changelog_path = 'CHANGELOG.md'
        with open(changelog_path, 'r', encoding='utf-8') as f:
            changelog = f.read()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        new_entry = f'- Return Statements Fix: Added explicit TypeScript return types and statements for games routes ({timestamp})'
        
        if '### Python Scripts Run' in changelog:
            updated_changelog = changelog.replace(
                '### Python Scripts Run',
                f'### Python Scripts Run\n{new_entry}'
            )
            
            with open(changelog_path, 'w', encoding='utf-8') as f:
                f.write(updated_changelog)
            print("✅ Updated CHANGELOG.md")
    except Exception as e:
        print(f"Note: Could not update changelog: {e}")
    
    print(f"\n🎉 Return Statements Fix Complete!")
    print("\n🔧 What was fixed:")
    print("• Added explicit TypeScript types: (req: Request, res: Response): void")
    print("• Added explicit return statement after error responses")
    print("• Made all code paths consistent with TypeScript strict mode")
    print("\n🎯 Next Steps:")
    print("1. Backend should now compile without TypeScript errors")
    print("2. Test: http://localhost:3001/api/games/test")
    print("3. Click 'Test API Connection' on homepage")
    print("4. Try 'Create Game' - should generate codes!")

if __name__ == "__main__":
    main()
