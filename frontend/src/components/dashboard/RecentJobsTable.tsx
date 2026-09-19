'use client'

import Link from 'next/link'
import { cn, formatDate, getRiskBadgeClass, getStatusBadgeClass, getStatusLabel } from '@/lib/utils'
import { JobListItem } from '@/types/dashboard'
import { ExternalLink, Mail, Phone, ShieldCheck, AlertTriangle, Activity } from 'lucide-react'

interface RecentJobsTableProps {
  jobs: JobListItem[]
  className?: string
}

export function RecentJobsTable({ jobs, className }: RecentJobsTableProps) {
  if (!jobs.length) {
    return (
      <div className={cn('card', className)}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-medium text-primary-text">Recent Jobs</h3>
        </div>
        <p className="text-secondary-text text-center py-8">No jobs found</p>
      </div>
    )
  }

  return (
    <div className={cn('card', className)}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-medium text-primary-text">Recent Jobs</h3>
      </div>
      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <th className="w-48">Job Title</th>
              <th className="w-32">Company</th>
              <th className="w-24">Source</th>
              <th className="w-20">Risk</th>
              <th className="w-24">Status</th>
              <th className="w-20">Contacts</th>
              <th className="w-24">Date</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((job, index) => (
              <tr
                key={job.id}
                className={cn("hover:bg-surface-secondary/50 transition-colors", `animate-slide-up`)}
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <td className="font-medium text-primary-text truncate max-w-[180px]">
                  <Link href={`/dashboard/jobs/${job.id}`} className="hover:text-accent transition-colors">
                    {job.title}
                  </Link>
                </td>
                <td className="text-secondary-text truncate max-w-[120px]">
                  {job.company_name || '—'}
                </td>
                <td>
                  <span className="badge bg-surface-secondary text-secondary-text border-border">
                    {job.source_name}
                  </span>
                </td>
                <td>
                  <span className={cn('badge', getRiskBadgeClass(job.risk_level))}>
                    {job.risk_level}
                  </span>
                </td>
                <td>
                  <span className={cn('badge', getStatusBadgeClass(job.status))}>
                    {getStatusLabel(job.status)}
                  </span>
                </td>
                <td>
                  <div className="flex items-center gap-1">
                    {job.has_email && <Mail className="w-3.5 h-3.5 text-green-400" />}
                    {job.has_phone && <Phone className="w-3.5 h-3.5 text-blue-400" />}
                  </div>
                </td>
                <td className="text-secondary-text text-sm font-mono">
                  {formatDate(job.posted_at || job.created_at)}
                </td>
                <td className="text-right">
                  <Link
                    href={`/dashboard/jobs/${job.id}`}
                    className="p-1.5 rounded-lg text-secondary-text hover:text-primary-text hover:bg-surface-secondary transition-colors"
                    title="View details"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-4 text-center">
        <Link href="/dashboard/jobs" className="btn-ghost text-sm">
          View All Jobs
          <ExternalLink className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  )
}