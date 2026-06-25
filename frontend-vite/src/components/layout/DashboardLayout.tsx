import { useEffect, useRef, useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'

export default function DashboardLayout() {
  const { pathname } = useLocation()
  const mainRef = useRef<HTMLElement>(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    if (mainRef.current) {
      mainRef.current.focus()
    }
    // Close sidebar on navigation on mobile
    if (window.innerWidth < 992) {
      setSidebarOpen(false)
    }
  }, [pathname])

  return (
    <div className="d-flex">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div 
          className="position-fixed top-0 start-0 w-100 h-100 bg-dark bg-opacity-50 d-lg-none" 
          style={{ zIndex: 998 }}
          onClick={() => setSidebarOpen(false)}
        />
      )}
      
      <Sidebar isOpen={sidebarOpen} />
      <div className="main-content">
        <Header onMenuClick={() => setSidebarOpen(true)} />
        <main
          ref={mainRef}
          tabIndex={-1}
          className="page-content"
          style={{ outline: 'none' }}
          aria-label="Main Content Area"
        >
          <Outlet />
        </main>
      </div>
    </div>
  )
}

