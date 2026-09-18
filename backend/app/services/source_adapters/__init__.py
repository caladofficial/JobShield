from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from pydantic import HttpUrl


@dataclass
class NormalizedJob:
    source: str
    source_job_id: Optional[str]
    source_url: str
    title: str
    company_name: Optional[str]
    description: str
    location: Optional[str]
    employment_type: Optional[str]
    salary: Optional[Dict[str, Any]]
    posted_at: Optional[datetime]
    expires_at: Optional[datetime]
    recruiter_name: Optional[str]
    emails: List[Dict[str, Any]]
    phone_numbers: List[Dict[str, Any]]
    apply_url: Optional[str]
    raw_source_metadata: Dict[str, Any]


@dataclass
class SourceHealth:
    status: str
    last_check: datetime
    error: Optional[str] = None
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset_at: Optional[datetime] = None


class SourceAdapter(ABC):
    def __init__(self, config: Dict[str, Any], credentials: Optional[Dict[str, str]] = None):
        self.config = config
        self.credentials = credentials or {}
        self.source_name = self.__class__.__name__.replace("Adapter", "").lower()

    @abstractmethod
    async def connect(self) -> bool:
        pass

    @abstractmethod
    async def authenticate(self) -> bool:
        pass

    @abstractmethod
    async def search_jobs(
        self,
        query: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[NormalizedJob]:
        pass

    @abstractmethod
    async def get_job(self, source_job_id: str) -> Optional[NormalizedJob]:
        pass

    @abstractmethod
    async def health_check(self) -> SourceHealth:
        pass

    async def normalize_job(self, raw_job: Dict[str, Any]) -> NormalizedJob:
        return NormalizedJob(
            source=self.source_name,
            source_job_id=raw_job.get("source_job_id"),
            source_url=raw_job.get("source_url", ""),
            title=raw_job.get("title", ""),
            company_name=raw_job.get("company_name"),
            description=raw_job.get("description", ""),
            location=raw_job.get("location"),
            employment_type=raw_job.get("employment_type"),
            salary=raw_job.get("salary"),
            posted_at=raw_job.get("posted_at"),
            expires_at=raw_job.get("expires_at"),
            recruiter_name=raw_job.get("recruiter_name"),
            emails=raw_job.get("emails", []),
            phone_numbers=raw_job.get("phone_numbers", []),
            apply_url=raw_job.get("apply_url"),
            raw_source_metadata=raw_job,
        )