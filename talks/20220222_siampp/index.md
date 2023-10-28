---
title: Automatic Discovery of Implementation Rules for Fast GPU + MPI Operations
tags: [MPI, CUDA]
time_start: 2022-02-25T16:00:00-06:00
location: "MS61: Experiences in Developing GPU Support for DOE Math Libraries"
event: SIAM Parallel Processing
url_slides: /pdf/20220225_siampp.pdf
how_invited: Invited talk
authors: ["Carl Pearson", "Karen Devine", "Aurya Javeed"]
abstract: "Developing a high-performance implementation of a distributed computational kernel for high-performacing computing is increasingly challenging. Systems are composed of heterogenous computational resources, and limited communication performance demands an asynchronous application design. Even if high-performance computation and communication libraries are available. the challenge becomes the best coordination of the provided operations to create an optimal result. This work presents a system that automatically generates design rules for a high-performance implementation of a compound operation provided as a dependence graph. The system searches among valid schedules to determine the fastest arrangement of operations. A post-processing step on the results of the search yields interpretable design rules. The fast implementation can be used directly, or experts can use the design rules to create a high-performance implementation."
publication: 20220304_pearson_pdsec
url_code: ["https://github.com/sandialabs/tenzing-core", "https://github.com/sandialabs/tenzing-mcts", "https://github.com/sandialabs/tenzing-dfs"]
url_video: "https://vimeo.com/682527688"
---
