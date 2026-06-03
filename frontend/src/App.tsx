import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@store/auth'

// Layouts
import DashboardLayout from '@components/layout/DashboardLayout'

// Pages
import Dashboard        from '@pages/Dashboard'
import Conversations    from '@pages/Conversations'
import Messages         from '@pages/Messages'
import Agents           from '@pages/Agents'
import Workflows        from '@pages/Workflows'
import Tickets          from '@pages/Tickets'
import Clients          from '@pages/Clients'
import Employees        from '@pages/Employees'
import Analytics        from '@pages/Analytics'
import Settings         from '@pages/Settings'
import WhatsApp         from '@pages/WhatsApp'
import Prompts          from '@pages/Prompts'
import Endpoints        from '@pages/Endpoints'
import Audit            from '@pages/Audit'
import Security         from '@pages/Security'
import Users            from '@pages/Users'
import Login            from '@pages/Login'

function RequireAuth({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore(s => s.isAuthenticated)
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/login" element={<Login />} />

      {/* Protected */}
      <Route
        path="/"
        element={
          <RequireAuth>
            <DashboardLayout />
          </RequireAuth>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard"     element={<Dashboard />} />
        <Route path="conversations" element={<Conversations />} />
        <Route path="conversations/:id/messages" element={<Messages />} />
        <Route path="agents"        element={<Agents />} />
        <Route path="workflows"     element={<Workflows />} />
        <Route path="tickets"       element={<Tickets />} />
        <Route path="clients"       element={<Clients />} />
        <Route path="employees"     element={<Employees />} />
        <Route path="analytics"     element={<Analytics />} />
        <Route path="settings"      element={<Settings />} />
        <Route path="whatsapp"      element={<WhatsApp />} />
        <Route path="prompts"       element={<Prompts />} />
        <Route path="endpoints"     element={<Endpoints />} />
        <Route path="audit"         element={<Audit />} />
        <Route path="security"      element={<Security />} />
        <Route path="users"         element={<Users />} />
      </Route>

      {/* 404 */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}
