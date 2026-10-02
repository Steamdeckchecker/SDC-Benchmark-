# Changelog

## 1.7.1

### Added

- Added the detected game title to the PNG report header in the format
  `SDC BENCHMARK | GAME TITLE`.
- Added Steam game-name lookup across the internal drive and additional Steam
  library folders, including microSD card libraries.
- Added game-name lookup for non-Steam shortcuts.

### Changed

- Increased the generated PNG report resolution to native Full HD
  (1920 × 1080 pixels).
- Increased the frametime graph's horizontal sampling resolution to take
  advantage of the larger output size.
- Added safe title normalization and truncation for long game names.

### Fallback behavior

- If no matching title can be found, the report uses `Steam App <ID>` so the
  measured application remains identifiable.
