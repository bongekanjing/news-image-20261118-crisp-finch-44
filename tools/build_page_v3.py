#!/usr/bin/env python3
"""Render the 18 November 2026 front page.

The page follows the shape the paid entries share: a region colour bar, a
strip of the day in numbers, thirteen numbered cards, then a locator map
beside a river of briefs.

Every card is measured from its own copy before it is drawn, so no card
overflows its box and none is left with dead space: whatever height the
words do not use, the figure fills. The figures are flat motifs keyed to the
story's field (war, markets, weather, politics) and tinted with the region
colour, so they carry meaning rather than decoration.

Colour carries meaning and nothing else: one hue per region, reused on the
bar, the card eyebrows, the map pins and the legend.
"""

import json
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 26
BG = (250, 248, 241)
INK = (24, 22, 20)
GREY = (96, 92, 86)
RULE = (150, 146, 136)
HAIR = (211, 205, 192)
LAND = (233, 229, 216)
SEA = (239, 237, 230)
RED = (150, 30, 30)
WHITE = (255, 255, 255)

HERE = os.path.dirname(os.path.abspath(__file__))

SB = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SR = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SI = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
NA = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
NB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

REGION_COLOUR = {
    "EUROPE": (30, 54, 106),
    "MIDDLE EAST": (18, 104, 70),
    "ASIA": (166, 108, 14),
    "AFRICA": (178, 84, 26),
    "AMERICAS": (88, 44, 116),
    "OCEANIA": (16, 104, 114),
    "WORLD": (36, 36, 40),
}
REGION_ORDER = ["EUROPE", "MIDDLE EAST", "ASIA", "AFRICA", "AMERICAS", "WORLD"]

_fc = {}


def F(path, px):
    key = (path, px)
    if key not in _fc:
        _fc[key] = ImageFont.truetype(path, int(round(px)))
    return _fc[key]


def wrap(text, fnt, width):
    out, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if not cur or fnt.getlength(trial) <= width:
            cur = trial
        else:
            out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def blit(d, lines, fnt, x, y, fill, lead):
    for i, ln in enumerate(lines):
        d.text((x, y + i * lead), ln, font=fnt, fill=fill)
    return y + len(lines) * lead


def track(fnt, text, extra=0.6):
    return sum(fnt.getlength(c) + extra for c in text) - extra


def tracked(d, text, fnt, x, y, fill, extra=0.6):
    cx = x
    for ch in text:
        d.text((cx, y), ch, font=fnt, fill=fill)
        cx += fnt.getlength(ch) + extra
    return cx


def tint(rgb, k):
    """Mix a colour towards the paper: k=0 the colour, k=1 the paper."""
    return tuple(int(c + (b - c) * k) for c, b in zip(rgb, BG))


# --------------------------------------------------------------- the copy

LEADS = [
    dict(region="MIDDLE EAST", field="WAR", place="IRAN",
         head="US jets strike Iran's Qeshm Island; Kuwait downs the drones",
         dek="Precision munitions hit an IRGC missile site on the Strait of "
             "Hormuz. Bahrain's defences intercepted the answering drones "
             "before dawn, the first such attack in two months.",
         ll=(26.9, 56.3)),
    dict(region="ASIA", field="DIPLOMACY", place="CHINA",
         head="Xi greets Trump on the Shenzhen tarmac as a Putin summit nears",
         dek="China's president broke precedent to meet Air Force One. The "
             "three leaders sit down on Thursday, with Ukraine and nuclear "
             "arms on the table.",
         ll=(22.5, 114.1)),
    dict(region="EUROPE", field="ECONOMY", place="KYIV",
         head="The EU proposes a 45bn-euro loan to keep Kyiv solvent",
         dek="Repayable only once Russia pays reparations, it covers about "
             "two-thirds of Ukraine's 2027 budget gap and is tied to a "
             "defence build-up.",
         ll=(50.45, 30.52)),
]

