from celery import shared_task
from app.core.database import async_session_maker
from app.models import EmailCampaign, EmailRecipient, EmailEvent, Job, JobContact, ContactType
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.services.email_providers import get_email_provider, EmailMessage
from datetime import datetime
import structlog
import asyncio

logger = structlog.get_logger()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_campaign_task(self, campaign_id: int):
    return asyncio.run(_send_campaign_async(campaign_id))


async def _send_campaign_async(campaign_id: int):
    async with async_session_maker() as db:
        stmt = (
            select(EmailCampaign)
            .where(EmailCampaign.id == campaign_id)
            .options(selectinload(EmailCampaign.recipients).selectinload(EmailRecipient.job))
        )
        result = await db.execute(stmt)
        campaign = result.scalar_one_or_none()

        if not campaign:
            logger.error("campaign_not_found", campaign_id=campaign_id)
            return {"status": "error", "message": "Campaign not found"}

        if campaign.status not in ["draft", "scheduled", "paused"]:
            return {"status": "error", "message": f"Campaign cannot be sent from status: {campaign.status}"}

        provider = get_email_provider(campaign.provider, campaign.get_provider_credentials())

        if not await provider.validate_connection():
            campaign.status = "failed"
            await db.commit()
            return {"status": "error", "message": "Email provider connection invalid"}

        quota = await provider.get_quota()
        if quota.get("remaining", 0) < campaign.total_recipients:
            campaign.status = "quota_exceeded"
            await db.commit()
            return {"status": "error", "message": "Insufficient email quota"}

        campaign.status = "sending"
        await db.commit()

        pending_recipients = [
            r for r in campaign.recipients
            if r.status == "pending"
        ]

        sent = 0
        failed = 0

        for recipient in pending_recipients:
            if campaign.status == "cancelled":
                break

            job = recipient.job
            job_title = job.title if job else "the position"
            company_name = job.company.name if job and job.company else "the company"
            recruiter_name = recipient.name or job.recruiter.name if job and job.recruiter else "Hiring Manager"

            subject = campaign.subject_template.format(
                candidate_name="Candidate",
                company_name=company_name,
                job_title=job_title,
                recruiter_name=recruiter_name,
                job_location=job.location if job else "",
            )

            body_html = campaign.body_html_template.format(
                candidate_name="Candidate",
                company_name=company_name,
                job_title=job_title,
                recruiter_name=recruiter_name,
                job_location=job.location if job else "",
            )

            body_text = campaign.body_text_template.format(
                candidate_name="Candidate",
                company_name=company_name,
                job_title=job_title,
                recruiter_name=recruiter_name,
                job_location=job.location if job else "",
            )

            message = EmailMessage(
                to=[recipient.email],
                subject=subject,
                body_html=body_html,
                body_text=body_text,
                from_email=campaign.from_email,
                from_name=campaign.from_name,
            )

            result = await provider.send(message)

            if result.success:
                recipient.status = "sent"
                recipient.sent_at = datetime.utcnow()
                sent += 1

                event = EmailEvent(
                    recipient_id=recipient.id,
                    event_type="sent",
                    details={"message_id": result.message_id},
                )
                db.add(event)
            else:
                recipient.status = "failed"
                recipient.error_message = result.error
                failed += 1

                event = EmailEvent(
                    recipient_id=recipient.id,
                    event_type="failed",
                    details={"error": result.error},
                )
                db.add(event)

            if sent % 10 == 0:
                campaign.sent_count = sent
                campaign.failed_count = failed
                await db.commit()

        campaign.sent_count = sent
        campaign.failed_count = failed
        campaign.status = "completed" if failed == 0 else "completed_with_errors"
        campaign.sent_at = datetime.utcnow()
        await db.commit()

        await provider.disconnect()

        logger.info("campaign_completed", campaign_id=campaign_id, sent=sent, failed=failed)
        return {"status": "success", "sent": sent, "failed": failed}


@shared_task
def send_test_email_task(campaign_id: int, test_email: str):
    return asyncio.run(_send_test_email_async(campaign_id, test_email))


async def _send_test_email_async(campaign_id: int, test_email: str):
    async with async_session_maker() as db:
        stmt = select(EmailCampaign).where(EmailCampaign.id == campaign_id)
        result = await db.execute(stmt)
        campaign = result.scalar_one_or_none()

        if not campaign:
            return {"status": "error", "message": "Campaign not found"}

        provider = get_email_provider(campaign.provider, campaign.get_provider_credentials())

        subject = f"[TEST] {campaign.subject_template.format(candidate_name='Test User', company_name='Test Company', job_title='Test Job', recruiter_name='Test Recruiter', job_location='Test Location')}"
        body_html = campaign.body_html_template.format(candidate_name='Test User', company_name='Test Company', job_title='Test Job', recruiter_name='Test Recruiter', job_location='Test Location')
        body_text = campaign.body_text_template.format(candidate_name='Test User', company_name='Test Company', job_title='Test Job', recruiter_name='Test Recruiter', job_location='Test Location')

        result = await provider.send_test(test_email, subject, body_html)

        await provider.disconnect()

        return {"status": "success" if result.success else "error", "message": result.error or "Test email sent"}