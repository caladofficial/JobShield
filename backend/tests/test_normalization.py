import pytest
from app.services.normalization import NormalizationEngine
from app.services.source_adapters import NormalizedJob
from datetime import datetime


@pytest.fixture
def sample_normalized_job():
    return NormalizedJob(
        source="manual",
        source_job_id="test-123",
        source_url="https://example.com/job/123",
        title="Software Engineer",
        company_name="Test Company",
        description="We are looking for a software engineer...",
        location="Bangalore, India",
        employment_type="Full-time",
        salary={"min": 1000000, "max": 2000000, "currency": "INR"},
        posted_at=datetime.now(),
        expires_at=None,
        recruiter_name="John Recruiter",
        emails=[{"value": "hr@testcompany.com", "type": "email"}],
        phone_numbers=[{"value": "+91 98765 43210", "type": "phone"}],
        apply_url="https://example.com/apply/123",
        raw_source_metadata={},
    )


def test_normalize_company_name():
    engine = NormalizationEngine(None)
    
    assert engine._normalize_company_name("Test Company Inc.") == "test company"
    assert engine._normalize_company_name("ABC Technologies Pvt Ltd") == "abc technologies"
    assert engine._normalize_company_name("  Multiple   Spaces  ") == "multiple spaces"


def test_validate_email():
    engine = NormalizationEngine(None)
    
    assert engine._validate_email("test@example.com") is True
    assert engine._validate_email("hr@company.org") is True
    assert engine._validate_email("invalid-email") is False
    assert engine._validate_email("@nodomain.com") is False
    assert engine._validate_email("no@domain") is False


def test_classify_email():
    engine = NormalizationEngine(None)
    
    is_corp, domain = engine._classify_email("hr@company.com")
    assert is_corp is True
    assert domain == "company.com"
    
    is_corp, domain = engine._classify_email("recruiter@gmail.com")
    assert is_corp is False
    assert domain == "gmail.com"


def test_hash_description():
    engine = NormalizationEngine(None)
    
    hash1 = engine._hash_description("Test description")
    hash2 = engine._hash_description("Test description")
    hash3 = engine._hash_description("Different description")
    
    assert hash1 == hash2
    assert hash1 != hash3
    assert len(hash1) == 64  # SHA256 hex length