---
title: Node-Aware Stencil Communication for Heterogeneous Supercomputers
event: C3SR Bi-weekly Technical Seminar
event_url:

location: Coordinated Science Lab 216
address:
  street: 1308 W Main St
  city: Urbana
  region: IL
  postcode: '61801'
  country: United States

summary: Optimizing Multi-GPU Stencil Communication
abstract: "High-performance distributed computing systems increasingly feature nodes that have multiple CPU sockets and multiple GPUs. The communication bandwidth between these components is non-uniform. Furthermore, these systems can expose different communication capabilities between these components. For communication-heavy applications, optimally using these capabilities is challenging and essential for performance.

This work presents approaches for automatic data placement and communication implementation for 3D stencil codes on multi-GPU nodes with non-homogeneous communication performance and capabilities. Benchmarking results in the Summit system show that choices in placement can result in a 20% improvements in single-node exchange, and communication specialization can yield a further 6x improvement in exchange time in a single node, and a 16% improvement at 1536 GPUs."

# Talk start and end times.
#   End time can optionally be hidden by prefixing the line with `#`.
time_start: 2020-02-28T14:00:00-06:00
time_end: 2020-02-28T15:00:00-06:00
all_day: false

authors: ["Carl Pearson"]
tags: ["stencil", "GPU"]

# Is this a featured talk? (true/false)
featured: true

image:
  caption: 'Image credit: [**Unsplash**](https://unsplash.com/photos/bzdhc5b3Bxs)'
  focal_point: Right

links:
url_code: ""
url_pdf: ""
url_slides: "pdf/20200228_c3sr_stencil.pdf"
url_video: ""

# Markdown Slides (optional).
#   Associate this talk with Markdown slides.
#   Simply enter your slide deck's filename without extension.
#   E.g. `slides = "example-slides"` references `content/slides/example-slides.md`.
#   Otherwise, set `slides = ""`.
slides: ""

# Projects (optional).
#   Associate this post with one or more of your projects.
#   Simply enter your project's folder or file name without extension.
#   E.g. `projects = ["internal-project"]` references `content/project/deep-learning/index.md`.
#   Otherwise, set `projects = []`.
projects:
- stencil_library

# Enable math on this page?
math: true
---
