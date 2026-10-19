"""Erzeugt die Webseite einer App der Familie: eine einzige HTML-Datei mit eingebetteten Bildern.

Aufruf im Ordner der App: python3 <appo-familie>/website/make_website.py [--config docs/website/site.json]
Liest den Inhalt aus der Konfiguration der App, Aufbau und Gestaltung aus vorlage.html und stil.css hier daneben,
verkleinert die Bilder auf JPEG mit 660 Pixel Breite, bettet sie per base64 ein und schreibt docs/website/index.html.

Die Abschnitte stehen bei allen Apps in derselben Reihenfolge: Kopf, Funktionen (mit Bildleiste), iPhone Duo,
Hilfe, Datenschutz, Impressum (DESIGN.md, „Webseite“). Gemeinsames (Impressum, Kontakt, Verantwortlicher,
„Weitere Apps von uns“, „Diese Webseite“) steht in der Vorlage, nicht in der App.

site.json (Bildpfade relativ zum Ordner der App, Texte mit HTML wie <strong> und <a> sind erlaubt):
  {
    "name": "Kaufo", "titel": "…", "beschreibung": "…", "app_store": "https://apps.apple.com/…",
    "zeichen": "haken" | "blatt" | "stift",
    "farben": {"hell": {"surface", "card", "ink", "muted", "accent", "partner"}, "dunkel": {…}},
    "einleitung": "<strong>…</strong> …", "hinweis": "…",
    "kopfbild": {"bild": "docs/appstore/raw/05-liste.png", "alt": "…"},
    "funktionen": {"titel": "…", "karten": [{"symbol": "kamera", "titel": "…", "text": "…"}]},
    "bilder": [{"bild": "…", "alt": "…"}],
    "duo": {"titel": "…", "text": "…",
            "innen": {"bild": "…", "bild_dunkel": "…", "alt": "…", "unterschrift": "…"},
            "aussen": {"bild": "…", "alt": "…", "unterschrift": "…"}},
    "hilfe": [{"frage": "…", "antwort": "…"}],
    "datenschutz": {"kurz": "…", "abschnitte": [{"titel": "…", "html": "<p>…</p>"}], "rechte": "…", "stand": "Oktober 2026"},
    "marken": "Apple, iPhone, iCloud und App Store"
  }
Symbole der Funktionskarten: symbole.json. Fehlt der Abschnitt „duo“, fällt er weg.
"""
import argparse
import base64
import html
import io
import json
import urllib.parse
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
WIDTH = 660
QUALITY = 80

# Der Blob als SVG-Pfad (gleiche Form auf allen Seiten, viewBox 0 0 100 100)
BLOB = ("M96.8,50.0 C96.8,59.3 89.9,71.1 83.3,78.0 C76.7,84.8 66.7,88.9 57.2,91.0 C47.8,93.1 34.2,95.1 26.6,90.6 "
        "C18.9,86.1 14.7,73.4 11.4,64.0 C8.1,54.6 4.0,43.1 6.6,34.2 C9.3,25.4 19.1,15.2 27.5,11.1 C35.9,6.9 47.9,7.2 "
        "57.2,9.1 C66.5,10.9 76.7,15.3 83.3,22.1 C89.9,28.9 96.8,40.7 96.8,50.0 Z")

