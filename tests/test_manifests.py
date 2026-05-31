"""Every apps/*/*/manifest.toml parses and has required keys."""
from pathlib import Path

import toml

REPO = Path(__file__).resolve().parent.parent


def test_all_manifests_valid():
    bad = []
    for mf in (REPO / "apps").glob("*/*/manifest.toml"):
        try:
            data = toml.loads(mf.read_text(encoding="utf-8"))
        except Exception as e:
            bad.append(f"{mf}: parse error {e!r}")
            continue
        app = data.get("app", {})
        if "name" not in app or "version" not in app:
            bad.append(f"{mf}: missing app.name/version")
        reqs = data.get("requirements", {})
        for key in ("apt", "pip", "github"):
            v = reqs.get(key, [])
            if not isinstance(v, list):
                bad.append(f"{mf}: requirements.{key} not list")
    assert not bad, "\n".join(bad)
