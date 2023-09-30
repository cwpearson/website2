+++
title = "Design of https://didillinois.win"
date = 2021-12-18T00:00:00
lastmod = 2021-12-18T00:00:00
draft = false

# Authors. Comma separated list, e.g. `["Bob Smith", "David Jones"]`.
authors = ["Carl Pearson"]

tags = []

summary = "Design of a static site with GNU Makefiles and pandoc"

# Projects (optional).
#   Associate this post with one or more of your projects.
#   Simply enter your project's folder or file name without extension.
#   E.g. `projects = ["deep-learning"]` references 
#   `content/project/deep-learning/index.md`.
#   Otherwise, set `projects = []`.
projects = []

# Featured image
# To use, add an image named `featured.jpg/png` to your project's folder. 
[image]
  # Caption (optional)
  caption = ""

  # Focal point (optional)
  # Options: Smart, Center, TopLeft, Top, TopRight, Left, Right, BottomLeft, Bottom, BottomRight
  focal_point = "Center"

  # Show image only in page previews?
  preview_only = true


categories = []

# Set captions for image gallery.


+++

Introducing https://didillinois.win, a static site with some Illinois sports updates.

[Did Illinois Win](https://didillinois.win) is a static site that shows an overview of the current season for each of the University of Illinois sports that I follow.
The source for the website is available here

## Objectives

The content on the site changes infrequently and is relatively simple.
I settled on a static site, which also makes it much easier to
* load quickly
* display well on mobile and desktop
* not require any javascript (I've never written any javascript before)

## Implementation (on [github](https://github.com/cwpearson/didillinoiswin))

Each table is defined in a separate markdown file that looks something like this:

```md
---
title: "2021 Football"
result: "yes"
---

| Date | Opponent | Result |
|-|-|-|
| 11/27/2021 | vs Northwestern  | [W 47-14](https://www.espn.com/college-football/game/_/gameId/401282722) | 
| 11/20/2021 | at Iowa  | [L 23-33](https://www.espn.com/college-football/game/_/gameId/401282721) | 
...
```

The first part of the file is the "frontmatter", which defines the title and the result that are floating above the table.
The rest is just a markdown table with a column for the game date, the opponent, and the result.
These files are updated manually by the site administrator (me) and then converted to HTML using [Pandoc](http://pandoc.org) ("a universal document converter").

```
pandoc --template static/template.html input.md -o output.html
```
* `--template static/template.html`: this argument specifies the template file (more on that below)
* `input.md`: this positional argument specifies the markdown file to convert
* `-o`: this specifies the output HTML file.

The template file looks likes this:

```html
<h1 class="sport">$title$</h1>
<h1 class="$result$">$result$</h1>

<!-- put the table in a div so we can center with CSS -->
<div align="center">
    $body$
</div>
```
* `$title$` and `$result$`: the text from the markdown frontmatter is subsituted in these fields.
* `$body$`: the rest of the markdown content is substituted here after being transformed.

This produces a fragment (not a complete webpage) of HTML for each of the sports.
These fragments are combined with an HTML header fragment...

```html
<!doctype html>
<html>

<head>
    <meta charset="UTF-8">
    <meta name="description" content="Find out if Illinois NCAA athletics won">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Did Illinois Win?</title>
    <link rel="stylesheet" href="style.css">

    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-WQY4PM3M68"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag() { dataLayer.push(arguments); }
        gtag('js', new Date());

        gtag('config', 'G-WQY4PM3M68');
    </script>

</head>
```

...and stitched into a webpage using bash:

```bash
cat header.html > index.html
echo "<div class="row">"  >> index.html
echo "<div class="column">" >> index.html
cat basketball.html >> index.html
echo "</div>" >> index.html
echo "<div class="column">" >> index.html
cat football.html >> index.html
echo "</div>" >> index.html
echo "</div>" >> index.html 
echo "<div class="row">"  >> index.html
echo "<div class="column">" >> index.html
cat volleyball.html >> index.html
echo "</div>" >> index.html
echo "</div>" >> index.html 
```

The combind result is that each sport's HTML fragment is put into its own div.
The divs are organized into a table of `row` and `column`.
A bit of CSS is used to handle the responsive layout of the divs wrapping the sports.

## Hosting

I chose to host on Netlify.
Instead of creating an `index.html` file and uploading it, Netlify can run some automated steps every time there is a push to a github repository.
I automated the generation of the website from the markdown files using GNU Make.
Then, on Netlify under "Site Settings" > "Build and Deploy", I specified `make` as the build command.
Netlify will clone the repository every time I push a modification to the markdown files, run `make` to produce `index.html`, and serve that as the site.

As of this writing, Netlify provides 100GB bandwidth and 300 build minutes, which is more than sufficient for a 0-traffic small static website.
Netlify [provides instructions](https://docs.netlify.com/domains-https/custom-domains/configure-external-dns/) for how to configure the external DNS.



## DNS

I purchased the `didillinois.win` domain from Google.
I then had to aim the domain at where the site was hosted on Netlify:

| Host Name | Type | TTL | Data |
|-|-|-|-|
| didillinois.win     | A    | 1 hour | 104.198.14.52               | 
| www.didillinois.win |CNAME | 1 hour | didillinoiswin.netlify.app. |
