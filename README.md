# Reference Tarot Decks

This repository contains royalty-free tarot decks compliant with the [Tarot Deck Specification](https://github.com/arcanaland/specifications). It currently features the [Rider-Waite-Smith](https://en.wikipedia.org/wiki/Rider%E2%80%93Waite_Tarot) deck and the [Aquatic Tarot](http://www.aquatictarot.net/deck/tarot.html) deck.

## Key Features

- **Rider-Waite-Smith and Aquatic**: Two beginner-friendly tarot decks with metadata, images, and i18n files.
- **Specification Compliance**: Demonstrates proper directory structure, metadata (`deck.toml`), and localization.

## Directory Structure

```
my-tarot-deck/
  deck.toml                # Deck metadata
  card_backs/              # Card back images
  scalable/                # SVG images (e.g., major_arcana/00.svg)
  h750/, h1200/, h2400/    # Raster images in various resolutions
  names/                   # Localization files (e.g., en.toml)
```

## Licensing

Please view each deck's `deck.toml` for license details.

## Contributing

Contributions are welcome! Follow the [Tarot Deck Specification](https://github.com/arcanaland/specifications) and submit a pull request. 

--- 

For more details, visit the [specification repo](https://github.com/arcanaland/specifications).
