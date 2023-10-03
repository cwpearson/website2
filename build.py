from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Union
import toml
import datetime
from string import Template
from pytz import timezone

import mistletoe

TEMPLATES_DIR = Path(__file__).parent / "templates"
POSTS_DIR = Path(__file__).parent / "posts"
PUBS_DIR = Path(__file__).parent / "publications"
STATIC_DIR = Path(__file__).parent / "static"

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


def read_markdown(path: Path) -> Tuple[Union[str, None], str]:
    toml = ""
    md = ""

    lines = []
    with open(path, "r") as f:
        lines = [line for line in f]

    delims = []
    for li, line in enumerate(lines):
        if line.strip() == "+++" or line.strip() == "---":
            delims += [li]

    # there's a header if the delimiter is found at least twice and the file starts with it
    if len(delims) >= 2 and delims[0] == 0:
        toml_lines = lines[1 : delims[1]]
        md_lines = lines[delims[1] + 1 :]
        return "".join(toml_lines), "".join(md_lines)
    else:
        return None, "".join(lines)


def maybe_localize_to_mountain(dt: datetime.datetime) -> datetime.datetime:
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        mountain = timezone("US/Mountain")
        return mountain.localize(dt)
    else:
        return dt


def render_post(spec: PostSpec) -> Post:
    print(f"==== render {spec.markdown_path}")
    toml_str, markdown = read_markdown(spec.markdown_path)

    header_data = toml.loads(toml_str)
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


def render_index(top_k_posts: List[Post]) -> str:
    with open(TEMPLATES_DIR / "index.tmpl") as f:
        tmpl = Template(f.read())

    top_k_posts_frag = "<ul>\n"
    for post in top_k_posts:
        top_k_posts_frag += f"<li>{post.title}</li>\n"
    top_k_posts_frag += "</ul>\n"

    return tmpl.safe_substitute(
        {
            "style_frag": "",
            "header_frag": "HEADER",
            "nav_frag": "NAV",
            "top_k_posts_frag": top_k_posts_frag,
        }
    )


def output_index(html):
    output_path = OUTPUT_DIR / "index.html"
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

    index_html = render_index(
        top_k_posts=sorted(posts, key=lambda p: p.create_time, reverse=True)[0:5]
    )
    output_index(index_html)
