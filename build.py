from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Union, Dict, Any
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
import urllib

import mistletoe
from mistletoe.contrib.pygments_renderer import PygmentsRenderer
import yaml
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

BYTES_RD = 0
BYTES_WR = 0

TCP_SLOW_START = 14600
LARGE_PAGES = []
SMALL_PAGES = 0

ROOT_DIR = Path(__file__).parent
CONTENT_DIR = ROOT_DIR / "content"
FRAGMENTS_DIR = ROOT_DIR / "fragments"
POSTS_DIR = ROOT_DIR / "posts"
PUBS_DIR = ROOT_DIR / "publications"
STATIC_DIR = ROOT_DIR / "static"
STYLE_DIR = ROOT_DIR / "style"
TALKS_DIR = ROOT_DIR / "talks"
TEMPLATES_DIR = ROOT_DIR / "templates"
THIRDPARTY_DIR = ROOT_DIR / "thirdparty"

OUTPUT_DIR = ROOT_DIR / "public"

PYGMENTS_STYLE = "default"


@dataclass(frozen=True)
class Tag:
    raw: str

    def string(self) -> str:
        return self.raw

    def url_component(self) -> str:
        """get a version of the tag that's safe for a URL"""
        return urllib.parse.quote(self.raw)


def canonical_tags(l: List[str]) -> List[Tag]:
    """returns a list of canonical tags for a list of strings"""
    s = set()
    for tag in l:
        s.add(Tag(tag.lower().replace(" ", "_")))
    return list(s)


@dataclass
class LinkSpec:
    """A link on the links page"""

    name: str
    url: str
    url_archive: str = ""
    date: datetime.datetime = None
    description: str = ""
    authors: List[str] = field(default_factory=list)


@dataclass
class Link:
    url: str
    name: str


@dataclass
class GalleryItem:
    src: Path  # relative path to the input image
    caption: str
    dst: Path  # relative path to the transformed image (may be same as source)
    thumb: Path  # relative path to the thumbnail


@dataclass
class PostSpec:
    markdown_path: Path
    markdown: str
    frontmatter: dict
    # path to the posts's directory, if there is one
    input_dir: Union[Path, None]
    output_dir: str
    resources: List[Path] = field(
        default_factory=list
    )  # paths to other things in the post directory
    gallery_items: List[GalleryItem] = field(
        default_factory=list
    )  # paths to other things in the post directory


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
    tags: List[Tag] = field(default_factory=list)
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
    url_pdf: str = ""
    url_arxiv: str = ""
    url_code: List[str] = field(default_factory=list)
    url_slides: str = ""
    url_poster: str = ""
    url_video: str = ""
    description: str = ""
    keywords: List[str] = field(default_factory=list)
    tags: List[Tag] = field(default_factory=list)


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
    publication: str = ""
    project: str = ""
    tags: List[Tag] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)


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
    links: List[Link] = field(default_factory=list)


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


# typevar to return same type as passed
def uniqify(l: List) -> List:
    return list(set(l))


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
        # just choose a very small level here, so its likely a host
        # will be compressing at least this much
        return len(gzip.compress(f.read(), compresslevel=2))


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


def load_links() -> List[LinkSpec]:
    global BYTES_RD
    specs = []
    for yaml_path in (CONTENT_DIR / "links").glob("*.yaml"):
        print(f"==== {yaml_path}")
        TIMER.stop()
        BYTES_RD += file_size(yaml_path)
        TIMER.start()
        with open(yaml_path, "r") as yaml_file:
            data = yaml.load(yaml_file, Loader=yaml.CLoader)
        if data:
            for entry in data:
                name = entry["name"]
                url = entry["url"]
                date = entry["date"]
                url_archive = entry.get("url_archive", "")
                description = entry.get("description", "")
                authors = entry.get("authors", [])
                specs += [LinkSpec(name, url, url_archive, date, description, authors)]
    return specs


