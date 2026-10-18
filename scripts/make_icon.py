"""Erzeugt ein App-Icon der Familie: der Blob (gleiche Formel wie der Blob in den Apps) mit einem weißen Zeichen.

Aufruf im Ordner der App:
  python3 <appo-familie>/scripts/make_icon.py <ausgabe.png> <akzent-hex> <partner-hex> <hintergrund-hex> <zeichen>

Zeichen: "haken" (Kaufo), "blatt" (Scanno), "stift" (Schreibo). Neue Apps bekommen hier ein neues Zeichen:
ein einziges, kräftiges Symbol, keine dünnen Linien (DESIGN.md, „Der Blob“).
Hintergrund hell: Creme FBF4E6; dunkel: die dunkle Fläche der Farbwelt mit den aufgehellten Farben, z. B.
  python3 make_icon.py AppIcon.png      2A3FD6 FF6B5B FBF4E6 stift
  python3 make_icon.py AppIcon-Dark.png 6B7CFF FF7F70 111324 stift
Alle Farbwelten auf einmal: scripts/make_icons.sh in der App (ruft dieses Skript je Farbwelt zweimal auf).
"""
import math
import sys

from PIL import Image, ImageDraw, ImageFilter

SIZE = 1024
SCALE = 4  # Supersampling für glatte Kanten


def blob_points(cx, cy, base, time=2.2, wobble=1.0, count=9):
    pts = []
    for i in range(count):
        a = i / count * 2 * math.pi
        off = wobble * (0.055 * math.sin(3 * a + time * 0.9)
                        + 0.035 * math.sin(5 * a - time * 1.3)
                        + 0.025 * math.sin(2 * a + time * 0.55))
        r = base * (1 + off)
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return pts


