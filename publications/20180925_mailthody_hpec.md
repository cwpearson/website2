+++
title = "Collaborative (CPU+ GPU) Algorithms for Triangle Counting and Truss Decomposition"
date = 2018-09-25
draft = false
tags = ["pangolin"]
authors = ["Vikram S. Mailthody", "Ketan Date", "Zaid Qureshi", "Carl Pearson", "Rakesh Nagi", "Jinjun Xiong", "Wen-Mei Hwu"]
venue = "2018 IEEE High Performance Extreme Computing Conference"
abstract = "In this paper, we present an update to our previous submission  from  Graph  Challenge  2017. This  work  describes and evaluates new software algorithm optimizations undertaken for our 2018 year submission on Collaborative CPU+GPU Algorithms for Triangle Counting and Truss Decomposition. First, we describe four major optimizations for the triangle counting which improved performance by up to 117x over our prior submission. Additionally,  we  show  that  our triangle-counting  algorithm  is on average 151.7x faster than NVIDIA’s NVGraph library (max 476x) for SNAP  datasets.  Second,  we  propose  a  novel  parallel k-truss  decomposition  algorithm that is time-efficient and  is  up to 13.9x faster than our previous submission. Third, we evaluate the  effect  of  generational  hardware  improvements  between  the IBM  \"Minsky\" (POWER8,  P100,  NVLink  1.0)  and  \"Newell\" (POWER9,  V100,  NVLink  2.0)  platforms.  Lastly,  the  software optimizations presented in this work and the hardware improvements  in  the  Newell  platform  enable  analytics  and  discovery  on large graphs  with millions of nodes  and billions of edges  in less than a minute. In sum, the new algorithmic implementations are significantly  faster  and  can  handle  much  larger  \"big\" graphs."
+++

* [pdf](/static/pdf/20180925_mailthody_hpec.pdf)