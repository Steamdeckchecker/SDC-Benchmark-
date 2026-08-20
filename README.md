# SDC Benchmark

Decky-Loader-Plugin mit fünfsekündigem Start-Countdown, einstellbarer
Benchmark-Dauer, Statusanzeige, Tonsignalen sowie CSV- und PNG-Export. Die
Messung nutzt die Gamescope-Performance-Schnittstelle und zeichnet jeden
gemeldeten Frame mit FPS und Frametime auf.

Die Laufzeit ist von 30 Sekunden bis 6 Minuten in 30-Sekunden-Schritten
einstellbar. Der zuletzt erzeugte PNG-Bericht lässt sich direkt im Plugin in
einer Vollbild-Vorschau öffnen.

## Installation

Den Ordner `sdc-benchmark` aus dem Distributionsarchiv nach
`~/homebrew/plugins/` kopieren und Decky Loader beziehungsweise Steam neu
starten.

## Ausgabe

Messdateien und der zugehörige PNG-Bericht werden unter
`/home/deck/Downloads` gespeichert. Der integrierte Renderer verwendet nur die
Python-Standardbibliothek; `matplotlib`, NumPy, Pillow, `pip` und eine
Internetverbindung werden nicht benötigt.

Der PNG-Bericht wird in 1280 × 720 Pixeln erzeugt und enthält:

- FPS- und Frametime-Verlauf
- durchschnittliche FPS
- 1-%-Low-FPS
- P99- und maximale Frametime
- Messdauer und Anzahl der erfassten Frames
- SDC-Benchmark-Logo

## Messquelle

Gamescope liefert die Zeit zwischen zwei präsentierten Frames in Nanosekunden.
Das Plugin speichert daraus die Frametime in Millisekunden und berechnet den
zugehörigen FPS-Wert. Die Messung funktioniert im Steam-Deck-Gaming-Modus mit
einer Gamescope-Control-Schnittstelle ab Version 6. Beim Ende des Countdowns
muss das zu messende Spiel fokussiert sein.

## Build

```bash
pnpm install
pnpm run build
```

Das Projekt basiert auf dem offiziellen
[Decky Plugin Template](https://github.com/SteamDeckHomebrew/decky-plugin-template)
und verwendet `@decky/ui` sowie `@decky/api`. Die Protokolldefinition folgt
Valves `gamescope-control.xml`. Zusätzliche Python-Module liegen entsprechend
der Decky-Paketstruktur unter `py_modules/`.
