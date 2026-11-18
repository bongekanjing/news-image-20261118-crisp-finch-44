#!/usr/bin/env python3
"""Render the 18 November 2026 front page.

Broadsheet on a 1024 square: masthead, a three-lead band above the fold,
then a four-column body. Each block is measured before it is drawn so the
flow stops cleanly above the footer rule instead of running into it.
"""

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 26
BG = (251, 250, 246)
INK = (22, 22, 22)
GREY = (92, 88, 82)
RULE = (150, 146, 138)
HAIR = (214, 210, 201)
ACCENT = (139, 26, 26)

SB = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SR = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SI = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
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


def track(fnt, text, extra=0.7):
    return sum(fnt.getlength(c) + extra for c in text) - extra


def tracked(d, text, fnt, x, y, fill, extra=0.7):
    cx = x
    for ch in text:
        d.text((cx, y), ch, font=fnt, fill=fill)
        cx += fnt.getlength(ch) + extra
    return cx


# --------------------------------------------------------------- copy

LEADS = [
    ("ASIA-PACIFIC  ·  DIPLOMACY",
     "Xi greets Trump on Shenzhen tarmac as Putin summit nears",
     "China's president broke precedent to meet Air Force One and hugged "
     "Trump before the APEC summit. The three leaders hold a trilateral on "
     "Thursday, with Ukraine and nuclear arms on the table.", 27, 12.2),
    ("MIDDLE EAST",
     "US jets strike Iran's Qeshm Island; Kuwait downs drones",
     "Precision munitions hit an IRGC missile site on the Strait of Hormuz. "
     "Bahrain's defences intercepted Iranian attacks before dawn.", 21, 10.6),
    ("EUROPE",
     "EU proposes \u20ac45bn loan for Kyiv",
     "Repaid only after Russia pays reparations. Envoys Witkoff and Kushner "
     "fly to Berlin for Ukraine talks.", 21, 10.6),
]

