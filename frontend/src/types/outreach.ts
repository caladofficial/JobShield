export interface EmailCampaignResponse {
  id: number
  user_id: number
  name: string
  subject_template: string
  body_html_template: string
  body_text_template: string
  from_email: string
  from_name: string | null
  provider: string
  status: string
  total_recipients: number
  sent_count: number
  failed_count: number
  created_at: string
  updated_at: string
  sent_at: string | null
}

export interface EmailRecipientResponse {
  id: number
  campaign_id: number
  job_id: number | null
  contact_id: number | null
  email: string
  name: string | null
  status: string
  sent_at: string | null
  delivered_at: string | null
  opened_at: string | null
  clicked_at: string | null
  bounced_at: string | null
  error_message: string | null
  created_at: string
}