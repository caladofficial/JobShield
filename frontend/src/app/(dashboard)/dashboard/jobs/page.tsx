'use client'

import { useState, useEffect, useCallback } from 'react'
import { cn, formatDate, formatCurrency, getRiskBadgeClass, getStatusBadgeClass, getStatusLabel } from '@/lib/utils'
import { jobsApi, sourcesApi } from '@/lib/api'
import { JobListItem, PaginatedResponse, JobStatus, RiskLevel, SourceResponse } from '@/types/dashboard'
import { DataTable } from '@/components/ui/DataTable'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'

import {
  Search,
  Filter,
  ChevronDown,
  ChevronUp,
  Download,
  Plus,
  ExternalLink,
  Mail,
  Phone,
  ShieldCheck,
  AlertTriangle,
  Activity,
  RefreshCw,
  Loader2,
} from 'lucide-react'

const STATUS_OPTIONS = [
  { value: '', label: 'All Status' },
  { value: 'new', label: 'New' },
  { value: 'processing', label: 'Processing' },
  { value: 'verified', label: 'Verified' },
  { value: 'needs_review', label: 'Needs Review' },
  { value: 'suspicious', label: 'Suspicious' },
  { value: 'high_risk', label: 'High Risk' },
  { value: 'unable_to_verify', label: 'Unable to Verify' },
  { value: 'expired', label: 'Expired' },
  { value: 'duplicate', label: 'Duplicate' },
]

const RISK_OPTIONS = [
  { value: '', label: 'All Risk Levels' },
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'unknown', label: 'Unknown' },
]

const SORT_OPTIONS = [
  { value: 'created_at', label: 'Created Date' },
  { value: 'posted_at', label: 'Posted Date' },
  { value: 'title', label: 'Title' },
  { value: 'verification_score', label: 'Verification Score' },
  { value: 'risk_level', label: 'Risk Level' },
]

