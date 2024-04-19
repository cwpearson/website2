+++
title = "std::is_constructible is (at best) Poorly Named"
date = 2024-04-19T00:00:00-0700
description = ""
tags = ["c++"]
+++

Consider the following C++ code

```c++
#include <type_traits>

struct S {
    template <typename T>
    S(T t) {
        static_assert(!std::is_same_v<T, float>, "");
    }
};

void foo() {
    static_assert(std::is_constructible_v<S, float>, "");
    // S(1.0f); // not okay, construct with T = float
}
```

`S` is a template `struct` parameterized on `T` with a constructor that `static_assert`s that `T` is not float: constructing an `S` with a `float` argument yields a compile-time error.
Even so, `std::is_constructible_v<S, float>` is `true`.

The [C++ 11 standard](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2012/n3337.pdf), which introduced `std::is_constructible`, says

> `is_constructible<T, Args...>` shall be satisfied if and only if the following variable definition would be well-formed for some invented variable `t`: `T t(create<Args>()...)`;

A well-formed expression is presumably one that is part of a well-formed program, which is a

> C++ program constructed according to the syntax rules, diagnosable semantic rules, and the One Definition Rule (3.2).

`S(1.0f)` is certainly valid syntax, and our mini-program follows ODR, so that leaves whether this `static_assert` failure is a diagnosable semantic rule.
In general I think it is not - imagine this

```c++
#include <type_traits>

struct S {
    template <typename T> S(T t); // float specialization defined elsewhere
};

void foo() {
    static_assert(std::is_constructible_v<S, float>, ""); // seems reasonable
}
```

Another way of thinking about is is that in the language of the C++ standard, a *constraint* is a condition for the function's participation in overload resolution.
Likewise, a *mandate* is a condition that if not met renders the program ill-formed.
Basically, `std::is_constructible_v` is operating at the level of *constraint*s as far as C++ is concerned.
Since `S(float)` is available to participate in overload resolution, `std::is_constructible_v` is happy, even though the actual program is ill-formed by *mandate*.
In this manner, it's kind of like being allowed to do `decltype(S(1.0f))` even though actually writing `S(1.0f)` in your program results in a compile-time error.

Perhaps `std::is_constructible` just needs a new name, like `std::is_constructor_defined`.