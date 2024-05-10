+++
title = "miniAero"
date = 2024-05-10T00:00:00-0700
description = "miniAero fork with Kokkos 4, CMake, and Python 3"
tags = []
draft = true
+++

I've [created an **unofficial** fork](https://github.com/cwpearson/miniAero) of [mantevo/miniAero](https://github.com/mantevo/miniAero) with support for Kokkos 4, the CMake build system, and Python 3.

miniAero is one of the [mantevo](manetvo.org) mini-applications.
Mini-apps are intended to distill the key computational components of larger high-performance computing applications into a smaller package that is easier to experiment with and study.
MiniAero was released in 2016 and enough has changed in the HPC software community to make it a bit annoying to run, even though the underlying computation is still relevant.
This fork is intended to be easier to build and run in 2024.

miniAero is implemented using the [Kokkos](kokkos.org) performance portability library.
Kokkos has had several major releases since miniAero was written, and although the basic features that miniAero uses haven't changed much, the API has drifted slightly.
I made minor modifications to allow miniAero to be compiled with Kokkos 4.3.00.

Kokkos has also settled on CMake as a build system.
Back in 2016, this was not as well established, and miniAero used Make.
The miniAero fork supports CMake (as well as CTest for testing).

On the subject of testing, the original test scripts were written with Python 2.
Python 2 is pretty much gone now, so I updated them to use Python 3.
I also added CI tests with Github Actions to hopefully prevent introducing any future regressions.

*Although miniAero was originally developed by researchers at my employer, Sandia National Labs, I have not consulted with them on this fork. The original project seems to be unmaintained.*