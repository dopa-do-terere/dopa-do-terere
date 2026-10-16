"""Gera os SVGs estáticos do README (tema dark e paper).

    pip install fonttools brotli
    python scripts/build.py
"""

from pathlib import Path

from glitch import LS_LABEL, Svg, measure, wrap

OUT = Path(__file__).resolve().parent.parent / "assets"
W = 840  # largura útil do README no GitHub: SVG em escala 1:1

VERSION = "v2026.10"

# Guampa de tereré, 8 px por célula. # = traço, + = erva (dither).
GUAMPA = [
    "............##",
    "...........##.",
    "..........##..",
    ".........##...",
    ".############.",
    ".#+.+.+##+.+#.",
    ".#.+.+##.+.+#.",
    "..#.+.+.+.+#..",
    "..#+.+.+.+.#..",
    "..#.+.+.+.+#..",
    "...#+.+.+.#...",
    "...#.+.+.+#...",
    "....######....",
    "...########...",
]

SECTIONS = [
    ("01", "SOBRE", "Quem sou eu."),
    ("02", "STACK", "Com o que eu construo."),
    ("03", "PROJETOS", "Projetos em destaque."),
    ("04", "TELEMETRIA", "Em números."),
    ("05", "CONTATO", "Vamos conversar."),
]

WHOAMI = [
    ("NOME", "Dopa do Tereré"),
    ("FUNÇÃO", "CEO @ Type77 · Sócio @ ZROOT"),
    ("BASE", "Chapecó/SC, Brasil"),
    ("FORMAÇÃO", "Ciência da Computação @ Unochapecó"),
    ("CONSTRUINDO", "Sistemas de gestão e automação para clientes da Type77"),
    ("ESTUDANDO", "Arquitetura de sistemas, IoT e infraestrutura"),
    ("PERGUNTE SOBRE", "Sistemas sob medida, controle de acesso, catracas, dashboards"),
    ("COMBUSTÍVEL", "Tereré gelado"),
]

STACK = [
    ("LINGUAGENS", ["TypeScript", "JavaScript", "Python", "PHP", "C++"]),
    ("BACK-END", ["Node.js", "Express", "Laravel", "Flask"]),
    ("FRONT-END", ["React", "Vite", "HTML", "CSS"]),
    ("DADOS & INFRA", ["PostgreSQL", "Docker", "Linux", "Git", "GitHub"]),
    ("IOT", ["Raspberry Pi", "Arduino"]),
]

PROJECTS = [
    ("wms", "WMS-Inviolavel", "LOGÍSTICA", "Gestão de estoque (WMS) completa.",
     ["Node.js", "TypeScript", "PostgreSQL", "React"]),
    ("tidesk", "TIDESK", "HELPDESK", "Helpdesk completo de tickets e suporte.",
     ["React", "TypeScript", "Node.js"]),
    ("zcontrol", "zControl (zIN)", "ACESSO",
     "SaaS de gestão de acessos integrado a catracas Hikvision.",
     ["Laravel", "PostgreSQL", "Docker"]),
    ("inviokey", "InvioKey", "IOT",
     "Armário inteligente de chaves: totem, painel admin e hardware.",
     ["Raspberry Pi", "IoT"]),
    ("inviinstall", "InvioInstall", "API", "Instalações, orçamentos e estoque via API REST.",
     ["Laravel", "REST API"]),
    ("ziq", "ZIQ API", "API", "API containerizada.", ["Node.js", "PostgreSQL", "Docker"]),
    ("zapy", "Zapy", "IOT", "Painel de controle de relés via GPIO.",
     ["Python", "Flask", "Raspberry Pi"]),
    ("flesak", "Cronograma Flesak", "DASHBOARD",
     "Clientes, plano de ação, KPIs e dashboard de performance.",
     ["JavaScript", "Dashboard"]),
]


def save(name, theme, svg):
    (OUT / f"{name}-{theme}.svg").write_text(svg.render(), encoding="utf-8")