def catmull_rom(points, steps=40):
    n = len(points)
    out = []
    for i in range(n):
        p0, p1, p2, p3 = points[(i - 1) % n], points[i], points[(i + 1) % n], points[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        for s in range(steps):
            t = s / steps
            mt = 1 - t
            x = mt ** 3 * p1[0] + 3 * mt ** 2 * t * c1[0] + 3 * mt * t ** 2 * c2[0] + t ** 3 * p2[0]
            y = mt ** 3 * p1[1] + 3 * mt ** 2 * t * c1[1] + 3 * mt * t ** 2 * c2[1] + t ** 3 * p2[1]
            out.append((x, y))
    return out


def hex_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def rounded_path(points, radius, steps=12):
    """Geschlossenes Polygon mit abgerundeten Ecken (quadratische Bézierkurve an jeder Ecke)."""
    out = []
    n = len(points)
    for i in range(n):
        p0, p1, p2 = points[i - 1], points[i], points[(i + 1) % n]

        def toward(a, b, d):
            dx, dy = b[0] - a[0], b[1] - a[1]
            length = math.hypot(dx, dy) or 1
            d = min(d, length / 2)
            return (a[0] + dx / length * d, a[1] + dy / length * d)

        a, b = toward(p1, p0, radius), toward(p1, p2, radius)
        for k in range(steps + 1):
            t = k / steps
            out.append(((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * b[0],
                        (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * b[1]))
    return out


def round_line(draw, points, width, fill):
    """Linie mit runden Enden."""
    draw.line(points, fill=fill, width=int(width), joint="curve")
    for x, y in (points[0], points[-1]):
        draw.ellipse((x - width / 2, y - width / 2, x + width / 2, y + width / 2), fill=fill)


def draw_page(draw, s, fill, cut):
    """Gefülltes Blatt mit Eselsohr und drei Textzeilen (wie SF Symbol doc.text.fill).
    `cut` ist die Farbe für Eselsohr und Zeilen – die Blob-Farbe in der Mitte."""
    cx, cy = s * 0.5, s * 0.515
    w, h, ear = s * 0.27, s * 0.34, s * 0.1
    left, right, top, bottom = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    draw.polygon(rounded_path([(left, top), (right - ear, top), (right, top + ear), (right, bottom), (left, bottom)], s * 0.045), fill=fill)
    draw.polygon(rounded_path([(right - ear, top), (right - ear, top + ear), (right, top + ear)], s * 0.02), fill=cut)
    for index, length in enumerate((0.15, 0.15, 0.09)):
        y = cy + s * index * 0.06
        round_line(draw, [(left + s * 0.06, y), (left + s * 0.06 + s * length, y)], s * 0.03, cut)


def draw_pencil(draw, s, fill):
    """Schmaler Stift schräg von rechts oben nach links unten: Spitze, Schaft, Kappe.
    Breite etwa wie die Strichstärke von Kaufos Haken; die Lücken zwischen den Teilen zeigen den Blob."""
    length, width = s * 0.46, s * 0.10
    tip, gap, cap = s * 0.11, s * 0.03, s * 0.065
    axis = (1 / math.sqrt(2), -1 / math.sqrt(2))   # von der Spitze zur Kappe (nach rechts oben)
    normal = (1 / math.sqrt(2), 1 / math.sqrt(2))
    cx, cy = s * 0.5, s * 0.515
    ox, oy = cx - axis[0] * length / 2, cy - axis[1] * length / 2

    def point(u, v):
        return (ox + axis[0] * u + normal[0] * v, oy + axis[1] * u + normal[1] * v)

    half = width / 2
    # Spitze
    draw.polygon(rounded_path([point(0, 0), point(tip, -half), point(tip, half)], s * 0.012), fill=fill)
    # Schaft
    body_start, body_end = tip + gap, length - cap - gap
    draw.polygon(rounded_path([point(body_start, -half), point(body_end, -half), point(body_end, half), point(body_start, half)], s * 0.01), fill=fill)
    # Kappe
    draw.polygon(rounded_path([point(length - cap, -half), point(length, -half), point(length, half), point(length - cap, half)], s * 0.03), fill=fill)


def main():
    out = sys.argv[1]
    accent = hex_rgb(sys.argv[2] if len(sys.argv) > 2 else "D63862")
    partner = hex_rgb(sys.argv[3] if len(sys.argv) > 3 else "FF8A66")
    background = hex_rgb(sys.argv[4] if len(sys.argv) > 4 else "FBF4E6")
    glyph = sys.argv[5] if len(sys.argv) > 5 else "stift"

    s = SIZE * SCALE
    img = Image.new("RGB", (s, s), background)

    outline = catmull_rom(blob_points(s / 2, s / 2 + s * 0.01, s * 0.36))

    # Weicher Schatten
    shadow = Image.new("L", (s, s), 0)
    ImageDraw.Draw(shadow).polygon([(x, y + s * 0.025) for x, y in outline], fill=90)
    shadow = shadow.filter(ImageFilter.GaussianBlur(s * 0.03))
    shade_color = tuple(int(c * 0.75 + b * 0.25) for c, b in zip(accent, background))
    img.paste(Image.new("RGB", (s, s), shade_color), (0, 0), shadow)

    # Verlauf Akzent → Partner (oben links nach unten rechts)
    gradient = Image.new("RGB", (s, s))
    gpx = gradient.load()
    step = 8
    for y in range(0, s, step):
        for x in range(0, s, step):
            t = min(1, max(0, (x + y) / (2 * s) * 1.3 - 0.1))
            color = tuple(int(a + (p - a) * t) for a, p in zip(accent, partner))
            for dy in range(step):
                for dx in range(step):
                    if x + dx < s and y + dy < s:
                        gpx[x + dx, y + dy] = color
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).polygon(outline, fill=255)
    img.paste(gradient, (0, 0), mask)

    # Glanzlicht
    shine = Image.new("L", (s, s), 0)
    ImageDraw.Draw(shine).ellipse((s * 0.27, s * 0.22, s * 0.55, s * 0.42), fill=70)
    shine = shine.filter(ImageFilter.GaussianBlur(s * 0.05))
    shine = Image.composite(shine, Image.new("L", (s, s), 0), mask)
    img.paste(Image.new("RGB", (s, s), (255, 255, 255)), (0, 0), shine)

    draw = ImageDraw.Draw(img)
    white = (255, 255, 255)
    if glyph == "haken":
        width = int(s * 0.075)
        check = [(s * 0.375, s * 0.515), (s * 0.465, s * 0.605), (s * 0.635, s * 0.425)]
        draw.line(check, fill=white, width=width, joint="curve")
        for x, y in (check[0], check[-1]):
            draw.ellipse((x - width / 2, y - width / 2, x + width / 2, y + width / 2), fill=white)
    elif glyph == "blatt":
        draw_page(draw, s, white, img.getpixel((int(s * 0.5), int(s * 0.52))))
    else:
        draw_pencil(draw, s, white)

    img.resize((SIZE, SIZE), Image.LANCZOS).save(out)


if __name__ == "__main__":
    main()
