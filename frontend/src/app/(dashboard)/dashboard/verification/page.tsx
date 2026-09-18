'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { cn, formatDate, getRiskBadgeClass, getStatusBadgeClass, getStatusLabel } from '@/lib/utils'
import { jobsApi } from '@/lib/api'
import { JobListItem, PaginatedResponse, JobStatus, RiskLevel } from '@/types/dashboard'
import { DataTable } from '@/components/ui/DataTable'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import {
  ShieldCheck,
  AlertTriangle,
  Activity,
  Search,
  Filter,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  RefreshCw,
  Loader2,
} from 'lucide-react'

const STATUS_OPTIONS = [
  { value: '', label: 'All Status' },
  { value: 'verified', label: 'Verified' },
  { value: 'needs_review', label: 'Needs Review' },
  { value: 'suspicious', label: 'Suspicious' },
  { value: 'high_risk', label: 'High Risk' },
  { value: 'unable_to_verify', label: 'Unable to Verify' },
]

const RISK_OPTIONS = [
  { value: '', label: 'All Risk Levels' },
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'unknown', label: 'Unknown' },
]

export default function VerificationPage() {
  const [jobs, setJobs] = useState<JobListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [filters, setFilters] = useState({
    status: '',
    risk_level: '',
    sort_by: 'verified_at',
    sort_order: 'desc',
  })
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    fetchJobs()
  }, [page, pageSize, filters])

  const fetchJobs = async () => {
    setLoading(true)
    try {
      const params = {
        page,
        page_size: pageSize,
        ...filters,
      }
      const response = await jobsApi.list(params)
      const data: PaginatedResponse<JobListItem> = response.data
      setJobs(data.items.filter(j => j.status !== 'new' && j.status !== 'processing'))
      setTotal(data.total)
    } catch (error) {
      console.error('Failed to fetch jobs:', error)
    } finally {
      setLoading(false)
    }
  }

  const columns = [
    {
      header: 'Job Title',
      accessor: 'title',
      cell: (job: JobListItem) => (
        <a href={`/dashboard/jobs/${job.id}`} className="font-medium text-primary-text hover:text-accent">
          {job.title}
        </a>
      ),
    },
    {
      header: 'Company',
      accessor: 'company_name',
      cell: (job: JobListItem) => <span className="text-secondary-text">{job.company_name || '—'}</span>,
    },
    {
      header: 'Source',
      accessor: 'source_name',
      cell: (job: JobListItem) => <Badge variant="outline" className="text-xs">{job.source_name}</Badge>,
    },
    {
      header: 'Risk',
      accessor: 'risk_level',
      cell: (job: JobListItem) => <Badge variant={getRiskBadgeClass(job.risk_level).replace('badge-', '') as any}>{job.risk_level}</Badge>,
    },
    {
      header: 'Status',
      accessor: 'status',
      cell: (job: JobListItem) => <Badge variant={getStatusBadgeClass(job.status).replace('badge-', '') as any}>{getStatusLabel(job.status)}</Badge>,
    },
    {
      header: 'Confidence',
      accessor: 'verification_score',
      cell: (job: JobListItem) => (
        <span className={cn('font-mono text-sm', job.verification_score !== null && job.verification_score >= 70 ? 'text-green-400' : job.verification_score !== null && job.verification_score >= 40 ? 'text-yellow-400' : 'text-red-400')}>
          {job.verification_score !== null ? `${job.verification_score.toFixed(1)}%` : '—'}
        </span>
      ),
    },
    {
      header: 'Verified',
      accessor: 'verified_at',
      cell: (job: JobListItem) => <span className="text-secondary-text text-sm font-mono">{job.verified_at ? formatDate(job.verified_at) : '—'}</span>,
    },
    {
      header: 'Actions',
      accessor: 'actions',
      cell: (job: JobListItem) => (
        <a href={`/dashboard/jobs/${job.id}`} className="p-1.5 rounded-lg text-secondary-text hover:text-primary-text hover:bg-surface-secondary" title="View details">
          <ExternalLink className="w-4 h-4" />
        </a>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-primary-text">Verification</h1>
          <p className="text-secondary-text mt-1">Review and manage job verification results</p>
        </div>
        <Button variant="secondary" onClick={fetchJobs} disabled={loading}>
          <RefreshCw className={cn('w-4 h-4', loading && 'animate-spin')} />
          Refresh
        </Button>
      </div>

      <div className="card p-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-secondary-text" />
            <input
              type="text"
              placeholder="Search verified jobs..."
              className="w-full pl-10 px-4 py-2.5 rounded-xl bg-surface-secondary border border-border text-primary-text placeholder-secondary-text focus:outline-none focus:ring-2 focus:ring-accent"
            />
          </div>
          <Button variant="ghost" onClick={() => setShowFilters(!showFilters)}>
            <Filter className="w-4 h-4 mr-2" />
            Filters
            {showFilters ? <ChevronUp className="w-4 h-4 ml-1" /> : <ChevronDown className="w-4 h-4 ml-1" />}
          </Button>
        </div>

        {showFilters && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="mt-4 pt-4 border-t border-border"
          >
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <select
                value={filters.status}
                onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
                className="px-4 py-2.5 rounded-xl bg-surface-secondary border border-border text-primary-text focus:outline-none focus:ring-2 focus:ring-accent"
              >
                {STATUS_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
              </select>
              <select
                value={filters.risk_level}
                onChange={(e) => setFilters(prev => ({ ...prev, risk_level: e.target.value }))}
                className="px-4 py-2.5 rounded-xl bg-surface-secondary border border-border text-primary-text focus:outline-none focus:ring-2 focus:ring-accent"
              >
                {RISK_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
              </select>
            </div>
          </motion.div>
        )}
      </div>

      <DataTable
        columns={columns}
        data={jobs}
        loading={loading}
        emptyMessage="No verified jobs found"
        pagination={{
          page,
          pageSize,
          total,
          onPageChange: setPage,
          onPageSizeChange: setPageSize,
        }}
      />
    </div>
  )
}