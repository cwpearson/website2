+++
draft = true
title = "How Team Scratch gets into your Kokkos functor"
date = 2023-11-10T08:00:00-07:00
+++

Hierarchical parallelism is a key feature of Kokkos - it provides a way for "teams", or subsets of active threads, to collaborate on a particular operations within a parallel region.
Kokkos provides a "scratch" memory, which is a way of providing a fast scratchpad to a team, where supported by the underlying execution system.
How the scratch memory ends up in the Team handle can be surprisingly convoluted - here, I attempt to outline it by following along with two examples:

1. `Kokkos::Serial`, which supports Kokkos scratch but does not actually have a special software-managed scratch memory
2. `Kokkos::Cuda`, which supports Kokkos scratch has a concept of scratch (shared memory)

Even if a backend does not have a special scratch-like memory, it can provide a normal allocation that Kokkos Teams can use as scratch memory, just without any special performance characteristics.
This is an excessive amount of information for a user of Kokkos, but it may be helpful to someone who has to work on a backend.

## 1. Telling Kokkos how much scratch space a functor needs

Briefly: each Kokkos Team has a scratch pad, which is memory that is only available to threads within that team, and whose lifetime is scoped to that of the Team.
Threads in the team can use that memory for collaborative work.

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

This interface is the same regardless of the Kokkos backend in use (as long as the backend supports Kokkos scratch memory!)

## 2. How does a backend use this information?

These two backends follow a similar strategy.

### 2.1 `Kokkos::parallel_for` asks the functor how much scratch space it wants

A `Kokkos::parallel_for` region is internally represented as a `ParallelFor` struct.

#### 2.1.1 `Kokkos::Serial`

In `Kokkos::Serial`, the `ParallelFor` ctor retrieves this information from the policy and some compile-time analysis of the functor.

