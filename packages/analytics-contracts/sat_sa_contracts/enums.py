from enum import StrEnum


class Severity(StrEnum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"
    informational = "informational"


class ReviewOutcome(StrEnum):
    accepted = "accepted"
    dismissed = "dismissed"
    explained = "explained"
    confirmed_concern = "confirmed_concern"
    false_positive = "false_positive"
    insufficient_evidence = "insufficient_evidence"
    further_investigation = "further_investigation"


class Role(StrEnum):
    reader = "reader"
    examiner = "examiner"
    administrator = "administrator"
