import re
from typing import Optional, List, Dict, Any
from datetime import datetime
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
from app.services.source_adapters import SourceAdapter, NormalizedJob, SourceHealth


class ManualURLAdapter(SourceAdapter):
    def __init__(self, config: Dict[str, Any], credentials: Optional[Dict[str, str]] = None):
        super().__init__(config, credentials)
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)

    async def connect(self) -> bool:
        return True

    async def authenticate(self) -> bool:
        return True

    async def search_jobs(
        self,
        query: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[NormalizedJob]:
        return []

    async def get_job(self, source_job_id: str) -> Optional[NormalizedJob]:
        if not source_job_id.startswith("http"):
            return None

        try:
            response = await self.client.get(source_job_id)
            response.raise_for_status()
            html = response.text
            return await self._extract_job_from_html(html, source_job_id)
        except Exception as e:
            return NormalizedJob(
                source=self.source_name,
                source_job_id=source_job_id,
                source_url=source_job_id,
                title="Unable to fetch",
                company_name=None,
                description=f"Error fetching URL: {str(e)}",
                location=None,
                employment_type=None,
                salary=None,
                posted_at=None,
                expires_at=None,
                recruiter_name=None,
                emails=[],
                phone_numbers=[],
                apply_url=None,
                raw_source_metadata={"error": str(e)},
            )

    async def _extract_job_from_html(self, html: str, url: str) -> NormalizedJob:
        soup = BeautifulSoup(html, "html.parser")

        title = self._extract_title(soup)
        company = self._extract_company(soup)
        description = self._extract_description(soup)
        location = self._extract_location(soup)
        emails = self._extract_emails(html)
        phones = self._extract_phones(html)
        apply_url = self._extract_apply_url(soup, url)

        return NormalizedJob(
            source=self.source_name,
            source_job_id=url,
            source_url=url,
            title=title or "Unknown Title",
            company_name=company,
            description=description or "",
            location=location,
            employment_type=None,
            salary=None,
            posted_at=None,
            expires_at=None,
            recruiter_name=None,
            emails=[{"value": e, "type": "email"} for e in emails],
            phone_numbers=[{"value": p, "type": "phone"} for p in phones],
            apply_url=apply_url,
            raw_source_metadata={"html_length": len(html)},
        )

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        selectors = [
            "h1.job-title",
            "h1[data-testid='job-title']",
            ".job-title h1",
            "h1.title",
            "h1",
            "title",
        ]
        for sel in selectors:
            el = soup.select_one(sel)
            if el and el.get_text(strip=True):
                return el.get_text(strip=True)
        return None

    def _extract_company(self, soup: BeautifulSoup) -> Optional[str]:
        selectors = [
            "[data-testid='company-name']",
            ".company-name",
            ".employer-name",
            "[itemprop='hiringOrganization']",
            ".job-company",
        ]
        for sel in selectors:
            el = soup.select_one(sel)
            if el and el.get_text(strip=True):
                return el.get_text(strip=True)
        return None

    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        selectors = [
            "[data-testid='job-description']",
            ".job-description",
            "#job-description",
            "[itemprop='description']",
            ".description",
            "main",
        ]
        for sel in selectors:
            el = soup.select_one(sel)
            if el:
                return el.get_text("\n", strip=True)
        return soup.get_text("\n", strip=True)[:10000]

    def _extract_location(self, soup: BeautifulSoup) -> Optional[str]:
        selectors = [
            "[data-testid='job-location']",
            ".job-location",
            "[itemprop='jobLocation']",
            ".location",
        ]
        for sel in selectors:
            el = soup.select_one(sel)
            if el and el.get_text(strip=True):
                return el.get_text(strip=True)
        return None

    def _extract_emails(self, html: str) -> List[str]:
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        emails = re.findall(email_pattern, html)
        return list(set(e.lower() for e in emails if not self._is_tracking_email(e)))

    def _extract_phones(self, html: str) -> List[str]:
        phone_pattern = r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
        phones = re.findall(phone_pattern, html)
        return list(set("".join(p) if isinstance(p, tuple) else p for p in phones))

    def _extract_apply_url(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        selectors = [
            "a[data-testid='apply-button']",
            ".apply-button a",
            "a.apply-now",
            "a[href*='apply']",
        ]
        for sel in selectors:
            el = soup.select_one(sel)
            if el and el.get("href"):
                href = el["href"]
                if href.startswith("http"):
                    return href
                from urllib.parse import urljoin
                return urljoin(base_url, href)
        return None

    def _is_tracking_email(self, email: str) -> bool:
        tracking_domains = [
            "tracking", "analytics", "metrics", "pixel", "beacon",
            "noreply", "no-reply", "donotreply", "bounce",
        ]
        domain = email.split("@")[-1].lower()
        return any(t in domain for t in tracking_domains)

    async def health_check(self) -> SourceHealth:
        return SourceHealth(status="connected", last_check=datetime.utcnow())

    async def close(self):
        await self.client.aclose()


class UnavailableAdapter(SourceAdapter):
    def __init__(self, config: Dict[str, Any], credentials: Optional[Dict[str, str]] = None):
        super().__init__(config, credentials)

    async def connect(self) -> bool:
        return False

    async def authenticate(self) -> bool:
        return False

    async def search_jobs(self, **kwargs) -> List[NormalizedJob]:
        return []

    async def get_job(self, source_job_id: str) -> Optional[NormalizedJob]:
        return None

    async def health_check(self) -> SourceHealth:
        return SourceHealth(
            status="requires_authorization",
            last_check=datetime.utcnow(),
            error="This source requires authorized API access. Please connect using approved credentials.",
        )


ADAPTER_REGISTRY = {
    "manual": ManualURLAdapter,
    "unavailable": UnavailableAdapter,
}


def get_adapter(source_name: str, config: Dict[str, Any], credentials: Optional[Dict[str, str]] = None) -> SourceAdapter:
    adapter_class = ADAPTER_REGISTRY.get(source_name.lower())
    if not adapter_class:
        return UnavailableAdapter(config, credentials)
    return adapter_class(config, credentials)