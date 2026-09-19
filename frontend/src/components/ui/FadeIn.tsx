'use client'

import { ReactNode, HTMLAttributes } from 'react'

interface FadeInProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  className?: string
  delay?: number
  duration?: number
}

export default function FadeIn({ 
  children, 
  className, 
  delay = 0, 
  duration = 300, 
  style, 
  ...props 
}: FadeInProps) {
  const animationStyle = {
    animationDelay: `${delay}ms`,
    animationDuration: `${duration}ms`,
  } as React.CSSProperties

  return (
    <div
      className={`animate-fade-in ${className || ''}`}
      style={{ ...animationStyle, ...style }}
      {...props}
    >
      {children}
    </div>
  )
}