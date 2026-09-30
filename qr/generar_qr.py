"""QR temático de la Encuesta Talleres Remedios con la línea gráfica Colmayor V7."""
import os
import pathlib

import qrcode
from PIL import Image, ImageDraw, ImageFont

URL = "https://encuesta-talleres-remedios.vercel.app"
ROOT = pathlib.Path(r"C:\Users\ASUS\OneDrive\Desktop\Remedios")
OUT = ROOT / "qr"
OUT.mkdir(exist_ok=True)
FONT = os.path.join(os.environ["TEMP"], "fonts", "Montserrat.ttf")

NAVY, TEAL, AQUA, DEEP = "#172139", "#108181", "#00AEAC", "#195855"
LIME, GOLD, CREAM = "#B4C42C", "#FBBB28", "#F7F4EA"


def font(size, weight="Bold"):
    f = ImageFont.truetype(FONT, size)
    f.set_variation_by_name(weight)
    return f


def qr_image(px=1200):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, border=0)
    qr.add_data(URL)
    qr.make(fit=True)
    m = qr.get_matrix()
    n = len(m)
    quiet = 4
    cell = px // (n + quiet * 2)
    size = cell * (n + quiet * 2)
    img = Image.new("RGBA", (size, size), "white")
    d = ImageDraw.Draw(img)
    off = quiet * cell

    finders = [(0, 0), (0, n - 7), (n - 7, 0)]
    def in_finder(r, c):
        return any(fr <= r < fr + 7 and fc <= c < fc + 7 for fr, fc in finders)

    # logo zone: leave the centre clear (H level tolerates it)
    logo_cells = int(n * 0.2) | 1
    lo = (n - logo_cells) // 2
    def in_logo(r, c):
        return lo - 1 <= r <= lo + logo_cells and lo - 1 <= c <= lo + logo_cells

    pad = cell * 0.03
    for r in range(n):
        for c in range(n):
            if not m[r][c] or in_finder(r, c) or in_logo(r, c):
                continue
            x, y = off + c * cell, off + r * cell
            d.rounded_rectangle([x + pad, y + pad, x + cell - pad, y + cell - pad], radius=cell * 0.3, fill=NAVY)

    for fr, fc in finders:
        x, y = off + fc * cell, off + fr * cell
        d.rounded_rectangle([x, y, x + 7 * cell, y + 7 * cell], radius=cell * 1.1, fill=TEAL)
        d.rounded_rectangle([x + cell, y + cell, x + 6 * cell, y + 6 * cell], radius=cell * 0.6, fill="white")
        d.rounded_rectangle([x + 2 * cell, y + 2 * cell, x + 5 * cell, y + 5 * cell], radius=cell * 0.4, fill=NAVY)

    # escudo on a white rounded badge with gold ring
    bx0 = off + (lo - 1) * cell + cell * 0.5
    bx1 = off + (lo + logo_cells + 1) * cell - cell * 0.5
    d.rounded_rectangle([bx0, bx0, bx1, bx1], radius=cell * 1.6, fill="white", outline=GOLD, width=max(3, cell // 3))
    esc = Image.open(ROOT / "marca" / "escudo.png").convert("RGBA")
    box = int((bx1 - bx0) * 0.72)
    esc.thumbnail((box, box), Image.LANCZOS)
    cx = int((bx0 + bx1) / 2)
    img.alpha_composite(esc, (cx - esc.width // 2, cx - esc.height // 2))
    return img.convert("RGB")


def centered(d, y, text, f, fill, width):
    w = d.textlength(text, font=f)
    d.text(((width - w) / 2, y), text, font=f, fill=fill)


def tarjeta(qr):
    W, H = 1240, 1754  # A5 a 150 ppp
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    head_h = 520
    d.rectangle([0, 0, W, head_h], fill=NAVY)
    d.ellipse([W - 420, -260, W + 260, 420], fill="#1B2A45")
    logo = Image.open(ROOT / "marca" / "logo-colmayor-horizontal.png").convert("RGBA")
    logo.thumbnail((420, 130), Image.LANCZOS)
    img.paste(logo, (80, 70), logo)

    d.rectangle([80, 262, 116, 268], fill=GOLD)
    d.text((132, 250), "TALLERES PARTICIPATIVOS", font=font(26, "Bold"), fill=AQUA)
    d.text((80, 300), "Encuesta de satisfacción", font=font(62, "ExtraBold"), fill="white")
    d.text((80, 374), "y atractivos del territorio", font=font(62, "ExtraBold"), fill="white")
    d.text((80, 458), "Plan Municipal de Turismo · Remedios, Antioquia", font=font(28, "Medium"), fill="#C9CFDB")

    stripe = [GOLD, TEAL, AQUA, LIME]
    for i, col in enumerate(stripe):
        d.rectangle([i * W // 4, head_h, (i + 1) * W // 4, head_h + 14], fill=col)

    card = 760
    cx0, cy0 = (W - card) // 2, head_h + 76
    shadow = Image.new("RGBA", (card + 40, card + 40), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([20, 28, card + 20, card + 28], radius=48, fill=(23, 33, 57, 40))
    img.paste(shadow, (cx0 - 20, cy0 - 20), shadow)
    d.rounded_rectangle([cx0, cy0, cx0 + card, cy0 + card], radius=48, fill="white", outline="#E4DFCF", width=2)
    q = qr.resize((card - 80, card - 80), Image.LANCZOS)
    img.paste(q, (cx0 + 40, cy0 + 40))

    y = cy0 + card + 52
    centered(d, y, "Escanee y responda", font(54, "ExtraBold"), NAVY, W)
    centered(d, y + 74, "Unos 8 minutos · Participación voluntaria y confidencial", font(28, "Medium"), DEEP, W)

    url = URL.replace("https://", "")
    f = font(28, "Bold")
    pw = d.textlength(url, font=f) + 64
    px0 = (W - pw) / 2
    d.rounded_rectangle([px0, y + 140, px0 + pw, y + 196], radius=28, fill=TEAL)
    centered(d, y + 151, url, f, "white", W)

    d.rectangle([0, H - 90, W, H], fill=NAVY)
    centered(d, H - 62, "Institución Universitaria Colegio Mayor de Antioquia · Datos protegidos · Ley 1581 de 2012",
             font(22, "SemiBold"), "#C9CFDB", W)
    return img


qr = qr_image()
qr.save(OUT / "qr-encuesta.png", dpi=(300, 300))
t = tarjeta(qr)
t.save(OUT / "tarjeta-qr-encuesta.png", dpi=(150, 150))
t.save(OUT / "tarjeta-qr-encuesta.pdf", resolution=150)
print("listo", qr.size, t.size)
