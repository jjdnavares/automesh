import { StrictMode } from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import {
  Outlet,
  RouterProvider,
  Link,
  createRouter,
  createRoute,
  createRootRoute,
} from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools'

function sessionUser() {
  const cookies = new URLSearchParams(document.cookie.split("; ").join("&"))
  let _sessionUser = cookies.get("user_id")
  if (_sessionUser === "Guest") {
    _sessionUser = null
  }
  return _sessionUser
}

const rootRoute = createRootRoute({
  beforeLoad: async ({ location }) => {
    if (!sessionUser()) {
      window.location.href = "/login?reditect-to=" + location.pathname
    }
  },
  component: () => (
    <>
      <div className="p-2 flex gap-2">
        <Link to="/" className="[&.active]:font-bold">
          Home
        </Link>{' '}
        <Link to="/about" className="[&.active]:font-bold">
          About
        </Link>
      </div>
      <hr />
      <Outlet />
      <TanStackRouterDevtools />
    </>
  ),
})

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: function Index() {
    return (
      <div className="p-2">
        <App />
      </div>
    )
  },
})

const aboutRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/about',
  component: function About() {
    return sessionUser() ?
      <div className="p-2">Hello to you, {sessionUser()}</div> :
      <div className="p-2">You are not logged in!</div>
  },
})

const routeTree = rootRoute.addChildren([indexRoute, aboutRoute])

const router = createRouter({ routeTree })

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}

const rootElement = document.getElementById('root')!
if (!rootElement.innerHTML) {
  const root = ReactDOM.createRoot(rootElement)
  root.render(
    <StrictMode>
      <RouterProvider router={router} />
    </StrictMode>,
  )
}