BODY = [
    ("MIDDLE EAST", [
        ("Israel launches a rare ground raid in central Gaza",
         "Dozens of displaced families fled their tents after troops entered "
         "an area Israel quit under a 2025 deal. Trump's Board of Peace "
         "faulted both Israel and Hamas for the stalled truce."),
        ("UN: 64 Yemeni children killed since September as war widens",
         "UNICEF counts 330,000 displaced and 800,000 cut off around Taiz. "
         "Government forces struck targets in Sanaa."),
        ("Saudis brace for a Yemen campaign into 2027",
         "Riyadh is preparing up to six more months of operations against the "
         "Houthis, sources said, despite battlefield setbacks."),
        ("Settlers kill a 72-year-old woman near Jericho",
         "Britain sanctioned eight Israeli construction firms and Australia "
         "three settlers and four groups over West Bank expansion."),
    ]),
    ("EUROPE", [
        ("Ukraine strikes the Kerch Bridge for a second day",
         "Drones and missiles hit the link to occupied Crimea. Berlin "
         "defended deep strikes into Russia after US criticism of them."),
        ("Zelenskyy calls Ukraine's battlefield positions 'strong'",
         "The president cited the defence of two frontline cities in a war "
         "now in its fifth year."),
        ("Coalition of the Willing meets in Berlin on Ukraine",
         "About 20 heads of state and government weighed security guarantees "
         "for Kyiv."),
        ("Bulgaria uncovers a five-year cyberespionage operation",
         "Prosecutors said the campaign hit state and private targets and was "
         "detailed during European Cyber Week."),
        ("UK and EU to unveil a trade deal this week",
         "Ministers dropped a planned foie gras import ban to smooth the "
         "agreement, which Brussels had tied to wider market access."),
    ]),
    ("AMERICAS", [
        ("Peltola flips Alaska, lifting Democrats to 56 Senate seats",
         "Mary Peltola beat Republican Dan Sullivan 50.1% to 45.8%, becoming "
         "the first Indigenous woman from Alaska elected to the Senate."),
        ("Man charged over 'incredibly brutal' attack on an Uber driver",
         "Samit Apurva Patel, 25, faces attempted murder and carjacking "
         "charges after Mohamed Yusuf was run over in Minnesota."),
        ("NSA blames a 'temporary degradation' for a secret network outage",
         "NSANet has been down since early Tuesday and staff were staggered. "
         "Officials see no evidence of a cyberattack."),
        ("Apple restores services after an internal update failed",
         "Apple Pay and iCloud broke for users; a Gmail disruption was "
         "unrelated, Google said."),
        ("Uncontacted Aw\u00e1 make contact in the Brazilian Amazon",
         "About 20 people approached a government team asking for yams, as "
         "loggers close in on their territory."),
        ("Brazil signals more fiscal measures in the near term",
         "Finance Minister Dario Durigan said the government would move ahead "
         "with new steps to steady the budget."),
    ]),
    ("ASIA-PACIFIC", [
        ("Modi offers ASEAN free e-visas and maritime cooperation",
         "At the Manila summit India's prime minister proposed visa-free "
         "tourism plus nuclear and critical-minerals tie-ups."),
        ("Xi vows to resist protectionism as Beijing touts an open door",
         "In his APEC address Xi attacked trade barriers; he and Putin also "
         "criticised Western sanctions."),
        ("Lee and Xi hold a third summit lasting 34 minutes",
         "South Korea's president met China's leader on the summit's "
         "sidelines as Seoul balances Washington and Beijing."),
        ("Cyclone Akvan to turn severe; India warns its east coast",
         "The Bay of Bengal storm should cross between Machilipatnam and "
         "Puri. Fishermen were told to stay ashore."),
        ("Japan's exports set an October record on chip demand",
         "Shipments rose for a 14th straight month, led by semiconductors "
         "and machinery, the government said."),
        ("India re-elected to the ITU council for 2027-30",
         "The vote keeps New Delhi in the UN agency's governance as it pushes "
         "digital-connectivity rules."),
    ]),
    ("AFRICA", [
        ("Senegal's ruling party expels the president and 31 others",
         "Pastef's break with Bassirou Diomaye Faye deepens a budget standoff "
         "that threatens IMF aid and the 2027 spending plan."),
        ("UN confirms 2,230 civilian deaths in Sudan in ten months",
         "Most were killed by drone strikes, the rights office said, as the "
         "army pushed into West Kordofan."),
        ("US urges respect for the Western Sahara ceasefire",
         "Washington pressed Rabat and the Polisario Front to hold the truce "
         "as UN peacekeepers ended their mission."),
        ("Angola cuts its main rate to a 10-year low",
         "The central bank eased as inflation slowed, joining a regional "
         "cycle of cuts."),
        ("Five charged in South Africa under its mercenary law",
         "The foreign nationals are accused of trying to travel to Russia to "
         "fight in Ukraine."),
        ("Ghana's bishops seek a state of emergency on illegal mining",
         "The clergy urged action on galamsey pollution poisoning rivers."),
    ]),
    ("BUSINESS", [
        ("Dow closes 560 points lower as the AI trade splits the market",
         "Nvidia's strong forecast lifted chip stocks while the Dow sank. "
         "Investors braced for Anthropic's IPO, a test of the AI boom."),
        ("Nvidia board said to rule out bringing back Jensen Huang",
         "Huang quit after 33 years over an affair scandal but said he would "
         "be honoured to return. He testifies on 1 December."),
        ("Amazon to invest $7bn in Indian renewables by 2030",
         "The pledge covers wind and solar and backs India's clean-power "
         "targets."),
        ("Gold slips below $3,800 as the dollar firms",
         "Bullion fell as traders weighed the Fed minutes and Nvidia's "
         "results."),
    ]),
    ("SPORT", [
        ("Jay Shah re-elected ICC chairman for a second term",
         "Cricket's governing body kept its leader as the sport prepares for "
         "Los Angeles 2028."),
        ("Nigeria to meet Zambia after beating DR Congo",
         "The Super Falcons advanced in 2028 Olympic qualifying."),
        ("Japan lose 2-1 in a friendly as Moriyasu tests new faces",
         "The coach used the window to try fresh combinations."),
    ]),
]

