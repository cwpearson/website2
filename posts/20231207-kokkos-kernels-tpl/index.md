+++
draft = true
title = Placeholder
+++

# How does the TPL and system work in Kokkos Kernels?

## Background

TPLs implement a subset of Kokkos Kernels interface.
Each TPL usually provides an implementation for certain combinations of types.

## Conceptual Architecture of the TPL system

Throughout, I will use placeholders COMPONENT, FUNC, and LIBWHATEVER.
1. COMPONENT is a Kokkos Kernels component, e.g. `blas` or `graph`.
2. FUNC is a specific function, e.g. `spmv` or `dgemm`.
3. PARAMETER_TYPES is a list of parameter types that a specific FUNC accepts. It might be different for e.g. `dgemm` and `zgemm`.
4. LIBWHATEVER is a specific TPL, e.g. MAGMA or oneMKL.

There are two primary pieces
1. The "**TPL availability struct**": 
2. The "**function implementation struct**": This struct has a static member function that implements above TPL/parameter type/function combination.

### **TPL Availability Struct**
The **TPL availability struct** has a single boolean member that says whether Kokkos Kernels know how to use a particular TPL for PARAMETER_TYPES to a particular FUNC.
This is a struct template, a standard C++ technique for creating values based on C++ type information.

### **Function Implementation Struct**
The **function implementation struct** is the core of the system.
It is a struct template, since what exactly it does varies depending on the types of its arguments.
It also has roles for the ETI system, which we ignore for this discussion.

```c++
template <
  PARAMETER_TYPES...,
  bool tpl_spec_avail = FUNC_tpl_spec_avail<PARAMETER_TYPES>::value,
  bool eti_spec_avail = ... // part of the ETI system
>
struct FUNC {
  static void func(PARAMETER_TYPES params...) {...}
}
```

For example, if `FUNC` was GEMM, then the PARAMETER_TYPES would be the types of the GEMM parameters, e.g. 2D `Kokkos::View`s for the three matrices, `size_t` for the leading dimensions, etc.
There are two additional, defaulted template parameters.
One is the corresponding **TPL availability struct**'s `value` (`true` if Kokkos Kernels is configured with a TPL that supports PARAMETER_TYPES).
The other we can ignore, as it's related to ETI


## Code of the TPL system

Each component has a `tpls` subdirectory, for example, `blas/tpls`.
In that directory, there is a pair of files for each interface, a `COMPONENT_FUNC_spec_avail.hpp` and `COMPONENT_FUNC_spec_decl.hpp` file.

> If the `tpls` directory is already a child of the `component` directory, why does it have `COMPONENT` in its name?
>
> This is namespacing: all Kokkos Kernels include directories are available during compilation

## The `impl/COMPONENT_FUNC_spec.hpp` file

> This file also has a lot of roles in the ETI system, but here we focus on what it does for the TPL system.

This file is responsible for declaring the function implementation struct template.


```c++

```


## the `impl/COMPONENT_FUNC_impl.hpp` file

## The `tpls/COMPONENT_FUNC_spec_avail.hpp` file

The purpose of this file is to define a "TPL availablilty struct": a struct, which given various template parameters, has a `value` member that is `false` if there is no TPL implementation of the function `FUNC`, or `true` otherwise.
It typically looks something like this:

```c++
// catch-all case
template<FUNC_ARG_TYPES...>
struct FUNC_tpl_spec_avail {
  enum : bool {value = false};
}

// LIBWHATEVER's macro & expansions
#if KOKKOSKERNELS_ENABLE_TPL_LIBWHATEVER

#define COMPONENT_FUNC_TPL_SPEC_AVAIL(PARAMS)
template<PARAMS>
struct FUNC_tpl_spec_avail {
  enum : bool {value = true};
}

// LIBWHATEVER's FUNC only works for double-precision args that are LayoutLeft and live in SYCL memory
COMPONENT_FUNC_TPL_SPEC_AVAIL(double, Kokkos::LayoutLeft, Kokkos::SYCLDeviceUSMSpace)
COMPONENT_FUNC_TPL_SPEC_AVAIL(double, Kokkos::LayoutLeft, Kokkos::SYCLDeviceUSMSpace)
#endif
```

The first part of the file defines an unspecialized `FUNC_tpl_spec_avail`, which is the catch-all case for unsupported argument types.
The rest consists of a different section for each TPL that offers this function.
For example, for an SpMV, there would be cuSparse and rocSparse and oneMKL, since each provide an SpMV implementation.
Each of those sections defines a macro, which expands into a specialization of the TPL availability struct, which has a member `value = true` for that specific combination of arguemnt types.

## The `tpls/COMPONENT_FUNC_spec_decl.hpp` file

This file is responsible for the declaration of the function implementation struct for all type combinations where the TPL availability struct's `value` member is true.
This is also done through a distinct macro for each COMPONENT and FUNC, since the implementation for any given function is usually identical across it's supported types, modulo the type names.

```c++
#define COMPONENT_FUNC_TPL_SPEC_DECL_LIBWHATEVER

#endif
```

Like the TPL availability struct, this one will have a sepratate specialization of the function implementation struct for each COMPONENT/FUNC and TPL.
