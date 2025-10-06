import {
  createRoute,
  createRootRouteWithContext,
  Outlet,
} from '@tanstack/react-router'
import { QueryClient } from '@tanstack/react-query'
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools'

import WorkflowListPage from './pages/workflow/WorkflowListPage'
import WorkflowPage from './pages/workflow/WorkflowPage'
import { Navbar } from './components/layout/Navbar'

// Root route with authentication check
export const rootRoute = createRootRouteWithContext<{ queryClient: QueryClient }>()({
  beforeLoad: async ({ location }) => {
    const cookies = new URLSearchParams(document.cookie.split("; ").join("&"))
    let _sessionUser = cookies.get("user_id")
    if (_sessionUser === "Guest" || !_sessionUser) {
      window.location.href = "/login?redirect-to=" + location.pathname
    }
  },
  component: () => (
    <>
      <Navbar />
      <main>
        <Outlet />
      </main>
      <TanStackRouterDevtools />
    </>
  ),
})

// Import the Index component directly instead of using the Route export
import { Index as HomePage } from './routes/index'
import { Navigate } from '@tanstack/react-router'

// Home route - redirects to /workflow
export const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: () => <Navigate to="/workflow" />,
})

// Original home page (kept for reference)
export const homeRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/home',
  component: HomePage,
})

// App/Desk route - redirects to Frappe desk
export const appRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/app',
  component: () => {
    // Redirect to Frappe desk
    window.location.href = '/app'
    return null
  },
})

// About route (existing)
export const aboutRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/about',
  component: function About() {
    // Existing about component implementation
    return (
      <div className="p-2">
        <h1 className="text-2xl font-bold">About</h1>
        <p>This is the about page</p>
      </div>
    )
  },
})

// Workflow routes
// Parent layout route for workflows
export const workflowRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: 'workflow',
  component: () => <Outlet />,
})

// Workflow list route
export const workflowIndexRoute = createRoute({
  getParentRoute: () => workflowRoute,
  path: '/',
  component: WorkflowListPage,
})

// Workflow detail/editor route
export const workflowDetailRoute = createRoute({
  getParentRoute: () => workflowRoute,
  path: '$workflowId',
  component: function WorkflowDetail() {
    // We can use workflowId later when implementing the workflow page properly
    // const { workflowId } = workflowDetailRoute.useParams()
    return <WorkflowPage />
  },
})

// Export the route tree
export const routeTree = rootRoute.addChildren([
  indexRoute,
  homeRoute,
  appRoute,
  aboutRoute,
  workflowRoute.addChildren([
    workflowIndexRoute,
    workflowDetailRoute,
  ]),
])
