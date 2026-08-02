# Reference Tarot Decks

This repository contains tarot decks that are public domain, open source, or Creative Commons-licensed in accordance with the [Tarot Deck Specification](https://github.com/arcanaland/specifications). It currently features the following decks:

| Deck | License | |
| --- | --- | --- |
| [Rider-Waite-Smith](https://en.wikipedia.org/wiki/Rider%E2%80%93Waite_Tarot) | `LicenseRef-PublicDomain AND CC0-1.0` | Artwork public domain (1909); digital restoration CC0 |
| [Aquatic Tarot](http://www.aquatictarot.net/deck/tarot.html) | `CC-BY-NC-SA-3.0` | |
| [ASCII Tarot](https://github.com/lawreka/ascii-tarot)` | `MIT` | |

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

All original code and documentation in this repository is licensed under the MIT license.

Card artwork is not original to this project. Each deck directory contains a `LICENSE` file with the applicable license text, copyright notice and required attribution.

## Contributing

Contributions are welcome! Follow the [Tarot Deck Specification](https://github.com/arcanaland/specifications) and submit a pull request. 
