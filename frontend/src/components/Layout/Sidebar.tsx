import { Link, useLocation } from 'react-router-dom'

export default function Sidebar() {
  const location = useLocation()
  const isActive = (path: string) => location.pathname === path

  const navLinkClass = (path: string) =>
    `block w-full text-left px-2.5 py-1.5 rounded-md text-sm font-medium transition-colors ${
      isActive(path)
        ? 'bg-secondary text-secondary-foreground'
        : 'text-foreground hover:bg-muted hover:text-foreground'
    }`

  return (
    <div className="w-[200px] flex-shrink-0 bg-secondary p-6 border-r border-border flex flex-col">
      <h2 className="mb-6">Doc Assistant</h2>
      <nav>
        <ul className="list-none p-0">
          <li className="mb-2">
            <Link to="/" className={navLinkClass('/')}>
              💬 Chat
            </Link>
          </li>
          <li className="mb-2">
            <Link to="/documents" className={navLinkClass('/documents')}>
              📄 Documents
            </Link>
          </li>
          <li className="mb-2">
            <Link to="/settings" className={navLinkClass('/settings')}>
              ⚙️ Settings
            </Link>
          </li>
        </ul>
      </nav>
    </div>
  )
}