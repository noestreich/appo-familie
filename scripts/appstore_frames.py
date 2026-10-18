"""Gestaltet App-Store-Bilder: Überschrift oben, Bildschirmfoto mit runden Ecken, Blob im Hintergrund.

Aufruf im Ordner der App: python3 <appo-familie>/scripts/appstore_frames.py [--config docs/appstore/frames.json]
Liest Farben und Überschriften aus der Konfiguration der App und gestaltet, was in docs/appstore liegt:

  raw/             → framed/ (1320 × 2868, iPhone 6,9") und framed-6.3/ (1206 × 2622, iPhone 6,3")
  raw-duo/         → framed-duo/ (2853 × 2007 quer bzw. 2007 × 2853 hochkant, je nach Rohbild)
  raw-duo-aussen/  → framed-duo-aussen/ (1398 × 2034)

Bilder, deren Name auf „dunkel“ endet, bekommen den dunklen Hintergrund.

frames.json (Farben als Hex, Überschriften als [Titel, Untertitel] je Dateiname ohne .png):
  {
    "colors": {"background": "F3F4FC", "ink": "161828", "muted": "60647C",
               "accent": "2A3FD6", "partner": "FF6B5B", "dark": "111324"},
    "captions":           {"01-heute": ["Jeder Tag eine Seite", "Tippen, fotografieren oder diktieren."]},
    "duo_captions":       {"01-doppelseite": ["…", "…"]},
    "duo_outer_captions": {"01-aussen": ["…", "…"]}
  }
Fehlende Farben nimmt das Skript aus der Standard-Farbwelt (Ultramarin & Koralle).
"""
import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH, HEIGHT = 1320, 2868
# Zweite Größe für den 6,3-Zoll-Platz in App Store Connect (Seitenverhältnis fast gleich, wird nur verkleinert)
SMALL = (1206, 2622)
# iPhone Duo, inneres Display – eigenes Fach in App Store Connect, hoch- oder querformatig.
# Aufgeklappt liegt das Duo quer wie ein aufgeschlagenes Buch (2853 × 2007).
DUO = (2007, 2853)
# iPhone Duo, Außendisplay
DUO_OUTER = (1398, 2034)

COLORS = {
    "background": "F3F4FC",
    "ink": "161828",
    "muted": "60647C",
    "accent": "2A3FD6",
    "partner": "FF6B5B",
    "dark": "111324",
}


def rgb(hex_string):
    h = hex_string.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


