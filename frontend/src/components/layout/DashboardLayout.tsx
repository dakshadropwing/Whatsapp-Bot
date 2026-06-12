import { useEffect, useRef } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'

export default function DashboardLayout() {
  const { pathname } = useLocation()
  const mainRef = useRef<HTMLElement>(null)

  useEffect(() => {
    if (mainRef.current) {
      mainRef.current.focus()
    }
  }, [pathname])

  return (
    <div className="d-flex">
      <Sidebar />
      <div className="main-content">
        <Header />
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

