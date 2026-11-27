"""Command-line interface for corporate-bullshit."""

from __future__ import annotations

import argparse
import contextlib
import os
import sys
from pathlib import Path

from lupaxa.corporate_bullshit.catalogue import Catalogue, load_catalogue
from lupaxa.corporate_bullshit.config import Settings, load_settings
from lupaxa.corporate_bullshit.exceptions import CorporateBullshitError, IOProblem, UsageError
from lupaxa.corporate_bullshit.formatting import render_result
from lupaxa.corporate_bullshit.models import (
    BINGO_SIZES,
    DOCUMENT_TYPES,
    EMAIL_TYPES,
    EXCUSE_TOPICS,
    FORMATS,
    MAX_COUNT,
    MAX_LEVEL,
    MAX_PARAGRAPHS,
    MEETING_TYPES,
    MIN_COUNT,
    MIN_LEVEL,
    MIN_PARAGRAPHS,
    MISSION_TYPES,
)
from lupaxa.corporate_bullshit.service import bingo, document, email, excuse, generate, jargon_define, jargon_list, jargon_random, meeting, mission, strategy, translate
from lupaxa.corporate_bullshit.version import get_version


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    try:
        return _run(argv)
    except BrokenPipeError:
        with contextlib.suppress(OSError):
            sys.stdout.close()
        return 0
    except CorporateBullshitError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.code


def build_parser() -> argparse.ArgumentParser:
    """Return the corporate-bullshit argument parser."""
    parser = argparse.ArgumentParser(prog="corporate-bullshit", description="Generate convincingly meaningless corporate language.")
    parser.add_argument("--version", action="version", version=f"corporate-bullshit {get_version()}")
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument("--config", help="TOML configuration file.")
    shared.add_argument("--format", dest="output_format", help="text, json, or markdown.")
    shared.add_argument("--output", help="Write the result to this file.")
    shared.add_argument("--force", action="store_true", help="Overwrite an existing output file.")
    shared.add_argument("--verbose", action="store_true", help="Print diagnostics on stderr.")
    shared.add_argument("--quiet", action="store_true", help="Hide warnings.")
    shared.add_argument("--colour", action="store_true", help="Colour text labels.")
    shared.add_argument("--no-colour", action="store_true", help="Do not colour text labels.")
    shared.add_argument("--seed", type=int, default=None, help="Repeatable random seed.")

    generated = argparse.ArgumentParser(add_help=False, parents=[shared])
    generated.add_argument("--level", type=_level, default=None, help="Bullshit intensity, 1 to 3.")
    generated.add_argument("--count", type=_count, default=None, help=f"How many results, {MIN_COUNT} to {MAX_COUNT}.")

    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("generate", parents=[generated], help="Generate corporate statements.")

    meeting_parser = commands.add_parser("meeting", parents=[generated], help="Generate meeting contributions.")
    meeting_parser.add_argument("--type", dest="kind", default="random", help="Meeting contribution type.")

    excuse_parser = commands.add_parser("excuse", parents=[generated], help="Generate a corporate excuse.")
    excuse_parser.add_argument("--topic", default="random", help="What the excuse is about.")

    strategy_parser = commands.add_parser("strategy", parents=[generated], help="Generate strategic objectives.")
    strategy_parser.add_argument("--no-kpi", action="store_true", help="Omit the fictional KPI.")

    mission_parser = commands.add_parser("mission", parents=[generated], help="Generate mission or vision text.")
    mission_parser.add_argument("--type", dest="kind", default="mission", help="mission, vision, values, purpose, or random.")
    mission_parser.add_argument("--company", default=None, help="Company name, inserted as literal text.")

    email_parser = commands.add_parser("email", parents=[generated], help="Generate a corporate email.")
    email_parser.add_argument("--type", dest="kind", default="update", help="Email type.")
    email_parser.add_argument("--recipient", default="", help="Recipient name, inserted as literal text.")
    email_parser.add_argument("--sender", default="", help="Sender name, inserted as literal text.")
    email_parser.add_argument("--paragraphs", type=_paragraphs, default=None, help="Body paragraph count.")
    email_parser.add_argument("--company", default=None, help="Company name, inserted as literal text.")

    jargon_parser = commands.add_parser("jargon", parents=[shared], help="Define or list corporate jargon.")
    jargon_parser.add_argument("--define", default=None, help="Look up a term. Matching ignores case.")
    jargon_parser.add_argument("--list", action="store_true", help="List known terms.")
    jargon_parser.add_argument("--count", type=_count, default=None, help="How many random terms to show.")

    translate_parser = commands.add_parser("translate", parents=[shared], help="Rewrite plain English as corporate English.")
    translate_parser.add_argument("text", nargs="?", help="Text to translate. Reads stdin when omitted.")
    translate_parser.add_argument("--level", type=_level, default=None, help="Bullshit intensity, 1 to 3.")

    bingo_parser = commands.add_parser("bingo", parents=[shared], help="Generate a buzzword bingo card.")
    bingo_parser.add_argument("--count", type=_count, default=None, help=f"How many cards, {MIN_COUNT} to {MAX_COUNT}.")
    bingo_parser.add_argument("--size", type=_bingo_size, default=5, help="Odd grid size: 3, 5, or 7.")

    document_parser = commands.add_parser("document", parents=[generated], help="Generate a fictional document.")
    document_parser.add_argument("--type", dest="kind", default="strategy", help="Document type.")
    document_parser.add_argument("--paragraphs", type=_paragraphs, default=None, help="Paragraph budget for the document.")
    document_parser.add_argument("--company", default=None, help="Company name, inserted as literal text.")
    return parser