# --- banner -----------------------------------------------------------------

def banner(theme):
    H = 420
    s = Svg(W, H, theme, "Dopa do Tereré — full-stack developer, CEO @ Type77, sócio @ ZROOT")
    s.rect(0, 0, W, H, "bg")
    s.dotgrid(0, 0, W, H)

    # barra de status
    s.label(24, 24, "DOPA_DO_TERERE // PERFIL")
    w = s.label(W - 24, 24, "SYSTEM ONLINE", fill="text", anchor="end")
    s.rect(W - 24 - w - 16, 16, 8, 8, "signal", cls="blink")
    s.line(0, 36.5, W, 36.5, "border")
    s.ruler(24.5, 37, W - 48)

    # título em pixel, com glitch horizontal breve
    size, x0 = 84, 22
    l1, l2 = "DOPA DO", "TERERÉ"
    y1, y2 = 140, 244
    s.css.append(
        ".gl{animation:gl 7s steps(1,end) infinite}"
        "@keyframes gl{0%,88%,100%{transform:none;opacity:0}"
        "89%{transform:translateX(-7px);opacity:1}90%{transform:translateX(5px);opacity:1}"
        "91%{transform:translateX(-2px);opacity:1}92%{transform:none;opacity:0}}"
        ".gs{animation:gs 7s steps(1,end) infinite}"
        "@keyframes gs{0%,88%,92%,100%{transform:none}89%{transform:translateX(4px)}"
        "90%{transform:translateX(-3px)}}")
    s.defs.append(f'<clipPath id="band1"><rect x="0" y="{y1 - 44}" width="{W}" height="14"/></clipPath>'
                  f'<clipPath id="band2"><rect x="0" y="{y2 - 30}" width="{W}" height="10"/></clipPath>')
    s.add('<g class="gs">')
    s.text(x0, y1, l1, "pixel", size, fill="text", ls=-0.02)
    s.text(x0, y2, l2, "pixel", size, fill="text", ls=-0.02)
    s.add("</g>")
    s.add('<g class="gl" clip-path="url(#band1)">')
    s.rect(0, y1 - 44, W, 14, "bg")
    s.text(x0, y1, l1, "pixel", size, fill="signal-ink", ls=-0.02)
    s.add("</g>")
    s.add('<g class="gl" clip-path="url(#band2)" style="animation-delay:-.2s">')
    s.rect(0, y2 - 30, W, 10, "bg")
    s.text(x0, y2, l2, "pixel", size, fill="text", ls=-0.02)
    s.add("</g>")
    tw = measure(l2, "pixel", size, 400, -0.02)
    s.rect(x0 + tw + 10, y2 - 12, 44, 12, "signal", cls="blink")

    # guampa
    gx, gy = 640, 84
    s.bitmap(gx, gy, GUAMPA, pitch=10, cell=9)
    s.label(gx + 70, gy + 14 * 10 + 22, "FIG.01 // GUAMPA", size=10, anchor="middle")

    # subtítulo e DataChips
    s.text(24, 292, "Full-stack developer. Sistemas de ponta a ponta.", "sans", 22, 400, "text",
           ls=-0.01)
    x = 24
    for c in ["CEO @ TYPE77", "SÓCIO @ ZROOT", "CIÊNCIA DA COMPUTAÇÃO @ UNOCHAPECÓ"]:
        x += s.chip(x, 312, c) + 8

    # rodapé do banner
    s.line(0, 368.5, W, 368.5, "border")
    s.label(24, 394, "CHAPECÓ/SC // BR · 27°06'S 52°37'W")
    s.label(W - 24, 394, f"{VERSION} · PT-BR", anchor="end")

    s.corners(8.5, 44.5, W - 17, 316)
    s.scanlines()
    save("banner", theme, s)


# --- cabeçalho de seção -----------------------------------------------------

