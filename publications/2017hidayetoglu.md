+++
title = "[ACES] Large Inverse-Scattering Solutions with DBIM on GPU-Enabled Supercomputers"

date = 2017-03-28
authors = ["Mert Hidayetoglu", "Carl Pearson", "Weng Cho Chew", "Levent Gurel", "Wen-mei Hwu"]


math = false
tags = ["applications"]
draft = false
+++

**Mert Hidayetoglu, Carl Pearson, Weng Cho Chew, Levent Gurel, Wen-mei Hwu**

In *Applied and Computational Electromagnetics Symposium, 2017*

We report inverse-scattering solutions on supercomputers involving large numbers of graphics processing units (GPUs). The distorted-Born iterative method (DBIM) is employed for the iterative inversions. In each iteration, the required forward problems are distributed among computing nodes equipped with GPUs, and solved with the multilevel fast multipole algorithm. A tomographic reconstruction of a synthetic object with a linear dimension of one hundred wavelengths is obtained on 256 GPUs. The results show that DBIM obtains images approximately four times faster on GPUs, compared to parallel executions on traditional CPU-only computing nodes.

* [pdf](/pdf/2017aces-dbim.pdf)