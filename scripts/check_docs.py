#!/usr/bin/env python3
"""Check local Markdown links/anchors and SVG syntax without network access."""
from collections import Counter
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def anchors(path):
    result, counts = set(), Counter()
    for heading in re.findall(r"^#{1,6}\s+(.+)$", path.read_text(), re.MULTILINE):
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        result.add(slug if not counts[slug] else f"{slug}-{counts[slug]}")
        counts[slug] += 1
    return result


def main():
    failures = []
    checked = 0
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        for target in re.findall(r"\]\(([^)\s]+)\)", path.read_text()):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc:
                continue
            checked += 1
            resolved = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            if not resolved.exists():
                failures.append(f"{path.relative_to(ROOT)}: missing {target}")
            elif parsed.fragment and resolved.suffix == ".md" and unquote(parsed.fragment) not in anchors(resolved):
                failures.append(f"{path.relative_to(ROOT)}: missing anchor {target}")
    for path in (ROOT / "docs" / "assets").glob("*.svg"):
        try:
            ET.parse(path)
        except ET.ParseError as error:
            failures.append(f"{path.relative_to(ROOT)}: {error}")
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"Checked {checked} local documentation links and SVG syntax.")


if __name__ == "__main__":
    main()
