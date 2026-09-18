'use client'

import { ReactNode, forwardRef } from 'react'
import { cn } from '@/lib/utils'

interface AnimatedProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  className?: string
  initial?: 'fade' | 'slideUp' | 'slideDown' | 'scale'
  delay?: number
  duration?: number
}

export const Animated = forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
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
        {props.children}
      </div>
    )
  }
)

Animated.displayName = 'Animated'

export { Animated }