'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { cn, formatDate } from '@/lib/utils'
import { contactsApi } from '@/lib/api'
import { ContactType, PaginatedResponse } from '@/types/dashboard'
import { DataTable } from '@/components/ui/DataTable'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import {
  Mail,
  Phone,
  Globe,
  User,
  Building2,
  Search,
  Filter,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  XCircle,
  HelpCircle,
} from 'lucide-react'

const TYPE_OPTIONS = [
  { value: '', label: 'All Types' },
  { value: 'email', label: 'Email' },
  { value: 'phone', label: 'Phone' },
  { value: 'website', label: 'Website' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'application_url', label: 'Application URL' },
]

const VALIDITY_OPTIONS = [
  { value: '', label: 'All' },
  { value: 'true', label: 'Valid Only' },
  { value: 'false', label: 'Invalid Only' },
]

const CORPORATE_OPTIONS = [
  { value: '', label: 'All' },
  { value: 'true', label: 'Corporate Only' },
  { value: 'false', label: 'Free Mail Only' },
]

export default function ContactsPage() {
  const [contacts, setContacts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(50)
  const [stats, setStats] = useState({
    total_contacts: 0,
    corporate_emails: 0,
    free_mail_addresses: 0,
    valid_phones: 0,
    invalid_contacts: 0,
    unverified_contacts: 0,
  })
  const [filters, setFilters] = useState({
    contact_type: '',
    is_valid: '',
    is_corporate: '',
    search: '',
  })
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    fetchContacts()
    fetchStats()
  }, [page, pageSize, filters])

  const fetchContacts = async () => {
    setLoading(true)
    try {
      const params = { page, page_size: pageSize, ...filters }
      const response = await contactsApi.list(params)
      const data: PaginatedResponse<any> = response.data
      setContacts(data.items)
      setTotal(data.total)
    } catch (error) {
      console.error('Failed to fetch contacts:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await contactsApi.stats()
      setStats(response.data)
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    }
  }

  const columns = [
    {
      header: 'Job',
      accessor: 'job',
      cell: (item: any) => (
        <div>
          <a href={`/dashboard/jobs/${item.job.id}`} className="font-medium text-primary-text hover:text-accent">
            {item.job.title}
          </a>
          <p className="text-xs text-secondary-text">{item.job.company}</p>
        </div>
      ),
    },
    {
      header: 'Contact',
      accessor: 'contact',
      cell: (item: any) => {
        const contact = item.contact
        const icons: Record<string, React.ReactNode> = {
          email: <Mail className="w-4 h-4 text-green-400" />,
          phone: <Phone className="w-4 h-4 text-blue-400" />,
          website: <Globe className="w-4 h-4 text-purple-400" />,
          linkedin: <User className="w-4 h-4 text-blue-600" />,
          application_url: <Globe className="w-4 h-4 text-orange-400" />,
        }
        return (
          <div className="flex items-center gap-2">
            {icons[contact.type]}
            <div>
              <p className="font-mono text-sm text-primary-text">{contact.normalized_value}</p>
              <p className="text-xs text-secondary-text capitalize">{contact.type.replace('_', ' ')}</p>
            </div>
          </div>
        )
      ),
    },
    {
      header: 'Type',
      accessor: 'contact.type',
      cell: (item: any) => (
        <Badge variant="outline" className="text-xs">
          {item.contact.type.replace('_', ' ')}
        </Badge>
      ),
    },
    {
      header: 'Validity',
      accessor: 'contact.is_valid',
      cell: (item: any) => (
        <Badge variant={item.contact.is_valid ? 'success' : 'danger'} className="text-xs">
          {item.contact.is_valid ? 'Valid' : 'Invalid'}
        </Badge>
      ),
    },
    {
      header: 'Email Type',
      accessor: 'contact.is_corporate',
      cell: (item: any) => {
        if (item.contact.type !== 'email') return <span className="text-secondary-text">—</span>
        return (
          <Badge variant={item.contact.is_corporate ? 'success' : 'outline'} className="text-xs">
            {item.contact.is_corporate ? 'Corporate' : 'Free Mail'}
          </Badge>
        )
      },
    },
    {
      header: 'Domain',
      accessor: 'contact.domain',
      cell: (item: any) => <span className="text-secondary-text text-sm font-mono">{item.contact.domain || '—'}</span>,
    },
    {
      header: 'Confidence',
      accessor: 'contact.confidence',
      cell: (item: any) => (
        <span className="font-mono text-sm">
          {Math.round(item.contact.confidence * 100)}%
        </span>
      ),
    },
    {
      header: 'Source',
      accessor: 'source',
      cell: (item: any) => <Badge variant="outline" className="text-xs">{item.source}</Badge>,
    },
    {
      header: 'Date',
      accessor: 'created_at',
      cell: (item: any) => <span className="text-secondary-text text-sm font-mono">{formatDate(item.created_at)}</span>,
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-primary-text">Contacts</h1>
          <p className="text-secondary-text mt-1">Extracted contact information from job postings</p>
        </div>
        <Button variant="secondary" onClick={fetchContacts} disabled={loading}>
          <RefreshCw className={cn('w-4 h-4', loading && 'animate-spin')} />
          Refresh
        </Button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4 mb-6">
        <StatCard label="Total Contacts" value={stats.total_contacts} icon={<Mail />} color="text-blue-400" bg="bg-blue-500/10" />
        <StatCard label="Corporate Emails" value={stats.corporate_emails} icon={<Building2 />} color="text-green-400" bg="bg-green-500/10" />
        <StatCard label="Free Mail" value={stats.free_mail_addresses} icon={<Mail />} color="text-yellow-400" bg="bg-yellow-500/10" />
        <StatCard label="Valid Phones" value={stats.valid_phones} icon={<Phone />} color="text-orange-400" bg="bg-orange-500/10" />
        <StatCard label="Invalid" value={stats.invalid_contacts} icon={<XCircle />} color="text-red-400" bg="bg-red-500/10" />
        <StatCard label="Unverified" value={stats.unverified_contacts} icon={<HelpCircle />} color="text-gray-400" bg="bg-gray-500/10" />
      </div>

      <div className="card p-4">
        <div className="flex flex-col sm:flex-row gap-3 mb-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-secondary-text" />
            <input
              type="text"
              placeholder="Search contacts..."
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
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
            className="mt-4 pt-4 border-t border-border grid grid-cols-1 sm:grid-cols-4 gap-3"
          >
            <select
              value={filters.contact_type}
              onChange={(e) => setFilters(prev => ({ ...prev, contact_type: e.target.value }))}
              className="px-4 py-2.5 rounded-xl bg-surface-secondary border border-border text-primary-text focus:outline-none focus:ring-2 focus:ring-accent"
            >
              {TYPE_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
            </select>
            <select
              value={filters.is_valid}
              onChange={(e) => setFilters(prev => ({ ...prev, is_valid: e.target.value }))}
              className="px-4 py-2.5 rounded-xl bg-surface-secondary border border-border text-primary-text focus:outline-none focus:ring-2 focus:ring-accent"
            >
              {VALIDITY_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
            </select>
            <select
              value={filters.is_corporate}
              onChange={(e) => setFilters(prev => ({ ...prev, is_corporate: e.target.value }))}
              className="px-4 py-2.5 rounded-xl bg-surface-secondary border border-border text-primary-text focus:outline-none focus:ring-2 focus:ring-accent"
            >
              {CORPORATE_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
            </select>
          </motion.div>
        )}
      </div>

      <DataTable
        columns={columns}
        data={contacts}
        loading={loading}
        emptyMessage="No contacts found"
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

function StatCard({ label, value, icon: Icon, color, bg }: any) {
  return (
    <Card>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-secondary-text">{label}</p>
          <p className="text-2xl font-bold text-primary-text font-mono mt-1">{value.toLocaleString()}</p>
        </div>
        <div className={cn('w-10 h-10 rounded-xl flex items-center justify-center', bg, color)}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </Card>
  )
}



