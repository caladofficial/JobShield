'use client'

import { forwardRef } from 'react'
import { cn } from '@/lib/utils'
import { ChevronLeft, ChevronRight, Loader2 } from 'lucide-react'
import { Animated } from '@/components/ui/Animated'

interface Column<T> {
  header: string
  accessor: keyof T | string
  cell?: (row: T) => React.ReactNode
  className?: string
}

interface PaginationProps {
  page: number
  pageSize: number
  total: number
  onPageChange: (page: number) => void
  onPageSizeChange: (pageSize: number) => void
}

interface DataTableProps<T> {
  columns: Column<T>[]
  data: T[]
  loading?: boolean
  emptyMessage?: string
  pagination?: PaginationProps
  className?: string
  rowKey?: keyof T | ((row: T) => string)
}

function Pagination({ page, pageSize, total, onPageChange, onPageSizeChange }: PaginationProps) {
  const totalPages = Math.ceil(total / pageSize)

  if (totalPages <= 1) return null

  return (
    <div className="flex items-center justify-between py-4 border-t border-border">
      <div className="text-sm text-secondary-text">
        Showing {((page - 1) * pageSize) + 1} to {Math.min(page * pageSize, total)} of {total} results
      </div>
      <div className="flex items-center gap-2">
        <select
          value={pageSize}
          onChange={(e) => onPageSizeChange(Number(e.target.value))}
          className="px-3 py-1.5 rounded-lg bg-surface-secondary border border-border text-primary-text text-sm focus:outline-none focus:ring-2 focus:ring-accent"
        >
          {[10, 20, 50, 100].map((size) => (
            <option key={size} value={size}>
              {size} per page
            </option>
          ))}
        </select>
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page === 1}
          className="p-2 rounded-lg text-secondary-text hover:text-primary-text hover:bg-surface-secondary disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
        <span className="text-sm text-secondary-text px-2">
          Page {page} of {totalPages}
        </span>
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page === totalPages}
          className="p-2 rounded-lg text-secondary-text hover:text-primary-text hover:bg-surface-secondary disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}

export function DataTable<T extends Record<string, any>>({
  columns,
  data,
  loading = false,
  emptyMessage = 'No data available',
  pagination,
  className,
  rowKey = 'id',
}: DataTableProps<T>) {
  const getRowKey = (row: T) => {
    if (typeof rowKey === 'function') return rowKey(row)
    return row[rowKey as keyof T] as string
  }

  if (loading) {
    return (
      <div className={cn('table-container', className)}>
        <table className="table">
          <thead>
            <tr>
              {columns.map((col) => (
                <th key={col.header} className={col.className}>
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {[...Array(5)].map((_, i) => (
              <Animated key={i} initial="fade" delay={i * 100}>
                <tr>
                  {columns.map((col) => (
                    <td key={col.header} className={col.className}>
                      <div className="h-4 bg-surface-secondary rounded animate-pulse" style={{ width: '60%' }} />
                    </td>
                  ))}
                </tr>
              </Animated>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  if (!data.length) {
    return (
      <div className={cn('card text-center py-12', className)}>
        <div className="text-secondary-text">{emptyMessage}</div>
      </div>
    )
  }

  return (
    <div className={cn('table-container', className)}>
      <table className="table">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.header} className={cn(col.className)}>
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rowIndex) => (
            <Animated key={getRowKey(row)} initial="fade" delay={rowIndex * 30}>
              <tr className="hover:bg-surface-secondary/50 transition-colors">
                {columns.map((col) => (
                  <td key={col.header} className={cn(col.className)}>
                    {col.cell ? col.cell(row) : row[col.accessor as keyof T]}
                  </td>
                ))}
              </tr>
            </Animated>
          ))}
        </tbody>
      </table>
      {pagination && <Pagination {...pagination} />}
    </div>
  )
}