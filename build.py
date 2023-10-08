from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Union, Dict
import toml
import datetime
from string import Template
from pytz import timezone
import subprocess
import shutil

import mistletoe
from mistletoe.contrib.pygments_renderer import PygmentsRenderer
import yaml

TEMPLATES_DIR = Path(__file__).parent / "templates"
POSTS_DIR = Path(__file__).parent / "posts"
PUBS_DIR = Path(__file__).parent / "publications"
STATIC_DIR = Path(__file__).parent / "static"
THIRDPARTY_DIR = Path(__file__).parent / "thirdparty"
STYLE_DIR = Path(__file__).parent / "style"
TALKS_DIR = Path(__file__).parent / "talks"

OUTPUT_DIR = Path(__file__).parent / "public"

PYGMENTS_STYLE = "default"

# height/width set in CSS
EMAIL_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M64 112c-8.8 0-16 7.2-16 16v22.1L220.5 291.7c20.7 17 50.4 17 71.1 0L464 150.1V128c0-8.8-7.2-16-16-16H64zM48 212.2V384c0 8.8 7.2 16 16 16H448c8.8 0 16-7.2 16-16V212.2L322 328.8c-38.4 31.5-93.7 31.5-132 0L48 212.2zM0 128C0 92.7 28.7 64 64 64H448c35.3 0 64 28.7 64 64V384c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V128z"/></svg>'
GITHUB_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 496 512"><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M165.9 397.4c0 2-2.3 3.6-5.2 3.6-3.3.3-5.6-1.3-5.6-3.6 0-2 2.3-3.6 5.2-3.6 3-.3 5.6 1.3 5.6 3.6zm-31.1-4.5c-.7 2 1.3 4.3 4.3 4.9 2.6 1 5.6 0 6.2-2s-1.3-4.3-4.3-5.2c-2.6-.7-5.5.3-6.2 2.3zm44.2-1.7c-2.9.7-4.9 2.6-4.6 4.9.3 2 2.9 3.3 5.9 2.6 2.9-.7 4.9-2.6 4.6-4.6-.3-1.9-3-3.2-5.9-2.9zM244.8 8C106.1 8 0 113.3 0 252c0 110.9 69.8 205.8 169.5 239.2 12.8 2.3 17.3-5.6 17.3-12.1 0-6.2-.3-40.4-.3-61.4 0 0-70 15-84.7-29.8 0 0-11.4-29.1-27.8-36.6 0 0-22.9-15.7 1.6-15.4 0 0 24.9 2 38.6 25.8 21.9 38.6 58.6 27.5 72.9 20.9 2.3-16 8.8-27.1 16-33.7-55.9-6.2-112.3-14.3-112.3-110.5 0-27.5 7.6-41.3 23.6-58.9-2.6-6.5-11.1-33.3 2.6-67.9 20.9-6.5 69 27 69 27 20-5.6 41.5-8.5 62.8-8.5s42.8 2.9 62.8 8.5c0 0 48.1-33.6 69-27 13.7 34.7 5.2 61.4 2.6 67.9 16 17.7 25.8 31.5 25.8 58.9 0 96.5-58.9 104.2-114.8 110.5 9.2 7.9 17 22.9 17 46.4 0 33.7-.3 75.4-.3 83.6 0 6.5 4.6 14.4 17.3 12.1C428.2 457.8 496 362.9 496 252 496 113.3 383.5 8 244.8 8zM97.2 352.9c-1.3 1-1 3.3.7 5.2 1.6 1.6 3.9 2.3 5.2 1 1.3-1 1-3.3-.7-5.2-1.6-1.6-3.9-2.3-5.2-1zm-10.8-8.1c-.7 1.3.3 2.9 2.3 3.9 1.6 1 3.6.7 4.3-.7.7-1.3-.3-2.9-2.3-3.9-2-.6-3.6-.3-4.3.7zm32.4 35.6c-1.6 1.3-1 4.3 1.3 6.2 2.3 2.3 5.2 2.6 6.5 1 1.3-1.3.7-4.3-1.3-6.2-2.2-2.3-5.2-2.6-6.5-1zm-11.4-14.7c-1.6 1-1.6 3.6 0 5.9 1.6 2.3 4.3 3.3 5.6 2.3 1.6-1.3 1.6-3.9 0-6.2-1.4-2.3-4-3.3-5.6-2z"/></svg>'
LINKEDIN_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M416 32H31.9C14.3 32 0 46.5 0 64.3v383.4C0 465.5 14.3 480 31.9 480H416c17.6 0 32-14.5 32-32.3V64.3c0-17.8-14.4-32.3-32-32.3zM135.4 416H69V202.2h66.5V416zm-33.2-243c-21.3 0-38.5-17.3-38.5-38.5S80.9 96 102.2 96c21.2 0 38.5 17.3 38.5 38.5 0 21.3-17.2 38.5-38.5 38.5zm282.1 243h-66.4V312c0-24.8-.5-56.7-34.5-56.7-34.6 0-39.9 27-39.9 54.9V416h-66.4V202.2h63.7v29.2h.9c8.9-16.8 30.6-34.5 62.9-34.5 67.2 0 79.7 44.3 79.7 101.9V416z"/></svg>'
SCHOALR_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M243.4 2.6l-224 96c-14 6-21.8 21-18.7 35.8S16.8 160 32 160v8c0 13.3 10.7 24 24 24H456c13.3 0 24-10.7 24-24v-8c15.2 0 28.3-10.7 31.3-25.6s-4.8-29.9-18.7-35.8l-224-96c-8-3.4-17.2-3.4-25.2 0zM128 224H64V420.3c-.6 .3-1.2 .7-1.8 1.1l-48 32c-11.7 7.8-17 22.4-12.9 35.9S17.9 512 32 512H480c14.1 0 26.5-9.2 30.6-22.7s-1.1-28.1-12.9-35.9l-48-32c-.6-.4-1.2-.7-1.8-1.1V224H384V416H344V224H280V416H232V224H168V416H128V224zM256 64a32 32 0 1 1 0 64 32 32 0 1 1 0-64z"/></svg>'