```c++
m_shared(arg_policy.scratch_size(0) + arg_policy.scratch_size(1) +
          FunctorTeamShmemSize<FunctorType>::value(arg_functor, 1)) {}
```
*[core/src/Serial/Kokkos_Serial_Parallel_Team.hpp#L265-L266](https://github.com/kokkos/kokkos/blob/d5a4802911318aebecbc775990dd198260ce2383/core/src/Serial/Kokkos_Serial_Parallel_Team.hpp#L265-L266)*


#### 2.1.2 `Kokkos::Cuda`

In `Kokkos::Cuda`, the `ParallelFor` ctor does something similar, except the size of the team may be larger than 1.

```c++
m_shmem_size =
        (m_policy.scratch_size(0, m_team_size) +
         FunctorTeamShmemSize<FunctorType>::value(m_functor, m_team_size));
```
*[core/src/Cuda/Kokkos_Cuda_Parallel_Team.hpp#L554-L556](https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_Parallel_Team.hpp#L554-L556)*


### 2.2 Ask the provided `TeamPolicy` what execution space instance to execute in

Sicne the functor will necessarily be executed in a specific instance of an execution space, `ParallelFor` needs to determine which instance that is.
That information is carried along with the `TeamPolicy` the called provided.

#### 2.2.1 `Kokkos::Serial`

In `Kokkos::Serial` it happens in `ParallelFor::execute`:

```c++
auto* internal_instance = m_policy.space().impl_internal_space_instance();
```
*[core/src/Serial/Kokkos_Serial_Parallel_Team.hpp#L249](https://github.com/kokkos/kokkos/blob/d5a4802911318aebecbc775990dd198260ce2383/core/src/Serial/Kokkos_Serial_Parallel_Team.hpp#L249)*

#### 2.2.2 `Kokkos::Cuda`

In `Kokkos::Cuda` this happens in in the `ParallelFor` ctor:

```c++
auto internal_space_instance =
    m_policy.space().impl_internal_space_instance();
```
*[core/src/Cuda/Kokkos_Cuda_Parallel_Team.hpp#L539-L540](https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_Parallel_Team.hpp#L539-L540)*


### 2.3 Ask the Execution Space Instance to Ensure that much Scratch Space is Available

#### 2.3.1 `Kokkos::Serial`

In `Kokkos::Serial` it happens in `ParallelFor::execute`

```c++
internal_instance->resize_thread_team_data(
    pool_reduce_size, team_reduce_size, team_shared_size,
    thread_local_size);
```
*https://github.com/kokkos/kokkos/blob/d5a4802911318aebecbc775990dd198260ce2383/core/src/Serial/Kokkos_Serial_Parallel_Team.hpp#L253-L255*

This `resize_thread_team_data` does a lot of work.
Suffice it to say it manages various allocations that this execution space instance can use inside Kokkos parallel regions.

#### 2.3.2 `Kokkos::Cuda`

In `Kokkos::Cuda` this happens in the `ParallelFor` ctor...

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
*[core/src/Cuda/Kokkos_Cuda_Parallel_Team.hpp#L567-L574](https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_Parallel_Team.hpp#L567-L574)*


### 2.4 Construct the Team handles and call the functor

The team handles are provided to the functor, and through these handles, the functor has access properties of the Team (size, index, scratch space, etc).

#### 2.4.1 `Kokkos::Serial`

In `Kokkos::Serial`'s `ParallelFor::exec`, a `Member` is constructed for each index in the league iteration space, and the functor is immediately called on that member.
Since only one team executes at a time, they all use the same scratch allocation that lives inside `data`.

```c++
  template <class TagType>
  inline std::enable_if_t<std::is_void<TagType>::value> exec(
      HostThreadTeamData& data) const {
    for (int ileague = 0; ileague < m_league; ++ileague) {
      m_functor(Member(data, ileague, m_league));
    }
  }
```
*[core/src/Serial/Kokkos_Serial_Parallel_Team.hpp#L225-L231](https://github.com/kokkos/kokkos/blob/d5a4802911318aebecbc775990dd198260ce2383/core/src/Serial/Kokkos_Serial_Parallel_Team.hpp#L225-L231)*

This `HostThreadTeamData` holds the various scratch allocations, and is a member of the underlying `Host::Serial` instance.

#### 2.4.2 `Kokkos::Cuda`

In `Kokkos::Cuda`'s `ParallelFor::operator()`, the handles are constructed.
Since multiple teams can execute simultaneously, each handle gets its own slice of the backing scratch allocation according to which team it is and how large the team is.

```c++
this->template exec_team<WorkTag>(typename Policy::member_type(
    kokkos_impl_cuda_shared_memory<void>(), m_shmem_begin, m_shmem_size,
    (void*)(((char*)m_scratch_ptr[1]) +
            ptrdiff_t(threadid / (blockDim.x * blockDim.y)) *
                m_scratch_size[1]),
    m_scratch_size[1], league_rank, m_league_size));
```
*[core/src/Cuda/Kokkos_Cuda_Parallel_Team.hpp#L504-L509](https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_Parallel_Team.hpp#L504-L509)*

This handle is immediately passed to `ParallelFor::exec_team`, which just calls the functor with the member as an argument:

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
*[core/src/Cuda/Kokkos_Cuda_Parallel_Team.hpp#L478-L488](https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_Parallel_Team.hpp#L478-L488)*

In short, `ParallelFor::operator()` is just a single invocation of the functor using a single team member.
This team member is constructed using an index in a CUDA grid, so how does this actually get injected into a CUDA kernel launch?

Just like in `Kokkos::Serial`, `ParallelFor::execute` makes the magic happen.
It passes the constructed `ParallelFor` object (itself, `*this`), into a `CudaParallelLaunch`, helpfully annotated with a short comment.
Recall that that the grid dimensions, shared memory size, and CUDA stream are already known by this point, since they are determined in the `ParallelFor` ctor.

```c++
CudaParallelLaunch<ParallelFor, LaunchBounds>(
    *this, grid, block, shmem_size_total,
    m_policy.space()
        .impl_internal_space_instance());  // copy to device and execute
```
*https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_Parallel_Team.hpp#L527-L530*

Within `CudaParallelLaunch` (and most of `Kokkos_Cuda_KernelLaunch.hpp`), this `ParallelFor` type fills the template parameter `DriverType`.
Rather than a `ParallelFor` this could be a `ParallelReduce` or a `ParallelScan`, but we'll stick with `ParallelFor` for our purposes.

`CudaParallelLaunch` is templated on an `Experimental::CudaLaunchMechanism`, which is set to whatever `DeduceCudaLaunchMechanism<DriverType>::launch_mechanism` evaluates to.
This process happens at compile-time and is determined by things like the size of the functor.

```c++
template <class DriverType, class LaunchBounds = Kokkos::LaunchBounds<>,
          Experimental::CudaLaunchMechanism LaunchMechanism =
              DeduceCudaLaunchMechanism<DriverType>::launch_mechanism,
          bool DoGraph = DriverType::Policy::is_graph_kernel::value>
struct CudaParallelLaunch;
```
*[core/src/Cuda/Kokkos_Cuda_KernelLaunch.hpp#L692-L696](https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_KernelLaunch.hpp#L692-L696)*

`CudaParallelLaunch` is a derived class of `CudaParallelLaunchImpl`, which actually implements the machinery to launch the kernel: all the ctor of `CudaParallelLaunch` does at runtime is ask `CudaParallelLaunchImpl` to launch the kernel.

```c++
CudaParallelLaunch(Args&&... args) {
  base_t::launch_kernel((Args &&) args...);
}
```
*[core/src/Cuda/Kokkos_Cuda_KernelLaunch.hpp#L707-L709](https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_KernelLaunch.hpp#L707-L709)*

In turn, `CudaParallelLaunchImpl` is a derived class of `CudaParallelLaunchKernelInvoker`

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
  ...
```
*[core/src/Cuda/Kokkos_Cuda_KernelLaunch.hpp#L633-L641](https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_KernelLaunch.hpp#L633-L641)*

`CudaParallelLaunchImpl`'s `launch_kernel` method optionally adjusts the CUDA shared memory configuration (e.g. the split between L1 cache and shared memory), and then just calls `CudaParallelLaunchKernelInvoker`'s `invoke_kernel`

```c++
base_t::invoke_kernel(driver, grid, block, shmem, cuda_instance);
```
*[core/src/Cuda/Kokkos_Cuda_KernelLaunch.hpp#L669-L669](https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_KernelLaunch.hpp#L669-L669)*


Finally turn, `CudaParallelLaunchKernelInvoker`'s `invoke_kernel` method is finally what launches the kernel

```c++
static void invoke_kernel(DriverType const& driver, dim3 const& grid,
                          dim3 const& block, int shmem,
                          CudaInternal const* cuda_instance) {
  (base_t::
        get_kernel_func())<<<grid, block, shmem, cuda_instance->m_stream>>>(
      driver);
}
```
*[core/src/Cuda/Kokkos_Cuda_KernelLaunch.hpp#L361-L367](https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_KernelLaunch.hpp#L361-L367)*

Recall that `DriverType` is actually `ParallelFor`, so the `ParallelFor` object is what gets passed into whatever kernel function is being executed.

We've found where the CUDA kernel actually gets launched, but what is this function that it's launching?
`base_t` here is a `CudaParallelLaunchKernelFunc` (the parent class of `CudaParallelLaunchKernelInvoker`).
So what does this `get_kernel_func` from `CudaParallelLaunchKernelFunc` do?

```c++
get_kernel_func() {
  return cuda_parallel_launch_local_memory<DriverType, MaxThreadsPerBlock,
                                            MinBlocksPerSM>;
}
```
*[core/src/Cuda/Kokkos_Cuda_KernelLaunch.hpp#L331-L334](https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_KernelLaunch.hpp#L331-L334)*

and finally...

```c++
template <class DriverType>
__global__ static void cuda_parallel_launch_local_memory(
    const DriverType driver) {
  driver();
}
```
*[core/src/Cuda/Kokkos_Cuda_KernelLaunch.hpp#L85-L89](https://github.com/kokkos/kokkos/blob/1a3ea28f6e97b4c9dd2c8ceed53ad58ed5f94dfe/core/src/Cuda/Kokkos_Cuda_KernelLaunch.hpp#L85-L89)*

It is just a function that calls `operator()` from the `DriverType`, e.g. the `ParallelFor` instance.
If you'll recall, `operator()` is what constructs a `Member` from the location in the CUDA grid and the shared memory pointer, and actually executes the functor.


## 2.5 In Summary

When the application developer uses `team_shmem_size` on the functor or `set_scratch_size` on the `TeamPolicy`, they are making a request for how much scratch size to use.
Inside the backend, the `ParallelFor` object that represents the parallel region has access to the functor and the `TeamPolicy`, so it can tell the execution space instance how much scratch memory this parallel region will need.
The instance will ensure that much is available.
Then the `ParallelFor` object will create the Team member handles, each of which will include its own piece of the scratch space, and call the functor on those handles.
