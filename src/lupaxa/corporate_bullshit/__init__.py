"""Offline generator of convincingly meaningless corporate language."""

from __future__ import annotations

from lupaxa.corporate_bullshit.exceptions import (
    CorporateBullshitError,
    DataFileError,
    GenerationError,
    IOProblem,
    TemplateError,
    UsageError,
    VocabularyError,
)
from lupaxa.corporate_bullshit.service import (
    bingo,
    document,
    email,
    excuse,
    generate,
    jargon_define,
    jargon_list,
    jargon_random,
    meeting,
    mission,
    strategy,
    translate,
)
from lupaxa.corporate_bullshit.version import __version__, get_version

__all__ = [
    "CorporateBullshitError",
    "DataFileError",
    "GenerationError",
    "IOProblem",
    "TemplateError",
    "UsageError",
    "VocabularyError",
    "__version__",
    "bingo",
    "document",
    "email",
    "excuse",
    "generate",
    "get_version",
    "jargon_define",
    "jargon_list",
    "jargon_random",
    "meeting",
    "mission",
    "strategy",
    "translate",
]
