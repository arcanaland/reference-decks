# SPDX-FileCopyrightText: 2026 Adam Fidel
# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "gen_index", Path(__file__).with_name("gen_index.py")
)
gen_index = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen_index)

DIGEST = "ab" * 32

DECK_TOML = """\
[deck]
schema_version = "2.0"
name = "Example Tarot"
identifier = "land.arcana/deck/example"
artist = "A. Artist"
version = "1.10"
license = "CC0-1.0"
attribution = "Art by A. Artist."
description = "An example."
tags = ["not-indexed"]
"""


def release(tag, *assets, draft=False, prerelease=False):
    return {
        "tag_name": tag,
        "draft": draft,
        "prerelease": prerelease,
        "assets": [
            {
                "name": name,
                "size": 100,
                "digest": f"sha256:{DIGEST}",
                "browser_download_url": f"https://example.invalid/{tag}/{name}",
            }
            for name in assets
        ],
    }


def full_deck(slug, root, ext):
    majors = [f"{slug}/{root}/major_arcana/{i:02d}.{ext}" for i in range(22)]
    ranks = "ace two three four five six seven eight nine ten page knight queen king".split()
    minors = [
        f"{slug}/{root}/minor_arcana/{suit}/{rank}.{ext}"
        for suit in ("wands", "cups", "swords", "pentacles")
        for rank in ranks
    ]
    return majors + minors


# --- Choosing a release -----------------------------------------------------


def test_version_ordering_is_numeric():
    releases = [
        release("example/v1.9", "example-1.9.tarotdeck"),
        release("example/v1.10", "example-1.10.tarotdeck"),
        release("example/v1.2", "example-1.2.tarotdeck"),
    ]
    assert gen_index.latest_release(releases, "example")["tag_name"] == "example/v1.10"


def test_latest_release_ignores_other_decks_with_a_shared_prefix():
    releases = [
        release("example/v1.0"),
        release("example-two/v9.0"),
    ]
    assert gen_index.latest_release(releases, "example")["tag_name"] == "example/v1.0"
    assert gen_index.slugs(releases) == ["example", "example-two"]


def test_latest_release_skips_drafts_and_prereleases():
    releases = [
        release("example/v1.0"),
        release("example/v2.0", draft=True),
        release("example/v3.0", prerelease=True),
    ]
    assert gen_index.latest_release(releases, "example")["tag_name"] == "example/v1.0"


def test_no_tarotdeck_asset_means_no_container():
    assert gen_index.container_asset(release("example/v1.1", "example-1.1.zip")) is None


def test_container_asset_is_found_beside_other_assets():
    r = release("example/v2.0", "example-2.0.zip", "example-2.0.tarotdeck")
    assert gen_index.container_asset(r)["name"] == "example-2.0.tarotdeck"


def test_two_containers_is_an_error():
    r = release("example/v2.0", "a.tarotdeck", "b.tarotdeck")
    with pytest.raises(gen_index.Unindexable):
        gen_index.container_asset(r)


# --- Cover and card count ---------------------------------------------------


def test_cover_is_the_fool_at_the_smallest_height():
    paths = (
        full_deck("example", "h2400", "png")
        + full_deck("example", "h750", "webp")
        + full_deck("example", "h1200", "png")
        + ["example/deck.toml", "example/card_backs/classic.png"]
    )
    assert gen_index.cover_path(paths, "example") == "example/h750/major_arcana/00.webp"


def test_cover_compares_heights_numerically():
    paths = ["example/h1200/major_arcana/00.png", "example/h800/major_arcana/00.jpg"]
    assert gen_index.cover_path(paths, "example") == "example/h800/major_arcana/00.jpg"


def test_cover_follows_the_extension_chain():
    paths = ["example/h800/major_arcana/00.jpg", "example/h800/major_arcana/00.webp"]
    assert gen_index.cover_path(paths, "example") == "example/h800/major_arcana/00.webp"


def test_cover_skips_a_height_without_a_fool():
    paths = ["example/h500/major_arcana/01.png", "example/h800/major_arcana/00.png"]
    assert gen_index.cover_path(paths, "example") == "example/h800/major_arcana/00.png"


def test_no_raster_height_means_no_cover():
    paths = ["example/ansi32/major_arcana/00.ansi", "example/scalable/major_arcana/00.svg"]
    assert gen_index.cover_path(paths, "example") is None


