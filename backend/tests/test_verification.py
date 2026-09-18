import pytest
from app.services.verification import VerificationPipeline


def test_calculate_final_confidence():
    pipeline = VerificationPipeline(None)
    
    source = {"score": 0.9, "signals": {}}
    employer = {"score": 0.8, "signals": {}}
    uploader = {"score": 0.7, "signals": {}}
    content = {"score": 0.85, "signals": {}}
    contact = {"score": 0.9, "signals": {}}
    risk = {"score": 0.1, "risk_level": "low", "signals": {}}
    
    confidence = pipeline._calculate_final_confidence(
        source, employer, uploader, content, contact, risk
    )
    
    # Weights: source=0.15, employer=0.25, uploader=0.15, content=0.20, contact=0.15, risk=0.10
    expected = (
        0.9 * 0.15 + 0.8 * 0.25 + 0.7 * 0.15 + 
        0.85 * 0.20 + 0.9 * 0.15 + (1.0 - 0.1) * 0.10
    ) * 100
    
    assert abs(confidence - round(expected, 2)) < 0.01


def test_determine_status():
    pipeline = VerificationPipeline(None)
    
    # High confidence, low risk -> VERIFIED
    assert pipeline._determine_status(80, "low") == "verified"
    
    # Medium confidence, low risk -> VERIFIED
    assert pipeline._determine_status(70, "low") == "verified"
    
    # Medium confidence, low risk -> NEEDS_REVIEW
    assert pipeline._determine_status(60, "low") == "needs_review"
    
    # Low confidence -> UNABLE_TO_VERIFY
    assert pipeline._determine_status(30, "low") == "unable_to_verify"
    
    # High risk -> HIGH_RISK
    assert pipeline._determine_status(90, "high") == "high_risk"
    
    # Medium risk -> NEEDS_REVIEW
    assert pipeline._determine_status(80, "medium") == "needs_review"


def test_is_suspicious_domain():
    pipeline = VerificationPipeline(None)
    
    assert pipeline._is_suspicious_domain("temp.xyz") is True
    assert pipeline._is_suspicious_domain("fake.top") is True
    assert pipeline._is_suspicious_domain("legitimate.com") is False
    assert pipeline._is_suspicious_domain("company.org") is False
    assert pipeline._is_suspicious_domain("throwaway.ml") is True


def test_is_suspicious_url():
    pipeline = VerificationPipeline(None)
    
    assert pipeline._is_suspicious_url("http://bit.ly/abc") is True
    assert pipeline._is_suspicious_url("https://tinyurl.com/xyz") is True
    assert pipeline._is_suspicious_url("https://legitimate.com/apply") is False
    assert pipeline._is_suspicious_url("https://company.com/careers") is False