def section(theme, num, key, title):
    H = 92
    s = Svg(W, H, theme, f"{num} // {key} — {title}")
    s.label(0, 22, f"{num} // {key}", fill="text")
    s.label(W, 22, f"SEC_{num} · {num} OF {len(SECTIONS):02d}", anchor="end")
    s.text(0, 66, title, "sans", 28, 400, "text", ls=-0.01)
    head = measure(f"{num} // {key}", "mono", 12, 500, LS_LABEL)
    s.segmented(0, 84, W, head)
    s.ruler(W - 128.5, 85, 128, step=8, major=32)
    save(f"head-{key.lower()}", theme, s)


# --- whoami -----------------------------------------------------------------

def whoami(theme):
    row = 30
    top = 84
    H = top + len(WHOAMI) * row + 96
    s = Svg(W, H, theme, "Perfil: " + "; ".join(f"{k}: {v}" for k, v in WHOAMI))
    s.rect(.5, .5, W - 1, H - 1, "bg-surface", "border")
    s.label(16, 22, "SYS // WHOAMI")
    s.label(W - 16, 22, "PERFIL.SYS", anchor="end")
    s.line(0, 34.5, W, 34.5, "border")

    s.text(16, 64, ">", "mono", 14, 500, "signal-ink")
    w = s.text(32, 64, "whoami", "mono", 14, 400, "text")
    s.rect(32 + w + 4, 52, 8, 14, "signal", cls="blink")

    y = top
    for i, (k, v) in enumerate(WHOAMI):
        s.dotted(16, y + .5, W - 32)
        s.label(16, y + 20, k, size=10)
        s.text(184, y + 20, v, "mono", 14, 400, "text")
        y += row
    s.dotted(16, y + .5, W - 32)

    # SignalItem
    y += 20
    s.rect(16, y, W - 32, 56, "signal-dim")
    s.text(32, y + 24, "↗", "mono", 14, 500, "signal-ink")
    s.label(52, y + 23, "SINAL DETECTADO", size=10, fill="signal-ink")
    s.text(52, y + 44, "Gosto de ver o software mexer no mundo físico: relés, catracas e armários.",
           "sans", 14, 400, "text")

    s.corners(4.5, 4.5, W - 9, H - 9, size=8)
    save("whoami", theme, s)


# --- stack ------------------------------------------------------------------

def stack(theme):
    row = 44
    top = 48
    H = top + len(STACK) * row + 56
    total = sum(len(v) for _, v in STACK)
    flat = [i for _, v in STACK for i in v]
    s = Svg(W, H, theme, "Stack: " + ", ".join(flat))
    s.rect(.5, .5, W - 1, H - 1, "bg-surface", "border")
    s.label(16, 22, "STACK // MÓDULOS CARREGADOS")
    s.label(W - 16, 22, f"{total:02d} / {total:02d} ✓", fill="signal-ink", anchor="end")
    s.line(0, 34.5, W, 34.5, "border")

    y = top
    for i, (cat, items) in enumerate(STACK):
        s.label(16, y + 17, f"{i + 1:02d}", size=10)
        s.label(44, y + 17, cat, size=10, fill="text")
        x = 184
        for it in items:
            x += s.chip(x, y, it) + 8
        y += row
        s.line(16, y - 10.5, W - 16, y - 10.5, "border", dash="4 4")

    # ticker (ease-linear é para tickers)
    y = H - 34
    s.line(0, y - .5, W, y - .5, "border")
    tick = "  ·  ".join(t.upper() for t in flat) + "  ·  "
    tw = measure(tick, "mono", 12, 400, LS_LABEL)
    s.defs.append(f'<clipPath id="tkc"><rect x="1" y="{y}" width="{W - 2}" height="32"/></clipPath>')
    s.add('<g clip-path="url(#tkc)"><g>'
          f'<animateTransform attributeName="transform" type="translate" from="0 0" '
          f'to="-{tw:.2f} 0" dur="40s" repeatCount="indefinite"/>')
    for k in range(3):
        s.text(16 + k * tw, y + 21, tick, "mono", 12, 400, "text-muted", ls=LS_LABEL)
    s.add("</g></g>")
    save("stack", theme, s)


