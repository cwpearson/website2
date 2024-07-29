+++
title = "Maximizing Kokkos Performance: Harnessing the Power of nvtx-connector and Nsight Systems"
date = 2024-07-26T00:00:00-0700
description = ""
tags = ["kokkos", "cmake"]
draft = true
+++

How can you ensure your Kokkos-based applications are truly optimized? Enter the dynamic duo of nvtx-connector and NVIDIA's Nsight Systems – tools that can take your Kokkos development to the next level.
In this blog post, we'll explore how integrating nvtx-connector and Nsight Systems into your Kokkos workflow can help you:

* Gain unprecedented visibility: Peer into the inner workings of your Kokkos applications with detailed, hierarchical timelines.
* Identify performance bottlenecks: Pinpoint exactly where your code is spending time, from kernel executions to memory transfers.
* Optimize with precision: Make data-driven decisions to refine your Kokkos code for maximum efficiency.
* Streamline debugging: Correlate application-level events with low-level system activities for easier troubleshooting.
* Enhance collaboration: Generate comprehensive performance reports that speak both to Kokkos experts and hardware specialists.

Whether you're fine-tuning an existing Kokkos application or embarking on a new project, mastering these tools will empower you to squeeze every ounce of performance from your code. Let's dive in and discover how nvtx-connector and Nsight Systems can transform your Kokkos development experience and help you create blazingly fast, efficient applications.

## Configuring your Kokkos Build

You don't need to change anything about how you build Kokkos for your application: Kokkos' profiling interface is always enabled.

## The nvtx-connector: Bridging Kokkos and NVIDIA Nsight Systems

Kokkos Tools is a suite of profiling and analysis tools designed to work seamlessly with Kokkos applications. It provides a powerful framework for gathering performance data and insights into your Kokkos-based code. The Kokkos Tools ecosystem includes various plugins and connectors that allow you to interface with different profiling and visualization tools, enhancing your ability to optimize Kokkos applications.
One of the key components of Kokkos Tools is the profiling API, which enables the collection of detailed performance data without requiring changes to your application code. This API is leveraged by various backends, including the nvtx-connector, which we'll focus on in this post.

The nvtx-connector is a crucial component that bridges the gap between Kokkos applications and NVIDIA's powerful profiling tools, particularly Nsight Systems. It translates Kokkos events into NVIDIA Tools Extension (NVTX) ranges, allowing you to visualize and analyze your Kokkos application's performance within the Nsight Systems interface.

```cmake

```

## Annotating Your Application with Kokkos Profiling Regions
To get the most out of the nvtx-connector and Nsight Systems, it's crucial to properly annotate your Kokkos application with profiling regions. These annotations allow you to mark specific sections of your code, making it easier to identify performance bottlenecks and understand the behavior of your application at a granular level.

Kokkos profiling regions are sections of code that you explicitly mark for profiling. When using the nvtx-connector, these regions are translated into NVTX ranges, which appear as colored bars in the Nsight Systems timeline view.

## How to Add Profiling Regions

Kokkos provides a pair of functions for adding profiling regions to your code. Here's how you use them

```c++
void foo() {
    Kokkos::Profiling::pushRegion("your region label");

    // your code here ...

    Kokkos::Profiling::popRegion();
}
```

You can nest profiling regions

```c++
void foo() {
    Kokkos::Profiling::pushRegion("outer region");

    // some code here ...

    Kokkos::Profiling::pushRegion("inner region");

    // your code here ...

    Kokkos::Profiling::popRegion(); // ends inner region
    Kokkos::Profiling::popRegion(); // ends outer region
}
```

Care is sometimes needed to ensure that every `pushRegion` has an associated `popRegion`.

```c++
void be_careful() {
    Kokkos::Profiling::pushRegion("my region");

    if (early_return) {
        Kokkos::Profiling::popRegion(); // ends "my region"
        return;
    }

    // some code here

    Kokkos:Profiling::popRegion(); // also ends "my region"
}
```

Also, be sure you pop a region before `return`ing from a function!

```c++
void dont_do_this() {
    Kokkos::Profiling::pushRegion("my region");
    int x;

    // some code here ...

    return x;
    Kokkos::Profiling::popRegion(); // oops, region won't ever be popped!
}
```

## How to Profile

From time to time Nvidia changes their profiling tools.
Thus far, however, the approach has been roughly this:

1. Run your application on the target platform using `nsys`
2. Copy the produced trace database file(s) to your client
3. View and analyze the results using Nsight Systems

There are variations on this theme that I won't cover - Nsight Systems can connect to a remote system to profile directly, or perhaps the client and target systems are the same.

The approach will be something like this
```bash
nsys 
```

