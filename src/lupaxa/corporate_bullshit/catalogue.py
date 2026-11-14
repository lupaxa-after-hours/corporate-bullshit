"""Load built-in language data and optional user TOML overlays.

User files are parsed with :mod:`tomllib` and never executed.
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from random import Random

from lupaxa.corporate_bullshit.exceptions import DataFileError, VocabularyError
from lupaxa.corporate_bullshit.lexicon import BINGO_TERMS, JARGON, WORDS
from lupaxa.corporate_bullshit.models import VOCABULARY_VERSION
from lupaxa.corporate_bullshit.patterns import PATTERNS

SLOT_RE = re.compile(r"\{([a-z][a-z0-9_]*)\}")
OPTIONAL_RE = re.compile(r"\[([^\[\]]*)\]")
SPECIAL_SLOTS = frozenset({"company", "percent"})
STOPWORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "of",
        "to",
        "and",
        "for",
        "in",
        "our",
        "on",
        "at",
        "by",
        "with",
        "so",
        "we",
        "it",
        "is",
    }
)


def significant_tokens(text: str) -> set[str]:
    """Return lowercase words worth refusing to repeat in one sentence."""
    found = re.findall(r"[a-z0-9]+", text.casefold())
    return {token for token in found if token not in STOPWORDS and len(token) > 2}


@dataclass
class JargonEntry:
    """One sarcastic definition."""

    term: str
    definition: str


@dataclass
class Catalogue:
    """Vocabulary, templates, and jargon available to one run."""

    version: str
    words: dict[str, dict[int, list[str]]]
    patterns: dict[str, dict[int, list[str]]]
    jargon: list[JargonEntry]
    bingo: list[str]
    warnings: list[str] = field(default_factory=list)
    custom: bool = False

    def choose_pattern(self, group: str, level: int, rng: Random) -> str:
        """Pick a template for ``group`` at this intensity."""
        levels = self.patterns.get(group)
        if not levels:
            raise VocabularyError(f"missing template group: {group}")
        pool: list[str] = []
        weights: list[int] = []
        for word_level, patterns in levels.items():
            if word_level > level:
                continue
            weight = _weight(word_level, level)
            for pattern in patterns:
                pool.append(pattern)
                weights.append(weight)
        if not pool:
            raise VocabularyError(f"no templates for {group} at level {level}")
        return rng.choices(pool, weights=weights, k=1)[0]

    def pick(
        self,
        category: str,
        level: int,
        rng: Random,
        avoid: set[str],
        preferred: list[str] | None = None,
    ) -> str:
        """Pick a word, preferring this intensity and avoiding repeats."""
        levels = self.words.get(category)
        if not levels:
            raise VocabularyError(f"missing vocabulary category: {category}")
        pool, weights = _pool(levels, level, avoid)
        if not pool:
            pool, weights = _pool(levels, level, set())
        if not pool:
            raise VocabularyError(f"no vocabulary for {category} at level {level}")
        if preferred:
            wanted = {item.casefold() for item in preferred}
            narrowed = [
                (word, weight)
                for word, weight in zip(pool, weights, strict=True)
                if word.casefold() in wanted
            ]
            if narrowed and rng.random() < 0.7:
                pool = [word for word, _weight in narrowed]
                weights = [1] * len(pool)
        return rng.choices(pool, weights=weights, k=1)[0]

    def jargon_lookup(self, term: str) -> JargonEntry | None:
        """Return a definition, ignoring case and surrounding space, or ``None``."""
        folded = " ".join(term.split()).casefold()
        if not folded:
            return None
        for entry in self.jargon:
            if entry.term.casefold() == folded:
                return entry
        return None


def load_builtin() -> Catalogue:
    """Return the packaged catalogue. Built-in templates must be valid."""
    catalogue = Catalogue(
        version=VOCABULARY_VERSION,
        words={
            name: {level: list(items) for level, items in levels.items()}
            for name, levels in WORDS.items()
        },
        patterns={
            name: {level: list(items) for level, items in levels.items()}
            for name, levels in PATTERNS.items()
        },
        jargon=[JargonEntry(term, definition) for term, definition in JARGON],
        bingo=list(BINGO_TERMS),
    )
    problems = _validate_patterns(catalogue)
    if problems:
        raise DataFileError("built-in templates are invalid: " + "; ".join(problems))
    if len(set(catalogue.bingo)) != len(catalogue.bingo):
        raise DataFileError("built-in bingo terms contain duplicates")
    return catalogue


def load_catalogue(paths: list[Path]) -> Catalogue:
    """Return the built-in catalogue plus any user files, in order."""
    catalogue = load_builtin()
    for path in paths:
        _merge_file(catalogue, path)
        catalogue.custom = True
    if catalogue.custom:
        catalogue.version = f"{VOCABULARY_VERSION}+custom"
    return catalogue


def _merge_file(catalogue: Catalogue, path: Path) -> None:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise DataFileError(f"cannot read {path}: {exc.strerror}") from exc
    try:
        parsed = tomllib.loads(raw)
    except tomllib.TOMLDecodeError as exc:
        raise DataFileError(f"invalid template file {path}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise DataFileError(f"invalid template file {path}: expected a table")
    known = {"words", "patterns", "jargon", "bingo", "version"}
    for key in parsed:
        if key not in known:
            catalogue.warnings.append(f"{path}: ignored unknown table '{key}'")
    if "words" in parsed:
        _merge_levels(catalogue, path, "words", parsed["words"], catalogue.words)
    if "patterns" in parsed:
        _merge_levels(catalogue, path, "patterns", parsed["patterns"], catalogue.patterns)
    if "jargon" in parsed:
        _merge_jargon(catalogue, path, parsed["jargon"])
    if "bingo" in parsed:
        _merge_bingo(catalogue, path, parsed["bingo"])


def _merge_levels(
    catalogue: Catalogue,
    path: Path,
    kind: str,
    table: object,
    target: dict[str, dict[int, list[str]]],
) -> None:
    if not isinstance(table, dict):
        catalogue.warnings.append(f"{path}: ignored {kind} because it is not a table")
        return
    for name, value in table.items():
        if not isinstance(name, str):
            catalogue.warnings.append(f"{path}: ignored a non-text {kind} name")
            continue
        bucket = target.setdefault(name, {1: [], 2: [], 3: []})
        entries = _read_level_map(
            path, kind, name, value, catalogue, allow_braces=kind == "patterns"
        )
        if kind == "patterns":
            entries = _keep_valid_patterns(catalogue, path, name, entries)
        for level, items in entries.items():
            for item in items:
                if item in bucket.setdefault(level, []):
                    catalogue.warnings.append(f"{path}: skipped duplicate {kind} entry '{item}'")
                    continue
                bucket[level].append(item)


def _read_level_map(
    path: Path,
    kind: str,
    name: str,
    value: object,
    catalogue: Catalogue,
    *,
    allow_braces: bool,
) -> dict[int, list[str]]:
    found: dict[int, list[str]] = {1: [], 2: [], 3: []}
    if isinstance(value, list):
        found[2] = _strings(path, f"{kind}.{name}", value, catalogue, allow_braces=allow_braces)
        return found
    if not isinstance(value, dict):
        catalogue.warnings.append(
            f"{path}: ignored {kind}.{name} because it is not a table or list"
        )
        return found
    for key, items in value.items():
        try:
            level = int(key)
        except (TypeError, ValueError):
            catalogue.warnings.append(
                f"{path}: ignored {kind}.{name}.{key} (level must be 1, 2, or 3)"
            )
            continue
        if level not in (1, 2, 3):
            catalogue.warnings.append(
                f"{path}: ignored {kind}.{name}.{key} (level must be 1, 2, or 3)"
            )
            continue
        if not isinstance(items, list):
            catalogue.warnings.append(
                f"{path}: ignored {kind}.{name}.{key} because it is not a list"
            )
            continue
        found[level] = _strings(
            path,
            f"{kind}.{name}.{level}",
            items,
            catalogue,
            allow_braces=allow_braces,
        )
    return found


def _strings(
    path: Path,
    label: str,
    items: list[object],
    catalogue: Catalogue,
    *,
    allow_braces: bool = False,
) -> list[str]:
    kept: list[str] = []
    for item in items:
        if not isinstance(item, str) or not item.strip():
            catalogue.warnings.append(f"{path}: ignored an empty or non-text entry in {label}")
            continue
        text = " ".join(item.split())
        if not allow_braces and ("{" in text or "}" in text):
            catalogue.warnings.append(
                f"{path}: ignored '{text}' in {label} because it contains braces"
            )
            continue
        kept.append(text)
    return kept


def _keep_valid_patterns(
    catalogue: Catalogue,
    path: Path,
    group: str,
    entries: dict[int, list[str]],
) -> dict[int, list[str]]:
    kept: dict[int, list[str]] = {1: [], 2: [], 3: []}
    for level, patterns in entries.items():
        for pattern in patterns:
            problem = pattern_problem(pattern, catalogue.words, catalogue.patterns)
            if problem:
                catalogue.warnings.append(f"{path}: ignored template in {group}: {problem}")
                continue
            kept[level].append(pattern)
    return kept


def _merge_jargon(catalogue: Catalogue, path: Path, value: object) -> None:
    if not isinstance(value, list):
        catalogue.warnings.append(f"{path}: ignored jargon because it is not a list")
        return
    known = {entry.term.casefold() for entry in catalogue.jargon}
    for item in value:
        if not isinstance(item, dict):
            catalogue.warnings.append(f"{path}: ignored a jargon entry that is not a table")
            continue
        term = item.get("term")
        definition = item.get("definition")
        if not isinstance(term, str) or not term.strip():
            catalogue.warnings.append(f"{path}: ignored a jargon entry with no term")
            continue
        if not isinstance(definition, str) or not definition.strip():
            catalogue.warnings.append(f"{path}: ignored jargon '{term}' with no definition")
            continue
        clean_term = " ".join(term.split())
        clean_definition = " ".join(definition.split())
        if clean_term.casefold() in known:
            catalogue.warnings.append(f"{path}: skipped duplicate jargon term '{clean_term}'")
            continue
        catalogue.jargon.append(JargonEntry(clean_term, clean_definition))
        known.add(clean_term.casefold())


def _merge_bingo(catalogue: Catalogue, path: Path, value: object) -> None:
    if not isinstance(value, list):
        catalogue.warnings.append(f"{path}: ignored bingo because it is not a list")
        return
    known = {term.casefold() for term in catalogue.bingo}
    for item in _strings(path, "bingo", value, catalogue):
        if item.casefold() in known:
            catalogue.warnings.append(f"{path}: skipped duplicate bingo term '{item}'")
            continue
        catalogue.bingo.append(item)
        known.add(item.casefold())


def pattern_problem(
    pattern: str,
    words: dict[str, dict[int, list[str]]],
    patterns: dict[str, dict[int, list[str]]],
) -> str | None:
    """Return an error string, or ``None`` when the template is safe to fill."""
    if pattern.count("[") != pattern.count("]"):
        return "unbalanced brackets"
    if "[" in pattern and OPTIONAL_RE.sub("", pattern).count("[") != 0:
        return "nested brackets are not supported"
    body = pattern.replace("[", "").replace("]", "")
    for name in SLOT_RE.findall(body):
        if name in SPECIAL_SLOTS or name in words or name in patterns:
            continue
        return f"unknown placeholder {{{name}}}"
    leftover = re.sub(r"\{[a-z][a-z0-9_]*\}", "", body)
    if "{" in leftover or "}" in leftover:
        return "invalid placeholder syntax"
    return None


def _validate_patterns(catalogue: Catalogue) -> list[str]:
    problems: list[str] = []
    for group, levels in catalogue.patterns.items():
        for level, patterns in levels.items():
            for pattern in patterns:
                problem = pattern_problem(pattern, catalogue.words, catalogue.patterns)
                if problem:
                    problems.append(f"{group} level {level}: {problem} ({pattern})")
    return problems


def _pool(
    levels: dict[int, list[str]],
    level: int,
    avoid: set[str],
) -> tuple[list[str], list[int]]:
    pool: list[str] = []
    weights: list[int] = []
    for word_level, words in levels.items():
        if word_level > level:
            continue
        weight = _weight(word_level, level)
        for word in words:
            if significant_tokens(word) & avoid:
                continue
            pool.append(word)
            weights.append(weight)
    return pool, weights


def _weight(item_level: int, requested: int) -> int:
    if requested <= 1:
        return 1
    if requested == 2:
        return 4 if item_level == 2 else 1
    return {1: 1, 2: 3, 3: 8}[item_level]
