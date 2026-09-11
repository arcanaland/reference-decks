# SPDX-FileCopyrightText: 2026 Adam Fidel
# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "release_notes", Path(__file__).with_name("release_notes.py")
)
release_notes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release_notes)


class FakeTree:
    def __init__(self, deck, files):
        self.deck = deck
        self.ref = None
        self.files = files
        self.paths = sorted(files)

    def read(self, path):
        return self.files[path]

    def has(self, path):
        return path in self.files


def test_installing_a_container_names_the_deck_directory():
    text = release_notes.installing("aquatic-tarot", "aquatic-tarot-2.0.tarotdeck")
    assert "$ unzip aquatic-tarot-2.0.tarotdeck -d ~/.local/share/tarot/decks/aquatic-tarot\n" in text
    assert (
        "$ unzip aquatic-tarot-2.0.tarotdeck -d "
        "~/.var/app/land.arcana.TarotCanvas/data/tarot/decks/aquatic-tarot\n"
    ) in text


def test_installing_a_legacy_zip_unpacks_into_decks():
    # The old zips wrap the deck directory themselves.
    text = release_notes.installing("aquatic-tarot", "aquatic-tarot-1.0.zip")
    assert "$ unzip aquatic-tarot-1.0.zip -d ~/.local/share/tarot/decks\n" in text


def test_licensing_reads_2_0_keys():
    meta = {
        "license": "MIT",
        "artist": "A. Artist",
        "links": [
            {"rel": "homepage", "url": "https://example.com"},
            {"rel": "buy", "url": "https://example.com/shop", "title": "Shop"},
        ],
    }
    text = release_notes.licensing(meta, FakeTree("example", {}), "o/r", "example/v2.0")
    assert "- **Artist:** A. Artist" in text
    assert "- **Links:** [homepage](https://example.com), [Shop](https://example.com/shop)" in text


def test_licensing_still_reads_1_0_keys():
    meta = {"license": "MIT", "author": "A. Artist", "website": "https://example.com"}
    text = release_notes.licensing(meta, FakeTree("example", {}), "o/r", "example/v1.0")
    assert "- **Artist:** A. Artist" in text
    assert "- **Website:** https://example.com" in text


def test_card_names_read_both_name_file_shapes():
    v2 = FakeTree("d", {"d/names/en.toml": '[name.card.major_arcana]\n00 = "Le Mat"\n'})
    v1 = FakeTree("d", {"d/names/en.toml": '[major_arcana]\n00 = "Le Mat"\n'})
    assert release_notes.card_names(v2) == {"00": "Le Mat"}
    assert release_notes.card_names(v1) == {"00": "Le Mat"}
