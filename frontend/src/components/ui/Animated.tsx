'use client'

import { ReactNode, HTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

interface AnimatedProps extends HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  className?: string
  initial?: 'fade' | 'slideUp' | 'slideDown' | 'scale'
  delay?: number
  duration?: number
}

export function Animated({ 
  children, 
  className, 
  initial = 'fade', 
  delay = 0, 
  duration = 300, 
  style, 
  ...props 
}: AnimatedProps) {
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
      className={cn(animationClasses[initial], className)}
      style={{ ...animationStyle, ...style }}
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