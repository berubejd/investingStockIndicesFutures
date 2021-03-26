#!/usr/bin/env python3

import os
import pathlib
import requests
import requests_cache

from datetime import timedelta
from bs4 import BeautifulSoup


tmp = pathlib.Path(os.getenv("TMP", "/tmp"))
cache_file = tmp / "indicies_cache"

expire_after = timedelta(minutes=5)
requests_cache.install_cache(cache_name=str(cache_file), expire_after=expire_after)
requests_cache.remove_expired_responses()

url = "https://m.investing.com/indices/indices-futures"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
}


def _get_soup(url=url, headers=headers):
    with requests.Session() as s:
        resp = s.get(url, headers=headers)

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(e)
            return None

        return BeautifulSoup(resp.content, "html.parser")


def print_header():
    print("Index|Last|Timestamp|Days Change|Days % Change")


def find_items():
    """
    <tr class="..." data-test="price-row">
        <td class="..." style="--cell-display:block;--cell-positions:flag">
            <div class="lazyload-wrapper">
                <div class="lazyload-placeholder"></div>
            </div>
        </td>
        <td class="... font-bold text-secondary" style="--cell-display:block;--cell-positions:name">
            <div class="..."> <a class="..." href="/indices/us-30-futures" title="Dow Jones Futures - (CFD)">US 30</a><span class="...">derived</span>
                <div class="" data-test="instrument-tracker">
                    <button class="..." type="button" aria-label="add alert" data-test="table-plus-icon">
                        <svg viewBox="0 0 24 24" width="1em" fill="none" style="height:auto">
                            ...
                        </svg>
                    </button>
                </div>
            </div>
        </td>
        <td class="... text-sm" style="--cell-display:block;--cell-positions:expire"><span data-mobile-cell="" class="mobile-only mr-1">Ex.</span>Jun 21</td>
        <td class="..." style="--cell-display:block;--cell-positions:last">32,607.00</td>
        <td class="...">32,611.00</td>
        <td class="...">32,496.50</td>
        <td class="..." dir="ltr" style="--cell-display:block;--cell-positions:chg">+106.0</td>
        <td class="..." dir="ltr" style="--cell-display:flex;--cell-positions:chg-pct">+0.33%</td>
        <td class="..." style="--cell-display:block;--cell-positions:time">
            <time dateTime="01:34:46">01:34:46</time>
        </td>
        <td class="..." data-test="market-open-1" style="--cell-display:block;--cell-positions:clock">
            <svg viewBox="0 0 24 24" width="1em" fill="none" style="height:auto" class="datatable_clock__3cqsC">
                ...
            </svg>
        </td>
    </tr>
    """
    soup = _get_soup()

    commodoties = soup.select("main tbody tr", {"data-test": "price-row"})

    for c in commodoties:
        c_commod = []

        c_data = c.select("td")

        # Get name
        c_commod.append(c_data[1].a.text)

        # Get last
        c_commod.append(c_data[3].text)

        # Get timestamp - Two different storage formats on the same page at this time
        c_time = c_data[8].select_one("time")

        c_commod.append(
            c_time["datetime"]
            if c_time and c_time.has_attr("datetime")
            else c_data[8].text
        )

        # Get change and change %
        # Only one format has the change value and the percentage is at another place in the table
        if len(c_data) == 9:
            c_change = "-"
            c_percent = c_data[4].text
        else:
            c_change = c_data[6].text
            c_percent = c_data[7].text

        c_commod.extend([c_change, c_percent])

        # Output row
        print("|".join(c_commod))


if __name__ == "__main__":
    print_header()
    find_items()
