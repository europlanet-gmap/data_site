import requests

from bs4 import BeautifulSoup

import attr

from joblib import Memory
memory = Memory("/tmp", verbose=0)


@attr.attrs
class Body():
    name = attr.ib(None)
    maps = attr.ib(None)


@attr.attrs
class Product():
    name = attr.ib(None)
    url = attr.ib(None)
    all_docs = attr.ib(None)
    readme = attr.ib(None)
    thumb = attr.ib(None)
    thumb_url = attr.ib(None)


baseurl = "https://data.planmap.eu/pub/"

bodies = ["mars", "mercury", "moon"]
# bodies = ["mars"]
ignore = ["versions/", "README.md"]

def fetch_address(url):
    html = requests.get(url).content
    soup = BeautifulSoup(html, "html5lib")
    return soup


def get_cleaned_links(soup, ignore=[]):
    found = soup.find_all(["a"], recursive=True)

    out = []
    for f in found:
        if list(f.children)[0] == f["href"] and f["href"] not in ignore:
            if f["href"][-1] == "/":
                name = f["href"][:-1]
            else:
                name = f["href"]
            out.append(name)
        # else:
        #     print(f"discarded {f}")


    return out



def fetch_maps():
    bb = []
    for body in bodies:
        b = Body()
        b.name = body
        url = baseurl + body
        soup = fetch_address(url)
        #     found = soup.find_all(["a"], recursive=True)

        maps = []
        out = get_cleaned_links(soup, ignore)
        for name in out:
            m = Product(name=name)
            maps.append(m)
        #     for f in found:
        #         if list(f.children)[0] == f["href"] and f["href"] not in ignore:
        #             m = Map(name=f["href"][:-1])
        #             out.append(m)

        b.maps = maps
        bb.append(b)

    return bb



def compose_urls(bb):
    # compose the per map urls
    for body in bb:
        for map in body.maps:
            new_addr = baseurl + body.name + "/" + map.name

            map.url = new_addr
    return bb

def append_docs(bb):
    # append the list of available docs
    for body in bb:
        for map in body.maps:
            docurl = map.url + "/" + "document/"
            soup = fetch_address(docurl)
            links = get_cleaned_links(soup, ignore)
            map.all_docs = links
    return bb

def append_readme(bb):
    for body in bb:
        for map in body.maps:
            docurl = map.url + "/"
            soup = fetch_address(docurl)
            links = get_cleaned_links(soup)
            for ln in links:
                # print(f" testing link {ln}")
                if ln.lower().endswith("readme.md"):
                    soup = fetch_address(map.url + "/" + ln)
                    map.readme = soup.get_text()
            # map.all_docs = links
    return bb



# select proper thumbnails
import re
def select_thumbnails(bb):
    for body in bb:
        for map in body.maps:
            found = None
            allpngs = []
            for doc in map.all_docs:
                #             print (doc)
                ma = re.match(f"{map.name}([\_-][0-9]*)?.browse\.png", doc)
                if ma:
                    found = doc
                    print(f"found good thumbnail {found}")

                ma = re.match(f"{map.name}.*(\.browse)?\.png", doc)
                if ma:
                    allpngs.append(doc)

                ma = re.match(f".*(\.browse)?\.png", doc)
                if ma:
                    allpngs.append(doc)

            if not found:
                print(f"Thumb Not found for {map.name}")
                if len(allpngs) > 0:
                    print(f"autoassign {allpngs[0]}")
                    found = allpngs[0]

            map.thumb = found

    return bb


def append_thumb_url(bb):
    for body in bb:
        for map in body.maps:
            thumb = map.thumb
            if thumb:
                map.thumb_url = map.url + "/" + "document/" + thumb



# @memory.cache
def scrape_maps():
    bb = fetch_maps()
    compose_urls(bb)
    append_docs(bb)
    append_readme(bb)
    select_thumbnails(bb)
    append_thumb_url(bb)

    return bb