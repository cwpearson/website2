+++
title = "Benchmarking CUDA Communication Primitives on High-Bandwidth Interconnects"
draft = false

# Talk start and end times.
#   End time can optionally be hidden by prefixing the line with `#`.
time_start = 2019-06-05T11:00:00
time_end = 2019-06-05T12:50:00

# Authors. Comma separated list, e.g. `["Bob Smith", "David Jones"]`.
authors = ["Carl Pearson"]

# Abstract and optional shortened version.
abstract = """Data-intensive applications such as machine learning and analytics have created a demand for faster interconnects to avert the memory bandwidth wall and allow GPUs to be effectively leveraged for lower compute intensity tasks. This has resulted in wide adoption of heterogeneous systems with varying underlying interconnects, and has delegated the task of understanding and copying data to the system or application developer. No longer is a malloc followed by memcpy the only or dominating modality of data transfer; application developers are faced with additional options such as unified memory and zero-copy memory. Data transfer performance on these systems is now impacted by many factors including data transfer modality, system interconnect hardware details, CPU caching state, CPU power management state, driver policies, virtual memory paging efficiency, and data placement.

This talk presents Comm|Scope, a set of microbenchmarks designed for system and application developers to understand memory transfer behavior across different data placement and exchange scenarios.
Comm|Scope comprehensively measures the latency and bandwidth of CUDA data transfer primitives, and avoids common pitfalls in ad-hoc measurements by controlling CPU caches, clock frequencies, and avoids measuring synchronization costs imposed by the measurement methodology where possible.
This paper also presents an evaluation of Comm|Scope on systems featuring the POWER and x86 CPU architectures and PCIe 3, NVLink 1, and NVLink 2 interconnects.
These systems are chosen as representative configurations of current high-performance GPU platforms.
Comm|Scope measurements can serve to update insights about the relative performance of data transfer methods on current systems.
This work also reports insights for how high-level system design choices affect the performance of these data transfers, and how developers can optimize applications on these systems."""
abstract_short = "This paper presents Comm|Scope, a set of microbenchmarks designed for system and application developers to understand memory transfer behavior across different data placement and exchange scenarios."

# Name of event and optional event URL.
event = "ADA Liason Meeting"
event_url = ""

# Location of event.
location = "Online"

# Is this a selected talk? (true/false)
selected = false

# Projects (optional).
#   Associate this talk with one or more of your projects.
#   Simply enter your project's folder or file name without extension.
#   E.g. `projects = ["deep-learning"]` references 
#   `content/project/deep-learning/index.md`.
#   Otherwise, set `projects = []`.
projects = ["scope"]

# Tags (optional).
#   Set `tags = []` for no tags, or use the form `tags = ["A Tag", "Another Tag"]` for one or more tags.
tags = ["microbenchmark", "bandwidth", "latency", "CUDA", "nvlink", "pcie", "POWER8", "POWER9", "x86", "cache", "GPU"]

# Slides (optional).
#   Associate this talk with Markdown slides.
#   Simply enter your slide deck's filename without extension.
#   E.g. `slides = "example-slides"` references 
#   `content/slides/example-slides.md`.
#   Otherwise, set `slides = ""`.
slides = ""

# Links (optional).
url_pdf = ""
url_slides = ""
url_video = ""
url_code = ""

# Does the content use math formatting?


# Featured image
# To use, add an image named `featured.jpg/png` to your page's folder. 
[image]
  # Caption (optional)
  caption = ""

  # Focal point (optional)
  # Options: Smart, Center, TopLeft, Top, TopRight, Left, Right, BottomLeft, Bottom, BottomRight
  focal_point = "Right"
+++

This talk is related to work published in ICPE.
You can find the paper [here](/publication/20190410_pearson_icpe).

