from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Union, Dict
import toml
import time
import datetime
from string import Template
from pytz import timezone
import subprocess
import shutil
from functools import lru_cache
import gzip
import re

import mistletoe
from mistletoe.contrib.pygments_renderer import PygmentsRenderer
import yaml
from PIL import Image

BYTES_RD = 0
BYTES_WR = 0

TCP_SLOW_START = 14600
LARGE_PAGES = []
SMALL_PAGES = 0

ROOT_DIR = Path(__file__).parent
CONTENT_DIR = ROOT_DIR / "content"
TEMPLATES_DIR = ROOT_DIR / "templates"
POSTS_DIR = ROOT_DIR / "posts"
PUBS_DIR = ROOT_DIR / "publications"
STATIC_DIR = ROOT_DIR / "static"
THIRDPARTY_DIR = ROOT_DIR / "thirdparty"
STYLE_DIR = ROOT_DIR / "style"
TALKS_DIR = ROOT_DIR / "talks"

OUTPUT_DIR = ROOT_DIR / "public"

PYGMENTS_STYLE = "default"

# height/width set in CSS
EMAIL_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M64 112c-8.8 0-16 7.2-16 16v22.1L220.5 291.7c20.7 17 50.4 17 71.1 0L464 150.1V128c0-8.8-7.2-16-16-16H64zM48 212.2V384c0 8.8 7.2 16 16 16H448c8.8 0 16-7.2 16-16V212.2L322 328.8c-38.4 31.5-93.7 31.5-132 0L48 212.2zM0 128C0 92.7 28.7 64 64 64H448c35.3 0 64 28.7 64 64V384c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V128z"/></svg>'
GITHUB_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 496 512"><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M165.9 397.4c0 2-2.3 3.6-5.2 3.6-3.3.3-5.6-1.3-5.6-3.6 0-2 2.3-3.6 5.2-3.6 3-.3 5.6 1.3 5.6 3.6zm-31.1-4.5c-.7 2 1.3 4.3 4.3 4.9 2.6 1 5.6 0 6.2-2s-1.3-4.3-4.3-5.2c-2.6-.7-5.5.3-6.2 2.3zm44.2-1.7c-2.9.7-4.9 2.6-4.6 4.9.3 2 2.9 3.3 5.9 2.6 2.9-.7 4.9-2.6 4.6-4.6-.3-1.9-3-3.2-5.9-2.9zM244.8 8C106.1 8 0 113.3 0 252c0 110.9 69.8 205.8 169.5 239.2 12.8 2.3 17.3-5.6 17.3-12.1 0-6.2-.3-40.4-.3-61.4 0 0-70 15-84.7-29.8 0 0-11.4-29.1-27.8-36.6 0 0-22.9-15.7 1.6-15.4 0 0 24.9 2 38.6 25.8 21.9 38.6 58.6 27.5 72.9 20.9 2.3-16 8.8-27.1 16-33.7-55.9-6.2-112.3-14.3-112.3-110.5 0-27.5 7.6-41.3 23.6-58.9-2.6-6.5-11.1-33.3 2.6-67.9 20.9-6.5 69 27 69 27 20-5.6 41.5-8.5 62.8-8.5s42.8 2.9 62.8 8.5c0 0 48.1-33.6 69-27 13.7 34.7 5.2 61.4 2.6 67.9 16 17.7 25.8 31.5 25.8 58.9 0 96.5-58.9 104.2-114.8 110.5 9.2 7.9 17 22.9 17 46.4 0 33.7-.3 75.4-.3 83.6 0 6.5 4.6 14.4 17.3 12.1C428.2 457.8 496 362.9 496 252 496 113.3 383.5 8 244.8 8zM97.2 352.9c-1.3 1-1 3.3.7 5.2 1.6 1.6 3.9 2.3 5.2 1 1.3-1 1-3.3-.7-5.2-1.6-1.6-3.9-2.3-5.2-1zm-10.8-8.1c-.7 1.3.3 2.9 2.3 3.9 1.6 1 3.6.7 4.3-.7.7-1.3-.3-2.9-2.3-3.9-2-.6-3.6-.3-4.3.7zm32.4 35.6c-1.6 1.3-1 4.3 1.3 6.2 2.3 2.3 5.2 2.6 6.5 1 1.3-1.3.7-4.3-1.3-6.2-2.2-2.3-5.2-2.6-6.5-1zm-11.4-14.7c-1.6 1-1.6 3.6 0 5.9 1.6 2.3 4.3 3.3 5.6 2.3 1.6-1.3 1.6-3.9 0-6.2-1.4-2.3-4-3.3-5.6-2z"/></svg>'
LINKEDIN_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M416 32H31.9C14.3 32 0 46.5 0 64.3v383.4C0 465.5 14.3 480 31.9 480H416c17.6 0 32-14.5 32-32.3V64.3c0-17.8-14.4-32.3-32-32.3zM135.4 416H69V202.2h66.5V416zm-33.2-243c-21.3 0-38.5-17.3-38.5-38.5S80.9 96 102.2 96c21.2 0 38.5 17.3 38.5 38.5 0 21.3-17.2 38.5-38.5 38.5zm282.1 243h-66.4V312c0-24.8-.5-56.7-34.5-56.7-34.6 0-39.9 27-39.9 54.9V416h-66.4V202.2h63.7v29.2h.9c8.9-16.8 30.6-34.5 62.9-34.5 67.2 0 79.7 44.3 79.7 101.9V416z"/></svg>'
SCHOALR_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M243.4 2.6l-224 96c-14 6-21.8 21-18.7 35.8S16.8 160 32 160v8c0 13.3 10.7 24 24 24H456c13.3 0 24-10.7 24-24v-8c15.2 0 28.3-10.7 31.3-25.6s-4.8-29.9-18.7-35.8l-224-96c-8-3.4-17.2-3.4-25.2 0zM128 224H64V420.3c-.6 .3-1.2 .7-1.8 1.1l-48 32c-11.7 7.8-17 22.4-12.9 35.9S17.9 512 32 512H480c14.1 0 26.5-9.2 30.6-22.7s-1.1-28.1-12.9-35.9l-48-32c-.6-.4-1.2-.7-1.8-1.1V224H384V416H344V224H280V416H232V224H168V416H128V224zM256 64a32 32 0 1 1 0 64 32 32 0 1 1 0-64z"/></svg>'


