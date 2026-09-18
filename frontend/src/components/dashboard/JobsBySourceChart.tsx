'use client'

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { cn } from '@/lib/utils'
import { Animated } from '@/components/ui/Animated'

interface ChartDataPoint {
  label: string
  value: number
}

interface JobsBySourceChartProps {
  data: ChartDataPoint[]
  className?: string
}

const COLORS = ['#A8FF60', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16']

export function JobsBySourceChart({ data, className }: JobsBySourceChartProps) {
  if (!data.length) {
    return (
      <div className={cn('h-48 flex items-center justify-center', className)}>
        <p className="text-secondary-text">No data available</p>
      </div>
    )
  }

  const total = data.reduce((sum, d) => sum + d.value, 0)

  return (
    <div className={cn('h-48 relative', className)}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            paddingAngle={2}
            dataKey="value"
            nameKey="label"
            label={({ label, percent }) => `${label} ${(percent * 100).toFixed(0)}%`}
            labelLine={false}
            labelStyle={{ fill: '#F2F2F2', fontSize: 11, fontFamily: 'Inter' }}
          >
            {data.map((entry, index) => (
              <Animated key={`cell-${index}`} initial="scaleIn" delay={index * 100}>
                <Cell fill={COLORS[index % COLORS.length]} />
              </Animated>
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: '#1B1E22',
              border: '1px solid #2A2E35',
              borderRadius: '0.75rem',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5)',
            }}
            formatter={(value: number) => [value.toLocaleString(), 'Jobs']}
          />
          <Legend
            wrapperStyle={{ paddingTop: 20 }}
            iconType="circle"
            iconSize={8}
            layout="vertical"
            align="right"
            verticalAlign="middle"
          />
        </PieChart>
      </ResponsiveContainer>
      <Animated initial="scaleIn" delay={500} className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="text-center">
          <p className="text-2xl font-bold font-mono text-primary-text">{total.toLocaleString()}</p>
          <p className="text-xs text-secondary-text">Total Jobs</p>
        </div>
      </Animated>
    </div>
  )
}