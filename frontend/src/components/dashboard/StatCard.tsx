'use client'

import { forwardRef } from 'react'
import { cn } from '@/lib/utils'
import { FadeIn, ScaleIn } from '@/components/ui/Animated'

interface StatCardProps {
  label: string
  value: number
  icon: React.ReactNode
  iconColor: string
  iconBg: string
  trend?: { value: number; label: string }
  className?: string
}

export const StatCard = forwardRef<HTMLDivElement, StatCardProps>(
  ({ label, value, icon, iconColor, iconBg, trend, className }, ref) => {
    return (
      <FadeIn ref={ref} className={cn('card stat-card', className)} whileHover={{ y: -2, boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)' }} transition={{ duration: 0.2 }}>
        <div className="flex items-start justify-between">
          <div>
            <p className="stat-label">{label}</p>
            <ScaleIn delay={100} className="stat-value font-mono">
              {value.toLocaleString()}
            </ScaleIn>
            {trend && (
              <FadeIn delay={200} className={cn('inline-flex items-center gap-1 text-xs font-medium mt-2', trend.value >= 0 ? 'text-green-400' : 'text-red-400')}>
                {trend.value >= 0 ? '↑' : '↓'} {Math.abs(trend.value)}% {trend.label}
              </FadeIn>
            )}
          </div>
          <div className={cn('w-12 h-12 rounded-xl flex items-center justify-center', iconBg, iconColor)}>
            {icon}
          </div>
        </div>
      </div>
    )
  )
)

StatCard.displayName = 'StatCard'