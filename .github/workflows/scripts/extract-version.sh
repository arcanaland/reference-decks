#!/bin/bash

# Extract version from deck.toml
VERSION=$(grep -E '^version\s*=\s*"[^"]+"' rider-waite-smith/deck.toml | sed -E 's/^version\s*=\s*"([^"]+)"/\1/')

# Check if version was found
if [ -z "$VERSION" ]; then
  echo "ERROR: Version not found in deck.toml" >&2
  exit 1
fi

# Output the version
echo "$VERSION"