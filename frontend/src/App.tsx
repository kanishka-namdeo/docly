import { useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { invoke } from '@tauri-apps/api/core'
import Chat from './pages/Chat'
import Documents from './pages/Documents'
import Settings from './pages/Settings'
import Sidebar from './components/Layout/Sidebar'
import ErrorBoundary from './components/common/ErrorBoundary'
import { Toaster } from '@/components/ui/sonner'
function App() {
  useEffect(() => {
    // Auto-start backend on app launch
    invoke('start_backend').catch((err) => {
      console.error('Failed to start backend:', err)
    })
    
    // Stop backend on app close
    return () => {
      invoke('stop_backend').catch(console.error)
    }
  }, [])
  
  return (
    <BrowserRouter>
      <ErrorBoundary>
        <div className="flex h-full">
          <Sidebar />
          <div className="flex-1 min-w-0 overflow-auto">
            <Routes>
              <Route path="/" element={<Chat />} />
              <Route path="/documents" element={<Documents />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </div>
        </div>
        <Toaster />
      </ErrorBoundary>
    </BrowserRouter>
  )
}

export default App
