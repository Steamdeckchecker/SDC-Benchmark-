# SDC Benchmark – Änderungsverlauf

## Version 1.7.1 — 2. Oktober 2026

### Neu

- Der erkannte Spielname wird jetzt im Format
  `SDC BENCHMARK | SPIELNAME` in der Kopfzeile des PNG-Berichts angezeigt.
- Steam-Spiele werden lokal auf dem internen Speicher und in zusätzlichen
  Steam-Bibliotheken einschließlich microSD-Karten erkannt.
- Spielnamen von Steam-fremden Verknüpfungen werden ebenfalls lokal ermittelt.

### Geändert

- Die erzeugten PNG-Berichte werden jetzt nativ in Full HD mit
  1920 × 1080 Pixeln erstellt.
- Die horizontale Abtastauflösung des Frametime-Diagramms wurde erhöht, damit
  die größere Bildauflösung sinnvoll genutzt wird.
- Lange Spielnamen und nicht unterstützte Sonderzeichen werden sicher
  angepasst beziehungsweise gekürzt.
- Die deutsche und englische Dokumentation wurde um die neuen
  Berichtsfunktionen erweitert.

### Fallback-Verhalten

- Kann kein passender Spielname ermittelt werden, verwendet der Bericht
  `Steam App <ID>`. Dadurch bleibt die gemessene Anwendung identifizierbar.

### Kompatibilität

- Die Erkennung des Spielnamens erfolgt vollständig lokal und benötigt keine
  Internetverbindung.
- Der Renderer verwendet weiterhin ausschließlich die Python-Standardbibliothek
  und benötigt weder Pillow noch NumPy oder matplotlib.
