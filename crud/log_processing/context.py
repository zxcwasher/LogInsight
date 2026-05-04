from schemas.log_analysis import (
    ExtractedLogFields,
    RuleMetadataSnapshot,
    EventContext,
    IncidentContext,
)


LOG_LEVEL_PRIORITY = {
    "DEBUG": 10,
    "INFO": 20,
    "WARN": 30,
    "ERROR": 40,
    "CRITICAL": 50,
}


def build_rule_metadata_snapshot(matched_rule) -> RuleMetadataSnapshot:
    if not matched_rule:
        return RuleMetadataSnapshot()

    return RuleMetadataSnapshot(
        rule_id=getattr(matched_rule, "id", None),
        rule_key=getattr(matched_rule, "key", None),
        rule_version=getattr(matched_rule, "version", 1),
        rule_priority=getattr(matched_rule, "priority", None),
        rule_source=getattr(matched_rule, "source", None),
        rule_enabled=getattr(matched_rule, "enabled", None),
    )


def build_explanation(
    pattern_key: str | None,
    extracted_fields: ExtractedLogFields,
) -> list[str]:
    reasons = []

    items = [
        ("Matched pattern", pattern_key),
        ("log_level", extracted_fields.log_level),
        ("status_code", extracted_fields.status_code),
        ("exception_type", extracted_fields.exception_type),
    ]

    for label, value in items:
        if value is not None:
            reasons.append(f"{label}: {value}")

    if not reasons:
        reasons.append("no signals detected")

    return reasons


def calculate_confidence(
    pattern_key: str | None,
    extracted_fields: ExtractedLogFields,
) -> float:
    score = 0.0

    if pattern_key:
        score += 0.5

    if extracted_fields.log_level:
        score += 0.15

    if extracted_fields.status_code:
        score += 0.15

    if extracted_fields.exception_type:
        score += 0.2

    return min(score, 1.0)


def build_event_context(
    raw_log: str,
    rule_metadata: RuleMetadataSnapshot,
    extracted_fields: ExtractedLogFields,
    confidence: float,
    explanation: list[str],
) -> EventContext:
    return EventContext(
        raw_log=raw_log,
        matched_rule_key=rule_metadata.rule_key,
        matched_rule_version=rule_metadata.rule_version,
        log_level=extracted_fields.log_level,
        status_code=extracted_fields.status_code,
        exception_type=extracted_fields.exception_type,
        confidence=confidence,
        explanation=explanation,
    )


def update_incident_context(
    incident_context: IncidentContext | None,
    event_context: EventContext,
    service: str | None = None,
) -> IncidentContext:
    if incident_context is None:
        incident_context = IncidentContext()

    incident_context.event_count += 1

    if service:
        incident_context.primary_service = service

    if event_context.exception_type:
        incident_context.primary_error_type = event_context.exception_type

    if event_context.status_code:
        incident_context.last_status_code = event_context.status_code

    if event_context.log_level:
        current = incident_context.highest_log_level
        if current is None:
            incident_context.highest_log_level = event_context.log_level
        else:
            old_priority = LOG_LEVEL_PRIORITY.get(current, 0)
            new_priority = LOG_LEVEL_PRIORITY.get(event_context.log_level, 0)

            if new_priority > old_priority:
                incident_context.highest_log_level = event_context.log_level

    if event_context.confidence is not None:
        if incident_context.confidence_avg is None:
            incident_context.confidence_avg = event_context.confidence
        else:
            old_total = incident_context.confidence_avg * (incident_context.event_count - 1)
            incident_context.confidence_avg = (
                old_total + event_context.confidence
            ) / incident_context.event_count

    return incident_context