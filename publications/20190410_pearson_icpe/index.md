+++
title = "Evaluating Characteristics of CUDA Communication Primitives on High-Bandwidth Interconnects"
date = 2019-04-09  # Schedule page publish date.
draft = false
tags = ["benchmark", "nvlink", "pcie", "V100", "P100"]
authors = ["Carl Pearson", "Adbul Dakkak", "Sarah Hashash", "Cheng Li", "I-Hsin Chung", "Jinjun Xiong", "Wen-Mei Hwu"]
venue = "2019 ACM/SPEC International Conference on Performance Engineering"
url_pdf = "/pdf/20190410_pearson_icpe.pdf"
url_code = "https://github.com/c3sr/comm_scope"
abstract = """
<p>Data-intensive applications such as machine learning and analytics have created a demand for faster interconnects to avert the memory bandwidth wall and allow GPUs to be effectively leveraged for lower compute intensity tasks. This has resulted in wide adoption of heterogeneous systems with varying underlying interconnects, and has delegated the task of understanding and copying data to the system or application developer. No longer is a malloc followed by memcpy the only or dominating modality of data transfer; application developers are faced with additional options such as unified memory and zero-copy memory. Data transfer performance on these systems is now impacted by many factors including data transfer modality, system interconnect hardware details, CPU caching state, CPU power management state, driver policies, virtual memory paging efficiency, and data placement.
</p><p>
This paper presents Comm|Scope, a set of microbenchmarks designed for system and application developers to understand memory transfer behavior across different data placement and exchange scenarios.
Comm|Scope comprehensively measures the latency and bandwidth of CUDA data transfer primitives, and avoids common pitfalls in ad-hoc measurements by controlling CPU caches, clock frequencies, and avoids measuring synchronization costs imposed by the measurement methodology where possible.
This paper also presents an evaluation of Comm|Scope on systems featuring the POWER and x86 CPU architectures and PCIe 3, NVLink 1, and NVLink 2 interconnects.
These systems are chosen as representative configurations of current high-performance GPU platforms.
Comm|Scope measurements can serve to update insights about the relative performance of data transfer methods on current systems.
This work also reports insights for how high-level system design choices affect the performance of these data transfers, and how developers can optimize applications on these systems.</p>
"""
+++
* Best Paper for the ICPE research track papers
* Functional ACM Artifact Evaluation.

<img src="/img/acm_artifact_functional.jpg" alt="functional artifact" width="200"/>

```bibtex
@inproceedings{10.1145/3297663.3310299,
author = {Pearson, Carl and Dakkak, Abdul and Hashash, Sarah and Li, Cheng and Chung, I-Hsin and Xiong, Jinjun and Hwu, Wen-Mei},
title = {Evaluating Characteristics of CUDA Communication Primitives on High-Bandwidth Interconnects},
year = {2019},
isbn = {9781450362399},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3297663.3310299},
doi = {10.1145/3297663.3310299},
booktitle = {Proceedings of the 2019 ACM/SPEC International Conference on Performance Engineering},
pages = {209–218},
numpages = {10},
keywords = {numa, cuda, power, nvlink, x86, gpu, benchmarking},
location = {Mumbai, India},
series = {ICPE ’19}
}
```


* [project](/project/scope)