BRIEFS = [
    "Trump says the US has closed a 'very big trade deal' with the Philippines",
    "Modi returns to Delhi after the ASEAN summit in Manila",
    "Canada and China extend trade cooperation before APEC",
    "Afghanistan gets $18m in UN emergency funds for 824,000 people",
    "Kenya inaugurates a new national stadium",
    "Uganda's Besigye family raises health concerns two years after arrest",
    "Mozambique's top court bars most media from the Mondlane trial",
    "Zimbabwe's Five return to a South African court over Russia",
    "India and Egypt form a group to explore a trade pact",
    "ICRA sees India's GDP growth at 7.5% for July-September",
    "Opening a small business in Germany takes 18 times as long as in France",
    "Trump envoy Witkoff and Kushner due in Berlin for Ukraine talks",
    "Bahrain's activist Nabeel Rajab dies at 62 in Turkey",
    "Egyptian writer ElGendy is barred from the US National Book Awards",
    "Eight-year-old Haitian boy held by US immigration is released",
    "Civil rights groups question the DOJ's new acting division chief",
]

FOOT_L = "THE WORLD TODAY  ·  18 NOVEMBER 2026"
FOOT_R = "Compiled from reporting published on the day  ·  page 1 of 1"


# --------------------------------------------------------------- render

