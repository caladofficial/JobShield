'use client'

import {
  BarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { cn } from '@/lib/utils'
import { ScaleIn } from '@/components/ui/Animated'

interface ChartDataPoint {
  label: string
  value: number
}

interface RiskDistributionChartProps {
  data: ChartDataPoint[]
  className?: string
}

const RISK_COLORS: Record<string, string> = {
  low: '#22C55E',
  medium: '#F59E0B',
  high: '#EF4444',
  unknown: '#6B7280',
}

export function RiskDistributionChart({ data, className }: RiskDistributionChartProps) {
  if (!data.length) {
    return (
      <div className={cn('h-48 flex items-center justify-center', className)}>
        <p className="text-secondary-text">No risk data available</p>
      </div>
    )
  }

  const maxValue = Math.max(...data.map(d => d.value), 1)

  return (
    <div className={cn('h-48 relative', className)}>
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
            formatter={(value: number) => [value.toLocaleString(), 'Jobs']}
          />
          <Legend
            wrapperStyle={{ paddingTop: 20 }}
            iconType="circle"
            iconSize={8}
            layout="horizontal"
            align="center"
          />
          <Bar
            dataKey="value"
            radius={[4, 4, 0, 0]}
            maxBarWidth={50}
          >
            {data.map((entry, index) => (
              <ScaleIn key={index} delay={index * 100}>
                <Cell fill={RISK_COLORS[entry.label.toLowerCase()] || '#6B7280'} />
              </ScaleIn>
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}