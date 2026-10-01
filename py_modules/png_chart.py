"""Dependency-free CapFrameX-inspired PNG renderer for SDC Benchmark."""

import binascii
import datetime
import math
import os
import struct
import zlib


FONT = {
    " ": (0, 0, 0, 0, 0, 0, 0),
    "A": (14, 17, 17, 31, 17, 17, 17),
    "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (15, 16, 16, 16, 16, 16, 15),
    "D": (30, 17, 17, 17, 17, 17, 30),
    "E": (31, 16, 16, 30, 16, 16, 31),
    "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (15, 16, 16, 23, 17, 17, 14),
    "H": (17, 17, 17, 31, 17, 17, 17),
    "I": (31, 4, 4, 4, 4, 4, 31),
    "J": (7, 2, 2, 2, 18, 18, 12),
    "K": (17, 18, 20, 24, 20, 18, 17),
    "L": (16, 16, 16, 16, 16, 16, 31),
    "M": (17, 27, 21, 21, 17, 17, 17),
    "N": (17, 25, 21, 19, 17, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14),
    "P": (30, 17, 17, 30, 16, 16, 16),
    "Q": (14, 17, 17, 17, 21, 18, 13),
    "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (15, 16, 16, 14, 1, 1, 30),
    "T": (31, 4, 4, 4, 4, 4, 4),
    "U": (17, 17, 17, 17, 17, 17, 14),
    "V": (17, 17, 17, 17, 17, 10, 4),
    "W": (17, 17, 17, 21, 21, 21, 10),
    "X": (17, 17, 10, 4, 10, 17, 17),
    "Y": (17, 17, 10, 4, 4, 4, 4),
    "Z": (31, 1, 2, 4, 8, 16, 31),
    "0": (14, 17, 19, 21, 25, 17, 14),
    "1": (4, 12, 4, 4, 4, 4, 14),
    "2": (14, 17, 1, 2, 4, 8, 31),
    "3": (30, 1, 1, 14, 1, 1, 30),
    "4": (2, 6, 10, 18, 31, 2, 2),
    "5": (31, 16, 16, 30, 1, 1, 30),
    "6": (14, 16, 16, 30, 17, 17, 14),
    "7": (31, 1, 2, 4, 8, 8, 8),
    "8": (14, 17, 17, 14, 17, 17, 14),
    "9": (14, 17, 17, 15, 1, 1, 14),
    ".": (0, 0, 0, 0, 0, 12, 12),
    ",": (0, 0, 0, 0, 4, 4, 8),
    ":": (0, 12, 12, 0, 12, 12, 0),
    "-": (0, 0, 0, 31, 0, 0, 0),
    "(": (2, 4, 8, 8, 8, 4, 2),
    ")": (8, 4, 2, 2, 2, 4, 8),
    "/": (1, 2, 2, 4, 8, 8, 16),
    "%": (17, 2, 4, 8, 16, 17, 0),
    "|": (4, 4, 4, 4, 4, 4, 4),
    "+": (0, 4, 4, 31, 4, 4, 0),
    "<": (1, 2, 4, 8, 4, 2, 1),
}

BACKGROUND = (25, 25, 28)
HEADER = (31, 31, 35)
PANEL = (39, 39, 43)
PLOT = (44, 44, 49)
CARD = (48, 48, 53)
GRID = (69, 69, 75)
AXIS = (112, 112, 120)
TEXT = (238, 238, 241)
MUTED = (170, 170, 178)
BLUE = (41, 151, 230)
BLUE_FILL = (30, 99, 151)
CYAN = (48, 216, 182)
ORANGE = (255, 132, 25)
YELLOW = (246, 184, 40)
RED = (239, 74, 82)
GREEN = (59, 203, 122)

