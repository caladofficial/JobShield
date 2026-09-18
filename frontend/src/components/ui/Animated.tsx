'use client'

import { ReactNode, HTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

interface FadeInProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  className?: string
  delay?: number
  duration?: number
}

export function FadeIn({ 
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
    >
      {children}
    </div>
  )
}

export function SlideUp({ 
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
      className={`animate-slide-up ${className || ''}`}
      style={{ ...animationStyle, ...style }}
    >
      {children}
    </div>
  )
}

export function SlideDown({ 
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
      className={`animate-slide-down ${className || ''}`}
      style={{ ...animationStyle, ...style }}
    >
      {children}
    </div>
  )
}

export function ScaleIn({ 
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
      className={`animate-scale-in ${className || ''}`}
      style={{ ...animationStyle, ...style }}
    >
      {children}
    </div>
  )
}