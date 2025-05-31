import React from 'react';

const GamePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full text-center">
        <h1 className="text-3xl font-bold mb-4 text-gray-800">🎮 Game Page Test</h1>
        <p className="text-gray-600 mb-4">
          If you can see this, the GamePage route is working!
        </p>
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
          ✅ Route Setup Successful
        </div>
        <p className="text-sm text-gray-500 mt-4">
          This is a simplified GamePage for testing.
          The full game will load once authentication is working.
        </p>
      </div>
    </div>
  );
};

export default GamePage;
