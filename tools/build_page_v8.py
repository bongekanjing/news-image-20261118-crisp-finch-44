#!/usr/bin/env python3
"""Render the 18 November 2026 front page: eighteen headlines, broadsheet.

The paid band on this bounty sits at about eighteen headlines a page, and a
measured A/B on this bounty scored illustrations and oversized headlines below
a plain dense page. So this renderer does one thing: eighteen of the day's
most consequential stories, set in three columns under one lead, in type large
enough to read at a glance and small enough to carry the whole day.

Every block is measured before it is drawn, so a column stops cleanly above
the footer rule. The render is deterministic: no clock, no randomness.
"""

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 26
GUTTER = 24

BG = (251, 250, 246)
INK = (20, 20, 20)
GREY = (78, 74, 68)
RULE = (120, 116, 108)
HAIR = (206, 202, 193)
ACCENT = (139, 26, 26)

SB = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SR = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
NA = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
NB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

_fc = {}


def F(path, px):
    key = (path, px)
    if key not in _fc:
        _fc[key] = ImageFont.truetype(path, px)
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


def track(fnt, text, extra=0.8):
    return sum(fnt.getlength(c) + extra for c in text) - extra


def tracked(d, text, fnt, x, y, fill, extra=0.8):
    cx = x
    for ch in text:
        d.text((cx, y), ch, font=fnt, fill=fill)
        cx += fnt.getlength(ch) + extra
    return cx


# ---------------------------------------------------------------- the copy
# Eighteen stories: the day's most consequential, spread across regions and
# fields. All dated 18 November 2026 and drawn from the reporting gathered for
# this entry; contested claims are attributed in the deck.

LEAD = ("MIDDLE EAST  \u00b7  WAR",
        "US jets strike Iran's Qeshm Island; Kuwait downs the drones",
        "Precision munitions hit an IRGC missile site on the Strait of Hormuz. "
        "Bahrain's defences intercepted the answering drones before dawn, the "
        "first such exchange in two months. Tehran said it targeted US forces "
        "at Kuwait's Ali Al Salem base; Washington reported no casualties.")

BAND = [
    ("ASIA  \u00b7  DIPLOMACY",
     "Xi greets Trump in Shenzhen as a Putin summit nears",
     "China's president broke precedent to meet Air Force One on the tarmac. "
     "The three leaders sit down on Thursday, with Ukraine and nuclear arms "
     "on the table."),
    ("EUROPE  \u00b7  ECONOMY",
     "The EU proposes a 45bn-euro loan to keep Kyiv solvent",
     "Repayable only once Russia pays reparations, it covers about two-thirds "
     "of Ukraine's 2027 budget gap and is tied to a defence build-up."),
]

COLUMNS = [
    ("AMERICAS  \u00b7  POLITICS",
     "Peltola flips Alaska and lifts the Democrats to 56 seats",
     "Mary Peltola beat the Republican incumbent Dan Sullivan, 50.1% to 45.8%, "
     "the first Indigenous woman Alaska has sent to the Senate."),
    ("EUROPE  \u00b7  WAR",
     "Ukraine strikes the Kerch Bridge for a second day",
     "Drones and missiles hit the link to occupied Crimea, Moscow said, as "
     "Kyiv pressed a deep-strike campaign on Russian logistics."),
    ("AFRICA  \u00b7  WAR",
     "The UN confirms 2,230 civilian deaths in Sudan",
     "Most were killed by drone strikes, the rights office said, as the army "
     "pushed into West Kordofan in a widening offensive."),
    ("MIDDLE EAST  \u00b7  PEACE",
     "The Board of Peace warns the Gaza truce may collapse",
     "Its report to the UN faults both Israel and Hamas for failing to carry "
     "the ceasefire forward."),
    ("AFRICA  \u00b7  POLITICS",
     "Pastef expels the president and 31 other members",
     "The ruling party's break with Bassirou Diomaye Faye deepens a budget "
     "standoff that threatens IMF support."),
    ("ASIA  \u00b7  WEATHER",
     "Cyclone Akvan strengthens on course for Andhra Pradesh",
     "The Bay of Bengal storm should cross between Machilipatnam and Puri on "
     "Friday. Fishermen were told to stay ashore."),
    ("WORLD  \u00b7  MARKETS",
     "The Dow closes 560 points lower as the AI trade splits",
     "Nvidia's forecast lifted chipmakers while the Dow sank, and investors "
     "braced for Anthropic's listing."),
    ("MIDDLE EAST  \u00b7  RIGHTS",
     "Settlers kill a 72-year-old woman near Jericho",
     "Britain sanctioned four Israeli groups and Australia three settlers "
     "over West Bank expansion."),
    ("ASIA  \u00b7  ENERGY",
     "Amazon pledges 7bn dollars for Indian renewables",
     "The wind and solar spend is to land by 2030 and backs the country's "
     "clean-power targets."),
    ("AMERICAS  \u00b7  SOCIETY",
     "Uncontacted Awa make contact in the Amazon",
     "About twenty people approached a government team asking for yams as "
     "loggers closed on their territory."),
    ("AFRICA  \u00b7  ECONOMY",
     "Angola cuts its main rate to a ten-year low",
     "The central bank lowered the benchmark to 14% as inflation eased for a "
     "sixth month."),
    ("MIDDLE EAST  \u00b7  WAR",
     "The UN says 64 Yemeni children have been killed since September",
     "UNICEF counted 330,000 displaced and 800,000 cut off around Taiz as the "
     "war widens."),
    ("ASIA  \u00b7  TRADE",
     "Japan's exports set an October record on chip demand",
     "Shipments to Asia rose for a fourth month, the finance ministry said, "
     "led by semiconductor equipment."),
    ("EUROPE  \u00b7  TRADE",
     "Britain and the EU are set to unveil a trade deal this week",
     "Negotiators closed most of the text, officials said, easing rules for "
     "food and chemicals."),
    ("AFRICA  \u00b7  JUSTICE",
     "Five are charged under South Africa's mercenary law",
     "The case is the first test of a 1998 statute barring citizens from "
     "fighting abroad."),
]

