import pytest
from app.models import User, Source, Job, JobStatus, RiskLevel


def test_user_model():
    user = User(
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User",
    )
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.role.value == "user"
    assert user.is_active is True


def test_source_model():
    source = Source(
        name="greenhouse",
        display_name="Greenhouse",
        adapter_class="GreenhouseAdapter",
    )
    assert source.name == "greenhouse"
    assert source.display_name == "Greenhouse"
    assert source.requires_authorization is False


def test_job_status_enum():
    assert JobStatus.NEW.value == "new"
    assert JobStatus.VERIFIED.value == "verified"
    assert JobStatus.HIGH_RISK.value == "high_risk"


def test_risk_level_enum():
    assert RiskLevel.LOW.value == "low"
    assert RiskLevel.MEDIUM.value == "medium"
    assert RiskLevel.HIGH.value == "high"
    assert RiskLevel.UNKNOWN.value == "unknown"