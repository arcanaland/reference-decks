# Reference Tarot Decks

This repository provides example tarot decks created using the [Tarot Deck Specification v1.0](https://github.com/arcanaland/specifications). It currently features the **Rider-Waite-Smith Tarot Deck**.

## Key Features

- **Rider-Waite-Smith Deck**: A classic, beginner-friendly tarot deck with metadata, images, and i18n files.
- **Specification Compliance**: Demonstrates proper directory structure, metadata (`deck.toml`), and localization.

## Directory Structure

```
rider-waite-smith/
  deck.toml                # Deck metadata
  card_backs/              # Card back images
  scalable/                # SVG images (e.g., major_arcana/00.svg)
  h750/, h1200/, h2400/    # Raster images in various resolutions
  names/                   # Localization files (e.g., en.toml)
```

## Licensing

The Rider-Waite-Smith deck is Public Domain. See `deck.toml` for details.

## Contributing

Contributions are welcome! Follow the [Tarot Deck Specification](https://github.com/arcanaland/specifications) and submit a pull request. 

--- 

For more details, visit the [specification repo](https://github.com/arcanaland/specifications).
