+++
title = "Node-Aware Stencil Communication on Heterogeneous Supercomputers"
date = 2020-03-09  # Schedule page publish date.
draft = false
projects = ["stencil"]
authors = ["Carl Pearson", "Mert Hidayetoglu", "Mohammad Almasri", "Omer Anjum", "I-Hsin Chung", "Jinjun Xiong", "Wen-Mei Hwu"]
venue = "2020 IEEE International Workshop on Automatic Performance Tuning (iWAPT)"
abstract = "High-performance distributed computing systems increasingly feature nodes that have multiple CPU sockets and multiple GPUs. The communication bandwidth between these components is non-uniform. Furthermore, these systems can expose different communication capabilities between these components. For communication-heavy applications, optimally using these capabilities is challenging and essential for performance.  Bespoke codes with optimized communication may be non-portable across run-time/software/hardware configurations, and existing stencil frameworks neglect optimized communication. This work presents node-aware approaches for automatic data placement and communication implementation for 3D stencil codes on multi-GPU nodes with non-homogeneous communication performance and capabilities. Benchmarking results in the Summit system show that choices in placement can result in a 20% improvement in single-node exchange, and communication specialization can yield a further 6x improvement in exchange time in a single node, and a 16% improvement at 1536 GPUs."
+++

```bibtex
@INPROCEEDINGS{9150372,
  author={C. {Pearson} and M. {Hidayetoğlu} and M. {Almasri} and O. {Anjum} and I. {Chung} and J. {Xiong} and W. W. {Hwu}},
  booktitle={2020 IEEE International Parallel and Distributed Processing Symposium Workshops (IPDPSW)}, 
  title={Node-Aware Stencil Communication for Heterogeneous Supercomputers}, 
  year={2020},
  volume={},
  number={},
  pages={796-805},
  doi={10.1109/IPDPSW50202.2020.00136}
}
```

* [pdf](/pdf/20200522_pearson_iwapt.pdf)
* [code](https://github.com/cwpearson/stencil)
* [slides](/pdf/20200522_pearson_iwapt_slides.pdf)