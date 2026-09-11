#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
#
# SPDX-FileCopyrightText: 2026 Adam Fidel
# SPDX-License-Identifier: MIT
"""Generate a machine-readable list of released decks.

gen_index.py            # print the generated index to stdout
gen_index.py --apply    # write it to index.json
gen_index.py --check
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import subprocess
import sys
import tomllib
import urllib.request
from pathlib import Path
from typing import Callable
from urllib.parse import quote

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = REPO_ROOT / "index.json"
REPO = "arcanaland/reference-decks"

FORMAT = 1
CONTAINER_EXT = ".tarotdeck"

# the order extensions are considered within a raster directory.
RASTER_CHAIN = ["png", "webp", "avif", "jpeg", "jpg"]

# [deck] keys copied into each entry. All of them must be present.
DECK_FIELDS = [
    "identifier",
    "name",
    "artist",
    "version",
    "schema_version",
    "license",
    "attribution",
    "description",
]

VERSION = re.compile(r"\d+(?:\.\d+)*")


class Unindexable(Exception):
    """A release that can't be indexed as it stands."""


# --- Pure functions ---------------------------------------------------------


def version_key(version: str) -> tuple[int, ...] | None:
    """Sort key for a dotted numeric version, so that 1.10 > 1.9."""
    if not VERSION.fullmatch(version):
        return None
    return tuple(int(part) for part in version.split("."))


def tag_version(tag: str, slug: str) -> str | None:
    prefix = f"{slug}/v"
    return tag[len(prefix) :] if tag.startswith(prefix) else None


def slugs(releases: list[dict]) -> list[str]:
    """Every deck with a <slug>/v<version> release."""
    found = set()
    for release in releases:
        slug, sep, rest = release["tag_name"].partition("/v")
        if sep and slug and "/" not in slug and version_key(rest):
            found.add(slug)
    return sorted(found)


def latest_release(releases: list[dict], slug: str) -> dict | None:
    """The published release with the highest version."""
    candidates = []
    for release in releases:
        if release.get("draft") or release.get("prerelease"):
            continue
        version = tag_version(release["tag_name"], slug)
        if version is None:
            continue
        key = version_key(version)
        if key is None:
            print(f"note: {release['tag_name']}: unparseable version, skipping", file=sys.stderr)
            continue
        candidates.append((key, release))
    return max(candidates, key=lambda c: c[0])[1] if candidates else None


def container_asset(release: dict) -> dict | None:
    assets = [a for a in release["assets"] if a["name"].endswith(CONTAINER_EXT)]
    if len(assets) > 1:
        names = ", ".join(a["name"] for a in assets)
        raise Unindexable(f"{release['tag_name']}: more than one container ({names})")
    return assets[0] if assets else None


def _heights(paths: list[str], slug: str) -> list[int]:
    heights = set()
    for path in paths:
        parts = path.split("/")
        if len(parts) > 2 and parts[0] == slug and (m := re.fullmatch(r"h(\d+)", parts[1])):
            heights.add(int(m.group(1)))
    return sorted(heights)


def _chain_rank(path: str) -> int | None:
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
    return RASTER_CHAIN.index(ext) if ext in RASTER_CHAIN else None


def cover_path(paths: list[str], slug: str) -> str | None:
    """The Fool from the smallest hNNN directory that has one."""
    for height in _heights(paths, slug):
        prefix = f"{slug}/h{height}/major_arcana/"
        fools = [
            (rank, p)
            for p in paths
            if p.startswith(prefix)
            and p[len(prefix) :].rsplit(".", 1)[0] == "00"
            and "/" not in p[len(prefix) :]
            and (rank := _chain_rank(p)) is not None
        ]
        if fools:
            return min(fools)[1]
    return None


def _card_ids(paths: list[str], slug: str, root: str | None) -> set[str]:
    ids = set()
    for path in paths:
        parts = path.split("/")
        if len(parts) < 4 or parts[0] != slug or (root and parts[1] != root):
            continue
        card = parts[2:]
        card[-1] = card[-1].rsplit(".", 1)[0]
        if (card[0] == "major_arcana" and len(card) == 2) or (
            card[0] == "minor_arcana" and len(card) == 3
        ):
            ids.add("/".join(card).lower())
    return ids


def card_count(paths: list[str], slug: str, cover: str | None) -> int:
    """Cards shipped at the cover's height, or across every root if there's no cover."""
    return len(_card_ids(paths, slug, cover.split("/")[1] if cover else None))


def raw_url(tag: str, path: str) -> str:
    ref = quote(f"refs/tags/{tag}", safe="/")
    return f"https://raw.githubusercontent.com/{REPO}/{ref}/{quote(path, safe='/')}"


def asset_sha256(asset: dict, download: Callable[[str, int], str]) -> str:
    """Bare hex digest."""
    digest = asset.get("digest")
    if digest:
        algo, _, hexdigest = digest.partition(":")
        if algo != "sha256" or not re.fullmatch(r"[0-9a-f]{64}", hexdigest):
            raise Unindexable(f"{asset['name']}: unexpected digest {digest!r}")
        return hexdigest
    return download(asset["browser_download_url"], asset["size"])


