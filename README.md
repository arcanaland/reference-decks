# Reference Tarot Decks

This repository contains tarot decks that are public domain, open source, or Creative Commons-licensed in accordance with the [Tarot Deck Specification](https://github.com/arcanaland/specifications). It currently features the following decks:

| Deck | License | |
| --- | --- | --- |
| [Rider-Waite-Smith](https://en.wikipedia.org/wiki/Rider%E2%80%93Waite_Tarot) | `LicenseRef-PublicDomain AND CC0-1.0` | Artwork public domain (1909); digital restoration CC0 |
| [Aquatic Tarot](http://www.aquatictarot.net/deck/tarot.html) | `CC-BY-NC-SA-3.0` | Noncommercial use only |
| [ASCII Tarot](https://github.com/lawreka/ascii-tarot) | `MIT` | |

## Deck Directory Structure

```
my-tarot-deck/
  deck.toml                # Deck metadata
  card_backs/              # Card back images
  scalable/                # SVG images (e.g., major_arcana/00.svg)
  h750/, h1200/, h2400/    # Raster images in various resolutions
  ansi32/, ansi50/         # Text-based art (ANSI and ASCII) for various heights
  names/                   # Localization files (e.g., en.toml)
```

## Licensing

This repository has no single license. Each deck contains its own terms.

All original code, documentation and deck packaging metadata is licensed under the MIT license. Card artwork is not original to this project and is licensed by its respective rights holders.

Per-file licensing is declared machine-readably in [`REUSE.toml`](./REUSE.toml) and full license texts are in [`LICENSES/`](./LICENSES/).

## Contributing

Contributions are welcome! Follow the [Tarot Deck Specification](https://github.com/arcanaland/specifications) and submit a pull request. 
