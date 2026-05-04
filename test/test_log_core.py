from types import SimpleNamespace

from crud.analysis.service import build_analysis_result
from crud.log_processing.context import (
    build_rule_metadata_snapshot,
    build_explanation,
    calculate_confidence,
    build_event_context,
    update_incident_context,
)
from crud.log_processing.extractos import extract_log_fields
from schemas.log_analysis import ExtractedLogFields, IncidentContext


def test_extract_info_log_without_error_signals():
    raw_log = "INFO payment-service started successfully"

    result = extract_log_fields(raw_log)

    assert result.log_level == "INFO"
    assert result.status_code is None
    assert result.exception_type is None


def test_extract_http_status_from_http_format():
    raw_log = "ERROR gateway HTTP 502 Bad Gateway"

    result = extract_log_fields(raw_log)

    assert result.log_level == "ERROR"
    assert result.status_code == 502


def test_extract_status_code_from_response_format():
    raw_log = "WARN api response=404 user not found"

    result = extract_log_fields(raw_log)

    assert result.log_level == "WARN"
    assert result.status_code == 404


def test_extract_exception_from_caused_by():
    raw_log = "ERROR job failed caused by ConnectionRefusedError"

    result = extract_log_fields(raw_log)

    assert result.exception_type == "ConnectionRefusedError"


def test_extract_exception_from_text_hint_timeout():
    raw_log = "ERROR request timed out while calling payment service"

    result = extract_log_fields(raw_log)

    assert result.exception_type == "TimeoutError"


def test_build_analysis_result_when_no_rule_matched():
    raw_log = "INFO service started"

    result = build_analysis_result(raw_log, matched_rule=None)

    assert result["matched"] is False
    assert result["pattern_key"] == "unknown"
    assert result["severity"] == "low"
    assert result["category"] == "unknown"
    assert result["service"] == "unknown"
    assert result["raw_log"] == raw_log


def test_build_analysis_result_when_rule_matched():
    raw_log = "ERROR payment status=500 TimeoutError"

    matched_rule = SimpleNamespace(
        id=1,
        key="payment_timeout",
        severity="high",
        message="Payment service timeout",
        category="payment",
        service="payment-service",
    )

    result = build_analysis_result(raw_log, matched_rule)

    assert result["matched"] is True
    assert result["pattern_id"] == 1
    assert result["pattern_key"] == "payment_timeout"
    assert result["severity"] == "high"
    assert result["message"] == "Payment service timeout"
    assert result["category"] == "payment"
    assert result["service"] == "payment-service"


def test_build_rule_metadata_snapshot_without_rule():
    result = build_rule_metadata_snapshot(None)

    assert result.rule_id is None
    assert result.rule_key is None
    assert result.rule_version is None


def test_build_rule_metadata_snapshot_with_rule():
    matched_rule = SimpleNamespace(
        id=10,
        key="db_down",
        version=2,
        priority=100,
        source="system",
        enabled=True,
    )

    result = build_rule_metadata_snapshot(matched_rule)

    assert result.rule_id == 10
    assert result.rule_key == "db_down"
    assert result.rule_version == 2
    assert result.rule_priority == 100
    assert result.rule_source == "system"
    assert result.rule_enabled is True


def test_build_explanation_with_all_signals():
    fields = ExtractedLogFields(
        log_level="ERROR",
        status_code=500,
        exception_type="TimeoutError",
    )

    result = build_explanation(
        pattern_key="payment_timeout",
        extracted_fields=fields,
    )

    assert "Matched pattern: payment_timeout" in result
    assert "log_level: ERROR" in result
    assert "status_code: 500" in result
    assert "exception_type: TimeoutError" in result


def test_build_explanation_without_signals():
    fields = ExtractedLogFields()

    result = build_explanation(
        pattern_key=None,
        extracted_fields=fields,
    )

    assert result == ["no signals detected"]


