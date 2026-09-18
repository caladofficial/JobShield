'use client'

import { ReactNode, forwardRef, HTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

interface AnimatedProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  className?: string
  initial?: 'fade' | 'slideUp' | 'slideDown' | 'scale'
  delay?: number
  duration?: number
}

export const Animated = forwardRef<HTMLDivElement, AnimatedProps & React.HTMLAttributes<HTMLDivElement>>(
  ({ children, className, initial = 'fade', delay = 0, duration = 300, style, ...props }, ref) => {
    const animationClasses = {
      fade: 'animate-fade-in',
      slideUp: 'animate-slide-up',
      slideDown: 'animate-slide-down',
      scale: 'animate-scale-in',
    }

    const animationStyle = {
      animationDelay: `${delay}ms`,
      animationDuration: `${duration}ms`,
    } as React.CSSProperties

    return (
      <div
        ref={ref}
        className={cn(animationClasses[initial], className)}
        style={{ ...animationStyle, ...style }}
        {...props}
      >
        {children}
      </div>
    )
  }
)

Animated.displayName = 'Animated'

export function MotionDiv({ 
  children, 
  className, 
  initial, 
  animate, 
  transition, 
  onClick 
}: {
  children: React.ReactNode
  className?: string
  initial?: Record<string, any>
  animate?: Record<string, any>
  transition?: Record<string, any>
  onClick?: () => void
}) {
  const hasAnimation = initial || animate
  const animationClass = hasAnimation ? 'animate-fade-in' : ''

  return (
    <div
      className={cn(animationClass, className)}
      onClick={onClick}
      style={{
        ...(initial?.opacity !== undefined && { opacity: initial.opacity }),
        ...(animate?.opacity !== undefined && { opacity: animate.opacity }),
      }}
    >
      {children}
    </div>
  )
}