# Das weiße Zeichen im Blob, wie im App-Icon (scripts/make_icon.py). {g} ist der Verlauf des Blobs.
GLYPHS = {
    "haken": '<path d="M32 52 L45 64 L69 38" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>',
    "blatt": ('<path fill="#fff" d="M40,32 H53 L64,43 V65 Q64,70 59,70 H40 Q35,70 35,65 V37 Q35,32 40,32 Z"/>\n'
              '        <path fill="url(#{g})" d="M53,32 V40 Q53,43 56,43 H64 Z"/>\n'
              '        <g fill="url(#{g})">\n'
              '          <rect x="41" y="49" width="16" height="3.4" rx="1.7"/>\n'
              '          <rect x="41" y="55" width="16" height="3.4" rx="1.7"/>\n'
              '          <rect x="41" y="61" width="10" height="3.4" rx="1.7"/>\n'
              '        </g>'),
    "stift": ('<g fill="#fff" stroke="#fff" stroke-width="1.2" stroke-linejoin="round">\n'
              '          <path d="M33.7,67.8 L38.0,56.4 L45.1,63.5 Z"/>\n'
              '          <path d="M40.1,54.3 L56.0,38.4 L63.1,45.5 L47.2,61.4 Z"/>\n'
              '          <path d="M58.1,36.3 L62.7,31.7 L69.8,38.8 L65.2,43.4 Z"/>\n'
              '        </g>'),
}


def rgb(hex_string):
    h = hex_string.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def colors(palette, line_alpha):
    """Farben einer Farbwelt plus Trennlinie (Tinte mit wenig Deckkraft)."""
    out = {key: "#" + value.lstrip("#").upper() for key, value in palette.items()}
    r, g, b = rgb(palette["ink"])
    out["line"] = f"rgba({r},{g},{b},{line_alpha})"
    return out


def embed(root, path):
    """Bild auf 660 Pixel Breite verkleinern (nie vergrößern), als JPEG einbetten. Liefert (data-URI, Breite, Höhe)."""
    image = Image.open(root / path).convert("RGB")
    if image.width > WIDTH:
        image = image.resize((WIDTH, round(image.height * WIDTH / image.width)), Image.LANCZOS)
    buffer = io.BytesIO()
    image.save(buffer, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    data = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{data}", image.width, image.height


def img(root, entry, indent, lazy=True):
    src, w, h = embed(root, entry["bild"])
    loading = ' loading="lazy"' if lazy else ""
    return f'{indent}<img src="{src}" alt="{html.escape(entry["alt"])}" width="{w}" height="{h}"{loading}>'


def favicon(glyph, light):
    svg = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>"
           f"<stop offset='0' stop-color='{light['accent']}'/><stop offset='1' stop-color='{light['partner']}'/>"
           f"</linearGradient></defs><path fill='url(#g)' d='{BLOB}'/>"
           + " ".join(line.strip() for line in GLYPHS[glyph].format(g="g").splitlines()).replace('"', "'") + "</svg>")
    return "data:image/svg+xml," + urllib.parse.quote(svg, safe=" ='/:,.-()#")


def features(config, symbols):
    cards = []
    for card in config["funktionen"]["karten"]:
        cards.append(f'      <div class="card"><div class="icon"><svg viewBox="0 0 24 24">{symbols[card["symbol"]]}</svg></div>\n'
                     f'        <h3>{card["titel"]}</h3><p>{card["text"]}</p></div>')
    return "\n".join(cards)


def duo_section(root, duo):
    if not duo:
        return ""
    inner, outer = duo["innen"], duo.get("aussen")
    dark = ""
    if inner.get("bild_dunkel"):
        src, _, _ = embed(root, inner["bild_dunkel"])
        dark = f'          <source srcset="{src}" media="(prefers-color-scheme: dark)">\n'
    parts = [
        "",
        '  <section id="duo" aria-labelledby="duo-titel">',
        f'    <h2 id="duo-titel">{duo["titel"]}</h2>',
        '    <div class="duo">',
        f'      <p class="duo-text">{duo["text"]}</p>',
        '      <figure class="duo-inner">',
        "        <picture>",
        dark + img(root, inner, "          "),
        "        </picture>",
        f'        <figcaption>{inner["unterschrift"]}</figcaption>',
        "      </figure>",
    ]
    if outer:
        parts += [
            '      <figure class="duo-outer">',
            img(root, outer, "        "),
            f'        <figcaption>{outer["unterschrift"]}</figcaption>',
            "      </figure>",
        ]
    parts += ["    </div>", "  </section>", ""]
    return "\n".join(parts)


