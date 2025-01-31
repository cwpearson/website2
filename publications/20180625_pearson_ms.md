+++
title = "Heterogeneous Application and System Modeling"
date = 2018-06-25
draft = false
tags = ["benchmark", "GPU", "nvlink", "pcie", "v100", "p100", "numa"]
authors = ["Carl Pearson"]
venue = "M.S. Thesis, May 2018"
url_pdf = "/pdf/pdf/20180625_pearson_ms.pdf"
abstract = "With the end of Dennard scaling, high-performance computing increasingly relies on heterogeneous systems with specialized hardware to improve application performance. This trend has driven up the complexity of high-performance software development, as developers must manage multiple programming systems and develop system-tuned code to utilize specialized hardware. In addition, it has exacerbated existing challenges of data placement as the specialized hardware often has local memories to fuel its computational demands. In addition to using appropriate software resources to target application computation at the best hardware for the job, application developers now must manage data movement and placement within their application, which also must be specifically tuned to the target system. Instead of relying on the application developer to have specialized knowledge of system characteristics and specialized expertise in multiple programming systems, this work proposes a heterogeneous system communication library that automatically chooses data location and data movement for high-performance application development and execution on heterogeneous systems. This work presents the foundational components of that library: a systematic approach for characterization of system communication links and application communication demands."

+++
