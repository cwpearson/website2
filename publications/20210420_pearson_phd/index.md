+++
title = "Movement and Placement of Non-Contiguous Data In Distributed GPU Computing"
date = 2021-04-20T00:00:00  # Schedule page publish date.
draft = false
tags = ["stencil", "mpi"]
venue = "Ph.D. Dissertation"
authors = ["Carl Pearson"]
abstract = """<p>
Steady increase in accelerator performance has driven demand for faster interconnects to avert the memory bandwidth wall.
This has resulted in wide adoption of heterogeneous systems with varying underlying interconnects, and has delegated the task of understanding and copying data to the system or application developer.
Data transfer performance on these systems is now impacted by many factors including data transfer modality, system interconnect hardware details, CPU caching state, CPU power management state, driver policies, virtual memory paging efficiency, and data placement.
</p><p>
This work finds that empirical communication measurements can be used to automatically schedule and execute intra- and inter-node communication in a modern heterogeneous system, providing ``hand-tuned'' performance without the need for complex or error-prone communication development at the application level.
Empirical measurements are provided by a set of microbenchmarks designed for system and application developers to understand memory transfer behavior across different data placement and exchange scenarios.
These benchmarks are the first comprehensive evaluation of all GPU communication primitives.
For communication-heavy applications, optimally using communication capabilities is challenging and essential for performance.
Two different approaches are examined.
The first is a high-level 3D stencil communication library, which can automatically create a static communication plan based on the stencil and system parameters.
This library is able to reduce iteration time of a state-of-the-art stencil code by $1.45\times$ at 3072 GPUs and 512 nodes.
The second is a more general MPI interposer library, with novel non-contiguous data handling and runtime implementation selection for MPI communication primitives.
A portable pure-MPI halo exchange is brought to within half the speed of the stencil-specific library, supported by a five order-of-magnitude improvement in MPI communication latency for non-contiguous data.</p>"""
+++

* [pdf](/pdf/20210420_pearson_phd.pdf)
* [Comm|Scope (github)](https://github.com/c3sr/comm_scope)
* [Stencil (github)](https://github.com/cwpearson/stencil)
* [TEMPI (github)](https://github.com/cwpearson/tempi)