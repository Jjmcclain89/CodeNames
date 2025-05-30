#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Debug Page Styling
Fixes white text on white background issue in DebugPage
"""

from pathlib import Path
from datetime import datetime

def add_changelog_entry():
    """Add entry to CHANGELOG.md"""
    try:
        changelog_path = Path("CHANGELOG.md")
        if not changelog_path.exists():
            print("Warning: CHANGELOG.md not found")
            return
            
        # Read current changelog
        with open(changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the Python Scripts section
        if "### Python Scripts Run" not in content:
            # Add the section if it doesn't exist
            unreleased_section = content.find("## [Unreleased]")
            if unreleased_section != -1:
                insert_point = content.find("### Added", unreleased_section)
                if insert_point != -1:
                    new_section = "\n### Python Scripts Run\n- Debug page styling fix: Fixed white text on white background visibility issues\n"
                    content = content[:insert_point] + new_section + content[insert_point:]
                else:
                    # Add after [Unreleased] header
                    insert_point = content.find("\n", unreleased_section) + 1
                    new_section = "\n### Python Scripts Run\n- Debug page styling fix: Fixed white text on white background visibility issues\n"
                    content = content[:insert_point] + new_section + content[insert_point:]
        else:
            # Add to existing section
            section_start = content.find("### Python Scripts Run")
            section_end = content.find("\n###", section_start + 1)
            if section_end == -1:
                section_end = content.find("\n## ", section_start + 1)
            
            entry = f"- Debug page styling fix: Fixed text visibility issues ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n"
            
            if section_end != -1:
                insert_point = section_end
                content = content[:insert_point] + entry + content[insert_point:]
            else:
                content += entry
        
        # Write back to changelog
        with open(changelog_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Updated CHANGELOG.md")
        
    except Exception as e:
        print(f"⚠️ Could not update CHANGELOG.md: {e}")

def fix_debug_page_styling():
    """Fix the DebugPage styling to make text visible"""
    print("🎨 Fixing debug page styling...")
    
    debug_page_path = Path("frontend/src/pages/DebugPage.tsx")
    
    # Fixed debug page with proper text colors and contrast
    fixed_debug_page = '''import React, { useState, useEffect } from 'react';
import authService from '../services/authService';
import socketService from '../services/socketService';

const DebugPage: React.FC = () => {
  const [apiStatus, setApiStatus] = useState<string>('Not tested');
  const [socketStatus, setSocketStatus] = useState<string>('Not connected');
  const [testResults, setTestResults] = useState<string[]>([]);

  const addResult = (message: string) => {
    setTestResults(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
  };

  const testAPI = async () => {
    addResult('🔑 Testing API connection...');
    setApiStatus('Testing...');
    
    try {
      const result = await authService.login('test-user');
      if (result.success) {
        setApiStatus('✅ Connected');
        addResult('🔑 API test successful');
      } else {
        setApiStatus('❌ Failed');
        addResult(`🔑 API test failed: ${result.error}`);
      }
    } catch (error) {
      setApiStatus('❌ Error');
      addResult(`🔑 API test error: ${error}`);
    }
  };

  const testSocket = () => {
    addResult('📡 Testing socket connection...');
    setSocketStatus('Connecting...');
    
    const socket = socketService.connect();
    
    socket.on('connect', () => {
      setSocketStatus('✅ Connected');
      addResult('📡 Socket connected successfully');
    });
    
    socket.on('connect_error', (error) => {
      setSocketStatus('❌ Failed');
      addResult(`📡 Socket connection failed: ${error}`);
    });
  };

  const clearResults = () => {
    setTestResults([]);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold mb-6 text-gray-900">Phase 1 Debug Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <h2 className="text-xl font-semibold mb-4 text-gray-900">API Connection Test</h2>
          <p className="mb-4 text-gray-700">
            Status: <span className="font-mono bg-gray-100 px-2 py-1 rounded text-gray-900">{apiStatus}</span>
          </p>
          <button 
            onClick={testAPI}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition-colors"
          >
            Test API Connection
          </button>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <h2 className="text-xl font-semibold mb-4 text-gray-900">Socket Connection Test</h2>
          <p className="mb-4 text-gray-700">
            Status: <span className="font-mono bg-gray-100 px-2 py-1 rounded text-gray-900">{socketStatus}</span>
          </p>
          <button 
            onClick={testSocket}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded transition-colors"
          >
            Test Socket Connection
          </button>
        </div>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Test Results</h2>
          <button 
            onClick={clearResults}
            className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-sm transition-colors"
          >
            Clear
          </button>
        </div>
        <div className="bg-gray-900 text-green-400 p-4 rounded h-64 overflow-y-auto font-mono text-sm">
          {testResults.length === 0 ? (
            <p className="text-gray-500">No test results yet...</p>
          ) : (
            <div className="space-y-1">
              {testResults.map((result, index) => (
                <div key={index} className="text-green-400">{result}</div>
              ))}
            </div>
          )}
        </div>
      </div>
      
      <div className="mt-6 bg-blue-50 border border-blue-200 p-4 rounded-lg">
        <p className="font-semibold text-blue-900 mb-2">Expected behavior:</p>
        <ul className="list-disc pl-5 mt-2 text-blue-800 space-y-1">
          <li>API test should return a token and user object</li>
          <li>Socket test should establish WebSocket connection</li>
          <li>Check browser console (F12) for detailed logs</li>
          <li>Both tests need backend server running on localhost:3001</li>
        </ul>
      </div>
      
      <div className="mt-4 bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
        <p className="font-semibold text-yellow-900 mb-2">🔧 Debugging Tips:</p>
        <ul className="list-disc pl-5 text-yellow-800 space-y-1">
          <li>If API fails: Check if backend server is running (npm run dev in backend folder)</li>
          <li>If Socket fails: Check CORS settings and port configurations</li>
          <li>Press F12 to open browser console for detailed error messages</li>
          <li>Try the regular login at <a href="/login" className="text-blue-600 underline hover:text-blue-800">/login</a> after tests pass</li>
        </ul>
      </div>
    </div>
  );
};

export default DebugPage;
'''
    
    with open(debug_page_path, 'w', encoding='utf-8') as f:
        f.write(fixed_debug_page)
    
    print("✅ Fixed debug page styling with proper text colors and contrast")

def main():
    """Main execution function"""
    print("🎨 Fixing Debug Page Styling Issues")
    print("=" * 40)
    
    try:
        # Fix the debug page styling
        fix_debug_page_styling()
        
        # Update changelog
        add_changelog_entry()
        
        print("\n🎉 Debug Page Styling Fixed!")
        print("=" * 40)
        
        print("\n📋 Changes made:")
        print("✅ Added proper text colors (text-gray-900, text-gray-700, etc.)")
        print("✅ Added background colors for better contrast")
        print("✅ Made status displays more readable with background highlights")
        print("✅ Added terminal-style output (dark background, green text)")
        print("✅ Added colored info boxes for better organization")
        print("✅ Added helpful debugging tips section")
        
        print("\n🔧 Next steps:")
        print("1. Refresh your browser page (F5 or Ctrl+R)")
        print("2. The debug page should now be fully readable")
        print("3. Try both test buttons to verify connections")
        print("4. Check browser console (F12) for detailed logs")
        
        return 0
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
