export interface ChartDataPoint {
  label: string
  value: number
}

export interface VerificationActivityChart {
  data: ChartDataPoint[]
}

export interface JobsBySourceChart {
  data: ChartDataPoint[]
}

export interface RiskDistributionChart {
  data: ChartDataPoint[]
}

export interface JobListItem {
  id: number
  source_id: number
  source_job_id: string | null
  source_url: string
  title: string
  company_name: string | null
  company_id: number | null
  location: string | null
  employment_type: string | null
  salary_min: number | null
  salary_max: number | null
  currency: string
  posted_at: string | null
  status: JobStatus
  risk_level: RiskLevel
  verification_score: number | null
  created_at: string
  has_email: boolean
  has_phone: boolean
  source_name: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export type JobStatus =
  | 'new'
  | 'processing'
  | 'verified'
  | 'needs_review'
  | 'suspicious'
  | 'high_risk'
  | 'unable_to_verify'
  | 'expired'
  | 'duplicate'

export type RiskLevel = 'low' | 'medium' | 'high' | 'unknown'

export interface SourceResponse {
  id: number
  name: string
  display_name: string
  description: string | null
  adapter_class: string
  base_url: string | null
  requires_authorization: boolean
  is_active: boolean
  rate_limit_per_minute: number
  config_schema: Record<string, any>
  created_at: string
  updated_at: string
}

export interface SourceConnectionResponse {
  id: number
  user_id: number
  source_id: number
  status: SourceStatus
  config: Record<string, any>
  last_sync_at: string | null
  last_error: string | null
  jobs_collected: number
  rate_limit_remaining: number | null
  rate_limit_reset_at: string | null
  created_at: string
  updated_at: string
  source?: SourceResponse
}

export type SourceStatus =
  | 'connected'
  | 'disconnected'
  | 'requires_authorization'
  | 'rate_limited'
  | 'error'
  | 'unavailable'

export interface StatsResponse {
  total_jobs: number
  verified_jobs: number
  needs_review: number
  high_risk: number
  total_contacts: number
  corporate_emails: number
  free_mail_emails: number
  valid_phones: number
  sources_active: number
  jobs_today: number
  verified_today: number
}

export interface DashboardResponse {
  stats: StatsResponse
  verification_activity: VerificationActivityChart
  jobs_by_source: JobsBySourceChart
  risk_distribution: RiskDistributionChart
  recent_jobs: JobListItem[]
  recent_events: Array<{
    type: string
    message: string
    level: string
    created_at: string
  }>
  source_health: SourceHealthItem[]
}

export interface SourceHealthItem {
  source: string
  status: string
  last_sync: string | null
  jobs_collected: number
  last_error: string | null
}