TRANSLATIONS = {
    "en": {
        "title": "SDC BENCHMARK", "frametimes": "FRAME TIMES",
        "recording_time": "RECORDING TIME (S)", "percentiles": "FPS PERCENTILES",
        "distribution": "FRAME DISTRIBUTION", "results": "RESULTS",
        "run_info": "RUN INFORMATION", "average": "AVERAGE", "minimum": "MINIMUM",
        "one_low": "1% LOW AVG", "point_one_low": "0.1% LOW AVG",
        "p99_ft": "P99 FRAME TIME", "max_ft": "MAX FRAME TIME",
        "duration": "DURATION", "frames": "FRAMES", "source": "SOURCE",
        "created": "CREATED", "thresholds": "REFERENCE LINES",
    },
    "de": {
        "title": "SDC BENCHMARK", "frametimes": "FRAMEZEITEN",
        "recording_time": "AUFNAHMEZEIT (S)", "percentiles": "FPS-PERZENTILE",
        "distribution": "FRAME-VERTEILUNG", "results": "ERGEBNISSE",
        "run_info": "MESSLAUF", "average": "DURCHSCHNITT", "minimum": "MINIMUM",
        "one_low": "1% LOW MITTEL", "point_one_low": "0.1% LOW MITTEL",
        "p99_ft": "P99 FRAMEZEIT", "max_ft": "MAX FRAMEZEIT",
        "duration": "DAUER", "frames": "FRAMES", "source": "QUELLE",
        "created": "ERSTELLT", "thresholds": "REFERENZLINIEN",
    },
    "es": {
        "title": "SDC BENCHMARK", "frametimes": "TIEMPOS DE FOTOGRAMA",
        "recording_time": "TIEMPO DE CAPTURA (S)", "percentiles": "PERCENTILES FPS",
        "distribution": "DISTRIBUCION DE FRAMES", "results": "RESULTADOS",
        "run_info": "INFORMACION DE PRUEBA", "average": "PROMEDIO", "minimum": "MINIMO",
        "one_low": "1% LOW PROMEDIO", "point_one_low": "0.1% LOW PROMEDIO",
        "p99_ft": "P99 TIEMPO FRAME", "max_ft": "MAX TIEMPO FRAME",
        "duration": "DURACION", "frames": "FRAMES", "source": "FUENTE",
        "created": "CREADO", "thresholds": "LINEAS DE REFERENCIA",
    },
    "fr": {
        "title": "SDC BENCHMARK", "frametimes": "TEMPS DE TRAME",
        "recording_time": "DUREE CAPTURE (S)", "percentiles": "PERCENTILES FPS",
        "distribution": "REPARTITION DES FRAMES", "results": "RESULTATS",
        "run_info": "INFORMATIONS DU TEST", "average": "MOYENNE", "minimum": "MINIMUM",
        "one_low": "1% LOW MOYEN", "point_one_low": "0.1% LOW MOYEN",
        "p99_ft": "P99 TEMPS TRAME", "max_ft": "MAX TEMPS TRAME",
        "duration": "DUREE", "frames": "FRAMES", "source": "SOURCE",
        "created": "CREE", "thresholds": "LIGNES DE REFERENCE",
    },
}