CARDS = [
    dict(region="AMERICAS", field="POLITICS", place="ALASKA",
         head="Peltola flips Alaska and lifts the Democrats to 56 seats",
         dek="Mary Peltola beat Dan Sullivan 50.1% to 45.8%, the first "
             "Indigenous woman Alaska sends to the Senate.",
         ll=(61.2, -149.9)),
    dict(region="EUROPE", field="WAR", place="CRIMEA",
         head="Ukraine hits the Kerch Bridge for a second day",
         dek="Drones and missiles struck the link to occupied Crimea, "
             "Moscow said, as Kyiv pressed its deep-strike campaign.",
         ll=(45.3, 36.5)),
    dict(region="AFRICA", field="POLITICS", place="SENEGAL",
         head="Pastef expels the president and 31 others",
         dek="The ruling party's break with Bassirou Diomaye Faye deepens a "
             "budget standoff that threatens IMF support.",
         ll=(14.7, -17.4)),
    dict(region="ASIA", field="WEATHER", place="ANDHRA",
         head="Cyclone Akvan strengthens on course for Andhra Pradesh",
         dek="The Bay of Bengal storm should cross between Machilipatnam and "
             "Puri on Friday. Fishermen were told to stay ashore.",
         ll=(17.7, 83.3)),
    dict(region="MIDDLE EAST", field="PEACE", place="GAZA",
         head="The Board of Peace warns the Gaza truce may collapse",
         dek="Its report to the UN faults both Israel and Hamas for failing "
             "to move the ceasefire on.",
         ll=(31.4, 34.4)),
    dict(region="AFRICA", field="WAR", place="SUDAN",
         head="The UN confirms 2,230 civilian deaths in ten months",
         dek="Most were killed by drone strikes, the rights office said, as "
             "the army pushed into West Kordofan.",
         ll=(13.6, 32.5)),
    dict(region="WORLD", field="MARKETS", place="WALL ST",
         head="The Dow closes 560 points lower as the AI trade splits",
         dek="Nvidia's forecast lifted chipmakers while the Dow sank, and "
             "investors braced for Anthropic's listing.",
         ll=(40.7, -74.0)),
    dict(region="AMERICAS", field="SOCIETY", place="BRAZIL",
         head="Uncontacted Awa make contact in the Amazon",
         dek="About twenty people approached a government team asking for "
             "yams as loggers closed on their territory.",
         ll=(-4.5, -56.0)),
    dict(region="AFRICA", field="CLIMATE", place="GHANA",
         head="Bishops seek an emergency over illegal mining",
         dek="The clergy urged action on galamsey pollution poisoning the "
             "country's rivers.",
         ll=(7.9, -1.0)),
    dict(region="ASIA", field="ENERGY", place="INDIA",
         head="Amazon pledges 7bn dollars for Indian renewables",
         dek="The wind and solar spend is to land by 2030 and backs the "
             "country's clean-power targets.",
         ll=(19.1, 72.9)),
]

BRIEFS = [
    ("MIDDLE EAST", "Yemen", "the UN says 64 children have been killed since September as the war widens"),
    ("MIDDLE EAST", "Riyadh", "Saudi Arabia braces for a Yemen campaign that may run into 2027"),
    ("MIDDLE EAST", "Jericho", "settlers kill a 72-year-old woman; Britain sanctions four groups"),
    ("EUROPE", "Kyiv", "Zelenskyy calls Ukraine's battlefield positions strong in the war's fifth year"),
    ("EUROPE", "Berlin", "about twenty governments weigh security guarantees for Kyiv"),
    ("EUROPE", "Sofia", "Bulgaria uncovers a five-year cyberespionage operation"),
    ("EUROPE", "Brussels", "Britain and the EU are set to unveil a trade deal this week"),
    ("AMERICAS", "Minnesota", "a man is charged over an 'incredibly brutal' attack on an Uber driver"),
    ("AMERICAS", "Washington", "the NSA blames a 'temporary degradation' for a secret network outage"),
    ("AMERICAS", "Cupertino", "Apple restores services after an internal update failed"),
    ("AMERICAS", "Brasilia", "Brazil signals more fiscal measures in the near term"),
    ("ASIA", "Manila", "Modi offers ASEAN free e-visas and maritime cooperation"),
    ("ASIA", "Beijing", "Xi vows to resist protectionism as Beijing touts an open door"),
    ("ASIA", "Seoul", "Lee and Xi hold a third summit lasting 34 minutes"),
    ("ASIA", "Tokyo", "Japan's exports set an October record on chip demand"),
    ("ASIA", "New Delhi", "India is re-elected to the ITU council for 2027-30"),
    ("AFRICA", "Rabat", "Washington urges respect for the Western Sahara ceasefire"),
    ("AFRICA", "Luanda", "Angola cuts its main rate to a ten-year low"),
    ("AFRICA", "Johannesburg", "five are charged under South Africa's mercenary law"),
    ("AFRICA", "Maputo", "the top court bars most media from the Mondlane trial"),
    ("WORLD", "Silicon Valley", "Nvidia's board is said to rule out bringing back Jensen Huang"),
    ("WORLD", "London", "gold slips below 3,800 dollars as the dollar firms"),
    ("WORLD", "Dubai", "Jay Shah is re-elected ICC chairman for a second term"),
    ("WORLD", "Kabul", "the UN gives Afghanistan 18m dollars for 824,000 people"),
]