@dataclass
class PostSpec:
    markdown_path: Path
    # path to the posts's directory, if there is one
    input_dir: Union[Path, None]
    output_dir: str
    resources: List[Path] = field(
        default_factory=list
    )  # paths to other things in the post directory


@dataclass
class GalleryItem:
    image: Path  # post/gallery/image is the path to the image
    caption: str
    full_path: Path = None  # full path to the image


@dataclass
class Post:
    spec: PostSpec
    title: str
    body_html: str
    create_time: datetime.datetime = None
    mod_time: datetime.datetime = create_time
    gallery_html: str = ""
    math: bool = False  # if post has math in it
    css: str = ""  # post-specific styling
    keywords: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    description: str = ""


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
    date: datetime.datetime = None
    authors_html: str = ""
    venue_html: str = ""
    abstract: str = ""
    url_pdf: List[str] = field(default_factory=list)
    url_code: List[str] = field(default_factory=list)
    url_slides: str = ""
    url_poster: str = ""
    url_video: str = ""
    description: str = ""
    keywords: List[str] = field(default_factory=list)


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
    time_start: datetime.datetime = None
    time_end: datetime.date = None
    authors_html: str = None
    how_invited: str = ""
    location: str = ""
    abstract: str = ""
    address: dict = field(default_factory=dict)
    event: str = ""
    event_url: str = None
    url_slides: str = None
    url_code: List[str] = field(default_factory=list)
    url_video: str = ""
    publication: str = None


@dataclass
class ProjectSpec:
    markdown_path: Path
    input_dir: Union[Path, None]
    output_dir: Path


@dataclass
class Project:
    spec: ProjectSpec
    title: str
    body_html: str
    tags: List[str]
    create_time: datetime.datetime = None


class Timer:
    def __init__(self):
        self.elapsed = None
        self.total = 0

    def start(self):
        self.elapsed = time.monotonic()

    def stop(self):
        if self.elapsed is not None:
            self.total += time.monotonic() - self.elapsed
            self.elapsed = None


TIMER = Timer()


def github_edit_url(src_rel: str) -> str:
    return f"https://github.com/cwpearson/website2/edit/master/{src_rel}"


def talk_page_location_div(loc: str) -> str:
    return f'<div class="location">{loc}</div>\n'


def talk_page_address_div(addr: Dict) -> str:
    return f'<div class="address"></div>\n'


def talk_page_time_div(start: datetime.datetime, end: datetime.datetime) -> str:
    html = ""
    if not start:
        return html
    html += f'<div class="time">\n'
    if isinstance(start, datetime.datetime):
        html += f"{start.strftime('%a %d %b %Y, %I:%M%p')}"
    elif isinstance(start, datetime.date):
        html += f"{start.strftime('%a %d %b %Y')}"
    if end and isinstance(end, datetime.datetime):
        html += f" - {end.strftime('%I:%M%p')}"
    html += "</div>\n"
    return html


def page_abstract_frag(abstract) -> str:
    html = ""
    html += '<div class="abstract">\n'
    html += '<span style="font-weight: bold;">Abstract: </span>\n'
    html += '<div class="abstract-text">\n'
    html += abstract
    html += "</div>\n"
    html += "</div>\n"
    return html


def gzipped_size(path) -> int:
    with open(path, "rb") as f:
        return len(gzip.compress(f.read()))


def file_size(path) -> int:
    sz = Path(path).stat().st_size
    return sz


def write_file(path, contents) -> int:
    global BYTES_WR
    global LARGE_PAGES
    global SMALL_PAGES
    with open(path, "w") as f:
        f.write(contents)
    TIMER.stop()
    BYTES_WR += file_size(path)
    if gzipped_size(path) > TCP_SLOW_START:
        LARGE_PAGES += [path]
    else:
        SMALL_PAGES += 1
    TIMER.start()


def dir_size(path) -> int:
    return sum(file.stat().st_size for file in Path(path).rglob("*"))