class Canvas:
    def __init__(self, width, height, color=BACKGROUND):
        self.width = width
        self.height = height
        self.pixels = bytearray(bytes(color) * (width * height))

    def set_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            offset = (y * self.width + x) * 3
            self.pixels[offset:offset + 3] = bytes(color)

    def fill_rect(self, x, y, width, height, color):
        x0, y0 = max(0, int(x)), max(0, int(y))
        x1, y1 = min(self.width, int(x + width)), min(self.height, int(y + height))
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for py in range(y0, y1):
            offset = (py * self.width + x0) * 3
            self.pixels[offset:offset + len(row)] = row

    def rect(self, x, y, width, height, color, thickness=1):
        self.fill_rect(x, y, width, thickness, color)
        self.fill_rect(x, y + height - thickness, width, thickness, color)
        self.fill_rect(x, y, thickness, height, color)
        self.fill_rect(x + width - thickness, y, thickness, height, color)

    def line(self, x0, y0, x1, y1, color, thickness=1):
        x0, y0, x1, y1 = map(lambda value: int(round(value)), (x0, y0, x1, y1))
        dx, sx = abs(x1 - x0), 1 if x0 < x1 else -1
        dy, sy = -abs(y1 - y0), 1 if y0 < y1 else -1
        error, radius = dx + dy, max(0, thickness // 2)
        while True:
            self.fill_rect(x0 - radius, y0 - radius, radius * 2 + 1, radius * 2 + 1, color)
            if x0 == x1 and y0 == y1:
                break
            doubled = 2 * error
            if doubled >= dy:
                error += dy
                x0 += sx
            if doubled <= dx:
                error += dx
                y0 += sy

    def dashed_line(self, x0, y0, x1, y1, color, dash=7, gap=5):
        if y0 == y1:
            x = int(x0)
            while x < int(x1):
                self.line(x, y0, min(x + dash, x1), y1, color)
                x += dash + gap

    def polyline(self, points, color, thickness=1):
        for index in range(1, len(points)):
            self.line(*points[index - 1], *points[index], color, thickness)

    def donut(self, center_x, center_y, radius, thickness, segments):
        inner = max(0, radius - thickness)
        total = sum(max(0.0, value) for value, _ in segments)
        if total <= 0:
            return
        boundaries, running = [], 0.0
        for value, color in segments:
            running += max(0.0, value) / total
            boundaries.append((running, color))
        for py in range(center_y - radius, center_y + radius + 1):
            for px in range(center_x - radius, center_x + radius + 1):
                dx, dy = px - center_x, py - center_y
                distance_sq = dx * dx + dy * dy
                if inner * inner <= distance_sq <= radius * radius:
                    ratio = ((math.atan2(dy, dx) + math.pi / 2) % (2 * math.pi)) / (2 * math.pi)
                    color = boundaries[-1][1]
                    for boundary, candidate in boundaries:
                        if ratio <= boundary:
                            color = candidate
                            break
                    self.set_pixel(px, py, color)

    def blit_rgb(self, pixels, source_width, source_height, x, y, width, height):
        x, y, width, height = int(x), int(y), max(1, int(width)), max(1, int(height))
        for target_y in range(height):
            source_y = min(source_height - 1, target_y * source_height // height)
            canvas_y = y + target_y
            if not 0 <= canvas_y < self.height:
                continue
            for target_x in range(width):
                canvas_x = x + target_x
                if not 0 <= canvas_x < self.width:
                    continue
                source_x = min(source_width - 1, target_x * source_width // width)
                source_offset = (source_y * source_width + source_x) * 3
                self.set_pixel(canvas_x, canvas_y, pixels[source_offset:source_offset + 3])

    @staticmethod
    def text_width(text, scale=1):
        return 0 if not text else len(str(text)) * 6 * scale - scale

    def text(self, x, y, text, color=TEXT, scale=1, align="left"):
        value = str(text).upper()
        width = self.text_width(value, scale)
        if align == "center":
            x -= width // 2
        elif align == "right":
            x -= width
        cursor_x = int(x)
        for character in value:
            glyph = FONT.get(character, FONT[" "])
            for row_index, row_bits in enumerate(glyph):
                for column in range(5):
                    if row_bits & (1 << (4 - column)):
                        self.fill_rect(cursor_x + column * scale, int(y) + row_index * scale, scale, scale, color)
            cursor_x += 6 * scale

    def write_png(self, output_path):
        rows, stride = [], self.width * 3
        for y in range(self.height):
            start = y * stride
            rows.append(b"\x00" + bytes(self.pixels[start:start + stride]))
        raw_data = b"".join(rows)

        def chunk(chunk_type, data):
            checksum = binascii.crc32(chunk_type + data) & 0xFFFFFFFF
            return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", checksum)

        png = bytearray(b"\x89PNG\r\n\x1a\n")
        png.extend(chunk(b"IHDR", struct.pack(">IIBBBBB", self.width, self.height, 8, 2, 0, 0, 0)))
        # Level 6 keeps reports compact while avoiding a long level-9 encode on Deck.
        png.extend(chunk(b"IDAT", zlib.compress(raw_data, level=6)))
        png.extend(chunk(b"IEND", b""))
        with open(output_path, "wb") as output_file:
            output_file.write(png)


def _read_ppm(path):
    with open(path, "rb") as image_file:
        data = image_file.read()
    index = 0

    def next_token():
        nonlocal index
        while index < len(data):
            if data[index] == 35:
                while index < len(data) and data[index] not in (10, 13):
                    index += 1
            elif data[index] in b" \t\r\n":
                index += 1
            else:
                break
        start = index
        while index < len(data) and data[index] not in b" \t\r\n#":
            index += 1
        if start == index:
            raise ValueError("Invalid PPM header")
        return data[start:index]

    if next_token() != b"P6":
        raise ValueError("Only binary P6 PPM files are supported")
    width, height, max_value = int(next_token()), int(next_token()), int(next_token())
    if width <= 0 or height <= 0 or max_value != 255:
        raise ValueError("Invalid PPM image")
    if data[index:index + 2] == b"\r\n":
        index += 2
    elif index < len(data) and data[index] in b" \t\r\n":
        index += 1
    pixels = data[index:index + width * height * 3]
    if len(pixels) != width * height * 3:
        raise ValueError("Incomplete PPM pixel data")
    return width, height, pixels


def _percentile(values, percentile):
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = (len(ordered) - 1) * max(0.0, min(1.0, percentile))
    lower, upper = int(math.floor(position)), int(math.ceil(position))
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _low_average(values, fraction):
    count = max(1, math.ceil(len(values) * fraction))
    return sum(sorted(values)[:count]) / count


def _nice_axis(maximum, tick_count=5):
    maximum = max(float(maximum), 0.001) * 1.06
    raw_step = maximum / tick_count
    magnitude = 10 ** math.floor(math.log10(raw_step))
    fraction = raw_step / magnitude
    nice_fraction = 1 if fraction <= 1 else 2 if fraction <= 2 else 5 if fraction <= 5 else 10
    step = nice_fraction * magnitude
    return math.ceil(maximum / step) * step, step


def _format_number(value, decimals=1):
    if decimals <= 0:
        return f"{value:.0f}"
    if abs(value) >= 100:
        return f"{value:.0f}"
    return f"{value:.{decimals}f}"


def _panel(canvas, x, y, width, height, title):
    canvas.fill_rect(x, y, width, height, PANEL)
    canvas.fill_rect(x, y, width, 3, BLUE)
    canvas.text(x + 14, y + 14, title, TEXT, scale=2)


def _sidebar_metric(canvas, x, y, width, label, value, color=TEXT):
    canvas.text(x, y, label, MUTED, scale=1)
    canvas.text(x + width, y - 4, value, color, scale=2, align="right")
    canvas.line(x, y + 20, x + width, y + 20, GRID)


def _downsample(cleaned, plot_width):
    end_time = max(cleaned[-1][0], 0.001)
    buckets = [[0.0, 0, 0.0] for _ in range(max(1, int(plot_width)))]
    for timestamp, _fps, frametime in cleaned:
        index = min(len(buckets) - 1, max(0, int(timestamp / end_time * (len(buckets) - 1))))
        bucket = buckets[index]
        bucket[0] += frametime
        bucket[1] += 1
        bucket[2] = max(bucket[2], frametime)
    return [(index, total / count, maximum) for index, (total, count, maximum) in enumerate(buckets) if count]


def generate_benchmark_png(data_points, output_path, source="Gamescope", logo_path=None, language="en"):
    """Create a 1280x720 benchmark report using only the Python standard library."""
    cleaned = []
    for point in data_points:
        try:
            timestamp, fps, frametime = float(point[0]), float(point[1]), float(point[2])
        except (TypeError, ValueError, IndexError):
            continue
        valid = all(math.isfinite(value) for value in (timestamp, fps, frametime))
        if valid and timestamp >= 0 and fps > 0 and frametime > 0:
            cleaned.append((timestamp, fps, frametime))
    if not cleaned:
        raise ValueError("No valid benchmark samples")
    cleaned.sort(key=lambda point: point[0])

    language = str(language).lower().split("-")[0]
    labels = TRANSLATIONS.get(language, TRANSLATIONS["en"])
    timestamps = [point[0] for point in cleaned]
    fps_values = [point[1] for point in cleaned]
    frametimes = [point[2] for point in cleaned]
    duration = max(timestamps[-1], 0.001)

    average_fps = sum(fps_values) / len(fps_values)
    one_low = _low_average(fps_values, 0.01)
    point_one_low = _low_average(fps_values, 0.001)
    minimum_fps = min(fps_values)
    p99_frametime = _percentile(frametimes, 0.99)
    max_frametime = max(frametimes)

    fps_metrics = [
        ("95TH PERCENTILE", _percentile(fps_values, 0.95)),
        (labels["average"], average_fps),
        ("5TH PERCENTILE", _percentile(fps_values, 0.05)),
        ("1ST PERCENTILE", _percentile(fps_values, 0.01)),
        (labels["one_low"], one_low),
        (labels["point_one_low"], point_one_low),
        (labels["minimum"], minimum_fps),
    ]
    count = len(fps_values)
    frame_groups = [
        (sum(1 for fps in fps_values if fps >= 60) * 100.0 / count, GREEN, "60+ FPS"),
        (sum(1 for fps in fps_values if 30 <= fps < 60) * 100.0 / count, YELLOW, "30-60 FPS"),
        (sum(1 for fps in fps_values if fps < 30) * 100.0 / count, RED, "<30 FPS"),
    ]

    canvas = Canvas(1280, 720)
    canvas.fill_rect(0, 0, 1280, 72, HEADER)
    canvas.fill_rect(0, 70, 1280, 2, BLUE)
    if logo_path and os.path.isfile(logo_path):
        try:
            logo_width, logo_height, logo_pixels = _read_ppm(logo_path)
            canvas.blit_rgb(logo_pixels, logo_width, logo_height, 14, 5, 62, 62)
        except (OSError, ValueError):
            pass
    canvas.text(92, 14, labels["title"], TEXT, scale=3)
    canvas.text(92, 45, f"{source} | {duration:.1f} S | {len(cleaned)} FRAMES", MUTED, scale=1)
    created_at = datetime.datetime.now().strftime("%Y-%m-%d | %H:%M:%S")
    canvas.text(1254, 27, created_at, MUTED, scale=1, align="right")

    left_x, left_width = 18, 912
    sidebar_x, sidebar_width = 946, 316

    chart_y, chart_height = 86, 366
    _panel(canvas, left_x, chart_y, left_width, chart_height, labels["frametimes"] + " (MS)")
    plot_left = left_x + 54
    plot_right = left_x + left_width - 18
    plot_top = chart_y + 48
    plot_bottom = chart_y + chart_height - 48
    plot_width = plot_right - plot_left
    plot_height = plot_bottom - plot_top
    canvas.fill_rect(plot_left, plot_top, plot_width, plot_height, PLOT)

    robust_max = max(35.0, _percentile(frametimes, 0.995) * 1.12)
    axis_max, axis_step = _nice_axis(robust_max, 5)
    tick_count = max(1, int(round(axis_max / axis_step)))
    for tick in range(tick_count + 1):
        value = tick * axis_step
        y = plot_bottom - value / axis_max * plot_height
        canvas.line(plot_left, y, plot_right, y, GRID)
        canvas.text(plot_left - 10, y - 4, _format_number(value, 0), MUTED, scale=1, align="right")
    for tick in range(7):
        ratio = tick / 6
        x = plot_left + ratio * plot_width
        canvas.line(x, plot_top, x, plot_bottom, GRID)
        canvas.text(x, plot_bottom + 12, _format_number(duration * ratio, 1), MUTED, scale=1, align="center")

    references = ((16.7, GREEN, "16.7 MS / 60 FPS"), (33.3, YELLOW, "33.3 MS / 30 FPS"))
    for reference, color, text_value in references:
        if reference <= axis_max:
            y = plot_bottom - reference / axis_max * plot_height
            canvas.dashed_line(plot_left, y, plot_right, y, color)
            canvas.text(plot_right - 8, y - 12, text_value, color, scale=1, align="right")

    sampled, average_points = _downsample(cleaned, plot_width), []
    for column, average, maximum in sampled:
        x = plot_left + column
        average_y = plot_bottom - min(average, axis_max) / axis_max * plot_height
        maximum_y = plot_bottom - min(maximum, axis_max) / axis_max * plot_height
        canvas.fill_rect(x, average_y, 1, plot_bottom - average_y, BLUE_FILL)
        if maximum > average * 1.35:
            canvas.line(x, maximum_y, x, average_y, RED)
        average_points.append((x, average_y))
    canvas.polyline(average_points, BLUE, 2)
    canvas.rect(plot_left, plot_top, plot_width, plot_height, AXIS)
    canvas.text((plot_left + plot_right) // 2, chart_y + chart_height - 18, labels["recording_time"], MUTED, scale=1, align="center")

    bars_x, bars_y, bars_width, bars_height = left_x, 466, 530, 236
    _panel(canvas, bars_x, bars_y, bars_width, bars_height, labels["percentiles"])
    label_width = 128
    bar_left = bars_x + label_width
    bar_right = bars_x + bars_width - 42
    bar_available = bar_right - bar_left
    bars_axis_max, _ = _nice_axis(max(value for _label, value in fps_metrics), 4)
    row_y = bars_y + 43
    for label, value in fps_metrics:
        canvas.text(bars_x + 14, row_y + 3, label, TEXT, scale=1)
        length = max(1, int(value / bars_axis_max * bar_available))
        canvas.fill_rect(bar_left, row_y, bar_available, 13, CARD)
        canvas.fill_rect(bar_left, row_y, length, 13, ORANGE)
        value_x = min(bar_left + length + 5, bars_x + bars_width - 8)
        value_align = "right" if length > bar_available - 32 else "left"
        canvas.text(value_x, row_y + 3, _format_number(value, 1), TEXT, scale=1, align=value_align)
        row_y += 25

    dist_x, dist_y, dist_width, dist_height = 562, 466, 368, 236
    _panel(canvas, dist_x, dist_y, dist_width, dist_height, labels["distribution"])
    donut_x, donut_y = dist_x + 254, dist_y + 135
    canvas.donut(donut_x, donut_y, 72, 22, [(value, color) for value, color, _label in frame_groups])
    canvas.text(donut_x, donut_y - 10, _format_number(frame_groups[0][0], 1) + "%", GREEN, scale=2, align="center")
    canvas.text(donut_x, donut_y + 13, "60+ FPS", MUTED, scale=1, align="center")
    legend_y = dist_y + 64
    for value, color, label in frame_groups:
        canvas.fill_rect(dist_x + 18, legend_y, 10, 10, color)
        canvas.text(dist_x + 38, legend_y + 2, label, TEXT, scale=1)
        canvas.text(dist_x + 148, legend_y + 2, _format_number(value, 1) + "%", color, scale=1, align="right")
        legend_y += 34

    _panel(canvas, sidebar_x, 86, sidebar_width, 616, labels["results"])
    metric_x, metric_width, y = sidebar_x + 18, sidebar_width - 36, 128
    result_metrics = (
        ("AVG FPS", _format_number(average_fps, 1), BLUE),
        ("1% LOW", _format_number(one_low, 1), ORANGE),
        ("0.1% LOW", _format_number(point_one_low, 1), ORANGE),
        (labels["p99_ft"], _format_number(p99_frametime, 1) + " MS", CYAN),
        (labels["max_ft"], _format_number(max_frametime, 1) + " MS", RED),
    )
    for label, value, color in result_metrics:
        _sidebar_metric(canvas, metric_x, y, metric_width, label, value, color)
        y += 43

    canvas.text(metric_x, y + 2, labels["run_info"], TEXT, scale=2)
    y += 39
    run_metrics = (
        (labels["duration"], _format_number(duration, 1) + " S"),
        (labels["frames"], str(len(cleaned))),
        (labels["source"], source),
        (labels["created"], datetime.datetime.now().strftime("%Y-%m-%d")),
    )
    for label, value in run_metrics:
        _sidebar_metric(canvas, metric_x, y, metric_width, label, value, TEXT)
        y += 43

    canvas.text(metric_x, y + 4, labels["thresholds"], TEXT, scale=2)
    y += 39
    canvas.fill_rect(metric_x, y + 3, 10, 10, GREEN)
    canvas.text(metric_x + 18, y + 5, "60 FPS = 16.7 MS", MUTED, scale=1)
    canvas.fill_rect(metric_x, y + 29, 10, 10, YELLOW)
    canvas.text(metric_x + 18, y + 31, "30 FPS = 33.3 MS", MUTED, scale=1)

    canvas.write_png(output_path)
    return output_path
