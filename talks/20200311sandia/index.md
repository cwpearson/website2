---
title: Optimizing Communication for CPU/GPU Nodes
event: Sandia National Labs Seminar
event_url:

location: Sandia National Labs
address:
  street:
  city: Albuquerque, NM
  region: 
  postcode: 
  country: USA

summary: Optimizing Multi-GPU Stencil Communication
abstract: "High-performance distributed computing systems increasingly feature nodes that have multiple CPU sockets and multiple GPUs. The communication bandwidth between those components depends on the underlying hardware and system software. Consequently, the bandwidth between these components is non-uniform, and these systems can expose different communication capabilities between these components. Optimally using these capabilities is challenging and essential consideration on emerging architectures. This talk starts by describing the performance of different CPU-GPU and GPU-GPU communication methods on nodes with high-bandwidth NVLink interconnects. This foundation is then used for domain partitioning, data placement, and communication planning in a CUDA+MPI 3D stencil halo exchange library."

# Talk start and end times.
#   End time can optionally be hidden by prefixing the line with `#`.
date: "2020-03-11T9:00:00Z"
date_end: "2020-03-11T10:00:00Z"
all_day: false

# Schedule page publish date (NOT talk date).
publishDate: "2020-03-11T00:00:00Z"

authors: ["Carl Pearson"]
tags: []

# Is this a featured talk? (true/false)
featured: true

image:
  caption: ''
  focal_point: Right

links:
url_code: ""
url_pdf: "pdf/20200311_sandia_stencil.pdf"
url_slides: ""
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
