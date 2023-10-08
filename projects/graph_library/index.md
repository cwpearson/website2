---
title: Graph Library
summary: Accelerating Static Graph Operations
tags:
- impact
- c3sr
date: "2016-04-27T00:00:00Z"

# Optional external URL for project (replaces project detail page).
external_link: ""

image:
  caption: 
  focal_point: Smart

links:
- icon: github
  icon_pack: fab
  name: Pangolin Graph Library
  url: https://github.com/c3sr/pangolin
- icon: link
  icon_pack: fa
  name: Pangolin C++ API Documentation
  url: https://pangolin-docs.netlify.app/
- icon: github
  icon_pack: fab
  name: Graph Challenge
  url: https://github.com/c3sr/graph_challenge
- icon: github
  icon_pack: fab
  name: Graph Dataset Tools
  url: https://github.com/cwpearson/graph-datasets2
- icon: link
  icon_pack: fa
  name: Graph Dataset Statistics
  url: https://graph-datasets-stats.netlify.com

url_code: ""
url_pdf: ""
url_slides: ""
url_video: ""

# Slides (optional).
#   Associate this project with Markdown slides.
#   Simply enter your slide deck's filename without extension.
#   E.g. `slides = "example-slides"` references `content/slides/example-slides.md`.
#   Otherwise, set `slides = ""`.
slides: ""
---

This project grew out of a 2018 graph challenge submission that I was tangentially involved in.
In 2019 I took charge of the triangle counting submission, where I implemented a variety of GPU triangle counting approaches.
This library contains those implementations, as well as k-truss decompositions written by my colleague Mohammad Almasri.
It also contains a fair amount of utility code, including sparse and dense data structures, system topology discovery code and search/load-balancing algorithms.