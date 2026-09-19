'use client'

import { ReactNode, HTMLAttributes } from 'react'

interface SlideUpProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  className?: string
  delay?: number
  duration?: number
}

export default function SlideUp({ 
  children, 
  className, 
  delay = 0, 
  duration = 300, 
  style, 
  ...props 
}: SlideUpProps) {
  const animationStyle = {
    animationDelay: `${delay}ms`,
    animationDuration: `${duration}ms`,
  } as React.CSSProperties

  return (
    <div
      className={`animate-slide-up ${className || ''}`}
      style={{ ...animationStyle, ...style }}
      {...props}
    >
      {children}
    </div>
  )
}