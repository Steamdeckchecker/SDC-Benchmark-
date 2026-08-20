"""Minimaler Gamescope-Performance-Client für Deckys ``py_modules``.

Gamescope stellt ab Version 6 seines privaten Wayland-Protokolls für eine App
die Zeit zwischen zwei präsentierten Frames bereit. Dieses Modul bindet die
Schnittstelle über ctypes an, damit das Decky-Plugin keine zusätzlichen
Python-Pakete oder nativen Hilfsprogramme benötigt.
"""

import ctypes
import ctypes.util
import glob
import os
import select
import time


class GamescopeMetricsError(RuntimeError):
    pass


class _WlMessage(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("signature", ctypes.c_char_p),
        ("types", ctypes.c_void_p),
    ]


class _WlInterface(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("version", ctypes.c_int),
        ("method_count", ctypes.c_int),
        ("methods", ctypes.POINTER(_WlMessage)),
        ("event_count", ctypes.c_int),
        ("events", ctypes.POINTER(_WlMessage)),
    ]


# Definition aus protocol/gamescope-control.xml (Interface-Version 6).
_GAMESCOPE_REQUESTS = (_WlMessage * 7)(
    _WlMessage(b"destroy", b"", None),
    _WlMessage(b"set_app_target_refresh_cycle", b"2uu", None),
    _WlMessage(b"take_screenshot", b"3suu", None),
    _WlMessage(b"display_sleep", b"4uu", None),
    _WlMessage(b"set_look", b"5hhu", None),
    _WlMessage(b"unset_look", b"5", None),
    _WlMessage(b"request_app_performance_stats", b"6u", None),
)

_GAMESCOPE_EVENTS = (_WlMessage * 4)(
    _WlMessage(b"feature_support", b"uuu", None),
    _WlMessage(b"active_display_info", b"2sssua", None),
    _WlMessage(b"screenshot_taken", b"3s", None),
    _WlMessage(b"app_performance_stats", b"6uuu", None),
)

_GAMESCOPE_INTERFACE = _WlInterface(
    b"gamescope_control",
    6,
    len(_GAMESCOPE_REQUESTS),
    _GAMESCOPE_REQUESTS,
    len(_GAMESCOPE_EVENTS),
    _GAMESCOPE_EVENTS,
)

_RegistryGlobalCallback = ctypes.CFUNCTYPE(
    None,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_uint32,
    ctypes.c_char_p,
    ctypes.c_uint32,
)
_RegistryGlobalRemoveCallback = ctypes.CFUNCTYPE(
    None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32
)
_FeatureSupportCallback = ctypes.CFUNCTYPE(
    None,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_uint32,
    ctypes.c_uint32,
    ctypes.c_uint32,
)
_ActiveDisplayInfoCallback = ctypes.CFUNCTYPE(
    None,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_char_p,
    ctypes.c_char_p,
    ctypes.c_char_p,
    ctypes.c_uint32,
    ctypes.c_void_p,
)
_ScreenshotTakenCallback = ctypes.CFUNCTYPE(
    None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p
)
_AppPerformanceStatsCallback = ctypes.CFUNCTYPE(
    None,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_uint32,
    ctypes.c_uint32,
    ctypes.c_uint32,
)


def _load_library(candidates):
    for candidate in candidates:
        if not candidate:
            continue
        try:
            return ctypes.CDLL(candidate)
        except OSError:
            continue
    raise GamescopeMetricsError(
        f"Benötigte Systembibliothek nicht gefunden: {candidates[0]}"
    )


