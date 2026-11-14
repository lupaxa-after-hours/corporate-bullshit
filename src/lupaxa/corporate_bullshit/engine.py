"""Fill templates from a catalogue and a seeded random stream."""

from __future__ import annotations

import re
from random import Random

from lupaxa.corporate_bullshit.catalogue import OPTIONAL_RE, SLOT_RE, Catalogue, significant_tokens
from lupaxa.corporate_bullshit.exceptions import TemplateError
from lupaxa.corporate_bullshit.models import PERCENTS
from lupaxa.corporate_bullshit.polish import COMPANY_MARK, polish

_OPTIONAL_CHANCE = {1: 0.2, 2: 0.55, 3: 0.95}
_MAX_DEPTH = 3


class Engine:
    """One seeded pass over the catalogue."""

    def __init__(self, catalogue: Catalogue, rng: Random, level: int, company: str = "") -> None:
        self.catalogue = catalogue
        self.rng = rng
        self.level = level
        self.company = company
        self.preferred: dict[str, list[str]] = {}
        self._avoid: set[str] = set()

    def render(self, group: str, *, stop: bool = True) -> str:
        """Render one sentence from a template group."""
        self._avoid = set()
        pattern = self.catalogue.choose_pattern(group, self.level, self.rng)
        raw = self.expand(pattern, depth=0)
        return polish(raw, self.company, stop=stop)

    def render_unique(self, group: str, count: int, *, stop: bool = True) -> list[str]:
        """Render ``count`` results, skipping duplicates while that is practical."""
        seen: set[str] = set()
        results: list[str] = []
        attempts = 0
        limit = max(count * 15, 20)
        while len(results) < count and attempts < limit:
            attempts += 1
            text = self.render(group, stop=stop)
            if text in seen:
                continue
            seen.add(text)
            results.append(text)
        while len(results) < count:
            results.append(self.render(group, stop=stop))
        return results

    def lock_terms(self) -> None:
        """Pick a small set of words and prefer them for the rest of this document."""
        preferred: dict[str, list[str]] = {}
        for category, count in (
            ("adjective", 2),
            ("noun", 2),
            ("verb", 2),
            ("outcome", 1),
            ("stakeholder", 1),
        ):
            avoid: set[str] = set()
            chosen: list[str] = []
            for _ in range(count):
                word = self.catalogue.pick(category, self.level, self.rng, avoid, None)
                chosen.append(word)
                avoid |= significant_tokens(word)
            preferred[category] = chosen
        self.preferred = preferred

    def expand(self, pattern: str, depth: int) -> str:
        """Substitute placeholders. Optional clauses are resolved first."""
        if depth > _MAX_DEPTH:
            raise TemplateError("template nesting is too deep")
        expanded = OPTIONAL_RE.sub(self._optional, pattern)
        return SLOT_RE.sub(lambda match: self._slot(match, depth), expanded)

    def _optional(self, match: re.Match[str]) -> str:
        if self.rng.random() < _OPTIONAL_CHANCE[self.level]:
            return match.group(1)
        return ""

    def _slot(self, match: re.Match[str], depth: int) -> str:
        name = match.group(1)
        if name == "company":
            return COMPANY_MARK
        if name == "percent":
            return str(self.rng.choice(PERCENTS))
        if name in self.catalogue.words:
            word = self.catalogue.pick(
                name,
                self.level,
                self.rng,
                self._avoid,
                self.preferred.get(name),
            )
            self._avoid |= significant_tokens(word)
            return word
        if name in self.catalogue.patterns:
            nested = self.catalogue.choose_pattern(name, self.level, self.rng)
            return self.expand(nested, depth + 1)
        raise TemplateError(f"unknown placeholder {{{name}}}")
