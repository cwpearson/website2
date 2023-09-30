+++
title = "[IWOPH] NUMA-Aware Data-Transfer Measurements for Power/NVLink Multi-GPU Systems"
date = 2018-06-28
draft = false

+++

**Carl Pearson, I-Hsin Chung, Zehra Sura, Jinjun Xiong, Wen-Mei Hwu**

In *International Workshop on OpenPower in HPC (IWOPH) 2018*

High-performance computing increasingly relies on heterogeneous systems with specialized hardware accelerators to improve application performance. For example, NVIDIA’s CUDA programming system and general-purpose GPUs have emerged as a widespread accelerator in HPC systems. This trend has exacerbated challenges of data placement as accelerators often have fast local memories to fuel their computational demands, but slower interconnects to feed those memories. Crucially, real-world data-transfer performance is strongly influenced not just by the underlying hardware, but by the capabilities of the programming systems. Understanding how application performance is affected by the logical communication exposed through abstractions, as well as the underlying system topology, is crucial for developing high-performance applications and architectures. This report presents initial data-transfer microbenchmark results from two POWER-based systems obtained during work towards developing an automated system performance characterization tool.

* [pdf](/pdf/20180628-iwoph.pdf)
* [slides](/pdf/20180628-iwoph-slides.pdf)