@dataclass
class PostSpec:
    markdown_path: Path
    is_dir: bool
    output_dir: str
    gallery_resources: List[Path] = field(
        default_factory=list
    )  # paths to files in gallery subdirectory
    resources: List[Path] = field(
        default_factory=list
    )  # paths to other things in the post directory


@dataclass
class Post:
    spec: PostSpec
    title: str
    body_html: str
    create_time: datetime.datetime = None
    mod_time: datetime.datetime = create_time


@dataclass
class PubSpec:
    markdown_path: Path
    is_dir: bool
    output_dir: str


@dataclass
class Pub:
    spec: PubSpec
    title: str
    body_html: str
    create_time: datetime.datetime = None
    mod_time: datetime.datetime = create_time
    authors: List[str] = field(default_factory=list)
    venue: str = ""


@dataclass
class TalkSpec:
    markdown_path: Path
    is_dir: bool
    output_dir: str


@dataclass
class Talk:
    spec: TalkSpec
    title: str
    body_html: str
    create_time: datetime.datetime = None
    mod_time: datetime.datetime = create_time
    authors: List[str] = field(default_factory=list)
    venue: str = ""


def find_posts() -> List[PostSpec]:
    specs = []

    for post in POSTS_DIR.iterdir():
        output_dir = Path("post") / f"{post.stem}"
        if post.is_file():
            specs += [PostSpec(markdown_path=post, is_dir=False, output_dir=output_dir)]
        elif post.is_dir():
            md_path = post / "index.md"
            if md_path.is_file():
                gallery_path = post / "gallery"

                if gallery_path.is_dir():
                    gallery_resources = list(gallery_path.iterdir())
                else:
                    gallery_resources = []
                resources = [
                    x
                    for x in post.iterdir()
                    if x.name != "gallery" and x.name != "index.md"
                ]
                specs += [
                    PostSpec(
                        markdown_path=md_path,
                        is_dir=True,
                        output_dir=output_dir,
                        gallery_resources=gallery_resources,
                        resources=resources,
                    )
                ]

    return specs


