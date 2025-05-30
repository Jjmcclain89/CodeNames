#!/usr/bin/env python3
"""
Fix login input issues - disable autocomplete and improve input handling
"""

import os

def fix_login_page():
    """Fix the LoginPage component to prevent autocomplete issues"""
    frontend_src = "../frontend/src"
    
    # Updated LoginPage with better input handling
    login_page_fixed = '''import React, { useState } from 'react';
import authService from '../services/authService';

interface LoginPageProps {
  onLogin: (user: any, token: string) => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!username.trim()) {
      setError('Username is required');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      console.log('Attempting login with username:', username.trim());
      const result = await authService.login(username.trim());
      console.log('Login result:', result);
      
      if (result.success && result.token && result.user) {
        console.log('Login successful');
        onLogin(result.user, result.token);
      } else {
        console.log('Login failed:', result.error);
        setError(result.error || 'Login failed');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError('Failed to connect to server');
    }

    setIsLoading(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUsername(e.target.value);
    if (error) setError(''); // Clear error when user starts typing
  };

  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h2 className="text-2xl font-bold text-center mb-6">Join Codenames</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4" autoComplete="off">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
              Choose a Username
            </label>
            <input
              type="text"
              id="username"
              name="username"
              value={username}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your username"
              disabled={isLoading}
              autoComplete="off"
              autoCorrect="off"
              autoCapitalize="off"
              spellCheck="false"
              data-lpignore="true"
            />
          </div>
          
          {error && (
            <div className="text-red-600 text-sm bg-red-50 p-2 rounded">{error}</div>
          )}
          
          <button
            type="submit"
            disabled={isLoading || !username.trim()}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white py-2 px-4 rounded-md font-medium transition-colors"
          >
            {isLoading ? 'Connecting...' : 'Join Game'}
          </button>
        </form>
        
        <div className="mt-6 text-center text-sm text-gray-600">
          <p>Enter any username to join or create an account</p>
          <p className="mt-2 text-xs">Debug: Check browser console for error details</p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
'''
    
    login_path = os.path.join(frontend_src, "pages", "LoginPage.tsx")
    with open(login_path, 'w', encoding='utf-8') as f:
        f.write(login_page_fixed)
    
    print("SUCCESS: Fixed LoginPage with better input handling")

def main():
    """Main execution function"""
    print("Fixing login input issues...")
    
    try:
        fix_login_page()
        print("\nSUCCESS: Fixed login input problems!")
        print("\nChanges made:")
        print("- Disabled browser autocomplete")
        print("- Added better input change handling")
        print("- Added console logging for debugging")
        print("- Improved error display")
        print("- Added visual feedback")
        
        print("\nNext steps:")
        print("1. Refresh your browser page")
        print("2. Try typing in the username field")
        print("3. Open browser console (F12) to see debug logs")
        
    except Exception as e:
        print(f"ERROR: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
