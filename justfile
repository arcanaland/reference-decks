default:
    @just --list

check: reuse

reuse:
    uvx reuse lint
