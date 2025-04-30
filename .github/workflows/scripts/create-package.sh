#!/bin/bash

# Get the version from the first parameter
VERSION=$1
TIMESTAMP=$2

# Check if version was provided
if [ -z "$VERSION" ]; then
  echo "ERROR: Version not provided" >&2
  exit 1
fi

# Format the package name
PACKAGE_NAME="rider-waite-smith-${VERSION}"
ZIP_FILE="${PACKAGE_NAME}.zip"

# Create a temporary directory for packaging
TEMP_DIR=$(mktemp -d)
DECK_DIR="${TEMP_DIR}/${PACKAGE_NAME}"

# Copy the rider-waite-smith directory to the temporary directory
mkdir -p "${DECK_DIR}"
cp -r rider-waite-smith/* "${DECK_DIR}/"

# Include metadata file with package info
cat >"${DECK_DIR}/PACKAGE-INFO.txt" <<EOL
Package: Rider-Waite-Smith Tarot Deck
Version: ${VERSION}
Build Date: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Created By: ${GITHUB_ACTOR:-"GitHub Actions"}
Repository: ${GITHUB_REPOSITORY:-"arcanaland/specifications"}

This package follows the Tarot Deck Specification v1.0.
EOL

# Create the zip file and suppress the output
(cd "${TEMP_DIR}" && zip -r "${ZIP_FILE}" "${PACKAGE_NAME}" >/dev/null)

# Check if zip command was successful
if [ $? -ne 0 ]; then
  echo "ERROR: Failed to create zip file" >&2
  rm -rf "${TEMP_DIR}"
  exit 1
fi

# Move the zip file to the current directory
mv "${TEMP_DIR}/${ZIP_FILE}" .

# Clean up the temporary directory
rm -rf "${TEMP_DIR}"

# Output just the filename, no other text
echo "${ZIP_FILE}"

