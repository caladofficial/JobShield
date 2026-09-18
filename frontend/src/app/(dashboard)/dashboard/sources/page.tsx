'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { cn, formatDate } from '@/lib/utils'
import { sourcesApi } from '@/lib/api'
import { SourceResponse, SourceConnectionResponse, SourceStatus } from '@/types/dashboard'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Input } from '@/components/ui/Input'
import { Modal } from '@/components/ui/Modal'
import {
  Database,
  Plug,
  PlugZap,
  WifiOff,
  AlertCircle,
  CheckCircle,
  XCircle,
  Clock,
  RefreshCw,
  Loader2,
  Settings,
  Trash2,
  ExternalLink,
  Plus,
} from 'lucide-react'

const STATUS_ICONS: Record<SourceStatus, React.ReactNode> = {
  connected: <CheckCircle className="w-5 h-5 text-green-400" />,
  disconnected: <XCircle className="w-5 h-5 text-gray-400" />,
  requires_authorization: <AlertCircle className="w-5 h-5 text-yellow-400" />,
  rate_limited: <WifiOff className="w-5 h-5 text-orange-400" />,
  error: <XCircle className="w-5 h-5 text-red-400" />,
  unavailable: <Clock className="w-5 h-5 text-gray-400" />,
}

const STATUS_LABELS: Record<SourceStatus, string> = {
  connected: 'Connected',
  disconnected: 'Disconnected',
  requires_authorization: 'Requires Authorization',
  rate_limited: 'Rate Limited',
  error: 'Error',
  unavailable: 'Unavailable',
}

const STATUS_BADGE: Record<SourceStatus, string> = {
  connected: 'bg-green-500/20 text-green-400 border-green-500/30',
  disconnected: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  requires_authorization: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  rate_limited: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  error: 'bg-red-500/20 text-red-400 border-red-500/30',
  unavailable: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
}

const SOURCE_ICONS: Record<string, React.ReactNode> = {
  greenhouse: <Database className="w-5 h-5" />,
  lever: <Database className="w-5 h-5" />,
  workday: <Building2 className="w-5 h-5" />,
  rss: <Rss className="w-5 h-5" />,
  manual: <Globe className="w-5 h-5" />,
  indeed: <Briefcase className="w-5 h-5" />,
  linkedin: <Linkedin className="w-5 h-5" />,
  naukri: <Briefcase className="w-5 h-5" />,
}

import { Building2, Globe, Rss, Briefcase, Linkedin } from 'lucide-react'

