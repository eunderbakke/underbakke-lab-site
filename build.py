#!/usr/bin/env python3
"""Builds the Underbakke Lab website.

Edit the files in content/, then run:  python3 build.py
The finished pages are written to docs/, which is what GitHub Pages serves.
Uses only the Python standard library.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
OUT = ROOT / "docs"

# Photos still hosted on Squarespace's image servers (see README).
CDN = "https://images.squarespace-cdn.com/content/v1/588523442e69cf6033cb146e/"
LOGO = CDN + "2336b613-6637-4016-84f4-89f6e11ae731/ESU+Lab+Logo+website-01.png?format=750w"

NAV = [
    ("index.html", "Home"),
    ("people.html", "People"),
    ("research.html", "Research"),
    ("publications.html", "Publications"),
    ("resources.html", "Resources"),
    ("news.html", "News"),
    ("contact.html", "Contact"),
]


def img(path, width=750):
    """Full address for a photo: local files stay as-is, others come from the CDN."""
    if path.startswith("assets/") or path.startswith("http"):
        return path
    return f"{CDN}{path}?format={width}w"


def inline(text):
    """Tiny Markdown: [text](url), **bold**, *italic*."""
    t = html.escape(text, quote=False).replace("\\*", "&#42;")  # \* is a literal asterisk
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", t)
    return t


def page(filename, title, body, current=None, description=""):
    current = current or filename
    nav = "\n".join(
        f'        <li><a href="{href}"{" aria-current=\"page\"" if href == current else ""}>{label}</a></li>'
        for href, label in NAV
    )
    full_title = "Underbakke Lab" if filename == "index.html" else f"{title} | Underbakke Lab"
    desc = description or (
        "The Underbakke Lab at Iowa State University studies the architecture "
        "and assembly of scaffolded signaling complexes."
    )
    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(full_title)}</title>
  <meta name="description" content="{html.escape(desc)}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Serif:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
  <link rel="icon" href="assets/favicon-32.png" sizes="32x32" type="image/png">
  <link rel="icon" href="assets/favicon-192.png" sizes="192x192" type="image/png">
  <link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
  <link rel="stylesheet" href="assets/style.css">
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="wrap header-inner">
      <a class="logo" href="index.html"><img src="{LOGO}" alt="Underbakke Lab" width="750" height="169"></a>
      <nav aria-label="Main">
        <ul>
{nav}
        </ul>
      </nav>
    </div>
  </header>
  <main id="main">
{body}
  </main>
  <footer class="site-footer">
    <div class="wrap footer-inner">
      <p><strong>Underbakke Lab</strong><br>
      Roy J. Carver Department of Biochemistry, Biophysics &amp; Molecular Biology<br>
      Iowa State University</p>
      <p>4212 Molecular Biology Building<br>
      2437 Pammel Dr., Ames, IA 50011<br>
      <a href="mailto:esu@iastate.edu">esu@iastate.edu</a></p>
    </div>
  </footer>
</body>
</html>
"""
    (OUT / filename).write_text(doc, encoding="utf-8")


# ---------- News ----------

def load_news():
    posts = []
    for chunk in re.split(r"^## ", (CONTENT / "news.md").read_text(encoding="utf-8"), flags=re.M)[1:]:
        lines = chunk.strip().split("\n")
        post = {"title": lines[0].strip(), "date": "", "image": None, "paras": []}
        rest = lines[1:]
        while rest and re.match(r"^(date|image):", rest[0]):
            key, value = rest.pop(0).split(":", 1)
            if key == "date":
                post["date"] = value.strip()
            else:
                src, _, alt = value.partition("|")
                post["image"] = (src.strip(), alt.strip())
        post["paras"] = [p.strip() for p in "\n".join(rest).split("\n\n") if p.strip()]
        year = re.search(r"(19|20)\d\d", post["date"])
        post["year"] = year.group(0) if year else ""
        posts.append(post)
    return posts


def news_post(post, level="h3"):
    parts = [f'<article class="post">',
             f'  <p class="post-date">{html.escape(post["date"])}</p>',
             f'  <{level}>{inline(post["title"])}</{level}>']
    parts += [f"  <p>{inline(p)}</p>" for p in post["paras"]]
    if post["image"]:
        src, alt = post["image"]
        parts.append(f'  <img src="{img(src)}" alt="{html.escape(alt)}" loading="lazy">')
    parts.append("</article>")
    return "\n".join(parts)


def build_news(posts):
    out, year = ['<div class="wrap">', "<h1>News</h1>"], None
    for post in posts:
        if post["year"] != year:
            if year is not None:
                out.append("</div></section>")
            year = post["year"]
            out.append(f'<section class="year"><h2>{year}</h2><div class="year-posts">')
        out.append(news_post(post))
    out.append("</div></section></div>")
    page("news.html", "News", "\n".join(out))


# ---------- People ----------

def initials(name):
    words = [w for w in re.sub(r",.*", "", name).split() if w[0].isalpha()]
    return (words[0][0] + words[-1][0]).upper()


def portrait(person):
    if person.get("photo"):
        return f'<img src="{img(person["photo"], 500)}" alt="{html.escape(person["name"])}" loading="lazy">'
    return f'<div class="no-photo" aria-hidden="true">{initials(person["name"])}</div>'


def person_card(person, default_role=""):
    lines = [f'<li class="person">', portrait(person), f'<h3>{html.escape(person["name"])}</h3>']
    role = person.get("role", default_role)
    if role:
        lines.append(f'<p>{html.escape(role)}</p>')
    for key in ("degree", "detail", "pronouns"):
        if person.get(key):
            lines.append(f'<p class="quiet">{html.escape(person[key])}</p>')
    if person.get("email"):
        lines.append(f'<p class="quiet"><a href="mailto:{person["email"]}">{person["email"]}</a></p>')
    lines.append("</li>")
    return "\n".join(lines)


