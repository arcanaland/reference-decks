alias reuse := lint-reuse

default:
    @just --list

check: lint-reuse

# REUSE compliance of every file in the repo
lint-reuse:
    uvx reuse lint

# Render a deck's release notes (add --apply to splice into the live release)
release-notes deck *args:
    ./tools/release_notes.py {{deck}} {{args}}

# Fail if any live release body has drifted from the generated notes
check-release-notes:
    ./tools/release_notes.py --all --check
