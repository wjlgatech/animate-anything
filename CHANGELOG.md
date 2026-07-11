# Changelog

All notable changes to this list are documented here (newest first).

## [Unreleased]
### Added
- **`/animate-anything` skill + engine** — turn a concept into a 3Blue1Brown-style ManimCommunity
  explainer, style-gated and rendered locally. Reverse-engineered Grant Sanderson's toolchain (target
  ManimCommunity, not ManimGL) and production style (palette incl. the `#333333` warm-grey canvas,
  role-based color, morph-to-show-equivalence, play→wait pacing) from `3b1b/videos` + `manimlib`.
  `scripts/animate.py {scaffold,lint,contract}` (stdlib, zero deps): scaffold a 5-beat scene, lint it
  0–100 against the style contract (gate slop in CI), print the contract. Golden `examples/odd_squares.py`
  renders without LaTeX and scores 100/100. Emit-the-composition, render-locally — no cloud video API.

### Added
- Initial release: ranked registry of animation tooling across 7 layers (CSS → AI-authored),
  the living knowledge-graph pipeline (README → `graph.json` → interactive map), `llms.txt`
  agent index, weekly link-freshness CI, and beginner→advanced roadmaps.
