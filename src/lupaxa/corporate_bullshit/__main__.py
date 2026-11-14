"""Allow ``python -m lupaxa.corporate_bullshit`` to run the CLI."""

from __future__ import annotations

from lupaxa.corporate_bullshit.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
