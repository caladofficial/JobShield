import re
import socket
import dns.resolver
import dns.exception
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from urllib.parse import urlparse
import httpx
import structlog
from app.models import Job, Company, Recruiter, JobContact, JobVerification, VerificationSignal, RiskEvent, VerificationStatus, JobStatus, RiskLevel, ContactType
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings

logger = structlog.get_logger()

logger = structlog.get_logger()


class VerificationPipeline:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def run_full_verification(self, job_id: int) -> JobVerification:
        job = await self._get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        job.status = JobStatus.PROCESSING
        await self.db.flush()

        verification = JobVerification(
            job_id=job.id,
            source_score=0.0,
            employer_score=0.0,
            uploader_score=0.0,
            content_score=0.0,
            contact_score=0.0,
            risk_score=0.0,
            final_confidence=0.0,
            status=JobStatus.PROCESSING,
        )
        self.db.add(verification)
        await self.db.flush()

        source_result = await self._verify_source(job, verification)
        employer_result = await self._verify_employer(job, verification)
        uploader_result = await self._verify_uploader(job, verification)
        content_result = await self._verify_content(job, verification)
        contact_result = await self._verify_contacts(job, verification)
        risk_result = await self._analyze_risk(job, verification)

        final_confidence = self._calculate_final_confidence(
            source_result, employer_result, uploader_result, content_result, contact_result, risk_result
        )

        final_status = self._determine_status(final_confidence, risk_result["risk_level"])

        verification.source_score = source_result["score"]
        verification.employer_score = employer_result["score"]
        verification.uploader_score = uploader_result["score"]
        verification.content_score = content_result["score"]
        verification.contact_score = contact_result["score"]
        verification.risk_score = risk_result["score"]
        verification.final_confidence = final_confidence
        verification.status = final_status
        verification.verified_at = datetime.utcnow()

        job.status = final_status
        job.risk_level = risk_result["risk_level"]
        job.verification_score = final_confidence
        job.verified_at = datetime.utcnow()

        await self.db.flush()
        return verification

    async def _get_job(self, job_id: int) -> Optional[Job]:
        stmt = select(Job).where(Job.id == job_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    def _calculate_final_confidence(
        self,
        source: Dict,
        employer: Dict,
        uploader: Dict,
        content: Dict,
        contact: Dict,
        risk: Dict,
    ) -> float:
        weights = {
            "source": 0.15,
            "employer": 0.25,
            "uploader": 0.15,
            "content": 0.20,
            "contact": 0.15,
            "risk": 0.10,
        }
        confidence = (
            source["score"] * weights["source"] +
            employer["score"] * weights["employer"] +
            uploader["score"] * weights["uploader"] +
            content["score"] * weights["content"] +
            contact["score"] * weights["contact"] +
            (1.0 - risk["score"]) * weights["risk"]
        )
        return round(confidence * 100, 2)

    def _determine_status(self, confidence: float, risk_level: RiskLevel) -> JobStatus:
        if risk_level == RiskLevel.HIGH:
            return JobStatus.HIGH_RISK
        if risk_level == RiskLevel.MEDIUM:
            return JobStatus.NEEDS_REVIEW
        if confidence >= 70:
            return JobStatus.VERIFIED
        if confidence >= 40:
            return JobStatus.NEEDS_REVIEW
        return JobStatus.UNABLE_TO_VERIFY

    def _add_signal(self, verification: JobVerification, stage: str, name: str, value: float, weight: float, details: Dict):
        signal = VerificationSignal(
            job_id=verification.job_id,
            stage=stage,
            signal_name=name,
            signal_value=value,
            weight=weight,
            details=details,
        )
        self.db.add(signal)

    def _add_risk_event(self, job_id: int, signal: str, severity: str, description: str, evidence: Dict):
        event = RiskEvent(
            job_id=job_id,
            signal=signal,
            severity=severity,
            description=description,
            evidence=evidence,
        )
        self.db.add(event)

    async def _verify_source(self, job: Job, verification: JobVerification) -> Dict[str, Any]:
        signals = {}
        score = 0.5

        if job.source_job_id:
            signals["has_source_job_id"] = True
            score += 0.2
        else:
            signals["has_source_job_id"] = False

        if job.source_url:
            signals["has_source_url"] = True
            score += 0.1
            try:
                parsed = urlparse(job.source_url)
                signals["source_domain"] = parsed.netloc
            except Exception:
                pass
        else:
            signals["has_source_url"] = False

        if job.raw_source_metadata:
            signals["has_metadata"] = True
            score += 0.1
        else:
            signals["has_metadata"] = False

        source_name = job.source.name.lower() if job.source else "unknown"
        trusted_sources = ["greenhouse", "lever", "workday", "ashby", "smartrecruiters", "icims"]
        if source_name in trusted_sources:
            signals["trusted_ats"] = True
            score += 0.3
        else:
            signals["trusted_ats"] = False

        score = min(1.0, score)
        verification.source_signals = signals

        for name, value in signals.items():
            self._add_signal(verification, "source", name, 1.0 if value else 0.0, 1.0, {"value": value})

        return {"score": score, "signals": signals}

    async def _verify_employer(self, job: Job, verification: JobVerification) -> Dict[str, Any]:
        signals = {}
        score = 0.0

        if not job.company:
            signals["has_company"] = False
            verification.employer_signals = signals
            return {"score": 0.0, "signals": signals}

        signals["has_company"] = True
        score += 0.2

        company = job.company

        if company.domain:
            signals["has_domain"] = True
            score += 0.15

            domain_valid = await self._verify_domain(company.domain)
            signals["domain_valid"] = domain_valid
            if domain_valid:
                score += 0.15

                has_mx = await self._check_mx_record(company.domain)
                signals["has_mx"] = has_mx
                if has_mx:
                    score += 0.1

                website_ok = await self._check_website(company.website or f"https://{company.domain}")
                signals["website_accessible"] = website_ok
                if website_ok:
                    score += 0.1

                if job.contacts:
                    corporate_emails = [c for c in job.contacts if c.type == ContactType.EMAIL and c.is_corporate]
                    if corporate_emails:
                        email_domain = corporate_emails[0].domain
                        if email_domain and email_domain.lower() == company.domain.lower():
                            signals["email_domain_matches"] = True
                            score += 0.2
                        else:
                            signals["email_domain_matches"] = False
                    else:
                        signals["email_domain_matches"] = False

        if company.website:
            signals["has_website"] = True
            score += 0.05

        if company.verification_status == VerificationStatus.VERIFIED:
            signals["previously_verified"] = True
            score += 0.1

        score = min(1.0, score)
        verification.employer_signals = signals

        for name, value in signals.items():
            self._add_signal(verification, "employer", name, 1.0 if value else 0.0, 1.0, {"value": value})

        return {"score": score, "signals": signals}

    async def _verify_domain(self, domain: str) -> bool:
        try:
            socket.gethostbyname(domain)
            return True
        except socket.gaierror:
            return False

    async def _check_mx_record(self, domain: str) -> bool:
        try:
            answers = dns.resolver.resolve(domain, "MX")
            return len(answers) > 0
        except dns.exception.DNSException:
            return False

    async def _check_website(self, url: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.head(url)
                return response.status_code < 400
        except Exception:
            return False

    async def _verify_uploader(self, job: Job, verification: JobVerification) -> Dict[str, Any]:
        signals = {}
        score = 0.0

        if not job.recruiter:
            signals["has_recruiter"] = False
            verification.uploader_signals = signals
            return {"score": 0.3, "signals": signals}

        signals["has_recruiter"] = True
        score += 0.2

        recruiter = job.recruiter

        if recruiter.name:
            signals["has_name"] = True
            score += 0.1

        if recruiter.email:
            signals["has_email"] = True
            score += 0.1
            if job.company and recruiter.email.endswith(f"@{job.company.domain}"):
                signals["email_matches_company"] = True
                score += 0.2
            else:
                signals["email_matches_company"] = False

        if recruiter.linkedin_url:
            signals["has_linkedin"] = True
            score += 0.1

        if recruiter.verification_status == VerificationStatus.VERIFIED:
            signals["previously_verified"] = True
            score += 0.2

        if recruiter.posting_count > 0:
            signals["has_posting_history"] = True
            score += min(0.2, recruiter.posting_count * 0.02)

        score = min(1.0, score)
        verification.uploader_signals = signals

        for name, value in signals.items():
            self._add_signal(verification, "uploader", name, 1.0 if value else 0.0, 1.0, {"value": value})

        return {"score": score, "signals": signals}

    async def _verify_content(self, job: Job, verification: JobVerification) -> Dict[str, Any]:
        signals = {}
        score = 0.5

        desc = job.description
        if len(desc) > 200:
            signals["adequate_length"] = True
            score += 0.1
        else:
            signals["adequate_length"] = False

        if len(desc) > 1000:
            signals["detailed_description"] = True
            score += 0.1

        title_lower = job.title.lower()
        desc_lower = desc.lower()

        if any(kw in desc_lower for kw in ["responsibilities", "requirements", "qualifications", "benefits", "about us"]):
            signals["structured_content"] = True
            score += 0.15

        if job.salary_min and job.salary_max and job.salary_min < job.salary_max:
            signals["has_salary_range"] = True
            score += 0.1

        if job.location:
            signals["has_location"] = True
            score += 0.05

        if job.employment_type:
            signals["has_employment_type"] = True
            score += 0.05

        score = min(1.0, score)
        verification.content_signals = signals

        for name, value in signals.items():
            self._add_signal(verification, "content", name, 1.0 if value else 0.0, 1.0, {"value": value})

        return {"score": score, "signals": signals}

    async def _verify_contacts(self, job: Job, verification: JobVerification) -> Dict[str, Any]:
        signals = {}
        score = 0.0

        contacts = job.contacts
        if not contacts:
            signals["has_contacts"] = False
            verification.contact_signals = signals
            return {"score": 0.0, "signals": signals}

        signals["has_contacts"] = True
        score += 0.2

        emails = [c for c in contacts if c.type == ContactType.EMAIL]
        phones = [c for c in contacts if c.type == ContactType.PHONE]

        if emails:
            signals["has_email"] = True
            score += 0.2
            valid_emails = [e for e in emails if e.is_valid]
            if valid_emails:
                signals["has_valid_email"] = True
                score += 0.1
                corporate_emails = [e for e in valid_emails if e.is_corporate]
                if corporate_emails:
                    signals["has_corporate_email"] = True
                    score += 0.2

        if phones:
            signals["has_phone"] = True
            score += 0.1
            valid_phones = [p for p in phones if p.is_valid]
            if valid_phones:
                signals["has_valid_phone"] = True
                score += 0.1

        apply_urls = [c for c in contacts if c.type == ContactType.APPLICATION_URL]
        if apply_urls:
            signals["has_apply_url"] = True
            score += 0.1

        score = min(1.0, score)
        verification.contact_signals = signals

        for name, value in signals.items():
            self._add_signal(verification, "contact", name, 1.0 if value else 0.0, 1.0, {"value": value})

        return {"score": score, "signals": signals}

    async def _analyze_risk(self, job: Job, verification: JobVerification) -> Dict[str, Any]:
        signals = {}
        risk_score = 0.0

        desc_lower = job.description.lower()
        title_lower = job.title.lower()

        scam_keywords = {
            "registration_fee": ["registration fee", "security deposit", "processing fee", "joining fee"],
            "payment_before_join": ["pay before joining", "pay to join", "deposit required", "upfront payment"],
            "training_payment": ["pay for training", "paid training", "training fee", "buy training"],
            "equipment_payment": ["buy laptop", "pay for equipment", "equipment fee", "laptop deposit"],
            "guaranteed_job": ["guaranteed job", "100% placement", "assured job", "job guarantee"],
            "whatsapp_only": ["whatsapp only", "contact on whatsapp", "whatsapp interview"],
            "telegram_only": ["telegram only", "contact on telegram", "telegram interview"],
            "personal_info_request": ["send aadhaar", "send pan", "send passport", "send bank details", "send otp"],
            "crypto_investment": ["crypto", "bitcoin", "investment", "trading", "forex"],
            "unrealistic_salary": [],
            "suspicious_links": [],
        }

        for category, keywords in scam_keywords.items():
            found = [kw for kw in keywords if kw in desc_lower]
            if found:
                signals[category] = found
                risk_score += len(found) * 0.05
                for kw in found:
                    self._add_risk_event(job.id, category, "medium", f"Found suspicious keyword: {kw}", {"keyword": kw})

        if job.salary_min and job.salary_max:
            if job.salary_max > 5000000:
                signals["unrealistic_salary"] = True
                risk_score += 0.15
                self._add_risk_event(job.id, "unrealistic_salary", "high", f"Salary ₹{job.salary_max:,} seems unrealistic", {"salary_max": job.salary_max})

        if job.contacts:
            for contact in job.contacts:
                if contact.type == ContactType.EMAIL and contact.is_valid:
                    domain = contact.domain
                    if domain and self._is_suspicious_domain(domain):
                        signals["suspicious_email_domain"] = True
                        risk_score += 0.1
                        self._add_risk_event(job.id, "suspicious_email_domain", "medium", f"Suspicious email domain: {domain}", {"domain": domain})

                if contact.type == ContactType.WEBSITE or contact.type == ContactType.APPLICATION_URL:
                    if contact.value and self._is_suspicious_url(contact.value):
                        signals["suspicious_url"] = True
                        risk_score += 0.15
                        self._add_risk_event(job.id, "suspicious_url", "high", f"Suspicious application URL: {contact.value}", {"url": contact.value})

        if job.company and job.company.domain:
            corporate_emails = [c for c in job.contacts if c.type == ContactType.EMAIL and c.is_corporate]
            if corporate_emails:
                for email_contact in corporate_emails:
                    if email_contact.domain and email_contact.domain != job.company.domain:
                        signals["email_domain_mismatch"] = True
                        risk_score += 0.2
                        self._add_risk_event(job.id, "email_domain_mismatch", "high", f"Email domain {email_contact.domain} doesn't match company domain {job.company.domain}", {
                            "email_domain": email_contact.domain,
                            "company_domain": job.company.domain,
                        })

        risk_score = min(1.0, risk_score)

        if risk_score < 0.3:
            risk_level = RiskLevel.LOW
        elif risk_score < 0.6:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.HIGH

        signals["risk_level"] = risk_level.value
        verification.risk_signals = signals

        return {"score": risk_score, "risk_level": risk_level, "signals": signals}

    def _is_suspicious_domain(self, domain: str) -> bool:
        suspicious_tlds = [".xyz", ".top", ".club", ".online", ".site", ".space", ".website", ".cf", ".tk", ".ml", ".ga"]
        suspicious_keywords = ["temp", "fake", "disposable", "trash", "throwaway", "10minutemail", "guerrillamail"]
        domain_lower = domain.lower()
        return any(domain_lower.endswith(tld) for tld in suspicious_tlds) or any(kw in domain_lower for kw in suspicious_keywords)

    def _is_suspicious_url(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if self._is_suspicious_domain(domain):
                return True
            suspicious_patterns = [
                r"bit\.ly", r"tinyurl", r"short\.link", r"goo\.gl", r"t\.co",
                r"redirect", r"tracking", r"click", r"affiliate",
            ]
            return any(re.search(p, url, re.IGNORECASE) for p in suspicious_patterns)
        except Exception:
            return False