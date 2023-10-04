from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Union
import toml
import datetime
from string import Template
from pytz import timezone
import subprocess

import mistletoe
import yaml

TEMPLATES_DIR = Path(__file__).parent / "templates"
POSTS_DIR = Path(__file__).parent / "posts"
PUBS_DIR = Path(__file__).parent / "publications"
STATIC_DIR = Path(__file__).parent / "static"
STYLE_DIR = Path(__file__).parent / "style"

OUTPUT_DIR = Path(__file__).parent / "public"


@dataclass
class PostSpec:
    markdown_path: Path
    is_dir: bool
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


def find_posts() -> List[PostSpec]:
    specs = []

    for post in POSTS_DIR.iterdir():
        if post.is_file():
            specs += [PostSpec(markdown_path=post, is_dir=False)]
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
                        gallery_resources=gallery_resources,
                        resources=resources,
                    )
                ]

    return specs


def read_markdown(path: Path) -> Tuple[Union[str, None], Union[str, None], str]:
    """
    assume +++ delimits toml frontmatter, and --- delimits yaml frontmatter

    returns toml, yaml, markdown
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
        return "".join(toml_lines), None, "".join(md_lines)
    elif len(yaml_delims) >= 2 and yaml_delims[0] == 0:
        yaml_lines = lines[1 : yaml_delims[1]]
        md_lines = lines[yaml_delims[1] + 1 :]
        return None, "".join(yaml_lines), "".join(md_lines)
    else:
        return None, None, "".join(lines)


def maybe_localize_to_mountain(dt: datetime.datetime) -> datetime.datetime:
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        mountain = timezone("US/Mountain")
        return mountain.localize(dt)
    else:
        return dt


def render_post(spec: PostSpec) -> Post:
    print(f"==== render {spec.markdown_path}")
    toml_str, yaml_str, markdown = read_markdown(spec.markdown_path)

    if toml_str:
        header_data = toml.loads(toml_str)
    elif yaml_str:
        header_data = yaml.loads(toml_str)
    title = header_data["title"]
    create_time = header_data["date"]
    create_time = maybe_localize_to_mountain(create_time)
    mod_time = header_data.get("lastmod", create_time)
    mod_time = maybe_localize_to_mountain(mod_time)

    body_html = mistletoe.markdown(markdown)
    return Post(
        spec=spec,
        title=title,
        body_html=body_html,
        create_time=create_time,
        mod_time=mod_time,
    )


def output_post(post: Post):
    if post.spec.is_dir:
        output_html_dir = OUTPUT_DIR / "post" / f"{post.spec.markdown_path.parent.stem}"
    else:
        output_html_dir = OUTPUT_DIR / "post" / f"{post.spec.markdown_path.stem}"
    print(f"==== output {post.spec.markdown_path} -> {output_html_dir}")
    output_html_dir.mkdir(parents=True, exist_ok=True)
    with open(output_html_dir / "index.html", "w") as f:
        f.write(post.body_html)


def find_pubs() -> List[PubSpec]:
    specs = []

    for pub in PUBS_DIR.iterdir():
        if pub.is_file():
            output_dir = Path("publication") / f"{pub.stem}"
            specs += [PubSpec(markdown_path=pub, is_dir=False, output_dir=output_dir)]
        elif pub.is_dir():
            output_dir = Path("publication") / f"{pub.stem}"
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
    toml_str, yaml_str, markdown = read_markdown(spec.markdown_path)

    if toml_str:
        print(toml_str)
        header_data = toml.loads(toml_str)
    elif yaml_str:
        header_data = yaml.safe_load(yaml_str)
    title = header_data["title"]
    create_time = header_data["date"]
    create_time = normalize_to_datetime(create_time)
    create_time = maybe_localize_to_mountain(create_time)
    mod_time = header_data.get("lastmod", create_time)
    mod_time = maybe_localize_to_mountain(mod_time)

    body_html = ""
    body_html += f"<h1>{title}</h1>\n"
    body_html += mistletoe.markdown(markdown)

    return Pub(
        spec=spec,
        title=title,
        body_html=body_html,
        create_time=create_time,
        mod_time=mod_time,
    )


def nav_frag() -> str:
    with open(TEMPLATES_DIR / "navbar_frag.html") as f:
        return f.read()


def navbar_css() -> str:
    with open(STYLE_DIR / "navbar.css") as f:
        return f.read()


def common_css() -> str:
    with open(STYLE_DIR / "common.css") as f:
        return f.read()


def footer_css() -> str:
    with open(STYLE_DIR / "footer.css") as f:
        return f.read()


def footer_frag() -> str:
    now_str = datetime.datetime.now().strftime("%x")
    cp = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True)
    sha = cp.stdout.decode("utf-8").strip()
    html = "<div class=footer>\n"
    html += f"<div>build {sha} on {now_str}</div>\n"
    html += (
        f'<div>copyright Carl Pearson {datetime.datetime.now().strftime("%Y")}</div>\n'
    )
    html += "</div>\n"
    return html


def output_pub(pub: Pub):
    with open(TEMPLATES_DIR / "pub.tmpl", "r") as f:
        tmpl = Template(f.read())

    html = tmpl.safe_substitute(
        {
            "style_frag": navbar_css() + common_css() + footer_css(),
            "header_frag": "",
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

    top_k_posts_frag = "<ul>\n"
    for post in top_k_posts:
        top_k_posts_frag += f"<li>{post.title}</li>\n"
    top_k_posts_frag += "</ul>\n"

    top_k_pubs_frag = "<ul>\n"
    for pub in top_k_pubs:
        top_k_pubs_frag += (
            f'<li><a href="{pub.spec.output_dir}/">{pub.title}</a></li>\n'
        )
    top_k_pubs_frag += "</ul>\n"

    return tmpl.safe_substitute(
        {
            "style_frag": navbar_css() + common_css() + footer_css(),
            "header_frag": "HEADER",
            "nav_frag": nav_frag(),
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


def render_publications() -> str:
    with open(TEMPLATES_DIR / "publications.tmpl") as f:
        tmpl = Template(f.read())

    return tmpl.safe_substitute(
        {
            "style_frag": navbar_css() + common_css() + footer_css(),
            "header_frag": "HEADER",
            "nav_frag": nav_frag(),
            "body_frag": "BODY",
            "footer_frag": footer_frag(),
        }
    )


def output_publications(html):
    output_path = OUTPUT_DIR / "publications" / "index.html"
    output_path.parent.mkdir(exist_ok=True, parents=True)
    print(f"==== write {output_path}")
    with open(output_path, "w") as f:
        f.write(html)


if __name__ == "__main__":
    post_specs = find_posts()
    for ps in post_specs:
        print(ps)
    posts = [render_post(spec) for spec in post_specs]
    for post in posts:
        output_post(post)

    pub_specs = find_pubs()
    for spec in pub_specs:
        print(spec)
    pubs = [render_pub(spec) for spec in pub_specs]
    for pub in pubs:
        output_pub(pub)

    index_html = render_index(
        top_k_posts=sorted(posts, key=lambda p: p.create_time, reverse=True)[0:5],
        top_k_pubs=sorted(pubs, key=lambda p: p.create_time, reverse=True)[0:5],
    )
    output_index(index_html)

    pubs_html = render_publications()
    output_publications(pubs_html)
