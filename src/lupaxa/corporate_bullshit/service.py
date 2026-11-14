"""High-level generation used by the library and the command-line tool."""

from __future__ import annotations

from collections.abc import Callable
from random import Random
from typing import TypeAlias

from lupaxa.corporate_bullshit.catalogue import Catalogue, JargonEntry, load_builtin
from lupaxa.corporate_bullshit.engine import Engine
from lupaxa.corporate_bullshit.exceptions import UsageError, VocabularyError
from lupaxa.corporate_bullshit.models import (
    BINGO_SIZES,
    DOCUMENT_SECTIONS,
    DOCUMENT_TITLES,
    DOCUMENT_TYPES,
    EMAIL_TYPES,
    EXCUSE_TOPICS,
    MEETING_TYPES,
    MISSION_TYPES,
)
from lupaxa.corporate_bullshit.translate import translate_text

JsonObject: TypeAlias = dict[str, object]
Section: TypeAlias = dict[str, object]


def _catalogue(catalogue: Catalogue | None) -> Catalogue:
    return catalogue if catalogue is not None else load_builtin()


def _engine(
    *,
    level: int,
    seed: int | None,
    catalogue: Catalogue | None,
    company: str = "",
) -> Engine:
    return Engine(_catalogue(catalogue), Random(seed), level, company)


def _choice(engine: Engine, value: str, allowed: tuple[str, ...], label: str) -> str:
    if value not in allowed:
        names = ", ".join(allowed)
        raise UsageError(f"unknown {label} '{value}'. Choose one of: {names}")
    if value != "random":
        return value
    concrete = [item for item in allowed if item != "random"]
    return str(engine.rng.choice(concrete))


def _unique_lines(engine: Engine, group_for_index: Callable[[], str], count: int) -> list[str]:
    seen: set[str] = set()
    results: list[str] = []
    attempts = 0
    while len(results) < count and attempts < max(count * 15, 20):
        attempts += 1
        text = engine.render(group_for_index())
        if text in seen:
            continue
        seen.add(text)
        results.append(text)
    while len(results) < count:
        results.append(engine.render(group_for_index()))
    return results


def generate(
    *,
    level: int = 2,
    count: int = 1,
    seed: int | None = None,
    catalogue: Catalogue | None = None,
) -> list[str]:
    """Return corporate statements."""
    engine = _engine(level=level, seed=seed, catalogue=catalogue)
    return engine.render_unique("statement", count)


def meeting(
    *,
    kind: str = "random",
    level: int = 2,
    count: int = 1,
    seed: int | None = None,
    catalogue: Catalogue | None = None,
) -> list[str]:
    """Return meeting contributions."""
    engine = _engine(level=level, seed=seed, catalogue=catalogue)

    def group() -> str:
        return "meeting_" + _choice(engine, kind, MEETING_TYPES, "meeting type")

    return _unique_lines(engine, group, count)


def excuse(
    *,
    topic: str = "random",
    level: int = 2,
    count: int = 1,
    seed: int | None = None,
    catalogue: Catalogue | None = None,
) -> list[str]:
    """Return professional-sounding excuses."""
    engine = _engine(level=level, seed=seed, catalogue=catalogue)

    def group() -> str:
        return "excuse_" + _choice(engine, topic, EXCUSE_TOPICS, "excuse topic")

    return _unique_lines(engine, group, count)


def strategy(
    *,
    level: int = 2,
    count: int = 1,
    seed: int | None = None,
    include_kpi: bool = True,
    catalogue: Catalogue | None = None,
) -> list[JsonObject]:
    """Return objectives, rationales, and optional fictional KPIs."""
    engine = _engine(level=level, seed=seed, catalogue=catalogue)
    results: list[JsonObject] = []
    for _ in range(count):
        item: JsonObject = {
            "objective": engine.render("strategy_objective"),
            "rationale": engine.render("strategy_rationale"),
            "fictional": True,
        }
        if include_kpi:
            item["kpi"] = engine.render("strategy_kpi")
        results.append(item)
    return results


def mission(
    *,
    kind: str = "mission",
    company: str = "",
    level: int = 2,
    count: int = 1,
    seed: int | None = None,
    catalogue: Catalogue | None = None,
) -> list[str]:
    """Return mission, vision, values, or purpose statements."""
    engine = _engine(level=level, seed=seed, catalogue=catalogue, company=company)

    def group() -> str:
        return "mission_" + _choice(engine, kind, MISSION_TYPES, "mission type")

    return _unique_lines(engine, group, count)


def email(
    *,
    kind: str = "update",
    recipient: str = "",
    sender: str = "",
    paragraphs: int = 3,
    company: str = "",
    level: int = 2,
    count: int = 1,
    seed: int | None = None,
    catalogue: Catalogue | None = None,
) -> list[JsonObject]:
    """Return fictional corporate emails."""
    engine = _engine(level=level, seed=seed, catalogue=catalogue, company=company)
    messages: list[JsonObject] = []
    for _ in range(count):
        chosen = _choice(engine, kind, EMAIL_TYPES, "email type")
        body = [engine.render(f"email_body_{chosen}") for _paragraph in range(paragraphs)]
        item: JsonObject = {
            "type": chosen,
            "subject": engine.render(f"email_subject_{chosen}", stop=False),
            "greeting": f"Dear {recipient}," if recipient else "Hello,",
            "paragraphs": body,
            "closing": "Kind regards,",
        }
        if recipient:
            item["recipient"] = recipient
        if sender:
            item["sender"] = sender
        messages.append(item)
    return messages


