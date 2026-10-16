"""GLITCH design system, reduzido ao que um README do GitHub consegue renderizar.

Tokens copiados do sistema GLITCH (tokens.json). Cada SVG embute só os glifos
que usa de cada fonte (subset woff2 em base64), porque um <img> no GitHub não
carrega fontes externas.
"""

import base64
import html
import io
from collections import defaultdict
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

FONT_DIR = Path(__file__).parent / "fonts"

# --- Tokens ---------------------------------------------------------------

PRIMITIVES = {
    "neutral-1000": "#0d0d0d", "neutral-950": "#141414", "neutral-900": "#1c1c1c",
    "neutral-850": "#222222", "neutral-800": "#2a2a2a", "neutral-600": "#6a6a66",
    "neutral-500": "#8a8a86", "neutral-100": "#f2f0eb", "neutral-50": "#fcfcfc",
    "paper-100": "#efece6", "paper-200": "#e4e0d9", "paper-300": "#d9d4cc",
    "paper-400": "#c9c4bb", "paper-600": "#7e7972", "paper-700": "#4d4943",
    "signal-500": "#00ff66", "signal-300": "#66ffa3", "signal-700": "#006b2e",
    "signal-900": "#0b3d22", "signal-100": "#c8f5d8",
}
P = PRIMITIVES

THEMES = {
    "dark": {
        "bg": P["neutral-1000"], "bg-surface": P["neutral-950"], "bg-surface-2": P["neutral-900"],
        "bg-active": P["neutral-850"], "border": P["neutral-800"], "border-strong": P["neutral-600"],
        "text": P["neutral-100"], "text-muted": P["neutral-500"], "interactive": P["neutral-100"],
        "text-inverse": P["neutral-1000"], "signal": P["signal-500"], "signal-ink": P["signal-500"],
        "signal-dim": P["signal-900"], "on-signal": P["neutral-1000"],
        "grid-dot": "#262626", "matrix-off": "#333331", "matrix-mid": P["neutral-600"],
        "matrix-on": P["neutral-100"], "scanline": P["neutral-100"],
    },
    "paper": {
        "bg": P["paper-100"], "bg-surface": P["paper-200"], "bg-surface-2": P["paper-300"],
        "bg-active": P["paper-400"], "border": P["paper-400"], "border-strong": P["paper-600"],
        "text": P["neutral-1000"], "text-muted": P["paper-700"], "interactive": P["neutral-1000"],
        "text-inverse": P["paper-100"], "signal": P["signal-500"], "signal-ink": P["signal-700"],
        "signal-dim": P["signal-100"], "on-signal": P["neutral-1000"],
        "grid-dot": "#d3cec6", "matrix-off": "#cbc6be", "matrix-mid": P["paper-600"],
        "matrix-on": P["neutral-1000"], "scanline": P["neutral-1000"],
    },
}

# Famílias: pixel (Silkscreen), mono (JetBrains Mono), sans (Geist).
FONT_FILES = {
    ("pixel", 400): "silkscreen-400.woff2",
    ("mono", 400): "jetbrains-mono-400.woff2",
    ("mono", 500): "jetbrains-mono-500.woff2",
    ("sans", 400): "geist-400.woff2",
    ("sans", 500): "geist-500.woff2",
}
FAMILY = {"pixel": "G Pixel", "mono": "G Mono", "sans": "G Sans"}

LS_LABEL = 0.04  # ls-label, +4%

