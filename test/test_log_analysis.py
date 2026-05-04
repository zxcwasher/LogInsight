from crud.log_processing.extractos import extract_log_fields
from crud.log_processing.context import calculate_confidence, update_incident_context
from schemas.log_analysis import ExtractedLogFields, EventContext, IncidentContext


def test_extract_log_fields_from_error_log():
    raw_log = "ERROR payment-service status=500 exception=TimeoutError"

    result = extract_log_fields(raw_log)

    assert result.log_level == "ERROR"
    assert result.status_code == 500
    assert result.exception_type == "TimeoutError"


def test_extract_warning_is_normalized_to_warn():
    raw_log = "WARNING api response=404"

    result = extract_log_fields(raw_log)

    assert result.log_level == "WARN"
    assert result.status_code == 404


def test_extract_fatal_is_normalized_to_error():
    raw_log = "FATAL database ConnectionRefusedError"

    result = extract_log_fields(raw_log)

    assert result.log_level == "ERROR"
    assert result.exception_type == "ConnectionRefusedError"


def test_confidence_with_all_signals():
    fields = ExtractedLogFields(
        log_level="ERROR",
        status_code=500,
        exception_type="TimeoutError",
    )

    result = calculate_confidence(
        pattern_key="db_timeout",
        extracted_fields=fields,
    )

    assert result == 1.0


def test_confidence_without_pattern_but_with_log_level():
    fields = ExtractedLogFields(
        log_level="ERROR",
        status_code=None,
        exception_type=None,
    )

    result = calculate_confidence(
        pattern_key=None,
        extracted_fields=fields,
    )

    assert result == 0.15


def test_update_incident_context_first_event():
    event_context = EventContext(
        raw_log="ERROR api status=500 TimeoutError",
        log_level="ERROR",
        status_code=500,
        exception_type="TimeoutError",
        confidence=1.0,
    )

    result = update_incident_context(
        incident_context=None,
        event_context=event_context,
        service="api",
    )

    assert result.event_count == 1
    assert result.primary_service == "api"
    assert result.primary_error_type == "TimeoutError"
    assert result.highest_log_level == "ERROR"
    assert result.last_status_code == 500
    assert result.confidence_avg == 1.0


def test_update_incident_context_keeps_highest_log_level():
    incident_context = IncidentContext(
        highest_log_level="WARN",
        event_count=1,
        confidence_avg=0.5,
    )

    event_context = EventContext(
        raw_log="CRITICAL database down",
        log_level="CRITICAL",
        status_code=503,
        exception_type="ConnectionRefusedError",
        confidence=1.0,
    )

    result = update_incident_context(
        incident_context=incident_context,
        event_context=event_context,
        service="database",
    )

    assert result.event_count == 2
    assert result.highest_log_level == "CRITICAL"
    assert result.last_status_code == 503
    assert result.primary_error_type == "ConnectionRefusedError"
    assert result.confidence_avg == 0.75