def _run(argv: list[str] | None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.verbose and args.quiet:
        parser.error("--verbose and --quiet cannot be combined")
    if args.colour and args.no_colour:
        parser.error("--colour and --no-colour cannot be combined")
    settings = load_settings(args.config)
    level = settings.level if getattr(args, "level", None) is None else args.level
    count = settings.count if getattr(args, "count", None) is None else args.count
    paragraphs = settings.paragraphs if getattr(args, "paragraphs", None) is None else args.paragraphs
    output_format = _resolve_format(args.output_format, settings)
    company = _resolve_company(args, settings)
    catalogue = load_catalogue([*settings.vocabulary, *settings.templates])
    if catalogue.warnings and not args.quiet:
        for warning in catalogue.warnings:
            print(f"warning: {warning}", file=sys.stderr)
    payload = _dispatch(args, level=level, count=count, paragraphs=paragraphs, company=company, catalogue=catalogue)
    if args.verbose:
        bits = [
            f"command={args.command}",
            f"format={output_format}",
            f"vocabulary={catalogue.version}",
        ]
        if "level" in payload:
            bits.append(f"level={payload['level']}")
        if args.seed is not None:
            bits.append(f"seed={args.seed}")
        print("corporate-bullshit: " + " ".join(bits), file=sys.stderr)
    text = render_result(payload, output_format, colour=_use_colour(args, settings, output_format))
    _emit(text, args.output, args.force)
    if args.verbose and args.output:
        print(f"corporate-bullshit: wrote {args.output}", file=sys.stderr)
    return 0


def _dispatch(args: argparse.Namespace, *, level: int, count: int, paragraphs: int, company: str, catalogue: Catalogue) -> dict[str, object]:
    """Build the structured result for one command."""
    command = args.command
    seed = args.seed
    base: dict[str, object] = {
        "mode": command,
        "vocabulary_version": catalogue.version,
    }
    if seed is not None:
        base["seed"] = seed

    if command == "generate":
        base["level"] = level
        base["count"] = count
        base["results"] = generate(level=level, count=count, seed=seed, catalogue=catalogue)
        return base
    if command == "meeting":
        _known(args.kind, MEETING_TYPES, "meeting type")
        base["level"] = level
        base["type"] = args.kind
        base["count"] = count
        base["results"] = meeting(kind=args.kind, level=level, count=count, seed=seed, catalogue=catalogue)
        return base
    if command == "excuse":
        _known(args.topic, EXCUSE_TOPICS, "excuse topic")
        base["level"] = level
        base["topic"] = args.topic
        base["count"] = count
        base["results"] = excuse(topic=args.topic, level=level, count=count, seed=seed, catalogue=catalogue)
        return base
    if command == "strategy":
        base["level"] = level
        base["count"] = count
        base["results"] = strategy(level=level, count=count, seed=seed, include_kpi=not args.no_kpi, catalogue=catalogue)
        return base
    if command == "mission":
        _known(args.kind, MISSION_TYPES, "mission type")
        base["level"] = level
        base["type"] = args.kind
        base["count"] = count
        if company:
            base["company"] = company
        base["results"] = mission(kind=args.kind, company=company, level=level, count=count, seed=seed, catalogue=catalogue)
        return base
    if command == "email":
        _known(args.kind, EMAIL_TYPES, "email type")
        recipient = _literal(args.recipient)
        sender = _literal(args.sender)
        base["level"] = level
        base["type"] = args.kind
        base["count"] = count
        base["paragraphs"] = paragraphs
        base["results"] = email(kind=args.kind, recipient=recipient, sender=sender, paragraphs=paragraphs, company=company, level=level, count=count, seed=seed, catalogue=catalogue)
        return base
    if command == "jargon":
        return _jargon(args, base, count, catalogue)
    if command == "translate":
        base["level"] = level
        source = _translate_input(args.text)
        base["input"] = source
        base["output"] = translate(source, level=level)
        return base
    if command == "bingo":
        base["size"] = args.size
        base["count"] = count
        base["cards"] = bingo(size=args.size, count=count, seed=seed, catalogue=catalogue)
        return base
    if command == "document":
        _known(args.kind, DOCUMENT_TYPES, "document type")
        base["level"] = level
        base["type"] = args.kind
        base["count"] = count
        base["paragraphs"] = paragraphs
        if company:
            base["company"] = company
        base["results"] = document(kind=args.kind, company=company, paragraphs=paragraphs, level=level, count=count, seed=seed, catalogue=catalogue)
        return base
    raise UsageError(f"unknown command: {command}")


def _jargon(args: argparse.Namespace, base: dict[str, object], count: int, catalogue: Catalogue) -> dict[str, object]:
    if args.define and args.list:
        raise UsageError("--define and --list cannot be combined")
    if args.define is not None:
        if args.count is not None:
            raise UsageError("--define and --count cannot be combined")
        found = jargon_define(args.define, catalogue=catalogue)
        base["entries"] = [{"term": found.term, "definition": found.definition}]
        return base
    if args.list:
        if args.count is not None:
            raise UsageError("--list and --count cannot be combined")
        base["list"] = True
        entries = []
        for term in jargon_list(catalogue=catalogue):
            found = jargon_define(term, catalogue=catalogue)
            entries.append({"term": found.term, "definition": found.definition})
        base["entries"] = entries
        return base
    picked = jargon_random(count=count, seed=args.seed, catalogue=catalogue)
    base["count"] = count
    base["entries"] = [{"term": entry.term, "definition": entry.definition} for entry in picked]
    return base


def _translate_input(text: str | None) -> str:
    if text is not None:
        if not text.strip():
            raise UsageError("missing input text")
        return text.strip()
    if sys.stdin.isatty():
        raise UsageError("missing input text")
    try:
        incoming = sys.stdin.read()
    except OSError as exc:
        raise UsageError("missing input text") from exc
    if not incoming.strip():
        raise UsageError("missing input text")
    return incoming.strip()


def _emit(text: str, destination: str | None, force: bool) -> None:
    if not text.endswith("\n"):
        text += "\n"
    if not destination:
        sys.stdout.write(text)
        sys.stdout.flush()
        return
    path = Path(destination)
    if path.exists() and path.is_dir():
        raise IOProblem(f"output path is a directory: {path}")
    if path.exists() and not force:
        raise IOProblem(f"output file exists: {path} (pass --force to overwrite)")
    try:
        path.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise IOProblem(f"cannot write {path}: {exc.strerror or exc}") from exc


def _resolve_format(raw: str | None, settings: Settings) -> str:
    name = (raw or settings.output_format).strip().lower()
    if name not in FORMATS:
        choices = ", ".join(FORMATS)
        raise UsageError(f"format must be one of: {choices}")
    return name


def _resolve_company(args: argparse.Namespace, settings: Settings) -> str:
    supplied = getattr(args, "company", None)
    if supplied is None:
        return settings.company
    return _literal(supplied)


def _literal(value: str) -> str:
    return " ".join(value.split())


def _use_colour(args: argparse.Namespace, settings: Settings, output_format: str) -> bool:
    if args.output or output_format != "text" or not sys.stdout.isatty():
        return False
    if "NO_COLOR" in os.environ:
        return False
    if args.no_colour:
        return False
    if args.colour:
        return True
    return settings.colour


def _known(value: str, allowed: tuple[str, ...], label: str) -> None:
    if value not in allowed:
        names = ", ".join(allowed)
        raise UsageError(f"unknown {label} '{value}'. Choose one of: {names}")


def _level(value: str) -> int:
    return _integer(value, "level", MIN_LEVEL, MAX_LEVEL)


def _count(value: str) -> int:
    return _integer(value, "count", MIN_COUNT, MAX_COUNT)


def _paragraphs(value: str) -> int:
    return _integer(value, "paragraphs", MIN_PARAGRAPHS, MAX_PARAGRAPHS)


def _bingo_size(value: str) -> int:
    try:
        size = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("size must be an integer") from exc
    if size not in BINGO_SIZES:
        raise argparse.ArgumentTypeError("size must be 3, 5, or 7")
    return size


def _integer(value: str, name: str, low: int, high: int) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{name} must be an integer") from exc
    if number < low or number > high:
        raise argparse.ArgumentTypeError(f"{name} must be from {low} to {high}")
    return number
