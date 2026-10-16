"""Painel de telemetria (stats do GitHub) no estilo GLITCH.

Roda no workflow com GITHUB_TOKEN e grava telemetry-dark.svg e
telemetry-paper.svg em --out. Sem token ou com a API fora do ar, desenha o
estado vazio { NO SIGNAL } em vez de falhar.

    GITHUB_TOKEN=... python scripts/telemetry.py --user dopa-do-terere --out dist
"""

import argparse
import json
import os
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from glitch import Svg

W = 840
QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    contributionsCollection { contributionCalendar { totalContributions } }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}
"""


def fetch(user, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": user}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        u = json.load(r)["data"]["user"]
    langs = Counter()
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            langs[e["node"]["name"]] += e["size"]
    total = sum(langs.values()) or 1
    return {
        "repos": u["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        "followers": u["followers"]["totalCount"],
        "contrib": u["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        "langs": [(n, v / total) for n, v in langs.most_common(6)],
    }


def render(theme, data, now):
    mes = "JAN FEV MAR ABR MAI JUN JUL AGO SET OUT NOV DEZ".split()[now.month - 1]
    stamp = now.strftime(f"%d {mes} %Y · %H:%M UTC")
    if not data:
        H = 200
        s = Svg(W, H, theme, "Telemetria: sem sinal")
        s.rect(.5, .5, W - 1, H - 1, "bg-surface", "border")
        s.label(16, 22, "SYS // TELEMETRIA")
        s.label(W - 16, 22, stamp, anchor="end")
        s.line(0, 34.5, W, 34.5, "border")
        s.text(W / 2, 120, "{ NO SIGNAL }", "pixel", 40, fill="text", anchor="middle")
        s.label(W / 2, 156, "× API INDISPONÍVEL · NOVA LEITURA EM 24H", size=10, anchor="middle")
        return s

    rows = data["langs"]
    H = 36 + 112 + 40 + len(rows) * 28 + 16
    s = Svg(W, H, theme, "Telemetria: {repos} repositórios públicos, {stars} estrelas, "
            "{followers} seguidores, {contrib} contribuições no último ano".format(**data))
    s.rect(.5, .5, W - 1, H - 1, "bg-surface", "border")
    s.label(16, 22, "SYS // TELEMETRIA")
    s.label(W - 16, 22, stamp, anchor="end")
    s.line(0, 34.5, W, 34.5, "border")

    cells = [("REPOS PÚBLICOS", data["repos"]), ("ESTRELAS", data["stars"]),
             ("SEGUIDORES", data["followers"]), ("CONTRIBUIÇÕES / 12M", data["contrib"])]
    cw = W / len(cells)
    for i, (k, v) in enumerate(cells):
        x = i * cw
        if i:
            s.line(x + .5, 35, x + .5, 148, "border")
        s.label(x + 16, 62, k, size=10)
        s.text(x + 16, 124, f"{v:,}".replace(",", "."), "sans", 40, 400, "text", ls=-0.02,
               tnum=True)
    s.line(0, 148.5, W, 148.5, "border")

    y = 176
    s.label(16, y, f"LINGUAGENS // TOP {len(rows)}", size=10)
    s.label(W - 16, y, "POR BYTES", size=10, anchor="end")
    y += 20
    cols, x0 = 92, 184
    for i, (name, pct) in enumerate(rows):
        filled = max(1, round(pct * cols))
        s.text(16, y + 11, name, "mono", 12, 400, "text")
        # a linguagem do topo é o sinal; o resto é matriz neutra
        on = "signal" if i == 0 else "matrix-on"
        s.matrix(x0, y, cols, 2, lambda c, r, f=filled, on=on: on if c < f else None)
        s.text(W - 16, y + 11, f"{pct * 100:.1f}%", "mono", 12, 400, "text-muted",
               anchor="end", tnum=True)
        y += 28
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default="dopa-do-terere")
    ap.add_argument("--out", default="dist")
    ap.add_argument("--sample", action="store_true", help="dados de exemplo, sem rede")
    a = ap.parse_args()

    data = None
    if a.sample:
        data = {"repos": 18, "stars": 42, "followers": 27, "contrib": 1284,
                "langs": [("TypeScript", .38), ("JavaScript", .21), ("PHP", .16),
                          ("Python", .12), ("Blade", .08), ("CSS", .05)]}
    elif os.environ.get("GITHUB_TOKEN"):
        try:
            data = fetch(a.user, os.environ["GITHUB_TOKEN"])
        except Exception as e:  # sem sinal: desenha o estado vazio
            print("telemetry: fetch falhou:", e)

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    for theme in ("dark", "paper"):
        (out / f"telemetry-{theme}.svg").write_text(render(theme, data, now).render(),
                                                    encoding="utf-8")
    print("telemetry:", "ok" if data else "no signal")


if __name__ == "__main__":
    main()
