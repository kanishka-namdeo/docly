import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Chat from './pages/Chat'
import Documents from './pages/Documents'
import Settings from './pages/Settings'
import Sidebar from './components/Layout/Sidebar'

function App() {
  return (
    <BrowserRouter>
      <div style={{ display: 'flex', height: '100%' }}>
        <Sidebar />
        <div style={{ flex: 1, minWidth: 0, overflow: 'auto' }}>
          <Routes>
            <Route path="/" element={<Chat />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App
