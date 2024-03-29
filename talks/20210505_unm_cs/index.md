---
title: Adding Fast GPU Derived Datatype Handing to Existing MPIs
tags: [mpi, GPU]
time_start: 2021-05-05T14:00:00-06:00
location: "University of New Mexico, Albuquerque, NM"
event: UNM Computer Science Department Colloquium
how_invited: Invited talk
abstract: "MPI derived datatypes are an abstraction that simplifies handling of non-contiguous data in MPI applications. These datatypes are recursively constructed at runtime from primitive Named Types defined in the MPI standard. More recently, the development and deployment of CUDA-aware MPI implementations has encouraged the transition of distributed high-performance MPI codes to use GPUs. Such implementations allow MPI functions to directly operate on GPU buffers, easing integration of GPU compute into MPI codes. This talk presents a novel datatype handling strategy for nested strided datatypes on GPUs, and its evaluation on a leadership-class supercomputer that does not have built-in support for such datatypes. It focuses on the datatype strategy itself, implementation decisions based off measured system performance, and a technique for experimental modifications to closed software systems."
url_slides: /pdf/20210505_unm_slides.pdf
url_code: https://github.com/cwpearson/tempi
---

### Link

* [github](https://github.com/cwpearson/tempi)
* [paper](/pdf/20210621_pearson_hpdc.pdf)