import base64
import csv
import datetime
import math
import os
import sys
import threading
import time

import decky

# Decky lädt ``main.py`` per ``spec_from_file_location``. Dadurch befindet sich
# der Plugin-Ordner nicht zuverlässig in ``sys.path``. Nur ``py_modules`` ist
# laut Template für zusätzliche Python-Module vorgesehen. Der explizite Pfad
# hält das Plugin zusätzlich mit älteren Decky-Versionen kompatibel.
PY_MODULES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "py_modules")
if PY_MODULES_DIR not in sys.path:
    sys.path.insert(0, PY_MODULES_DIR)

from gamescope_metrics import GamescopeMetricsReader
from png_chart import generate_benchmark_png


SUPPORTED_LANGUAGES = {"de", "en", "es", "fr"}


class BenchmarkRuntimeError(RuntimeError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def _classify_error(error):
    if isinstance(error, BenchmarkRuntimeError):
        return error.code

    message = str(error).lower()
    if "systembibliothek" in message or "system library" in message:
        return "missing_library"
    if "kein spiel fokussiert" in message or "keine fokussierte" in message:
        return "no_focused_game"
    if (
        "keine gamescope-wayland" in message
        or "gamescope-x11-anzeige" in message
        or "gaming-modus" in message
    ):
        return "gaming_mode_required"
    if "zu alt" in message:
        return "gamescope_too_old"
    if "getrennt" in message:
        return "connection_lost"
    if "keine frames" in message:
        return "no_frames"
    if any(
        fragment in message
        for fragment in (
            "gamescope-control",
            "performance-abfragen",
            "gamescope antwortet nicht",
            "gamescope-initialisierung",
            "wayland-registry",
        )
    ):
        return "gamescope_unavailable"
    return "benchmark_failed"


class Plugin:
    def __init__(self):
        self.is_running = False
        self.countdown = 0
        self.time_left = 0
        self.benchmark_thread = None
        self.status = "Idle"
        self.last_csv_path = ""
        self.last_png_path = ""
        self.last_error = ""
        self.last_error_code = ""
        self.measurement_source = "Gamescope"
        self.report_language = "de"
        self.sample_count = 0
        self.downloads_dir = os.path.join(decky.DECKY_USER_HOME, "Downloads")
        self.logo_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets",
            "sdc-benchmark-logo.ppm",
        )

    async def _main(self):
        decky.logger.info("SDC Benchmark 1.4.0 initialized.")

    async def _unload(self):
        self.is_running = False
        if self.benchmark_thread and self.benchmark_thread.is_alive():
            self.benchmark_thread.join(timeout=1.5)
        decky.logger.info("SDC Benchmark entladen.")

    async def start_benchmark(self, duration: int = 60, language: str = "de"):
        if self.is_running:
            return {
                "status": "error",
                "error_code": "already_running",
                "message": "The benchmark is already running.",
            }

        duration = max(30, min(360, int(duration)))
        duration = max(30, min(360, ((duration + 15) // 30) * 30))
        language = str(language).lower().split("-")[0]
        if language not in SUPPORTED_LANGUAGES:
            language = "en"
        self.is_running = True
        self.status = "Countdown"
        self.countdown = 5
        self.time_left = duration
        self.last_error = ""
        self.last_error_code = ""
        self.last_csv_path = ""
        self.last_png_path = ""
        self.measurement_source = "Gamescope"
        self.report_language = language
        self.sample_count = 0

        self.benchmark_thread = threading.Thread(
            target=self._run_benchmark_process,
            args=(duration,),
            daemon=True,
        )
        self.benchmark_thread.start()
        return {"status": "success"}

    async def stop_benchmark(self):
        self.is_running = False
        self.status = "Stopped"
        self.countdown = 0
        self.time_left = 0
        return {"status": "stopped"}

    async def get_status(self):
        return {
            "is_running": self.is_running,
            "status": self.status,
            "countdown": self.countdown,
            "time_left": self.time_left,
            "last_csv": self.last_csv_path,
            "last_png": self.last_png_path,
            "error": self.last_error,
            "error_code": self.last_error_code,
            "source": self.measurement_source,
            "sample_count": self.sample_count,
        }

    async def get_last_png_preview(self):
        """Liefert das letzte Diagramm als kleine Data-URL für das Decky-Modal."""
        png_path = self.last_png_path
        if not png_path or not os.path.isfile(png_path):
            return {
                "status": "error",
                "error_code": "no_report",
                "message": "No PNG report has been created yet.",
            }

        # Deckys Plugin-Socket ist auf 1 MiB begrenzt. Die stdlib-Berichte sind
        # normalerweise deutlich kleiner; die Grenze verhindert ein Blockieren.
        if os.path.getsize(png_path) > 700_000:
            return {
                "status": "error",
                "error_code": "preview_too_large",
                "message": "The PNG report is too large to preview.",
            }

        with open(png_path, "rb") as png_file:
            encoded = base64.b64encode(png_file.read()).decode("ascii")

        return {
            "status": "success",
            "data_url": f"data:image/png;base64,{encoded}",
            "path": png_path,
        }

    def _run_benchmark_process(self, duration: int):
        metrics_reader = None
        try:
            while self.countdown > 0 and self.is_running:
                time.sleep(1)
                self.countdown -= 1

            if not self.is_running:
                self.status = "Stopped"
                return

            self.status = "Running"
            self.time_left = duration

            app_id = GamescopeMetricsReader.get_focused_app_id()
            metrics_reader = GamescopeMetricsReader()
            metrics_reader.start(app_id)

            now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            csv_filename = f"benchmark_{now_str}.csv"
            csv_path = os.path.join(self.downloads_dir, csv_filename)
            os.makedirs(self.downloads_dir, exist_ok=True)

            data_points = []
            start_time = time.monotonic()
            self.last_csv_path = csv_path

            with open(csv_path, mode="w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["Timestamp_s", "FPS", "Frametime_ms"])

                while self.is_running:
                    elapsed_total = time.monotonic() - start_time
                    if elapsed_total >= duration:
                        break

                    samples = metrics_reader.poll(timeout=0.25)
                    wrote_samples = False
                    for sample_time, fps, frametime_ms in samples:
                        elapsed = sample_time - start_time
                        if elapsed < 0 or elapsed > duration:
                            continue

                        row = (
                            round(elapsed, 4),
                            round(fps, 3),
                            round(frametime_ms, 3),
                        )
                        writer.writerow(row)
                        data_points.append(row)
                        self.sample_count += 1
                        wrote_samples = True

                    if wrote_samples:
                        csv_file.flush()

                    remaining = duration - (time.monotonic() - start_time)
                    self.time_left = max(0, math.ceil(remaining))

            metrics_reader.stop()

            if not self.is_running:
                self.status = "Stopped"
                self.time_left = 0
                return

            if not data_points:
                raise BenchmarkRuntimeError(
                    "no_frames",
                    "Gamescope hat keine Frames geliefert. Bitte sicherstellen, "
                    "dass beim Start ein Spiel fokussiert ist."
                )

            if data_points:
                png_path = os.path.join(
                    self.downloads_dir, f"benchmark_{now_str}.png"
                )
                if self._generate_chart(data_points, png_path):
                    self.last_png_path = png_path

            self.is_running = False
            self.time_left = 0
            self.status = "Finished"
        except Exception as error:
            self.is_running = False
            self.countdown = 0
            self.time_left = 0
            self.status = "Error"
            self.last_error = str(error)
            self.last_error_code = _classify_error(error)
            decky.logger.exception("Benchmark fehlgeschlagen")
        finally:
            if metrics_reader:
                metrics_reader.close()

    def _generate_chart(self, data_points, output_png_path):
        """Erstellt den PNG-Bericht ohne externe Python-Abhängigkeiten."""
        try:
            generate_benchmark_png(
                data_points,
                output_png_path,
                source=self.measurement_source,
                logo_path=self.logo_path,
                language=self.report_language,
            )
            return True
        except Exception as error:
            decky.logger.warning(f"Diagramm konnte nicht erstellt werden: {error}")
            return False
