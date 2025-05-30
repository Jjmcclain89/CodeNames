import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
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
