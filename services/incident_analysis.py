def analyze_logs(logs: str):
    if "timeout" in logs:
        return "Possible timeout issue"
    if "connection refused" in logs:
        return "Service unvailable"
    return "Unknown error"