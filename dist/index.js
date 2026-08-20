const manifest = {"name":"SDC Benchmark"};
const API_VERSION = 2;
const internalAPIConnection = window.__DECKY_SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED_deckyLoaderAPIInit;
if (!internalAPIConnection) {
    throw new Error('[@decky/api]: Failed to connect to the loader as as the loader API was not initialized. This is likely a bug in Decky Loader.');
}
let api;
try {
    api = internalAPIConnection.connect(API_VERSION, manifest.name);
}
catch {
    api = internalAPIConnection.connect(1, manifest.name);
    console.warn(`[@decky/api] Requested API version ${API_VERSION} but the running loader only supports version 1. Some features may not work.`);
}
if (api._version != API_VERSION) {
    console.warn(`[@decky/api] Requested API version ${API_VERSION} but the running loader only supports version ${api._version}. Some features may not work.`);
}
const callable = api.callable;
const definePlugin = (fn) => {
    return (...args) => {
        return fn(...args);
    };
};

var DefaultContext = {
  color: undefined,
  size: undefined,
  className: undefined,
  style: undefined,
  attr: undefined
};
var IconContext = SP_REACT.createContext && /*#__PURE__*/SP_REACT.createContext(DefaultContext);

var _excluded = ["attr", "size", "title"];
function _objectWithoutProperties(source, excluded) { if (source == null) return {}; var target = _objectWithoutPropertiesLoose(source, excluded); var key, i; if (Object.getOwnPropertySymbols) { var sourceSymbolKeys = Object.getOwnPropertySymbols(source); for (i = 0; i < sourceSymbolKeys.length; i++) { key = sourceSymbolKeys[i]; if (excluded.indexOf(key) >= 0) continue; if (!Object.prototype.propertyIsEnumerable.call(source, key)) continue; target[key] = source[key]; } } return target; }
function _objectWithoutPropertiesLoose(source, excluded) { if (source == null) return {}; var target = {}; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { if (excluded.indexOf(key) >= 0) continue; target[key] = source[key]; } } return target; }
function _extends() { _extends = Object.assign ? Object.assign.bind() : function (target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i]; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { target[key] = source[key]; } } } return target; }; return _extends.apply(this, arguments); }
function ownKeys(e, r) { var t = Object.keys(e); if (Object.getOwnPropertySymbols) { var o = Object.getOwnPropertySymbols(e); r && (o = o.filter(function (r) { return Object.getOwnPropertyDescriptor(e, r).enumerable; })), t.push.apply(t, o); } return t; }
function _objectSpread(e) { for (var r = 1; r < arguments.length; r++) { var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? ownKeys(Object(t), true).forEach(function (r) { _defineProperty(e, r, t[r]); }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : ownKeys(Object(t)).forEach(function (r) { Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r)); }); } return e; }
function _defineProperty(obj, key, value) { key = _toPropertyKey(key); if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }
function _toPropertyKey(t) { var i = _toPrimitive(t, "string"); return "symbol" == typeof i ? i : i + ""; }
function _toPrimitive(t, r) { if ("object" != typeof t || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r); if ("object" != typeof i) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
function Tree2Element(tree) {
  return tree && tree.map((node, i) => /*#__PURE__*/SP_REACT.createElement(node.tag, _objectSpread({
    key: i
  }, node.attr), Tree2Element(node.child)));
}
function GenIcon(data) {
  return props => /*#__PURE__*/SP_REACT.createElement(IconBase, _extends({
    attr: _objectSpread({}, data.attr)
  }, props), Tree2Element(data.child));
}
function IconBase(props) {
  var elem = conf => {
    var {
        attr,
        size,
        title
      } = props,
      svgProps = _objectWithoutProperties(props, _excluded);
    var computedSize = size || conf.size || "1em";
    var className;
    if (conf.className) className = conf.className;
    if (props.className) className = (className ? className + " " : "") + props.className;
    return /*#__PURE__*/SP_REACT.createElement("svg", _extends({
      stroke: "currentColor",
      fill: "currentColor",
      strokeWidth: "0"
    }, conf.attr, attr, svgProps, {
      className: className,
      style: _objectSpread(_objectSpread({
        color: props.color || conf.color
      }, conf.style), props.style),
      height: computedSize,
      width: computedSize,
      xmlns: "http://www.w3.org/2000/svg"
    }), title && /*#__PURE__*/SP_REACT.createElement("title", null, title), props.children);
  };
  return IconContext !== undefined ? /*#__PURE__*/SP_REACT.createElement(IconContext.Consumer, null, conf => elem(conf)) : elem(DefaultContext);
}

// THIS FILE IS AUTO GENERATED
function FaChartLine (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M496 384H64V80c0-8.84-7.16-16-16-16H16C7.16 64 0 71.16 0 80v336c0 17.67 14.33 32 32 32h464c8.84 0 16-7.16 16-16v-32c0-8.84-7.16-16-16-16zM464 96H345.94c-21.38 0-32.09 25.85-16.97 40.97l32.4 32.4L288 242.75l-73.37-73.37c-12.5-12.5-32.76-12.5-45.25 0l-68.69 68.69c-6.25 6.25-6.25 16.38 0 22.63l22.62 22.62c6.25 6.25 16.38 6.25 22.63 0L192 237.25l73.37 73.37c12.5 12.5 32.76 12.5 45.25 0l96-96 32.4 32.4c15.12 15.12 40.97 4.41 40.97-16.97V112c.01-8.84-7.15-16-15.99-16z"},"child":[]}]})(props);
}function FaImage (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M464 448H48c-26.51 0-48-21.49-48-48V112c0-26.51 21.49-48 48-48h416c26.51 0 48 21.49 48 48v288c0 26.51-21.49 48-48 48zM112 120c-30.928 0-56 25.072-56 56s25.072 56 56 56 56-25.072 56-56-25.072-56-56-56zM64 384h384V272l-87.515-87.515c-4.686-4.686-12.284-4.686-16.971 0L208 320l-55.515-55.515c-4.686-4.686-12.284-4.686-16.971 0L64 336v48z"},"child":[]}]})(props);
}function FaPlay (props) {
  return GenIcon({"attr":{"viewBox":"0 0 448 512"},"child":[{"tag":"path","attr":{"d":"M424.4 214.7L72.4 6.6C43.8-10.3 0 6.1 0 47.9V464c0 37.5 40.7 60.1 72.4 41.3l352-208c31.4-18.5 31.5-64.1 0-82.6z"},"child":[]}]})(props);
}function FaStop (props) {
  return GenIcon({"attr":{"viewBox":"0 0 448 512"},"child":[{"tag":"path","attr":{"d":"M400 32H48C21.5 32 0 53.5 0 80v352c0 26.5 21.5 48 48 48h352c26.5 0 48-21.5 48-48V80c0-26.5-21.5-48-48-48z"},"child":[]}]})(props);
}

const startBenchmark = callable("start_benchmark");
const stopBenchmark = callable("stop_benchmark");
const getStatus = callable("get_status");
const getLastPngPreview = callable("get_last_png_preview");
const withTimeout = (request, action, timeoutMs = 5000) => new Promise((resolve, reject) => {
    const timer = window.setTimeout(() => reject(new Error(`${action}: Das Backend antwortet nicht.`)), timeoutMs);
    request.then((result) => {
        window.clearTimeout(timer);
        resolve(result);
    }, (error) => {
        window.clearTimeout(timer);
        reject(error);
    });
});
const errorMessage = (error, fallback) => error instanceof Error && error.message ? error.message : fallback;
const formatDuration = (seconds) => {
    if (seconds < 60) {
        return `${seconds} Sekunden`;
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    const minuteText = minutes === 1 ? "1 Minute" : `${minutes} Minuten`;
    return remainingSeconds
        ? `${minuteText} ${remainingSeconds} Sekunden`
        : minuteText;
};
function BenchmarkPreviewModal({ dataUrl, path, closeModal, }) {
    return (SP_JSX.jsx(DFL.ConfirmModal, { bAlertDialog: true, bAllowFullSize: true, closeModal: closeModal, onOK: closeModal, strTitle: "Letzter Benchmark-Bericht", strOKButtonText: "Schlie\u00DFen", children: SP_JSX.jsxs("div", { style: { width: "100%", maxWidth: "1280px" }, children: [SP_JSX.jsx("img", { src: dataUrl, alt: "Letzter SDC-Benchmark-Bericht", style: {
                        display: "block",
                        width: "100%",
                        height: "auto",
                        borderRadius: "8px",
                    } }), SP_JSX.jsx("div", { style: {
                        marginTop: "10px",
                        fontSize: "0.75em",
                        opacity: 0.75,
                        wordBreak: "break-all",
                    }, children: path })] }) }));
}
// Erzeugt den Start-/Endton ohne zusätzliche Audiodateien.
const playBeep = (frequency = 880, durationMs = 250) => {
    try {
        const AudioContextClass = window.AudioContext ??
            window
                .webkitAudioContext;
        if (!AudioContextClass) {
            return;
        }
        const audioContext = new AudioContextClass();
        const oscillator = audioContext.createOscillator();
        const gain = audioContext.createGain();
        oscillator.type = "sine";
        oscillator.frequency.setValueAtTime(frequency, audioContext.currentTime);
        gain.gain.setValueAtTime(0.1, audioContext.currentTime);
        oscillator.connect(gain);
        gain.connect(audioContext.destination);
        oscillator.start();
        window.setTimeout(() => {
            oscillator.stop();
            void audioContext.close();
        }, durationMs);
    }
    catch (error) {
        console.error("SDC Benchmark: Audio-Fehler", error);
    }
};
function Content() {
    const [duration, setDuration] = SP_REACT.useState(60);
    const [isRunning, setIsRunning] = SP_REACT.useState(false);
    const [statusText, setStatusText] = SP_REACT.useState("Bereit");
    const [lastCsv, setLastCsv] = SP_REACT.useState("");
    const [lastPng, setLastPng] = SP_REACT.useState("");
    const [measurementSource, setMeasurementSource] = SP_REACT.useState("Gamescope");
    const [previewLoading, setPreviewLoading] = SP_REACT.useState(false);
    const [previewError, setPreviewError] = SP_REACT.useState("");
    const previousStatus = SP_REACT.useRef("Idle");
    SP_REACT.useEffect(() => {
        let active = true;
        let requestPending = false;
        const pollStatus = async () => {
            if (requestPending) {
                return;
            }
            requestPending = true;
            try {
                const result = await withTimeout(getStatus(), "Statusabfrage", 3000);
                if (!active) {
                    return;
                }
                setIsRunning(result.is_running);
                setLastCsv(result.last_csv || "");
                setLastPng(result.last_png || "");
                setMeasurementSource(result.source || "Gamescope");
                if (previousStatus.current === "Countdown" && result.status === "Running") {
                    playBeep(880, 300);
                }
                else if (previousStatus.current === "Running" &&
                    result.status === "Finished") {
                    playBeep(1046, 200);
                    window.setTimeout(() => playBeep(1318, 300), 250);
                }
                previousStatus.current = result.status;
                switch (result.status) {
                    case "Countdown":
                        setStatusText(`Startet in ${result.countdown}s … (ins Spiel wechseln!)`);
                        break;
                    case "Running":
                        setStatusText(`Benchmark läuft – noch ${result.time_left}s · ${result.sample_count} Frames`);
                        break;
                    case "Finished":
                        setStatusText(`Benchmark abgeschlossen! ${result.sample_count} Frames erfasst.`);
                        break;
                    case "Stopped":
                        setStatusText("Abgebrochen.");
                        break;
                    case "Error":
                        setStatusText(`Fehler: ${result.error || "Unbekannter Fehler"}`);
                        break;
                    default:
                        setStatusText("Bereit");
                }
            }
            catch (error) {
                if (active) {
                    console.error("SDC Benchmark: Statusabfrage fehlgeschlagen", error);
                    setIsRunning(false);
                    setStatusText(`${errorMessage(error, "Backend nicht erreichbar")} ` +
                        "Plugin oder Decky bitte neu starten.");
                }
            }
            finally {
                requestPending = false;
            }
        };
        void pollStatus();
        const interval = window.setInterval(() => void pollStatus(), 500);
        return () => {
            active = false;
            window.clearInterval(interval);
        };
    }, []);
    const handleStart = async () => {
        setStatusText("Initialisiere …");
        try {
            const result = await withTimeout(startBenchmark(duration), "Benchmark-Start");
            if (result.status === "error") {
                setStatusText(result.message || "Start fehlgeschlagen");
            }
            else {
                setIsRunning(true);
                setStatusText("Start bestätigt – Countdown läuft …");
            }
        }
        catch (error) {
            console.error("SDC Benchmark: Start fehlgeschlagen", error);
            setIsRunning(false);
            setStatusText(`${errorMessage(error, "Start fehlgeschlagen")} ` +
                "Plugin oder Decky bitte neu starten.");
        }
    };
    const handleStop = async () => {
        try {
            await withTimeout(stopBenchmark(), "Benchmark-Abbruch");
        }
        catch (error) {
            console.error("SDC Benchmark: Abbruch fehlgeschlagen", error);
            setStatusText(errorMessage(error, "Abbruch fehlgeschlagen"));
        }
    };
    const handlePreview = async () => {
        setPreviewLoading(true);
        setPreviewError("");
        try {
            const result = await withTimeout(getLastPngPreview(), "PNG-Vorschau", 8000);
            if (result.status === "error" || !result.data_url) {
                setPreviewError(result.message || "PNG-Vorschau konnte nicht geladen werden.");
                return;
            }
            DFL.showModal(SP_JSX.jsx(BenchmarkPreviewModal, { dataUrl: result.data_url, path: result.path || lastPng }), undefined, {
                strTitle: "SDC Benchmark",
                bHideMainWindowForPopouts: false,
                bNeverPopOut: true,
            });
        }
        catch (error) {
            console.error("SDC Benchmark: PNG-Vorschau fehlgeschlagen", error);
            setPreviewError(errorMessage(error, "PNG-Vorschau fehlgeschlagen"));
        }
        finally {
            setPreviewLoading(false);
        }
    };
    return (SP_JSX.jsxs(DFL.PanelSection, { title: "Benchmark Tool", children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.SliderField, { label: "Benchmark-Dauer", description: `Gewählte Laufzeit: ${formatDuration(duration)} (${duration} s)`, value: duration, min: 30, max: 360, step: 30, showValue: true, valueSuffix: " Sekunden", disabled: isRunning, onChange: setDuration }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: "Status", childrenLayout: "below", children: statusText }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: "Messquelle", children: measurementSource }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: !isRunning ? (SP_JSX.jsxs(DFL.ButtonItem, { layout: "below", onClick: () => void handleStart(), children: [SP_JSX.jsx(FaPlay, { style: { marginRight: "8px" } }), " Starten (5 s Verz\u00F6gerung)"] })) : (SP_JSX.jsxs(DFL.ButtonItem, { layout: "below", onClick: () => void handleStop(), children: [SP_JSX.jsx(FaStop, { style: { marginRight: "8px" } }), " Abbrechen"] })) }), lastCsv && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: "CSV-Datei", childrenLayout: "below", children: SP_JSX.jsx("div", { style: { fontSize: "0.8em", wordBreak: "break-all" }, children: lastCsv }) }) })), lastPng && (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsxs(DFL.ButtonItem, { layout: "below", disabled: previewLoading, onClick: () => void handlePreview(), children: [SP_JSX.jsx(FaImage, { style: { marginRight: "8px" } }), previewLoading ? "Lade Vorschau …" : "Letztes PNG anzeigen"] }) }), previewError && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: "Vorschau-Fehler", childrenLayout: "below", children: previewError }) })), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: "Diagramm PNG", childrenLayout: "below", children: SP_JSX.jsx("div", { style: { fontSize: "0.8em", wordBreak: "break-all" }, children: lastPng }) }) })] }))] }));
}
var index = definePlugin(() => ({
    name: "SDC Benchmark",
    titleView: SP_JSX.jsx("div", { className: DFL.staticClasses.Title, children: "SDC Benchmark" }),
    content: SP_JSX.jsx(Content, {}),
    icon: SP_JSX.jsx(FaChartLine, {}),
    onDismount() {
        console.log("SDC Benchmark wurde entladen");
    },
}));

export { index as default };
//# sourceMappingURL=index.js.map