def jargon_define(term: str, catalogue: Catalogue | None = None) -> JargonEntry:
    """Look up one term. Unknown terms raise ``UsageError``."""
    found = _catalogue(catalogue).jargon_lookup(" ".join(term.split()))
    if found is None:
        raise UsageError(f"unknown jargon term: {term.strip() or term}")
    return found


def jargon_list(catalogue: Catalogue | None = None) -> list[str]:
    """Return jargon terms in case-insensitive order."""
    entries = _catalogue(catalogue).jargon
    return [entry.term for entry in sorted(entries, key=lambda item: item.term.casefold())]


def jargon_random(
    *,
    count: int = 1,
    seed: int | None = None,
    catalogue: Catalogue | None = None,
) -> list[JargonEntry]:
    """Return random jargon entries, without duplicates when the list allows it."""
    entries = list(_catalogue(catalogue).jargon)
    if not entries:
        raise VocabularyError("the jargon dictionary is empty")
    rng = Random(seed)
    if count <= len(entries):
        return rng.sample(entries, count)
    picked = rng.sample(entries, len(entries))
    while len(picked) < count:
        picked.append(rng.choice(entries))
    return picked


def translate(
    text: str,
    *,
    level: int = 2,
) -> str:
    """Translate ordinary English into corporate English."""
    return translate_text(text, level)


def bingo(
    *,
    size: int = 5,
    count: int = 1,
    seed: int | None = None,
    catalogue: Catalogue | None = None,
) -> list[list[list[str]]]:
    """Return bingo cards. The centre cell is ``FREE SPACE``."""
    if size not in BINGO_SIZES:
        raise UsageError("bingo size must be 3, 5, or 7")
    source = _catalogue(catalogue)
    needed = size * size - 1
    terms = list(dict.fromkeys(source.bingo))
    if len(terms) < needed:
        raise VocabularyError(
            f"need {needed} unique bingo terms for a {size}×{size} card, found {len(terms)}"
        )
    rng = Random(seed)
    cards: list[list[list[str]]] = []
    seen: set[tuple[tuple[str, ...], ...]] = set()
    attempts = 0
    while len(cards) < count and attempts < count * 8:
        attempts += 1
        card = _card(rng, terms, size)
        key = tuple(tuple(row) for row in card)
        if key in seen:
            continue
        seen.add(key)
        cards.append(card)
    while len(cards) < count:
        cards.append(_card(rng, terms, size))
    return cards


def _card(rng: Random, terms: list[str], size: int) -> list[list[str]]:
    picked = rng.sample(terms, size * size - 1)
    middle = size // 2
    cursor = 0
    card: list[list[str]] = []
    for row_index in range(size):
        row: list[str] = []
        for column in range(size):
            if row_index == middle and column == middle:
                row.append("FREE SPACE")
            else:
                row.append(picked[cursor])
                cursor += 1
        card.append(row)
    return card


def document(
    *,
    kind: str = "strategy",
    company: str = "",
    paragraphs: int = 3,
    level: int = 2,
    count: int = 1,
    seed: int | None = None,
    catalogue: Catalogue | None = None,
) -> list[JsonObject]:
    """Return fictional corporate documents."""
    engine = _engine(level=level, seed=seed, catalogue=catalogue, company=company)
    documents: list[JsonObject] = []
    for _ in range(count):
        chosen = _choice(engine, kind, DOCUMENT_TYPES, "document type")
        engine.lock_terms()
        documents.append(_one_document(engine, chosen, company, paragraphs))
        engine.preferred = {}
    return documents


def _one_document(engine: Engine, kind: str, company: str, paragraphs: int) -> JsonObject:
    name = company.strip() or "The organisation"
    title = f"{name}: {DOCUMENT_TITLES[kind]}"
    layout = DOCUMENT_SECTIONS[kind]
    shares = _shares(paragraphs, len(layout))
    sections: list[Section] = []
    for (heading, style), amount in zip(layout, shares, strict=True):
        group = {
            "prose": "document",
            "objective": "strategy_objective",
            "initiative": "initiative",
            "outcome": "outcome_item",
            "kpi": "strategy_kpi",
            "recommendation": "recommendation",
        }[style]
        sections.append(
            {
                "heading": heading,
                "style": "items" if style != "prose" else "prose",
                "fictional": style == "kpi",
                "content": [engine.render(group) for _ in range(amount)],
            }
        )
    return {
        "type": kind,
        "company": company.strip(),
        "title": title,
        "fictional": True,
        "sections": sections,
    }


def _shares(total: int, slots: int) -> list[int]:
    total = max(total, slots)
    base, remainder = divmod(total, slots)
    return [base + (1 if index < remainder else 0) for index in range(slots)]
