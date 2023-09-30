from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Union

import mistletoe

POSTS_DIR = Path(__file__).parent / "posts"
PUBS_DIR = Path(__file__).parent / "publications"
STATIC_DIR = Path(__file__).parent / "static"

OUTPUT_DIR = Path(__file__).parent / "public"


@dataclass
class Post:
    toml: str
    markdown: str


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
        toml_lines = lines[0 : delims[1]]
        md_lines = lines[delims[1] + 2 :]
        return "".join(toml_lines), "".join(md_lines)
    else:
        return None, "".join(lines)


def render_post(spec: PostSpec):
    if spec.is_dir:
        output_html_dir = OUTPUT_DIR / "post" / f"{spec.markdown_path.parent.stem}"
    else:
        output_html_dir = OUTPUT_DIR / "post" / f"{spec.markdown_path.stem}"
    print(f"==== render {spec.markdown_path} -> {output_html_dir}")
    toml, markdown = read_markdown(spec.markdown_path)

    html = mistletoe.markdown(markdown)

    output_html_dir.mkdir(parents=True, exist_ok=True)
    with open(output_html_dir / "index.html", "w") as f:
        f.write(html)


if __name__ == "__main__":
    post_specs = find_posts()
    for ps in post_specs:
        print(ps)

    for post_spec in post_specs:
        render_post(post_spec)