class GamescopeMetricsReader:
    PROTOCOL_VERSION = 6
    PERFORMANCE_FEATURE = 7
    REQUEST_PERFORMANCE_STATS_OPCODE = 6

    def __init__(self):
        self._wayland = _load_library(
            [ctypes.util.find_library("wayland-client"), "libwayland-client.so.0"]
        )
        self._configure_wayland_api()

        self._display = None
        self._registry = None
        self._control = None
        self._control_version = 0
        self._app_id = 0
        self._running = False
        self._samples = []
        self._feature_list_complete = False
        self._performance_feature_found = False

        # Callback-Objekte und Listener-Arrays müssen während der gesamten
        # Verbindung referenziert bleiben.
        self._registry_global_callback = _RegistryGlobalCallback(
            self._on_registry_global
        )
        self._registry_remove_callback = _RegistryGlobalRemoveCallback(
            self._on_registry_remove
        )
        self._feature_callback = _FeatureSupportCallback(self._on_feature_support)
        self._display_info_callback = _ActiveDisplayInfoCallback(
            self._on_active_display_info
        )
        self._screenshot_callback = _ScreenshotTakenCallback(
            self._on_screenshot_taken
        )
        self._performance_callback = _AppPerformanceStatsCallback(
            self._on_app_performance_stats
        )

        self._registry_listener = (ctypes.c_void_p * 2)(
            ctypes.cast(self._registry_global_callback, ctypes.c_void_p).value,
            ctypes.cast(self._registry_remove_callback, ctypes.c_void_p).value,
        )
        self._control_listener = (ctypes.c_void_p * 4)(
            ctypes.cast(self._feature_callback, ctypes.c_void_p).value,
            ctypes.cast(self._display_info_callback, ctypes.c_void_p).value,
            ctypes.cast(self._screenshot_callback, ctypes.c_void_p).value,
            ctypes.cast(self._performance_callback, ctypes.c_void_p).value,
        )

    def _configure_wayland_api(self):
        self._wayland.wl_display_connect.argtypes = [ctypes.c_char_p]
        self._wayland.wl_display_connect.restype = ctypes.c_void_p
        self._wayland.wl_display_disconnect.argtypes = [ctypes.c_void_p]
        self._wayland.wl_display_disconnect.restype = None
        self._wayland.wl_display_roundtrip.argtypes = [ctypes.c_void_p]
        self._wayland.wl_display_roundtrip.restype = ctypes.c_int
        self._wayland.wl_display_dispatch.argtypes = [ctypes.c_void_p]
        self._wayland.wl_display_dispatch.restype = ctypes.c_int
        self._wayland.wl_display_flush.argtypes = [ctypes.c_void_p]
        self._wayland.wl_display_flush.restype = ctypes.c_int
        self._wayland.wl_display_get_fd.argtypes = [ctypes.c_void_p]
        self._wayland.wl_display_get_fd.restype = ctypes.c_int
        self._wayland.wl_proxy_get_version.argtypes = [ctypes.c_void_p]
        self._wayland.wl_proxy_get_version.restype = ctypes.c_uint32
        self._wayland.wl_proxy_add_listener.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_void_p,
        ]
        self._wayland.wl_proxy_add_listener.restype = ctypes.c_int

        # wl_proxy_marshal_flags ist variadisch; nur die festen Parameter
        # werden deklariert.
        self._wayland.wl_proxy_marshal_flags.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.POINTER(_WlInterface),
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        self._wayland.wl_proxy_marshal_flags.restype = ctypes.c_void_p

    def _display_candidates(self):
        candidates = [None]
        runtime_dir = os.environ.get("XDG_RUNTIME_DIR")
        if not runtime_dir:
            for uid in (os.getuid(), 1000):
                uid_runtime = f"/run/user/{uid}"
                if os.path.isdir(uid_runtime):
                    runtime_dir = uid_runtime
                    os.environ["XDG_RUNTIME_DIR"] = runtime_dir
                    break

        if runtime_dir:
            for pattern in ("gamescope-*", "wayland-*"):
                for path in sorted(glob.glob(os.path.join(runtime_dir, pattern))):
                    if path.endswith(".lock") or not os.path.exists(path):
                        continue
                    name = os.path.basename(path).encode("utf-8")
                    if name not in candidates:
                        candidates.append(name)
        return candidates

    def connect(self):
        if self._display:
            return

        last_error = None
        for display_name in self._display_candidates():
            self._display = self._wayland.wl_display_connect(display_name)
            if not self._display:
                continue

            try:
                self._initialize_connected_display()
                return
            except GamescopeMetricsError as error:
                last_error = error
                self.close()

        if last_error:
            raise last_error
        raise GamescopeMetricsError(
            "Keine Gamescope-Wayland-Verbindung gefunden. "
            "Der Benchmark muss im Gaming-Modus laufen."
        )

    def _initialize_connected_display(self):
        registry_interface = _WlInterface.in_dll(
            self._wayland, "wl_registry_interface"
        )
        display_version = self._wayland.wl_proxy_get_version(self._display)
        self._registry = self._wayland.wl_proxy_marshal_flags(
            self._display,
            1,  # wl_display.get_registry
            ctypes.byref(registry_interface),
            display_version,
            0,
            None,
        )
        if not self._registry:
            raise GamescopeMetricsError("Wayland-Registry konnte nicht geöffnet werden")

        result = self._wayland.wl_proxy_add_listener(
            self._registry, self._registry_listener, None
        )
        if result != 0:
            raise GamescopeMetricsError("Wayland-Registry-Listener fehlgeschlagen")

        if self._wayland.wl_display_roundtrip(self._display) < 0:
            raise GamescopeMetricsError("Gamescope antwortet nicht")

        if not self._control:
            raise GamescopeMetricsError(
                "Gamescope-Control-Schnittstelle wurde nicht gefunden"
            )
        if self._control_version < self.PROTOCOL_VERSION:
            raise GamescopeMetricsError(
                "Gamescope ist zu alt für die Frametime-Abfrage "
                f"(Version {self._control_version}, benötigt: 6)"
            )

        # Empfängt die initiale Feature-Liste, sofern Gamescope sie sendet.
        if self._wayland.wl_display_roundtrip(self._display) < 0:
            raise GamescopeMetricsError("Gamescope-Initialisierung fehlgeschlagen")
        if self._feature_list_complete and not self._performance_feature_found:
            raise GamescopeMetricsError(
                "Gamescope meldet keine Unterstützung für Performance-Abfragen"
            )

    def _on_registry_global(self, _data, registry, name, interface, version):
        if not interface or interface.decode("utf-8") != "gamescope_control":
            return
        if self._control:
            return

        self._control_version = min(int(version), self.PROTOCOL_VERSION)
        self._control = self._wayland.wl_proxy_marshal_flags(
            registry,
            0,  # wl_registry.bind
            ctypes.byref(_GAMESCOPE_INTERFACE),
            self._control_version,
            0,
            ctypes.c_uint32(name),
            ctypes.c_char_p(_GAMESCOPE_INTERFACE.name),
            ctypes.c_uint32(self._control_version),
            None,
        )
        if self._control:
            self._wayland.wl_proxy_add_listener(
                self._control, self._control_listener, None
            )

    def _on_registry_remove(self, _data, _registry, _name):
        return

    def _on_feature_support(self, _data, _control, feature, version, _flags):
        if feature == self.PERFORMANCE_FEATURE and version > 0:
            self._performance_feature_found = True
        elif feature == 0:
            self._feature_list_complete = True

    def _on_active_display_info(
        self,
        _data,
        _control,
        _connector,
        _make,
        _model,
        _flags,
        _refresh_rates,
    ):
        return

    def _on_screenshot_taken(self, _data, _control, _path):
        return

    def _on_app_performance_stats(
        self, _data, _control, app_id, frametime_ns_lo, frametime_ns_hi
    ):
        frametime_ns = (int(frametime_ns_hi) << 32) | int(frametime_ns_lo)
        if app_id == self._app_id and 0 < frametime_ns < 10_000_000_000:
            frametime_ms = frametime_ns / 1_000_000.0
            fps = 1_000_000_000.0 / frametime_ns
            self._samples.append((time.monotonic(), fps, frametime_ms))

        if self._running:
            self._request_next_sample()

    def _request_next_sample(self):
        self._wayland.wl_proxy_marshal_flags(
            self._control,
            self.REQUEST_PERFORMANCE_STATS_OPCODE,
            None,
            self._control_version,
            0,
            ctypes.c_uint32(self._app_id),
        )

    def start(self, app_id):
        self.connect()
        if not app_id or int(app_id) == 769:
            raise GamescopeMetricsError(
                "Kein Spiel fokussiert. Nach dem Start bitte ins Spiel wechseln."
            )
        self._app_id = int(app_id)
        self._running = True
        self._samples.clear()
        self._request_next_sample()
        self._wayland.wl_display_flush(self._display)

    def poll(self, timeout=0.25):
        if not self._display or not self._running:
            return []

        self._wayland.wl_display_flush(self._display)
        display_fd = self._wayland.wl_display_get_fd(self._display)
        readable, _, _ = select.select([display_fd], [], [], timeout)
        if readable and self._wayland.wl_display_dispatch(self._display) < 0:
            raise GamescopeMetricsError("Gamescope-Verbindung wurde getrennt")

        samples = self._samples
        self._samples = []
        return samples

    def stop(self):
        self._running = False

    def close(self):
        self._running = False
        if self._display:
            self._wayland.wl_display_disconnect(self._display)
        self._display = None
        self._registry = None
        self._control = None
        self._control_version = 0
        self._feature_list_complete = False
        self._performance_feature_found = False

    @staticmethod
    def get_focused_app_id():
        x11 = _load_library([ctypes.util.find_library("X11"), "libX11.so.6"])
        x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
        x11.XOpenDisplay.restype = ctypes.c_void_p
        x11.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
        x11.XDefaultRootWindow.restype = ctypes.c_ulong
        x11.XInternAtom.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
        x11.XInternAtom.restype = ctypes.c_ulong
        x11.XGetWindowProperty.argtypes = [
            ctypes.c_void_p,
            ctypes.c_ulong,
            ctypes.c_ulong,
            ctypes.c_long,
            ctypes.c_long,
            ctypes.c_int,
            ctypes.c_ulong,
            ctypes.POINTER(ctypes.c_ulong),
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_ulong),
            ctypes.POINTER(ctypes.c_ulong),
            ctypes.POINTER(ctypes.POINTER(ctypes.c_ubyte)),
        ]
        x11.XGetWindowProperty.restype = ctypes.c_int
        x11.XFree.argtypes = [ctypes.c_void_p]
        x11.XFree.restype = ctypes.c_int
        x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
        x11.XCloseDisplay.restype = ctypes.c_int

        display_names = [None]
        display_env = os.environ.get("DISPLAY")
        if display_env:
            display_names.append(display_env.encode("utf-8"))
        for socket_path in sorted(glob.glob("/tmp/.X11-unix/X*")):
            suffix = os.path.basename(socket_path)[1:]
            candidate = f":{suffix}".encode("utf-8")
            if candidate not in display_names:
                display_names.append(candidate)

        display = None
        for display_name in display_names:
            display = x11.XOpenDisplay(display_name)
            if display:
                break
        if not display:
            raise GamescopeMetricsError("Gamescope-X11-Anzeige wurde nicht gefunden")

        try:
            root = x11.XDefaultRootWindow(display)
            for property_name in (
                b"GAMESCOPE_FOCUSED_APP_GFX",
                b"GAMESCOPE_FOCUSED_APP",
            ):
                atom = x11.XInternAtom(display, property_name, 1)
                if not atom:
                    continue

                actual_type = ctypes.c_ulong()
                actual_format = ctypes.c_int()
                item_count = ctypes.c_ulong()
                bytes_after = ctypes.c_ulong()
                value_ptr = ctypes.POINTER(ctypes.c_ubyte)()

                result = x11.XGetWindowProperty(
                    display,
                    root,
                    atom,
                    0,
                    1,
                    0,
                    6,  # XA_CARDINAL
                    ctypes.byref(actual_type),
                    ctypes.byref(actual_format),
                    ctypes.byref(item_count),
                    ctypes.byref(bytes_after),
                    ctypes.byref(value_ptr),
                )
                try:
                    if (
                        result == 0
                        and actual_format.value == 32
                        and item_count.value > 0
                        and value_ptr
                    ):
                        value = ctypes.cast(
                            value_ptr, ctypes.POINTER(ctypes.c_ulong)
                        )[0]
                        if value:
                            return int(value & 0xFFFFFFFF)
                finally:
                    if value_ptr:
                        x11.XFree(value_ptr)
        finally:
            x11.XCloseDisplay(display)

        raise GamescopeMetricsError("Keine fokussierte Gamescope-App gefunden")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback):
        self.close()