# Movimento: dur-fast 120ms, dur-blink 1000ms, ease-step steps(3).
BASE_CSS = """
.blink{animation:blink 1s steps(1,end) infinite}
@keyframes blink{50%{opacity:0}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""

_fonts = {}


def _font(key):
    if key not in _fonts:
        _fonts[key] = TTFont(FONT_DIR / FONT_FILES[key])
    return _fonts[key]


def measure(s, font="mono", size=12, weight=400, ls=0.0):
    f = _font((font, weight))
    cmap, hmtx = f.getBestCmap(), f["hmtx"]
    upm = f["head"].unitsPerEm
    w = sum(hmtx[cmap.get(ord(c), ".notdef")][0] for c in s) * size / upm
    return w + ls * size * len(s)


def wrap(s, width, **kw):
    lines, cur = [], ""
    for word in s.split():
        nxt = f"{cur} {word}".strip()
        if cur and measure(nxt, **kw) > width:
            lines.append(cur)
            cur = word
        else:
            cur = nxt
    return lines + [cur] if cur else lines


def _subset_b64(key, chars):
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga", "zero", "tnum"]
    opts.name_IDs = []
    opts.notdef_outline = True
    font = TTFont(FONT_DIR / FONT_FILES[key])
    sub = subset.Subsetter(opts)
    sub.populate(text="".join(sorted(chars)))
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


class Svg:
    def __init__(self, w, h, theme, label):
        self.w, self.h, self.aria = w, h, label
        self.c = THEMES[theme]
        self.theme = theme
        self.parts, self.defs, self.css = [], [], [BASE_CSS]
        self.used = defaultdict(set)

    def col(self, name):
        return self.c.get(name, name)

    def add(self, s):
        self.parts.append(s)

    # --- primitivas -------------------------------------------------------

    def rect(self, x, y, w, h, fill="bg", stroke=None, rx=0, cls=None, extra=""):
        a = f'x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}"'
        a += f' fill="{self.col(fill)}"' if fill else ' fill="none"'
        if stroke:
            a += f' stroke="{self.col(stroke)}" stroke-width="1"'
        if rx:
            a += f' rx="{rx}"'
        if cls:
            a += f' class="{cls}"'
        self.add(f"<rect {a} {extra}/>")

    def line(self, x1, y1, x2, y2, stroke="border", dash=None, width=1):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="M{x1:g} {y1:g}L{x2:g} {y2:g}" stroke="{self.col(stroke)}" '
                 f'stroke-width="{width}"{d} fill="none"/>')

    def text(self, x, y, s, font="mono", size=12, weight=400, fill="text",
             anchor="start", ls=0.0, cls=None, tnum=False):
        self.used[(font, weight)].update(s)
        a = f'x="{x:g}" y="{y:g}" font-family="{FAMILY[font]}" font-size="{size}"'
        if weight != 400:
            a += f' font-weight="{weight}"'
        a += f' fill="{self.col(fill)}"'
        if anchor != "start":
            a += f' text-anchor="{anchor}"'
        if ls:
            a += f' letter-spacing="{ls * size:.2f}"'
        if cls:
            a += f' class="{cls}"'
        if tnum:
            a += ' style="font-feature-settings:\'tnum\',\'zero\'"'
        self.add(f"<text {a}>{html.escape(s)}</text>")
        return measure(s, font, size, weight, ls)

    def label(self, x, y, s, size=12, fill="text-muted", anchor="start", weight=500, cls=None):
        """label-10 / label-12: mono, uppercase, +4%."""
        s = s.upper()
        w = measure(s, "mono", size, weight, LS_LABEL)
        if anchor == "end":
            x -= w
        elif anchor == "middle":
            x -= w / 2
        self.text(x, y, s, "mono", size, weight, fill, ls=LS_LABEL, cls=cls)
        return w

    # --- padrões GLITCH ---------------------------------------------------

    def dotgrid(self, x, y, w, h, pitch=12):
        pid = "dg"
        self.defs.append(
            f'<pattern id="{pid}" width="{pitch}" height="{pitch}" patternUnits="userSpaceOnUse">'
            f'<rect x="{pitch / 2 - .5:g}" y="{pitch / 2 - .5:g}" width="1" height="1" '
            f'fill="{self.col("grid-dot")}"/></pattern>')
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{pid})"/>')

    def scanlines(self):
        self.defs.append(
            '<pattern id="sl" width="4" height="4" patternUnits="userSpaceOnUse">'
            f'<rect width="4" height="1" fill="{self.col("scanline")}"/></pattern>')
        # opacity-scanline: 0.05, nunca mais que isso.
        self.add(f'<rect width="{self.w}" height="{self.h}" fill="url(#sl)" opacity="0.05" '
                 'pointer-events="none"/>')

    def corners(self, x, y, w, h, size=10, stroke="text"):
        c = self.col(stroke)
        d = (f"M{x} {y + size}V{y}H{x + size}"
             f"M{x + w - size} {y}H{x + w}V{y + size}"
             f"M{x + w} {y + h - size}V{y + h}H{x + w - size}"
             f"M{x + size} {y + h}H{x}V{y + h - size}")
        self.add(f'<path d="{d}" stroke="{c}" stroke-width="1" fill="none"/>')

    def ruler(self, x, y, w, step=8, major=64, stroke="border-strong"):
        d = "".join(
            f"M{x + i:g} {y}v{6 if i % major == 0 else 3}" for i in range(0, int(w) + 1, step))
        self.add(f'<path d="{d}" stroke="{self.col(stroke)}" stroke-width="1"/>')

    def segmented(self, x, y, w, head):
        """Regra segmentada: trecho sólido sob o rótulo, o resto em hairline."""
        self.rect(x, y - 1, head, 2, "text")
        self.line(x + head + 4, y, x + w, y, "border")

    def dotted(self, x, y, w, stroke="matrix-off"):
        self.line(x, y, x + w, y, stroke, dash="1 3")

    def chip(self, x, y, s, h=24, fill="bg-surface-2", stroke="border", ink="text", size=12):
        tw = measure(s, "mono", size, 400)
        w = tw + 16
        self.rect(x + .5, y + .5, w - 1, h - 1, fill, stroke, rx=1)
        self.text(x + 8, y + h / 2 + size * 0.36, s, "mono", size, 400, ink)
        return w

    def matrix(self, x, y, cols, rows, on, pitch=6, cell=5, fill_on="matrix-on"):
        """on: função (col, row) -> None | nome de cor."""
        out = []
        for r in range(rows):
            for c in range(cols):
                f = on(c, r)
                color = self.col(f) if f else self.col("matrix-off")
                out.append(f'<rect x="{x + c * pitch:g}" y="{y + r * pitch:g}" '
                           f'width="{cell}" height="{cell}" fill="{color}"/>')
        self.add("".join(out))

    def bitmap(self, x, y, rows, pitch=8, cell=7, palette=None):
        palette = palette or {"#": "matrix-on", "+": "matrix-mid", "*": "signal"}
        out = []
        for r, row in enumerate(rows):
            for c, ch in enumerate(row):
                if ch in palette:
                    out.append(f'<rect x="{x + c * pitch:g}" y="{y + r * pitch:g}" '
                               f'width="{cell}" height="{cell}" fill="{self.col(palette[ch])}"/>')
        self.add("".join(out))

    # --- saída ------------------------------------------------------------

    def render(self):
        faces = []
        for (fam, wt), chars in sorted(self.used.items()):
            b64 = _subset_b64((fam, wt), chars | {" "})
            faces.append(f'@font-face{{font-family:"{FAMILY[fam]}";font-weight:{wt};'
                         f'src:url(data:font/woff2;base64,{b64}) format("woff2")}}')
        style = "".join(faces) + "".join(self.css)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
            f'width="{self.w}" height="{self.h}" role="img" aria-label="{html.escape(self.aria)}">'
            f"<title>{html.escape(self.aria)}</title>"
            f"<defs><style>{style}</style>{''.join(self.defs)}</defs>"
            + "".join(self.parts) + "</svg>\n")
