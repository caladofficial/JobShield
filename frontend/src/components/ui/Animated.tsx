'use client'

import { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface AnimatedProps {
  children: ReactNode
  className?: string
  initial?: 'fade' | 'slideUp' | 'slideDown' | 'scale'
  delay?: number
  duration?: number
}

export function Animated({ children, className, initial = 'fade', delay = 0, duration = 300 }: AnimatedProps) {
  const animationClasses = {
    fade: 'animate-fade-in',
    slideUp: 'animate-slide-up',
    slideDown: 'animate-slide-down',
    scale: 'animate-scale-in',
  }

  const style = {
    animationDelay: `${delay}ms`,
    animationDuration: `${duration}ms`,
  } as React.CSSProperties

  return (
    <div
      className={cn(animationClasses[initial], className)}
      style={style}
    >
      {children}
    </div>
  )
}

interface MotionDivProps {
  children: ReactNode
  className?: string
  initial?: Record<string, any>
  animate?: Record<string, any>
  transition?: Record<string, any>
  onClick?: () => void
}

export function MotionDiv({ children, className, initial, animate, transition, onClick }: MotionDivProps) {
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