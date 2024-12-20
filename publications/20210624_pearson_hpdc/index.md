+++
title = "TEMPI: An Interposed MPI Library with a Canonical Representation of CUDA-aware Datatypes"
date = 2021-06-24T00:00:00  # Schedule page publish date.
draft = false
tags = ["stencil", "MPI", "MPI datatypes", "Summit"]
venue = "2021 ACM Symposium on High-Performance Parallel and Distributed Computing"
authors = ["Carl Pearson", "Kun Wu", "I-Hsin Chung", "Jinjun Xiong", "Wen-Mei Hwu"]
url_poster = "/pdf/20210624_pearson_hpdc_poster.pdf"
url_pdf = "/pdf/20210624_pearson_hpdc.pdf"
url_arxiv = "https://arxiv.org/abs/2012.14363"
url_github = "https://github.com/cwpearson/tempi"
url_slides = "/pdf/20210624_pearson_hpdc_slides.pdf"
url_video = "https://www.youtube.com/watch?v=H-fbTWr85qw"
abstract = " MPI derived datatypes are an abstraction that simplifies handling of non-contiguous data in MPI applications. These datatypes are recursively constructed at runtime from primitive Named Types defined in the MPI standard. More recently, the development and deployment of CUDA-aware MPI implementations has encouraged the transition of distributed high-performance MPI codes to use GPUs. Such implementations allow MPI functions to directly operate on GPU buffers, easing integration of GPU compute into MPI codes. This work first presents a novel datatype handling strategy for nested strided datatypes, which finds a middle ground between the specialized or generic handling in prior work. This work also shows that the performance characteristics of non-contiguous data handling can be modeled with empirical system measurements, and used to transparently improve MPI_Send/Recv latency. Finally, despite substantial attention to non-contiguous GPU data and CUDA-aware MPI implementations, good performance cannot be taken for granted. This work demonstrates its contributions through an MPI interposer library, TEMPI. TEMPI can be used with existing MPI deployments without system or application changes. Ultimately, the interposed-library model of this work demonstrates MPI_Pack speedup of up to 242,000× and MPI_Send speedup of up to 59,000x compared to the MPI implementation deployed on a leadership-class supercomputer. This yields speedup of more than 917x in a 3D halo exchange with 3072 processes."
+++
