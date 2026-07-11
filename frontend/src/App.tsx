import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Chat from './pages/Chat'
import Documents from './pages/Documents'
import Settings from './pages/Settings'
import Sidebar from './components/Layout/Sidebar'
import ErrorBoundary from './components/common/ErrorBoundary'
import { ToastProvider } from './components/common/ToastContext'

function App() {
  return (
    <BrowserRouter>
      <ErrorBoundary>
        <ToastProvider>
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
        </ToastProvider>
      </ErrorBoundary>
    </BrowserRouter>
  )
}

export default App
