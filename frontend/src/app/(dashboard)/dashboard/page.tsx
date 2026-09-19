'use client'

import { useEffect, useState } from 'react'
import {
  Briefcase,
  ShieldCheck,
  AlertTriangle,
  Mail,
  Phone,
  Database,
  TrendingUp,
  Activity,
  RefreshCw,
} from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { StatCard } from '@/components/dashboard/StatCard'
import { VerificationActivityChart } from '@/components/dashboard/VerificationActivityChart'
import { JobsBySourceChart } from '@/components/dashboard/JobsBySourceChart'
import { RiskDistributionChart } from '@/components/dashboard/RiskDistributionChart'
import { RecentJobsTable } from '@/components/dashboard/RecentJobsTable'
import { SourceHealthCards } from '@/components/dashboard/SourceHealthCards'
import { analyticsApi } from '@/lib/api'
import { DashboardResponse } from '@/types/dashboard'
import { cn } from '@/lib/utils'

export default function DashboardPage() {
  const [data, setData] = useState<DashboardResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = async () => {
    try {
      setLoading(true)
      const response = await analyticsApi.dashboard()
      setData(response.data)
      setError(null)
    } catch (err) {
      setError('Failed to load dashboard data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const stats = [
    { label: 'Total Jobs', value: data?.stats.total_jobs ?? 0, icon: Briefcase, color: 'text-blue-400', bg: 'bg-blue-500/10' },
    { label: 'Verified', value: data?.stats.verified_jobs ?? 0, icon: ShieldCheck, color: 'text-green-400', bg: 'bg-green-500/10' },
    { label: 'Needs Review', value: data?.stats.needs_review ?? 0, icon: AlertTriangle, color: 'text-yellow-400', bg: 'bg-yellow-500/10' },
    { label: 'High Risk', value: data?.stats.high_risk ?? 0, icon: Activity, color: 'text-red-400', bg: 'bg-red-500/10' },
    { label: 'Contacts', value: data?.stats.total_contacts ?? 0, icon: Mail, color: 'text-purple-400', bg: 'bg-purple-500/10' },
    { label: 'Corporate Emails', value: data?.stats.corporate_emails ?? 0, icon: Mail, color: 'text-cyan-400', bg: 'bg-cyan-500/10' },
    { label: 'Valid Phones', value: data?.stats.valid_phones ?? 0, icon: Phone, color: 'text-orange-400', bg: 'bg-orange-500/10' },
    { label: 'Active Sources', value: data?.stats.sources_active ?? 0, icon: Database, color: 'text-pink-400', bg: 'bg-pink-500/10' },
  ]

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.map((_, i) => (
            <div key={i} className="animate-slide-up" style={{ animationDelay: `${i * 50}ms` }}>
              <StatCardSkeleton />
            </div>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <ChartSkeleton />
          <ChartSkeleton />
          <ChartSkeleton />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <TableSkeleton />
          <CardSkeleton />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <Card className="text-center py-12">
        <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-primary-text mb-2">Failed to load dashboard</h3>
        <p className="text-secondary-text mb-4">{error}</p>
        <button onClick={fetchData} className="btn-primary">
          <RefreshCw className="w-4 h-4 mr-2" />
          Retry
        </button>
      </Card>
    )
  }

  return (
    <div className="animate-fade-in" style={{ animationDuration: '300ms' }}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-primary-text">Dashboard</h1>
          <p className="text-secondary-text mt-1">Your job intelligence overview</p>
        </div>
        <button onClick={fetchData} className="btn-secondary" disabled={loading}>
          <RefreshCw className={cn('w-4 h-4', loading && 'animate-spin')} />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {stats.map((stat, index) => (
          <div key={stat.label} className="animate-slide-up" style={{ animationDelay: `${index * 50}ms` }}>
            <StatCard
              label={stat.label}
              value={stat.value}
              icon: stat.icon
              iconColor={stat.color}
              iconBg={stat.bg}
            />
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="animate-slide-up" style={{ animationDelay: '100ms' }}>
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium text-primary-text">Verification Activity</h3>
              <TrendingUp className="w-4 h-4 text-secondary-text" />
            </div>
            <VerificationActivityChart data={data?.verification_activity.data ?? []} />
          </Card>
        </div>

        <div className="animate-slide-up" style={{ animationDelay: '150ms' }}>
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium text-primary-text">Jobs by Source</h3>
              <Database className="w-4 h-4 text-secondary-text" />
            </div>
            <JobsBySourceChart data={data?.jobs_by_source.data ?? []} />
          </Card>
        </div>

        <div className="animate-slide-up" style={{ animationDelay: '200ms' }}>
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium text-primary-text">Risk Distribution</h3>
              <AlertTriangle className="w-4 h-4 text-secondary-text" />
            </div>
            <RiskDistributionChart data={data?.risk_distribution.data ?? []} />
          </Card>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="animate-slide-up" style={{ animationDelay: '250ms' }}>
          <RecentJobsTable jobs={data?.recent_jobs ?? []} />
        </div>

        <div className="animate-slide-up" style={{ animationDelay: '300ms' }}>
          <SourceHealthCards sources={data?.source_health ?? []} />
        </div>
      </div>

      <div className="animate-slide-up" style={{ animationDelay: '350ms' }}>
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-medium text-primary-text">Recent Activity</h3>
            <Activity className="w-4 h-4 text-secondary-text" />
          </div>
          <div className="space-y-3 max-h-64 overflow-y-auto scrollbar-thin">
            {data?.recent_events?.map((event, index) => (
              <div key={index} className="animate-slide-up" style={{ animationDelay: `${400 + index * 50}ms` }}>
                <div className="flex items-center gap-3 p-3 rounded-xl bg-surface-secondary/50">
                  <div className="w-2 h-2 rounded-full bg-accent" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-primary-text truncate">{event.message}</p>
                    <p className="text-xs text-secondary-text">{new Date(event.created_at).toLocaleString()}</p>
                  </div>
                  <span className={cn('badge px-2 py-0.5', event.level === 'error' && 'bg-red-500/20 text-red-400', event.level === 'warning' && 'bg-yellow-500/20 text-yellow-400', event.level === 'info' && 'bg-blue-500/20 text-blue-400')}>
                    {event.level}
                  </span>
                </div>
              </div>
            ))}
            {(!data?.recent_events || data.recent_events.length === 0) && (
              <p className="text-secondary-text text-center py-8">No recent activity</p>
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}

function StatCardSkeleton() {
  return (
    <Card className="animate-pulse">
      <div className="flex items-center justify-between">
        <div className="h-4 w-24 bg-surface-secondary rounded" />
        <div className="h-10 w-10 bg-surface-secondary rounded-xl" />
      </div>
      <div className="mt-4 h-8 w-32 bg-surface-secondary rounded" />
      <div className="mt-1 h-4 w-20 bg-surface-secondary rounded" />
    </Card>
  )
}

function ChartSkeleton() {
  return (
    <Card className="animate-pulse">
      <div className="h-4 w-32 bg-surface-secondary rounded mb-4" />
      <div className="h-48 bg-surface-secondary rounded" />
    </Card>
  )
}

function TableSkeleton() {
  return (
    <Card className="animate-pulse">
      <div className="h-4 w-32 bg-surface-secondary rounded mb-4" />
      <div className="space-y-3">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-12 bg-surface-secondary rounded" />
        ))}
      </div>
    </Card>
  )
}

function CardSkeleton() {
  return (
    <Card className="animate-pulse">
      <div className="h-4 w-32 bg-surface-secondary rounded mb-4" />
      <div className="space-y-3">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-10 bg-surface-secondary rounded" />
        ))}
      </div>
    </Card>
  )
}