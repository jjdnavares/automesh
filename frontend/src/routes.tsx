import {
  createRoute,
  createRootRoute,
  createRootRouteWithContext,
  Outlet,
  Link,
} from '@tanstack/react-router'
import { QueryClient } from '@tanstack/react-query'
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools'

import App from './App'
import WorkflowListPage from './pages/workflow/WorkflowListPage'
import WorkflowPage from './pages/workflow/WorkflowPage'

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
      <div className="p-2 flex gap-2 bg-white border-b">
        <Link to="/" className="[&.active]:font-bold">
          Home
        </Link>
        <Link to="/workflow" className="[&.active]:font-bold">
          Workflows
        </Link>
        <Link to="/about" className="[&.active]:font-bold">
          About
        </Link>
      </div>
      <div className="p-4">
        <Outlet />
      </div>
      <TanStackRouterDevtools />
    </>
  ),
})

// Home route
export const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: function Index() {
    return <App />
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
    const { workflowId } = workflowDetailRoute.useParams()
    return <WorkflowPage />
  },
})

// Export the route tree
export const routeTree = rootRoute.addChildren([
  indexRoute,
  aboutRoute,
  workflowRoute.addChildren([
    workflowIndexRoute,
    workflowDetailRoute,
  ]),
])
