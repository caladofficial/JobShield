'use client'

import { ReactNode, HTMLAttributes } from 'react'

interface SlideDownProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  className?: string
  delay?: number
  duration?: number
}

export function SlideDown({ 
  children, 
  className, 
  delay = 0, 
  duration = 300, 
  style, 
  ...props 
}: SlideDownProps) {
  const animationStyle = {
    animationDelay: `${delay}ms`,
    animationDuration: `${duration}ms`,
  } as React.CSSProperties

  return (
    <div
      className={`animate-slide-down ${className || ''}`}
      style={{ ...animationStyle, ...style }}
      {...props}
    >
      {children}
    </div>
  )
}