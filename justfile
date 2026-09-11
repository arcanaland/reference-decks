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

# Render index.json to stdout (pass --apply or --check)
index *args:
    ./tools/gen_index.py {{args}}

# Fail if index.json has drifted from the live releases (needs gh)
check-index:
    ./tools/gen_index.py --check

# Unit tests for the tools
test-tools:
    uv run --with pytest pytest tools/
