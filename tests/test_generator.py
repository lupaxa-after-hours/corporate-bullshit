"""Generation, formatting, configuration, and exit codes."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from lupaxa.corporate_bullshit.catalogue import load_builtin, load_catalogue, pattern_problem
from lupaxa.corporate_bullshit.cli import main
from lupaxa.corporate_bullshit.exceptions import TemplateError, UsageError, VocabularyError
from lupaxa.corporate_bullshit.lexicon import WORDS
from lupaxa.corporate_bullshit.service import (
    bingo,
    document,
    email,
    excuse,
    generate,
    jargon_define,
    jargon_list,
    meeting,
    mission,
    strategy,
    translate,
)

REPEAT = re.compile(r"\b([A-Za-z][A-Za-z-]+)\s+\1\b", re.IGNORECASE)


def _assert_sentence(text: str) -> None:
    assert text
    assert "{" not in text
    assert "}" not in text
    assert "  " not in text
    assert not re.search(r"\bthe the\b", text, re.IGNORECASE)
    assert not re.search(r"\b(a|an)\s+\1\b", text, re.IGNORECASE)
    assert text[0].isupper() or text[0].isdigit()
    assert text[-1] in ".!?"
    assert REPEAT.search(text) is None


def test_builtin_templates_load() -> None:
    """Packaged vocabulary and templates are valid."""
    catalogue = load_builtin()
    assert catalogue.version == "1"
    assert len(catalogue.bingo) >= 48
    assert catalogue.jargon_lookup("synergy") is not None


def test_all_intensities_and_seed_repeat() -> None:
    """The same seed and level produce the same statements, and levels differ."""
    first = generate(level=3, count=5, seed=12345)
    second = generate(level=3, count=5, seed=12345)
    other = generate(level=1, count=5, seed=12345)
    assert first == second
    assert first != other
    assert len(set(first)) == 5
    for line in first + other:
        _assert_sentence(line)


def test_level_one_avoids_maximum_vocabulary() -> None:
    """Intensity 1 stays with the plain vocabulary."""
    catalogue = load_builtin()
    banned = {word.casefold() for word in WORDS["verb"][3]}
    for seed in range(30):
        for line in generate(level=1, count=3, seed=seed, catalogue=catalogue):
            folded = line.casefold()
            assert not any(word in folded for word in banned)


def test_meeting_and_excuse_categories() -> None:
    """Each meeting type and excuse topic produces a sentence."""
    for kind in (
        "agreement",
        "avoidance",
        "deflection",
        "followup",
        "strategy",
        "objection",
        "summary",
    ):
        text = meeting(kind=kind, seed=8, level=2)[0]
        _assert_sentence(text)
    for topic in (
        "deadline",
        "budget",
        "technical",
        "meeting",
        "report",
        "project",
        "performance",
        "communication",
    ):
        text = excuse(topic=topic, seed=8, level=2)[0]
        _assert_sentence(text)


def test_unknown_meeting_type() -> None:
    """Unknown categories are rejected."""
    with pytest.raises(UsageError):
        meeting(kind="karaoke")


def test_strategy_marks_kpis_as_fictional() -> None:
    """Strategy results carry an objective, a rationale, and a fictional KPI."""
    item = strategy(count=2, seed=11, level=3)[0]
    assert "objective" in item
    assert "rationale" in item
    assert item["fictional"] is True
    assert "kpi" in item
    _assert_sentence(str(item["objective"]))
    bare = strategy(count=1, seed=11, include_kpi=False)[0]
    assert "kpi" not in bare


def test_mission_inserts_company_literally() -> None:
    """A company name is copied through, including characters that look like placeholders."""
    text = mission(company="Acme {verb} Corp", seed=5, level=2)[0]
    assert "Acme {verb} Corp" in text
    without = text.replace("Acme {verb} Corp", "")
    assert "{" not in without


def test_email_structure() -> None:
    """Emails have a subject, greeting, body, and closing."""
    message = email(kind="followup", recipient="The Team", sender="Jordan Hale", paragraphs=3, seed=6, level=2)[0]
    assert message["subject"]
    assert message["greeting"] == "Dear The Team,"
    body = message["paragraphs"]
    assert isinstance(body, list)
    assert len(body) == 3
    assert message["closing"] == "Kind regards,"
    assert message["sender"] == "Jordan Hale"
    for paragraph in body:
        _assert_sentence(str(paragraph))


def test_jargon_lookup_list_and_unknown() -> None:
    """Jargon lookup ignores case, listing is sorted, and unknown terms fail clearly."""
    entry = jargon_define("  SyNeRgY ")
    assert entry.term == "Synergy"
    assert "departments" in entry.definition
    listed = jargon_list()
    assert listed == sorted(listed, key=str.casefold)
    assert "Synergy" in listed
    with pytest.raises(UsageError, match="unknown jargon term"):
        jargon_define("not-a-real-term")


def test_translate_rules_and_preservation() -> None:
    """Known lines are rewritten. Unknown lines stay put. Intensity changes the rewrite."""
    mild = translate("We need to finish this today", level=1)
    heavy = translate("We need to finish this today.", level=3)
    assert mild != heavy
    assert "strategically accelerate" in heavy
    assert translate("The cat sat on the mat", level=3) == "The cat sat on the mat"
    money = translate("We need more money", level=3)
    assert "investment" in money


def test_bingo_shape_free_space_and_uniqueness() -> None:
    """Cards use odd sizes, a centre free space, and no repeated terms."""
    for size in (3, 5, 7):
        cards = bingo(size=size, count=2, seed=12345)
        assert len(cards) == 2
        again = bingo(size=size, count=2, seed=12345)
        assert cards == again
        middle = size // 2
        for card in cards:
            assert len(card) == size
            assert card[middle][middle] == "FREE SPACE"
            terms = [cell for row in card for cell in row if cell != "FREE SPACE"]
            assert len(terms) == len(set(terms))
    with pytest.raises(UsageError):
        bingo(size=4)


def test_document_sections() -> None:
    """A strategy document has the expected sections and fictional KPIs."""
    doc = document(kind="strategy", company="Acme Corp", paragraphs=8, seed=3, level=2)[0]
    assert doc["title"] == "Acme Corp: Strategic Plan"
    sections = doc["sections"]
    assert isinstance(sections, list)
    headings = [str(section["heading"]) for section in sections if isinstance(section, dict)]
    assert "Executive Summary" in headings
    assert "Strategic Objectives" in headings
    assert "Key Performance Indicators (Fictional)" in headings
    assert "Conclusion" in headings
    kpi = next(section for section in sections if isinstance(section, dict) and section["fictional"])
    assert kpi["content"]


def test_invalid_placeholder_is_reported() -> None:
    """Templates with unknown placeholders are not accepted."""
    catalogue = load_builtin()
    problem = pattern_problem("Hello {not_a_category}.", catalogue.words, catalogue.patterns)
    assert problem is not None
    assert pattern_problem("We {verb} the {noun}.", catalogue.words, catalogue.patterns) is None


def test_user_vocabulary_skips_invalid_entries(tmp_path: Path) -> None:
    """Bad user entries are ignored. A file that is not TOML is an error."""
    path = tmp_path / "extra.toml"
    path.write_text(
        "\n".join(
            [
                "[words.verb]",
                '2 = ["blockchainise", "bad {verb}", ""]',
                "",
                "[[jargon]]",
                'term = "Wheelhouse"',
                'definition = "Already packaged."',
                "",
                "[patterns.statement]",
                '1 = ["Please {not_real} the {noun}.", "Please {verb} the {noun} today."]',
            ]
        ),
        encoding="utf-8",
    )
    catalogue = load_catalogue([path])
    assert catalogue.custom
    assert "blockchainise" in catalogue.words["verb"][2]
    assert any("braces" in warning for warning in catalogue.warnings)
    assert any("unknown placeholder" in warning for warning in catalogue.warnings)
    broken = tmp_path / "broken.toml"
    broken.write_text("this = [", encoding="utf-8")
    with pytest.raises(Exception, match="invalid template file"):
        load_catalogue([broken])


def test_missing_category_raises() -> None:
    """Rendering cannot invent a vocabulary category."""
    catalogue = load_builtin()
    with pytest.raises(VocabularyError):
        catalogue.pick("nope", 2, __import__("random").Random(1), set())


def test_cli_json_markdown_and_files(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """JSON is valid, Markdown uses structure, and files are protected."""
    assert main(["generate", "--seed", "5", "--format", "json", "--count", "2"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["mode"] == "generate"
    assert payload["seed"] == 5
    assert payload["level"] == 2
    assert len(payload["results"]) == 2

    assert main(["bingo", "--size", "5", "--seed", "5", "--format", "markdown"]) == 0
    markdown = capsys.readouterr().out
    assert "FREE SPACE" in markdown
    assert markdown.strip().startswith("|")

    destination = tmp_path / "out.txt"
    assert main(["generate", "--seed", "1", "--output", str(destination)]) == 0
    assert destination.read_text(encoding="utf-8").strip()
    assert main(["generate", "--seed", "1", "--output", str(destination)]) == 3
    assert main(["generate", "--seed", "1", "--output", str(destination), "--force"]) == 0
    missing = tmp_path / "missing" / "out.txt"
    assert main(["generate", "--output", str(missing)]) == 3


def test_config_defaults_and_cli_override(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Configuration supplies defaults and the command line replaces them."""
    path = tmp_path / "corporate-bullshit.toml"
    path.write_text('level = 1\nformat = "json"\ncount = 2\ncompany = "Config Co"\n', encoding="utf-8")
    assert main(["generate", "--config", str(path), "--seed", "9"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["level"] == 1
    assert payload["count"] == 2
    assert main(["generate", "--config", str(path), "--level", "3", "--seed", "9", "--format", "json"]) == 0
    overridden = json.loads(capsys.readouterr().out)
    assert overridden["level"] == 3


def test_invalid_arguments_and_translate_stdin(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """Bad arguments exit 2. Translate accepts stdin."""
    with pytest.raises(SystemExit) as caught:
        main(["generate", "--level", "9"])
    assert caught.value.code == 2
    with pytest.raises(SystemExit) as caught:
        main(["bingo", "--size", "4"])
    assert caught.value.code == 2
    assert main(["jargon", "--define", "nope"]) == 2
    assert main(["translate"]) == 2
    assert main(["meeting", "--type", "nope"]) == 2
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO("We need more money\n"))
    assert main(["translate", "--level", "2"]) == 0
    assert capsys.readouterr().out.strip()


def test_document_markdown_and_help() -> None:
    """Document Markdown has headings, and help exits 0."""
    from lupaxa.corporate_bullshit.formatting import render_result

    doc = document(kind="report", seed=2, paragraphs=4)[0]
    rendered = render_result({"mode": "document", "results": [doc]}, "markdown")
    assert rendered.startswith("# ")
    assert "## Executive Summary" in rendered
    with pytest.raises(SystemExit) as caught:
        main(["--help"])
    assert caught.value.code == 0


def test_template_error_type_exists() -> None:
    """Template failures use the vocabulary exit family."""
    assert TemplateError.code == 4
