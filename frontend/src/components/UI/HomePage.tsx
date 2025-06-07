import React from 'react'

const HomePage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold text-center mb-8">Codenames</h1>
      <div className="text-center">
        <p className="mb-4">Welcome to Codenames Online!</p>
        <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
          Create Game
        </button>
      </div>
    </div>
  )
}

export default HomePage
