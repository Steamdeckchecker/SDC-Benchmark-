# SDC Benchmark Changelog

## Version 1.7.1 — October 2, 2026

### Added

- Added the detected game title to the PNG report header in the format
  `SDC BENCHMARK | GAME TITLE`.
- Added local Steam game-name lookup across the internal drive and additional
  Steam library folders, including microSD card libraries.
- Added game-name lookup for non-Steam shortcuts.

### Changed

- Increased the generated PNG report resolution to native Full HD
  (1920 × 1080 pixels).
- Increased the frametime graph's horizontal sampling resolution to take
  advantage of the larger output size.
- Added safe title normalization and truncation for long game names and
  unsupported special characters.
- Updated the English and German documentation for the new report features.

### Fallback behavior

- If no matching title can be found, the report uses `Steam App <ID>` so the
  measured application remains identifiable.

### Compatibility

- Title detection works locally and does not require an internet connection.
- The renderer continues to use only the Python standard library and does not
  require Pillow, NumPy, or matplotlib.