export default function SourcesPage() {
  const [sources, setSources] = useState<SourceResponse[]>([])
  const [connections, setConnections] = useState<SourceConnectionResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [selectedSource, setSelectedSource] = useState<SourceResponse | null>(null)
  const [connectionForm, setConnectionForm] = useState({
    source_id: '',
    config: {} as Record<string, any>,
    credentials: {} as Record<string, string>,
  })
  const [connecting, setConnecting] = useState(false)
  const [healthChecking, setHealthChecking] = useState<number | null>(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    try {
      const [sourcesRes, connectionsRes] = await Promise.all([
        sourcesApi.list(),
        sourcesApi.connections(),
      ])
      setSources(sourcesRes.data)
      setConnections(connectionsRes.data)
    } catch (error) {
      console.error('Failed to fetch sources:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleConnect = async () => {
    if (!connectionForm.source_id) return
    setConnecting(true)
    try {
      await sourcesApi.createConnection({
        source_id: parseInt(connectionForm.source_id),
        config: connectionForm.config,
        credentials: connectionForm.credentials,
      })
      setModalOpen(false)
      setConnectionForm({ source_id: '', config: {}, credentials: {} })
      fetchData()
    } catch (error) {
      console.error('Failed to connect source:', error)
    } finally {
      setConnecting(false)
    }
  }

  const handleSync = async (connectionId: number) => {
    try {
      await sourcesApi.sync(connectionId)
      fetchData()
    } catch (error) {
      console.error('Failed to sync:', error)
    }
  }

  const handleHealthCheck = async (connectionId: number) => {
    setHealthChecking(connectionId)
    try {
      await sourcesApi.health(connectionId)
      fetchData()
    } catch (error) {
      console.error('Health check failed:', error)
    } finally {
      setHealthChecking(null)
    }
  }

  const handleDelete = async (connectionId: number) => {
    if (!confirm('Are you sure you want to disconnect this source?')) return
    try {
      await sourcesApi.deleteConnection(connectionId)
      fetchData()
    } catch (error) {
      console.error('Failed to delete connection:', error)
    }
  }

  const openModal = (source: SourceResponse) => {
    setSelectedSource(source)
    setConnectionForm({ source_id: String(source.id), config: {}, credentials: {} })
    setModalOpen(true)
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-primary-text">Sources</h1>
          <p className="text-secondary-text mt-1">Manage job source connections and integrations</p>
        </div>
        <Button onClick={() => openModal(sources.find(s => s.name === 'manual')!)}>
          <Plus className="w-4 h-4 mr-2" />
          Add Manual Job
        </Button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <div className="h-10 w-24 bg-surface-secondary rounded animate-pulse mb-4" />
              <div className="h-6 w-32 bg-surface-secondary rounded animate-pulse mb-2" />
              <div className="h-4 w-20 bg-surface-secondary rounded animate-pulse" />
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sources.map((source) => {
            const connection = connections.find(c => c.source_id === source.id)
            const status = connection?.status || 'disconnected'
            const Icon = SOURCE_ICONS[source.name] || <Database className="w-5 h-5" />

            return (
              <motion.div
                key={source.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="card relative"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-surface flex items-center justify-center">
                      {Icon}
                    </div>
                    <div>
                      <h3 className="font-medium text-primary-text">{source.display_name}</h3>
                      <p className="text-xs text-secondary-text">{source.name}</p>
                    </div>
                  </div>
                  {source.requires_authorization && (
                    <Badge variant="outline" className="text-xs">
                      Auth Required
                    </Badge>
                  )}
                </div>

                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className={cn('badge px-2 py-1', STATUS_BADGE[status])}>
                      {STATUS_ICONS[status]}
                      {STATUS_LABELS[status]}
                    </span>
                    <div className="flex items-center gap-1">
                      {connection && (
                        <>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleSync(connection.id)}
                            disabled={status !== 'connected'}
                            className="h-8 px-2"
                          >
                            <RefreshCw className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleHealthCheck(connection.id)}
                            disabled={healthChecking === connection.id}
                            className="h-8 px-2"
                          >
                            {healthChecking === connection.id ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <PlugZap className="w-4 h-4" />
                            )}
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(connection.id)}
                            className="h-8 px-2 text-red-400 hover:bg-red-600/10"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </>
                      )}
                    </div>
                  </div>

                  {connection && (
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center gap-2 text-secondary-text">
                        <Clock className="w-3.5 h-3.5" />
                        <span>Last sync: {connection.last_sync_at ? formatDate(connection.last_sync_at) : 'Never'}</span>
                      </div>
                      <div className="flex items-center gap-2 text-secondary-text">
                        <Database className="w-3.5 h-3.5" />
                        <span>{connection.jobs_collected} jobs collected</span>
                      </div>
                      {connection.last_error && (
                        <div className="flex items-center gap-2 text-red-400">
                          <AlertCircle className="w-3.5 h-3.5" />
                          <span className="truncate max-w-[200px]">{connection.last_error}</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {!connection && (
                  <Button
                    className="w-full"
                    onClick={() => openModal(source)}
                    variant={source.requires_authorization ? 'secondary' : 'primary'}
                  >
                    {source.requires_authorization ? 'Configure Access' : 'Connect'}
                    <Plug className="w-4 h-4 ml-2" />
                  </Button>
                )}
              </motion.div>
            )
          })}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Connect Source" size="md">
        <div className="space-y-4">
          <p className="text-secondary-text">
            Configure connection for <strong className="text-primary-text">{selectedSource?.display_name}</strong>
          </p>

          <div>
            <label className="block text-sm font-medium text-secondary-text mb-1">Source</label>
            <select
              value={connectionForm.source_id}
              onChange={(e) => setConnectionForm(prev => ({ ...prev, source_id: e.target.value }))}
              className="w-full px-4 py-2.5 rounded-xl bg-surface-secondary border border-border text-primary-text focus:outline-none focus:ring-2 focus:ring-accent"
              disabled
            >
              {sources.map(s => (
                <option key={s.id} value={String(s.id)}>{s.display_name}</option>
              ))}
            </select>
          </div>

          {selectedSource?.name === 'manual' && (
            <div>
              <label className="block text-sm font-medium text-secondary-text mb-1">Job URL</label>
              <Input
                placeholder="https://example.com/job/123"
                value={connectionForm.config.job_url || ''}
                onChange={(e) => setConnectionForm(prev => ({ ...prev, config: { ...prev.config, job_url: e.target.value } }))}
              />
            </div>
          )}

          {selectedSource?.name === 'greenhouse' && (
            <div>
              <label className="block text-sm font-medium text-secondary-text mb-1">Board Token</label>
              <Input
                placeholder="your-board-token"
                type="password"
                value={connectionForm.credentials.board_token || ''}
                onChange={(e) => setConnectionForm(prev => ({ ...prev, credentials: { ...prev.credentials, board_token: e.target.value } }))}
              />
            </div>
          )}

          {selectedSource?.name === 'lever' && (
            <div>
              <label className="block text-sm font-medium text-secondary-text mb-1">Company Name</label>
              <Input
                placeholder="company-name"
                value={connectionForm.credentials.company || ''}
                onChange={(e) => setConnectionForm(prev => ({ ...prev, credentials: { ...prev.credentials, company: e.target.value } }))}
              />
            </div>
          )}

          {selectedSource?.name === 'rss' && (
            <div>
              <label className="block text-sm font-medium text-secondary-text mb-1">Feed URL</label>
              <Input
                placeholder="https://example.com/jobs.rss"
                value={connectionForm.config.feed_url || ''}
                onChange={(e) => setConnectionForm(prev => ({ ...prev, config: { ...prev.config, feed_url: e.target.value } }))}
              />
            </div>
          )}

          <div className="flex gap-2 pt-2">
            <Button variant="secondary" onClick={() => setModalOpen(false)} className="flex-1" disabled={connecting}>
              Cancel
            </Button>
            <Button onClick={handleConnect} className="flex-1" disabled={connecting}>
              {connecting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  Connecting...
                </>
              ) : (
                'Connect'
              )}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

