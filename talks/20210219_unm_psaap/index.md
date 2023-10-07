---
title: Adding Fast GPU Derived Datatype Handing to Existing MPIs

date: "2021-02-15T00:00:00Z"

tags: [mpi]
---

*February 19th, 1:00 PM, University of New Mexico, Albuquerque, NM*

Invited talk to the PSAAP Colloquium at University of New Mexico Computer Science

### Abstract

MPI derived datatypes are an abstraction that simplifies handling of non-contiguous data in MPI applications. These datatypes are recursively constructed at runtime from primitive Named Types defined in the MPI standard. More recently, the development and deployment of CUDA-aware MPI implementations has encouraged the transition of distributed high-performance MPI codes to use GPUs. Such implementations allow MPI functions to directly operate on GPU buffers, easing integration of GPU compute into MPI codes. Despite substantial attention to CUDA-aware MPI implementations, they continue to offer cripplingly poor GPU performance when manipulating derived datatypes on GPUs. This work presents a new MPI library, TEMPI, to address this issue. TEMPI first introduces a common datatype to represent equivalent MPI derived datatypes. TEMPI can be used as an interposed library on existing MPI deployments without system or application changes. Furthermore, this work presents a performance model of GPU derived datatype handling, demonstrating that previously preferred “one-shot” methods are not always fastest.

### Link

* [slides](/pdf/20210219_unm_slides.pdf)
* [github](https://github.com/cwpearson/tempi)
* [pdf](/pdf/20210121_pearson_arxiv.pdf)
* [arxiv](https://arxiv.org/abs/2012.14363)