+++
title = "miniAero Fork for Kokkos 4"
date = 2024-05-10T00:00:00-0700
description = "miniAero fork with Kokkos 4, CMake, and Python 3"
tags = ["c++", "cmake"]
draft = true
+++

I've created an **unofficial** fork of the [mantevo/miniAero](https://github.com/mantevo/miniAero) proxy application, featuring support for Kokkos 4, the CMake build system, and Python 3.
You can explore the fork on [github](https://github.com/cwpearson/miniAero).
Although miniAero was originally developed by researchers at my employer, Sandia National Labs, I have not consulted with them on this fork. The original project seems to be inactive.

## Background

miniAero is part of the [mantevo](manetvo.org) suite of proxy applications, which simplify the core computational components of larger high-performance computing applications into more manageable, smaller packages.
MiniAero is a computation fluid dynamics (CFD) code.
It utilizes a cell-centered unstructured finite volume solver that can operate with either first-order or second-order accuracy, alongside explicit time integration via a standard fourth-order Runge Kutta method.
MiniAero is structured to support simulations based on either the Euler or compressible Navier-Stokes equations, making it versatile for studying transonic turbulent flows among other scenarios.

MiniAero was released in 2016 and enough has changed in the HPC software community to make it a bit annoying to run, even though the underlying computation is still relevant.
This fork is intended to be easier to use in 2024.

## miniAero for Kokkos 4

miniAero is implemented using the [Kokkos](kokkos.org) performance portability library.
Kokkos has had several major releases since miniAero was written, and although the basic features that miniAero uses haven't changed much, the API has drifted slightly.
I made minor modifications to allow miniAero to be compiled with Kokkos 4.3.00.

## miniAero with CMake

Kokkos has also settled on CMake as a build system.
Back in 2016, this was not as well established, and miniAero used Make.
The miniAero fork supports CMake (as well as CTest for testing).

## miniAero Testing with Python 3 and Github Actions

On the subject of testing, the original test scripts were written with Python 2.
Python 2 is pretty much gone now, so I updated them to use Python 3.
I also added CI tests with Github Actions to hopefully prevent introducing any future regressions.
