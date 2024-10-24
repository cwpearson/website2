+++
title = "KokkosComm: Communication Layer for Distributed Kokkos Applications"
date = 2024-09-25T09:00:00-0500
authors = ["Gabriel Dos Santos", "Nicole Avans", "Cedric Chevalier", "Hugo Taboada", "Carl Pearson", "Jan Ciesko", "Stephen L. Olivier", "Marc Perache"]
venue = "EuroMPI"
tags = ["Kokkos", "MPI"]
description = ""
url_pdf = "/pdf/20240925_santos_eurompi.pdf"
abstract = "The Kokkos C++ Performance Portability Programming Ecosystem provides multi-dimensional data structures, concurrency, and algorithms to support shared-memory heterogeneous programming on modern HPC architectures. HPC applications that use Kokkos for intra-node parallelism typically rely on MPI to distribute their code across multiple nodes. For this kind of distributed application, programmers have to implement the logic to exchange Kokkos Views using MPI. In this short-paper, we introduce KokkosComm: an experimental, zero-overhead interface built on top of standard message-passing libraries. KokkosComm unifies existing practices by offering a streamlined API for exchanging first-class Kokkos objects within modern C++ applications."
+++
