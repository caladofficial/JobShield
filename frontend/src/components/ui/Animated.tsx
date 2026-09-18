'use client'

import { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface AnimatedProps {
  children: ReactNode
  className?: string
  initial?: 'fade' | 'slideUp' | 'slideDown' | 'scale'
  delay?: number
  duration?: number
  ref?: React.Ref<HTMLDivElement>
  onClick?: () => void
  style?: React.CSSProperties
}

export function Animated({ 
  children, 
  className, 
  initial = 'fade', 
  delay = 0, 
  duration = 300,
  ref,
  onClick,
  style,
  ...props
}: AnimatedProps & React.HTMLAttributes<HTMLDivElement>) {
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
      onClick={onClick}
      {...props}
    >
      {children}
    </div>
  )
}

export function MotionDiv({ 
  children, 
  className, 
  initial, 
  animate, 
  transition, 
  onClick 
}: {
  children: ReactNode
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