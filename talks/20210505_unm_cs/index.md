---
title: Adding Fast GPU Derived Datatype Handing to Existing MPIs

date: "2021-05-05T00:00:00Z"

tags: [mpi]
---

*May 5th, 2:00 PM, University of New Mexico, Albuquerque, NM*

Invited talk to the Computer Science Department Colloquium

### Abstract

MPI derived datatypes are an abstraction that simplifies handling of non-contiguous data in MPI applications.
These datatypes are recursively constructed at runtime from primitive Named Types defined in the MPI standard.
More recently, the development and deployment of CUDA-aware MPI implementations has encouraged the transition of distributed high-performance MPI codes to use GPUs.
Such implementations allow MPI functions to directly operate on GPU buffers, easing integration of GPU compute into MPI codes.
This talk presents a novel datatype handling strategy for nested strided datatypes on GPUs, and its evaluation on a leadership-class supercomputer that does not have built-in support for such datatypes.
It focuses on the datatype strategy itself, implementation decisions based off measured system performance, and a technique for experimental modifications to closed software systems.

### Link

* [slides](/pdf/20210505_unm_slides.pdf)
* [github](https://github.com/cwpearson/tempi)
* [paper](/pdf/20210621_pearson_hpdc.pdf)