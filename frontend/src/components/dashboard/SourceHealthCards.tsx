'use client'

import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'
import {
  Database,
  CheckCircle,
  AlertCircle,
  XCircle,
  Clock,
  WifiOff,
  RefreshCw,
} from 'lucide-react'

interface SourceHealthItem {
  source: string
  status: string
  last_sync: string | null
  jobs_collected: number
  last_error: string | null
}

interface SourceHealthCardsProps {
  sources: SourceHealthItem[]
  className?: string
}

const STATUS_ICONS: Record<string, React.ReactNode> = {
  connected: <CheckCircle className="w-5 h-5 text-green-400" />,
  disconnected: <XCircle className="w-5 h-5 text-gray-400" />,
  requires_authorization: <AlertCircle className="w-5 h-5 text-yellow-400" />,
  rate_limited: <WifiOff className="w-5 h-5 text-orange-400" />,
  error: <XCircle className="w-5 h-5 text-red-400" />,
  unavailable: <Clock className="w-5 h-5 text-gray-400" />,
}

const STATUS_LABELS: Record<string, string> = {
  connected: 'Connected',
  disconnected: 'Disconnected',
  requires_authorization: 'Requires Authorization',
  rate_limited: 'Rate Limited',
  error: 'Error',
  unavailable: 'Unavailable',
}

const STATUS_BADGE: Record<string, string> = {
  connected: 'bg-green-500/20 text-green-400 border-green-500/30',
  disconnected: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  requires_authorization: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  rate_limited: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  error: 'bg-red-500/20 text-red-400 border-red-500/30',
  unavailable: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
}

export function SourceHealthCards({ sources, className }: SourceHealthCardsProps) {
  return (
    <div className={cn('card', className)}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-medium text-primary-text">Source Health</h3>
        <Database className="w-4 h-4 text-secondary-text" />
      </div>

      {!sources.length ? (
        <p className="text-secondary-text text-center py-8">No sources connected</p>
      ) : (
        <div className="space-y-3">
          {sources.map((source, index) => (
            <motion.div
              key={source.source}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="flex items-center justify-between p-3 rounded-xl bg-surface-secondary/50 border border-border/50 hover:border-border transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-surface flex items-center justify-center">
                  {STATUS_ICONS[source.status] || <Database className="w-5 h-5 text-secondary-text" />}
                </div>
                <div>
                  <p className="font-medium text-primary-text">{source.source}</p>
                  <p className="text-xs text-secondary-text">
                    {source.jobs_collected} jobs collected
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <span className={cn('badge px-2 py-1', STATUS_BADGE[source.status] || STATUS_BADGE.unavailable)}>
                  {STATUS_LABELS[source.status] || source.status}
                </span>

                {source.last_sync && (
                  <span className="flex items-center gap-1 text-xs text-secondary-text">
                    <Clock className="w-3 h-3" />
                    {new Date(source.last_sync).toLocaleDateString()}
                  </span>
                )}

                {source.last_error && (
                  <span className="text-xs text-red-400 truncate max-w-[150px]" title={source.last_error}>
                    {source.last_error}
                  </span>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      )}

      <div className="mt-4 pt-4 border-t border-border">
        <p className="text-xs text-secondary-text text-center">
          Click on a source in the Sources page to manage connections and sync jobs.
        </p>
      </div>
    </div>
  )
}

