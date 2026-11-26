# THE THURSDAY GLOBE — news-image-20261126

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/hmnk0311/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/hmnk0311/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

One front page for Thursday 26 November 2026: **36 stories,
6 continents, one page and a map.**

## The image

`entry.png` is a 1024x1024 newspaper front page dated Thursday
26 November 2026. A dotted world map carries 14 numbered pins, and
every pin resolves to a numbered brief on the page, so a reader who
missed the day can trace each story to its place.

The day's lead is the United States proposal, after an eight-month
Section 301 investigation, to place new tariffs on 14 trading
partners — with every rate printed as an "up to" figure, exactly as
proposed rather than as if already in force. The second lead
reports Wednesday's tanker fires in the Strait of Hormuz in claims
language, because the mine strikes were Iranian claims that Reuters
said it could not independently verify. A strip across the page
follows Ukraine's deep strike on the Savasleyka air base and the
reactions around it.

Around those sit the rest of the day as Thursday's papers carried
it: the Gaza strike and Lebanon's second airport, the Cairo Ring
Road tanker disaster at the health ministry's latest toll, Sudan's
Blue Nile drone strikes, South Africa's Phala Phala ruling, the
Russian airspace incursions reported by Japan, South Korea and
Taiwan, the Bogor mine flood, US PCE inflation and jobless claims
released early for Thanksgiving, Australia's Flight Centre data
investigation, Alcaraz on Sinner's absence, and the three NFL
Thanksgiving fixtures.

## Running it

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` uses only the Python standard library and no network. It
validates the bundled image before delivering it: file size, PNG
chunk structure with a CRC32 check on every chunk, IHDR-first and
IEND-last ordering, the 1024-pixel side limit, and then a plain
in-place copy whose SHA-256 is verified against the source.

## Sources

[SOURCES.md](SOURCES.md) lists, story by story, the wire reports
and Thursday-morning papers each brief rests on, including the
places where a claim is attributed rather than stated as fact.

## License

MIT — see [LICENSE](LICENSE).
