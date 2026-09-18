'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { cn, formatDate } from '@/lib/utils'
import { outreachApi } from '@/lib/api'
import { EmailCampaignResponse, EmailRecipientResponse, PaginatedResponse } from '@/types/outreach'
import { DataTable } from '@/components/ui/DataTable'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/card'
import { Modal } from '@/components/ui/Modal'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { Select } from '@/components/ui/Select'
import {
  Plus,
  Send,
  Eye,
  RefreshCw,
  Loader2,
  X,
  CheckCircle,
  AlertCircle,
  Mail,
  Edit,
  Trash2,
  ChevronDown,
  ChevronUp,
} from 'lucide-react'

const STATUS_BADGES: Record<string, { variant: string; icon: React.ReactNode }> = {
  draft: { variant: 'outline', icon: <Edit className="w-3.5 h-3.5" /> },
  scheduled: { variant: 'info', icon: <Clock className="w-3.5 h-3.5" /> },
  sending: { variant: 'info', icon: <Loader2 className="w-3.5 h-3.5 animate-spin" /> },
  sent: { variant: 'success', icon: <CheckCircle className="w-3.5 h-3.5" /> },
  completed: { variant: 'success', icon: <CheckCircle className="w-3.5 h-3.5" /> },
  completed_with_errors: { variant: 'warning', icon: <AlertCircle className="w-3.5 h-3.5" /> },
  failed: { variant: 'danger', icon: <X className="w-3.5 h-3.5" /> },
  cancelled: { variant: 'outline', icon: <X className="w-3.5 h-3.5" /> },
  paused: { variant: 'warning', icon: <Pause className="w-3.5 h-3.5" /> },
}

import { Clock, Pause } from 'lucide-react'

const PROVIDERS = [
  { value: 'gmail', label: 'Gmail API' },
  { value: 'microsoft_graph', label: 'Microsoft Graph' },
  { value: 'smtp', label: 'SMTP' },
]

