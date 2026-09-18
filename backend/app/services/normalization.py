import hashlib
import re
from typing import Optional, List, Dict, Any
from datetime import datetime
import phonenumbers
from phonenumbers import NumberParseException
from app.services.source_adapters import NormalizedJob
from app.models import Job, Company, Recruiter, JobContact, ContactType, VerificationStatus, JobStatus
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class NormalizationEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def normalize_and_store(self, normalized_job: NormalizedJob, user_id: int, source_id: int) -> Job:
        description_hash = self._hash_description(normalized_job.description)

        existing_job = await self._find_existing_job(source_id, normalized_job.source_job_id, description_hash)
        if existing_job:
            return await self._update_job(existing_job, normalized_job)

        company = await self._get_or_create_company(normalized_job)
        recruiter = await self._get_or_create_recruiter(normalized_job, company.id if company else None, source_id)

        job = Job(
            user_id=user_id,
            source_id=source_id,
            source_job_id=normalized_job.source_job_id,
            source_url=normalized_job.source_url,
            title=normalized_job.title,
            company_id=company.id if company else None,
            description=normalized_job.description,
            description_hash=description_hash,
            location=normalized_job.location,
            employment_type=normalized_job.employment_type,
            salary_min=normalized_job.salary.get("min") if normalized_job.salary else None,
            salary_max=normalized_job.salary.get("max") if normalized_job.salary else None,
            currency=normalized_job.salary.get("currency", "INR") if normalized_job.salary else "INR",
            posted_at=normalized_job.posted_at,
            expires_at=normalized_job.expires_at,
            recruiter_id=recruiter.id if recruiter else None,
            apply_url=normalized_job.apply_url,
            status=JobStatus.NEW,
            raw_source_metadata=normalized_job.raw_source_metadata,
        )

        self.db.add(job)
        await self.db.flush()

        await self._extract_and_store_contacts(job, normalized_job)

        return job

    def _hash_description(self, description: str) -> str:
        return hashlib.sha256(description.encode()).hexdigest()

    async def _find_existing_job(self, source_id: int, source_job_id: Optional[str], description_hash: str) -> Optional[Job]:
        if source_job_id:
            stmt = select(Job).where(Job.source_id == source_id, Job.source_job_id == source_job_id)
            result = await self.db.execute(stmt)
            job = result.scalar_one_or_none()
            if job:
                return job

        stmt = select(Job).where(Job.description_hash == description_hash)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _update_job(self, job: Job, normalized_job: NormalizedJob) -> Job:
        job.title = normalized_job.title
        job.description = normalized_job.description
        job.location = normalized_job.location
        job.employment_type = normalized_job.employment_type
        if normalized_job.salary:
            job.salary_min = normalized_job.salary.get("min")
            job.salary_max = normalized_job.salary.get("max")
            job.currency = normalized_job.salary.get("currency", "INR")
        job.posted_at = normalized_job.posted_at
        job.expires_at = normalized_job.expires_at
        job.apply_url = normalized_job.apply_url
        job.raw_source_metadata = normalized_job.raw_source_metadata
        job.updated_at = datetime.utcnow()

        await self._extract_and_store_contacts(job, normalized_job)
        return job

    async def _get_or_create_company(self, normalized_job: NormalizedJob) -> Optional[Company]:
        if not normalized_job.company_name:
            return None

        normalized_name = self._normalize_company_name(normalized_job.company_name)
        domain = self._extract_domain(normalized_job.company_name, normalized_job.source_url)

        stmt = select(Company).where(Company.normalized_name == normalized_name)
        result = await self.db.execute(stmt)
        company = result.scalar_one_or_none()

        if not company:
            company = Company(
                name=normalized_job.company_name,
                normalized_name=normalized_name,
                domain=domain,
                website=self._guess_website(domain) if domain else None,
            )
            self.db.add(company)
            await self.db.flush()
        else:
            if domain and not company.domain:
                company.domain = domain
            if not company.website and domain:
                company.website = self._guess_website(domain)

        return company

    def _normalize_company_name(self, name: str) -> str:
        name = re.sub(r"\s+", " ", name.strip().lower())
        name = re.sub(r"[^\w\s]", "", name)
        suffixes = ["inc", "llc", "ltd", "corp", "corporation", "company", "co", "pvt", "private", "limited"]
        for suffix in suffixes:
            name = re.sub(rf"\b{suffix}\b", "", name)
        return " ".join(name.split())

    def _extract_domain(self, company_name: str, source_url: str) -> Optional[str]:
        try:
            parsed = urlparse(source_url)
            domain = parsed.netloc.lower().replace("www.", "")
            if domain and not any(x in domain for x in ["linkedin", "indeed", "naukri", "glassdoor", "greenhouse", "lever"]):
                return domain
        except Exception:
            pass
        return None

    def _guess_website(self, domain: str) -> str:
        if not domain.startswith("http"):
            return f"https://{domain}"
        return domain

    async def _get_or_create_recruiter(
        self, normalized_job: NormalizedJob, company_id: Optional[int], source_id: int
    ) -> Optional[Recruiter]:
        if not normalized_job.recruiter_name and not normalized_job.emails:
            return None

        email = normalized_job.emails[0].get("value") if normalized_job.emails else None

        stmt = select(Recruiter).where(
            Recruiter.company_id == company_id,
            Recruiter.source_id == source_id,
        )
        if email:
            stmt = stmt.where(Recruiter.email == email)
        elif normalized_job.recruiter_name:
            stmt = stmt.where(Recruiter.name == normalized_job.recruiter_name)

        result = await self.db.execute(stmt)
        recruiter = result.scalar_one_or_none()

        if not recruiter:
            recruiter = Recruiter(
                company_id=company_id,
                source_id=source_id,
                name=normalized_job.recruiter_name,
                email=email,
            )
            self.db.add(recruiter)
            await self.db.flush()
        else:
            if normalized_job.recruiter_name and not recruiter.name:
                recruiter.name = normalized_job.recruiter_name
            if email and not recruiter.email:
                recruiter.email = email

        return recruiter

    async def _extract_and_store_contacts(self, job: Job, normalized_job: NormalizedJob):
        await self._store_emails(job, normalized_job.emails)
        await self._store_phones(job, normalized_job.phone_numbers)
        if normalized_job.apply_url:
            await self._store_contact(job, ContactType.APPLICATION_URL, normalized_job.apply_url, normalized_job.apply_url)

    async def _store_emails(self, job: Job, emails: List[Dict[str, Any]]):
        seen = set()
        for email_data in emails:
            email = email_data.get("value", "").lower().strip()
            if not email or email in seen:
                continue
            seen.add(email)

            is_valid = self._validate_email(email)
            is_corporate, domain = self._classify_email(email)

            await self._store_contact(
                job,
                ContactType.EMAIL,
                email,
                email,
                is_valid=is_valid,
                is_corporate=is_corporate,
                domain=domain,
                confidence=0.9 if is_valid else 0.3,
                verification_method="regex_syntax" if is_valid else "none",
            )

    async def _store_phones(self, job: Job, phones: List[Dict[str, Any]]):
        seen = set()
        for phone_data in phones:
            phone = phone_data.get("value", "").strip()
            if not phone or phone in seen:
                continue
            seen.add(phone)

            normalized, is_valid, country = self._normalize_phone(phone)

            if normalized in seen:
                continue
            seen.add(normalized)

            await self._store_contact(
                job,
                ContactType.PHONE,
                phone,
                normalized,
                is_valid=is_valid,
                domain=country,
                confidence=0.9 if is_valid else 0.3,
                verification_method="libphonenumber" if is_valid else "none",
            )

    async def _store_contact(
        self,
        job: Job,
        contact_type: ContactType,
        value: str,
        normalized_value: str,
        is_valid: bool = False,
        is_corporate: bool = False,
        domain: Optional[str] = None,
        confidence: float = 0.0,
        verification_method: Optional[str] = None,
    ):
        stmt = select(JobContact).where(
            JobContact.job_id == job.id,
            JobContact.type == contact_type,
            JobContact.normalized_value == normalized_value,
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.is_valid = is_valid
            existing.is_corporate = is_corporate
            existing.domain = domain
            existing.confidence = max(existing.confidence, confidence)
            existing.verification_method = verification_method
        else:
            contact = JobContact(
                job_id=job.id,
                type=contact_type,
                value=value,
                normalized_value=normalized_value,
                is_valid=is_valid,
                is_corporate=is_corporate,
                domain=domain,
                confidence=confidence,
                verification_method=verification_method,
                verification_status=VerificationStatus.VERIFIED if is_valid else VerificationStatus.PENDING,
            )
            self.db.add(contact)

    def _validate_email(self, email: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def _classify_email(self, email: str) -> tuple[bool, str]:
        domain = email.split("@")[-1].lower()
        free_domains = {
            "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com",
            "icloud.com", "protonmail.com", "zoho.com", "yandex.com", "mail.ru",
            "live.com", "msn.com", "rediffmail.com", "in.com",
        }
        is_corporate = domain not in free_domains
        return is_corporate, domain

    def _normalize_phone(self, phone: str) -> tuple[str, bool, Optional[str]]:
        try:
            parsed = phonenumbers.parse(phone, None)
            if phonenumbers.is_valid_number(parsed):
                normalized = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                country = phonenumbers.region_code_for_number(parsed)
                return normalized, True, country
            else:
                normalized = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                country = phonenumbers.region_code_for_number(parsed)
                return normalized, False, country
        except NumberParseException:
            digits = re.sub(r"\D", "", phone)
            if len(digits) >= 10:
                return f"+{digits}", False, None
            return phone, False, None