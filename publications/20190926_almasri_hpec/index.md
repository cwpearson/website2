+++
title = "[HPEC] Update on k-truss Decomposition on GPU"
date = 2019-08-22  # Schedule page publish date.
draft = false
+++

**Mohammad Almasri, Omer Anjum, Carl Pearson, Vikram S. Mailthody, Zaid Qureshi, Rakesh Nagi, Jinjun Xiong, Wen-Mei Hwu**

In *2019 IEEE High Performance Extreme Computing Conference*

In this paper, we present an update to our previous submission on k-truss decomposition from Graph Challenge 2018. 
For single GPU k-truss implementation, we propose multiple algorithmic optimizations that significantly improve performance by up to 35.2x (6.9x on average) compared to our previous GPU implementation. In addition, we present a scalable multi-GPU implementation in which each GPU handles a different 'k' value.
Compared to our prior multi-GPU implementation,the proposed approach is faster by up to 151.3x (78.8x on average). In case when the edges with only maximal k-truss are sought, incrementing the 'k' value in each iteration is inefficient particularly for graphs with large maximum k-truss.
Thus, we propose binary search for the 'k' value to find the maximal k-truss. The binary search approach on a single GPU is up to 101.5 (24.3x on average) faster than our 2018 $k$-truss submission. 
Lastly, we  show that the proposed binary search finds the maximum k-truss for "Twitter" graph dataset having 2.8 billion bidirectional edges in just 16 minutes on a single V100 GPU.

* [pdf](/pdf/2019_almasri_hpec.pdf)
* [slides](/pdf/2019_almasri_hpec_slides.pdf)