def output_links_page(links: List[LinkSpec]):
    frontmatter, markdown = read_markdown(CONTENT_DIR / "links" / "index.md")

    nav_html, nav_css = nav_frag()
    footer_html, footer_css = footer_frag()

    by_month = {}
    for spec in links:
        year, month = spec.date.year, spec.date.month
        by_month[(year, month)] = by_month.get((year, month), []) + [spec]

    links_html = ""
    for (year, month), specs in sorted(by_month.items(), reverse=True):
        links_html += '<div class="month-group">\n'
        h2 = datetime.datetime.strptime(f"{year} {month}", "%Y %m").strftime("%B %Y")
        links_html += f"<h2>{h2}</h2>\n"
        for spec in specs:
            links_html += '<div class="link">\n'
            links_html += f'<a class="name" href="{spec.url}">{spec.name}</a>\n'
            if spec.url_archive:
                links_html += f'<div class="archive">(<a href="{spec.url_archive}">archive</a>)</div>\n'
            if spec.authors:
                links_html += f'<div class="authors">{", ".join(spec.authors)}</div>\n'
            if spec.description:
                links_html += f'<div class="description">{spec.description}</div>\n'
            links_html += "</div>\n"
        links_html += "</div>\n"
    if links_html:
        links_html = f'<div class="link-wrapper">\n{links_html}</div>\n'

    title = frontmatter["title"]
    html = template("links.tmpl").safe_substitute(
        {
            "style_frag": nav_css
            + style("common.css")
            + style("links.css")
            + footer_css,
            "head_frag": head_frag(title=title, descr="Interesting things I've read"),
            "nav_frag": nav_html,
            "title": title,
            "body_frag": links_html,
            "footer_frag": footer_html,
        }
    )
    output_dir = OUTPUT_DIR / "links"
    print(f'==== output {CONTENT_DIR / "links" / "index.md"} -> {output_dir}')
    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = output_dir / "index.html"
    write_file(html_path, html)


def render_links_frag(links: List[Link]) -> Tuple[str, str]:
    """generates html,css for links"""

    css = style("page_links.css")

    html = ""
    for link in links:
        html += '<div class="page-link">\n'
        html += f'<a href="{link.url}">{link.name}</a>\n'
        html += "</div>\n"

    if html:
        html = f'<div class="page-links-horiz">{html}</div>\n'
    return html, css


def render_project(spec: ProjectSpec) -> Project:
    print(f"==== render {spec.markdown_path}")
    frontmatter, markdown = read_markdown(spec.markdown_path)

    draft = frontmatter.get("draft", False)
    if draft:
        return None
    title = frontmatter["title"]
    create_time = frontmatter["date"]
    create_time = maybe_localize_to_mountain(create_time)
    raw_tags = frontmatter.get("tags", [])

    body_html = ""
    body_html += f"<h1>{title}</h1>\n"
    with PygmentsRenderer(style=PYGMENTS_STYLE) as renderer:
        body_html += renderer.render(mistletoe.Document(markdown))

    return Project(
        spec=spec,
        title=title,
        body_html=body_html,
        create_time=create_time,
        tags=canonical_tags(raw_tags),
        links=[
            Link(url=link["url"], name=link["name"])
            for link in frontmatter.get("links", [])
        ],
    )


