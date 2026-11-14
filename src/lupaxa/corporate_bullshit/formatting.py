"""Render generation results as text, Markdown, or JSON."""

from __future__ import annotations

import json
from typing import TypeAlias

JsonObject: TypeAlias = dict[str, object]


def render_result(payload: JsonObject, fmt: str, *, colour: bool = False) -> str:
    """Format a result payload. ``fmt`` is ``text``, ``json``, or ``markdown``."""
    if fmt == "json":
        return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    mode = str(payload["mode"])
    if fmt == "markdown":
        return _MARKDOWN[mode](payload)
    return _TEXT[mode](payload, colour)


def _label(text: str, colour: bool) -> str:
    if not colour:
        return text
    return f"\033[1m{text}\033[0m"


def _lines(values: list[str]) -> str:
    return "\n".join(values) + "\n"


def _bullets(values: list[str]) -> str:
    return "\n".join(f"- {value}" for value in values) + "\n"


def _text_generate(payload: JsonObject, _colour: bool) -> str:
    return _lines(_strings(payload["results"]))


def _md_generate(payload: JsonObject) -> str:
    return _bullets(_strings(payload["results"]))


def _text_strategy(payload: JsonObject, colour: bool) -> str:
    blocks: list[str] = []
    for item in _objects(payload["results"]):
        lines = [
            f"{_label('Objective:', colour)} {item['objective']}",
            f"{_label('Rationale:', colour)} {item['rationale']}",
        ]
        if "kpi" in item:
            lines.append(f"{_label('KPI (fictional):', colour)} {item['kpi']}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + "\n"


def _md_strategy(payload: JsonObject) -> str:
    blocks: list[str] = []
    for item in _objects(payload["results"]):
        lines = [
            f"**Objective:** {item['objective']}",
            "",
            f"**Rationale:** {item['rationale']}",
        ]
        if "kpi" in item:
            lines.extend(["", f"**KPI (fictional):** {item['kpi']}"])
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + "\n"


def _text_email(payload: JsonObject, colour: bool) -> str:
    blocks: list[str] = []
    for item in _objects(payload["results"]):
        lines = [f"{_label('Subject:', colour)} {item['subject']}", "", str(item["greeting"]), ""]
        lines.extend(str(paragraph) + "\n" for paragraph in _strings(item["paragraphs"]))
        lines.append(str(item["closing"]))
        sender = item.get("sender")
        if isinstance(sender, str) and sender:
            lines.append(sender)
        blocks.append("\n".join(lines).rstrip())
    return "\n\n".join(blocks) + "\n"


def _md_email(payload: JsonObject) -> str:
    blocks: list[str] = []
    for item in _objects(payload["results"]):
        lines = [f"**Subject:** {item['subject']}", "", str(item["greeting"]), ""]
        lines.extend(str(paragraph) for paragraph in _strings(item["paragraphs"]))
        lines.extend(["", str(item["closing"])])
        sender = item.get("sender")
        if isinstance(sender, str) and sender:
            lines.extend(["", sender])
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + "\n"


def _text_jargon(payload: JsonObject, colour: bool) -> str:
    entries = _objects(payload["entries"])
    if payload.get("list"):
        return _lines([str(item["term"]) for item in entries])
    lines = [f"{_label(str(item['term']) + ':', colour)} {item['definition']}" for item in entries]
    return _lines(lines)


def _md_jargon(payload: JsonObject) -> str:
    entries = _objects(payload["entries"])
    if payload.get("list"):
        return _bullets([str(item["term"]) for item in entries])
    lines = [f"**{item['term']}:** {item['definition']}" for item in entries]
    return "\n\n".join(lines) + "\n"


def _text_translate(payload: JsonObject, _colour: bool) -> str:
    return str(payload["output"]) + "\n"


def _md_translate(payload: JsonObject) -> str:
    return str(payload["output"]) + "\n"


def _text_bingo(payload: JsonObject, _colour: bool) -> str:
    cards = _grids(payload["cards"])
    return "\n\n".join(_card_text(card) for card in cards) + "\n"


def _md_bingo(payload: JsonObject) -> str:
    cards = _grids(payload["cards"])
    blocks: list[str] = []
    for index, card in enumerate(cards, start=1):
        table = _card_markdown(card)
        if len(cards) > 1:
            blocks.append(f"## Card {index}\n\n{table}")
        else:
            blocks.append(table)
    return "\n\n".join(blocks) + "\n"


def _text_document(payload: JsonObject, colour: bool) -> str:
    return "\n\n".join(_document_text(item, colour) for item in _objects(payload["results"])) + "\n"


def _md_document(payload: JsonObject) -> str:
    return "\n\n".join(_document_markdown(item) for item in _objects(payload["results"])) + "\n"


def _document_text(item: JsonObject, colour: bool) -> str:
    parts = [str(item["title"])]
    for section in _objects(item["sections"]):
        parts.append(_label(str(section["heading"]), colour))
        content = _strings(section["content"])
        if section["style"] == "items":
            parts.append("\n".join(f"- {line}" for line in content))
        else:
            parts.append("\n\n".join(content))
    return "\n\n".join(parts)


def _document_markdown(item: JsonObject) -> str:
    parts = [f"# {item['title']}"]
    for section in _objects(item["sections"]):
        content = _strings(section["content"])
        body = (
            "\n".join(f"- {line}" for line in content)
            if section["style"] == "items"
            else "\n\n".join(content)
        )
        parts.append(f"## {section['heading']}\n\n{body}")
    return "\n\n".join(parts)


def _card_text(card: list[list[str]]) -> str:
    wrapped = [[_wrap(cell, 18) for cell in row] for row in card]
    widths = [
        max(len(line) for row in wrapped for line in row[column]) for column in range(len(card))
    ]
    border = "+" + "+".join("-" * (width + 2) for width in widths) + "+"
    lines = [border]
    for row in wrapped:
        height = max(len(cell) for cell in row)
        for line_index in range(height):
            cells = []
            for column, cell in enumerate(row):
                piece = cell[line_index] if line_index < len(cell) else ""
                cells.append(" " + piece.ljust(widths[column]) + " ")
            lines.append("|" + "|".join(cells) + "|")
        lines.append(border)
    return "\n".join(lines)


def _card_markdown(card: list[list[str]]) -> str:
    header = "| " + " | ".join(" " for _ in card) + " |"
    separator = "| " + " | ".join("---" for _ in card) + " |"
    rows = ["| " + " | ".join(cell.replace("|", "\\|") for cell in row) + " |" for row in card]
    return "\n".join([header, separator, *rows])


def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        if len(current) + 1 + len(word) <= width:
            current = f"{current} {word}"
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _strings(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _objects(value: object) -> list[JsonObject]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _grids(value: object) -> list[list[list[str]]]:
    if not isinstance(value, list):
        return []
    cards: list[list[list[str]]] = []
    for card in value:
        if not isinstance(card, list):
            continue
        rows: list[list[str]] = []
        for row in card:
            if isinstance(row, list):
                rows.append([str(cell) for cell in row])
        cards.append(rows)
    return cards


_TEXT = {
    "generate": _text_generate,
    "meeting": _text_generate,
    "excuse": _text_generate,
    "mission": _text_generate,
    "strategy": _text_strategy,
    "email": _text_email,
    "jargon": _text_jargon,
    "translate": _text_translate,
    "bingo": _text_bingo,
    "document": _text_document,
}
_MARKDOWN = {
    "generate": _md_generate,
    "meeting": _md_generate,
    "excuse": _md_generate,
    "mission": _md_generate,
    "strategy": _md_strategy,
    "email": _md_email,
    "jargon": _md_jargon,
    "translate": _md_translate,
    "bingo": _md_bingo,
    "document": _md_document,
}
