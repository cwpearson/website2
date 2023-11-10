+++
draft = true
title = "How does Kokkos manage team scratch spaces internally"
date = 2023-11-10T08:00:00-07:00
+++

Let's follow along three parallel examples:

1. `Kokkos::Serial`, which supports Kokkos scratch but does not actually have a special software-managed scratch memory
2. `Kokkos::Cuda`, which supports Kokkos scratch has a concept of scratch (shared memory)
3. `Kokkos::OpenACC`, which does not currently support Kokkos scratch memory

Even if a backend does not have a special scratch-like memory, it can provide a normal allocation that Kokkos Teams can use as scratch memory, just without any special performance characteristics.

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
m_shmem_size =
        (m_policy.scratch_size(0, m_team_size) +
         FunctorTeamShmemSize<FunctorType>::value(m_functor, m_team_size));
```

*https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_Parallel_Team.hpp#L554-L556*

In `Kokkos::OpenACC`

```c++
```

### Ask the provided `TeamPolicy` what execution space instance to execute in

The functor will be executed in a specific instance of the Execution Space.

In `Kokkos::Cuda`

```c++
auto internal_space_instance =
    m_policy.space().impl_internal_space_instance();
```

*https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_Parallel_Team.hpp#L539-L540*

### Asks the Execution Space instance to ensure that much scratch space is available

In `Kokkos::Cuda`

```c++
m_scratch_pool_id = internal_space_instance->acquire_team_scratch_space();
      m_scratch_ptr[1]  = internal_space_instance->resize_team_scratch_space(
          m_scratch_pool_id,
          static_cast<std::int64_t>(m_scratch_size[1]) *
              (std::min(
                  static_cast<std::int64_t>(Cuda().concurrency() /
                                            (m_team_size * m_vector_size)),
                  static_cast<std::int64_t>(m_league_size))));
```

*https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_Parallel_Team.hpp#L567-L574*

### Construct the Team handles and call the functor

The team handles are provided to the functor, and provide it access to the various properties of the Team (size, scratch space, etc).
Team handle gets a slice of the backing scratch allocation (using league id, team size, scratch pointer)

In `Kokkos::Cuda`'s `ParallelFor::operator()`

```c++
this->template exec_team<WorkTag>(typename Policy::member_type(
    kokkos_impl_cuda_shared_memory<void>(), m_shmem_begin, m_shmem_size,
    (void*)(((char*)m_scratch_ptr[1]) +
            ptrdiff_t(threadid / (blockDim.x * blockDim.y)) *
                m_scratch_size[1]),
    m_scratch_size[1], league_rank, m_league_size));
```
*https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_Parallel_Team.hpp#L504-L509*

### Call the functor and pass the constructed handles

In `Kokkos::Cuda`, `exec_team` from above just calls the functor.
```c++
template <class TagType>
__device__ inline std::enable_if_t<std::is_void<TagType>::value> exec_team(
    const Member& member) const {
  m_functor(member);
}

template <class TagType>
__device__ inline std::enable_if_t<!std::is_void<TagType>::value> exec_team(
    const Member& member) const {
  m_functor(TagType(), member);
}
```
*https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_Parallel_Team.hpp#L478-L488*

But how does this actually get injected into a CUDA kernel launch?

The `ParallelFor`'s `execute` member passes the constructed `ParallelFor` object (itself), into a `CudaParallelLaunch`, helpfully annotated with a short comment
Recall that that the grid dimensions, shared memory size, and CUDA stream are already known by this point, since they are determined in the `ParallelFor`` ctor.

```c++
CudaParallelLaunch<ParallelFor, LaunchBounds>(
    *this, grid, block, shmem_size_total,
    m_policy.space()
        .impl_internal_space_instance());  // copy to device and execute
```
*https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_Parallel_Team.hpp#L527-L530*

Within `CudaParallelLaunch` (and most of `Kokkos_Cuda_KernelLaunch.hpp`), this `ParallelFor` type is referred to as the `DriverType`.
 

`CudaParallelLaunch` examines the `ParallelFor` type to decide how to launch the kernel using `DeduceCudaLaunchMechanism<DriverType>`. This happens at compile-time through a default template parameter.

```c++
template <class DriverType, class LaunchBounds = Kokkos::LaunchBounds<>,
          Experimental::CudaLaunchMechanism LaunchMechanism =
              DeduceCudaLaunchMechanism<DriverType>::launch_mechanism,
          bool DoGraph = DriverType::Policy::is_graph_kernel::value>
struct CudaParallelLaunch;
```
*https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_KernelLaunch.hpp#L692-L696*

`CudaParallelLaunch` is a derived class of `CudaParallelLaunchImpl`, which actually implements the machinery to launch the kernel: all the ctor of `CudaParallelLaunch` does at runtime is ask `CudaParallelLaunchImpl` to launch the kernel.

```c++
CudaParallelLaunch(Args&&... args) {
  base_t::launch_kernel((Args &&) args...);
}
```
*https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_KernelLaunch.hpp#L707-L709*

So what does `CudaParallelLaunchImpl` do?

`CudaParallelLaunchImpl` is a derived class of `CudaParallelLaunchKernelInvoker`

```c++
struct CudaParallelLaunchImpl<
    DriverType, Kokkos::LaunchBounds<MaxThreadsPerBlock, MinBlocksPerSM>,
    LaunchMechanism>
    : CudaParallelLaunchKernelInvoker<
          DriverType, Kokkos::LaunchBounds<MaxThreadsPerBlock, MinBlocksPerSM>,
          LaunchMechanism> {
  using base_t = CudaParallelLaunchKernelInvoker<
      DriverType, Kokkos::LaunchBounds<MaxThreadsPerBlock, MinBlocksPerSM>,
      LaunchMechanism>;
```
*https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_KernelLaunch.hpp#L633-L641*

`CudaParallelLaunchImpl`'s `launch_kernel` method optionally adjusts the CUDA shared memory configuration, and then just calls `CudaParallelLaunchKernelInvoker`'s `invoke_kernel`

```c++
base_t::invoke_kernel(driver, grid, block, shmem, cuda_instance);
```
*https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_KernelLaunch.hpp#L669C15-L669C28*

So what does `CudaParallelLaunchKernelInvoker` do?
It's a dervied class of `CudaParallelLaunchKernelFunc`, and it's `invoke_kernel` method is finally what launches the kernel

```c++
static void invoke_kernel(DriverType const& driver, dim3 const& grid,
                          dim3 const& block, int shmem,
                          CudaInternal const* cuda_instance) {
  (base_t::
        get_kernel_func())<<<grid, block, shmem, cuda_instance->m_stream>>>(
      driver);
}
```
*https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_KernelLaunch.hpp#L361-L367*

Recall that `DriverType` is actually `ParallelFor`, so the `ParallelFor` object is what gets passed into whatever kernel function is being executed.

So what does this `get_kernel_func` from `CudaParallelLaunchKernelFunc` do?

```c++
get_kernel_func() {
  return cuda_parallel_launch_local_memory<DriverType, MaxThreadsPerBlock,
                                            MinBlocksPerSM>;
}
```
*https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_KernelLaunch.hpp#L331-L334*

and finally...

```c++
template <class DriverType>
__global__ static void cuda_parallel_launch_local_memory(
    const DriverType driver) {
  driver();
}
```
*https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_KernelLaunch.hpp#L85-L89*

It is just a function that calls `operator()` from the DriverType, e.g. the `ParallelFor` instance.
If you'll recall, that is what constructs a `TeamPolicy` from the location in the CUDA grid and the shared memory pointer, and actually executes the functor.


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
