import { type ReactNode } from 'react';

interface PageLayoutProps {
  children: ReactNode;
  title?: string;
  subtitle?: string;
  fullWidth?: boolean;
  className?: string;
}

export function PageLayout({ children, title, subtitle, fullWidth = false, className = '' }: PageLayoutProps) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white pt-2">
      <div className={`mx-auto ${fullWidth ? 'w-full px-4 sm:px-6' : 'max-w-7xl px-4 sm:px-6'} pb-12`}>
        {(title || subtitle) && (
          <div className="py-6 sm:py-8 md:py-12">
            {title && <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight text-gray-900 mb-2 sm:mb-3">{title}</h1>}
            {subtitle && <p className="text-base sm:text-lg md:text-xl text-gray-600">{subtitle}</p>}
          </div>
        )}
        <div className={className}>
          {children}
        </div>
      </div>
    </div>
  )
}
