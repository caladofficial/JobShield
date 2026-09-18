export interface ContactInfo {
  type: 'email' | 'phone' | 'website' | 'linkedin' | 'application_url'
  value: string
  normalized_value: string
  is_valid: boolean
  is_corporate: boolean
  domain: string | null
  confidence: number
  verification_method: string | null
  verification_status: string
}

export interface JobResponse {
  id: number
  user_id: number
  source_id: number
  source_job_id: string | null
  source_url: string
  title: string
  company_name: string | null
  description: string
  location: string | null
  employment_type: string | null
  salary_min: number | null
  salary_max: number | null
  currency: string
  posted_at: string | null
  expires_at: string | null
  apply_url: string | null
  status: JobStatus
  risk_level: RiskLevel
  verification_score: number | null
  created_at: string
  updated_at: string
  verified_at: string | null
  company: CompanyResponse | null
  recruiter: RecruiterResponse | null
  contacts: ContactInfo[]
  verification: JobVerificationResponse | null
}

export interface CompanyResponse {
  id: number
  name: string
  normalized_name: string
  website: string | null
  domain: string | null
  logo_url: string | null
  description: string | null
  size: string | null
  industry: string | null
  headquarters: string | null
  founded_year: number | null
  linkedin_url: string | null
  verification_score: number | null
  verification_status: string
  verification_signals: Record<string, any>
  created_at: string
  updated_at: string
}

export interface RecruiterResponse {
  id: number
  company_id: number | null
  source_id: number | null
  source_recruiter_id: string | null
  name: string | null
  email: string | null
  phone: string | null
  linkedin_url: string | null
  title: string | null
  verification_score: number | null
  verification_status: string
  verification_signals: Record<string, any>
  posting_count: number
  created_at: string
  updated_at: string
}

export interface JobVerificationResponse {
  id: number
  job_id: number
  source_score: number
  employer_score: number
  uploader_score: number
  content_score: number
  contact_score: number
  risk_score: number
  final_confidence: number
  status: JobStatus
  source_signals: Record<string, any>
  employer_signals: Record<string, any>
  uploader_signals: Record<string, any>
  content_signals: Record<string, any>
  contact_signals: Record<string, any>
  risk_signals: Record<string, any>
  ai_analysis: AIAnalysis | null
  verified_at: string | null
  created_at: string
  updated_at: string
}

export interface AIAnalysis {
  job_quality: number
  scam_risk: number
  contact_consistency: number
  summary: string
  reasons: string[]
}

export interface RiskEventResponse {
  id: number
  job_id: number
  signal: string
  severity: string
  description: string
  evidence: Record<string, any>
  created_at: string
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