import enum
from datetime import datetime, UTC
from typing import Optional
from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    Index,
    UniqueConstraint,
    BigInteger,
    JSON,
    Boolean,
    Integer,
    Float,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class JobStatus(str, enum.Enum):
    NEW = "new"
    PROCESSING = "processing"
    VERIFIED = "verified"
    NEEDS_REVIEW = "needs_review"
    SUSPICIOUS = "suspicious"
    HIGH_RISK = "high_risk"
    UNABLE_TO_VERIFY = "unable_to_verify"
    EXPIRED = "expired"
    DUPLICATE = "duplicate"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class ContactType(str, enum.Enum):
    EMAIL = "email"
    PHONE = "phone"
    WEBSITE = "website"
    LINKEDIN = "linkedin"
    APPLICATION_URL = "application_url"


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    SKIPPED = "skipped"


class SourceStatus(str, enum.Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    REQUIRES_AUTHORIZATION = "requires_authorization"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    UNAVAILABLE = "unavailable"


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    sources: Mapped[list["SourceConnection"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    jobs: Mapped[list["Job"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    exports: Mapped[list["Export"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    campaigns: Mapped[list["EmailCampaign"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    adapter_class: Mapped[str] = mapped_column(String(100), nullable=False)
    base_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    requires_authorization: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rate_limit_per_minute: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    config_schema: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    connections: Mapped[list["SourceConnection"]] = relationship(back_populates="source", cascade="all, delete-orphan")
    jobs: Mapped[list["Job"]] = relationship(back_populates="source")


class SourceConnection(Base):
    __tablename__ = "source_connections"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[SourceStatus] = mapped_column(SQLEnum(SourceStatus), default=SourceStatus.DISCONNECTED, nullable=False)
    credentials_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    jobs_collected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rate_limit_remaining: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rate_limit_reset_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    user: Mapped["User"] = relationship(back_populates="sources")
    source: Mapped["Source"] = relationship(back_populates="connections")

    __table_args__ = (
        UniqueConstraint("user_id", "source_id", name="uq_user_source"),
    )


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    domain: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    headquarters: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    founded_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    verification_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    verification_status: Mapped[VerificationStatus] = mapped_column(SQLEnum(VerificationStatus), default=VerificationStatus.PENDING, nullable=False)
    verification_signals: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    jobs: Mapped[list["Job"]] = relationship(back_populates="company")
    recruiters: Mapped[list["Recruiter"]] = relationship(back_populates="company")


class Recruiter(Base):
    __tablename__ = "recruiters"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    company_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True)
    source_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("sources.id", ondelete="SET NULL"), nullable=True, index=True)
    source_recruiter_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    verification_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    verification_status: Mapped[VerificationStatus] = mapped_column(SQLEnum(VerificationStatus), default=VerificationStatus.PENDING, nullable=False)
    verification_signals: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    posting_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    company: Mapped[Optional["Company"]] = relationship(back_populates="recruiters")
    source: Mapped[Optional["Source"]] = relationship()


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("sources.id", ondelete="RESTRICT"), nullable=False, index=True)
    source_job_id: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    source_url: Mapped[str] = mappedColumn(String(1000), nullable=False)
    title: Mapped[str] = mapped_column(String(500), index=True, nullable=False)
    company_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    description_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    employment_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    salary_min: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    salary_max: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    recruiter_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("recruiters.id", ondelete="SET NULL"), nullable=True, index=True)
    apply_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    status: Mapped[JobStatus] = mapped_column(SQLEnum(JobStatus), default=JobStatus.NEW, index=True, nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(SQLEnum(RiskLevel), default=RiskLevel.UNKNOWN, index=True, nullable=False)
    verification_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    raw_source_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="jobs")
    source: Mapped["Source"] = relationship(back_populates="jobs")
    company: Mapped[Optional["Company"]] = relationship(back_populates="jobs")
    recruiter: Mapped[Optional["Recruiter"]] = relationship()
    contacts: Mapped[list["JobContact"]] = relationship(back_populates="job", cascade="all, delete-orphan")
    verification: Mapped[Optional["JobVerification"]] = relationship(back_populates="job", uselist=False, cascade="all, delete-orphan")
    duplicates: Mapped[list["JobDuplicate"]] = relationship(back_populates="job", cascade="all, delete-orphan", foreign_keys="JobDuplicate.job_id")
    duplicate_of: Mapped[list["JobDuplicate"]] = relationship(back_populates="duplicate_job", cascade="all, delete-orphan", foreign_keys="JobDuplicate.duplicate_job_id")

    __table_args__ = (
        Index("ix_jobs_user_status", "user_id", "status"),
        Index("ix_jobs_source_source_job_id", "source_id", "source_job_id"),
        Index("ix_jobs_company_title_location", "company_id", "title", "location"),
    )


class JobContact(Base):
    __tablename__ = "job_contacts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    type: Mapped[ContactType] = mapped_column(SQLEnum(ContactType), nullable=False, index=True)
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    normalized_value: Mapped[str] = mapped_column(String(500), index=True, nullable=False)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_corporate: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    verification_method: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    verification_status: Mapped[VerificationStatus] = mapped_column(SQLEnum(VerificationStatus), default=VerificationStatus.PENDING, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    job: Mapped["Job"] = relationship(back_populates="contacts")

    __table_args__ = (
        UniqueConstraint("job_id", "type", "normalized_value", name="uq_job_contact"),
    )


class JobVerification(Base):
    __tablename__ = "job_verifications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    source_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    employer_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    uploader_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    content_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    contact_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    final_confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[JobStatus] = mapped_column(SQLEnum(JobStatus), default=JobStatus.NEW, nullable=False)

    source_signals: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    employer_signals: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    uploader_signals: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    content_signals: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    contact_signals: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    risk_signals: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    ai_analysis: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    job: Mapped["Job"] = relationship(back_populates="verification")


class VerificationSignal(Base):
    __tablename__ = "verification_signals"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    stage: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    signal_name: Mapped[str] = mapped_column(String(100), nullable=False)
    signal_value: Mapped[float] = mapped_column(Float, nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)


class RiskEvent(Base):
    __tablename__ = "risk_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    signal: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)


class JobDuplicate(Base):
    __tablename__ = "job_duplicates"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    duplicate_job_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    match_type: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    job: Mapped["Job"] = relationship(back_populates="duplicates", foreign_keys=[job_id])
    duplicate_job: Mapped["Job"] = relationship(back_populates="duplicate_of", foreign_keys=[duplicate_job_id])

    __table_args__ = (
        UniqueConstraint("job_id", "duplicate_job_id", name="uq_job_duplicate"),
    )


class EmailCampaign(Base):
    __tablename__ = "email_campaigns"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    subject_template: Mapped[str] = mapped_column(Text, nullable=False)
    body_html_template: Mapped[str] = mapped_column(Text, nullable=False)
    body_text_template: Mapped[str] = mapped_column(Text, nullable=False)
    from_email: Mapped[str] = mapped_column(String(255), nullable=False)
    from_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)
    total_recipients: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sent_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="campaigns")
    recipients: Mapped[list["EmailRecipient"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")


class EmailRecipient(Base):
    __tablename__ = "email_recipients"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("email_campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True, index=True)
    contact_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("job_contacts.id", ondelete="SET NULL"), nullable=True, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    clicked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    bounced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    campaign: Mapped["EmailCampaign"] = relationship(back_populates="recipients")
    job: Mapped[Optional["Job"]] = relationship()
    contact: Mapped[Optional["JobContact"]] = relationship()


class EmailEvent(Base):
    __tablename__ = "email_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    recipient_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("email_recipients.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)


class Export(Base):
    __tablename__ = "exports"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    format: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    filters: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    download_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    row_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="exports")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True, nullable=False)


class SystemEvent(Base):
    __tablename__ = "system_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    level: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True, nullable=False)