def build_people():
    data = json.loads((CONTENT / "people.json").read_text(encoding="utf-8"))
    pi = data["pi"]
    out = ['<div class="wrap">', "<h1>People</h1>",
           '<section class="pi">',
           f'<a href="{pi["link"]}">{portrait(pi)}</a>',
           "<div>",
           f'<h2><a href="{pi["link"]}">{html.escape(pi["name"])}</a></h2>',
           f'<p>{html.escape(pi["role"])}</p>',
           f'<p class="quiet">{html.escape(pi["pronouns"])}</p>',
           f'<p><a href="mailto:{pi["email"]}">{pi["email"]}</a></p>',
           "</div></section>"]
    groups = [("Graduate Students", "graduate", "Graduate Student", "people"),
              ("Undergraduate Researchers", "undergraduate", "Undergraduate Researcher", "people"),
              ("Lab Alumni", "alumni", "", "people alumni")]
    for heading, key, role, cls in groups:
        anchor = ' id="alumni"' if key == "alumni" else ""
        out.append(f"<section{anchor}><h2>{heading}</h2><ul class=\"{cls}\">")
        out += [person_card(p, role) for p in data[key]]
        out.append("</ul></section>")
    out.append("</div>")
    page("people.html", "People", "\n".join(out))


# ---------- Publications ----------

def load_publications():
    text = (CONTENT / "publications.md").read_text(encoding="utf-8")
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def build_publications(pubs):
    items = "\n".join(f"<li>{inline(p)}</li>" for p in pubs)
    body = f"""<div class="wrap">
<h1>Publications</h1>
<ol class="pubs" reversed>
{items}
</ol>
<p><a href="http://scholar.google.com/citations?user=TLvHrmUAAAAJ&amp;hl=en&amp;oi=ao">View the full publication list on Google Scholar</a></p>
</div>"""
    page("publications.html", "Publications", body)


# ---------- Home ----------

def build_home(posts, pubs):
    latest = "\n".join(news_post(p) for p in posts[:3])
    highlighted = ["Pyk2 scaffolding relieves Src autoinhibition",
                   "Molecularly imprinted nanoparticles reveal",
                   "Activation loop phosphorylation tunes",
                   "Controlling kinase activities by selective protection"]
    chosen = [next(p for p in pubs if key in p) for key in highlighted]
    highlights = "\n".join(f"<li>{inline(p)}</li>" for p in chosen)
    gallery = [
        ("1619112768846-AT1MVWM629SZBS2MZL9K/IMG_20190926_175013070_HDR_2.jpg", "Iowa State University campus", ""),
        ("1485121448955-PYBTHIZFRJE0ECHU34HR/IMAG0291.jpg", "Molecular Biology Building", "Molecular Biology Building"),
        ("1485121449088-N683AHISA7K556SPQ3TV/IMAG02901.jpg", "Mural of chemistry by Grant Wood", "Chemistry as envisioned by Grant Wood"),
        ("1705677192992-OT6Q6YVZ3982TZO0PUVH/MBB_south_2013.jpg", "South side of the Molecular Biology Building", ""),
    ]
    figs = "\n".join(
        f'<figure><img src="{img(src)}" alt="{alt}" loading="lazy">'
        + (f"<figcaption>{cap}</figcaption>" if cap else "") + "</figure>"
        for src, alt, cap in gallery
    )
    body = f"""<section class="hero">
  <div class="wrap hero-inner">
    <h1>Welcome to the Underbakke Lab!</h1>
    <p>We are located in the Roy J. Carver Department of Biochemistry, Biophysics &amp; Molecular Biology at Iowa State University.</p>
    <p><a class="button" href="research.html">Read about our research</a></p>
  </div>
</section>
<div class="wrap">
  <figure class="pano">
    <img src="{img('1619112740203-QGFKDQQV8G2Q6REDWTQZ/PANO_20200829_124351.vr.jpg', 1500)}" alt="Panorama of the Underbakke Lab">
    <figcaption>Underbakke Lab</figcaption>
  </figure>
  <div class="home-cols">
    <section>
      <h2>Latest news</h2>
      {latest}
      <p><a href="news.html">All news</a></p>
    </section>
    <section>
      <h2>Highlighted publications</h2>
      <ul class="pubs plain">
      {highlights}
      </ul>
      <p><a href="publications.html">All publications</a></p>
    </section>
  </div>
  <section class="gallery" aria-label="Around campus">
  {figs}
  </section>
</div>"""
    page("index.html", "Home", body)


# ---------- Plain pages ----------

def build_plain(filename, title, current=None):
    fragment = (CONTENT / filename).read_text(encoding="utf-8").replace("{{CDN}}", CDN)
    page(filename, title, f'<div class="wrap prose">\n{fragment}\n</div>', current=current)


def main():
    OUT.mkdir(exist_ok=True)
    posts, pubs = load_news(), load_publications()
    build_home(posts, pubs)
    build_news(posts)
    build_people()
    build_publications(pubs)
    build_plain("research.html", "Research")
    build_plain("techniques.html", "HDX-MS", current="research.html")
    build_plain("resources.html", "Resources")
    build_plain("contact.html", "Contact")
    build_plain("eric-underbakke.html", "Eric Underbakke", current="people.html")
    (OUT / ".nojekyll").write_text("")
    print(f"Built {len(list(OUT.glob('*.html')))} pages: {len(posts)} news posts, {len(pubs)} publications")


if __name__ == "__main__":
    main()
