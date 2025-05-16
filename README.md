# Reference Tarot Decks

This repository contains royalty-free tarot decks compliant with the [Tarot Deck Specification](https://github.com/arcanaland/specifications). It currently features the following decks:

- [Rider-Waite-Smith](https://en.wikipedia.org/wiki/Rider%E2%80%93Waite_Tarot)
- [Aquatic Tarot](http://www.aquatictarot.net/deck/tarot.html)
- [ASCII Tarot](https://github.com/lawreka/ascii-tarot)

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

All original code, workflows and documentation in this repository is licensed under the MIT license.

For non-original deck-specific assets, please see each deck's `deck.toml` for license details.

## Contributing

Contributions are welcome! Follow the [Tarot Deck Specification](https://github.com/arcanaland/specifications) and submit a pull request. 

--- 

For more details, visit the [specification repo](https://github.com/arcanaland/specifications).
