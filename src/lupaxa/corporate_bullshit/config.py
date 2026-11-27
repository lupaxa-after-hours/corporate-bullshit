"""Optional TOML configuration. The tool runs without a file."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from lupaxa.corporate_bullshit.exceptions import UsageError
from lupaxa.corporate_bullshit.models import FORMATS, MAX_COUNT, MAX_LEVEL, MAX_PARAGRAPHS, MIN_COUNT, MIN_LEVEL, MIN_PARAGRAPHS

_KEYS = {
    "level",
    "format",
    "count",
    "paragraphs",
    "colour",
    "color",
    "company",
    "vocabulary",
    "templates",
}


@dataclass
class Settings:
    """Defaults. Command-line options replace these after the file is read."""

    level: int = 2
    output_format: str = "text"
    count: int = 1
    paragraphs: int = 3
    colour: bool = True
    company: str = ""
    vocabulary: list[Path] = field(default_factory=list)
    templates: list[Path] = field(default_factory=list)


def load_settings(explicit: str | None) -> Settings:
    """Load TOML defaults. A missing default location is not an error."""
    path = discover_config(explicit)
    settings = Settings()
    if path is None:
        return settings
    try:
        parsed = tomllib.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise UsageError(f"cannot read configuration {path}: {exc.strerror}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise UsageError(f"invalid configuration {path}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise UsageError(f"invalid configuration {path}: expected a table")
    unknown = sorted(set(parsed) - _KEYS)
    if unknown:
        names = ", ".join(unknown)
        raise UsageError(f"invalid configuration {path}: unknown keys: {names}")
    if "colour" in parsed and "color" in parsed:
        raise UsageError(f"invalid configuration {path}: set colour or color, not both")
    if "level" in parsed:
        settings.level = _bounded(parsed["level"], "level", MIN_LEVEL, MAX_LEVEL, path)
    if "format" in parsed:
        settings.output_format = _format(parsed["format"], path)
    if "count" in parsed:
        settings.count = _bounded(parsed["count"], "count", MIN_COUNT, MAX_COUNT, path)
    if "paragraphs" in parsed:
        settings.paragraphs = _bounded(parsed["paragraphs"], "paragraphs", MIN_PARAGRAPHS, MAX_PARAGRAPHS, path)
    if "colour" in parsed or "color" in parsed:
        raw = parsed["colour"] if "colour" in parsed else parsed["color"]
        if not isinstance(raw, bool):
            raise UsageError(f"invalid configuration {path}: colour must be true or false")
        settings.colour = raw
    if "company" in parsed:
        if not isinstance(parsed["company"], str):
            raise UsageError(f"invalid configuration {path}: company must be text")
        settings.company = " ".join(parsed["company"].split())
    base = path.parent
    if "vocabulary" in parsed:
        settings.vocabulary = _paths(parsed["vocabulary"], "vocabulary", base, path)
    if "templates" in parsed:
        settings.templates = _paths(parsed["templates"], "templates", base, path)
    return settings


def discover_config(explicit: str | None) -> Path | None:
    """Find the configuration file, if the user has one."""
    if explicit:
        path = Path(explicit)
        if not path.is_file():
            raise UsageError(f"configuration file not found: {path}")
        return path
    env = os.environ.get("CORPORATE_BULLSHIT_CONFIG")
    if env:
        path = Path(env)
        if not path.is_file():
            raise UsageError(f"configuration file not found: {path}")
        return path
    local = Path.cwd() / "corporate-bullshit.toml"
    if local.is_file():
        return local
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    home = base / "corporate-bullshit" / "config.toml"
    if home.is_file():
        return home
    return None


def _bounded(value: object, name: str, low: int, high: int, path: Path) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise UsageError(f"invalid configuration {path}: {name} must be an integer")
    if value < low or value > high:
        raise UsageError(f"invalid configuration {path}: {name} must be from {low} to {high}")
    return value


def _format(value: object, path: Path) -> str:
    if not isinstance(value, str):
        raise UsageError(f"invalid configuration {path}: format must be text")
    name = value.strip().lower()
    if name not in FORMATS:
        choices = ", ".join(FORMATS)
        raise UsageError(f"invalid configuration {path}: format must be one of: {choices}")
    return name


def _paths(value: object, name: str, base: Path, path: Path) -> list[Path]:
    if isinstance(value, str):
        raw_items: list[object] = [value]
    elif isinstance(value, list):
        raw_items = list(value)
    else:
        raise UsageError(f"invalid configuration {path}: {name} must be a path or a list of paths")
    paths: list[Path] = []
    for item in raw_items:
        if not isinstance(item, str) or not item.strip():
            raise UsageError(f"invalid configuration {path}: {name} entries must be paths")
        candidate = Path(item)
        if not candidate.is_absolute():
            candidate = base / candidate
        paths.append(candidate)
    return paths
