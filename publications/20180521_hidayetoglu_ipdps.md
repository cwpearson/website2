+++
title = "A Fast and Massively-Parallel Solver for Multiple-Scattering Tomographic Image Reconstruction"
date = 2018-05-21
draft = false
authors = ["Mert Hidayetoglu", "Carl Pearson", "Izzat El Hajj", "Levent Gurel", "Weng Cho Chew", "Wen-Mei Hwu"]
tags = ["applications", "GPU"]
venue = "2018 IEEE International Parallel and Distributed Processing Symposium"
url_pdf = "/pdf/20180521_hidayetoglu_ipdps.pdf"
abstract = "We present a massively-parallel solver for large Helmholtz-type inverse scattering problems. The solver employs the distorted Born iterative method for capturing the multiple-scattering phenomena in image reconstructions. This method requires many full-wave forward-scattering solutions in each iteration, constituting the main performance bottleneck with its high computational complexity. As a remedy, we use the multilevel fast multipole algorithm (MLFMA). The solver scales among computing nodes using a two-dimensional parallelization strategy that distributes illuminations in one dimension, and MLFMA sub-trees in the other dimension. Multi-core CPUs and GPUs are used to provide per-node speedup. We demonstrate a 76% efficiency when scaling from 64 GPUs to 4,096 GPUs. The paper provides reconstruction of a 204.8λ×204.8λ image (4M unknowns) executed on 4,096 GPUs in near-real time (almost 2 minutes). To the best of our knowledge, this is the largest full-wave inverse scattering solution to date, in terms of both image size and computational resources."
+++
