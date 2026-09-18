'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'
import { analyticsApi } from '@/lib/api'
import { DashboardResponse } from '@/types/dashboard'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { VerificationActivityChart } from '@/components/dashboard/VerificationActivityChart'
import { JobsBySourceChart } from '@/components/dashboard/JobsBySourceChart'
import { RiskDistributionChart } from '@/components/dashboard/RiskDistributionChart'
import { DataTable } from '@/components/ui/DataTable'
import {
  TrendingUp,
  Database,
  AlertTriangle,
  Activity,
  RefreshCw,
  Loader2,
  BarChart3,
  PieChart,
  LineChart,
} from 'lucide-react'

export default function AnalyticsPage() {
  const [data, setData] = useState<DashboardResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    try {
      const [dashboardRes, sourcesRes, riskRes] = await Promise.all([
        analyticsApi.dashboard(),
        analyticsApi.sources(),
        analyticsApi.risk(),
      ])
      setData({
        ...dashboardRes.data,
        sources_analytics: sourcesRes.data,
        risk_analytics: riskRes.data,
      } as any)
    } catch (error) {
      console.error('Failed to fetch analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <ChartSkeleton />
          <ChartSkeleton />
          <ChartSkeleton />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartSkeleton />
          <ChartSkeleton />
        </div>
        <Card className="animate-pulse">
          <div className="h-6 w-32 bg-surface-secondary rounded mb-4" />
          <div className="h-64 bg-surface-secondary rounded" />
        </Card>
      </div>
    )
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-primary-text">Analytics</h1>
          <p className="text-secondary-text mt-1">Insights into your job verification data</p>
        </div>
        <Button variant="secondary" onClick={fetchData} disabled={loading}>
          <RefreshCw className={cn('w-4 h-4', loading && 'animate-spin')} />
          Refresh
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium text-primary-text">Verification Activity (7 Days)</h3>
              <LineChart className="w-4 h-4 text-secondary-text" />
            </div>
            <VerificationActivityChart data={data?.verification_activity.data ?? []} />
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium text-primary-text">Jobs by Source</h3>
              <PieChart className="w-4 h-4 text-secondary-text" />
            </div>
            <JobsBySourceChart data={data?.jobs_by_source.data ?? []} />
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium text-primary-text">Risk Distribution</h3>
              <AlertTriangle className="w-4 h-4 text-secondary-text" />
            </div>
            <RiskDistributionChart data={data?.risk_distribution.data ?? []} />
          </Card>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
          <Card>
            <h3 className="font-medium text-primary-text mb-4">Source Performance</h3>
            <DataTable
              columns={[
                { header: 'Source', accessor: 'source', cell: (row: any) => <Badge variant="outline" className="text-xs">{row.source}</Badge> },
                { header: 'Total Jobs', accessor: 'total_jobs', cell: (row: any) => <span className="font-mono">{row.total_jobs}</span> },
                { header: 'Verified', accessor: 'verified_jobs', cell: (row: any) => <span className="font-mono text-green-400">{row.verified_jobs}</span> },
                { header: 'Verification Rate', accessor: 'verification_rate', cell: (row: any) => <span className="font-mono">{row.verification_rate}%</span> },
              ]}
              data={(data as any)?.sources_analytics ?? []}
              loading={false}
              emptyMessage="No source data available"
            />
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Card>
            <h3 className="font-medium text-primary-text mb-4">Top Risk Signals</h3>
            <DataTable
              columns={[
                { header: 'Signal', accessor: 'signal', cell: (row: any) => <span className="font-medium text-primary-text">{row.signal.replace(/_/g, ' ')}</span> },
                { header: 'Count', accessor: 'count', cell: (row: any) => <span className="font-mono">{row.count}</span> },
              ]}
              data={(data as any)?.risk_analytics ?? []}
              loading={false}
              emptyMessage="No risk signals detected"
            />
          </Card>
        </motion.div>
      </div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
        <Card>
          <h3 className="font-medium text-primary-text mb-4">Detailed Metrics</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard label="Avg Verification Score" value={data?.stats.verified_jobs && data?.stats.total_jobs ? Math.round((data.stats.verified_jobs / data.stats.total_jobs) * 100) : 0} suffix="%" icon={<TrendingUp />} color="text-blue-400" bg="bg-blue-500/10" />
            <MetricCard label="High Risk %" value={data?.stats.total_jobs ? Math.round((data.stats.high_risk / data.stats.total_jobs) * 100) : 0} suffix="%" icon={<AlertTriangle />} color="text-red-400" bg="bg-red-500/10" />
            <MetricCard label="Contacts/Job" value={data?.stats.total_jobs ? Math.round((data.stats.total_contacts / data.stats.total_jobs) * 10) / 10 : 0} icon={<Mail />} color="text-purple-400" bg="bg-purple-500/10" />
            <MetricCard label="Corporate Email %" value={data?.stats.emails_found ? Math.round((data.stats.corporate_emails / data.stats.emails_found) * 100) : 0} suffix="%" icon={<Building2 />} color="text-green-400" bg="bg-green-500/10" />
          </div>
        </Card>
      </motion.div>
    </motion.div>
  )
}

function ChartSkeleton() {
  return (
    <Card className="animate-pulse">
      <div className="h-6 w-48 bg-surface-secondary rounded mb-4" />
      <div className="h-48 bg-surface-secondary rounded" />
    </Card>
  )
}

function MetricCard({ label, value, suffix = '', icon: Icon, color, bg }: any) {
  return (
    <Card>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-secondary-text">{label}</p>
          <p className="text-2xl font-bold text-primary-text font-mono mt-1">{value}{suffix}</p>
        </div>
        <div className={cn('w-10 h-10 rounded-xl flex items-center justify-center', bg, color)}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </Card>
  )
}

import { Mail, Building2 } from 'lucide-react'