export default function JobsPage() {
  const [jobs, setJobs] = useState<JobListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [sources, setSources] = useState<SourceResponse[]>([])
  const [filters, setFilters] = useState({
    search: '',
    status: '',
    risk_level: '',
    source_id: '',
    has_email: false,
    has_phone: false,
    sort_by: 'created_at',
    sort_order: 'desc',
  })
  const [showFilters, setShowFilters] = useState(false)
  const [scanModalOpen, setScanModalOpen] = useState(false)
  const [scanUrl, setScanUrl] = useState('')
  const [scanSourceId, setScanSourceId] = useState('')
  const [scanning, setScanning] = useState(false)

  const fetchJobs = useCallback(async () => {
    setLoading(true)
    try {
      const params = {
        page,
        page_size: pageSize,
        ...filters,
      }
      const response = await jobsApi.list(params)
      const data: PaginatedResponse<JobListItem> = response.data
      setJobs(data.items)
      setTotal(data.total)
    } catch (error) {
      console.error('Failed to fetch jobs:', error)
    } finally {
      setLoading(false)
    }
  }, [page, pageSize, filters])

  const fetchSources = useCallback(async () => {
    try {
      const response = await sourcesApi.list()
      setSources(response.data)
    } catch (error) {
      console.error('Failed to fetch sources:', error)
    }
  }, [])

  useEffect(() => {
    fetchJobs()
    fetchSources()
  }, [fetchJobs, fetchSources])

  const handleScan = async () => {
    if (!scanUrl.trim()) return
    setScanning(true)
    try {
      await jobsApi.scan({ source_url: scanUrl, source_id: scanSourceId ? parseInt(scanSourceId) : undefined })
      setScanModalOpen(false)
      setScanUrl('')
      setScanSourceId('')
      fetchJobs()
    } catch (error) {
      console.error('Failed to scan job:', error)
    } finally {
      setScanning(false)
    }
  }

  const handleExport = async () => {
    try {
      const response = await jobsApi.list({ ...filters, page: 1, page_size: 10000 })
      // Trigger export via exports API
      // This would need the exports API to be called
    } catch (error) {
      console.error('Failed to export:', error)
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
      cell: (job: JobListItem) => (
        <span className="text-secondary-text truncate max-w-[150px] block">
          {job.company_name || '—'}
        </span>
      ),
    },
    {
      header: 'Location',
      accessor: 'location',
      cell: (job: JobListItem) => <span className="text-secondary-text">{job.location || '—'}</span>,
    },
    {
      header: 'Type',
      accessor: 'employment_type',
      cell: (job: JobListItem) => (
        <Badge variant="outline" className="text-xs">
          {job.employment_type || '—'}
        </Badge>
      ),
    },
    {
      header: 'Salary',
      accessor: 'salary',
      cell: (job: JobListItem) => (
        <span className="font-mono text-sm">
          {job.salary_min || job.salary_max ? (
            `${formatCurrency(job.salary_min)} - ${formatCurrency(job.salary_max)} ${job.currency}`
          ) : (
            '—'
          )}
        </span>
      ),
    },
    {
      header: 'Source',
      accessor: 'source_name',
      cell: (job: JobListItem) => (
        <Badge variant="outline" className="text-xs">
          {job.source_name}
        </Badge>
      ),
    },
    {
      header: 'Risk',
      accessor: 'risk_level',
      cell: (job: JobListItem) => (
        <Badge variant={getRiskBadgeClass(job.risk_level).replace('badge-', '') as any}>
          {job.risk_level}
        </Badge>
      ),
    },
    {
      header: 'Status',
      accessor: 'status',
      cell: (job: JobListItem) => (
        <Badge variant={getStatusBadgeClass(job.status).replace('badge-', '') as any}>
          {getStatusLabel(job.status)}
        </Badge>
      ),
    },
    {
      header: 'Score',
      accessor: 'verification_score',
      cell: (job: JobListItem) => (
        <span className={cn('font-mono text-sm', job.verification_score !== null && job.verification_score >= 70 ? 'text-green-400' : job.verification_score !== null && job.verification_score >= 40 ? 'text-yellow-400' : 'text-red-400')}>
          {job.verification_score !== null ? `${job.verification_score.toFixed(1)}%` : '—'}
        </span>
      ),
    },
    {
      header: 'Contacts',
      accessor: 'contacts',
      cell: (job: JobListItem) => (
        <div className="flex items-center gap-1">
          {job.has_email && <Mail className="w-3.5 h-3.5 text-green-400" />}
          {job.has_phone && <Phone className="w-3.5 h-3.5 text-blue-400" />}
        </div>
      ),
    },
    {
      header: 'Posted',
      accessor: 'posted_at',
      cell: (job: JobListItem) => (
        <span className="text-secondary-text text-sm font-mono">
          {formatDate(job.posted_at || job.created_at)}
        </span>
      ),
    },
    {
      header: '',
      accessor: 'actions',
      cell: (job: JobListItem) => (
        <div className="flex items-center gap-1 justify-end">
          <a
            href={`/dashboard/jobs/${job.id}`}
            className="p-1.5 rounded-lg text-secondary-text hover:text-primary-text hover:bg-surface-secondary transition-colors"
            title="View details"
          >
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-primary-text">Jobs</h1>
          <p className="text-secondary-text mt-1">Manage and verify job postings</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" onClick={() => fetchJobs()} disabled={loading}>
            <RefreshCw className={cn('w-4 h-4', loading && 'animate-spin')} />
            Refresh
          </Button>
          <Button onClick={() => setScanModalOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Scan Job URL
          </Button>
        </div>
      </div>

      <Card className={cn('overflow-hidden', !showFilters && 'mb-0')}>
        <div className="p-4 border-b border-border">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-secondary-text" />
              <Input
                placeholder="Search jobs..."
                value={filters.search}
                onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                className="pl-10"
              />
            </div>
            <Button variant="ghost" onClick={() => setShowFilters(!showFilters)}>
              <Filter className="w-4 h-4 mr-2" />
              Filters
              {showFilters ? <ChevronUp className="w-4 h-4 ml-1" /> : <ChevronDown className="w-4 h-4 ml-1" />}
            </Button>
          </div>
        </div>

        <div className={cn('transition-all duration-200 overflow-hidden', showFilters ? 'h-auto opacity-100' : 'h-0 opacity-0')}>
          {showFilters && (
            <div className="p-4 border-t border-border bg-surface-secondary/30">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
                <Select
                  value={filters.status}
                  onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
                  options={STATUS_OPTIONS}
                  placeholder="Status"
                />
                <Select
                  value={filters.risk_level}
                  onChange={(e) => setFilters(prev => ({ ...prev, risk_level: e.target.value }))}
                  options={RISK_OPTIONS}
                  placeholder="Risk Level"
                />
                <Select
                  value={filters.source_id}
                  onChange={(e) => setFilters(prev => ({ ...prev, source_id: e.target.value }))}
                  options={[{ value: '', label: 'All Sources' }, ...sources.map(s => ({ value: String(s.id), label: s.display_name }))]}
                  placeholder="Source"
                />
                <Select
                  value={filters.sort_by}
                  onChange={(e) => setFilters(prev => ({ ...prev, sort_by: e.target.value }))}
                  options={SORT_OPTIONS}
                  placeholder="Sort By"
                />
                <Select
                  value={filters.sort_order}
                  onChange={(e) => setFilters(prev => ({ ...prev, sort_order: e.target.value }))}
                  options={[
                    { value: 'desc', label: 'Descending' },
                    { value: 'asc', label: 'Ascending' },
                  ]}
                  placeholder="Order"
                />
              </div>
              <div className="flex items-center gap-4 mt-3">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={filters.has_email}
                    onChange={(e) => setFilters(prev => ({ ...prev, has_email: e.target.checked }))}
                    className="w-4 h-4 rounded border-border bg-surface-secondary text-accent focus:ring-accent"
                  />
                  <span className="text-sm text-secondary-text">Has Email</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={filters.has_phone}
                    onChange={(e) => setFilters(prev => ({ ...prev, has_phone: e.target.checked }))}
                    className="w-4 h-4 rounded border-border bg-surface-secondary text-accent focus:ring-accent"
                  />
                  <span className="text-sm text-secondary-text">Has Phone</span>
                </label>
              </div>
            </div>
          )}
        </div>
      </Card>

      <Card>
        <DataTable
          columns={columns}
          data={jobs}
          loading={loading}
          emptyMessage="No jobs found"
          pagination={{
            page,
            pageSize,
            total,
            onPageChange: setPage,
            onPageSizeChange: setPageSize,
          }}
        />
      </Card>

      <Modal open={scanModalOpen} onClose={() => setScanModalOpen(false)} title="Scan Job URL" size="md">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-secondary-text mb-1">Job URL</label>
            <Input
              value={scanUrl}
              onChange={(e) => setScanUrl(e.target.value)}
              placeholder="https://example.com/job/123"
              disabled={scanning}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-text mb-1">Source (Optional)</label>
            <Select
              value={scanSourceId}
              onValueChange={setScanSourceId}
              options={[{ value: '', label: 'Auto-detect' }, ...sources.map(s => ({ value: String(s.id), label: s.display_name }))]}
              placeholder="Select source"
              disabled={scanning}
            />
          </div>

          <div className="flex gap-2 pt-2">
            <Button variant="secondary" onClick={() => setScanModalOpen(false)} className="flex-1" disabled={scanning}>
              Cancel
            </Button>
            <Button onClick={handleScan} className="flex-1" disabled={scanning || !scanUrl.trim()}>
              {scanning ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  Scanning...
                </>
              ) : (
                'Scan Job'
              )}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}