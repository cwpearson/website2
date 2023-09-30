+++
title = "C3SR Minsky Machines"
date = 2017-09-27T08:41:21-05:00
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

I manage the two Minsky machines available to the C3SR center at Illinois.

## Minsky Machine Overview

| Product | IBM S822LC |
|---------|------------|
| Model   | 8335-GTB   |
| CPU     | 2x Power8  |
| GPU     | 4x NVIDIA P100 w/ 16GB RAM |
| RAM     | 512 GB |

Each P8 CPU has 10 cores with 8-way SMT, yielding 80 threads per CPU or 160 threads on each Minsky machine.

Each CPU is connected to two NVIDIA P100s by two NVLinks each. Those two P100s are also connected by two NVLinks. The machine is a pair of these CPU-GPU-GPU triangles, connected at the CPUs by an IBM *X bus*.

## Access

Minsky1 may be accessed at `minsky1-1.csl.illinois.edu`

Minsky2 may be accessed at `minsky2-1.csl.illinois.edu` or `minsky2-2.csl.illinois.edu`.

Both machines are behind the UIUC firewall. You will need to be on the UIUC network (either on-campus or through VPN) to access the machines.