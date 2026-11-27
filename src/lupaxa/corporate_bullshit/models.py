"""Shared command names and limits."""

from __future__ import annotations

VOCABULARY_VERSION = "1"

MIN_LEVEL = 1
MAX_LEVEL = 3
MIN_COUNT = 1
MAX_COUNT = 100
MIN_PARAGRAPHS = 1
MAX_PARAGRAPHS = 40
BINGO_SIZES = (3, 5, 7)
FORMATS = ("text", "json", "markdown")

MEETING_TYPES = ("agreement", "avoidance", "deflection", "followup", "strategy", "objection", "summary", "random")
EXCUSE_TOPICS = ("deadline", "budget", "technical", "meeting", "report", "project", "performance", "communication", "random")
MISSION_TYPES = ("mission", "vision", "values", "purpose", "random")
EMAIL_TYPES = ("update", "followup", "apology", "announcement", "request", "escalation", "reminder", "random")
DOCUMENT_TYPES = ("strategy", "report", "proposal", "business-plan", "executive-summary", "transformation-plan", "random")

PERCENTS = (12, 17, 23, 27, 33, 37, 42, 48, 64, 73, 87, 110, 250)

DOCUMENT_SECTIONS: dict[str, tuple[tuple[str, str], ...]] = {
    "strategy": (
        ("Executive Summary", "prose"),
        ("Background", "prose"),
        ("Strategic Objectives", "objective"),
        ("Key Initiatives", "initiative"),
        ("Business Justification", "prose"),
        ("Expected Outcomes", "outcome"),
        ("Key Performance Indicators (Fictional)", "kpi"),
        ("Recommendations", "recommendation"),
        ("Conclusion", "prose"),
    ),
    "report": (
        ("Executive Summary", "prose"),
        ("Background", "prose"),
        ("Findings", "prose"),
        ("Expected Outcomes", "outcome"),
        ("Key Performance Indicators (Fictional)", "kpi"),
        ("Recommendations", "recommendation"),
        ("Conclusion", "prose"),
    ),
    "proposal": (
        ("Executive Summary", "prose"),
        ("Background", "prose"),
        ("Key Initiatives", "initiative"),
        ("Business Justification", "prose"),
        ("Expected Outcomes", "outcome"),
        ("Recommendations", "recommendation"),
        ("Conclusion", "prose"),
    ),
    "business-plan": (
        ("Executive Summary", "prose"),
        ("Background", "prose"),
        ("Strategic Objectives", "objective"),
        ("Key Initiatives", "initiative"),
        ("Business Justification", "prose"),
        ("Expected Outcomes", "outcome"),
        ("Key Performance Indicators (Fictional)", "kpi"),
        ("Conclusion", "prose"),
    ),
    "executive-summary": (("Executive Summary", "prose"), ("Expected Outcomes", "outcome"), ("Recommendations", "recommendation")),
    "transformation-plan": (
        ("Executive Summary", "prose"),
        ("Background", "prose"),
        ("Strategic Objectives", "objective"),
        ("Key Initiatives", "initiative"),
        ("Expected Outcomes", "outcome"),
        ("Key Performance Indicators (Fictional)", "kpi"),
        ("Recommendations", "recommendation"),
        ("Conclusion", "prose"),
    ),
}

DOCUMENT_TITLES = {
    "strategy": "Strategic Plan",
    "report": "Status Report",
    "proposal": "Proposal",
    "business-plan": "Business Plan",
    "executive-summary": "Executive Summary",
    "transformation-plan": "Transformation Plan",
}
