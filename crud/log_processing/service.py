from datetime import datetime
from types import SimpleNamespace

from crud.analysis.repository import get_active_patterns
from crud.analysis.service import match_pattern, build_analysis_result

from crud.event.service import create_event_service
from crud.incident.service import create_or_find_incident

from crud.log_processing.extractos import extract_log_fields

from crud.log_processing.context import (
    build_rule_metadata_snapshot,
    build_explanation,
    calculate_confidence,
    build_event_context,
    update_incident_context,
)


async def process_log(
    db,
    user_id: int,
    raw_log: str,
    source: str = "log",
    host: str = "unknown",
    timestamp=None,
):
    if timestamp is None:
        timestamp = datetime.utcnow()

    extracted = extract_log_fields(raw_log)

    active_rules = await get_active_patterns(db)
    matched_rule = match_pattern(raw_log, active_rules)

    if matched_rule is None:
        return None

    analysis_result = build_analysis_result(
        raw_log=raw_log,
        matched_rule=matched_rule,
    )

    rule_metadata = build_rule_metadata_snapshot(matched_rule)

    explanation = build_explanation(
        pattern_key=rule_metadata.rule_key,
        extracted_fields=extracted,
    )

    confidence = calculate_confidence(
        pattern_key=rule_metadata.rule_key,
        extracted_fields=extracted,
    )

    event_context = build_event_context(
        raw_log=raw_log,
        rule_metadata=rule_metadata,
        extracted_fields=extracted,
        confidence=confidence,
        explanation=explanation,
    )

    incident_context = update_incident_context(
        incident_context=None,
        event_context=event_context,
        service=analysis_result.get("service"),
    )

    incident_analysis = SimpleNamespace(**analysis_result)

    incident = await create_or_find_incident(
        db=db,
        user_id=user_id,
        analysis_result=incident_analysis,
    )

    event = await create_event_service(
        db=db,
        user_id=user_id,
        incident=incident,
        analysis_result=analysis_result,
        source=source,
        host=host,
        timestamp=timestamp,
    )

    return {
        "incident": incident,
        "event": event,
        "analysis_result": analysis_result,
        "extracted_fields": extracted,
        "rule_metadata": rule_metadata,
        "event_context": event_context,
        "incident_context": incident_context,
        "confidence": confidence,
        "explanation": explanation,
    }