def output_project(project: Project):
    links_html, links_css = render_links_frag(project.links)

    nav_html, nav_css = nav_frag()
    footer_html, footer_css = footer_frag(
        edit_url=github_edit_url(project.spec.markdown_path.relative_to(ROOT_DIR))
    )
    html = template("project.tmpl").safe_substitute(
        {
            "style_frag": nav_css
            + style("common.css")
            + style("tag.css")
            + links_css
            + footer_css,
            "head_frag": head_frag(title=project.title),
            "nav_frag": nav_html,
            "body_frag": project.body_html,
            "links_frag": links_html,
            "tags_frag": render_tags_frag(project.tags),
            "footer_frag": footer_html,
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
    project_links = ""
    for project in sorted(projects, key=lambda x: x.create_time, reverse=True):
        project_links += project_card(project)

    nav_html, nav_css = nav_frag()
    footer_html, footer_css = footer_frag()
    return template("projects.tmpl").safe_substitute(
        {
            "style_frag": nav_css
            + style("common.css")
            + style("cards.css")
            + footer_css,
            "head_frag": head_frag(title="Projects", descr="Links to project pages"),
            "nav_frag": nav_html,
            "body_frag": project_links,
            "footer_frag": footer_html,
        }
    )


def find_posts() -> List[PostSpec]:
    specs = []

    for post in POSTS_DIR.iterdir():
        output_dir = Path("post") / f"{post.stem}"
        if post.is_file():
            frontmatter, markdown = read_markdown(post)
            specs += [
                PostSpec(
                    markdown_path=post,
                    frontmatter=frontmatter,
                    markdown=markdown,
                    input_dir=None,
                    output_dir=output_dir,
                )
            ]
        elif post.is_dir():
            md_path = post / "index.md"
            if md_path.is_file():
                frontmatter, markdown = read_markdown(md_path)
                resources = [
                    x.relative_to(post)
                    for x in post.iterdir()
                    if x.name not in ("gallery", "index.md")
                ]

                specs += [
                    PostSpec(
                        markdown_path=md_path,
                        frontmatter=frontmatter,
                        markdown=markdown,
                        input_dir=post,
                        output_dir=output_dir,
                        resources=resources,
                    )
                ]

    return specs


def preprocess_gallery(spec: PostSpec):

    gallery_items: List[GalleryItem] = []

    for gi in spec.frontmatter.get("gallery_item", []):

        src = Path(gi["image"])

        if src.suffix.lower() == ".heic":
            dst = src.with_suffix(".jpg")
        else:
            dst = src

        thumb = dst.stem + "_thumb" + dst.suffix

        gallery_items += [
            GalleryItem(
                src=src,
                caption=gi.get("caption", ""),
                dst=dst,
                thumb=thumb,
            )
        ]
    ps.gallery_items = gallery_items


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
    print(f"==== post resources into -> {output_dir}")
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
    for gi in spec.gallery_items:
        src_path = spec.input_dir / "gallery" / gi.src
        dst_path = output_dir / "gallery" / gi.dst
        thumb_path = output_dir / "gallery" / gi.thumb
        src_img = Image.open(src_path)
        BYTES_RD += file_size(src_path)
        print(f"==== gallery image {src_path} -> {dst_path}")
        dst_path.parent.mkdir(exist_ok=True, parents=True)
        src_img.save(dst_path)
        BYTES_WR += file_size(dst_path)

        print(f"==== gallery thumb {src_path} -> {thumb_path}")
        src_img.thumbnail((256, 256), Image.Resampling.LANCZOS)
        thumb_path.parent.mkdir(exist_ok=True, parents=True)
        src_img.save(thumb_path, quality=75)
        BYTES_WR += file_size(thumb_path)


def render_gallery_frag(gallery_items: List[GalleryItem], post_root: Path) -> str:
    if not gallery_items:
        return ""

    html = '<div class="gallery">\n'

    for gi in gallery_items:
        html += '<div class="item">\n'
        html += '<div class="image">\n'

        img_frag = img(
            src=Path("gallery") / gi.thumb,
            alt=gi.caption,
            path=OUTPUT_DIR / post_root / "gallery" / gi.thumb,
        )

        html += f'<a href="gallery/{gi.dst}">{img_frag}</a>\n'
        html += "</div>\n"  # .image
        html += '<div class="caption">\n'
        html += gi.caption + "\n"
        html += "</div>\n"  # .caption

        html += "</div>\n"  # .item

    html += "</div>\n"  # .gallery
    return html


def render_post(spec: PostSpec) -> Post:
    print(f"==== render {spec.input_dir} -> {spec.output_dir}")

    draft = spec.frontmatter.get("draft", False)
    if draft:
        return None
    title = spec.frontmatter["title"]
    create_time = spec.frontmatter["date"]
    create_time = maybe_localize_to_mountain(create_time)
    mod_time = spec.frontmatter.get("lastmod", create_time)
    mod_time = maybe_localize_to_mountain(mod_time)
    math = spec.frontmatter.get("math", False)

    gallery_html = render_gallery_frag(spec.gallery_items, post_root=spec.output_dir)
    raw_tags = spec.frontmatter.get("tags", [])

    body_html = ""
    body_html += f"<h1>{title}</h1>\n"
    body_html += f'<div class="byline">by Carl Pearson</div>'
    with PygmentsRenderer(style=PYGMENTS_STYLE) as renderer:
        body_html += renderer.render(mistletoe.Document(spec.markdown))

    return Post(
        spec=spec,
        title=title,
        body_html=body_html,
        create_time=create_time,
        mod_time=mod_time,
        gallery_html=gallery_html,
        math=math,
        css=spec.frontmatter.get("css", ""),
        tags=canonical_tags(raw_tags),
        keywords=uniqify(spec.frontmatter.get("keywords", []) + raw_tags),
        description=spec.frontmatter.get("description", ""),
    )


def output_post(post: Post):
    nav_html, nav_css = nav_frag()
    footer_html, footer_css = footer_frag(
        edit_url=github_edit_url(post.spec.markdown_path.relative_to(ROOT_DIR))
    )
    html = template("post.tmpl").safe_substitute(
        {
            "style_frag": nav_css
            + style("common.css")
            + style("tag.css")
            + style("post.css")
            + footer_css
            + post.css,
            "head_frag": head_frag(
                title=post.title,
                math=post.math,
                descr=post.description,
                keywords=post.keywords,
            ),
            "nav_frag": nav_html,
            "body_frag": post.body_html,
            "gallery_frag": post.gallery_html,
            "tags_frag": render_tags_frag(post.tags),
            "footer_frag": footer_html,
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
    raw_tags = frontmatter.get("tags", [])

    venue = frontmatter.get("venue", "")
    if venue:
        venue_html = venue_div(venue, _class="venue")
    else:
        venue_html = ""

    keywords = raw_tags + frontmatter.get("keywords", [])
    if venue:
        keywords += [venue]
    keywords = uniqify(keywords)

    url_code = frontmatter.get("url_code", [])
    if isinstance(url_code, str):
        url_code = [url_code]

    url_pdf = frontmatter.get("url_pdf", "")

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
        url_arxiv=frontmatter.get("url_arxiv", ""),
        url_code=url_code,
        url_slides=frontmatter.get("url_slides", ""),
        url_poster=frontmatter.get("url_poster", ""),
        url_video=frontmatter.get("url_video", ""),
        description=frontmatter.get("description", ""),
        keywords=keywords,
        tags=canonical_tags(raw_tags),
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


@lru_cache(maxsize=None)
def fragment(name) -> str:
    global BYTES_RD
    path = FRAGMENTS_DIR / name
    TIMER.stop()
    BYTES_RD += file_size(path)
    TIMER.start()
    with open(path, "r") as f:
        return f.read() + "\n"


@lru_cache(maxsize=None)
def katex_frag() -> str:
    return fragment("katex_frag.html")


@lru_cache(maxsize=None)
def nav_frag() -> Tuple[str, str]:
    """returns html + css for navbar"""
    return fragment("navbar_frag.html"), style("navbar.css")


@lru_cache(maxsize=None)
def style(css) -> str:
    global BYTES_RD
    path = STYLE_DIR / css
    TIMER.stop()
    BYTES_RD += file_size(path)
    TIMER.start()
    with open(path, "r") as f:
        return f.read() + "\n"


@lru_cache(maxsize=None)
def template(tmpl_name) -> Template:
    global BYTES_RD
    path = TEMPLATES_DIR / tmpl_name
    TIMER.stop()
    BYTES_RD += file_size(path)
    TIMER.start()
    with open(path, "r") as f:
        return Template(f.read() + "\n")


def render_talk(spec: TalkSpec) -> Pub:
    print(f"==== render {spec.markdown_path}")
    frontmatter, markdown = read_markdown(spec.markdown_path)

    title = frontmatter["title"]

    time_start = frontmatter.get("time_start", None)
    time_end = frontmatter.get("time_end", None)

    authors_html = authors_span(frontmatter.get("authors", []))
    raw_tags = frontmatter.get("tags", [])

    body_html = ""
    with PygmentsRenderer(style=PYGMENTS_STYLE) as renderer:
        body_html += renderer.render(mistletoe.Document(markdown))

    url_code = frontmatter.get("url_code", [])
    if isinstance(url_code, str):
        url_code = [url_code]

    event = frontmatter.get("event", "")
    keywords = raw_tags + frontmatter.get("keywords", [])
    if event:
        keywords += [event]
    keywords = uniqify(keywords)

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
        publication=frontmatter.get("publication", ""),
        project=frontmatter.get("project", ""),
        tags=canonical_tags(raw_tags),
        keywords=keywords,
    )


def render_crossref_frag(urls: List[str]) -> str:
    """returns html,css for crossref frags"""
    html = ""
    for url in urls:
        if not url:
            continue
        elif url.startswith("/project/"):
            html += f'<div class="page-link"><a href="{url}">project</a></div>\n'
        elif url.startswith("/publication/"):
            html += f'<div class="page-link"><a href="{url}">publication</a></div>\n'
        else:
            html += f'<div class="page-link"><a href="{url}">{url}</a></div>\n'
    if html:
        html = f'<div class="page-links-horiz">\n{html}</div>\n'

    return html, style("page_links.css")


def output_talk(talk: Talk):
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

    video_html, video_css = video_embed_frag(talk.url_video)
    nav_html, nav_css = nav_frag()
    footer_html, footer_css = footer_frag(
        edit_url=github_edit_url(talk.spec.markdown_path.relative_to(ROOT_DIR))
    )

    crossref_frag, crossref_css = render_crossref_frag([talk.publication, talk.project])

    html = template("talk.tmpl").safe_substitute(
        {
            "style_frag": nav_css
            + style("common.css")
            + video_css
            + style("tag.css")
            + style("talk.css")
            + crossref_css
            + footer_css,
            "head_frag": head_frag(
                title=talk.title,
                keywords=talk.keywords,
            ),
            "nav_frag": nav_html,
            "title": talk.title,
            "authors": talk.authors_html,
            "time": time_html,
            "how_invited": talk.how_invited,
            "location": location_html,
            "event": event_frag,
            "address": address_html,
            "abstract": abstract_frag,
            "crossref_frag": crossref_frag,
            "body_frag": talk.body_html,
            "video_frag": video_html,
            "links_frag": links_frag,
            "slides_object": slides_object,
            "tags_frag": render_tags_frag(talk.tags),
            "footer_frag": footer_html,
        }
    )
    output_dir = OUTPUT_DIR / talk.spec.output_dir
    print(f"==== output {talk.spec.markdown_path} -> {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = output_dir / "index.html"
    write_file(html_path, html)


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


def footer_frag(edit_url="") -> Tuple[str, str]:
    """returns html,css for the footer"""
    global SHA
    now_str = datetime.datetime.now().strftime("%x")
    if SHA is None:
        cp = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True
        )
        SHA = cp.stdout.decode("utf-8").strip()
    html = '<div class="footer">\n'
    html += "<hr />\n"
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
    return html, style("footer.css")


def head_frag(
    title: str = "", descr: str = "", keywords: List[str] = [], math=False
) -> str:
    global BYTES_RD
    html = ""
    html += '<meta name="viewport" content="width=device-width">\n'
    html += '<meta charset="utf-8">\n'
    if title:
        html += f"<title>{title}</title>\n"
    html += '<meta name="generator" content="github.com/cwpearson/website2">\n'
    html += '<meta name="author" content="Carl Pearson">\n'
    if descr:
        html += f'<meta name="description" content="{descr}">\n'
    if keywords:
        html += f'<meta name="keywords" content="{",".join(keywords)}">\n'

    if math:
        html += katex_frag()

    html += '<link rel="icon" type="image/x-icon" href="/favicon.ico"/>\n'

    html += '<script async src="https://analytics.carlpearson.net/script.js" data-website-id="4f4469b9-91eb-4a1e-9f85-6be37368d942"></script>\n'

    return html


def video_embed_frag(url) -> Tuple[str, str]:
    """takes a url to a video and returns an html fragment, css fragment to embed it"""
    if not url:
        return "", ""

    if "youtube.com" in url:
        ms = re.findall(r"\?v=(.*)", url)
        video_id = ms[0]
        with open(TEMPLATES_DIR / "youtube_embed_frag.tmpl", "r") as f:
            tmpl = Template(f.read())
        return tmpl.safe_substitute({"video_id": video_id}), style("video.css")

    if "vimeo.com" in url:
        ms = re.findall(r"vimeo.com/([^/]*)/?", url)
        video_id = ms[0]
        with open(TEMPLATES_DIR / "vimeo_embed_frag.tmpl", "r") as f:
            tmpl = Template(f.read())
        return tmpl.safe_substitute({"video_id": video_id}), style("video.css")


def paper_embed_frag(url) -> Tuple[str, str]:
    html = ""
    if url:
        html += f"<h2>Paper</h2>\n"
        html += f'<div class="paper">\n'
        if url.endswith(".pdf"):
            html += f'<object class="paper-viewport" data="{url}" type="application/pdf" width="400" height="300">\n'
            html += f'<a href="{url}">paper</a>\n'
            html += "</object>\n"
            html += f'<div><a href="{url}">paper</a></div>'
        else:
            html += f'<a href="{url}">paper</a>\n'
        html += "</div>"
    return html, ""


def render_tags_frag(tags: List[Tag]) -> str:
    html = ""
    for tag in tags:
        html += f'<div class="tag">\n'
        html += page_href("/tag/" + tag.url_component(), "#" + tag.string())
        html += "</div>\n"
    if html:
        html = f'<div class="tag-container">\n' + html + "</div>\n"
    return html


def output_pub(pub: Pub):
    output_dir = OUTPUT_DIR / pub.spec.output_dir
    print(f"==== output {pub.spec.markdown_path} -> {output_dir}")
    links = []
    if pub.url_arxiv:
        links += [Link(url=pub.url_arxiv, name="arxiv")]
    for url in pub.url_code:
        ms = re.findall(".*github.com/(.+)", url)
        if ms:
            links += [Link(url=url, name=ms[0])]
        else:
            links += [Link(url=url, name="code")]
    if pub.url_slides:
        links += [Link(url=pub.url_slides, name="slides")]
    if pub.url_poster:
        links += [Link(url=pub.url_poster, name="poster")]
    links_html, links_css = render_links_frag(links)

    video_html, video_css = video_embed_frag(pub.url_video)
    paper_html, paper_css = paper_embed_frag(pub.url_pdf)
    nav_html, nav_css = nav_frag()
    footer_html, footer_css = footer_frag(
        edit_url=github_edit_url(pub.spec.markdown_path.relative_to(ROOT_DIR))
    )

    html = template("pub.tmpl").safe_substitute(
        {
            "style_frag": nav_css
            + style("common.css")
            + style("tag.css")
            + links_css
            + paper_css
            + video_css
            + style("publication.css")
            + footer_css,
            "head_frag": head_frag(
                pub.title,
                descr=pub.description,
                keywords=pub.keywords,
            ),
            "nav_frag": nav_html,
            "title": pub.title,
            "authors": pub.authors_html,
            "venue": pub.venue_html,
            "date": pub.date.strftime("%m/%d/%y"),
            "abstract": pub.abstract,
            "links_frag": links_html,
            "body_frag": pub.body_html,
            "paper_frag": paper_html,
            "video_frag": video_html,
            "tags_frag": render_tags_frag(pub.tags),
            "footer_frag": footer_html,
        }
    )

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
            spec=PostSpec(
                markdown_path=None,
                markdown=None,
                frontmatter=None,
                input_dir=None,
                output_dir=Path("posts"),
            ),
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

    nav_html, nav_css = nav_frag()
    footer_html, footer_css = footer_frag(edit_url=github_edit_url("index.md"))

    return tmpl.safe_substitute(
        {
            "style_frag": nav_css
            + style("common.css")
            + style("cards.css")
            + style("index.css")
            + footer_css,
            "head_frag": head_frag(
                title="Carl Pearson",
                descr="Personal site for Carl pearson",
            ),
            "nav_frag": nav_html,
            "bio_text": bio,
            "email_svg": fragment("email_svg.html"),
            "linkedin_svg": fragment("linkedin_svg.html"),
            "github_svg": fragment("github_svg.html"),
            "scholar_svg": fragment("scholar_svg.html"),
            "top_k_posts_frag": top_k_posts_frag,
            "top_k_pubs_frag": top_k_pubs_frag,
            "footer_frag": footer_html,
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
    nav_html, nav_css = nav_frag()
    footer_html, footer_css = footer_frag(edit_url=github_edit_url("experience.md"))
    return tmpl.safe_substitute(
        {
            "style_frag": nav_css
            + style("common.css")
            + style("index.css")
            + footer_css,
            "head_frag": head_frag(title=title, descr=descr),
            "nav_frag": nav_html,
            "title": title,
            "body_frag": body_frag,
            "footer_frag": footer_html,
        }
    )


def render_recognition() -> str:
    with open(TEMPLATES_DIR / "recognition.tmpl") as f:
        tmpl = Template(f.read())

    frontmatter, md_str = read_markdown("recognition.md")

    body_frag = mistletoe.markdown(md_str)
    title = frontmatter["title"]
    descr = frontmatter["description"]

    nav_html, nav_css = nav_frag()
    footer_html, footer_css = footer_frag(edit_url=github_edit_url("recognition.md"))

    return tmpl.safe_substitute(
        {
            "style_frag": nav_css
            + style("common.css")
            + style("index.css")
            + footer_css,
            "head_frag": head_frag(title=title, descr=descr),
            "nav_frag": nav_html,
            "title": title,
            "body_frag": body_frag,
            "footer_frag": footer_html,
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

    nav_html, nav_css = nav_frag()
    footer_html, footer_css = footer_frag()
    return tmpl.safe_substitute(
        {
            "style_frag": nav_css
            + style("common.css")
            + style("cards.css")
            + footer_css,
            "head_frag": head_frag(
                title="Publications", descr="List of my publications"
            ),
            "nav_frag": nav_html,
            "body_frag": pub_links,
            "footer_frag": footer_html,
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

    nav_html, nav_css = nav_frag()
    footer_html, footer_css = footer_frag()
    return tmpl.safe_substitute(
        {
            "style_frag": nav_css
            + style("common.css")
            + style("cards.css")
            + footer_css,
            "head_frag": head_frag(title="Posts", descr="Links to my posts"),
            "nav_frag": nav_html,
            "body_frag": post_links,
            "footer_frag": footer_html,
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

    nav_html, nav_css = nav_frag()
    footer_html, footer_css = footer_frag()
    return tmpl.safe_substitute(
        {
            "style_frag": nav_css
            + style("common.css")
            + style("cards.css")
            + footer_css,
            "head_frag": head_frag(title="Talks", descr="Links to my talks"),
            "nav_frag": nav_html,
            "body_frag": talk_links,
            "footer_frag": footer_html,
        }
    )


def render_tag_page(
    tag: str,
    projects: List[Project],
    talks: List[Talk],
    pubs: List[Pub],
    posts: List[Post],
):
    global BYTES_WR
    global BYTES_RD
    global SMALL_PAGES
    global LARGE_PAGES
    pubs_frag = ""
    if pubs:
        pubs_frag += "<h2>Publications</h2>\n"
        for pub in pubs:
            pubs_frag += pub_card(pub)

    posts_frag = ""
    if posts:
        posts_frag += "<h2>Posts</h2>\n"
        for post in posts:
            posts_frag += post_card(post)

    talks_frag = ""
    if talks:
        talks_frag += "<h2>Talks</h2>\n"
        for talk in talks:
            talks_frag += talk_card(talk)

    projects_frag = ""
    if projects:
        projects_frag += "<h2>Projects</h2>\n"
        for project in projects:
            projects_frag += project_card(project)

    nav_html, nav_css = nav_frag()
    footer_html, footer_css = footer_frag()
    title = f"#{tag.string()}"
    html = template("tag.tmpl").safe_substitute(
        {
            "style_frag": nav_css
            + style("common.css")
            + style("cards.css")
            + style("tag_page.css")
            + footer_css,
            "head_frag": head_frag(title=title),
            "nav_frag": nav_html,
            "title": title,
            "pubs_frag": pubs_frag,
            "posts_frag": posts_frag,
            "talks_frag": talks_frag,
            "projects_frag": projects_frag,
            "footer_frag": footer_html,
        }
    )

    output_path = OUTPUT_DIR / "tag" / tag.string() / "index.html"
    output_path.parent.mkdir(exist_ok=True, parents=True)
    with open(output_path, "w") as f:
        f.write(html)
    TIMER.stop()
    BYTES_WR += file_size(output_path)
    if gzipped_size(output_path) > TCP_SLOW_START:
        LARGE_PAGES += [path]
    else:
        SMALL_PAGES += 1
    TIMER.start()


def render_tags(tags: List[Tag]) -> str:
    body_html = ""
    for tag in sorted(tags, key=lambda t: t.string()):
        body_html += '<div class="tag">\n'
        body_html += f'<a href="/tag/{tag.url_component()}">#{tag.string()}</a>'
        body_html += "</div>\n"
    if body_html:
        body_html = f'<div class="tag-container">\n{body_html}</div>\n'

    nav_html, nav_css = nav_frag()
    footer_html, footer_css = footer_frag()
    return template("tags.tmpl").safe_substitute(
        {
            "style_frag": nav_css + style("common.css") + style("tag.css") + footer_css,
            "head_frag": head_frag(title="Tags", descr="List of all tags"),
            "nav_frag": nav_html,
            "body_frag": body_html,
            "footer_frag": footer_html,
        }
    )


if __name__ == "__main__":
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

    TIMER.start()
    favicons()
    robots_txt()

    project_specs = find_projects()
    projects = [render_project(spec) for spec in project_specs]

    post_specs = find_posts()
    for ps in post_specs:
        preprocess_gallery(ps)
    for ps in post_specs:
        move_post_resources(ps)
    posts = [render_post(spec) for spec in post_specs]
    posts = [p for p in posts if p is not None]

    pubs = load_pubs()

    talk_specs = find_talks()
    talks = [render_talk(spec) for spec in talk_specs]
    talks = [t for t in talks if t is not None]

    link_specs = load_links()
    links = output_links_page(link_specs)

    # generate pages
    for project in projects:
        output_project(project)
    for post in posts:
        output_post(post)
    for talk in talks:
        output_talk(talk)
    for pub in pubs:
        output_pub(pub)

    # collate different kinds of pages for each tag
    all_tags = {}
    for kind, pages in [
        ("projects", projects),
        ("talks", talks),
        ("pubs", pubs),
        ("posts", posts),
    ]:
        for page in pages:
            for tag in page.tags:
                if tag not in all_tags:
                    all_tags[tag] = {
                        "projects": [],
                        "talks": [],
                        "pubs": [],
                        "posts": [],
                    }
                all_tags[tag][kind] += [page]

    for tag, pages in all_tags.items():
        render_tag_page(
            tag, pages["projects"], pages["talks"], pages["pubs"], pages["posts"]
        )

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

    tags_html = render_tags(all_tags.keys())
    output_html("tags", tags_html)

    copy_static()
    copy_thirdparty()

    TIMER.stop()

    print(f"read  {BYTES_RD} B")
    print(f"wrote {BYTES_WR} B")
    print(f"{(BYTES_RD + BYTES_WR) / TIMER.total} B/s")

    print(f"{len(LARGE_PAGES)} large pages / {SMALL_PAGES} small pages")
    for path in LARGE_PAGES:
        print(f"  ({gzipped_size(path)}B) {path} ")
