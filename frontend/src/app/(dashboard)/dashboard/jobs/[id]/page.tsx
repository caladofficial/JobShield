'use client'

import { useEffect, useState } from 'react'
import { cn, formatDate, formatCurrency, getRiskBadgeClass, getStatusBadgeClass, getStatusLabel } from '@/lib/utils'
import { jobsApi, verificationApi } from '@/lib/api'
import { JobResponse, JobVerificationResponse, RiskEventResponse, ContactInfo } from '@/types/job'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs'
import FadeIn from '@/components/ui/FadeIn'
import SlideUp from '@/components/ui/SlideUp'
import {
  ExternalLink,
  ShieldCheck,
  AlertTriangle,
  Building2,
  User,
  Mail,
  Phone,
  Globe,
  Link as LinkIcon,
  Calendar,
  DollarSign,
  Briefcase,
  MapPin,
  Clock,
  Check,
  X,
  HelpCircle,
  Activity,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  Download,
} from 'lucide-react'

const VERIFICATION_STAGES = [
  { key: 'source', label: 'Source', icon: ShieldCheck },
  { key: 'employer', label: 'Employer', icon: Building2 },
  { key: 'uploader', label: 'Uploader', icon: User },
  { key: 'content', label: 'Content', icon: Briefcase },
  { key: 'contact', label: 'Contacts', icon: Mail },
  { key: 'risk', label: 'Risk Analysis', icon: Activity },
]