def deck_entry(
    slug: str,
    tag: str,
    deck_toml: str,
    paths: list[str],
    asset: dict,
    sha256: str,
) -> dict:
    """One `decks` entry, from deck.toml and the file list at the release tag."""
    meta = tomllib.loads(deck_toml).get("deck", {})
    missing = [k for k in DECK_FIELDS if k not in meta]
    if missing:
        raise Unindexable(f"{tag}: deck.toml has no {', '.join(missing)}")
    if tag != f"{slug}/v{meta['version']}":
        raise Unindexable(f"{tag}: deck.toml says version {meta['version']!r}")

    cover = cover_path(paths, slug)
    entry = {k: meta[k] for k in DECK_FIELDS}
    entry.update(
        slug=slug,
        card_count=card_count(paths, slug, cover),
        cover=raw_url(tag, cover) if cover else None,
        package={
            "url": asset["browser_download_url"],
            "size": asset["size"],
            "sha256": sha256,
        },
    )
    return entry


def render(entries: list[dict], source_commit: str) -> str:
    index = {
        "format": FORMAT,
        "source_commit": source_commit,
        "decks": sorted(entries, key=lambda e: e["slug"]),
    }
    return json.dumps(index, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def committed_source_commit(text: str) -> str | None:
    try:
        value = json.loads(text).get("source_commit")
    except (json.JSONDecodeError, AttributeError):
        return None
    return value if isinstance(value, str) else None


def drift(committed: str, generated: str) -> str:
    """A unified diff, empty when the two are byte-identical."""
    if committed == generated:
        return ""
    return "".join(
        difflib.unified_diff(
            committed.splitlines(keepends=True),
            generated.splitlines(keepends=True),
            "index.json (committed)",
            "index.json (generated)",
        )
    )


# --- git and gh -------------------------------------------------------------


def run(*args: str) -> str:
    proc = subprocess.run(
        args, cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8"
    )
    if proc.returncode != 0:
        sys.exit(f"{' '.join(args[:3])}: {proc.stderr.strip() or proc.returncode}")
    return proc.stdout


def list_releases() -> list[dict]:
    """Every release, across all pages of the API."""
    out = run("gh", "api", "--paginate", f"repos/{REPO}/releases?per_page=100")
    # --paginate concatenates one JSON array per page.
    decoder, releases, pos = json.JSONDecoder(), [], 0
    while pos < len(out):
        if out[pos].isspace():
            pos += 1
            continue
        page, pos = decoder.raw_decode(out, pos)
        releases.extend(page)
    return releases


def require_tag(tag: str) -> None:
    proc = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"refs/tags/{tag}^{{}}"],
        cwd=REPO_ROOT,
        capture_output=True,
    )
    if proc.returncode != 0:
        sys.exit(f"{tag}: released, but not a tag in this clone (git fetch --tags)")


def download_sha256(url: str, size: int) -> str:
    print(f"note: no digest from GitHub, downloading {url}", file=sys.stderr)
    digest, seen = hashlib.sha256(), 0
    with urllib.request.urlopen(url) as response:
        while chunk := response.read(1 << 20):
            digest.update(chunk)
            seen += len(chunk)
    if seen != size:
        sys.exit(f"{url}: downloaded {seen} bytes, GitHub says {size}")
    return digest.hexdigest()


def generate(source_commit: str) -> str:
    releases = list_releases()
    entries = []
    for slug in slugs(releases):
        release = latest_release(releases, slug)
        if release is None:
            continue
        tag = release["tag_name"]
        asset = container_asset(release)
        if asset is None:
            print(f"note: {tag}: no {CONTAINER_EXT} asset, leaving {slug} out", file=sys.stderr)
            continue
        require_tag(tag)
        deck_toml = run("git", "show", f"{tag}:{slug}/deck.toml")
        paths = run("git", "ls-tree", "-r", "--name-only", tag, "--", f"{slug}/").splitlines()
        entries.append(
            deck_entry(slug, tag, deck_toml, paths, asset, asset_sha256(asset, download_sha256))
        )
    return render(entries, source_commit)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="write index.json")
    mode.add_argument("--check", action="store_true", help="fail on drift")
    args = parser.parse_args()

    head = run("git", "rev-parse", "--short=7", "HEAD").strip()
    committed = INDEX_PATH.read_text(encoding="utf-8") if INDEX_PATH.exists() else ""

    try:
        # --check uses source_commit
        text = generate((committed_source_commit(committed) or head) if args.check else head)
    except Unindexable as e:
        sys.exit(str(e))

    if args.check:
        diff = drift(committed, text)
        if diff:
            sys.stdout.write(diff)
            print("index.json has drifted: run `just index --apply`", file=sys.stderr)
            return 1
        print("index.json: up to date")
        return 0
    if args.apply:
        INDEX_PATH.write_text(text, encoding="utf-8")
        print(f"wrote {INDEX_PATH.relative_to(REPO_ROOT)}", file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
