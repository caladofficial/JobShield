'use client'

import { forwardRef } from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

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
      <motion.div
        ref={ref}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={cn('card stat-card', className)}
        whileHover={{ y: -2, boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)' }}
        transition={{ duration: 0.2 }}
      >
        <div className="flex items-start justify-between">
          <div>
            <p className="stat-label">{label}</p>
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1, type: 'spring', stiffness: 200 }}
              className="stat-value font-mono"
            >
              {value.toLocaleString()}
            </motion.div>
            {trend && (
              <motion.span
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
                className={cn('inline-flex items-center gap-1 text-xs font-medium mt-2', trend.value >= 0 ? 'text-green-400' : 'text-red-400')}
              >
                {trend.value >= 0 ? '↑' : '↓'} {Math.abs(trend.value)}% {trend.label}
              </motion.span>
            )}
          </div>
          <div className={cn('w-12 h-12 rounded-xl flex items-center justify-center', iconBg, iconColor)}>
            {icon}
          </div>
        </div>
      </motion.div>
    )
  }
)

StatCard.displayName = 'StatCard'

