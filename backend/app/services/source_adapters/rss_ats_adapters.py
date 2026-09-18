import feedparser
from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx
from app.services.source_adapters import SourceAdapter, NormalizedJob, SourceHealth


class RSSAdapter(SourceAdapter):
    def __init__(self, config: Dict[str, Any], credentials: Optional[Dict[str, str]] = None):
        super().__init__(config, credentials)
        self.feed_url = config.get("feed_url")
        self.client = httpx.AsyncClient(timeout=30.0)

    async def connect(self) -> bool:
        if not self.feed_url:
            return False
        try:
            response = await self.client.get(self.feed_url)
            return response.status_code == 200
        except Exception:
            return False

    async def authenticate(self) -> bool:
        return True

    async def search_jobs(
        self,
        query: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[NormalizedJob]:
        if not self.feed_url:
            return []

        try:
            response = await self.client.get(self.feed_url)
            response.raise_for_status()
            feed = feedparser.parse(response.text)

            jobs = []
            for entry in feed.entries[offset:offset + limit]:
                job = self._parse_entry(entry)
                if job:
                    jobs.append(job)
            return jobs
        except Exception:
            return []

    async def get_job(self, source_job_id: str) -> Optional[NormalizedJob]:
        if not self.feed_url:
            return None

        try:
            response = await self.client.get(self.feed_url)
            response.raise_for_status()
            feed = feedparser.parse(response.text)

            for entry in feed.entries:
                if entry.get("id") == source_job_id or entry.get("link") == source_job_id:
                    return self._parse_entry(entry)
        except Exception:
            pass
        return None

    def _parse_entry(self, entry: Any) -> Optional[NormalizedJob]:
        title = entry.get("title", "").strip()
        if not title:
            return None

        description = entry.get("description", "") or entry.get("summary", "")
        link = entry.get("link", "")
        published = entry.get("published_parsed")
        posted_at = datetime(*published[:6]) if published else None

        company = None
        location = None
        for tag in entry.get("tags", []):
            term = tag.get("term", "").lower()
            if "company" in term or "employer" in term:
                company = tag.get("term")
            elif "location" in term or "city" in term:
                location = tag.get("term")

        return NormalizedJob(
            source=self.source_name,
            source_job_id=entry.get("id", link),
            source_url=link,
            title=title,
            company_name=company,
            description=description,
            location=location,
            employment_type=None,
            salary=None,
            posted_at=posted_at,
            expires_at=None,
            recruiter_name=None,
            emails=[],
            phone_numbers=[],
            apply_url=link,
            raw_source_metadata=dict(entry),
        )

    async def health_check(self) -> SourceHealth:
        try:
            if not self.feed_url:
                return SourceHealth(status="error", last_check=datetime.utcnow(), error="No feed URL configured")

            response = await self.client.get(self.feed_url)
            if response.status_code == 200:
                feed = feedparser.parse(response.text)
                return SourceHealth(
                    status="connected",
                    last_check=datetime.utcnow(),
                    rate_limit_remaining=len(feed.entries),
                )
            return SourceHealth(status="error", last_check=datetime.utcnow(), error=f"HTTP {response.status_code}")
        except Exception as e:
            return SourceHealth(status="error", last_check=datetime.utcnow(), error=str(e))

    async def close(self):
        await self.client.aclose()


class GreenhouseAdapter(SourceAdapter):
    def __init__(self, config: Dict[str, Any], credentials: Optional[Dict[str, str]] = None):
        super().__init__(config, credentials)
        self.board_token = config.get("board_token") or credentials.get("board_token")
        self.base_url = "https://boards-api.greenhouse.io/v1/boards"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def connect(self) -> bool:
        return bool(self.board_token)

    async def authenticate(self) -> bool:
        if not self.board_token:
            return False
        try:
            response = await self.client.get(f"{self.base_url}/{self.board_token}")
            return response.status_code == 200
        except Exception:
            return False

    async def search_jobs(self, **kwargs) -> List[NormalizedJob]:
        if not self.board_token:
            return []

        limit = kwargs.get("limit", 50)
        offset = kwargs.get("offset", 0)

        try:
            response = await self.client.get(
                f"{self.base_url}/{self.board_token}/jobs",
                params={"per_page": limit, "page": (offset // limit) + 1},
            )
            response.raise_for_status()
            data = response.json()

            jobs = []
            for job_data in data.get("jobs", []):
                jobs.append(self._parse_job(job_data))
            return jobs
        except Exception:
            return []

    async def get_job(self, source_job_id: str) -> Optional[NormalizedJob]:
        if not self.board_token:
            return None

        try:
            response = await self.client.get(f"{self.base_url}/{self.board_token}/jobs/{source_job_id}")
            if response.status_code == 200:
                return self._parse_job(response.json())
        except Exception:
            pass
        return None

    def _parse_job(self, job_data: Dict[str, Any]) -> NormalizedJob:
        return NormalizedJob(
            source="greenhouse",
            source_job_id=str(job_data.get("id")),
            source_url=job_data.get("absolute_url", ""),
            title=job_data.get("title", ""),
            company_name=job_data.get("company_name"),
            description=job_data.get("content", ""),
            location=job_data.get("location", {}).get("name") if job_data.get("location") else None,
            employment_type=job_data.get("employment_type"),
            salary=None,
            posted_at=self._parse_date(job_data.get("updated_at")),
            expires_at=None,
            recruiter_name=None,
            emails=[],
            phone_numbers=[],
            apply_url=job_data.get("absolute_url"),
            raw_source_metadata=job_data,
        )

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            return None

    async def health_check(self) -> SourceHealth:
        try:
            if not self.board_token:
                return SourceHealth(status="requires_authorization", last_check=datetime.utcnow(), error="Board token not configured")

            response = await self.client.get(f"{self.base_url}/{self.board_token}")
            if response.status_code == 200:
                return SourceHealth(status="connected", last_check=datetime.utcnow())
            return SourceHealth(status="error", last_check=datetime.utcnow(), error=f"HTTP {response.status_code}")
        except Exception as e:
            return SourceHealth(status="error", last_check=datetime.utcnow(), error=str(e))

    async def close(self):
        await self.client.aclose()


class LeverAdapter(SourceAdapter):
    def __init__(self, config: Dict[str, Any], credentials: Optional[Dict[str, str]] = None):
        super().__init__(config, credentials)
        self.company = config.get("company") or credentials.get("company")
        self.base_url = f"https://api.lever.co/v0/postings/{self.company}"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def connect(self) -> bool:
        return bool(self.company)

    async def authenticate(self) -> bool:
        if not self.company:
            return False
        try:
            response = await self.client.get(self.base_url, params={"mode": "json"})
            return response.status_code == 200
        except Exception:
            return False

    async def search_jobs(self, **kwargs) -> List[NormalizedJob]:
        if not self.company:
            return []

        limit = kwargs.get("limit", 50)
        offset = kwargs.get("offset", 0)

        try:
            response = await self.client.get(
                self.base_url,
                params={"mode": "json", "limit": limit, "offset": offset},
            )
            response.raise_for_status()
            jobs_data = response.json()

            jobs = []
            for job_data in jobs_data:
                jobs.append(self._parse_job(job_data))
            return jobs
        except Exception:
            return []

    async def get_job(self, source_job_id: str) -> Optional[NormalizedJob]:
        if not self.company:
            return None

        try:
            response = await self.client.get(f"{self.base_url}/{source_job_id}", params={"mode": "json"})
            if response.status_code == 200:
                return self._parse_job(response.json())
        except Exception:
            pass
        return None

    def _parse_job(self, job_data: Dict[str, Any]) -> NormalizedJob:
        return NormalizedJob(
            source="lever",
            source_job_id=job_data.get("id", ""),
            source_url=job_data.get("hostedUrl", ""),
            title=job_data.get("text", ""),
            company_name=self.company,
            description=job_data.get("descriptionPlain", ""),
            location=job_data.get("categories", {}).get("location"),
            employment_type=job_data.get("categories", {}).get("commitment"),
            salary=None,
            posted_at=self._parse_date(job_data.get("createdAt")),
            expires_at=None,
            recruiter_name=None,
            emails=[],
            phone_numbers=[],
            apply_url=job_data.get("applyUrl") or job_data.get("hostedUrl"),
            raw_source_metadata=job_data,
        )

    def _parse_date(self, timestamp: Optional[int]) -> Optional[datetime]:
        if not timestamp:
            return None
        try:
            return datetime.fromtimestamp(timestamp / 1000)
        except Exception:
            return None

    async def health_check(self) -> SourceHealth:
        try:
            if not self.company:
                return SourceHealth(status="requires_authorization", last_check=datetime.utcnow(), error="Company not configured")

            response = await self.client.get(self.base_url, params={"mode": "json"})
            if response.status_code == 200:
                return SourceHealth(status="connected", last_check=datetime.utcnow())
            return SourceHealth(status="error", last_check=datetime.utcnow(), error=f"HTTP {response.status_code}")
        except Exception as e:
            return SourceHealth(status="error", last_check=datetime.utcnow(), error=str(e))

    async def close(self):
        await self.client.aclose()