def read_markdown(path: Path) -> Tuple[Dict, str]:
    """
    assume +++ delimits toml frontmatter, and --- delimits yaml frontmatter

    returns frontmater dict, markdown
    """

    toml_delims = []
    yaml_delims = []

    lines = []
    with open(path, "r") as f:
        lines = [line for line in f]

    delims = []
    for li, line in enumerate(lines):
        if line.strip() == "+++":
            toml_delims += [li]
        elif line.strip() == "---":
            yaml_delims += [li]

    # there's a header if the delimiter is found at least twice and the file starts with it
    if len(toml_delims) >= 2 and toml_delims[0] == 0:
        toml_lines = lines[1 : toml_delims[1]]
        md_lines = lines[toml_delims[1] + 1 :]
        return toml.loads("".join(toml_lines)), "".join(md_lines)
    elif len(yaml_delims) >= 2 and yaml_delims[0] == 0:
        yaml_lines = lines[1 : yaml_delims[1]]
        md_lines = lines[yaml_delims[1] + 1 :]
        return yaml.load("".join(yaml_lines), Loader=yaml.CLoader), "".join(md_lines)
    else:
        return {}, "".join(lines)


def maybe_localize_to_mountain(dt: datetime.datetime) -> datetime.datetime:
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        mountain = timezone("US/Mountain")
        return mountain.localize(dt)
    else:
        return dt


def render_post(spec: PostSpec) -> Post:
    print(f"==== render {spec.markdown_path}")
    frontmatter, markdown = read_markdown(spec.markdown_path)

    draft = frontmatter.get("draft", False)
    if draft:
        return None
    title = frontmatter["title"]
    create_time = frontmatter["date"]
    create_time = maybe_localize_to_mountain(create_time)
    mod_time = frontmatter.get("lastmod", create_time)
    mod_time = maybe_localize_to_mountain(mod_time)

    body_html = ""
    body_html += f"<h1>{title}</h1>\n"
    with PygmentsRenderer(style=PYGMENTS_STYLE) as renderer:
        body_html += renderer.render(mistletoe.Document(markdown))

    return Post(
        spec=spec,
        title=title,
        body_html=body_html,
        create_time=create_time,
        mod_time=mod_time,
    )


