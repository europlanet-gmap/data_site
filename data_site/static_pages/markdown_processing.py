from flask_flatpages.utils import pygmented_markdown
from bs4 import BeautifulSoup

import re
urlfinder = re.compile('^(https?:\/\/\S+)')
urlfinder2 = re.compile('\s(https?:\/\/\S+)')
def urlify_markdown(value):
    value = urlfinder.sub(r'<\1>', value)
    return urlfinder2.sub(r' <\1>', value)

def post_process(func):
    def wrapper(text, flatpages=None):

        text = urlify_markdown(text)

        o = func(text, flatpages)

        bs = BeautifulSoup(o)

        for h in bs.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            name = h.text
            name = re.sub(r'[^\w\s-]', '', name.lower())
            name = re.sub(r'[\s]+', '-', name).strip('-_')
            h["id"] = name

        for s in bs.find_all("strong", string="Note"):
            new_tag = bs    .new_tag("p")
            s.find_previous("hl")
            s["class"] = "alert alert-primary"
            s.find_next("hl")

        for i in bs.find_all("img"):
            i["class"] = "img-fluid rounded mx-auto d-block"
            i["style"] = "max-width: 70%"

        for t in bs.find_all("table"):
            t["class"] = "table table-striped table-hover d-block"
            t["style"] = "max-width: 70%"

        for c in bs.find_all("figcaption"):
            c["class"] = "figure-caption mb-2"

        return bs.prettify()

    return wrapper

md_renderer = post_process(pygmented_markdown)