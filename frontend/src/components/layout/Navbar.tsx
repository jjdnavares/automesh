import { Link } from '@tanstack/react-router'
import { LogOut, Menu, X, Activity, LayoutGrid, Info } from 'lucide-react'
import { useState } from 'react'

export function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  
  const toggleMobileMenu = () => setMobileMenuOpen(!mobileMenuOpen)
  
  return (
    <header className="bg-white shadow-md sticky top-0 z-50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 justify-between items-center">
          {/* Logo & Brand */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center">
              <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center mr-2">
                <Activity className="h-6 w-6 text-white" />
              </div>
              <span className="text-xl font-bold text-indigo-600">AutoMesh</span>
            </Link>
          </div>
          
          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            <Link 
              to="/app" 
              className="flex items-center text-gray-600 hover:text-indigo-600 px-3 py-2 text-sm font-medium [&.active]:text-indigo-600 [&.active]:font-semibold border-b-2 border-transparent hover:border-indigo-600 transition-colors"
            >
              <Activity className="h-4 w-4 mr-1.5" />
              Desk
            </Link>
            <Link 
              to="/workflow" 
              className="flex items-center text-gray-600 hover:text-indigo-600 px-3 py-2 text-sm font-medium [&.active]:text-indigo-600 [&.active]:font-semibold border-b-2 border-transparent hover:border-indigo-600 transition-colors"
            >
              <LayoutGrid className="h-4 w-4 mr-1.5" />
              Workflows
            </Link>
            <Link 
              to="/about" 
              className="flex items-center text-gray-600 hover:text-indigo-600 px-3 py-2 text-sm font-medium [&.active]:text-indigo-600 [&.active]:font-semibold border-b-2 border-transparent hover:border-indigo-600 transition-colors"
            >
              <Info className="h-4 w-4 mr-1.5" />
              About
            </Link>
            <button 
              className="ml-4 flex items-center text-white bg-indigo-600 hover:bg-indigo-700 px-4 py-2 rounded-md text-sm font-medium transition-colors"
              onClick={() => {
                document.cookie = "user_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
                window.location.href = "/login";
              }}
            >
              <LogOut className="h-4 w-4 mr-1.5" />
              <span>Log out</span>
            </button>
          </nav>
          
          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              type="button"
              className="inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-500"
              onClick={toggleMobileMenu}
            >
              <span className="sr-only">Open main menu</span>
              {mobileMenuOpen ? (
                <X className="block h-6 w-6" aria-hidden="true" />
              ) : (
                <Menu className="block h-6 w-6" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>
      </div>
      
      {/* Mobile menu, show/hide based on menu state */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white shadow-lg border-t">
          <div className="space-y-1 px-4 pb-3 pt-2">
            <Link
              to="/app"
              className="flex items-center rounded-md px-3 py-2 text-base font-medium text-gray-700 hover:bg-gray-50 hover:text-indigo-600 [&.active]:bg-indigo-50 [&.active]:text-indigo-600"
              onClick={() => setMobileMenuOpen(false)}
            >
              <Activity className="h-5 w-5 mr-2 text-indigo-500" />
              Desk
            </Link>
            <Link
              to="/workflow"
              className="flex items-center rounded-md px-3 py-2 text-base font-medium text-gray-700 hover:bg-gray-50 hover:text-indigo-600 [&.active]:bg-indigo-50 [&.active]:text-indigo-600"
              onClick={() => setMobileMenuOpen(false)}
            >
              <LayoutGrid className="h-5 w-5 mr-2 text-indigo-500" />
              Workflows
            </Link>
            <Link
              to="/about"
              className="flex items-center rounded-md px-3 py-2 text-base font-medium text-gray-700 hover:bg-gray-50 hover:text-indigo-600 [&.active]:bg-indigo-50 [&.active]:text-indigo-600"
              onClick={() => setMobileMenuOpen(false)}
            >
              <Info className="h-5 w-5 mr-2 text-indigo-500" />
              About
            </Link>
            <button 
              className="flex w-full items-center rounded-md px-3 py-2 mt-2 text-base font-medium text-white bg-indigo-600 hover:bg-indigo-700"
              onClick={() => {
                document.cookie = "user_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
                window.location.href = "/login";
              }}
            >
              <LogOut className="h-5 w-5 mr-2" />
              <span>Log out</span>
            </button>
          </div>
        </div>
      )}
    </header>
  )
}
