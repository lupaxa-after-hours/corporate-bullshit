"""Rule-based translation of plain English into corporate English."""

from __future__ import annotations

import re

from lupaxa.corporate_bullshit.exceptions import UsageError
from lupaxa.corporate_bullshit.lexicon import PHRASES, WORD_RULES
from lupaxa.corporate_bullshit.polish import polish


def translate_text(text: str, level: int) -> str:
    """Rewrite ``text``. Unrecognised wording is left as it was."""
    original = text.strip()
    if not original:
        raise UsageError("missing input text")
    rewritten = _apply(original, level)
    if rewritten.casefold() == original.casefold():
        return original
    return polish(rewritten)


def _apply(original: str, level: int) -> str:
    phrases = [item for item in PHRASES if item[0] <= level]
    phrases.sort(key=lambda item: (len(item[1]), item[0]), reverse=True)
    lower = original.casefold()
    pieces: list[tuple[str, bool]] = []
    index = 0
    while index < len(original):
        matched = False
        for _rule_level, source, replacement in phrases:
            end = index + len(source)
            if (
                end <= len(original)
                and lower.startswith(source.casefold(), index)
                and _boundary(original, index, end)
            ):
                pieces.append((replacement, False))
                index = end
                matched = True
                break
        if not matched:
            pieces.append((original[index], True))
            index += 1
    return _apply_words(pieces, level)


def _apply_words(pieces: list[tuple[str, bool]], level: int) -> str:
    rules: dict[str, str] = {}
    for rule_level, source, replacement in WORD_RULES:
        if rule_level <= level:
            rules[source.casefold()] = replacement
    if not rules:
        return "".join(part for part, _original in pieces)
    ordered = sorted(rules, key=len, reverse=True)
    pattern = re.compile(
        r"\b(" + "|".join(re.escape(word) for word in ordered) + r")\b",
        re.IGNORECASE,
    )
    chunks: list[str] = []
    buffer: list[str] = []

    def flush() -> None:
        if not buffer:
            return
        text = "".join(buffer)
        buffer.clear()

        def replace(match: re.Match[str]) -> str:
            return rules[match.group(1).casefold()]

        chunks.append(pattern.sub(replace, text))

    for part, original in pieces:
        if original:
            buffer.append(part)
        else:
            flush()
            chunks.append(part)
    flush()
    return "".join(chunks)


def _boundary(text: str, start: int, end: int) -> bool:
    before = start == 0 or not text[start - 1].isalnum()
    after = end == len(text) or not text[end].isalnum()
    return before and after
