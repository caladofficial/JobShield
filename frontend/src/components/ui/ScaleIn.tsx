'use client'

import { ReactNode, HTMLAttributes } from 'react'

interface ScaleInProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  className?: string
  delay?: number
  duration?: number
}

export function ScaleIn({ 
  children, 
  className, 
  delay = 0, 
  duration = 300, 
  style, 
  ...props 
}: ScaleInProps) {
  const animationStyle = {
    animationDelay: `${delay}ms`,
    animationDuration: `${duration}ms`,
  } as React.CSSProperties

  return (
    <div
      className={`animate-scale-in ${className || ''}`}
      style={{ ...animationStyle, ...style }}
      {...props}
    >
      {children}
    </div>
  )
}