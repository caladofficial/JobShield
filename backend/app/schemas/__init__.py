from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    NEW = "new"
    PROCESSING = "processing"
    VERIFIED = "verified"
    NEEDS_REVIEW = "needs_review"
    SUSPICIOUS = "suspicious"
    HIGH_RISK = "high_risk"
    UNABLE_TO_VERIFY = "unable_to_verify"
    EXPIRED = "expired"
    DUPLICATE = "duplicate"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class ContactType(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    WEBSITE = "website"
    LINKEDIN = "linkedin"
    APPLICATION_URL = "application_url"


class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    SKIPPED = "skipped"


class SourceStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    REQUIRES_AUTHORIZATION = "requires_authorization"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    UNAVAILABLE = "unavailable"


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: int
    type: str


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    pass


class SourceBase(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    adapter_class: str
    base_url: Optional[str] = None
    requires_authorization: bool = False
    rate_limit_per_minute: int = 60
    config_schema: Dict[str, Any] = {}


class SourceCreate(SourceBase):
    pass


class SourceUpdate(BaseModel):
    is_active: Optional[bool] = None
    rate_limit_per_minute: Optional[int] = None


class SourceResponse(SourceBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SourceConnectionBase(BaseModel):
    source_id: int
    config: Dict[str, Any] = {}


class SourceConnectionCreate(SourceConnectionBase):
    credentials: Optional[Dict[str, str]] = None


class SourceConnectionUpdate(BaseModel):
    config: Optional[Dict[str, Any]] = None
    credentials: Optional[Dict[str, str]] = None


class SourceConnectionResponse(SourceConnectionBase):
    id: int
    user_id: int
    status: SourceStatus
    last_sync_at: Optional[datetime] = None
    last_error: Optional[str] = None
    jobs_collected: int
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    source: Optional[SourceResponse] = None

    class Config:
        from_attributes = True


class CompanyBase(BaseModel):
    name: str
    website: Optional[str] = None
    domain: Optional[str] = None
    description: Optional[str] = None
    size: Optional[str] = None
    industry: Optional[str] = None
    headquarters: Optional[str] = None
    founded_year: Optional[int] = None
    linkedin_url: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(CompanyBase):
    name: Optional[str] = None


class CompanyResponse(CompanyBase):
    id: int
    normalized_name: str
    logo_url: Optional[str] = None
    verification_score: Optional[float] = None
    verification_status: VerificationStatus
    verification_signals: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RecruiterBase(BaseModel):
    company_id: Optional[int] = None
    source_id: Optional[int] = None
    source_recruiter_id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    title: Optional[str] = None


class RecruiterCreate(RecruiterBase):
    pass


class RecruiterUpdate(RecruiterBase):
    pass


class RecruiterResponse(RecruiterBase):
    id: int
    verification_score: Optional[float] = None
    verification_status: VerificationStatus
    verification_signals: Dict[str, Any] = {}
    posting_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SalaryInfo(BaseModel):
    min: Optional[int] = None
    max: Optional[int] = None
    currency: str = "INR"
    period: str = "yearly"


class ContactInfo(BaseModel):
    type: ContactType
    value: str
    normalized_value: str
    is_valid: bool = False
    is_corporate: bool = False
    domain: Optional[str] = None
    confidence: float = 0.0
    verification_method: Optional[str] = None
    verification_status: VerificationStatus = VerificationStatus.PENDING


class JobBase(BaseModel):
    source_id: int
    source_job_id: Optional[str] = None
    source_url: HttpUrl
    title: str = Field(min_length=1, max_length=500)
    company_name: Optional[str] = None
    description: str = Field(min_length=1)
    location: Optional[str] = None
    employment_type: Optional[str] = None
    salary: Optional[SalaryInfo] = None
    posted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    recruiter_name: Optional[str] = None
    apply_url: Optional[HttpUrl] = None
    raw_source_metadata: Dict[str, Any] = {}


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = None
    company_name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    salary: Optional[SalaryInfo] = None
    posted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    recruiter_name: Optional[str] = None
    apply_url: Optional[HttpUrl] = None
    status: Optional[JobStatus] = None
    risk_level: Optional[RiskLevel] = None


class JobResponse(JobBase):
    id: int
    user_id: int
    company_id: Optional[int] = None
    recruiter_id: Optional[int] = None
    description_hash: str
    status: JobStatus
    risk_level: RiskLevel
    verification_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    verified_at: Optional[datetime] = None
    company: Optional[CompanyResponse] = None
    recruiter: Optional[RecruiterResponse] = None
    contacts: List[ContactInfo] = []
    verification: Optional["JobVerificationResponse"] = None

    class Config:
        from_attributes = True


class JobListItem(BaseModel):
    id: int
    source_id: int
    source_job_id: Optional[str] = None
    source_url: str
    title: str
    company_name: Optional[str] = None
    company_id: Optional[int] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    currency: str
    posted_at: Optional[datetime] = None
    status: JobStatus
    risk_level: RiskLevel
    verification_score: Optional[float] = None
    created_at: datetime
    has_email: bool = False
    has_phone: bool = False
    source_name: str


class JobVerificationBase(BaseModel):
    source_score: float = 0.0
    employer_score: float = 0.0
    uploader_score: float = 0.0
    content_score: float = 0.0
    contact_score: float = 0.0
    risk_score: float = 0.0
    final_confidence: float = 0.0
    status: JobStatus
    source_signals: Dict[str, Any] = {}
    employer_signals: Dict[str, Any] = {}
    uploader_signals: Dict[str, Any] = {}
    content_signals: Dict[str, Any] = {}
    contact_signals: Dict[str, Any] = {}
    risk_signals: Dict[str, Any] = {}
    ai_analysis: Optional[Dict[str, Any]] = None


class JobVerificationCreate(JobVerificationBase):
    pass


class JobVerificationUpdate(BaseModel):
    source_score: Optional[float] = None
    employer_score: Optional[float] = None
    uploader_score: Optional[float] = None
    content_score: Optional[float] = None
    contact_score: Optional[float] = None
    risk_score: Optional[float] = None
    final_confidence: Optional[float] = None
    status: Optional[JobStatus] = None
    source_signals: Optional[Dict[str, Any]] = None
    employer_signals: Optional[Dict[str, Any]] = None
    uploader_signals: Optional[Dict[str, Any]] = None
    content_signals: Optional[Dict[str, Any]] = None
    contact_signals: Optional[Dict[str, Any]] = None
    risk_signals: Optional[Dict[str, Any]] = None
    ai_analysis: Optional[Dict[str, Any]] = None


class JobVerificationResponse(JobVerificationBase):
    id: int
    job_id: int
    verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RiskEventBase(BaseModel):
    signal: str
    severity: str
    description: str
    evidence: Dict[str, Any] = {}


class RiskEventResponse(RiskEventBase):
    id: int
    job_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class JobScanRequest(BaseModel):
    source_url: HttpUrl
    source_id: Optional[int] = None
    force_rescan: bool = False


class JobScanResponse(BaseModel):
    job_id: int
    status: JobStatus
    message: str


class VerificationProgress(BaseModel):
    job_id: int
    stage: str
    progress: int
    message: str
    completed: bool = False


class ExportRequest(BaseModel):
    format: str = Field(pattern="^(xlsx|csv)$")
    filters: Dict[str, Any] = {}


class ExportResponse(BaseModel):
    id: int
    user_id: int
    format: str
    status: str
    filters: Dict[str, Any] = {}
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    row_count: int
    created_at: datetime
    completed_at: Optional[datetime] = None


class EmailCampaignBase(BaseModel):
    name: str
    subject_template: str
    body_html_template: str
    body_text_template: str
    from_email: EmailStr
    from_name: Optional[str] = None
    provider: str


class EmailCampaignCreate(EmailCampaignBase):
    recipient_contact_ids: List[int] = []


class EmailCampaignUpdate(BaseModel):
    name: Optional[str] = None
    subject_template: Optional[str] = None
    body_html_template: Optional[str] = None
    body_text_template: Optional[str] = None
    from_email: Optional[EmailStr] = None
    from_name: Optional[str] = None
    status: Optional[str] = None


class EmailCampaignResponse(EmailCampaignBase):
    id: int
    user_id: int
    status: str
    total_recipients: int
    sent_count: int
    failed_count: int
    created_at: datetime
    updated_at: datetime
    sent_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmailRecipientResponse(BaseModel):
    id: int
    campaign_id: int
    job_id: Optional[int] = None
    contact_id: Optional[int] = None
    email: str
    name: Optional[str] = None
    status: str
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    bounced_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    redis: str
    timestamp: datetime


class StatsResponse(BaseModel):
    total_jobs: int
    verified_jobs: int
    needs_review: int
    high_risk: int
    total_contacts: int
    corporate_emails: int
    free_mail_emails: int
    valid_phones: int
    sources_active: int
    jobs_today: int
    verified_today: int


class ChartDataPoint(BaseModel):
    label: str
    value: int


class VerificationActivityChart(BaseModel):
    data: List[ChartDataPoint]


class JobsBySourceChart(BaseModel):
    data: List[ChartDataPoint]


class RiskDistributionChart(BaseModel):
    data: List[ChartDataPoint]


class DashboardResponse(BaseModel):
    stats: StatsResponse
    verification_activity: VerificationActivityChart
    jobs_by_source: JobsBySourceChart
    risk_distribution: RiskDistributionChart
    recent_jobs: List[JobListItem]
    recent_events: List[Dict[str, Any]]
    source_health: List[SourceConnectionResponse]


JobResponse.model_rebuild()