def help_items(config):
    out = []
    for item in config["hilfe"]:
        out.append(f'      <h3>{item["frage"]}</h3>\n      <p>{item["antwort"]}</p>')
    return "\n".join(out)


def privacy(config):
    """Nummerierte Abschnitte: Verantwortlicher, die der App, „Weitere Apps“, „Diese Webseite“, Rechte."""
    name = config["name"]
    privacy_config = config["datenschutz"]
    sections = [("Verantwortlicher", '<p>aketo GmbH, Baenschstr. 67, 10247 Berlin, Deutschland<br>\n'
                                     '      E-Mail: <a href="mailto:info@aketo.de">info@aketo.de</a></p>')]
    sections += [(s["titel"], s["html"]) for s in privacy_config["abschnitte"]]
    sections += [
        ("„Weitere Apps von uns“",
         f"<p>In den Einstellungen zeigt {name} unsere anderen Apps. Die Angaben und Bilder werden über Apples öffentliche "
         "App-Store-Schnittstelle (itunes.apple.com, apps.apple.com) geladen. Dabei erhält Apple deine IP-Adresse. "
         "Wir erhalten keine Daten.</p>"),
        ("Diese Webseite",
         "<p>Diese Seite verwendet keine Cookies, keine Analyse-Werkzeuge und lädt keine Inhalte von Dritten "
         "(alle Bilder und Schriften sind eingebettet bzw. stammen von deinem Gerät).</p>"),
        ("Deine Rechte", f'<p>{privacy_config["rechte"]}</p>'),
    ]
    return "\n\n".join(f"      <h3>{number}. {title}</h3>\n      {body}" for number, (title, body) in enumerate(sections, 1))


def fill(template, values):
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    if "{{" in template:
        raise SystemExit("Nicht ersetzt: " + template[template.index("{{"):template.index("{{") + 40])
    return template


def main():
    parser = argparse.ArgumentParser(description="Webseite einer App der Familie erzeugen")
    parser.add_argument("--config", default="docs/website/site.json")
    parser.add_argument("--root", default=".", help="Ordner der App; Bildpfade beziehen sich darauf")
    parser.add_argument("--out", default="docs/website/index.html")
    args = parser.parse_args()

    root = Path(args.root)
    config = json.loads((root / args.config).read_text(encoding="utf-8"))
    symbols = json.loads((HERE / "symbole.json").read_text(encoding="utf-8"))
    light = colors(config["farben"]["hell"], ".1")
    dark = colors(config["farben"]["dunkel"], ".12")
    r, g, b = rgb(light["accent"])

    values = {"hell." + k: v for k, v in light.items()}
    values.update({"dunkel." + k: v for k, v in dark.items()})
    values["logo_schatten"] = f"rgba({r},{g},{b},.3)"
    style = fill((HERE / "stil.css").read_text(encoding="utf-8"), values)

    values.update({
        "stil": style,
        "titel": html.escape(config["titel"]),
        "beschreibung": html.escape(config["beschreibung"]),
        "favicon": favicon(config["zeichen"], light),
        "name": config["name"],
        "blob": BLOB,
        "zeichen": GLYPHS[config["zeichen"]].format(g="blob"),
        "einleitung": config["einleitung"],
        "app_store": config["app_store"],
        "hinweis": config["hinweis"],
        "kopfbild": img(root, config["kopfbild"], "", lazy=False),
        "funktionen_titel": config["funktionen"]["titel"],
        "funktionen": features(config, symbols),
        "bilder": "\n".join(img(root, entry, "        ") for entry in config["bilder"]),
        "duo": duo_section(root, config.get("duo")),
        "hilfe": help_items(config),
        "datenschutz_kurz": config["datenschutz"]["kurz"],
        "datenschutz": privacy(config),
        "datenschutz_stand": config["datenschutz"]["stand"],
        "marken": config["marken"],
    })
    page = fill((HERE / "vorlage.html").read_text(encoding="utf-8"), values)
    out = root / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"✓ {out} ({len(page) // 1024} KB)")


if __name__ == "__main__":
    main()
