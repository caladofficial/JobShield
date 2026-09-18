'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { cn, formatDate, formatDateTime } from '@/lib/utils'
import { exportsApi } from '@/lib/api'
import { ExportResponse, PaginatedResponse } from '@/types/dashboard'
import { DataTable } from '@/components/ui/DataTable'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { Modal } from '@/components/ui/Modal'
import {
  Download,
  FileSpreadsheet,
  Filter,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Loader2,
  X,
  CheckCircle,
  Clock,
  AlertCircle,
} from 'lucide-react'

const STATUS_BADGES: Record<string, string> = {
  pending: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  processing: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  completed: 'bg-green-500/20 text-green-400 border-green-500/30',
  failed: 'bg-red-500/20 text-red-400 border-red-500/30',
  expired: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
}

const STATUS_ICONS: Record<string, React.ReactNode> = {
  pending: <Clock className="w-4 h-4" />,
  processing: <Loader2 className="w-4 h-4 animate-spin" />,
  completed: <CheckCircle className="w-4 h-4" />,
  failed: <AlertCircle className="w-4 h-4" />,
  expired: <X className="w-4 h-4" />,
}

export default function ExportsPage() {
  const [exports, setExports] = useState<ExportResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [modalOpen, setModalOpen] = useState(false)
  const [exportForm, setExportForm] = useState({
    format: 'xlsx' as 'xlsx' | 'csv',
    filters: {} as Record<string, any>,
  })
  const [exporting, setExporting] = useState(false)

  useEffect(() => {
    fetchExports()
  }, [page, pageSize])

  const fetchExports = async () => {
    setLoading(true)
    try {
      const response = await exportsApi.list({ page, page_size: pageSize })
      const data: PaginatedResponse<ExportResponse> = response.data
      setExports(data.items)
      setTotal(data.total)
    } catch (error) {
      console.error('Failed to fetch exports:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    setExporting(true)
    try {
      const response = await exportsApi.create(exportForm)
      setModalOpen(false)
      fetchExports()
    } catch (error) {
      console.error('Failed to create export:', error)
    } finally {
      setExporting(false)
    }
  }

  const handleDownload = async (exportId: number) => {
    try {
      const response = await exportsApi.download(exportId)
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `JobShield_${new Date().toISOString().split('T')[0]}.xlsx`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to download export:', error)
    }
  }

  const columns = [
    {
      header: 'Format',
      accessor: 'format',
      cell: (exp: ExportResponse) => (
        <Badge variant="outline" className="text-xs">
          <FileSpreadsheet className="w-3 h-3 mr-1" />
          {exp.format.toUpperCase()}
        </Badge>
      ),
    },
    {
      header: 'Status',
      accessor: 'status',
      cell: (exp: ExportResponse) => (
        <Badge variant="outline" className={cn('text-xs', STATUS_BADGES[exp.status])}>
          {STATUS_ICONS[exp.status]}
          {exp.status.charAt(0).toUpperCase() + exp.status.slice(1)}
        </Badge>
      ),
    },
    {
      header: 'Rows',
      accessor: 'row_count',
      cell: (exp: ExportResponse) => <span className="font-mono text-sm">{exp.row_count.toLocaleString()}</span>,
    },
    {
      header: 'Filters',
      accessor: 'filters',
      cell: (exp: ExportResponse) => (
        <span className="text-secondary-text text-sm max-w-[200px] truncate block">
          {Object.keys(exp.filters).length > 0 ? JSON.stringify(exp.filters) : 'All jobs'}
        </span>
      ),
    },
    {
      header: 'Created',
      accessor: 'created_at',
      cell: (exp: ExportResponse) => <span className="text-secondary-text text-sm font-mono">{formatDateTime(exp.created_at)}</span>,
    },
    {
      header: 'Completed',
      accessor: 'completed_at',
      cell: (exp: ExportResponse) => <span className="text-secondary-text text-sm font-mono">{exp.completed_at ? formatDateTime(exp.completed_at) : '—'}</span>,
    },
    {
      header: 'Actions',
      accessor: 'actions',
      cell: (exp: ExportResponse) => (
        <div className="flex items-center gap-1 justify-end">
          {exp.status === 'completed' && exp.download_url && (
            <Button size="sm" variant="secondary" onClick={() => handleDownload(exp.id)}>
              <Download className="w-3.5 h-3.5 mr-1" />
              Download
            </Button>
          )}
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-primary-text">Exports</h1>
          <p className="text-secondary-text mt-1">Download job data as Excel or CSV files</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" onClick={fetchExports} disabled={loading}>
            <RefreshCw className={cn('w-4 h-4', loading && 'animate-spin')} />
            Refresh
          </Button>
          <Button onClick={() => setModalOpen(true)}>
            <FileSpreadsheet className="w-4 h-4 mr-2" />
            New Export
          </Button>
        </div>
      </div>

      <DataTable
        columns={columns}
        data={exports}
        loading={loading}
        emptyMessage="No exports found"
        pagination={{
          page,
          pageSize,
          total,
          onPageChange: setPage,
          onPageSizeChange: setPageSize,
        }}
      />

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Create Export" size="md">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-secondary-text mb-1">Format</label>
            <select
              value={exportForm.format}
              onChange={(e) => setExportForm(prev => ({ ...prev, format: e.target.value as 'xlsx' | 'csv' }))}
              className="w-full px-4 py-2.5 rounded-xl bg-surface-secondary border border-border text-primary-text focus:outline-none focus:ring-2 focus:ring-accent"
            >
              <option value="xlsx">Excel (.xlsx)</option>
              <option value="csv">CSV (.csv)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-text mb-1">Filters (Optional)</label>
            <div className="space-y-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" className="w-4 h-4 rounded border-border bg-surface-secondary text-accent focus:ring-accent" />
                <span className="text-sm text-secondary-text">Only verified jobs</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" className="w-4 h-4 rounded border-border bg-surface-secondary text-accent focus:ring-accent" />
                <span className="text-sm text-secondary-text">Only jobs with emails</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" className="w-4 h-4 rounded border-border bg-surface-secondary text-accent focus:ring-accent" />
                <span className="text-sm text-secondary-text">Only jobs with phones</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" className="w-4 h-4 rounded border-border bg-surface-secondary text-accent focus:ring-accent" />
                <span className="text-sm text-secondary-text">Exclude high risk jobs</span>
              </label>
            </div>
          </div>

          <div className="flex gap-2 pt-2">
            <Button variant="secondary" onClick={() => setModalOpen(false)} className="flex-1" disabled={exporting}>
              Cancel
            </Button>
            <Button onClick={handleExport} className="flex-1" disabled={exporting}>
              {exporting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  Creating...
                </>
              ) : (
                'Create Export'
              )}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

