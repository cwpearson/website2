+++
draft = true
title = "How does Kokkos manage team scratch spaces internally"
+++

Some backends do not natively have a "scratch space" concept (e.g. serial CPU code).

Let's follow along three parallel examples:

1. `Kokkos::Serial`, which supports scratch but does not actually have an underlying concept of software-managed scratch, 
2. `Kokkos::Cuda`, which supports scratch and has a concept of scratch (shared memory)
3. `Kokkos::OpenACC`, which does not currently support Kokkos scratch memory

## Telling Kokkos how much scratch space a functor needs

Briefly: each Kokkos Team has a scratch pad, which is memory that is only available to threads within that team, and whose lifetime is scoped to that of the Team.
Threads in the can use that memory for collaborative work.
This is the same regardless of which backend you're using.

Further reading: https://kokkos.github.io/kokkos-core-wiki/ProgrammingGuide/HierarchicalParallelism.html

There are two methods for you to tell Kokkos how much scratch space you want for a particular parallel region.
You can use either method, but not both!
The first is to implement the `team_shmem_size` member of the functor:

```c++
template<class ExecutionSpace>
struct functor {
  size_t team_shmem_size (int team_size) const {
    return sizeof(double)*5*team_size +
           sizeof(int)*160;
  }
};
```

The second is to call the `set_scratch_size` member of the `Kokkos::TeamPolicy`.

```c++
using Policy = TeamPolicy<ExecutionSpace>;
Policy policy_1 = Policy(league_size, team_size).
                         set_scratch_size(1, Kokkos::PerTeam(1024), Kokkos::PerThread(32));
Policy policy_2 = Policy(league_size, team_size).
                         set_scratch_size(1, Kokkos::PerThread(32));
Policy policy_3 = Policy(league_size, team_size).
                         set_scratch_size(0, Kokkos::PerTeam(1024));
```

In the above method, the total scratch space per team is the `Kokkos::PerTeam` value plus the `Kokkos::PerThread` value times the number of threads.

## How does a backend use this information?

None of this is has to work this way, but the backends tend to follow a similar strategy.

### `Kokkos::parallel_for` asks the functor how much scratch space it wants

In `Kokkos::Serial`

```c++
```

In `Kokkos::Cuda`

```c++
```

In `Kokkos::OpenACC`

```c++
```

2. The backend's implementation of `Kokkos::parallel_for`
    1. asks the functor how much scratch space it wants

### Ask the provided `TeamPolicy` what execution space instance to execute in

The functor will be executed in a specific instance of the Execution Space.

### Asks the Execution Space instance to ensure that much scratch space is available


### Construct the Team handles and call the functor

The team handles are provided to the functor, and provide it access to the various properties of the Team (size, scratch space, etc).
Team handle gets a slice of the backing scratch allocation (using league id, team size, scratch pointer)


### Call the functor and pass the constructed handles


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
