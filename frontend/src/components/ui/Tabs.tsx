'use client'

import { forwardRef } from 'react'
import { cn } from '@/lib/utils'

interface TabsProps {
  value: string
  onValueChange: (value: string) => void
  children: React.ReactNode
  className?: string
}

export const Tabs = forwardRef<HTMLDivElement, TabsProps>(
  ({ value, onValueChange, children, className }, ref) => {
    return (
      <div ref={ref} className={cn('space-y-4', className)}>
        {children}
      </div>
    )
  }
)

Tabs.displayName = 'Tabs'

interface TabsListProps {
  children: React.ReactNode
  className?: string
}

export const TabsList = forwardRef<HTMLDivElement, TabsListProps>(
  ({ children, className }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('flex items-center gap-1', className)}
        role="tablist"
      >
        {children}
      </div>
    )
  }
)

TabsList.displayName = 'TabsList'

interface TabsTriggerProps {
  value: string
  children: React.ReactNode
  className?: string
  disabled?: boolean
}

export const TabsTrigger = forwardRef<HTMLButtonElement, TabsTriggerProps>(
  ({ value, children, className, disabled, ...props }, ref) => {
    const context = TabsContext.useContext()
    if (!context) throw new Error('TabsTrigger must be used within Tabs')

    const isActive = context.value === value

    return (
      <button
        ref={ref}
        role="tab"
        aria-selected={isActive}
        aria-controls={`tabs-${value}`}
        id={`tabs-trigger-${value}`}
        onClick={() => !disabled && context.onValueChange(value)}
        disabled={disabled}
        className={cn(
          'px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-background',
          isActive
            ? 'bg-background text-accent shadow-card'
            : 'text-secondary-text hover:text-primary-text hover:bg-surface',
          disabled && 'opacity-50 cursor-not-allowed',
          className
        )}
        {...props}
      >
        {children}
      </button>
    )
  }
)

TabsTrigger.displayName = 'TabsTrigger'

import { createContext, useContext } from 'react'

interface TabsContextValue {
  value: string
  onValueChange: (value: string) => void
}

const TabsContext = createContext<TabsContextValue | null>(null)

interface TabsContentProps {
  value: string
  children: React.ReactNode
  className?: string
}

export const TabsContent = forwardRef<HTMLDivElement, TabsContentProps>(
  ({ value, children, className }, ref) => {
    const context = TabsContext.useContext()
    if (!context) throw new Error('TabsContent must be used within Tabs')

    if (context.value !== value) return null

    return (
      <div
        ref={ref}
        id={`tabs-${value}`}
        role="tabpanel"
        aria-labelledby={`tabs-trigger-${value}`}
        className={cn('animate-in fade-in-0 duration-200', className)}
      >
        {children}
      </div>
    )
  }
)

TabsContent.displayName = 'TabsContent'