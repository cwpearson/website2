+++
title = "Paper Accepted at ICPE 2019!"
subtitle = ""
date = 2019-03-11T00:00:00
lastmod = 2019-03-11T00:00:00
draft = false

# Authors. Comma separated list, e.g. `["Bob Smith", "David Jones"]`.
authors = ["Carl Pearson"]

tags = []

summary = "Paper accepted at ICPE 2019"

# Projects (optional).
#   Associate this post with one or more of your projects.
#   Simply enter your project's folder or file name without extension.
#   E.g. `projects = ["deep-learning"]` references 
#   `content/project/deep-learning/index.md`.
#   Otherwise, set `projects = []`.
# projects = ["internal-project"]

# Featured image
# To use, add an image named `featured.jpg/png` to your project's folder. 
[image]
  # Caption (optional)
  caption = "Image credit: [**ICPE**](https://icpe2019.spec.org/)"

  # Focal point (optional)
  # Options: Smart, Center, TopLeft, Top, TopRight, Left, Right, BottomLeft, Bottom, BottomRight
  focal_point = "Center"

  # Show image only in page previews?
  preview_only = true


categories = []
+++

My paper *Evaluating Characteristics of CUDA Communication Primitives on High-Bandwidth Interconnects* is a **best paper nominee** and received an **artifact evaluation stamp**! It will appear  in [session 9][program] on April 10th at the International Conference on Performance Engineering (ICPE) in Mubmai, April 7-11. This work was started during an internsip at IBM's T.J. Watson research center in New York, and my colleagues from the IMPACT research group at the University of Illinois as well as IBM Research are co-authors on the paper.

Once it is published, you will be able to find the full paper on this site, and on the IMPACT research group website.

The code is available on Github as part of the [Scope](https://github.com/c3sr/scope) project under [Comm|Scope](https://github.com/c3sr/comm_scope).

Here's the abstract from the paper:

> Data-intensive applications such as machine learning and analytics have created a demand for faster interconnects to avert the memory bandwidth wall and allow GPUs to be effectively leveraged for lower compute intensity tasks.
This has resulted in wide adoption of heterogeneous systems with varying underlying interconnects, and has delegated the task of understanding and copying data to the system or application developer.
No longer is a malloc followed by memcpy the only or dominating modality of data transfer; application developers are faced with additional options such as unified memory and zero-copy memory.
Data transfer performance on these systems is now impacted by many factors including data transfer modality, system interconnect hardware details, CPU caching state, CPU power management state, driver policies, virtual memory paging efficiency, and data placement.
>
> This paper presents Comm|Scope, a set of microbenchmarks designed for system and application developers to understand memory transfer behavior across different data placement and exchange scenarios.
Comm|Scope comprehensively measures the latency and bandwidth of CUDA data transfer primitives, and avoids common pitfalls in ad-hoc measurements by controlling CPU caches, clock frequencies, and avoids measuring synchronization costs imposed by the measurement methodology where possible.
This paper also presents an evaluation of Comm|Scope on systems featuring the POWER and x86 CPU architectures and PCIe 3, NVLink 1, and NVLink 2 interconnects.
These systems are chosen as representative configurations of current high-performance GPU platforms.
Comm|Scope measurements can serve to update insights about the relative performance of data transfer methods on current systems.
This work also reports insights for how high-level system design choices affect the performance of these data transfers, and how developers can optimize applications on these systems.

Thanks to my co-authors:

* Abdul Dakkak (University of Illinois Urbana-Champaign)
* Sarah Hashash (University of Illinois Urbana-Champaign)
* Cheng Li (University of Illinois Urbana-Champaign)
* I-Hsin Chung (IBM T.J. Watson Research)
* Jinjun Xiong (IBM T.J. Watson Research)
* Wen-Mei Hwu (University of Illinois Urbana-Champaign)

and thanks for the support of:

* IBM-ILLINOIS Center for Cognitive Computing Systems Research (C3SR) - a research collaboration as part of the IBM AI Horizon Network.
* The Blue Waters sustained-petascale computing project, which is supported by the National Science Foundation award OCI-0725070 and the state of Illinois. 
Blue Waters is a joint effort of the University of Illinois at Urbana-Champaign and its National Center for Supercomputing Applications.

[program]: https://icpe2019.spec.org/conference-program.html#session9