FONT_CANDIDATES = {
    "bold": [
        "/System/Library/Fonts/SFNSRounded.ttf",
        "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "regular": [
        "/System/Library/Fonts/SFNS.ttf",
        "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
}


def font(kind, size):
    for path in FONT_CANDIDATES[kind]:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def blob_points(cx, cy, base, time=2.2, count=9):
    points = []
    for i in range(count):
        a = i / count * 2 * math.pi
        offset = (0.055 * math.sin(3 * a + time * 0.9) + 0.035 * math.sin(5 * a - time * 1.3)
                  + 0.025 * math.sin(2 * a + time * 0.55))
        r = base * (1 + offset)
        points.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    smooth = []
    n = len(points)
    for i in range(n):
        p0, p1, p2, p3 = points[(i - 1) % n], points[i], points[(i + 1) % n], points[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        for s in range(30):
            t = s / 30
            mt = 1 - t
            smooth.append((
                mt ** 3 * p1[0] + 3 * mt ** 2 * t * c1[0] + 3 * mt * t ** 2 * c2[0] + t ** 3 * p2[0],
                mt ** 3 * p1[1] + 3 * mt ** 2 * t * c1[1] + 3 * mt * t ** 2 * c2[1] + t ** 3 * p2[1],
            ))
    return smooth


def wrap(draw, text, fnt, max_width):
    words, lines, line = text.split(), [], ""
    for word in words:
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            line = trial
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines


def compose(raw_path, out_path, title, subtitle, colors, dark=False, size=(WIDTH, HEIGHT), corner=0.09):
    """`size` ist die Ausgabegröße; Schrift, Ränder und Blob wachsen mit ihrer Breite.
    `corner` ist der Eckenradius des Bildschirmfotos im Verhältnis zu seiner Breite."""
    WIDTH, HEIGHT = size
    # Hochkant wie bisher. Quer (Duo aufgeklappt) etwas kleinere Schrift und ein größeres Bild.
    landscape = WIDTH > HEIGHT
    k = HEIGHT / 1650 if landscape else WIDTH / 1320
    ACCENT, PARTNER = colors["accent"], colors["partner"]
    background = colors["dark"] if dark else colors["background"]
    title_color = (250, 244, 236) if dark else colors["ink"]
    subtitle_color = (190, 178, 168) if dark else colors["muted"]

    canvas = Image.new("RGB", (WIDTH, HEIGHT), background)

    # Blob im Hintergrund, rechts oben hinter dem Bildschirm
    blob = Image.new("L", (WIDTH, HEIGHT), 0)
    ImageDraw.Draw(blob).polygon(blob_points(WIDTH * 0.97, HEIGHT * 0.505, 470 * k), fill=255)
    blob = blob.filter(ImageFilter.GaussianBlur(2))
    gradient = Image.new("RGB", (WIDTH, HEIGHT))
    gp = gradient.load()
    for y in range(0, HEIGHT, 4):
        for x in range(0, WIDTH, 4):
            t = min(1, max(0, (x / WIDTH + y / HEIGHT) * 0.9 - 0.2))
            color = tuple(int(a + (b - a) * t) for a, b in zip(ACCENT, PARTNER))
            for dy in range(4):
                for dx in range(4):
                    if x + dx < WIDTH and y + dy < HEIGHT:
                        gp[x + dx, y + dy] = color
    canvas.paste(gradient, (0, 0), blob.point(lambda v: int(v * (0.85 if dark else 0.9))))

    draw = ImageDraw.Draw(canvas)
    title_font = font("bold", int(92 * k))
    subtitle_font = font("regular", int(50 * k))
    margin = int(90 * k)
    y = int(150 * k)
    for line in wrap(draw, title, title_font, WIDTH - 2 * margin):
        draw.text((margin, y), line, font=title_font, fill=title_color)
        y += int(108 * k)
    y += int(14 * k)
    for line in wrap(draw, subtitle, subtitle_font, WIDTH - 2 * margin):
        draw.text((margin, y), line, font=subtitle_font, fill=subtitle_color)
        y += int(64 * k)

    # Bildschirmfoto
    shot = Image.open(raw_path).convert("RGB")
    top = max(y + int(60 * k), int(560 * k)) if not landscape else y + int(50 * k)
    target_height = HEIGHT - top + int(120 * k)  # unten etwas angeschnitten wirkt wie ein Gerät, das ins Bild ragt
    max_width = WIDTH * 0.88 if landscape else 1060 * k
    scale = min(max_width / shot.width, target_height / shot.height)
    shot = shot.resize((int(shot.width * scale), int(shot.height * scale)), Image.LANCZOS)
    x = (WIDTH - shot.width) // 2
    radius = int(shot.width * corner)
    mask = Image.new("L", shot.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, shot.width, shot.height), radius=radius, fill=255)

    shadow = Image.new("L", (WIDTH, HEIGHT), 0)
    ImageDraw.Draw(shadow).rounded_rectangle((x, top + 24, x + shot.width, top + 24 + shot.height), radius=radius, fill=110)
    shadow = shadow.filter(ImageFilter.GaussianBlur(40 * k))
    canvas.paste((0, 0, 0), (0, 0), shadow)

    frame = Image.new("L", (WIDTH, HEIGHT), 0)
    rim = int(14 * k)
    ImageDraw.Draw(frame).rounded_rectangle((x - rim, top - rim, x + shot.width + rim, top + shot.height + rim), radius=radius + rim, fill=255)
    canvas.paste((20, 20, 22), (0, 0), frame)
    canvas.paste(shot, (x, top), mask)

    canvas.save(out_path, optimize=True)


def frame_folder(raw, out, captions, colors, size_for, corner, label, small=None):
    if not raw.exists():
        return
    out.mkdir(parents=True, exist_ok=True)
    if small:
        small.mkdir(parents=True, exist_ok=True)
    for path in sorted(raw.glob("*.png")):
        title, subtitle = captions.get(path.stem, (path.stem, ""))
        if path.stem not in captions:
            print(f"! {label}{path.name}: keine Überschrift in der Konfiguration")
        size = size_for(Image.open(path))
        compose(path, out / path.name, title, subtitle, colors,
                dark=path.stem.endswith("dunkel"), size=size, corner=corner)
        if small:
            Image.open(out / path.name).resize(SMALL, Image.LANCZOS).save(small / path.name, optimize=True)
        print(f"✓ {label}{path.name}")


def main():
    parser = argparse.ArgumentParser(description="App-Store-Bilder der App-Familie gestalten")
    parser.add_argument("--config", default="docs/appstore/frames.json")
    parser.add_argument("--root", default="docs/appstore", help="Ordner mit raw/, raw-duo/, raw-duo-aussen/")
    args = parser.parse_args()

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    colors = {key: rgb(value) for key, value in {**COLORS, **config.get("colors", {})}.items()}
    root = Path(args.root)

    frame_folder(root / "raw", root / "framed", config.get("captions", {}), colors,
                 lambda shot: (WIDTH, HEIGHT), 0.09, "", small=root / "framed-6.3")
    frame_folder(root / "raw-duo", root / "framed-duo", config.get("duo_captions", {}), colors,
                 lambda shot: DUO if shot.height >= shot.width else (DUO[1], DUO[0]), 0.035, "Duo ")
    frame_folder(root / "raw-duo-aussen", root / "framed-duo-aussen", config.get("duo_outer_captions", {}), colors,
                 lambda shot: DUO_OUTER, 0.09, "Duo außen ")


if __name__ == "__main__":
    main()
