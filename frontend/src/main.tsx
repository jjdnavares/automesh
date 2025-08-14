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
  createRootRouteWithContext,
} from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools'

import {
  useQuery,
  useMutation,
  useQueryClient,
  QueryClient,
  QueryClientProvider,
} from '@tanstack/react-query'

import {
  Avatar,
  AvatarFallback,
  AvatarImage,
} from "@/components/ui/avatar"
import { Button } from './components/ui/button'


// Create a client
const queryClient = new QueryClient()

function sessionUser() {
  const cookies = new URLSearchParams(document.cookie.split("; ").join("&"))
  let _sessionUser = cookies.get("user_id")
  if (_sessionUser === "Guest") {
    _sessionUser = null
  }
  return _sessionUser
}

const rootRoute = createRootRouteWithContext<{ queryClient: QueryClient }>()({
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

async function getUserInfo() {
  const response = await fetch('/api/method/automesh.api.get_current_user_info')
  if (!response.ok) {
    throw new Error("Error occured while fetching user info")
  }

  const data = await response.json()

  if (data.message) {
    return data.message
  }

  return data
}

const aboutRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/about',
  component: function About() {
    // Access the client
    const queryClient = useQueryClient()

    // Queries
    const { data, isLoading, isError } = useQuery({ 
      queryKey: ['current_user'], 
      queryFn: getUserInfo,
    })

    async function logout() {
        const response = await fetch('/api/method/logout')
        if (!response.ok) {
          throw new Error("Error occured while logging out")
        }

        window.location.href = '/login'
    }

    if (isLoading) {
      return <div className="p-2">Loading...</div>
    }

    if (isError) {
      return <div className="p-2">Error fetching user info</div>
    }

    return (
      <div className="p-2" >
        <Avatar className="h-24 w-24">
          <AvatarImage src={data.user_image} alt={data.full_name} />
          <AvatarFallback>CN</AvatarFallback>
        </Avatar>
        <h1>{data.full_name}</h1>

        <Button onClick={logout}>Logout</Button>
      </div>
    )
  },
})

const routeTree = rootRoute.addChildren([indexRoute, aboutRoute])

const router = createRouter({
  routeTree, 
  defaultPreloadStaleTime: 0,
  context: {
    queryClient,
  },
})

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
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>
    </StrictMode>,
  )
}