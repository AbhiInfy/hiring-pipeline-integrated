from __future__ import annotations

from pathlib import Path


def load_env_file(path: Path, *, override: bool = False) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key:
            continue

        if override or key not in __import__("os").environ:
            __import__("os").environ[key] = value


def load_project_env(integration_root: Path) -> None:
    load_env_file(integration_root / ".env", override=False)
    load_env_file(integration_root / "src" / ".env", override=False)