# --- cards de projeto -------------------------------------------------------

def card(theme, idx, slug, name, kind, desc, chips):
    CW, H = 400, 176
    s = Svg(CW, H, theme, f"{name}: {desc} Stack: {', '.join(chips)}")
    s.rect(.5, .5, CW - 1, H - 1, "bg-surface", "border")
    s.label(16, 22, f"PRJ_{idx:03d}", size=10)
    s.label(CW - 16, 22, f"{kind} ↗", size=10, fill="text", anchor="end")
    s.segmented(16, 34, CW - 32, measure(f"PRJ_{idx:03d}", "mono", 10, 500, LS_LABEL))
    s.text(16, 66, name, "sans", 20, 500, "text")
    for i, ln in enumerate(wrap(desc, CW - 32, font="sans", size=14)[:2]):
        s.text(16, 92 + i * 20, ln, "sans", 14, 400, "text-muted")
    x = 16
    for c in chips:
        x += s.chip(x, H - 40, c) + 6
    save(f"card-{slug}", theme, s)


# --- botões -----------------------------------------------------------------

def button(theme, slug, text, primary):
    BW, H = 220, 44  # size-touch
    s = Svg(BW, H, theme, text)
    if primary:
        s.rect(0, 0, BW, H, "signal", rx=1)
        ink = "on-signal"
    else:
        s.rect(.5, .5, BW - 1, H - 1, "bg-surface-2", "border-strong", rx=1)
        ink = "text"
    s.label(BW / 2, H / 2 + 4.5, text, fill=ink, anchor="middle")
    save(f"btn-{slug}", theme, s)


# --- rodapé -----------------------------------------------------------------

def footer(theme):
    H = 168
    s = Svg(W, H, theme, "Fim da transmissão. Valeu pela visita. Bora um tereré?")
    s.rect(0, 0, W, H, "bg")
    s.line(0, .5, W, .5, "border")
    s.ruler(.5, 1, W - 1)
    s.label(0, 34, "EOF // FIM DA TRANSMISSÃO")
    s.label(W, 34, "DOPA_DO_TERERE", anchor="end")
    s.text(0, 88, "VALEU PELA VISITA", "pixel", 40, fill="text", ls=-0.02)
    w = s.text(0, 120, "Bora um tereré?", "mono", 16, 400, "text")
    s.rect(w + 4, 106, 9, 16, "signal", cls="blink")

    # matriz: sinal entrando da esquerda para a direita
    cols, rows = 40, 5
    x0 = W - cols * 6 + 1
    s.matrix(x0, 72, cols, rows,
             lambda c, r: ("signal" if c == cols - 1 and r == 2 else
                           "matrix-on" if (c * 7 + r * 3) % 11 < c // 6 else
                           "matrix-mid" if (c + r * 5) % 9 == 0 else None))
    s.line(0, 148.5, W, 148.5, "border")
    s.label(0, H - 2, f"{VERSION} · GLITCH DESIGN SYSTEM", size=10)
    s.label(W, H - 2, "© 2026", size=10, anchor="end")
    save("footer", theme, s)


def main():
    OUT.mkdir(exist_ok=True)
    for theme in ("dark", "paper"):
        banner(theme)
        for num, key, title in SECTIONS:
            section(theme, num, key, title)
        whoami(theme)
        stack(theme)
        for i, p in enumerate(PROJECTS, 1):
            card(theme, i, *p)
        button(theme, "linkedin", "LINKEDIN ↗", True)
        button(theme, "x", "X / TWITTER ↗", False)
        footer(theme)
    print("ok:", len(list(OUT.glob("*.svg"))), "svgs")


if __name__ == "__main__":
    main()
