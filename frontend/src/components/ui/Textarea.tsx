'use client'

import { forwardRef, TextareaHTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaHTMLAttributes<HTMLTextAreaElement>>(
  ({ className, ...props }, ref) => {
    return (
      <textarea
        ref={ref}
        className={cn(
          'w-full px-4 py-2.5 rounded-xl bg-surface-secondary border border-border text-primary-text placeholder-secondary-text transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent resize-y min-h-[100px]',
          className
        )}
        {...props}
      />
    )
  }
)

Textarea.displayName = 'Textarea'