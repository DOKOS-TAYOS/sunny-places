from __future__ import annotations

import shutil
from pathlib import Path


def remove_path(target: Path) -> None:
    if target.is_dir():
        shutil.rmtree(target, ignore_errors=True)
    elif target.exists():
        target.unlink(missing_ok=True)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    for pattern in ("__pycache__", ".pytest_cache", "pytest-cache-files-*"):
        for match in root.rglob(pattern):
            if ".venv" in match.parts:
                continue
            remove_path(match)


if __name__ == "__main__":
    main()
