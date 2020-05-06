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
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


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
    print("Index, Last, Timestamp, Days Change, Days % Change")

def find_items():
    """
    <article data-href="/indices/us-30-futures" class="pairItem js-link-item">
        <div class="pullLeft titleComod fullWidthPercent">
            <a href="/indices/us-30-futures" class="pullLeft" >
                Dow 30
            </a>
            <div class="pullRight pid-8873-last">
                18,094.0
            </div>
	        <span class="derivedIcon">
                DERIVED
            </span>
        </div>
        <div class="pullRight fullWidthPercent secondTitle">
            <span class="isOpenExch-8873 pullLeft clockGreen"></span>
            <span class="pullLeft pairTimestamp">
                <i class="pid-8873-time">
                    21:19:35
                </i>
                &nbsp;|&nbsp;Futures
            </span>
            <div class="comodMerg pullRight">
                <span dir="ltr" class="redFont paddingChangeAttr pid-8873-pc">
                    -946.0
                </span>
                <span dir="rtl"></span>
                <span dir="ltr" class="parentheses redFont pid-8873-pcp">
                    -4.97%
                </span>
            </div>
        </div>
        <div class="clear"></div>
    </article>
    """
    soup = _get_soup()
    
    commodoties = soup.select("article")

    for c in commodoties:
        c_commod = []

        # Get name and current value
        c_current = c.select_one(".titleComod")

        # Name
        c_commod.append(c_current.select_one("a").text)
        # Last
        c_commod.append(c_current.select_one("div").text)

        # Get timestamp
        c_commod.append(c.select_one(".pairTimestamp i").text)

        # Get change and change %
        c_change = c.select(".comodMerg span")

        for ch in c_change:
            if ch.text:
                c_commod.append(ch.text)

        # Output row
        print("|".join(c_commod))

if __name__ == "__main__":
    print_header()
    find_items()
