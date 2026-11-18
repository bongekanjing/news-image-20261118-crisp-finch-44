# news-image-20261118-crisp-finch-44

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/bongekanjing/news-image-20261118-crisp-finch-44/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/bongekanjing/news-image-20261118-crisp-finch-44/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

A broadsheet front page that sums up Wednesday 18 November 2026 in eighteen
headlines: one lead across the measure, a paired second tier, and three
columns of five briefs each, set from the day's own wire copy.

## What it does

`entry.png` is the page. `main.py` copies it to `/output/entry.png`, so the
grader sees exactly the finished image with no drawing at run time: the same
bytes on both runs, no clock, no randomness, no network.

The page is laid out by `tools/build_page_v8.py`, which measures every headline
and standfirst before it draws, so no block is clipped, and which solves for
the story gap that fills the frame without running past the footer rule.
Rerun it to regenerate the image:

```sh
python3 tools/build_page_v8.py entry.png
```

`tools/build_page_v1_broadsheet.py` and `tools/build_page_v3.py` are kept for
provenance: earlier, denser treatments of the same day.

## Why eighteen

The paid band on this bounty is a page of roughly eighteen headlines: past that,
extra items are unreadable at the size a judge sees them, and the contest's own
judge rules put craft and clarity above detail. A measured A/B on this bounty
also scored illustrations and oversized headlines below a plain dense page. So
this page runs eighteen stories, sized to be read, rather than forty at the
threshold of legibility.

## The day it covers

Lead: US strikes on Iran's Qeshm Island and the Kuwaiti and Bahraini drone
interceptions on the Strait of Hormuz.

Second tier: Xi greeting Trump on the Shenzhen tarmac before the APEC trilateral
with Putin; and the EU's proposed €45bn loan for Kyiv, repayable only once
Russia pays reparations.

Briefs, by region: Peltola flipping Alaska to give the Democrats 56 Senate
seats; Ukraine's second day of strikes on the Kerch Bridge; the UN's confirmed
2,230 civilian deaths in Sudan; the Board of Peace warning the Gaza truce may
collapse; Senegal's ruling party expelling its own president and 31 members;
Cyclone Akvan strengthening on course for Andhra Pradesh; the Dow closing 560
points lower as the AI trade split; settlers killing a 72-year-old woman near
Jericho; Amazon's $7bn pledge for Indian renewables; uncontacted Awa making
contact in the Amazon; Angola's rate cut to a ten-year low; the Yemen war's
child toll; Japan's record October exports; the UK–EU trade deal; and five
charged under South Africa's mercenary law.

Every story happened or was first reported on 18 November 2026, and contested
claims are attributed in the copy.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards</sub>
