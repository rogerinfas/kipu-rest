import { Outlet, createRootRoute } from '@tanstack/react-router'

export const Route = createRootRoute({
  component: () => (
    <div className="h-screen w-screen overflow-hidden bg-[#2B1D16] text-[#F5EBDD]">
      <Outlet />
    </div>
  ),
})
