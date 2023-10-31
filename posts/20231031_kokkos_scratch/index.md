+++
draft = true
title = "How does Kokkos manage team scratch spaces internally"
+++

Some backends do not natively have a "scratch space" concept (e.g. serial CPU code).

1. A Kokkos functor describes how much scratch space it needs
    * this can be a runtime value
2. The backend's implementation of `Kokkos::parallel_for`
    1. asks the functor how much scratch space it wants
    2. Looks at the provided `Policy` to determine which execution space instance the functor will be executing in
    3. Asks the execution space instance to ensure that much scratch is available
    4. Constructs the Team handles as necessary to execute the `Kokkos::parallel_for`, providing those team handles with enough information to internally acquire their little slice of the total available scratch space. This is usually something equivalent to a pointer to the scratch space, a league id, and a team size.
    5. Provide the appropriate member to the functor when each iteration is executed.
3. When the functor is executed, it will ask the member for scratch space to operate in. The member tracks that space per 2.4, so it can provide it.

Some underlying programming ssytems natively handle scratch space: e.g., when you launch a CUDA kernel, you tell CUDA how much scratch space you want, and CUDA provides it.

1. A Kokkos functor describes how much scratch space it needs
    * this can be a runtime value
2. The backend's implementation of `Kokkos::parallel_for`
    1. Define a team handle that knows how to access the underlying programming system scratch space.
    2. asks the functor how much scratch space it wants
    3. Launch the parallel region, telling the programming system how much scratch the functor wanted.
3. When the functor is executed, it will ask the member for scratch space to operate in. The member knows how to retrieve the programming system scratch space, and it does.

## Kokkos::ScratchSpace Type

This is a type that takes a pointer to a level 0 (and optionally level 1) scratch space allocation, and handles all the pointer arithmetic to align requested sizes appropriately.