def test_calculate_confidence_only_pattern():
    fields = ExtractedLogFields()

    result = calculate_confidence(
        pattern_key="some_pattern",
        extracted_fields=fields,
    )

    assert result == 0.5


def test_calculate_confidence_all_signals():
    fields = ExtractedLogFields(
        log_level="ERROR",
        status_code=500,
        exception_type="TimeoutError",
    )

    result = calculate_confidence(
        pattern_key="payment_timeout",
        extracted_fields=fields,
    )

    assert result == 1.0


def test_build_event_context():
    raw_log = "ERROR payment status=500 TimeoutError"

    matched_rule = SimpleNamespace(
        id=1,
        key="payment_timeout",
        version=3,
        priority=100,
        source="system",
        enabled=True,
    )

    rule_metadata = build_rule_metadata_snapshot(matched_rule)

    fields = ExtractedLogFields(
        log_level="ERROR",
        status_code=500,
        exception_type="TimeoutError",
    )

    explanation = build_explanation(
        pattern_key=rule_metadata.rule_key,
        extracted_fields=fields,
    )

    event_context = build_event_context(
        raw_log=raw_log,
        rule_metadata=rule_metadata,
        extracted_fields=fields,
        confidence=1.0,
        explanation=explanation,
    )

    assert event_context.raw_log == raw_log
    assert event_context.matched_rule_key == "payment_timeout"
    assert event_context.matched_rule_version == 3
    assert event_context.log_level == "ERROR"
    assert event_context.status_code == 500
    assert event_context.exception_type == "TimeoutError"
    assert event_context.confidence == 1.0


def test_update_incident_context_first_event():
    raw_log = "ERROR payment status=500 TimeoutError"

    fields = extract_log_fields(raw_log)

    event_context = build_event_context(
        raw_log=raw_log,
        rule_metadata=build_rule_metadata_snapshot(None),
        extracted_fields=fields,
        confidence=0.5,
        explanation=["test"],
    )

    incident_context = update_incident_context(
        incident_context=None,
        event_context=event_context,
        service="payment-service",
    )

    assert incident_context.event_count == 1
    assert incident_context.primary_service == "payment-service"
    assert incident_context.primary_error_type == "TimeoutError"
    assert incident_context.highest_log_level == "ERROR"
    assert incident_context.last_status_code == 500
    assert incident_context.confidence_avg == 0.5


def test_update_incident_context_second_event_updates_average_confidence():
    incident_context = IncidentContext(
        event_count=1,
        confidence_avg=0.5,
        highest_log_level="WARN",
    )

    raw_log = "CRITICAL database HTTP 503 ConnectionRefusedError"

    fields = extract_log_fields(raw_log)

    event_context = build_event_context(
        raw_log=raw_log,
        rule_metadata=build_rule_metadata_snapshot(None),
        extracted_fields=fields,
        confidence=1.0,
        explanation=["test"],
    )

    result = update_incident_context(
        incident_context=incident_context,
        event_context=event_context,
        service="database",
    )

    assert result.event_count == 2
    assert result.confidence_avg == 0.75
    assert result.highest_log_level == "CRITICAL"
    assert result.primary_service == "database"
    assert result.primary_error_type == "ConnectionRefusedError"
    assert result.last_status_code == 503


def test_update_incident_context_does_not_replace_higher_log_level_with_lower():
    incident_context = IncidentContext(
        event_count=1,
        confidence_avg=1.0,
        highest_log_level="ERROR",
    )

    raw_log = "WARN api response=404"

    fields = extract_log_fields(raw_log)

    event_context = build_event_context(
        raw_log=raw_log,
        rule_metadata=build_rule_metadata_snapshot(None),
        extracted_fields=fields,
        confidence=0.3,
        explanation=["test"],
    )

    result = update_incident_context(
        incident_context=incident_context,
        event_context=event_context,
        service="api",
    )

    assert result.event_count == 2
    assert result.highest_log_level == "ERROR"
    assert result.last_status_code == 404