def test_card_count_at_cover_height():
    paths = full_deck("example", "h800", "jpg") + full_deck("example", "h1200", "png")[:22]
    cover = gen_index.cover_path(paths, "example")
    assert gen_index.card_count(paths, "example", cover) == 78


def test_card_count_majors_only():
    paths = full_deck("example", "h800", "jpg")[:22] + ["example/h800/card_backs/x.jpg"]
    cover = gen_index.cover_path(paths, "example")
    assert gen_index.card_count(paths, "example", cover) == 22


def test_card_count_without_a_cover_counts_every_root():
    paths = full_deck("example", "ansi32", "ansi") + full_deck("example", "scalable", "svg")
    assert gen_index.card_count(paths, "example", None) == 78


# --- sha256 -----------------------------------------------------------------


def test_sha256_uses_githubs_digest():
    def download(url, size):
        raise AssertionError("should not download")

    asset = release("example/v1.0", "example-1.0.tarotdeck")["assets"][0]
    assert gen_index.asset_sha256(asset, download) == DIGEST


def test_sha256_falls_back_to_downloading():
    calls = []

    def download(url, size):
        calls.append((url, size))
        return "cd" * 32

    asset = release("example/v1.0", "example-1.0.tarotdeck")["assets"][0]
    asset["digest"] = None
    assert gen_index.asset_sha256(asset, download) == "cd" * 32
    assert calls == [(asset["browser_download_url"], 100)]


def test_sha256_rejects_another_algorithm():
    asset = release("example/v1.0", "example-1.0.tarotdeck")["assets"][0]
    asset["digest"] = "sha512:" + "ab" * 64
    with pytest.raises(gen_index.Unindexable):
        gen_index.asset_sha256(asset, lambda url, size: "")


# --- Entries and output -----------------------------------------------------


def entry():
    asset = release("example/v1.10", "example-1.10.tarotdeck")["assets"][0]
    paths = full_deck("example", "h800", "jpg")
    return gen_index.deck_entry("example", "example/v1.10", DECK_TOML, paths, asset, DIGEST)


def test_entry_has_exactly_the_contract_fields():
    e = entry()
    assert sorted(e) == sorted(
        [
            "slug", "identifier", "name", "artist", "version", "schema_version",
            "license", "attribution", "description", "card_count", "cover", "package",
        ]
    )
    assert e["package"] == {
        "url": "https://example.invalid/example/v1.10/example-1.10.tarotdeck",
        "size": 100,
        "sha256": DIGEST,
    }
    assert e["cover"] == (
        "https://raw.githubusercontent.com/arcanaland/reference-decks/"
        "refs/tags/example/v1.10/example/h800/major_arcana/00.jpg"
    )
    assert e["card_count"] == 78


def test_entry_fails_loudly_without_an_artist():
    toml = DECK_TOML.replace('artist = "A. Artist"\n', "")
    asset = release("example/v1.10", "example-1.10.tarotdeck")["assets"][0]
    with pytest.raises(gen_index.Unindexable, match="artist"):
        gen_index.deck_entry("example", "example/v1.10", toml, [], asset, DIGEST)


def test_entry_fails_when_deck_toml_disagrees_with_the_tag():
    asset = release("example/v1.9", "example-1.9.tarotdeck")["assets"][0]
    with pytest.raises(gen_index.Unindexable, match="version"):
        gen_index.deck_entry("example", "example/v1.9", DECK_TOML, [], asset, DIGEST)


def test_output_is_byte_stable():
    a, b = entry(), entry()
    b["slug"] = "aaa-first"
    first = gen_index.render([a, b], "d94106a")
    second = gen_index.render([b, a], "d94106a")
    assert first == second
    assert first.endswith("}\n") and not first.endswith("\n\n")
    assert first == json.dumps(json.loads(first), indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    assert [d["slug"] for d in json.loads(first)["decks"]] == ["aaa-first", "example"]


def test_empty_index():
    assert gen_index.render([], "d94106a") == (
        '{\n  "decks": [],\n  "format": 1,\n  "source_commit": "d94106a"\n}\n'
    )


def test_drift():
    text = gen_index.render([], "d94106a")
    assert gen_index.drift(text, text) == ""
    assert "-  \"format\": 2" in gen_index.drift(text.replace("1", "2"), text)
    assert gen_index.committed_source_commit(text) == "d94106a"
    assert gen_index.committed_source_commit("not json") is None
