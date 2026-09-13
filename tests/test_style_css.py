from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

CSS_PATH = Path(__file__).resolve().parents[1] / "web_dashboard" / "css" / "style.css"


def test_css_has_balanced_blocks_and_no_duplicate_selectors():
    css = CSS_PATH.read_text(encoding="utf-8")

    assert css.count("{") == css.count("}"), "CSS block balance is broken."

    no_media_css = re.sub(r"@media\s*\([^)]*\)\s*\{.*?\}", "", css, flags=re.IGNORECASE | re.DOTALL)
    selectors = []
    for match in re.findall(r"([^{]+)\s*\{", no_media_css):
        selector = match.strip()
        if selector and not selector.startswith("@"):
            selectors.append(selector)

    duplicates = {name: count for name, count in Counter(selectors).items() if count > 1}

    assert not duplicates, f"Duplicate CSS selectors detected in the base stylesheet: {sorted(duplicates)}"