export default function JobDetailPage({ params }: { params: { id: string } }) {
  const [job, setJob] = useState<JobResponse | null>(null)
  const [verification, setVerification] = useState<JobVerificationResponse | null>(null)
  const [riskEvents, setRiskEvents] = useState<RiskEventResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({})

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const [jobRes, verRes, riskRes] = await Promise.all([
          jobsApi.get(parseInt(params.id)),
          verificationApi.get(parseInt(params.id)).catch(() => null),
          verificationApi.riskEvents(parseInt(params.id)).catch(() => []),
        ])
        setJob(jobRes.data)
        setVerification(verRes?.data || null)
        setRiskEvents(riskRes?.data || [])
      } catch (error) {
        console.error('Failed to fetch job details:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [params.id])

  const toggleSection = (key: string) => {
    setExpandedSections(prev => ({ ...prev, [key]: !prev[key] }))
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <JobDetailSkeleton />
      </div>
    )
  }

  if (!job) {
    return (
      <Card className="text-center py-12">
        <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-primary-text mb-2">Job not found</h3>
        <Button variant="secondary" onClick={() => window.history.back()}>
          Back to Jobs
        </Button>
      </Card>
    )
  }

  const getVerificationIcon = (score: number) => {
    if (score >= 70) return <Check className="w-5 h-5 text-green-400" />
    if (score >= 40) return <HelpCircle className="w-5 h-5 text-yellow-400" />
    return <X className="w-5 h-5 text-red-400" />
  }

  return (
    <FadeIn duration={300}>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Badge variant={getStatusBadgeClass(job.status).replace('badge-', '') as any}>
              {getStatusLabel(job.status)}
            </Badge>
            <Badge variant={getRiskBadgeClass(job.risk_level).replace('badge-', '') as any}>
              {job.risk_level} Risk
            </Badge>
          </div>
          <h1 className="text-2xl font-bold text-primary-text">{job.title}</h1>
          <p className="text-secondary-text mt-1">{job.company_name || 'Unknown Company'}</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" onClick={() => window.open(job.source_url, '_blank')}>
            <ExternalLink className="w-4 h-4 mr-2" />
            Original Post
          </Button>
          <Button variant="secondary">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <Animated initial="slideUp" delay={100} className="lg:col-span-2 space-y-6">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
            <TabsList className="bg-surface-secondary rounded-xl p-1">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="verification">Verification</TabsTrigger>
              <TabsTrigger value="risk">Risk Analysis</TabsTrigger>
              <TabsTrigger value="source">Source Data</TabsTrigger>
            </TabsList>

            <TabsContent value="overview">
              <div className="space-y-6">
                <Card variant="elevated">
                  <h3 className="font-medium text-primary-text mb-4">Job Details</h3>
                  <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <dt className="text-sm text-secondary-text">Company</dt>
                      <dd className="text-primary-text font-medium mt-1">{job.company_name || '—'}</dd>
                    </div>
                    <div>
                      <dt className="text-sm text-secondary-text">Location</dt>
                      <dd className="text-primary-text font-medium mt-1 flex items-center gap-2">
                        <MapPin className="w-4 h-4 text-secondary-text" />
                        {job.location || '—'}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-secondary-text">Employment Type</dt>
                      <dd className="text-primary-text font-medium mt-1 flex items-center gap-2">
                        <Briefcase className="w-4 h-4 text-secondary-text" />
                        {job.employment_type || '—'}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-secondary-text">Salary Range</dt>
                      <dd className="text-primary-text font-medium mt-1 flex items-center gap-2">
                        <DollarSign className="w-4 h-4 text-secondary-text" />
                        {job.salary_min || job.salary_max
                          ? `${formatCurrency(job.salary_min)} - ${formatCurrency(job.salary_max)} ${job.currency}`
                          : 'Not specified'}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-secondary-text">Posted Date</dt>
                      <dd className="text-primary-text font-medium mt-1 flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-secondary-text" />
                        {formatDate(job.posted_at)}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-secondary-text">Expires</dt>
                      <dd className="text-primary-text font-medium mt-1 flex items-center gap-2">
                        <Clock className="w-4 h-4 text-secondary-text" />
                        {formatDate(job.expires_at)}
                      </dd>
                    </div>
                    <div className="sm:col-span-2">
                      <dt className="text-sm text-secondary-text">Description</dt>
                      <dd className="text-primary-text mt-2 whitespace-pre-wrap text-sm leading-relaxed max-h-64 overflow-y-auto scrollbar-thin">
                        {job.description}
                      </dd>
                    </div>
                  </dl>
                </Card>

                <Card variant="elevated">
                  <h3 className="font-medium text-primary-text mb-4">Contacts</h3>
                  {job.contacts && job.contacts.length > 0 ? (
                    <div className="space-y-3">
                      {job.contacts.map((contact: ContactInfo, index) => (
                        <Animated key={index} initial="slideUp" delay={index * 50}>
                          <div className="flex items-center justify-between p-3 rounded-xl bg-surface-secondary/50 border border-border/50">
                            <div className="flex items-center gap-3">
                              {contact.type === 'email' && <Mail className="w-5 h-5 text-green-400" />}
                              {contact.type === 'phone' && <Phone className="w-5 h-5 text-blue-400" />}
                              {contact.type === 'website' && <Globe className="w-5 h-5 text-purple-400" />}
                              {contact.type === 'application_url' && <LinkIcon className="w-5 h-5 text-orange-400" />}
                              <div>
                                <p className="font-medium text-primary-text">{contact.normalized_value}</p>
                                <p className="text-xs text-secondary-text capitalize">{contact.type.replace('_', ' ')}</p>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              {contact.is_valid ? (
                                <Check className="w-4 h-4 text-green-400" />
                              ) : (
                                <X className="w-4 h-4 text-red-400" />
                              )}
                              <Badge variant={contact.is_corporate ? 'success' : 'outline'} className="text-xs">
                                {contact.is_corporate ? 'Corporate' : 'Free Mail'}
                              </Badge>
                              <Badge variant="outline" className="text-xs">
                                {Math.round(contact.confidence * 100)}%
                              </Badge>
                            </div>
                          </div>
                        </Animated>
                      ))}
                    </div>
                  ) : (
                    <p className="text-secondary-text text-center py-8">No contacts extracted</p>
                  )}
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="verification">
              {verification && (
                <div className="space-y-6">
                  <Card variant="elevated">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-medium text-primary-text">Verification Pipeline</h3>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xl font-bold text-accent">
                          {verification.final_confidence.toFixed(1)}%
                        </span>
                        <span className="text-sm text-secondary-text">Confidence</span>
                      </div>
                    </div>
                    <div className="space-y-3">
                      {VERIFICATION_STAGES.map((stage, index) => {
                        const scoreKey = `${stage.key}_score` as keyof JobVerificationResponse
                        const score = verification[scoreKey] as number
                        const signals = verification[`${stage.key}_signals`] as Record<string, any>

                        return (
                          <Animated key={stage.key} initial="slideUp" delay={index * 50}>
                            <button
                              onClick={() => toggleSection(stage.key)}
                              className="w-full flex items-center justify-between p-3 rounded-xl bg-surface-secondary/50 border border-border/50 hover:border-border transition-colors"
                            >
                              <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-xl bg-surface flex items-center justify-center">
                                  <stage.icon className="w-5 h-5 text-secondary-text" />
                                </div>
                                <div>
                                  <p className="font-medium text-primary-text">{stage.label}</p>
                                  <p className="text-xs text-secondary-text">
                                    {Object.keys(signals).filter(k => signals[k]).length} / {Object.keys(signals).length} checks passed
                                  </p>
                                </div>
                              </div>
                              <div className="flex items-center gap-3">
                                <getVerificationIcon(score) />
                                <span className={cn('font-mono font-bold', score >= 70 ? 'text-green-400' : score >= 40 ? 'text-yellow-400' : 'text-red-400')}>
                                  {score.toFixed(0)}%
                                </span>
                                <ChevronDown className={cn('w-4 h-4 text-secondary-text transition-transform', expandedSections[stage.key] && 'rotate-180')} />
                              </div>
                            </button>
                            <Animated initial="slideDown" className="mt-2 ml-14 space-y-2" key={`${stage.key}-details`}>
                              {expandedSections[stage.key] && Object.entries(signals).map(([key, value]) => (
                                <div key={key} className="flex items-center justify-between text-sm">
                                  <span className="text-secondary-text">{key.replace(/_/g, ' ')}</span>
                                  <span className={value ? 'text-green-400' : 'text-red-400'}>
                                    {value ? '✓ Passed' : '✗ Failed'}
                                  </span>
                                </div>
                              ))}
                            </Animated>
                          </Animated>
                        )
                      })}
                    </div>
                  </Card>

                  {verification.ai_analysis && (
                    <Card variant="elevated">
                      <h3 className="font-medium text-primary-text mb-4">AI Analysis</h3>
                      <div className="space-y-3">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-xl bg-surface flex items-center justify-center">
                            <Activity className="w-5 h-5 text-accent" />
                          </div>
                          <div>
                            <p className="font-medium text-primary-text">Job Quality</p>
                            <p className="text-xs text-secondary-text">AI assessment of job posting quality</p>
                          </div>
                          <div className="ml-auto font-mono text-xl font-bold text-green-400">
                            {(verification.ai_analysis.job_quality * 100).toFixed(0)}%
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-xl bg-surface flex items-center justify-center">
                            <AlertTriangle className="w-5 h-5 text-red-400" />
                          </div>
                          <div>
                            <p className="font-medium text-primary-text">Scam Risk</p>
                            <p className="text-xs text-secondary-text">AI assessment of fraudulent indicators</p>
                          </div>
                          <div className="ml-auto font-mono text-xl font-bold text-red-400">
                            {(verification.ai_analysis.scam_risk * 100).toFixed(0)}%
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-xl bg-surface flex items-center justify-center">
                            <ShieldCheck className="w-5 h-5 text-blue-400" />
                          </div>
                          <div>
                            <p className="font-medium text-primary-text">Contact Consistency</p>
                            <p className="text-xs text-secondary-text">AI assessment of contact information validity</p>
                          </div>
                          <div className="ml-auto font-mono text-xl font-bold text-blue-400">
                            {(verification.ai_analysis.contact_consistency * 100).toFixed(0)}%
                          </div>
                        </div>
                      </div>
                      {verification.ai_analysis.summary && (
                        <p className="mt-4 text-sm text-secondary-text">{verification.ai_analysis.summary}</p>
                      )}
                      {verification.ai_analysis.reasons && verification.ai_analysis.reasons.length > 0 && (
                        <ul className="mt-4 space-y-1">
                          {verification.ai_analysis.reasons.map((reason: string, i: number) => (
                            <li key={i} className="text-sm text-secondary-text flex items-center gap-2">
                              <Check className="w-4 h-4 text-green-400 flex-shrink-0" />
                              {reason}
                            </li>
                          ))}
                        </ul>
                      )}
                    </Card>
                  )}
                </div>
              )}
            </TabsContent>

            <TabsContent value="risk">
              <div className="space-y-6">
                <Card variant="elevated">
                  <h3 className="font-medium text-primary-text mb-4">Risk Signals</h3>
                  {riskEvents.length > 0 ? (
                    <div className="space-y-3">
                      {riskEvents.map((event, index) => (
                        <Animated key={index} initial="slideUp" delay={index * 50}>
                          <div className="p-3 rounded-xl bg-surface-secondary/50 border border-border/50">
                            <div className="flex items-start gap-3">
                              <div className={cn('w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0', event.severity === 'high' && 'bg-red-500/20', event.severity === 'medium' && 'bg-yellow-500/20', event.severity === 'low' && 'bg-green-500/20')}>
                                {event.severity === 'high' && <AlertTriangle className="w-4 h-4 text-red-400" />}
                                {event.severity === 'medium' && <AlertTriangle className="w-4 h-4 text-yellow-400" />}
                                {event.severity === 'low' && <ShieldCheck className="w-4 h-4 text-green-400" />}
                              </div>
                              <div className="flex-1">
                                <p className="font-medium text-primary-text">{event.signal.replace(/_/g, ' ')}</p>
                                <p className="text-sm text-secondary-text mt-1">{event.description}</p>
                                <Badge variant={event.severity === 'high' ? 'danger' : event.severity === 'medium' ? 'warning' : 'success'} className="mt-2 text-xs">
                                  {event.severity}
                                </Badge>
                              </div>
                            </div>
                          </div>
                        </Animated>
                      ))}
                    </div>
                  ) : (
                    <p className="text-secondary-text text-center py-8">No risk signals detected</p>
                  )}
                </Card>

                {verification && (
                  <Card variant="elevated">
                    <h3 className="font-medium text-primary-text mb-4">Risk Score Breakdown</h3>
                    <div className="space-y-3">
                      {Object.entries(verification.risk_signals).map(([key, value]) => (
                        <div key={key} className="flex items-center justify-between">
                          <span className="text-secondary-text">{key.replace(/_/g, ' ')}</span>
                          <span className="font-mono">{typeof value === 'number' ? value.toFixed(2) : String(value)}</span>
                        </div>
                      ))}
                    </div>
                  </Card>
                )}
              </div>
            </TabsContent>

            <TabsContent value="source">
              <Card variant="elevated">
                <h3 className="font-medium text-primary-text mb-4">Raw Source Data</h3>
                <pre className="bg-background rounded-xl p-4 overflow-x-auto scrollbar-thin text-xs text-secondary-text max-h-96">
                  {JSON.stringify(job.raw_source_metadata, null, 2)}
                </pre>
              </Card>
            </TabsContent>
          </Tabs>
        </Animated>

        <Animated initial="slideUp" delay={200}>
          <Card variant="elevated" className="sticky top-24">
            <h3 className="font-medium text-primary-text mb-4">Quick Actions</h3>
            <div className="space-y-2">
              <Button variant="secondary" className="w-full justify-start" onClick={() => window.open(job.source_url, '_blank')}>
                <ExternalLink className="w-4 h-4 mr-2" />
                View Original Posting
              </Button>
              <Button variant="secondary" className="w-full justify-start">
                <RefreshCw className="w-4 h-4 mr-2" />
                Re-verify Job
              </Button>
              <Button variant="secondary" className="w-full justify-start">
                <Download className="w-4 h-4 mr-2" />
                Export This Job
              </Button>
              <Button variant="secondary" className="w-full justify-start">
                <Mail className="w-4 h-4 mr-2" />
                Add to Outreach
              </Button>
            </div>

            <div className="mt-6 pt-6 border-t border-border">
              <h4 className="font-medium text-primary-text mb-3">Verification Summary</h4>
              <dl className="space-y-3 text-sm">
                {verification && [
                  { label: 'Source', score: verification.source_score },
                  { label: 'Employer', score: verification.employer_score },
                  { label: 'Uploader', score: verification.uploader_score },
                  { label: 'Content', score: verification.content_score },
                  { label: 'Contacts', score: verification.contact_score },
                  { label: 'Risk (inverted)', score: 100 - verification.risk_score },
                ].map((item, index) => (
                  <Animated key={item.label} initial="slideUp" delay={index * 50}>
                    <div className="flex items-center justify-between">
                      <span className="text-secondary-text">{item.label}</span>
                      <span className={cn('font-mono font-bold', item.score >= 70 ? 'text-green-400' : item.score >= 40 ? 'text-yellow-400' : 'text-red-400')}>
                        {item.score.toFixed(0)}%
                      </span>
                    </div>
                    <div className="h-1.5 bg-surface-secondary rounded-full overflow-hidden mt-1">
                      <div
                        className={cn('h-full rounded-full', item.score >= 70 ? 'bg-green-400' : item.score >= 40 ? 'bg-yellow-400' : 'bg-red-400')}
                        style={{ width: `${item.score}%` }}
                      />
                    </div>
                  </Animated>
                ))}
              </dl>
            </div>
          </Card>
        </Animated>
      </div>
    </Animated>
  )
}