def favicons():
    im = Image.open(STATIC_DIR / "img" / "avatar.jpg")
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
    im.save(OUTPUT_DIR / "favicon.ico", sizes=[(x, x) for x in [16, 32, 64]])


def read_markdown(path: Path) -> Tuple[Dict, str]:
    """
    assume +++ delimits toml frontmatter, and --- delimits yaml frontmatter

    returns frontmater dict, markdown
    """
    global BYTES_RD

    toml_delims = []
    yaml_delims = []

    lines = []
    TIMER.stop()
    BYTES_RD += file_size(path)
    TIMER.start()
    with open(path, "r") as f:
        lines = [line for line in f]

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


def find_projects() -> List[ProjectSpec]:
    specs = []

    for project in (CONTENT_DIR / "projects").iterdir():
        if project.name == "index.md":
            continue
        output_dir = Path("project") / f"{project.stem}"
        if project.is_file():
            specs += [
                ProjectSpec(
                    markdown_path=project, input_dir=None, output_dir=output_dir
                )
            ]
        elif project.is_dir():
            md_path = project / "index.md"
            if md_path.is_file():
                specs += [
                    ProjectSpec(
                        markdown_path=md_path, input_dir=project, output_dir=output_dir
                    )
                ]

    return specs


def render_project(spec: ProjectSpec) -> Project:
    print(f"==== render {spec.markdown_path}")
    frontmatter, markdown = read_markdown(spec.markdown_path)

    draft = frontmatter.get("draft", False)
    if draft:
        return None
    title = frontmatter["title"]
    tags = frontmatter.get("tags", [])
    create_time = frontmatter["date"]
    create_time = maybe_localize_to_mountain(create_time)

    body_html = ""
    body_html += f"<h1>{title}</h1>\n"
    with PygmentsRenderer(style=PYGMENTS_STYLE) as renderer:
        body_html += renderer.render(mistletoe.Document(markdown))

    return Project(
        spec=spec,
        title=title,
        body_html=body_html,
        create_time=create_time,
        tags=tags,
    )


