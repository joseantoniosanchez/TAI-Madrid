import re

import bs4
import yaml

sp = re.compile(r"\s+")
sep = re.compile(r"  +")


def dict_from_txt(f, rever=False, parse_key=None):
    d = {}
    with open(f) as y:
        for l in y.readlines():
            tup = sep.split(l.strip())
            if rever:
                tup = list(reversed(tup))
            k = tup[0]
            v = tup[1:]
            if parse_key:
                k = parse_key(k)
            elif k.isdigit():
                k = int(k)
            if len(v) == 1:
                v = v[0]
            else:
                v = tuple(v)
            d[k] = v
    return d


def yaml_from_file(f):
    with open(f) as y:
        return yaml.load(y)


def yaml_to_file(f, data):
    with open(f, 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)


def soup_from_file(f):
    with open(f, 'rb') as html:
        soup = bs4.BeautifulSoup(html, "lxml")
        return soup


def fix_html(html, *args, **kargs):
    html = bs4.BeautifulSoup(html, "html.parser")
    for n in html.findAll("span"):
        t = sp.sub("", n.get_text())
        if len(t) == 0 or t == "None":
            n.extract()

    for n in html.findAll("td"):
        t = sp.sub("", n.get_text())
        if t == "None":
            n.string = ""

    for t in html.select(".idde"):
        spans = t.findAll("span")
        if len(spans) == 1:
            spans[0].unwrap()
            del t.attrs["class"]

    for table in html.findAll("table"):
        rows = []
        for tr in table.select("tbody tr"):
            rows.append([sp.sub("", td.get_text()) for td in tr.findAll("td")])
        if len(rows) == 0:
            continue
        for i in range(len(rows[0]) - 1, -1, -1):
            flag = True
            for r in rows:
                flag = flag and r[i] == ""
            if flag:
                for tr in table.select("tr"):
                    tr.findAll(["td", "th"])[i].extract()

    for table in html.findAll("table"):
        rowA = (None, ) * 999
        for tr in table.select("tbody tr"):
            tds = tr.findAll("td")
            rowB = [sp.sub(" ", td.get_text()).strip() for td in tds]
            for i in range(1, len(rowB)):
                if rowA[i] == rowB[i]:
                    cl = tds[i].attrs.get("class", [])
                    cl.append("repe")
                    tds[i].attrs["class"] = cl
            rowA = rowB

    for n in html.findAll(text=lambda text: isinstance(text, bs4.Comment)):
        n.extract()

    return str(html)
