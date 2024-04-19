+++
title = "C++ API Design"
date = 2024-03-27T00:00:00-0700
description = ""
tags = ["c++"]
+++

## Different Symbols

Let's say I have a collection of related functions, like the `MPI_Send` family of functions.
They all have the same signature (with the exception of `MPI_Isend`), and they all have relatively subtle differences in semantics.

```c++
int MPI_Send(const void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm)
int MPI_Isend(const void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm, MPI_Request *request)
int MPI_Ssend(const void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm)
int MPI_Rsend(const void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm)
int MPI_Bsend(const void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm)
```

The path the MPI standard chose to take was the following:
* The user chooses which style they want by using a different symbol in their program (e.g. `MPI_Send` vs `MPI_Isend`).
* Since each function is a different symbol, they can have different signatures. 
  * However, the MPI standards people decided to have `MPI_Isend` have an output parameter for the `request` rather than a different return type.

I think the standards committee could have just as easily done:

```c++
struct IsendResult {
    int err;
    MPI_Request req;
};

int         MPI_Send( const void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm)
IsendResult MPI_Isend(const void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm)
int         MPI_Ssend(const void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm)
int         MPI_Rsend(const void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm)
int         MPI_Bsend(const void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm)
```

Which in my opinion would have been a better choice from a C++ perspective.
I prefer defining these kinds of return structs rather than using `std::pair` or `std::tuple` because then the members of the return type have meaningful names rather than just numbers.

Maybe the commitee could have even gone as far as:

```c++
struct SendResult {
    int err;
};

struct IsendResult {
    int err;
    MPI_Request req;
};

SendResult  MPI_Send( const void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm)
IsendResult MPI_Isend(const void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm)
SendResult  MPI_Ssend(const void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm)
SendResult  MPI_Rsend(const void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm)
SendResult  MPI_Bsend(const void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm)
```

One could imagine even changing the above `struct`s to use the PIMPL idiom to help maintain binary compatibility, but leaving that aside...

## Overloading

Another option would have been to do an overload

```c++
// Immediate ommitted since the signature is different
enum class Mode {
    Blocking,
    Buffered,
    Immediate,
    Ready,
    Synchronous
};

struct SendResult {
    int err;
    MPI_Request req;
};

SendResult send(const void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm, const Mode mode = Mode::Blocking)
```

This reduces the number of public APIs we have, which is nice, but there are several downsides.
Some compile-time information is moved to run-time, which reduces the number of errors that can be caught statically.
* The implementation needs to include a run-time switch on the `mode` argument, which will probably farm out internally to separate implementation functions anyway.
* meaningful members of `SendResult` depend on the function arguments, which the C++ type system cannot help you with (imagine getting a send return somewhere far away from the callsite - how do you know wether `req` is okay to access? Maybe an additional field that discriminates on the `mode` parameter of the `send` call that generated it? Or maybe a sentinel value for `req`?)


## Full Specialization
The final option is full specialization of a generic function template.
This basically moves the `mode` parameter from the "Overload" case from run-time back to compile-time.

```c++
enum class Mode {
    Blocking,
    Buffered,
    Immediate,
    Ready,
    Synchronous
};

// most modes just return an error code
template <Mode mode>
struct SendReturn {
    using type = int;
}

// Immediate return value includes an MPI_Request
struct IsendResult {
    int err;
    MPI_Request req;
};
template<> struct SendReturn<Mode::Immediate> {
    using type = IsendResult;
}

template <Mode mode>
SendReturn<mode>::type send(const void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm);

template<>
SendReturn<Mode::Blocking>::type send<Mode::Blocking>(const void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm) {
    // implementation of blocking send
}

// other full specializations
```

This is largely equivalent to the "Different Symbols" implementation, just expressed through template specialization rather than different symbols.

Since this is a function template, all specializations need to match the same template, so to have different return types we return a template `SendResult` object that is specialized on the mode as well.
The fields in this `SendResult` depends on the mode, so there's no danger of accidentally accessing a meaningless `req` field from a non-Immediate send.

The real question is, does this buy you anything over the "Different Symbols" method?
I think this just moves our function call machinery from symbol lookup to template resolution, and I don't think the user or the implementer gets anything in return.

