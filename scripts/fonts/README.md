# Fontes

Os SVGs de `assets/` embutem um subset destas fontes (só os glifos usados),
porque um `<img>` no GitHub não carrega fontes externas. Todas sob a
[SIL Open Font License 1.1](https://openfontlicense.org).

| Arquivo | Fonte | Papel no GLITCH |
| --- | --- | --- |
| `silkscreen-400.woff2` | [Silkscreen](https://github.com/googlefonts/silkscreen), Jason Kottke | Pixel / display |
| `jetbrains-mono-*.woff2` | [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono) v2.304, JetBrains | Mono / sistema |
| `geist-*.woff2` | [Geist](https://github.com/vercel/geist-font), Vercel | Grotesk editorial |

Para regerar os SVGs:

```sh
pip install fonttools brotli
python scripts/build.py
```
