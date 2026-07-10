import { Link, useLocation } from 'react-router-dom'

export default function Sidebar() {
  const location = useLocation()
  const isActive = (path: string) => location.pathname === path

  return (
    <div style={{ width: '200px', flexShrink: 0, backgroundColor: '#f5f5f5', padding: '20px', borderRight: '1px solid #ddd', display: 'flex', flexDirection: 'column' }}>
      <h2 style={{ marginBottom: '20px' }}>Doc Assistant</h2>
      <nav>
        <ul style={{ listStyle: 'none', padding: 0 }}>
          <li style={{ marginBottom: '10px' }}>
            <Link to="/" style={{ textDecoration: 'none', color: isActive('/') ? '#0066cc' : '#333', fontWeight: isActive('/') ? 'bold' : 'normal' }}>💬 Chat</Link>
          </li>
          <li style={{ marginBottom: '10px' }}>
            <Link to="/documents" style={{ textDecoration: 'none', color: isActive('/documents') ? '#0066cc' : '#333', fontWeight: isActive('/documents') ? 'bold' : 'normal' }}>📄 Documents</Link>
          </li>
          <li style={{ marginBottom: '10px' }}>
            <Link to="/settings" style={{ textDecoration: 'none', color: isActive('/settings') ? '#0066cc' : '#333', fontWeight: isActive('/settings') ? 'bold' : 'normal' }}>⚙️ Settings</Link>
          </li>
        </ul>
      </nav>
    </div>
  )
}