function JobDetailSkeleton() {
  return (
    <>
      <Card variant="elevated">
        <div className="flex items-center gap-2 mb-4">
          <div className="h-6 w-20 bg-surface-secondary rounded animate-pulse" />
          <div className="h-6 w-32 bg-surface-secondary rounded animate-pulse" />
        </div>
        <h1 className="text-2xl font-bold">
          <div className="h-8 w-64 bg-surface-secondary rounded animate-pulse" />
        </h1>
      </Card>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card variant="elevated">
            <div className="h-6 w-32 bg-surface-secondary rounded mb-4 animate-pulse" />
            <div className="grid grid-cols-2 gap-4">
              {[...Array(6)].map((_, i) => (
                <div key={i}>
                  <div className="h-4 w-24 bg-surface-secondary rounded animate-pulse mb-1" />
                  <div className="h-6 w-32 bg-surface-secondary rounded animate-pulse" />
                </div>
              ))}
            </div>
          </Card>
        </div>
        <Card variant="elevated" className="sticky top-24">
          <div className="h-6 w-24 bg-surface-secondary rounded mb-4 animate-pulse" />
          <div className="space-y-2">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-10 bg-surface-secondary rounded animate-pulse" />
            ))}
          </div>
        </Card>
      </div>
    </>
  )
}