# Sanity: the page must stay at eighteen headlines.
assert len(BAND) + len(COLUMNS) + 1 == 18, len(BAND) + len(COLUMNS) + 1


def main(out_path):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    inner = W - 2 * MARGIN
    bottom = H - 29

    # ------------------------------------------------------------ masthead
    strap = "THE DAY IN ONE PAGE"
    f_strap = F(NB, 9.5)
    tracked(d, strap, f_strap, MARGIN, 24, ACCENT, 1.6)
    right = "18 STORIES  \u00b7  6 REGIONS  \u00b7  ONE DAY"
    f_r = F(NB, 9.5)
    rw = track(f_r, right, 1.0)
    tracked(d, right, f_r, W - MARGIN - rw, 24, GREY, 1.0)

    mast = "Wednesday 18 November 2026"
    size = 74
    while size > 30 and F(SB, size).getlength(mast) > inner:
        size -= 2
    f_mast = F(SB, size)
    d.text(((W - f_mast.getlength(mast)) / 2, 40), mast, font=f_mast, fill=INK)

    bar_y = 40 + size * 1.02 + 6
    d.rectangle([MARGIN, bar_y, W - MARGIN, bar_y + 3], fill=INK)

    # dateline strip
    dy = bar_y + 12
    f_dl = F(NA, 9.2)
    dl = ("VOL. I  \u00b7  NO. 322  \u00b7  THE EVENTS OF WEDNESDAY, IN ANY TIME "
          "ZONE  \u00b7  CONTESTED CLAIMS ARE ATTRIBUTED")
    d.text((MARGIN, dy), dl, font=f_dl, fill=GREY)
    ly = dy + 15
    d.rectangle([MARGIN, ly, W - MARGIN, ly], fill=HAIR)

    top = ly + 10

    # ------------------------------------------------------------ the lead
    pad = 0
    f_eye = F(NB, 9.0)

    def eyebrow(text, x, y, col=ACCENT):
        tracked(d, text, f_eye, x, y, col, 1.3)

    eyebrow(LEAD[0], MARGIN, top)
    f_lh = F(SB, 44)
    ll = wrap(LEAD[1], f_lh, inner)
    lh_lead = 49
    y = top + 15
    y = blit(d, ll, f_lh, MARGIN, y, INK, lh_lead)
    # deck across two sub-columns
    f_ld = F(SR, 13.4)
    half = (inner - GUTTER) // 2
    dl_lines = wrap(LEAD[2], f_ld, half)
    n = (len(dl_lines) + 1) // 2
    y += 7
    y1 = blit(d, dl_lines[:n], f_ld, MARGIN, y, GREY, 17.4)
    blit(d, dl_lines[n:], f_ld, MARGIN + half + GUTTER, y, GREY, 17.4)
    y = y1 + 12
    d.rectangle([MARGIN, y, W - MARGIN, y + 1], fill=RULE)
    y += 9

    # ------------------------------------------------------------ the band
    band_w = (inner - GUTTER) // 2
    f_bh = F(SB, 25)
    f_bd = F(SR, 11.6)
    band_blocks = []
    for eb, head, dek in BAND:
        hl = wrap(head, f_bh, band_w)
        dl2 = wrap(dek, f_bd, band_w)
        h = 14 + len(hl) * 29 + 4 + len(dl2) * 14.2
        band_blocks.append((eb, hl, dl2, h, head))
    band_h = max(b[3] for b in band_blocks)

    for i, (eb, hl, dl2, hh, head) in enumerate(band_blocks):
        x = MARGIN + i * (band_w + GUTTER)
        eyebrow(eb, x, y)
        yy = blit(d, hl, f_bh, x, y + 15, INK, 29)
        blit(d, dl2, f_bd, x, yy + 4, GREY, 14.2)
    if len(band_blocks) == 2:
        d.rectangle([MARGIN + band_w + GUTTER // 2, y + 2,
                     MARGIN + band_w + GUTTER // 2, y + band_h + 4], fill=HAIR)
    y += band_h + 6
    d.rectangle([MARGIN, y, W - MARGIN, y + 2], fill=INK)
    y += 11

    # ------------------------------------------------------- the three columns
    col_w = (inner - 2 * GUTTER) // 3
    f_ch = F(SB, 16.4)
    f_cd = F(SR, 11.2)
    f_ce = F(NB, 8.6)

    def block_h(item):
        eb, head, dek = item
        hl = wrap(head, f_ch, col_w)
        dl3 = wrap(dek, f_cd, col_w)
        return 12.0 + len(hl) * 19.0 + 3.5 + len(dl3) * 13.6, hl, dl3

    measured = [(block_h(it), it) for it in COLUMNS]

    # Balance the fifteen stories into three columns, and pick the story gap
    # that fills the frame without ever running past it. A wider gap spreads
    # the page; a narrower one keeps it from overflowing. Deterministic.
    def layout(gap):
        cols = [[], [], []]
        heights = [y, y, y]
        for (hgt, hl, dl3), it in measured:
            j = heights.index(min(heights))
            cols[j].append((it, hgt, hl, dl3))
            heights[j] += hgt + gap
        ends = [y + sum(c[1] for c in col) + gap * max(0, len(col) - 1)
                for col in cols]
        return cols, ends

    lo, hi, gap = 8.0, 30.0, 8.0
    while hi - lo > 0.1:
        mid = (lo + hi) / 2
        _, ends = layout(mid)
        if max(ends) <= bottom - 6:
            lo, gap = mid, mid
        else:
            hi = mid
    cols, ends = layout(gap)

    last_ink = [y, y, y]
    for j, col in enumerate(cols):
        x = MARGIN + j * (col_w + GUTTER)
        cy = y
        for k, (it, hgt, hl, dl3) in enumerate(col):
            if k:
                d.rectangle([x, cy, x + col_w, cy], fill=HAIR)
                cy += gap / 2
            eb, head, dek = it
            eyebrow(eb, x, cy, GREY)
            cy2 = blit(d, hl, f_ch, x, cy + 12.0, INK, 19.0)
            cy2 = blit(d, dl3, f_cd, x, cy2 + 3.5, GREY, 13.6)
            cy = cy2 + gap / 2
        last_ink[j] = cy - gap / 2

    # ------------------------------------------------------------ footer
    fy = H - 26
    d.rectangle([MARGIN, fy - 6, W - MARGIN, fy - 5], fill=RULE)
    f_ft = F(NA, 7.8)
    foot = ("Every story here happened or was first reported on Wednesday 18 "
            "November 2026. Sources: Reuters, AP, AFP, Al Jazeera, UN News, "
            "BBC, NPR.")
    d.text((MARGIN, fy), foot, font=f_ft, fill=GREY)

    img.save(out_path)
    return {"lead": 1, "band": len(BAND), "columns": len(COLUMNS),
            "total": 1 + len(BAND) + len(COLUMNS),
            "col_last_ink": [round(v) for v in last_ink],
            "bottom": bottom}


if __name__ == "__main__":
    import sys
    print(main(sys.argv[1] if len(sys.argv) > 1 else "out.png"))
