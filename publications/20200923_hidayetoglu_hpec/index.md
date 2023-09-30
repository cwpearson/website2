+++
title = "[HPEC] At-Scale Sparse Deep Neural Network Inference With Efficient GPU Implementation"
date = 2020-09-23  # Schedule page publish date.
draft = false
+++

**Mert Hidayetoglu, Carl Pearson, Vikram Sharma Mailthody, Eiman Ebrahimi, Jinjun Xiong, Rakesh Nagi, Wen-Mei Hwu**

In *2020 IEEE High Performance Extreme Compute Conference*

This paper presents GPU performance optimization and scaling results for inference models of the Sparse Deep Neural Network Challenge 2020.
Demands for network quality have increased rapidly, pushing the size and thus the memory requirements of many neural networks beyond the capacity ofavailable accelerators.
Sparse deep neural networks (SpDNN) have shown promise for reining in the memory footprint of large neural networks.\
However, there is room for improvement inimplementing SpDNN operations on GPUs.
This work presents optimized sparse matrix multiplication kernels fused with theReLU function.
The optimized kernels reuse input feature mapsfrom the shared memory and sparse weights from registers.
For multi-GPU parallelism, our SpDNN implementation duplicates weights and statically partition the feature maps across GPUs.
Results for the challenge benchmarks show that the proposed kernel design and multi-GPU parallelization achieve up to 180TeraEdges per second inference throughput.
These results areup to 4.3x faster for a single GPU and an order of magnitude faster at full scale than those of the champion of the 2019 SparseDeep Neural Network Graph Challenge for the same generation of NVIDIA V100 GPUs.
Using the same implementation1, we also show single-GPU throughput on NVIDIA A100 is 2.37x faster than V100

```bibtex
@INPROCEEDINGS{9286206,
  author={M. {Hidayetoğlu} and C. {Pearson} and V. S. {Mailthody} and E. {Ebrahimi} and J. {Xiong} and R. {Nagi} and W. -m. {Hwu}},
  booktitle={2020 IEEE High Performance Extreme Computing Conference (HPEC)}, 
  title={At-Scale Sparse Deep Neural Network Inference With Efficient GPU Implementation}, 
  year={2020},
  volume={},
  number={},
  pages={1-7},
  doi={10.1109/HPEC43674.2020.9286206}
  }
```

* [pdf](/pdf/20200923_hidayetoglu_hpec.pdf)
* [code] (https://github.com/merthidayetoglu/sparse-DNN)
* [slides](/pdf/20200923_hidayetoglu_hpec_slides.pdf)