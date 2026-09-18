'use client'

import { forwardRef, InputHTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  ({ className, type = 'text', ...props }, ref) => {
    return (
      <input
        ref={ref}
        type={type}
        className={cn(
          'w-full px-4 py-2.5 rounded-xl bg-surface-secondary border border-border text-primary-text placeholder-secondary-text transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent',
          className
        )}
        {...props}
      />
    )
  }
)

Input.displayName = 'Input'