export default function OutreachPage() {
  const [campaigns, setCampaigns] = useState<EmailCampaignResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingCampaign, setEditingCampaign] = useState<EmailCampaignResponse | null>(null)
  const [viewingCampaign, setViewingCampaign] = useState<EmailCampaignResponse | null>(null)
  const [recipients, setRecipients] = useState<EmailRecipientResponse[]>([])
  const [recipientsLoading, setRecipientsLoading] = useState(false)
  const [recipientsPage, setRecipientsPage] = useState(1)
  const [recipientsTotal, setRecipientsTotal] = useState(0)
  const [formData, setFormData] = useState({
    name: '',
    subject_template: '',
    body_html_template: '',
    body_text_template: '',
    from_email: '',
    from_name: '',
    provider: 'gmail',
    recipient_contact_ids: [] as number[],
  })
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    fetchCampaigns()
  }, [page, pageSize])

  const fetchCampaigns = async () => {
    setLoading(true)
    try {
      const response = await outreachApi.campaigns.list({ page, page_size: pageSize })
      const data: PaginatedResponse<EmailCampaignResponse> = response.data
      setCampaigns(data.items)
      setTotal(data.total)
    } catch (error) {
      console.error('Failed to fetch campaigns:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchRecipients = async (campaignId: number, pageNum = 1) => {
    setRecipientsLoading(true)
    try {
      const response = await outreachApi.recipients.list(campaignId, { page: pageNum, page_size: 50 })
      const data: PaginatedResponse<EmailRecipientResponse> = response.data
      setRecipients(data.items)
      setRecipientsTotal(data.total)
    } catch (error) {
      console.error('Failed to fetch recipients:', error)
    } finally {
      setRecipientsLoading(false)
    }
  }

  const handleSubmit = async () => {
    setSubmitting(true)
    try {
      if (editingCampaign) {
        await outreachApi.campaigns.update(editingCampaign.id, formData)
      } else {
        await outreachApi.campaigns.create(formData)
      }
      setModalOpen(false)
      setEditingCampaign(null)
      resetForm()
      fetchCampaigns()
    } catch (error) {
      console.error('Failed to save campaign:', error)
    } finally {
      setSubmitting(false)
    }
  }

  const handleSend = async (campaignId: number) => {
    if (!confirm('Send this campaign to all recipients?')) return
    try {
      await outreachApi.campaigns.send(campaignId)
      fetchCampaigns()
    } catch (error) {
      console.error('Failed to send campaign:', error)
    }
  }

  const handleTestSend = async (campaignId: number) => {
    const email = prompt('Enter test email address:')
    if (!email) return
    try {
      await outreachApi.campaigns.sendTest(campaignId, email)
      alert('Test email sent!')
    } catch (error) {
      console.error('Failed to send test email:', error)
    }
  }

  const handlePreview = async (campaignId: number, contactId: number) => {
    try {
      const response = await outreachApi.campaigns.preview(campaignId, contactId)
      alert(`Subject: ${response.data.subject}\n\n${response.data.body_text}`)
    } catch (error) {
      console.error('Failed to preview:', error)
    }
  }

  const handleCancel = async (campaignId: number) => {
    if (!confirm('Cancel this campaign?')) return
    try {
      await outreachApi.campaigns.cancel(campaignId)
      fetchCampaigns()
    } catch (error) {
      console.error('Failed to cancel campaign:', error)
    }
  }

  const handleDelete = async (campaignId: number) => {
    if (!confirm('Delete this campaign permanently?')) return
    try {
      await outreachApi.campaigns.delete(campaignId)
      fetchCampaigns()
    } catch (error) {
      console.error('Failed to delete campaign:', error)
    }
  }

  const openCreateModal = () => {
    setEditingCampaign(null)
    resetForm()
    setModalOpen(true)
  }

  const openEditModal = (campaign: EmailCampaignResponse) => {
    setEditingCampaign(campaign)
    setFormData({
      name: campaign.name,
      subject_template: campaign.subject_template,
      body_html_template: campaign.body_html_template,
      body_text_template: campaign.body_text_template,
      from_email: campaign.from_email,
      from_name: campaign.from_name || '',
      provider: campaign.provider,
      recipient_contact_ids: [],
    })
    setModalOpen(true)
  }

  const openViewModal = (campaign: EmailCampaignResponse) => {
    setViewingCampaign(campaign)
    fetchRecipients(campaign.id)
  }

  const resetForm = () => {
    setFormData({
      name: '',
      subject_template: '',
      body_html_template: '',
      body_text_template: '',
      from_email: '',
      from_name: '',
      provider: 'gmail',
      recipient_contact_ids: [],
    })
  }

  const campaignColumns = [
    {
      header: 'Name',
      accessor: 'name',
      cell: (c: EmailCampaignResponse) => <span className="font-medium text-primary-text">{c.name}</span>,
    },
    {
      header: 'Subject',
      accessor: 'subject_template',
      cell: (c: EmailCampaignResponse) => <span className="text-secondary-text truncate max-w-[200px] block">{c.subject_template}</span>,
    },
    {
      header: 'Provider',
      accessor: 'provider',
      cell: (c: EmailCampaignResponse) => <Badge variant="outline" className="text-xs">{c.provider}</Badge>,
    },
    {
      header: 'Status',
      accessor: 'status',
      cell: (c: EmailCampaignResponse) => {
        const { variant, icon } = STATUS_BADGES[c.status] || { variant: 'outline', icon: null }
        return (
          <Badge variant={variant as any} className="text-xs flex items-center gap-1">
            {icon}
            {c.status}
          </Badge>
        )
      },
    },
    {
      header: 'Recipients',
      accessor: 'total_recipients',
      cell: (c: EmailCampaignResponse) => (
        <div className="flex items-center gap-2">
          <span className="font-mono">{c.sent_count} / {c.total_recipients}</span>
          {c.failed_count > 0 && <Badge variant="danger" className="text-xs">{c.failed_count} failed</Badge>}
        </div>
      ),
    },
    {
      header: 'Created',
      accessor: 'created_at',
      cell: (c: EmailCampaignResponse) => <span className="text-secondary-text text-sm font-mono">{formatDate(c.created_at)}</span>,
    },
    {
      header: 'Actions',
      accessor: 'actions',
      cell: (c: EmailCampaignResponse) => (
        <div className="flex items-center gap-1 justify-end">
          <Button variant="ghost" size="sm" onClick={() => handlePreview(c.id, 0)} title="Preview">
            <Eye className="w-3.5 h-3.5" />
          </Button>
          <Button variant="ghost" size="sm" onClick={() => handleTestSend(c.id)} title="Send Test">
            <Mail className="w-3.5 h-3.5" />
          </Button>
          {['draft', 'scheduled', 'paused'].includes(c.status) && (
            <Button variant="ghost" size="sm" onClick={() => handleSend(c.id)} title="Send">
              <Send className="w-3.5 h-3.5" />
            </Button>
          )}
          {['sending', 'pending'].includes(c.status) && (
            <Button variant="ghost" size="sm" onClick={() => handleCancel(c.id)} title="Cancel" className="text-red-400 hover:bg-red-600/10">
              <X className="w-3.5 h-3.5" />
            </Button>
          )}
          <Button variant="ghost" size="sm" onClick={() => openEditModal(c)} title="Edit">
            <Edit className="w-3.5 h-3.5" />
          </Button>
          <Button variant="ghost" size="sm" onClick={() => openViewModal(c)} title="View Recipients">
            <Users className="w-3.5 h-3.5" />
          </Button>
          <Button variant="ghost" size="sm" onClick={() => handleDelete(c.id)} title="Delete" className="text-red-400 hover:bg-red-600/10">
            <Trash2 className="w-3.5 h-3.5" />
          </Button>
        </div>
      ),
    },
  ]

  const recipientColumns = [
    {
      header: 'Email',
      accessor: 'email',
      cell: (r: EmailRecipientResponse) => <span className="font-mono text-sm text-primary-text">{r.email}</span>,
    },
    {
      header: 'Name',
      accessor: 'name',
      cell: (r: EmailRecipientResponse) => <span className="text-secondary-text">{r.name || '—'}</span>,
    },
    {
      header: 'Job',
      accessor: 'job_id',
      cell: (r: EmailRecipientResponse) => <span className="text-secondary-text text-sm">Job #{r.job_id}</span>,
    },
    {
      header: 'Status',
      accessor: 'status',
      cell: (r: EmailRecipientResponse) => {
        const { variant, icon } = STATUS_BADGES[r.status] || { variant: 'outline', icon: null }
        return (
          <Badge variant={variant as any} className="text-xs flex items-center gap-1">
            {icon}
            {r.status}
          </Badge>
        )
      },
    },
    {
      header: 'Sent',
      accessor: 'sent_at',
      cell: (r: EmailRecipientResponse) => <span className="text-secondary-text text-sm font-mono">{r.sent_at ? formatDate(r.sent_at) : '—'}</span>,
    },
    {
      header: 'Error',
      accessor: 'error_message',
      cell: (r: EmailRecipientResponse) => r.error_message ? (
        <span className="text-red-400 text-sm truncate max-w-[200px] block" title={r.error_message}>{r.error_message}</span>
      ) : (
        <span className="text-secondary-text">—</span>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-primary-text">Outreach</h1>
          <p className="text-secondary-text mt-1">Manage email campaigns to job contacts</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" onClick={fetchCampaigns} disabled={loading}>
            <RefreshCw className={cn('w-4 h-4', loading && 'animate-spin')} />
            Refresh
          </Button>
          <Button onClick={openCreateModal}>
            <Plus className="w-4 h-4 mr-2" />
            New Campaign
          </Button>
        </div>
      </div>

      <DataTable
        columns={campaignColumns}
        data={campaigns}
        loading={loading}
        emptyMessage="No campaigns created yet"
        pagination={{
          page,
          pageSize,
          total,
          onPageChange: setPage,
          onPageSizeChange: setPageSize,
        }}
      />

      <Modal open={modalOpen} onClose={() => { setModalOpen(false); setEditingCampaign(null); resetForm(); }} title={editingCampaign ? 'Edit Campaign' : 'New Campaign'} size="lg">
        <div className="space-y-4 max-h-[70vh] overflow-y-auto">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-secondary-text mb-1">Campaign Name</label>
              <Input value={formData.name} onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))} placeholder="My Campaign" />
            </div>
            <div>
              <label className="block text-sm font-medium text-secondary-text mb-1">Provider</label>
              <Select value={formData.provider} onValueChange={(v) => setFormData(prev => ({ ...prev, provider: v }))} options={PROVIDERS} />
            </div>
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-secondary-text mb-1">From Email</label>
              <Input value={formData.from_email} onChange={(e) => setFormData(prev => ({ ...prev, from_email: e.target.value }))} placeholder="you@company.com" />
            </div>
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-secondary-text mb-1">From Name (Optional)</label>
              <Input value={formData.from_name} onChange={(e) => setFormData(prev => ({ ...prev, from_name: e.target.value }))} placeholder="Your Name" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-text mb-1">Subject Template</label>
            <Input
              value={formData.subject_template}
              onChange={(e) => setFormData(prev => ({ ...prev, subject_template: e.target.value }))}
              placeholder="Application for {{job_title}} — {{candidate_name}}"
            />
            <p className="text-xs text-secondary-text mt-1">
              Variables: {{candidate_name}}, {{company_name}}, {{job_title}}, {{recruiter_name}}, {{job_location}}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-text mb-1">HTML Body Template</label>
            <Textarea
              value={formData.body_html_template}
              onChange={(e) => setFormData(prev => ({ ...prev, body_html_template: e.target.value }))}
              rows={6}
              placeholder="<p>Dear {{recruiter_name}},</p><p>I'm applying for {{job_title}} at {{company_name}}...</p>"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-text mb-1">Text Body Template</label>
            <Textarea
              value={formData.body_text_template}
              onChange={(e) => setFormData(prev => ({ ...prev, body_text_template: e.target.value }))}
              rows={6}
              placeholder="Dear {{recruiter_name}},\n\nI'm applying for {{job_title}} at {{company_name}}..."
            />
          </div>

          <div className="flex gap-2 pt-2">
            <Button variant="secondary" onClick={() => { setModalOpen(false); setEditingCampaign(null); resetForm(); }} className="flex-1" disabled={submitting}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} className="flex-1" disabled={submitting}>
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  Saving...
                </>
              ) : (
                editingCampaign ? 'Update Campaign' : 'Create Campaign'
              )}
            </Button>
          </div>
        </div>
      </Modal>

      <AnimatePresence>
        {viewingCampaign && (
          <Modal open onClose={() => setViewingCampaign(null)} title={`Recipients: ${viewingCampaign.name}`} size="xl">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-medium text-primary-text">Recipients ({recipientsTotal})</h3>
                <div className="flex items-center gap-2">
                  <Button variant="secondary" size="sm" onClick={() => handleSend(viewingCampaign!.id)} disabled={viewingCampaign?.status !== 'draft' && viewingCampaign?.status !== 'scheduled' && viewingCampaign?.status !== 'paused'}>
                    <Send className="w-3.5 h-3.5 mr-1" />
                    Send Campaign
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => handleTestSend(viewingCampaign!.id)}>
                    <Mail className="w-3.5 h-3.5 mr-1" />
                    Test
                  </Button>
                </div>
              </div>
              <DataTable
                columns={recipientColumns}
                data={recipients}
                loading={recipientsLoading}
                emptyMessage="No recipients in this campaign"
                pagination={{
                  page: recipientsPage,
                  pageSize: 50,
                  total: recipientsTotal,
                  onPageChange: setRecipientsPage,
                  onPageSizeChange: () => {},
                }}
              />
            </div>
          </Modal>
        )}
      </AnimatePresence>
    </div>
  )
}

import { Users } from 'lucide-react'