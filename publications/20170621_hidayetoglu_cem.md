+++
draft = false

date = "2017-06-21"
title = "[CEM] Scalable Parallel DBIM Solutions of Inverse-Scattering Problems"

math = false
publication = "Computing and Electromagnetics International Workshop (CEM), 2017"



selected = false

tags = ["applications"]

+++

**Mert Hidayetoglu, Carl Pearson,  Levent Gurel, Wen-mei Hwu, Weng Cho Chew**

In *Computing and Electromagnetics International Workshop (CEM), 2017*

We report scalable solutions of inverse-scattering problems with the distorted Born iterative method (DBIM) on large number of computing nodes. Distributing forward solutions does not scale well when the number of illuminations is not greater than the number of computing nodes. As a remedy, we distribute both forward solutions and the corresponding forward solvers to improve granularity of DBIM solutions. This paper provides a set of solutions demonstrating good scaling of the proposed parallelization strategy up to 1,024 computing nodes, employing 16,394 processing cores in total.

* [pdf](/pdf/20170621_hidayetoglu_cem.pdf)