def output_post(post: Post):
    with open(TEMPLATES_DIR / "post.tmpl", "r") as f:
        tmpl = Template(f.read())

    html = tmpl.safe_substitute(
        {
            "style_frag": navbar_css() + common_css() + footer_css(),
            "head_frag": head_frag(),
            "nav_frag": nav_frag(),
            "body_frag": post.body_html,
            "footer_frag": footer_frag(),
        }
    )
    output_dir = OUTPUT_DIR / post.spec.output_dir
    print(f"==== output {post.spec.markdown_path} -> {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "index.html", "w") as f:
        f.write(html)


def find_pubs() -> List[PubSpec]:
    specs = []

    for pub in PUBS_DIR.iterdir():
        output_dir = Path("publication") / f"{pub.stem}"
        if pub.is_file():
            specs += [PubSpec(markdown_path=pub, is_dir=False, output_dir=output_dir)]
        elif pub.is_dir():
            md_path = pub / "index.md"
            if md_path.is_file():
                specs += [
                    PubSpec(
                        markdown_path=md_path,
                        is_dir=True,
                        output_dir=output_dir,
                    )
                ]

    return specs


def normalize_to_datetime(o) -> datetime.datetime:
    if isinstance(o, datetime.date):
        return datetime.datetime.combine(o, datetime.datetime.min.time())  # midnight
    elif isinstance(o, datetime.datetime):
        return o
    else:
        raise RuntimeError(type(o))


def render_pub(spec: PubSpec) -> Pub:
    print(f"==== render {spec.markdown_path}")
    frontmatter, markdown = read_markdown(spec.markdown_path)

    title = frontmatter["title"]
    create_time = frontmatter["date"]
    create_time = normalize_to_datetime(create_time)
    create_time = maybe_localize_to_mountain(create_time)
    mod_time = frontmatter.get("lastmod", create_time)
    mod_time = maybe_localize_to_mountain(mod_time)

    body_html = ""
    body_html += f"<h1>{title}</h1>\n"
    with PygmentsRenderer(style=PYGMENTS_STYLE) as renderer:
        body_html += renderer.render(mistletoe.Document(markdown))

    return Pub(
        spec=spec,
        title=title,
        body_html=body_html,
        create_time=create_time,
        mod_time=mod_time,
        venue=frontmatter.get("venue", ""),
        authors=frontmatter.get("authors", []),
    )


def find_talks() -> List[TalkSpec]:
    specs = []

    for talk in TALKS_DIR.iterdir():
        output_dir = Path("talk") / f"{talk.stem}"
        if talk.is_file():
            specs += [TalkSpec(markdown_path=talk, is_dir=False, output_dir=output_dir)]
        elif talk.is_dir():
            md_path = talk / "index.md"
            if md_path.is_file():
                specs += [
                    TalkSpec(
                        markdown_path=md_path,
                        is_dir=True,
                        output_dir=output_dir,
                    )
                ]

    return specs


def render_talk(spec: TalkSpec) -> Pub:
    print(f"==== render {spec.markdown_path}")
    frontmatter, markdown = read_markdown(spec.markdown_path)

    title = frontmatter["title"]
    create_time = frontmatter["date"]
    create_time = normalize_to_datetime(create_time)
    create_time = maybe_localize_to_mountain(create_time)
    mod_time = frontmatter.get("lastmod", create_time)
    mod_time = maybe_localize_to_mountain(mod_time)

    body_html = ""
    body_html += f"<h1>{title}</h1>\n"
    with PygmentsRenderer(style=PYGMENTS_STYLE) as renderer:
        body_html += renderer.render(mistletoe.Document(markdown))

    return Talk(
        spec=spec,
        title=title,
        body_html=body_html,
        create_time=create_time,
        mod_time=mod_time,
        venue=frontmatter.get("venue", ""),
        authors=frontmatter.get("authors", []),
    )


def output_talk(talk: Talk):
    with open(TEMPLATES_DIR / "talk.tmpl", "r") as f:
        tmpl = Template(f.read())

    html = tmpl.safe_substitute(
        {
            "style_frag": navbar_css() + common_css() + footer_css(),
            "head_frag": head_frag(),
            "nav_frag": nav_frag(),
            "body_frag": talk.body_html,
            "footer_frag": footer_frag(),
        }
    )
    output_dir = OUTPUT_DIR / talk.spec.output_dir
    print(f"==== output {talk.spec.markdown_path} -> {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "index.html", "w") as f:
        f.write(html)


def nav_frag() -> str:
    with open(TEMPLATES_DIR / "navbar_frag.html") as f:
        return f.read()


def navbar_css() -> str:
    with open(STYLE_DIR / "navbar.css") as f:
        return f.read() + "\n"


def common_css() -> str:
    with open(STYLE_DIR / "common.css") as f:
        return f.read() + "\n"


def footer_css() -> str:
    with open(STYLE_DIR / "footer.css") as f:
        return f.read() + "\n"


def index_css() -> str:
    with open(STYLE_DIR / "index.css") as f:
        return f.read() + "\n"


def copy_static():
    src = STATIC_DIR
    dst = OUTPUT_DIR / "static"
    print(f"==== {src} -> {dst}")
    shutil.copytree(src, dst, dirs_exist_ok=True)


def copy_thirdparty():
    src = THIRDPARTY_DIR
    dst = OUTPUT_DIR / "thirdparty"
    print(f"==== {src} -> {dst}")
    shutil.copytree(src, dst, dirs_exist_ok=True)


SHA = None


def footer_frag() -> str:
    global SHA
    global DIRTY
    now_str = datetime.datetime.now().strftime("%x")
    if SHA is None:
        cp = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True
        )
        SHA = cp.stdout.decode("utf-8").strip()
    html = '<div class="footer">\n'
    html += "<hr \>\n"
    html += f"<div>build {SHA} on {now_str}</div>\n"
    html += (
        f'<div>copyright Carl Pearson {datetime.datetime.now().strftime("%Y")}</div>\n'
    )
    html += "</div>\n"
    return html


def head_frag(title: str = "", descr: str = "", keywords: List[str] = []) -> str:
    html = ""
    html += '<meta name="viewport" content="width=device-width">\n'
    if title:
        html += f"<title>{title}</title>\n"
    html += '<meta name="generator" content="github.com/cwpearson/website2">\n'
    html += '<meta name="author" content="Carl Pearson">\n'
    if descr:
        html += f'<meta name="keywords" content="{descr}">\n'
    if keywords:
        html += f'<meta name="keywords" content="{"".join(keywords)}">\n'

    with open(TEMPLATES_DIR / "katex_frag.html") as f:
        html += f.read() + "\n"

    return html


def output_pub(pub: Pub):
    with open(TEMPLATES_DIR / "pub.tmpl", "r") as f:
        tmpl = Template(f.read())

    html = tmpl.safe_substitute(
        {
            "style_frag": navbar_css() + common_css() + footer_css(),
            "head_frag": head_frag(),
            "nav_frag": nav_frag(),
            "body_frag": pub.body_html,
            "footer_frag": footer_frag(),
        }
    )
    output_dir = OUTPUT_DIR / pub.spec.output_dir
    print(f"==== output {pub.spec.markdown_path} -> {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "index.html", "w") as f:
        f.write(html)


def render_index(top_k_posts: List[Post], top_k_pubs: List[Pub]) -> str:
    with open(TEMPLATES_DIR / "index.tmpl") as f:
        tmpl = Template(f.read())

    frontmatter, _ = read_markdown("index.md")
    bio = frontmatter["bio"]

    top_k_posts_frag = ""
    for post in top_k_posts:
        top_k_posts_frag += post_card(post)

    # fake "Post" that just links to all posts
    top_k_posts_frag += post_card(
        Post(
            spec=PostSpec(markdown_path=None, is_dir=None, output_dir=Path("posts")),
            title="...",
            body_html=None,
        )
    )

    top_k_pubs_frag = ""
    for pub in top_k_pubs:
        top_k_pubs_frag += pub_card(pub)
    top_k_pubs_frag += pub_card(
        Pub(
            spec=PubSpec(
                markdown_path=None, is_dir=None, output_dir=Path("publications")
            ),
            title="...",
            body_html=None,
        )
    )

    return tmpl.safe_substitute(
        {
            "style_frag": navbar_css() + common_css() + index_css() + footer_css(),
            "head_frag": head_frag(
                title="Carl Pearson",
                descr="Personal site for Carl pearson",
            ),
            "nav_frag": nav_frag(),
            "bio_text": bio,
            "email_svg": EMAIL_SVG,
            "linkedin_svg": LINKEDIN_SVG,
            "github_svg": GITHUB_SVG,
            "scholar_svg": SCHOALR_SVG,
            "top_k_posts_frag": top_k_posts_frag,
            "top_k_pubs_frag": top_k_pubs_frag,
            "footer_frag": footer_frag(),
        }
    )


def output_index(html):
    output_path = OUTPUT_DIR / "index.html"
    print(f"==== write {output_path}")
    with open(output_path, "w") as f:
        f.write(html)


def render_experience() -> str:
    with open(TEMPLATES_DIR / "experience.tmpl") as f:
        tmpl = Template(f.read())

    frontmatter, md_str = read_markdown("experience.md")
    title = frontmatter["title"]
    descr = frontmatter["description"]

    body_frag = mistletoe.markdown(md_str)

    return tmpl.safe_substitute(
        {
            "style_frag": navbar_css() + common_css() + index_css() + footer_css(),
            "head_frag": head_frag(title=title, descr=descr),
            "nav_frag": nav_frag(),
            "title": title,
            "body_frag": body_frag,
            "footer_frag": footer_frag(),
        }
    )


def render_recognition() -> str:
    with open(TEMPLATES_DIR / "recognition.tmpl") as f:
        tmpl = Template(f.read())

    frontmatter, md_str = read_markdown("recognition.md")

    body_frag = mistletoe.markdown(md_str)
    title = frontmatter["title"]
    descr = frontmatter["description"]

    return tmpl.safe_substitute(
        {
            "style_frag": navbar_css() + common_css() + index_css() + footer_css(),
            "head_frag": head_frag(title=title, descr=descr),
            "nav_frag": nav_frag(),
            "title": title,
            "body_frag": body_frag,
            "footer_frag": footer_frag(),
        }
    )


def output_html(prefix, html):
    output_path = OUTPUT_DIR / prefix / "index.html"
    output_path.parent.mkdir(exist_ok=True, parents=True)
    print(f"==== write {output_path}")
    with open(output_path, "w") as f:
        f.write(html)


def authors_span(authors: List[str]) -> str:
    html = ""
    for i, author in enumerate(authors):
        if author == "Carl Pearson" or author == "Pearson, Carl":
            html += f"<strong>{author}</strong>"
        else:
            html += author
        if i + 1 < len(authors):
            html += ", "
    return html


def pub_card(pub: Pub) -> str:
    """
    return an html fragment for a Pub
    """

    if pub.create_time:
        mmyy = pub.create_time.strftime("%m/%y")
    else:
        mmyy = ""

    html = ""
    html += f'<a href="/{pub.spec.output_dir}" class="no-decoration">\n'
    html += f'<div class="pub-card">\n'
    html += '<div class="pub-ref">\n'
    html += f'<div class="pub-title">{pub.title}</div>\n'

    html += "<div>\n"
    if pub.authors:
        html += f'<div class="pub-authors">{authors_span(pub.authors)}</div>\n'
    if pub.venue:
        _in = "in "
        if pub.venue.lower() == "arxiv":
            _in = ""
        elif pub.venue.lower() == "tech report":
            _in = ""
        elif "thesis" in pub.venue.lower():
            _in = ""
        html += f'<div class="pub-venue-wrapper">{_in}<div class="pub-venue">{pub.venue}</div></div>\n'
    html += "</div>\n"

    html += "</div>\n"  # pub-ref

    html += f'<div class="pub-date">{mmyy}</div>\n'

    html += "</div>\n"  # pub-card
    html += "</a>\n"
    return html


def render_publications(pubs: List[Pub]) -> str:
    with open(TEMPLATES_DIR / "publications.tmpl") as f:
        tmpl = Template(f.read())

    pub_links = ""
    for pub in sorted(pubs, key=lambda x: x.create_time, reverse=True):
        # pub_links += f'<li><a href="/{pub.spec.output_dir}/">{pub.title}</a></li>\n'
        pub_links += pub_card(pub)

    return tmpl.safe_substitute(
        {
            "style_frag": navbar_css() + common_css() + footer_css(),
            "head_frag": head_frag(),
            "nav_frag": nav_frag(),
            "body_frag": pub_links,
            "footer_frag": footer_frag(),
        }
    )


def output_publications(html):
    output_path = OUTPUT_DIR / "publications" / "index.html"
    output_path.parent.mkdir(exist_ok=True, parents=True)
    print(f"==== write {output_path}")
    with open(output_path, "w") as f:
        f.write(html)


def post_card(post: Post) -> str:
    """
    return an html fragment for a post
    """

    if post.create_time:
        mmddyy = post.create_time.strftime("%m/%d/%y")
    else:
        mmddyy = ""

    html = ""
    html += f'<a href="/{post.spec.output_dir}" class="no-decoration">\n'
    html += f'<div class="post-card">\n'
    html += f'<div class="post-title">{post.title}</div>\n'
    html += f'<div class="post-date">{mmddyy}</div>\n'
    html += "</div>\n"
    html += "</a>\n"
    return html


def render_posts(posts: List[Post]) -> str:
    with open(TEMPLATES_DIR / "posts.tmpl") as f:
        tmpl = Template(f.read())

    post_links = ""
    for post in sorted(posts, key=lambda x: x.create_time, reverse=True):
        post_links += post_card(post)

    return tmpl.safe_substitute(
        {
            "style_frag": navbar_css() + common_css() + footer_css(),
            "head_frag": head_frag(),
            "nav_frag": nav_frag(),
            "body_frag": post_links,
            "footer_frag": footer_frag(),
        }
    )


def talk_card(talk: Talk) -> str:
    """
    return an html fragment for a Talk
    """

    mmddyy = talk.create_time.strftime("%m/%d/%y")

    html = ""
    html += f'<a href="/{talk.spec.output_dir}" class="no-decoration">\n'
    html += f'<div class="pub-card">\n'
    html += '<div class="pub-ref">\n'
    html += f'<div class="pub-title">{talk.title}</div>\n'

    html += "<div>\n"
    if talk.authors:
        html += f'<div class="pub-authors">{authors_span(talk.authors)}</div>\n'
    if talk.venue:
        _in = "in "
        if talk.venue.lower() == "arxiv":
            _in = ""
        elif talk.venue.lower() == "tech report":
            _in = ""
        elif "thesis" in talk.venue.lower():
            _in = ""
        html += f'<div class="pub-venue-wrapper">{_in}<div class="pub-venue">{talk.venue}</div></div>\n'
    html += "</div>\n"

    html += "</div>\n"  # pub-ref

    html += f'<div class="pub-date">{mmddyy}</div>\n'

    html += "</div>\n"  # pub-card
    html += "</a>\n"
    return html


def render_talks(talks: List[Talk]) -> str:
    with open(TEMPLATES_DIR / "talks.tmpl") as f:
        tmpl = Template(f.read())

    talk_links = ""
    for talk in sorted(talks, key=lambda x: x.create_time, reverse=True):
        talk_links += talk_card(talk)

    return tmpl.safe_substitute(
        {
            "style_frag": navbar_css() + common_css() + footer_css(),
            "head_frag": head_frag(),
            "nav_frag": nav_frag(),
            "body_frag": talk_links,
            "footer_frag": footer_frag(),
        }
    )


if __name__ == "__main__":
    post_specs = find_posts()
    for ps in post_specs:
        print(ps)
    posts = [render_post(spec) for spec in post_specs]
    posts = [p for p in posts if p is not None]
    for post in posts:
        output_post(post)

    pub_specs = find_pubs()
    for spec in pub_specs:
        print(spec)
    pubs = [render_pub(spec) for spec in pub_specs]
    pubs = [p for p in pubs if p is not None]
    for pub in pubs:
        output_pub(pub)

    talk_specs = find_talks()
    for spec in talk_specs:
        print(spec)
    talks = [render_talk(spec) for spec in talk_specs]
    talks = [t for t in talks if t is not None]
    for talk in talks:
        output_talk(talk)

    index_html = render_index(
        top_k_posts=sorted(posts, key=lambda p: p.create_time, reverse=True)[0:5],
        top_k_pubs=sorted(pubs, key=lambda p: p.create_time, reverse=True)[0:5],
    )
    output_index(index_html)

    publications_html = render_publications(pubs)
    output_html("publications", publications_html)

    posts_html = render_posts(posts)
    output_html("posts", posts_html)

    talks_html = render_talks(talks)
    output_html("talks", talks_html)

    experience_html = render_experience()
    output_html("experience", experience_html)

    recognition_html = render_recognition()
    output_html("recognition", recognition_html)

    copy_static()
    copy_thirdparty()