Then I usually just `scp` the resulting trace files to my client and fire up Nsight Systems. File > Import > Select your trace files.

## Installing Nsight Systems on your Client

There are two halves to Night Systems: the first does the profiling on the target platform, and the second is installed on your client to view the results. Go to Nvidia's website and look for "Download Nsight Systems for [your OS] host". There are Windows, macOS, and Linux versions. This is what you will use to view and analyze the profiling results.

## Putting it all together: miniFE

miniFE is a 


I added profiling regions to my fork of miniFE in [this PR](https://github.com/cwpearson/miniFE/pull/11/files).

**Set up some paths for the example**
```bash
ROOT=kokkos_nsys_example
KOKKOS_SRC=$ROOT/kokkos
KOKKOS_BUILD=$KOKKOS_SRC/build
KOKKOS_INSTALL=$KOKKOS_SRC/install
TOOLS_SRC=$ROOT/kokkos-tools
TOOLS_BUILD=$ROOT/kokkos-tools/build
MINIFE_SRC=$ROOT/miniFE
MINIFE_BUILD=$MINIFE_SRC/build
```

**Compile Kokkos for CUDA**

You're probably already doing this for your application if you use Nvidia GPUs, but I include it here for completeness.
* Remember to choose a `-DKokkos_ARCH_` appropriate for your GPU

```bash
git clone --branch develop --depth 1 https://github.com/kokkos/kokkos.git $KOKKOS_SRC

cmake -S $KOKKOS_SRC -B $KOKKOS_BUILD \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=$KOKKOS_INSTALL \
  -DCMAKE_CXX_COMIPLER=$(realpath $KOKKOS_SRC/bin/nvcc_wrapper) \
  -DKokkos_ENABLE_CUDA=ON \
  -DKokkos_ARCH_AMPERE86=ON \
  -DCMAKE_CXX_STANDARD=17 \
  -DCMAKE_CXX_EXTENSIONS=OFF

cmake --build $KOKKOS_BUILD --target install --parallel $(nproc)
```

**Compile the nvtx-connector**

The nvtx-connector needs to know where Kokkos is installed so it can retrieve the CUDA toolkit path.

```bash
git clone --branch develop --depth 1 https://github.com/kokkos/kokkos-tools.git $TOOLS_SRC

cmake -S $TOOLS_SRC -B $TOOLS_BUILD \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_CXX_EXTENSIONS=OFF \
  -DKokkos_ROOT=$KOKKOS_INSTALL

cmake --build $TOOLS_BUILD/profiling/nvtx-connector
```

**Compile miniFE**
```bash
git clone https://github.com/cwpearson/miniFE.git $MINIFE_SRC

cmake -S $MINIFE_SRC/kokkos -B $MINIFE_BUILD \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_CXX_COMPILER=$(realpath $KOKKOS_SRC/bin/nvcc_wrapper) \
  -DCMAKE_CXX_STANDARD=17 \
  -DCMAKE_CXX_EXTENSIONS=OFF \
  -DKokkos_ROOT=$KOKKOS_INSTALL \
  -DMINIFE_ENABLE_MPI=OFF

cmake --build $MINIFE_BUILD
```

**Run miniFE with nsight systems**

This will create `reportX.nsys-rep`

```bash
# tell Kokkos::initialize which tools library to use
export KOKKOS_TOOLS_LIBS=$TOOLS_BUILD/profiling/nvtx-connector/libkp_nvtx_connector.so

nsys profile -f true -t cuda,nvtx $MINIFE_BUILD/miniFE.kokkos
```

If it worked, you will see a couple messages in your output

```
-----------------------------------------------------------
KokkosP: NVTX Analyzer Connector (sequence is 0, version: 20211015)
-----------------------------------------------------------
```

```
-----------------------------------------------------------
KokkosP: Finalization of NVTX Connector. Complete.
-----------------------------------------------------------
```

```
Generating '/tmp/nsys-report-e218.qdstrm'
[1/1] [========================100%] report1.nsys-rep
Generated:
    /.../report1.nsys-rep
```

## Looking at the Result

Copy the produced `report[N].nsys-rep` file from the server to the client, and open it in the client Nsight Systems.

File > Open > report1.nsys-rep

## Extras: MPI + nsys

```bash
nsys profile -t cuda,nvtx,mpi --mpi-impl=openmpi
nsys profile -t cuda,nvtx,mpi --mpi-impl=mpich
```

## Extras: Unified Memory + nsys

CUDA Unified Memory `cudaMallocManaged`, or on newer platforms like Grace/Hopper.

```bash
nsys profile --cuda-um-cpu-page-faults=true --cuda-um-gpu-page-faults=true
```