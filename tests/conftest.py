"""Keep tests away from a developer's real configuration file."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _isolated_config(monkeypatch: pytest.MonkeyPatch, tmp_path_factory: pytest.TempPathFactory) -> None:
    root = tmp_path_factory.mktemp("config-home")
    monkeypatch.chdir(root)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(root / "xdg"))
    monkeypatch.delenv("CORPORATE_BULLSHIT_CONFIG", raising=False)
    monkeypatch.delenv("NO_COLOR", raising=False)
