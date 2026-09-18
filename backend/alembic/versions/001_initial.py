"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2026-09-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('role', sa.Enum('admin', 'user', name='userrole'), nullable=False, server_default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Sources table
    op.create_table(
        'sources',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('display_name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('adapter_class', sa.String(100), nullable=False),
        sa.Column('base_url', sa.String(500), nullable=True),
        sa.Column('requires_authorization', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('rate_limit_per_minute', sa.Integer(), nullable=False, server_default='60'),
        sa.Column('config_schema', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_index('ix_sources_name', 'sources', ['name'], unique=True)

    # Source connections table
    op.create_table(
        'source_connections',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('source_id', sa.BigInteger(), nullable=False),
        sa.Column('status', sa.Enum('connected', 'disconnected', 'requires_authorization', 'rate_limited', 'error', 'unavailable', name='sourcestatus'), nullable=False, server_default='disconnected'),
        sa.Column('credentials_encrypted', sa.Text(), nullable=True),
        sa.Column('config', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('jobs_collected', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rate_limit_remaining', sa.Integer(), nullable=True),
        sa.Column('rate_limit_reset_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'source_id', name='uq_user_source'),
    )
    op.create_index('ix_source_connections_user_id', 'source_connections', ['user_id'])
    op.create_index('ix_source_connections_source_id', 'source_connections', ['source_id'])

    # Companies table
    op.create_table(
        'companies',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('normalized_name', sa.String(255), nullable=False),
        sa.Column('website', sa.String(500), nullable=True),
        sa.Column('domain', sa.String(255), nullable=True),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('size', sa.String(50), nullable=True),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('headquarters', sa.String(255), nullable=True),
        sa.Column('founded_year', sa.Integer(), nullable=True),
        sa.Column('linkedin_url', sa.String(500), nullable=True),
        sa.Column('verification_score', sa.Float(), nullable=True),
        sa.Column('verification_status', sa.Enum('pending', 'verified', 'failed', 'skipped', name='verificationstatus'), nullable=False, server_default='pending'),
        sa.Column('verification_signals', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_companies_name', 'companies', ['name'])
    op.create_index('ix_companies_normalized_name', 'companies', ['normalized_name'])
    op.create_index('ix_companies_domain', 'companies', ['domain'])

    # Recruiters table
    op.create_table(
        'recruiters',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('company_id', sa.BigInteger(), nullable=True),
        sa.Column('source_id', sa.BigInteger(), nullable=True),
        sa.Column('source_recruiter_id', sa.String(100), nullable=True),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('linkedin_url', sa.String(500), nullable=True),
        sa.Column('title', sa.String(100), nullable=True),
        sa.Column('verification_score', sa.Float(), nullable=True),
        sa.Column('verification_status', sa.Enum('pending', 'verified', 'failed', 'skipped', name='verificationstatus'), nullable=False, server_default='pending'),
        sa.Column('verification_signals', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('posting_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_recruiters_company_id', 'recruiters', ['company_id'])
    op.create_index('ix_recruiters_source_id', 'recruiters', ['source_id'])
    op.create_index('ix_recruiters_email', 'recruiters', ['email'])
    op.create_index('ix_recruiters_source_recruiter_id', 'recruiters', ['source_recruiter_id'])

    # Jobs table
    op.create_table(
        'jobs',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('source_id', sa.BigInteger(), nullable=False),
        sa.Column('source_job_id', sa.String(255), nullable=True),
        sa.Column('source_url', sa.String(1000), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('company_id', sa.BigInteger(), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('description_hash', sa.String(64), nullable=False),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('employment_type', sa.String(100), nullable=True),
        sa.Column('salary_min', sa.BigInteger(), nullable=True),
        sa.Column('salary_max', sa.BigInteger(), nullable=True),
        sa.Column('currency', sa.String(3), nullable=False, server_default='INR'),
        sa.Column('posted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('recruiter_id', sa.BigInteger(), nullable=True),
        sa.Column('apply_url', sa.String(1000), nullable=True),
        sa.Column('status', sa.Enum('new', 'processing', 'verified', 'needs_review', 'suspicious', 'high_risk', 'unable_to_verify', 'expired', 'duplicate', name='jobstatus'), nullable=False, server_default='new'),
        sa.Column('risk_level', sa.Enum('low', 'medium', 'high', 'unknown', name='risklevel'), nullable=False, server_default='unknown'),
        sa.Column('verification_score', sa.Float(), nullable=True),
        sa.Column('raw_source_metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['recruiter_id'], ['recruiters.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_jobs_user_id', 'jobs', ['user_id'])
    op.create_index('ix_jobs_source_id', 'jobs', ['source_id'])
    op.create_index('ix_jobs_source_job_id', 'jobs', ['source_job_id'])
    op.create_index('ix_jobs_company_id', 'jobs', ['company_id'])
    op.create_index('ix_jobs_recruiter_id', 'jobs', ['recruiter_id'])
    op.create_index('ix_jobs_status', 'jobs', ['status'])
    op.create_index('ix_jobs_risk_level', 'jobs', ['risk_level'])
    op.create_index('ix_jobs_posted_at', 'jobs', ['posted_at'])
    op.create_index('ix_jobs_created_at', 'jobs', ['created_at'])
    op.create_index('ix_jobs_description_hash', 'jobs', ['description_hash'])
    op.create_index('ix_jobs_user_status', 'jobs', ['user_id', 'status'])
    op.create_index('ix_jobs_source_source_job_id', 'jobs', ['source_id', 'source_job_id'])
    op.create_index('ix_jobs_company_title_location', 'jobs', ['company_id', 'title', 'location'])

    # Job contacts table
    op.create_table(
        'job_contacts',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('job_id', sa.BigInteger(), nullable=False),
        sa.Column('type', sa.Enum('email', 'phone', 'website', 'linkedin', 'application_url', name='contacttype'), nullable=False),
        sa.Column('value', sa.String(500), nullable=False),
        sa.Column('normalized_value', sa.String(500), nullable=False),
        sa.Column('is_valid', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_corporate', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('domain', sa.String(255), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('verification_method', sa.String(100), nullable=True),
        sa.Column('verification_status', sa.Enum('pending', 'verified', 'failed', 'skipped', name='verificationstatus'), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('job_id', 'type', 'normalized_value', name='uq_job_contact'),
    )
    op.create_index('ix_job_contacts_job_id', 'job_contacts', ['job_id'])
    op.create_index('ix_job_contacts_type', 'job_contacts', ['type'])
    op.create_index('ix_job_contacts_normalized_value', 'job_contacts', ['normalized_value'])
    op.create_index('ix_job_contacts_domain', 'job_contacts', ['domain'])

    # Job verifications table
    op.create_table(
        'job_verifications',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('job_id', sa.BigInteger(), nullable=False),
        sa.Column('source_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('employer_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('uploader_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('content_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('contact_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('risk_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('final_confidence', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', sa.Enum('new', 'processing', 'verified', 'needs_review', 'suspicious', 'high_risk', 'unable_to_verify', 'expired', 'duplicate', name='jobstatus'), nullable=False, server_default='new'),
        sa.Column('source_signals', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('employer_signals', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('uploader_signals', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('content_signals', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('contact_signals', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('risk_signals', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('ai_analysis', sa.JSON(), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('job_id'),
    )
    op.create_index('ix_job_verifications_job_id', 'job_verifications', ['job_id'])

    # Verification signals table
    op.create_table(
        'verification_signals',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('job_id', sa.BigInteger(), nullable=False),
        sa.Column('stage', sa.String(50), nullable=False),
        sa.Column('signal_name', sa.String(100), nullable=False),
        sa.Column('signal_value', sa.Float(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('details', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_verification_signals_job_id', 'verification_signals', ['job_id'])
    op.create_index('ix_verification_signals_stage', 'verification_signals', ['stage'])

    # Risk events table
    op.create_table(
        'risk_events',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('job_id', sa.BigInteger(), nullable=False),
        sa.Column('signal', sa.String(100), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('evidence', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_risk_events_job_id', 'risk_events', ['job_id'])
    op.create_index('ix_risk_events_signal', 'risk_events', ['signal'])

    # Job duplicates table
    op.create_table(
        'job_duplicates',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('job_id', sa.BigInteger(), nullable=False),
        sa.Column('duplicate_job_id', sa.BigInteger(), nullable=False),
        sa.Column('similarity_score', sa.Float(), nullable=False),
        sa.Column('match_type', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['duplicate_job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('job_id', 'duplicate_job_id', name='uq_job_duplicate'),
    )
    op.create_index('ix_job_duplicates_job_id', 'job_duplicates', ['job_id'])
    op.create_index('ix_job_duplicates_duplicate_job_id', 'job_duplicates', ['duplicate_job_id'])

    # Email campaigns table
    op.create_table(
        'email_campaigns',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('subject_template', sa.Text(), nullable=False),
        sa.Column('body_html_template', sa.Text(), nullable=False),
        sa.Column('body_text_template', sa.Text(), nullable=False),
        sa.Column('from_email', sa.String(255), nullable=False),
        sa.Column('from_name', sa.String(255), nullable=True),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='draft'),
        sa.Column('total_recipients', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('sent_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_email_campaigns_user_id', 'email_campaigns', ['user_id'])

    # Email recipients table
    op.create_table(
        'email_recipients',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('campaign_id', sa.BigInteger(), nullable=False),
        sa.Column('job_id', sa.BigInteger(), nullable=True),
        sa.Column('contact_id', sa.BigInteger(), nullable=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('opened_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('clicked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('bounced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['campaign_id'], ['email_campaigns.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['contact_id'], ['job_contacts.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_email_recipients_campaign_id', 'email_recipients', ['campaign_id'])
    op.create_index('ix_email_recipients_job_id', 'email_recipients', ['job_id'])
    op.create_index('ix_email_recipients_contact_id', 'email_recipients', ['contact_id'])

    # Email events table
    op.create_table(
        'email_events',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('recipient_id', sa.BigInteger(), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('details', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['recipient_id'], ['email_recipients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_email_events_recipient_id', 'email_events', ['recipient_id'])

    # Exports table
    op.create_table(
        'exports',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('format', sa.String(20), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('filters', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('download_url', sa.String(500), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('row_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_exports_user_id', 'exports', ['user_id'])

    # Audit logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_id', sa.String(100), nullable=True),
        sa.Column('details', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_resource_type', 'audit_logs', ['resource_type'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])

    # System events table
    op.create_table(
        'system_events',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('source', sa.String(100), nullable=False),
        sa.Column('level', sa.String(20), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('details', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_system_events_event_type', 'system_events', ['event_type'])
    op.create_index('ix_system_events_created_at', 'system_events', ['created_at'])


def downgrade() -> None:
    op.drop_table('system_events')
    op.drop_table('audit_logs')
    op.drop_table('exports')
    op.drop_table('email_events')
    op.drop_table('email_recipients')
    op.drop_table('email_campaigns')
    op.drop_table('job_duplicates')
    op.drop_table('risk_events')
    op.drop_table('verification_signals')
    op.drop_table('job_verifications')
    op.drop_table('job_contacts')
    op.drop_table('jobs')
    op.drop_table('recruiters')
    op.drop_table('companies')
    op.drop_table('source_connections')
    op.drop_table('sources')
    op.drop_table('users')