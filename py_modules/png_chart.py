"""Abhängigkeitsfreier PNG-Renderer in Deckys ``py_modules``."""

import binascii
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
}


BACKGROUND = (12, 20, 36)
PANEL = (19, 31, 52)
CARD = (25, 39, 63)
GRID = (53, 68, 91)
AXIS = (122, 142, 166)
TEXT = (226, 232, 240)
MUTED = (148, 163, 184)
FPS_COLOR = (56, 189, 248)
FRAMETIME_COLOR = (251, 113, 133)
ACCENT = (167, 139, 250)


class Canvas:
    def __init__(self, width, height, color=BACKGROUND):
        self.width = width
        self.height = height
        self.pixels = bytearray(bytes(color) * (width * height))

    def set_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            offset = (y * self.width + x) * 3
            self.pixels[offset : offset + 3] = bytes(color)

    def fill_rect(self, x, y, width, height, color):
        x0 = max(0, int(x))
        y0 = max(0, int(y))
        x1 = min(self.width, int(x + width))
        y1 = min(self.height, int(y + height))
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for py in range(y0, y1):
            offset = (py * self.width + x0) * 3
            self.pixels[offset : offset + len(row)] = row

    def rect(self, x, y, width, height, color, thickness=1):
        self.fill_rect(x, y, width, thickness, color)
        self.fill_rect(x, y + height - thickness, width, thickness, color)
        self.fill_rect(x, y, thickness, height, color)
        self.fill_rect(x + width - thickness, y, thickness, height, color)

    def line(self, x0, y0, x1, y1, color, thickness=1):
        x0 = int(round(x0))
        y0 = int(round(y0))
        x1 = int(round(x1))
        y1 = int(round(y1))
        dx = abs(x1 - x0)
        sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0)
        sy = 1 if y0 < y1 else -1
        error = dx + dy
        radius = max(0, thickness // 2)

        while True:
            self.fill_rect(
                x0 - radius,
                y0 - radius,
                radius * 2 + 1,
                radius * 2 + 1,
                color,
            )
            if x0 == x1 and y0 == y1:
                break
            doubled = 2 * error
            if doubled >= dy:
                error += dy
                x0 += sx
            if doubled <= dx:
                error += dx
                y0 += sy

    def polyline(self, points, color, thickness=1):
        for index in range(1, len(points)):
            self.line(*points[index - 1], *points[index], color, thickness)

    def blit_rgb(self, pixels, source_width, source_height, x, y, width, height):
        """Skaliert RGB-Pixel per Nearest-Neighbour auf die Zeichenfläche."""
        x = int(x)
        y = int(y)
        width = max(1, int(width))
        height = max(1, int(height))
        for target_y in range(height):
            source_y = min(source_height - 1, target_y * source_height // height)
            canvas_y = y + target_y
            if canvas_y < 0 or canvas_y >= self.height:
                continue
            for target_x in range(width):
                canvas_x = x + target_x
                if canvas_x < 0 or canvas_x >= self.width:
                    continue
                source_x = min(source_width - 1, target_x * source_width // width)
                source_offset = (source_y * source_width + source_x) * 3
                self.set_pixel(
                    canvas_x,
                    canvas_y,
                    pixels[source_offset : source_offset + 3],
                )

    @staticmethod
    def text_width(text, scale=1):
        if not text:
            return 0
        return len(text) * 6 * scale - scale

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
                        self.fill_rect(
                            cursor_x + column * scale,
                            int(y) + row_index * scale,
                            scale,
                            scale,
                            color,
                        )
            cursor_x += 6 * scale

    def write_png(self, output_path):
        rows = []
        stride = self.width * 3
        for y in range(self.height):
            start = y * stride
            rows.append(b"\x00" + bytes(self.pixels[start : start + stride]))
        raw_data = b"".join(rows)

        def chunk(chunk_type, data):
            checksum = binascii.crc32(chunk_type + data) & 0xFFFFFFFF
            return (
                struct.pack(">I", len(data))
                + chunk_type
                + data
                + struct.pack(">I", checksum)
            )

        png = bytearray(b"\x89PNG\r\n\x1a\n")
        png.extend(
            chunk(
                b"IHDR",
                struct.pack(">IIBBBBB", self.width, self.height, 8, 2, 0, 0, 0),
            )
        )
        png.extend(chunk(b"IDAT", zlib.compress(raw_data, level=9)))
        png.extend(chunk(b"IEND", b""))

        with open(output_path, "wb") as output_file:
            output_file.write(png)


def _read_ppm(path):
    """Liest ein binäres 8-Bit-P6-PPM ohne externe Bildbibliothek."""
    with open(path, "rb") as image_file:
        data = image_file.read()

    index = 0

    def next_token():
        nonlocal index
        while index < len(data):
            if data[index] == 35:  # '#': Kommentar bis zum Zeilenende
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
            raise ValueError("Ungültiger PPM-Header")
        return data[start:index]

    if next_token() != b"P6":
        raise ValueError("Nur binäre P6-PPM-Dateien werden unterstützt")
    width = int(next_token())
    height = int(next_token())
    max_value = int(next_token())
    if width <= 0 or height <= 0 or max_value != 255:
        raise ValueError("Ungültige PPM-Abmessungen oder Farbtiefe")

    if data[index : index + 2] == b"\r\n":
        index += 2
    elif index < len(data) and data[index] in b" \t\r\n":
        index += 1

    expected_size = width * height * 3
    pixels = data[index : index + expected_size]
    if len(pixels) != expected_size:
        raise ValueError("PPM-Pixeldaten sind unvollständig")
    return width, height, pixels


def _nice_axis(maximum, tick_count=5):
    maximum = max(float(maximum), 0.001) * 1.08
    raw_step = maximum / tick_count
    magnitude = 10 ** math.floor(math.log10(raw_step))
    fraction = raw_step / magnitude
    if fraction <= 1:
        nice_fraction = 1
    elif fraction <= 2:
        nice_fraction = 2
    elif fraction <= 5:
        nice_fraction = 5
    else:
        nice_fraction = 10
    step = nice_fraction * magnitude
    axis_max = math.ceil(maximum / step) * step
    return axis_max, step


def _format_number(value, decimals=1):
    if decimals <= 0:
        return f"{value:.0f}"
    if abs(value) >= 100:
        return f"{value:.0f}"
    if abs(value) >= 10 and decimals < 2:
        return f"{value:.1f}"
    return f"{value:.{decimals}f}"


def _percentile(values, percentile):
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(len(ordered) * percentile) - 1))
    return ordered[index]


def _draw_card(canvas, x, y, width, label, value, color):
    canvas.fill_rect(x, y, width, 76, CARD)
    canvas.fill_rect(x, y, 5, 76, color)
    canvas.text(x + 20, y + 14, label, MUTED, scale=2)
    canvas.text(x + 20, y + 42, value, color, scale=3)


def generate_benchmark_png(
    data_points,
    output_path,
    source="Gamescope",
    logo_path=None,
):
    """Erzeugt einen 1280x720-Benchmarkbericht ausschließlich mit stdlib."""
    cleaned = []
    for point in data_points:
        try:
            timestamp = float(point[0])
            fps = float(point[1])
            frametime = float(point[2])
        except (TypeError, ValueError, IndexError):
            continue
        if not all(math.isfinite(value) for value in (timestamp, fps, frametime)):
            continue
        if timestamp < 0 or fps <= 0 or frametime <= 0:
            continue
        cleaned.append((timestamp, fps, frametime))

    if not cleaned:
        raise ValueError("Keine gültigen Benchmarkdaten für das Diagramm")

    cleaned.sort(key=lambda point: point[0])
    timestamps = [point[0] for point in cleaned]
    fps_values = [point[1] for point in cleaned]
    frametimes = [point[2] for point in cleaned]

    average_fps = sum(fps_values) / len(fps_values)
    low_count = max(1, math.ceil(len(fps_values) * 0.01))
    one_percent_low = sum(sorted(fps_values)[:low_count]) / low_count
    p99_frametime = _percentile(frametimes, 0.99)
    max_frametime = max(frametimes)

    canvas = Canvas(1280, 720)
    if logo_path and os.path.isfile(logo_path):
        try:
            logo_width, logo_height, logo_pixels = _read_ppm(logo_path)
            canvas.blit_rgb(
                logo_pixels,
                logo_width,
                logo_height,
                22,
                5,
                88,
                88,
            )
        except (OSError, ValueError):
            # Der Bericht bleibt auch bei einem beschädigten optionalen Logo nutzbar.
            pass
    canvas.text(640, 25, "SDC BENCHMARK REPORT", TEXT, scale=4, align="center")
    subtitle = (
        f"{source} | {timestamps[-1]:.1f} S | {len(cleaned)} FRAMES"
    )
    canvas.text(640, 68, subtitle, MUTED, scale=2, align="center")

    card_width = 250
    card_gap = 24
    cards_start = 104
    _draw_card(
        canvas,
        cards_start,
        100,
        card_width,
        "AVG FPS",
        _format_number(average_fps, 1),
        FPS_COLOR,
    )
    _draw_card(
        canvas,
        cards_start + (card_width + card_gap),
        100,
        card_width,
        "1% LOW",
        _format_number(one_percent_low, 1),
        ACCENT,
    )
    _draw_card(
        canvas,
        cards_start + 2 * (card_width + card_gap),
        100,
        card_width,
        "P99 FRAMETIME",
        f"{_format_number(p99_frametime, 1)} MS",
        FRAMETIME_COLOR,
    )
    _draw_card(
        canvas,
        cards_start + 3 * (card_width + card_gap),
        100,
        card_width,
        "MAX FRAMETIME",
        f"{_format_number(max_frametime, 1)} MS",
        FRAMETIME_COLOR,
    )

    plot_left = 94
    plot_right = 1186
    plot_top = 222
    plot_bottom = 620
    plot_width = plot_right - plot_left
    plot_height = plot_bottom - plot_top
    canvas.fill_rect(plot_left, plot_top, plot_width, plot_height, PANEL)

    fps_axis_max, fps_step = _nice_axis(max(fps_values))
    frametime_axis_max, frametime_step = _nice_axis(max(frametimes))

    fps_tick_count = max(1, round(fps_axis_max / fps_step))
    frametime_tick_count = max(1, round(frametime_axis_max / frametime_step))
    horizontal_lines = max(fps_tick_count, frametime_tick_count, 5)

    for tick in range(horizontal_lines + 1):
        ratio = tick / horizontal_lines
        y = plot_bottom - ratio * plot_height
        canvas.line(plot_left, y, plot_right, y, GRID, 1)

    for tick in range(fps_tick_count + 1):
        value = tick * fps_step
        y = plot_bottom - (value / fps_axis_max) * plot_height
        canvas.text(
            plot_left - 12,
            y - 7,
            _format_number(value, 0),
            FPS_COLOR,
            scale=2,
            align="right",
        )

    for tick in range(frametime_tick_count + 1):
        value = tick * frametime_step
        y = plot_bottom - (value / frametime_axis_max) * plot_height
        canvas.text(
            plot_right + 12,
            y - 7,
            _format_number(value, 1),
            FRAMETIME_COLOR,
            scale=2,
        )

    x_max = max(timestamps[-1], 0.001)
    x_ticks = 6
    for tick in range(x_ticks + 1):
        ratio = tick / x_ticks
        x = plot_left + ratio * plot_width
        canvas.line(x, plot_top, x, plot_bottom, GRID, 1)
        canvas.text(
            x,
            plot_bottom + 15,
            _format_number(x_max * ratio, 1),
            MUTED,
            scale=2,
            align="center",
        )

    canvas.rect(plot_left, plot_top, plot_width, plot_height, AXIS, 2)
    canvas.text(plot_left, plot_top - 27, "FPS", FPS_COLOR, scale=2)
    canvas.text(
        plot_right,
        plot_top - 27,
        "FRAMETIME (MS)",
        FRAMETIME_COLOR,
        scale=2,
        align="right",
    )
    canvas.text(640, 678, "ZEIT (SEKUNDEN)", MUTED, scale=2, align="center")

    fps_points = []
    frametime_points = []
    for timestamp, fps, frametime in cleaned:
        x = plot_left + (timestamp / x_max) * plot_width
        fps_y = plot_bottom - min(fps, fps_axis_max) / fps_axis_max * plot_height
        frametime_y = (
            plot_bottom
            - min(frametime, frametime_axis_max)
            / frametime_axis_max
            * plot_height
        )
        fps_points.append((x, fps_y))
        frametime_points.append((x, frametime_y))

    canvas.polyline(fps_points, FPS_COLOR, 3)
    canvas.polyline(frametime_points, FRAMETIME_COLOR, 3)
    canvas.write_png(output_path)
    return output_path
