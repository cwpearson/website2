+++
title = "Kokkos Ecosystem in the Map of Github"
date = 2024-12-17T00:00:00-0700
lastmod = 2024-12-17T00:00:00-0700
description = ""
tags = []
draft = false

[[gallery_item]]
image = "zoom_1.png"
caption = "The full map of GitHub, annotated to show where the Kokkos ecosystem is."
[[gallery_item]]
image = "zoom_2.png"
caption = "\"AILandia\", the GitHub continent annotated to show the Kokkos ecosystem in SimuVisia."
[[gallery_item]]
image = "zoom_3.png"
caption = "\"SimuVisia\" annotated to show where the Kokkos ecosystem is."
[[gallery_item]]
image = "zoom_4.png"
caption = "Zoomed-in view of \"SimuVisia\" where Kokkos, Kokkos Kernels, and Trilinos are clearly visible."

+++

**this is not my work**

User [anvaka](https://github.com/anvaka) has created a ["Map of Github"](https://anvaka.github.io/map-of-github/) using a public dataset that captures GitHub activity between 2020 and 2023. 

"Dots are close to each other if they have a lot of common stargazers."
* Jaccard similarity between lists of stargazers
* Leiden clustering to cluster the repositories
* A custom layout engine to create the visualization
* ChatGPT to help generate the names (e.g. "SimuVisia")

The source and a more extensive description are available in the [GitHub repository](https://github.com/anvaka/map-of-github).
Additional discussion on [Hacker News](https://news.ycombinator.com/item?id=42426284).