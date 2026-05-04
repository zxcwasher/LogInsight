import re


def match_pattern(raw_log: str, patterns):
    for pattern in patterns:
        if re.search(pattern.pattern, raw_log, re.IGNORECASE):
            return pattern

    return None



def build_analysis_result(raw_log: str, matched_rule):
    if matched_rule is None:
        return {
            "matched": False,
            "pattern_id": None,
            "pattern_key": "unknown",
            "severity": "low",
            "message": "Unclassified log",
            "category": "unknown",
            "service": "unknown",
            "normalized_message": raw_log,
            "raw_log": raw_log,
        }

    severity = (
        matched_rule.severity.value
        if hasattr(matched_rule.severity, "value")
        else matched_rule.severity
    )

    return {
        "matched": True,
        "pattern_id": matched_rule.id,
        "pattern_key": matched_rule.key,
        "severity": severity,
        "message": matched_rule.message,
        "category": matched_rule.category,
        "service": matched_rule.service or "unknown",
        "normalized_message": matched_rule.message,
        "raw_log": raw_log,
    }

