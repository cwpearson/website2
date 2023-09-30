+++
title = "[HPEC] Update on Triangle Counting on GPU"
date = 2019-08-22T00:00:00  # Schedule page publish date.
draft = false

tags = ["applications"]
+++

**Carl Pearson, Mohammad Almasri, Omer Anjum, Vikram S. Mailthody, Zaid Qureshi, Rakesh Nagi, Jinjun Xiong, Wen-Mei Hwu**

In *2019 IEEE High Performance Extreme Computing Conference*.

This work presents an update to the triangle-counting portion of the subgraph isomorphism static graph challenge.  This  work  is  motivated  by  a  desire  to  understand the  impact  of  CUDA  unified  memory on the triangle-counting problem. First, CUDA unified memory is used to overlap reading large graph data from disk with graph data structures in GPU memory. Second, we use CUDA unified memory hintsto solve multi-GPU performance scaling challenges present in our last submission. Finally, we improve the single-GPU kernel performance from our past submission by introducing a work-stealing dynamic algorithm GPU kernel with persistent threads, which makes performance adaptive for large graphs withoutrequiring a graph analysis phase.

* [pdf](/pdf/2019_pearson_hpec.pdf)
* [poster](/pdf/2019_pearson_hpec_poster.pdf)