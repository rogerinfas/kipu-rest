import { Outlet, createRootRoute } from '@tanstack/react-router'
import { Sidebar } from '../components/Sidebar'

export const Route = createRootRoute({
  component: () => (
    <div className="flex h-screen w-screen overflow-hidden bg-[#2B1D16] text-[#F5EBDD]">
      <Sidebar />
      <div className="min-w-0 flex-1">
        <Outlet />
      </div>
    </div>
  ),
})
