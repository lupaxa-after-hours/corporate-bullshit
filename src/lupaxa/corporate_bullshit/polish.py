"""Turn a filled template into a sentence."""

from __future__ import annotations

import re

from lupaxa.corporate_bullshit.exceptions import GenerationError

COMPANY_MARK = "\ue000"

_SPACES = re.compile(r"[ \t]+")
_SPACE_BEFORE_PUNCT = re.compile(r" +([,.;:!?])")
_SPACE_AFTER_PUNCT = re.compile(r"([,.;:!?])([A-Za-z])")
_THE_THE = re.compile(r"\b([Tt]he)\s+[Tt]he\b")
_ARTICLE = re.compile(r"\b([Aa]n?)\s+([A-Za-z0-9][A-Za-z0-9-]*)")


def polish(text: str, company: str = "", *, stop: bool = True) -> str:
    """Clean spacing, articles, and the final mark. Company text stays literal."""
    inserted = ""
    if COMPANY_MARK in text:
        inserted = company.strip() or "The organisation"
        text = inserted.join(text.split(COMPANY_MARK))
    text = _tidy(text)
    text = _THE_THE.sub(r"\1", text)
    if not (inserted and text.startswith(inserted)):
        text = _capitalise(text)
    text = _ARTICLE.sub(_fix_article, text)
    if stop:
        text = _ensure_stop(text)
    text = _tidy(text)
    if not text or text in ".!?":
        raise GenerationError("generated text was empty")
    return text


def _tidy(text: str) -> str:
    text = _SPACES.sub(" ", text.replace("\n", " ")).strip()
    text = _SPACE_BEFORE_PUNCT.sub(r"\1", text)
    text = _SPACE_AFTER_PUNCT.sub(r"\1 \2", text)
    return text.strip()


def _capitalise(text: str) -> str:
    chars = list(text)
    for index, char in enumerate(chars):
        if char.isalpha():
            chars[index] = char.upper()
            break
    return "".join(chars)


def _ensure_stop(text: str) -> str:
    if text and text[-1] not in ".!?":
        return text + "."
    return text


def _fix_article(match: re.Match[str]) -> str:
    word = match.group(2)
    article = _article_for(word)
    if match.group(1)[0].isupper():
        article = article.capitalize()
    return f"{article} {word}"


def _article_for(word: str) -> str:
    folded = word.casefold()
    if folded.startswith("uni"):
        return "a"
    if folded.startswith(("un", "um", "ul", "up", "ur", "ut", "ug", "hour", "honour", "honest")):
        return "an"
    if folded[:1] in "aeio":
        return "an"
    return "a"
