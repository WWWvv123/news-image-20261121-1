#!/usr/bin/env python3
"""Draw a classic newspaper front page poster for 21 November 2026.

No network access, no downloaded images or fonts. Everything is drawn
in code with the system DejaVu fonts. Deterministic: two runs produce
byte-identical PNG output.
"""

import hashlib
import os
import random

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 36

PAPER = (244, 234, 213)      # aged newsprint
PAPER_DARK = (232, 219, 190)
INK = (26, 22, 18)           # near-black ink
ACCENT = (139, 26, 26)       # restrained dark red
RULE = (60, 52, 44)
FAINT = (120, 108, 88)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF = "DejaVuSerif.ttf"
SERIF_B = "DejaVuSerif-Bold.ttf"
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"


def wrap(text, fnt, max_width, draw):
    """Greedy word wrap; returns a list of lines fitting max_width."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if draw.textlength(trial, font=fnt) <= max_width:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def draw_lines(draw, x, y, lines, fnt, fill, spacing):
    """Draw lines top-left at (x, y); return y just past the last line."""
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + spacing
    return y


def text_h(lines, fnt, spacing):
    return len(lines) * (fnt.size + spacing) - spacing


def center(draw, cx, y, text, fnt, fill):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return y + fnt.size


def rule(draw, x0, x1, y, width=2, fill=RULE):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def draw_story(draw, x, y, width, kicker, headline, body, h_font, b_font):
    """One column story: red kicker, bold headline, serif body.

    Returns the y just past the story (before the gap).
    """
    kf = font(SANS_B, 15)
    draw.text((x, y), kicker, font=kf, fill=ACCENT)
    y += 15 + 8
    hlines = wrap(headline, h_font, width, draw)
    y = draw_lines(draw, x, y, hlines, h_font, INK, 4)
    y += 6
    blines = wrap(body, b_font, width, draw)
    y = draw_lines(draw, x, y, blines, b_font, INK, 5)
    return y


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # --- aged newsprint: faint deterministic speckles and fibres ---
    rng = random.Random(20261121)
    for _ in range(900):
        x = rng.randint(0, W - 1)
        y = rng.randint(0, H - 1)
        shade = rng.choice([PAPER_DARK, (238, 228, 205), (226, 212, 182)])
        draw.point((x, y), fill=shade)
    for _ in range(60):
        x = rng.randint(0, W - 1)
        y = rng.randint(0, H - 1)
        ln = rng.randint(6, 26)
        draw.line([(x, y), (x + ln, y + rng.randint(-2, 2))],
                  fill=(236, 226, 202), width=1)

    # --- outer frame: double rule ---
    rule(draw, MARGIN, W - MARGIN, 22, 3)
    rule(draw, MARGIN, W - MARGIN, 28, 1)

    # --- masthead (auto-fit to the frame width) ---
    y = 46
    masthead = "THE WORLD IN ONE PICTURE"
    msize = 60
    mf = font(SERIF_B, msize)
    while draw.textlength(masthead, font=mf) > W - 2 * MARGIN and msize > 20:
        msize -= 1
        mf = font(SERIF_B, msize)
    center(draw, W // 2, y, masthead, mf, INK)
    y += msize + 12

    # --- dateline ---
    df = font(SANS, 21)
    center(draw, W // 2, y, "Saturday 21 November 2026", df, INK)
    y += 21 + 6
    sf = font(SANS, 14)
    center(draw, W // 2, y, "SIX STORIES  ·  ONE PAGE  ·  ALL THE NEWS THAT FITS",
           sf, FAINT)
    y += 14 + 14

    # --- thick rule under masthead ---
    rule(draw, MARGIN, W - MARGIN, y, 4)
    rule(draw, MARGIN, W - MARGIN, y + 7, 1)
    y += 22

    # --- lead story ---
    kf = font(SANS_B, 16)
    draw.text((MARGIN, y), "LEAD STORY", font=kf, fill=ACCENT)
    y += 16 + 10
    hf = font(SERIF_B, 46)
    lead_head = "MEXICO CAPTURES\n\u2018EL CHAPO ISIDRO\u2019"
    hlines = wrap(lead_head, hf, W - 2 * MARGIN, draw)
    y = draw_lines(draw, MARGIN, y, hlines, hf, INK, 6)
    y += 10
    bf = font(SERIF, 22)
    lead_body = (
        "Mexican forces captured Fausto Isidro Meza Flores, one of the "
        "FBI\u2019s 10 most wanted cartel bosses, in Guasave, Sinaloa, "
        "overnight \u2014 with help from US intelligence."
    )
    blines = wrap(lead_body, bf, W - 2 * MARGIN, draw)
    y = draw_lines(draw, MARGIN, y, blines, bf, INK, 7)
    y += 16

    # --- rule above the columns ---
    rule(draw, MARGIN, W - MARGIN, y, 3)
    y += 18
    columns_top = y

    # --- two ruled columns ---
    col_w = 458
    left_x = MARGIN
    right_x = W - MARGIN - col_w
    mid_x = W // 2
    h_font = font(SERIF_B, 25)
    b_font = font(SERIF, 19)

    ly = draw_story(
        draw, left_x, columns_top, col_w,
        "CLIMATE  ·  COP31",
        "Climate Talks Run Into Overtime",
        "COP31 talks in Antalya run into overtime on Saturday with no "
        "deal yet; fossil fuels are missing from the draft deal.",
        h_font, b_font)
    ly += 20
    rule(draw, left_x, left_x + col_w, ly, 1, fill=FAINT)
    ly += 16
    ly = draw_story(
        draw, left_x, ly, col_w,
        "MIDDLE EAST",
        "Trump Weighs New Strikes on Iran",
        "President Trump weighs new strikes on Iran as Israel presses "
        "for action, US and Israeli officials say.",
        h_font, b_font)
    ly += 20
    rule(draw, left_x, left_x + col_w, ly, 1, fill=FAINT)
    ly += 16
    ly = draw_story(
        draw, left_x, ly, col_w,
        "FRANCE",
        "Protests Draw Smaller Crowds",
        "Lower turnout at largely peaceful cost-of-living and student "
        "protests in France \u2014 82,500 people nationwide, 21,500 in "
        "Paris.",
        h_font, b_font)

    ry = draw_story(
        draw, right_x, columns_top, col_w,
        "UKRAINE",
        "Missiles Strike Zelenskyy\u2019s Hometown",
        "Russian ballistic missiles struck Kryvyi Rih on Friday night "
        "\u2014 2 killed, a 7-year-old boy and a 20-year-old woman, and "
        "60 wounded, including 6 children \u2014 in a double-tap attack. "
        "Russian missiles and a drone also crashed in Poland during the "
        "biggest November barrage: 404 drones, 111 missiles.",
        h_font, b_font)
    ry += 20
    rule(draw, right_x, right_x + col_w, ry, 1, fill=FAINT)
    ry += 16
    ry = draw_story(
        draw, right_x, ry, col_w,
        "MARKETS",
        "Markets Plunge as Nasdaq Wipes Out 2026 Gains",
        "The Nasdaq drops 5.28% on Friday, wiping out its 2026 gains "
        "\u2014 down 2.7% for the year. The S&P 500 falls 3.7% and the "
        "Dow 1.9%, both entering correction territory. Nvidia drops "
        "14%; Anthropic falls 8.5% on its second day of trading.",
        h_font, b_font)

    bottom = max(ly, ry)

    # --- vertical rule between columns ---
    draw.line([(mid_x, columns_top), (mid_x, bottom)], fill=RULE, width=1)

    # --- footer ---
    fy = bottom + 20
    rule(draw, MARGIN, W - MARGIN, fy, 3)
    rule(draw, MARGIN, W - MARGIN, fy + 6, 1)
    fy += 16
    ff = font(SANS, 14)
    center(draw, W // 2, fy, "Sources: Reuters  ·  Associated Press  ·  "
           "The New York Times  ·  CNN  ·  Morningstar", ff, FAINT)
    fy += 14 + 5
    center(draw, W // 2, fy, "All stories from 21 November 2026",
           font(SANS_B, 13), FAINT)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "entry.png")
    img.save(out, "PNG")
    with open(out, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    print("entry.png sha256: %s" % digest)
    print("entry.png size: %d bytes" % os.path.getsize(out))


if __name__ == "__main__":
    main()
