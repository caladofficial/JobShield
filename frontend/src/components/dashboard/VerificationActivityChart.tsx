'use client'

import { motion } from 'framer-motion'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { cn } from '@/lib/utils'

interface ChartDataPoint {
  label: string
  value: number
}

interface VerificationActivityChartProps {
  data: ChartDataPoint[]
  className?: string
}

export function VerificationActivityChart({ data, className }: VerificationActivityChartProps) {
  const maxValue = Math.max(...data.map(d => d.value), 1)

  return (
    <div className={cn('h-48', className)}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2A2E35" vertical={false} />
          <XAxis
            dataKey="label"
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#858B94', fontSize: 11, fontFamily: 'Inter' }}
            dy={10}
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#858B94', fontSize: 11, fontFamily: 'Inter' }}
            tickCount={4}
            domain={[0, maxValue * 1.2]}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1B1E22',
              border: '1px solid #2A2E35',
              borderRadius: '0.75rem',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5)',
            }}
            labelStyle={{ color: '#F2F2F2', fontFamily: 'Inter' }}
            itemStyle={{ color: '#F2F2F2', fontFamily: 'Inter' }}
            formatter={(value: number) => [value.toLocaleString(), 'Jobs Verified']}
          />
          <Bar
            dataKey="value"
            fill="#A8FF60"
            radius={[4, 4, 0, 0]}
            maxBarWidth={40}
          >
            {data.map((entry, index) => (
              <motion.rect
                key={index}
                initial={{ height: 0, y: maxValue * 1.2 }}
                animate={{ height: (entry.value / maxValue) * 100 * 3.5, y: (1 - entry.value / (maxValue * 1.2)) * 100 * 3.5 }}
                transition={{ delay: index * 0.1, type: 'spring', stiffness: 100, damping: 15 }}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}