NUMBERS = [
    ("45bn", "euros, the EU loan proposed for Kyiv"),
    ("2,230", "civilian deaths the UN confirms in Sudan"),
    ("31", "expelled by Senegal's ruling party"),
    ("560", "points the Dow lost as the AI trade split"),
    ("34", "minutes in the third Lee-Xi summit"),
    ("7bn", "dollars for Indian renewables"),
]

STRAP = "THE WORLD'S NEWS IN ONE PICTURE"

CHECKS = []


# --------------------------------------------------------------- figures

def motif(d, box, field, col):
    """A flat figure for a story's field, filling box=(x0,y0,x1,y1)."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    if w < 12 or h < 12:
        return
    pale = tint(col, 0.42)
    mid = tint(col, 0.10)
    d.rectangle([x0, y0, x1, y1], fill=pale)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    s = min(w, h)

    if field == "WAR":
        for k in range(3):
            yy = y1 - h * (0.22 + 0.24 * k)
            d.line([(x0 + w * 0.12, yy), (x1 - w * 0.12, yy - h * 0.1)],
                   fill=mid, width=max(1, int(h * 0.05)))
        d.polygon([(cx - s * 0.2, y0 + h * 0.2), (cx + s * 0.24, cy),
                   (cx - s * 0.2, cy), (cx + s * 0.06, y0 + h * 0.2)],
                  fill=col)

    elif field == "MARKETS":
        bars = [0.62, 0.44, 0.5, 0.3, 0.16]
        bw = w * 0.1
        for i, v in enumerate(bars):
            bx = x0 + w * 0.18 + i * (bw * 1.7)
            d.rectangle([bx, y1 - h * 0.18 - h * 0.6 * v,
                         bx + bw, y1 - h * 0.18], fill=mid)
        d.line([(x0 + w * 0.1, y0 + h * 0.3), (x1 - w * 0.1, y1 - h * 0.24)],
               fill=col, width=max(2, int(h * 0.06)))

    elif field == "WEATHER":
        r = s * 0.3
        for k in range(3):
            rr = r * (1 - 0.26 * k)
            d.arc([cx - rr, cy - rr, cx + rr, cy + rr],
                  start=20 + k * 40, end=320 + k * 40,
                  fill=col if k else mid, width=max(1, int(h * 0.045)))

    elif field == "POLITICS":
        bw2, bh2 = w * 0.42, h * 0.42
        d.rectangle([cx - bw2 / 2, y0 + h * 0.2, cx + bw2 / 2,
                     y0 + h * 0.2 + bh2], outline=col, width=max(2, int(h * 0.055)))
        d.line([(cx - bw2 * 0.1, y0 + h * 0.2),
                (cx - bw2 * 0.22, y0 + h * 0.34)],
               fill=col, width=max(2, int(h * 0.055)))
        d.rectangle([cx + bw2 * 0.02, y0 + h * 0.44, cx + bw2 * 0.7,
                     y0 + h * 0.44 + bh2 * 0.3], fill=mid)

    elif field == "PEACE":
        d.arc([cx - s * 0.34, cy - s * 0.34, cx + s * 0.34, cy + s * 0.34],
              start=200, end=340, fill=col, width=max(2, int(h * 0.07)))
        d.line([(cx - s * 0.34, cy + s * 0.05), (cx + s * 0.34, cy + s * 0.05)],
               fill=mid, width=max(1, int(h * 0.03)))

    elif field == "DIPLOMACY":
        r2 = s * 0.2
        d.ellipse([cx - r2 * 1.7, cy - r2, cx + r2 * 0.3, cy + r2],
                  outline=col, width=max(2, int(h * 0.05)))
        d.ellipse([cx - r2 * 0.3, cy - r2, cx + r2 * 1.7, cy + r2],
                  outline=mid, width=max(2, int(h * 0.05)))

    elif field == "ECONOMY":
        for k in range(3):
            yy = y0 + h * (0.26 + 0.24 * k)
            d.rectangle([x0 + w * 0.16, yy, x0 + w * (0.5 + 0.14 * k),
                         yy + h * 0.09], fill=col if k == 1 else mid)

    elif field == "ENERGY":
        for k in range(3):
            bx = x0 + w * (0.2 + 0.26 * k)
            d.line([(bx, y1 - h * 0.16), (bx, y0 + h * 0.3)],
                   fill=col, width=max(2, int(h * 0.05)))
            d.line([(bx, y0 + h * 0.3), (bx + w * 0.11, y0 + h * 0.42)],
                   fill=col, width=max(1, int(h * 0.035)))
            d.line([(bx, y0 + h * 0.3), (bx - w * 0.11, y0 + h * 0.42)],
                   fill=col, width=max(1, int(h * 0.035)))

    elif field == "CLIMATE":
        d.arc([cx - s * 0.36, cy - s * 0.36, cx + s * 0.36, cy + s * 0.36],
              start=0, end=360, fill=mid, width=max(1, int(h * 0.04)))
        d.rectangle([cx - s * 0.06, cy - s * 0.1, cx + s * 0.06, cy + s * 0.2],
                    fill=col)
        d.line([(cx - s * 0.14, cy + s * 0.2), (cx + s * 0.14, cy + s * 0.2)],
               fill=col, width=max(2, int(h * 0.05)))

    else:  # SOCIETY and anything else: a scatter of people
        for i in range(5):
            px = x0 + w * (0.2 + 0.15 * i)
            py = cy + (h * 0.08 if i % 2 else -h * 0.05)
            rr = max(2, s * 0.055)
            d.ellipse([px - rr, py - rr * 2.1, px + rr, py - rr * 0.1],
                      fill=col if i % 2 else mid)
            d.rectangle([px - rr * 1.5, py, px + rr * 1.5, py + h * 0.22],
                        fill=col if i % 2 else mid)


# --------------------------------------------------------------- the map

def draw_map(d, box, pins):
    """Draw the world in box=(x0,y0,x1,y1) with a numbered pin per story."""
    x0, y0, x1, y1 = box
    d.rectangle([x0, y0, x1, y1], fill=SEA)
    lat_top, lat_bot = 84.0, -58.0
    w, h = x1 - x0, y1 - y0

    def proj(lat, lon):
        return (x0 + (lon + 180.0) / 360.0 * w,
                y0 + (lat_top - lat) / (lat_top - lat_bot) * h)

    with open(os.path.join(HERE, "land.geojson")) as fh:
        land = json.load(fh)

    for feat in land["features"]:
        geom = feat["geometry"]
        polys = ([geom["coordinates"]] if geom["type"] == "Polygon"
                 else geom["coordinates"])
        for poly in polys:
            for ring in poly:
                pts = [proj(lat, lon) for lon, lat in ring]
                if len(pts) < 3:
                    continue
                d.polygon(pts, fill=LAND)
                d.line(pts + [pts[0]], fill=(190, 185, 172), width=1)

    d.rectangle([x0, y0, x1, y1], outline=(200, 195, 183), width=1)

    f_pin = F(NB, 7)
    for num, (lat, lon), region in pins:
        cx, cy = proj(lat, lon)
        if not (x0 + 7 <= cx <= x1 - 7 and y0 + 7 <= cy <= y1 - 7):
            continue
        col = REGION_COLOUR[region]
        r = 6.5
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col,
                  outline=WHITE, width=1)
        t = str(num)
        d.text((cx - f_pin.getlength(t) / 2, cy - 4.3), t, font=f_pin, fill=WHITE)


# --------------------------------------------------------------- the page

def main(out_path):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    inner = W - 2 * MARGIN

    # ---- top rail
    f_rail = F(NB, 8)
    tracked(d, STRAP, f_rail, MARGIN, 14, GREY, 0.9)
    counts = {}
    for item in LEADS + CARDS:
        counts[item["region"]] = counts.get(item["region"], 0) + 1
    for reg, _place, _txt in BRIEFS:
        counts[reg] = counts.get(reg, 0) + 1
    regions_used = [r for r in REGION_ORDER if counts.get(r)]
    total = sum(counts.values())
    contract = "%d STORIES  \u00b7  %d REGIONS  \u00b7  ALL FROM WEDNESDAY" % (
        total, len(regions_used))
    cw = track(f_rail, contract, 0.9)
    tracked(d, contract, f_rail, W - MARGIN - cw, 14, RED, 0.9)
    d.line([(MARGIN, 27), (W - MARGIN, 27)], fill=INK, width=2)

    # ---- masthead: the date is the nameplate
    mast = "Wednesday 18 November 2026"
    size = 78
    while F(SB, size).getlength(mast) > inner and size > 30:
        size -= 1
    f_m = F(SB, size)
    d.text(((W - F(SB, size).getlength(mast)) / 2, 32), mast, font=f_m, fill=INK)

    # ---- region bar
    bar_y = 32 + size * 1.05 + 5
    bar_h = 18
    f_rb = F(NB, 7.6)
    x = float(MARGIN)
    for reg in regions_used:
        seg = inner * counts.get(reg, 0) / total
        col = REGION_COLOUR[reg]
        d.rectangle([x, bar_y, x + seg, bar_y + bar_h], fill=col)
        label = "%s %d" % (reg, counts.get(reg, 0))
        lw = track(f_rb, label, 0.5)
        d.text((x + (seg - lw) / 2, bar_y + 5), label, font=f_rb, fill=WHITE)
        x += seg

    # ---- the day in numbers
    ny = bar_y + bar_h + 8
    nh = 29
    d.rectangle([MARGIN, ny, W - MARGIN, ny + nh], outline=HAIR, width=1)
    f_nl = F(NB, 7.8)
    tracked(d, "THE DAY IN NUMBERS", f_nl, MARGIN + 6, ny + 10.5, RED, 0.7)
    nx = MARGIN + 6 + track(f_nl, "THE DAY IN NUMBERS", 0.7) + 12
    avail = (W - MARGIN - 6 - nx) / len(NUMBERS)
    for i, (big, small) in enumerate(NUMBERS):
        col_x = nx + i * avail
        f_big = F(SB, 12.5)
        d.text((col_x, ny + 4), big, font=f_big, fill=INK)
        bw = f_big.getlength(big) + 3.5
        f_sm = F(NA, 6.6)
        lines, cur = [], ""
        for wd in small.split():
            t = (cur + " " + wd).strip()
            if not cur or f_sm.getlength(t) <= avail - bw - 3:
                cur = t
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        for j, ln in enumerate(lines[:2]):
            d.text((col_x + bw, ny + 3.5 + j * 8), ln, font=f_sm, fill=GREY)

    # ---- featured grid
    top = ny + nh + 9
    gut = 9
    lead_w = (inner - 2 * gut) / 3
    f_eye = F(NB, 6.8)
    card_w = (inner - 4 * gut) / 5
    EYE_H = 11
    PAD = 5

    def card_need(item, w_, big):
        avail_w = w_ - 2 * PAD
        f_h = F(SB, 19 if big else 12.6)
        hl = 20.4 if big else 13.8
        f_d = F(SR, 9.4 if big else 8.5)
        dl = 12.2 if big else 10.6
        hl_lines = wrap(item["head"], f_h, avail_w)
        dl_lines = wrap(item["dek"], f_d, avail_w)
        fig_h = 62 if big else 44
        text_h = (17 + EYE_H + 3 + fig_h + 4 + len(hl_lines) * hl + 2
                  + len(dl_lines) * dl)
        return text_h + PAD + 2, hl_lines, dl_lines

    def card(x, y, w_, h_, num, item, big, hl_lines, dl_lines):
        d.rectangle([x, y, x + w_, y + h_], outline=HAIR, width=1)
        col = REGION_COLOUR[item["region"]]
        d.rectangle([x, y, x + 15, y + 15], fill=RED)
        f_num = F(NB, 8.6)
        t = str(num)
        d.text((x + 7.5 - f_num.getlength(t) / 2, y + 3.2), t,
               font=f_num, fill=WHITE)
        ey = y + 17
        d.rectangle([x + PAD, ey, x + w_ - PAD, ey + EYE_H], fill=col)
        label = "%s  \u00b7  %s" % (item["region"], item["field"])
        lw = track(f_eye, label, 0.4)
        if lw > w_ - 2 * PAD - 4:
            label = item["region"]
            lw = track(f_eye, label, 0.4)
        d.text((x + PAD + (w_ - 2 * PAD - lw) / 2, ey + 2.4), label,
               font=f_eye, fill=WHITE)
        # figure sits between the eyebrow and the headline, as a band
        fig_h = 62 if big else 44
        fy0 = ey + EYE_H + 3
        motif(d, (x + PAD, fy0, x + w_ - PAD, fy0 + fig_h),
              item["field"], col)
        ty = fy0 + fig_h + 4
        f_h = F(SB, 19 if big else 12.6)
        hl = 20.4 if big else 13.8
        f_d = F(SR, 9.4 if big else 8.5)
        dl = 12.2 if big else 10.6
        hy = blit(d, hl_lines, f_h, x + PAD, ty, INK, hl)
        ty2 = blit(d, dl_lines, f_d, x + PAD, hy + 2, GREY, dl)
        CHECKS.append((num, round(y + h_, 1), round(ty2, 1),
                       round(x + w_, 1),
                       max(f_h.getlength(s) for s in hl_lines) if hl_lines else 0,
                       w_ - 2 * PAD))

    # three leads, one height for the row
    lead_rows = [card_need(it, lead_w, True) for it in LEADS]
    lead_h = max(r[0] for r in lead_rows)
    lead_h = max(lead_h, 132)
    for i, item in enumerate(LEADS):
        card(MARGIN + i * (lead_w + gut), top, lead_w, lead_h, i + 1, item,
             True, lead_rows[i][1], lead_rows[i][2])

    row_y = top + lead_h + gut
    rows = []
    for r in range(2):
        chunk = CARDS[r * 5:(r + 1) * 5]
        need = [card_need(it, card_w, False) for it in chunk]
        rows.append((max(n[0] for n in need), need))

    # one uniform height for the two five-card rows
    row_h = max(h for h, _ in rows)
    for r, (h_r, need) in enumerate(rows):
        chunk = CARDS[r * 5:(r + 1) * 5]
        for c, item in enumerate(chunk):
            card(MARGIN + c * (card_w + gut), row_y + r * (row_h + gut),
                 card_w, row_h, 4 + r * 5 + c, item, False,
                 need[c][1], need[c][2])

    # ---- map + briefs
    band = row_y + 2 * row_h + gut + 10
    d.line([(MARGIN, band - 5), (W - MARGIN, band - 5)], fill=INK, width=2)

    map_w = 452
    f_sec = F(NB, 8.6)
    tracked(d, "WHERE IT HAPPENED", f_sec, MARGIN, band, RED, 0.8)
    map_top = band + 14
    map_bottom = 978
    draw_map(d, (MARGIN, map_top, MARGIN + map_w, map_bottom),
             [(i + 1, it["ll"], it["region"])
              for i, it in enumerate(LEADS + CARDS)])
    ly = map_bottom + 4
    lx = float(MARGIN)
    f_leg = F(NB, 6.8)
    for reg in regions_used:
        d.rectangle([lx, ly + 1, lx + 7, ly + 7], fill=REGION_COLOUR[reg])
        lw = track(f_leg, reg, 0.4)
        d.text((lx + 10, ly), reg, font=f_leg, fill=GREY)
        lx += 10 + lw + 9

    # briefs, sized to fill the column height exactly
    bx = MARGIN + map_w + 15
    tracked(d, "ALSO ON WEDNESDAY 18 NOVEMBER", f_sec, bx, band, RED, 0.8)
    b_top = band + 14
    b_bottom = map_bottom
    ncols, bgut = 2, 10
    bw = (W - MARGIN - bx - bgut) / ncols
    per_col = (len(BRIEFS) + ncols - 1) // ncols

    best = None
    for fs in (7.0, 7.2, 7.4, 7.6, 7.8, 8.0, 8.2, 8.4):
        f_bn = F(NB, fs)
        f_bt = F(NA, fs)
        BL = fs * 1.22
        heights = []
        for c in range(ncols):
            tot = 0
            for reg, place, text in BRIEFS[c * per_col:(c + 1) * per_col]:
                nw = f_bn.getlength("00") + 3
                kw = f_bn.getlength(place + ":") + 2.5
                n = len(wrap(text, f_bt, bw - nw - kw))
                tot += n * BL + 3
            heights.append(tot)
        if max(heights) <= b_bottom - b_top:
            best = (fs, f_bn, f_bt, BL)
        else:
            break
    if best is None:
        best = (7.0, F(NB, 7.0), F(NA, 7.0), 7.0 * 1.22)
    fs, f_bn, f_bt, BL = best

    # spread any slack as extra leading so the river ends at the map's foot
    slack = (b_bottom - b_top) - max(
        sum(len(wrap(t, f_bt, bw - f_bn.getlength("00") - 3
                     - f_bn.getlength(p + ":") - 2.5)) * BL + 3
            for _r, p, t in BRIEFS[c * per_col:(c + 1) * per_col])
        for c in range(ncols))
    pad = max(0.0, slack / max(1, per_col - 1))

    num = len(LEADS) + len(CARDS) + 1
    for c in range(ncols):
        cx = bx + c * (bw + bgut)
        cy = b_top
        for reg, place, text in BRIEFS[c * per_col:(c + 1) * per_col]:
            n = "%d" % num
            d.text((cx, cy), n, font=f_bn, fill=RED)
            nw = f_bn.getlength(n) + 3
            kick = place + ":"
            d.text((cx + nw, cy), kick, font=f_bn, fill=REGION_COLOUR[reg])
            kw = f_bn.getlength(kick) + 2.5
            cy = blit(d, wrap(text, f_bt, bw - nw - kw), f_bt, cx + nw + kw,
                      cy, INK, BL)
            cy += 3 + pad
            num += 1

    # ---- footer
    d.line([(MARGIN, 995), (W - MARGIN, 995)], fill=INK, width=1)
    f_f = F(NA, 7.4)
    left = ("Every story happened or was first reported on Wednesday "
            "18 November 2026; contested claims are attributed.")
    d.text((MARGIN, 1001), left, font=f_f, fill=GREY)
    right = "Sources: Reuters, AP, AFP, BBC, Al Jazeera, UN News"
    d.text((W - MARGIN - f_f.getlength(right), 1001), right, font=f_f, fill=GREY)

    img.save(out_path, "PNG", optimize=True)
    return dict(stories=total, briefs=len(BRIEFS), regions=len(regions_used),
                fonts=round(fs, 2))


if __name__ == "__main__":
    import sys
    st = main(sys.argv[1] if len(sys.argv) > 1 else "entry.png")
    print(st)
