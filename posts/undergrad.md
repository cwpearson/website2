+++
title = "Undergraduate Research Opportunities"
date = 2018-02-25T08:41:21-05:00
draft = false

# Tags and categories
# For example, use `tags = []` for no tags, or the form `tags = ["A Tag", "Another Tag"]` for one or more tags.
tags = []
categories = []

# Featured image
# Place your image in the `static/img/` folder and reference its filename below, e.g. `image = "example.jpg"`.
[header]
image = ""
caption = ""

+++

I'm looking for a few good undergraduate students! Please contact me if you're interested in any of the tasks on this page.
More significant engagement with masters or doctoral students on any of these topics is also welcome.

*(Last updated Feb 25, 2018)*

## System Characterization

The IMPACT group is working on a heterogeneous system benchmarking tool: [rai-project/microbench](github.com/rai-project/microbench).

We'd like to extend it with the following capabilities:

* Adding persistent storage benchmarking
* Enhancing the CUDA communication benchmarking (full-duplex)
* Benchmarking system atomics, cooperative kernel launches, and other new CUDA features
* Adding network storage discovery and performance characterization (MPI, RPC, and so on)
* Adding communication collective performance characterization (MPI / NCCL / Blink / direct CUDA implementations, others)

## Application Characterization

I have written a heterogeneous application profiling tool. It needs to be better.

* Trace application disk I/O
* Extending the tool to work with networked applications
    * Trace application network requests (MPI or otherwise)
    * Visualization of parallel traces
* Techniques for replaying application profiles / rescheduling computation and communication

## Automatic Architecture Determination

I am investigating using the tools above to automatically propose architectures fitted to applications of interest. I need some help with

* Performance estimation for GPU kernels
* Architecture generation as a constrained optimization problem
