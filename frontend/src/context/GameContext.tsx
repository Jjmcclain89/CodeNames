import React, { createContext, useContext, ReactNode } from 'react'

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