def output_project(project: Project):
    global BYTES_RD

    tmpl_path = TEMPLATES_DIR / "project.tmpl"
    TIMER.stop()
    BYTES_RD += file_size(tmpl_path)
    TIMER.start()
    with open(tmpl_path, "r") as f:
        tmpl = Template(f.read())

    html = tmpl.safe_substitute(
        {
            "style_frag": style("navbar.css")
            + style("common.css")
            + style("footer.css"),
            "head_frag": head_frag(),
            "nav_frag": nav_frag(),
            "body_frag": project.body_html,
            "footer_frag": footer_frag(
                edit_url=github_edit_url(
                    project.spec.markdown_path.relative_to(ROOT_DIR)
                )
            ),
        }
    )
    output_dir = OUTPUT_DIR / project.spec.output_dir
    print(f"==== output {project.spec.markdown_path} -> {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = output_dir / "index.html"
    write_file(html_path, html)


def project_card(project: Project) -> str:
    """
    return an html fragment for a Project
    """

    html = ""
    html += f'<a href="/{project.spec.output_dir}" class="no-decoration">\n'
    html += f'<div class="content-card">\n'
    html += '<div class="project-ref">\n'
    html += f'<div class="project-title">{project.title}</div>\n'
    html += "</div>\n"  # project-ref
    html += "</div>\n"  # content-card
    html += "</a>\n"
    return html


def render_projects_index(projects: List[Project]) -> str:
    global BYTES_RD
    tmpl_path = TEMPLATES_DIR / "projects.tmpl"
    TIMER.stop()
    BYTES_RD += file_size(tmpl_path)
    TIMER.start()
    with open(tmpl_path) as f:
        tmpl = Template(f.read())

    project_links = ""
    for project in sorted(projects, key=lambda x: x.create_time, reverse=True):
        project_links += project_card(project)

    return tmpl.safe_substitute(
        {
            "style_frag": style("navbar.css")
            + style("common.css")
            + style("footer.css"),
            "head_frag": head_frag(),
            "nav_frag": nav_frag(),
            "body_frag": project_links,
            "footer_frag": footer_frag(),
        }
    )


def find_posts() -> List[PostSpec]:
    specs = []

    for post in POSTS_DIR.iterdir():
        output_dir = Path("post") / f"{post.stem}"
        if post.is_file():
            specs += [
                PostSpec(markdown_path=post, input_dir=None, output_dir=output_dir)
            ]
        elif post.is_dir():
            md_path = post / "index.md"
            if md_path.is_file():
                resources = [
                    x.relative_to(post) for x in post.iterdir() if x.name != "index.md"
                ]
                specs += [
                    PostSpec(
                        markdown_path=md_path,
                        input_dir=post,
                        output_dir=output_dir,
                        resources=resources,
                    )
                ]

    return specs


def maybe_localize_to_mountain(dt: datetime.datetime) -> datetime.datetime:
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        mountain = timezone("US/Mountain")
        return mountain.localize(dt)
    else:
        return dt


def img(src, alt="", path=None) -> str:
    html = f'<img src="{src}"'
    if alt:
        html += f' alt="{alt}"'
    if path:
        global BYTES_RD
        TIMER.stop()
        BYTES_RD += file_size(path)
        TIMER.start()
        im = Image.open(path)
        w, h = im.size
        html += f' height="{h}" width="{w}"'

    html += ">"
    return html


def page_href(url: str, hint: str):
    if "arxiv.org" in url:
        return f'<a href="{url}">arxiv</a>\n'
    elif "github.com" in url:
        m = re.findall("github.com/([^/]+)/([^/]+)/?.*", url)
        return f'<a href="{url}">github/{m[0][0]}/{m[0][1]}</a>\n'
    return f'<a href="{url}">{hint}</a>\n'


def move_post_resources(spec: PostSpec):
    global BYTES_RD
    global BYTES_WR
    output_dir = OUTPUT_DIR / spec.output_dir
    print(f"==== post resources {spec.markdown_path} -> {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    for res in spec.resources:
        src = spec.input_dir / res
        dst = output_dir / res
        print(f"==== {src} -> {dst}")
        if src.is_file():
            shutil.copy2(src, dst)
            TIMER.stop()
            sz = file_size(dst)
            TIMER.start()
            BYTES_RD += sz
            BYTES_WR += sz
        elif src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
            TIMER.stop()
            sz = dir_size(dst)
            TIMER.start()
            BYTES_RD += sz
            BYTES_WR += sz


def render_gallery_frag(gallery_items: List[GalleryItem]) -> str:
    if not gallery_items:
        return ""

    html = '<div class="gallery">\n'

    for gi in gallery_items:
        html += (
            img(src=Path("gallery") / gi.image, alt=gi.caption, path=gi.full_path)
            + "\n"
        )

    html += "</div>\n"
    return html


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
    math = frontmatter.get("math", False)

    gallery_items = [
        GalleryItem(
            gi["image"],
            gi["caption"],
            full_path=OUTPUT_DIR / spec.output_dir / "gallery" / gi["image"],
        )
        for gi in frontmatter.get("gallery_item", [])
    ]

    gallery_html = render_gallery_frag(gallery_items)

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
        gallery_html=gallery_html,
        math=math,
        css=frontmatter.get("css", ""),
        tags=frontmatter.get("tags", []),
        keywords=frontmatter.get("keywords", []),
        description=frontmatter.get("description", ""),
    )


def output_post(post: Post):
    global BYTES_RD

    tmpl_path = TEMPLATES_DIR / "post.tmpl"
    TIMER.stop()
    BYTES_RD += file_size(tmpl_path)
    TIMER.start()
    with open(tmpl_path, "r") as f:
        tmpl = Template(f.read())

    html = tmpl.safe_substitute(
        {
            "style_frag": style("navbar.css")
            + style("common.css")
            + style("post.css")
            + style("footer.css")
            + post.css,
            "head_frag": head_frag(
                math=post.math,
                descr=post.description,
                keywords=post.tags + post.keywords,
            ),
            "nav_frag": nav_frag(),
            "body_frag": post.body_html,
            "gallery_frag": post.gallery_html,
            "footer_frag": footer_frag(
                edit_url=github_edit_url(post.spec.markdown_path.relative_to(ROOT_DIR))
            ),
        }
    )
    output_dir = OUTPUT_DIR / post.spec.output_dir
    print(f"==== output {post.spec.markdown_path} -> {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = output_dir / "index.html"
    write_file(html_path, html)


def render_pub(spec: PubSpec) -> Pub:
    print(f"==== render {spec.markdown_path}")
    frontmatter, markdown = read_markdown(spec.markdown_path)

    title = frontmatter["title"]
    date = normalize_and_localize(frontmatter["date"])
    authors_html = authors_span(frontmatter.get("authors", []))

    venue = frontmatter.get("venue", "")
    if venue:
        venue_html = venue_div(venue, _class="venue")
    else:
        venue_html = ""

    url_code = frontmatter.get("url_code", [])
    if isinstance(url_code, str):
        url_code = [url_code]

    url_pdf = frontmatter.get("url_pdf", [])
    if isinstance(url_pdf, str):
        url_pdf = [url_pdf]

    with PygmentsRenderer(style=PYGMENTS_STYLE) as renderer:
        body_html = renderer.render(mistletoe.Document(markdown))

    return Pub(
        spec=spec,
        title=title,
        body_html=body_html,
        date=date,
        venue_html=venue_html,
        authors_html=authors_html,
        abstract=frontmatter.get("abstract", ""),
        url_pdf=url_pdf,
        url_code=url_code,
        url_slides=frontmatter.get("url_slides", ""),
        url_poster=frontmatter.get("url_poster", ""),
        url_video=frontmatter.get("url_video", ""),
        description=frontmatter.get("description", ""),
        keywords=frontmatter.get("tags", []) + frontmatter.get("keywords", []),
    )


def load_pubs() -> List[PubSpec]:
    pubs = []

    for pub in PUBS_DIR.iterdir():
        output_dir = Path("publication") / f"{pub.stem}"
        if pub.is_file():
            spec = PubSpec(markdown_path=pub, is_dir=False, output_dir=output_dir)
        elif pub.is_dir():
            md_path = pub / "index.md"
            if md_path.is_file():
                spec = PubSpec(
                    markdown_path=md_path,
                    is_dir=True,
                    output_dir=output_dir,
                )
        else:
            continue
        pubs += [render_pub(spec)]

    return pubs


def maybe_at_midnight(o) -> datetime.datetime:
    if isinstance(o, datetime.datetime):
        return o
    elif isinstance(o, datetime.date):
        return datetime.datetime.combine(o, datetime.datetime.min.time())  # midnight
    else:
        raise RuntimeError(type(o))


def normalize_and_localize(o) -> datetime.datetime:
    return maybe_localize_to_mountain(maybe_at_midnight(o))


def robots_txt():
    global BYTES_RD
    global BYTES_WR
    shutil.copy(Path(__file__).parent / "robots.txt", OUTPUT_DIR / "robots.txt")
    TIMER.stop()
    sz = file_size(OUTPUT_DIR / "robots.txt")
    BYTES_WR += sz
    BYTES_RD += sz
    TIMER.start()


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

    time_start = frontmatter.get("time_start", None)
    time_end = frontmatter.get("time_end", None)

    authors_html = authors_span(frontmatter.get("authors", []))

    body_html = ""
    with PygmentsRenderer(style=PYGMENTS_STYLE) as renderer:
        body_html += renderer.render(mistletoe.Document(markdown))

    url_code = frontmatter.get("url_code", [])
    if isinstance(url_code, str):
        url_code = [url_code]

    return Talk(
        spec=spec,
        title=title,
        body_html=body_html,
        how_invited=frontmatter.get("how_invited", ""),
        location=frontmatter.get("location", ""),
        authors_html=authors_html,
        time_start=time_start,
        time_end=time_end,
        abstract=frontmatter.get("abstract", ""),
        event=frontmatter.get("event", ""),
        event_url=frontmatter.get("event_url", None),
        url_slides=frontmatter.get("url_slides", None),
        url_code=url_code,
        url_video=frontmatter.get("url_video", ""),
        publication=frontmatter.get("publication", None),
    )


def output_talk(talk: Talk):
    global BYTES_RD
    tmpl_path = TEMPLATES_DIR / "talk.tmpl"
    TIMER.stop()
    BYTES_RD += file_size(tmpl_path)
    TIMER.start()
    with open(tmpl_path, "r") as f:
        tmpl = Template(f.read())

    location_html = ""
    if talk.location:
        location_html = talk_page_location_div(talk.location)
    address_html = ""
    if talk.address:
        address_html = talk_page_address_div(talk.address)
    time_html = ""
    if talk.time_start:
        time_html = talk_page_time_div(talk.time_start, talk.time_end)
    abstract_frag = ""
    if talk.abstract:
        abstract_frag = page_abstract_frag(talk.abstract)

    publication_frag = ""
    if talk.publication:
        publication_frag = (
            f'<a href="/publication/{talk.publication}">related publication</a>\n'
        )

    event_frag = ""
    if talk.event:
        event_frag = f'<div class="event">\n'
        if talk.event_url:
            event_frag += f'<a href="{talk.event_url}">{talk.event}</a>\n'
        else:
            event_frag += f"{talk.event}\n"
        event_frag += "</div>"

    slides_object = ""
    if talk.url_slides:
        slides_object += f"<h2>Slides</h2>\n"
        slides_object += f'<div class="slides">\n'
        if talk.url_slides.endswith(".pdf"):
            slides_object += f'<object class="slides-viewport" data="{talk.url_slides}" type="application/pdf" width="400" height="300">\n'
            slides_object += f'<a href="{talk.url_slides}">slides</a>\n'
            slides_object += "</object>\n"
            slides_object += f'<div><a href="{talk.url_slides}">slides</a></div>'
        else:
            slides_object += f'<a href="{talk.url_slides}">slides</a>\n'

        slides_object += "</div>"

    links_frag = ""
    links_frag += "<h2>Links</h2>\n"
    if talk.url_code:
        links_frag += '<div class="talk-page-links">\n'
        for url in talk.url_code:
            if "github.com" in url:
                label = url
            else:
                label = url
            links_frag += '<div class="talk-page-link">\n'
            links_frag += f'<a href="{url}">{label}</a>\n'
            links_frag += "</div>\n"
        links_frag += "</div>\n"

    html = tmpl.safe_substitute(
        {
            "style_frag": style("navbar.css")
            + style("common.css")
            + style("talk.css")
            + style("footer.css"),
            "head_frag": head_frag(),
            "nav_frag": nav_frag(),
            "title": talk.title,
            "authors": talk.authors_html,
            "time": time_html,
            "how_invited": talk.how_invited,
            "location": location_html,
            "event": event_frag,
            "address": address_html,
            "abstract": abstract_frag,
            "body_frag": talk.body_html,
            "video_frag": video_embed_frag(talk.url_video),
            "links_frag": links_frag,
            "slides_object": slides_object,
            "footer_frag": footer_frag(
                edit_url=github_edit_url(talk.spec.markdown_path.relative_to(ROOT_DIR))
            ),
        }
    )
    output_dir = OUTPUT_DIR / talk.spec.output_dir
    print(f"==== output {talk.spec.markdown_path} -> {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = output_dir / "index.html"
    write_file(html_path, html)


def nav_frag() -> str:
    global BYTES_RD
    path = TEMPLATES_DIR / "navbar_frag.html"
    BYTES_RD += file_size(path)
    with open(path) as f:
        return f.read() + "\n"


@lru_cache(maxsize=None)
def style(css) -> str:
    global BYTES_RD
    path = STYLE_DIR / css
    BYTES_RD += file_size(path)
    with open(path) as f:
        return f.read() + "\n"


def copy_static():
    global BYTES_RD
    global BYTES_WR

    for src_path in STATIC_DIR.rglob("*"):
        if src_path.is_file():
            dst_path = OUTPUT_DIR / (src_path.relative_to(STATIC_DIR))
            dst_path.parent.mkdir(exist_ok=True, parents=True)
            print(f"==== {src_path} -> {dst_path}")
            if src_path.suffix == ".jpg":
                src_img = Image.open(src_path)
                src_img.save(dst_path, optimize=True, quality=85)
            elif src_path.suffix == ".png":
                src_img = Image.open(src_path)
                src_img.save(dst_path, optimize=True)
            else:
                shutil.copy(src=src_path, dst=dst_path)
            TIMER.stop()
            src_sz = file_size(src_path)
            dst_sz = file_size(dst_path)
            TIMER.start()
            BYTES_RD += src_sz
            BYTES_WR += dst_sz


def copy_thirdparty():
    global BYTES_RD
    global BYTES_WR
    src = THIRDPARTY_DIR
    dst = OUTPUT_DIR / "thirdparty"
    print(f"==== {src} -> {dst}")
    shutil.copytree(src, dst, dirs_exist_ok=True)
    TIMER.stop()
    sz = dir_size(dst)
    TIMER.start()
    BYTES_RD += sz
    BYTES_WR += sz


SHA = None


def footer_frag(edit_url="") -> str:
    global SHA
    now_str = datetime.datetime.now().strftime("%x")
    if SHA is None:
        cp = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True
        )
        SHA = cp.stdout.decode("utf-8").strip()
    html = '<div class="footer">\n'
    html += "<hr \>\n"
    html += '<div class="footer-items">\n'
    html += f"<div>build {SHA} on {now_str}</div>\n"
    html += f'<div><a href="https://github.com/cwpearson/website2">github.com/cwpearson/website2</a></div>\n'
    html += (
        f'<div>copyright Carl Pearson {datetime.datetime.now().strftime("%Y")}</div>\n'
    )
    if edit_url:
        html += f'<div><a href="{edit_url}">edit</a></div>\n'
    html += "</div>\n"
    html += "</div>\n"
    return html


def head_frag(
    title: str = "", descr: str = "", keywords: List[str] = [], math=False
) -> str:
    global BYTES_RD
    html = ""
    html += '<meta name="viewport" content="width=device-width">\n'
    if title:
        html += f"<title>{title}</title>\n"
    html += '<meta name="generator" content="github.com/cwpearson/website2">\n'
    html += '<meta name="author" content="Carl Pearson">\n'
    if descr:
        html += f'<meta name="description" content="{descr}">\n'
    if keywords:
        html += f'<meta name="keywords" content="{",".join(keywords)}">\n'

    if math:
        katex_path = TEMPLATES_DIR / "katex_frag.html"
        TIMER.stop()
        BYTES_RD += file_size(katex_path)
        TIMER.start()
        with open(katex_path) as f:
            html += f.read() + "\n"

    html += '<link rel="icon" type="image/x-icon" href="/favicon.ico"/>\n'

    html += '<script async src="https://analytics.carlpearson.net/script.js" data-website-id="b5d84f78-f4ee-4ce8-ae90-d2cd59e70fbf"></script>\n'

    return html


def video_embed_frag(url) -> str:
    """takes a url to a video and returns an html fragment to embed it"""
    if not url:
        return ""

    if "youtube.com" in url:
        ms = re.findall(r"\?v=(.*)", url)
        video_id = ms[0]
        with open(TEMPLATES_DIR / "youtube_embed_frag.tmpl", "r") as f:
            tmpl = Template(f.read())
        return tmpl.safe_substitute({"video_id": video_id})

    if "vimeo.com" in url:
        ms = re.findall(r"vimeo.com/([^/]*)/?", url)
        video_id = ms[0]
        with open(TEMPLATES_DIR / "vimeo_embed_frag.tmpl", "r") as f:
            tmpl = Template(f.read())
        return tmpl.safe_substitute({"video_id": video_id})


def output_pub(pub: Pub):
    global BYTES_RD
    tmpl_path = TEMPLATES_DIR / "pub.tmpl"
    TIMER.stop()
    BYTES_RD += file_size(tmpl_path)
    TIMER.start()
    with open(tmpl_path, "r") as f:
        tmpl = Template(f.read())

    links_html = ""
    for url in pub.url_pdf:
        links_html += f'<div class="link">\n'
        links_html += page_href(url, "pdf")
        links_html += "</div>\n"
    for url in pub.url_code:
        links_html += f'<div class="link">\n'
        links_html += page_href(url, "code")
        links_html += "</div>\n"
    if pub.url_slides:
        links_html += f'<div class="link">\n'
        links_html += page_href(pub.url_slides, "slides")
        links_html += "</div>\n"
    if pub.url_poster:
        links_html += f'<div class="link">\n'
        links_html += page_href(pub.url_poster, "poster")
        links_html += "</div>\n"
    if links_html:
        links_html = f'<div class="link-container">\n' + links_html + "</div>\n"

    video_frag = video_embed_frag(pub.url_video)

    html = tmpl.safe_substitute(
        {
            "style_frag": style("navbar.css")
            + style("common.css")
            + style("publication.css")
            + style("footer.css"),
            "head_frag": head_frag(
                pub.title,
                descr=pub.description,
                keywords=pub.keywords,
            ),
            "nav_frag": nav_frag(),
            "title": pub.title,
            "authors": pub.authors_html,
            "venue": pub.venue_html,
            "date": pub.date.strftime("%m/%d/%y"),
            "abstract": pub.abstract,
            "links_frag": links_html,
            "body_frag": pub.body_html,
            "video_frag": video_frag,
            "footer_frag": footer_frag(
                edit_url=github_edit_url(pub.spec.markdown_path.relative_to(ROOT_DIR))
            ),
        }
    )
    output_dir = OUTPUT_DIR / pub.spec.output_dir
    print(f"==== output {pub.spec.markdown_path} -> {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = output_dir / "index.html"
    write_file(html_path, html)


def render_index(top_k_posts: List[Post], top_k_pubs: List[Pub]) -> str:
    global BYTES_RD
    tmpl_path = TEMPLATES_DIR / "index.tmpl"
    TIMER.stop()
    BYTES_RD += file_size(tmpl_path)
    TIMER.start()
    with open(tmpl_path) as f:
        tmpl = Template(f.read())

    frontmatter, _ = read_markdown("index.md")
    bio = frontmatter["bio"]

    top_k_posts_frag = ""
    for post in top_k_posts:
        top_k_posts_frag += post_card(post)

    # fake "Post" that just links to all posts
    top_k_posts_frag += post_card(
        Post(
            spec=PostSpec(markdown_path=None, input_dir=None, output_dir=Path("posts")),
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
            "style_frag": style("navbar.css")
            + style("common.css")
            + style("cards.css")
            + style("index.css")
            + style("footer.css"),
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
            "footer_frag": footer_frag(edit_url=github_edit_url("index.md")),
        }
    )


def output_index(html):
    output_path = OUTPUT_DIR / "index.html"
    print(f"==== write {output_path}")
    write_file(output_path, html)


def render_experience() -> str:
    global BYTES_RD
    tmpl_path = TEMPLATES_DIR / "experience.tmpl"
    TIMER.stop()
    BYTES_RD += file_size(tmpl_path)
    TIMER.start()
    with open(tmpl_path) as f:
        tmpl = Template(f.read())

    frontmatter, md_str = read_markdown("experience.md")
    title = frontmatter["title"]
    descr = frontmatter["description"]

    body_frag = mistletoe.markdown(md_str)

    return tmpl.safe_substitute(
        {
            "style_frag": style("navbar.css")
            + style("common.css")
            + style("index.css")
            + style("footer.css"),
            "head_frag": head_frag(title=title, descr=descr),
            "nav_frag": nav_frag(),
            "title": title,
            "body_frag": body_frag,
            "footer_frag": footer_frag(edit_url=github_edit_url("experience.md")),
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
            "style_frag": style("navbar.css")
            + style("common.css")
            + style("index.css")
            + style("footer.css"),
            "head_frag": head_frag(title=title, descr=descr),
            "nav_frag": nav_frag(),
            "title": title,
            "body_frag": body_frag,
            "footer_frag": footer_frag(edit_url=github_edit_url("recognition.md")),
        }
    )


def output_html(prefix, html):
    output_path = OUTPUT_DIR / prefix / "index.html"
    output_path.parent.mkdir(exist_ok=True, parents=True)
    print(f"==== write {output_path}")
    write_file(output_path, html)


def authors_span(authors: List[str]) -> str:
    assert isinstance(authors, list)
    html = ""
    for i, author in enumerate(authors):
        if author == "Carl Pearson" or author == "Pearson, Carl":
            html += f"<strong>{author}</strong>"
        else:
            html += author
        if i + 1 < len(authors):
            html += ", "
    return html


def venue_div(venue: str, _class="pub-venue") -> str:
    _in = "in "
    if venue.lower() == "arxiv":
        _in = ""
    elif venue.lower() == "tech report":
        _in = ""
    elif "thesis" in venue.lower():
        _in = ""
    elif "dissertation" in venue.lower():
        _in = ""
    return (
        f'<div class="{_class}-wrapper">{_in}<div class="{_class}">{venue}</div></div>'
    )


def pub_card(pub: Pub) -> str:
    """
    return an html fragment for a Pub
    """

    if pub.date:
        mmyy = pub.date.strftime("%m/%y")
    else:
        mmyy = ""

    html = ""
    html += f'<a href="/{pub.spec.output_dir}" class="no-decoration">\n'
    html += f'<div class="content-card">\n'
    html += '<div class="pub-ref">\n'
    html += f'<div class="pub-title">{pub.title}</div>\n'

    html += "<div>\n"
    if pub.authors_html:
        html += f'<div class="authors">{pub.authors_html}</div>\n'
    if pub.venue_html:
        html += pub.venue_html + "\n"
    html += "</div>\n"

    html += "</div>\n"  # pub-ref

    html += f'<div class="pub-date">{mmyy}</div>\n'

    html += "</div>\n"  # content-card
    html += "</a>\n"
    return html


def render_publications(pubs: List[Pub]) -> str:
    global BYTES_RD
    tmpl_path = TEMPLATES_DIR / "publications.tmpl"
    TIMER.stop()
    BYTES_RD += file_size(tmpl_path)
    TIMER.start()
    with open(tmpl_path) as f:
        tmpl = Template(f.read())

    pub_links = ""
    for pub in sorted(pubs, key=lambda x: x.date, reverse=True):
        pub_links += pub_card(pub)

    return tmpl.safe_substitute(
        {
            "style_frag": style("navbar.css")
            + style("common.css")
            + style("cards.css")
            + style("footer.css"),
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
    write_file(output_path, html)


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
    html += f'<div class="content-card">\n'
    html += f'<div class="post-title">{post.title}</div>\n'
    html += f'<div class="post-date">{mmddyy}</div>\n'
    html += "</div>\n"
    html += "</a>\n"
    return html


def render_posts(posts: List[Post]) -> str:
    global BYTES_RD
    tmpl_path = TEMPLATES_DIR / "posts.tmpl"
    TIMER.stop()
    BYTES_RD += file_size(tmpl_path)
    TIMER.start()
    with open(tmpl_path) as f:
        tmpl = Template(f.read())

    post_links = ""
    for post in sorted(posts, key=lambda x: x.create_time, reverse=True):
        post_links += post_card(post)

    return tmpl.safe_substitute(
        {
            "style_frag": style("navbar.css")
            + style("common.css")
            + style("footer.css"),
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

    if talk.time_start:
        mmddyy = talk.time_start.strftime("%m/%d/%y")
    else:
        mmddyy = "???"

    html = ""
    html += f'<a href="/{talk.spec.output_dir}" class="no-decoration">\n'
    html += f'<div class="content-card">\n'
    html += '<div class="pub-ref">\n'
    html += f'<div class="pub-title">{talk.title}</div>\n'

    html += "<div>\n"
    if talk.event:
        _at = "at "
        if "online" in talk.event.lower():
            _at = ""
        html += f'<div class="venue-wrapper">{_at}<div class="venue">{talk.event}</div></div>\n'
    html += "</div>\n"

    html += "</div>\n"  # pub-ref

    html += f'<div class="pub-date">{mmddyy}</div>\n'

    html += "</div>\n"  # content-card
    html += "</a>\n"
    return html


def render_talks(talks: List[Talk]) -> str:
    global BYTES_RD
    tmpl_path = TEMPLATES_DIR / "talks.tmpl"
    TIMER.stop()
    BYTES_RD += file_size(tmpl_path)
    TIMER.start()
    with open(tmpl_path) as f:
        tmpl = Template(f.read())

    def bytime(x: Talk):
        """
        the start time may not be localized, so localize if needed
        """
        if x.time_start:
            return normalize_and_localize(x.time_start)
        else:
            return x.publish_time

    talk_links = ""
    for talk in sorted(talks, key=bytime, reverse=True):
        talk_links += talk_card(talk)

    return tmpl.safe_substitute(
        {
            "style_frag": style("navbar.css")
            + style("common.css")
            + style("cards.css")
            + style("footer.css"),
            "head_frag": head_frag(),
            "nav_frag": nav_frag(),
            "body_frag": talk_links,
            "footer_frag": footer_frag(),
        }
    )


if __name__ == "__main__":
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

    TIMER.start()
    favicons()
    robots_txt()

    post_specs = find_posts()
    for ps in post_specs:
        move_post_resources(ps)
    posts = [render_post(spec) for spec in post_specs]
    posts = [p for p in posts if p is not None]
    for post in posts:
        output_post(post)

    pubs = load_pubs()
    for pub in pubs:
        output_pub(pub)

    talk_specs = find_talks()
    talks = [render_talk(spec) for spec in talk_specs]
    talks = [t for t in talks if t is not None]
    for talk in talks:
        output_talk(talk)

    project_specs = find_projects()
    projects = [render_project(spec) for spec in project_specs]
    for project in projects:
        output_project(project)

    index_html = render_index(
        top_k_posts=sorted(posts, key=lambda p: p.create_time, reverse=True)[0:5],
        top_k_pubs=sorted(pubs, key=lambda p: p.date, reverse=True)[0:5],
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

    projects_html = render_projects_index(projects)
    output_html("projects", projects_html)

    copy_static()
    copy_thirdparty()

    TIMER.stop()

    print(f"read  {BYTES_RD} B")
    print(f"wrote {BYTES_WR} B")
    print(f"{(BYTES_RD + BYTES_WR) / TIMER.total} B/s")

    print(f"{len(LARGE_PAGES)} large pages / {SMALL_PAGES} small pages")
    for path in LARGE_PAGES:
        print(f"  ({gzipped_size(path)}B) {path} ")