def main(out_path):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    inner = W - 2 * MARGIN

    # folio
    f_strip = F(NB, 10)
    d.text((MARGIN, 16), "WORLD EDITION", font=f_strip, fill=ACCENT)
    tracked(d, "NO. 322", f_strip, MARGIN + track(f_strip, "WORLD EDITION") + 16,
            16, GREY)
    rt = "WEDNESDAY, 18 NOVEMBER 2026"
    d.text((W - MARGIN - track(f_strip, rt), 16), rt, font=f_strip, fill=INK)
    d.line([(MARGIN, 33), (W - MARGIN, 33)], fill=INK, width=1)

    # nameplate
    size = 76
    while F(SB, size).getlength("THE WORLD TODAY") > inner - 6:
        size -= 1
    f_m = F(SB, size)
    mw = f_m.getlength("THE WORLD TODAY")
    d.text(((W - mw) / 2, 38), "THE WORLD TODAY", font=f_m, fill=INK)
    d.line([(MARGIN, 116), (W - MARGIN, 116)], fill=INK, width=3)
    d.line([(MARGIN, 121), (W - MARGIN, 121)], fill=INK, width=1)
    f_t = F(SI, 12.5)
    tag = "One day, one page: the world's news of 18 November 2026, region by region"
    d.text(((W - f_t.getlength(tag)) / 2, 126), tag, font=f_t, fill=GREY)

    # lead band
    top = 152
    widths = [402, 294, 248]
    xs, cur = [], MARGIN
    for i, w_ in enumerate(widths):
        xs.append(cur)
        cur += w_ + 13
    f_k = F(NB, 9)
    band_bottom = top
    for i, (kick, head, dek, hs, ds) in enumerate(LEADS):
        x, w_ = xs[i], widths[i]
        y = top
        d.text((x, y), kick, font=f_k, fill=ACCENT)
        y += 14
        f_h = F(SB, hs)
        y = blit(d, wrap(head, f_h, w_), f_h, x, y, INK, hs * 1.06)
        y += 4
        f_d = F(SR, round(ds))
        y = blit(d, wrap(dek, f_d, w_), f_d, x, y, GREY, ds * 1.3)
        band_bottom = max(band_bottom, y)
        if i:
            d.line([(x - 6, top), (x - 6, band_bottom)], fill=RULE, width=1)

    rule_y = band_bottom + 11
    d.line([(MARGIN, rule_y), (W - MARGIN, rule_y)], fill=INK, width=2)

    # body grid
    ncols, gut = 4, 13
    colw = (inner - (ncols - 1) * gut) / ncols
    colx = [MARGIN + i * (colw + gut) for i in range(ncols)]
    body_top = rule_y + 13
    bottom = 984

    f_sec = F(NB, 9.5)
    f_bh = F(SB, 13.5)
    f_bd = F(NA, 9.2)
    f_br_lead = F(NB, 9.2)
    SEC_H = 20
    HEAD_L = 12.6
    DEK_L = 11.2

    def block_h(head, dek):
        return (len(wrap(head, f_bh, colw)) * HEAD_L + 2
                + len(wrap(dek, f_bd, colw)) * DEK_L + 14)

    col, y = 0, body_top
    stats = {"placed": 0, "dropped": [], "briefs": 0, "sections": 0}

    def next_col():
        nonlocal col, y
        col += 1
        y = body_top

    def section_head(name):
        nonlocal y
        sw = track(f_sec, name)
        d.text((colx[col], y + 2), name, font=f_sec, fill=ACCENT)
        d.line([(colx[col], y + 13), (colx[col] + sw, y + 13)],
               fill=ACCENT, width=1)
        stats["sections"] += 1
        y += SEC_H

    for section, stories in BODY:
        # a new section always starts at the top of a fresh column if it will
        # not fit whole enough to look intentional
        if y > body_top and y + SEC_H + block_h(*stories[0]) > bottom:
            next_col()
        if col >= ncols:
            stats["dropped"].append(section)
            break
        section_head(section)
        for head, dek in stories:
            h = block_h(head, dek)
            if y + h > bottom:
                next_col()
                if col >= ncols:
                    stats["dropped"].append(section + " / " + head[:36])
                    break
                # never leave a continued story without its section label
                section_head(section)
            yy = blit(d, wrap(head, f_bh, colw), f_bh, colx[col], y, INK, HEAD_L)
            yy = blit(d, wrap(dek, f_bd, colw), f_bd, colx[col], yy + 2, GREY, DEK_L)
            y = yy + 14
            d.line([(colx[col], y - 5), (colx[col] + colw, y - 5)], fill=HAIR, width=1)
            stats["placed"] += 1

    # briefs fill whatever columns are left
    bi = 0
    while bi < len(BRIEFS) and col < ncols:
        if y > body_top and y + SEC_H + 26 > bottom:
            next_col()
            if col >= ncols:
                break
        section_head("IN BRIEF")
        while bi < len(BRIEFS):
            item = BRIEFS[bi]
            lines = wrap(item, f_br_lead, colw - 9)
            h = len(lines) * DEK_L + 8
            if y + h > bottom:
                break
            for j, ln in enumerate(lines):
                d.text((colx[col], y + j * DEK_L), ln, font=f_br_lead, fill=INK)
            d.ellipse([colx[col] + 0.5, y + 4, colx[col] + 3.5, y + 7], fill=ACCENT)
            y += h - 4
            d.line([(colx[col], y), (colx[col] + colw, y)], fill=HAIR, width=1)
            y += 4
            bi += 1
            stats["briefs"] += 1

    # column rules
    for i in range(1, ncols):
        d.line([(colx[i] - gut / 2, body_top), (colx[i] - gut / 2, bottom)],
               fill=HAIR, width=1)

    # footer
    d.line([(MARGIN, 995), (W - MARGIN, 995)], fill=INK, width=1)
    f_f = F(NA, 8.5)
    d.text((MARGIN, 1001), FOOT_L, font=f_f, fill=GREY)
    d.text((W - MARGIN - f_f.getlength(FOOT_R), 1001), FOOT_R, font=f_f, fill=GREY)

    img.save(out_path, "PNG", optimize=True)
    return stats


if __name__ == "__main__":
    import sys
    st = main(sys.argv[1] if len(sys.argv) > 1 else "entry.png")
    print("stories:", st["placed"], " briefs:", st["briefs"], " dropped:", st["dropped"])
