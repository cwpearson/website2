+++
title = "Goal-Oriented Metaprogramming"
date = 2023-01-28T00:00:00
lastmod = 2023-01-28T00:00:00
draft = false

# Authors. Comma separated list, e.g. `["Bob Smith", "David Jones"]`.
authors = ["Carl Pearson"]

tags = ["c++"]

summary = ""

# Projects (optional).
#   Associate this post with one or more of your projects.
#   Simply enter your project's folder or file name without extension.
#   E.g. `projects = ["deep-learning"]` references 
#   `content/project/deep-learning/index.md`.
#   Otherwise, set `projects = []`.
projects = []

# Featured image
# To use, add an image named `featured.jpg/png` to your project's folder. 
[image]
  # Caption (optional)
  caption = ""

  # Focal point (optional)
  # Options: Smart, Center, TopLeft, Top, TopRight, Left, Right, BottomLeft, Bottom, BottomRight
  focal_point = "Center"

  # Show image only in page previews?
  preview_only = false


categories = []

# Set captions for image gallery.


+++

# So you want to...

C++ types are not [first-class citizens](https://en.wikipedia.org/wiki/First-class_citizen).
You cannot pass them as arguments or return them from functions, nor assign them to variables.
This makes it challenging to manipulate them in a straightforward way as you would any other value.

C++ is such a large language (especially since C++ 11), that it's possible to do nearly anything.
The trick is to figure out what language feature to use to accomplish your objective.

## ...write a function of types that returns a type

Since types are not first-class citizens in C++, this is impossible.
Instead, define a template struct.
The template parameters are the "function" arguments, and a [type alias](https://en.cppreference.com/w/cpp/language/type_alias) is the return type:

```c++
template <typename T, typename U>
struct make_a_tuple {
  using result = std::tuple<T, U>;
};
```

`make_a_tuple` is a "function" that takes two types and yields an `std::tuple` of those types:

```c++
auto tup = typename make_a_tuple<int, float>::result;
```

(since `make_a_tuple::result` is a dependent type, you need the `typename` keywork to tell C++ that `make_a_tuple<...>::result` is a type).

## ... write a function of types that returns a value

You can't write a function that takes a type as an argument and returns a value.
There are two options here.
If the value is tightly associated with the type, you can use a static constexpr member function, a static const member, or an enum (for integral types).
I'm not sure why you would prefer one over the other.

```c++
template <unsigned I>
struct Int {
    static consteval int twice_function() {return I*2;}
    static const int twice_member = I * 2;
    enum : unsigned {twice_enum = I*2};
};

void foo() {
    Int<3>::twice_function();
    Int<3>::twice_member;
    Int<3>::twice_enum;
}
```

The second option is to define a template function that returns a value:

```c++
template <typename T, typename U>
consteval size_t size_of_pair() {
  return sizeof(std::make_pair<T(), U()>);
}

void foo() {
  size_t sz = size_of_pair<int, float>();
}
```

The second option is more attractive if you need to do some more complicated operation on types.

## ... operate conditionally on tupes

The simplest options is to use  `std::conditional` from `<type_traits>`.

```c++
template <typename T, typename U>
struct larger_type {
  using type = std::conditional<
    sizeof(T) >= sizeof(U), // predicate (convertible to bool)
    T,  // if true
    U   // if false
  >::type;
};

void foo() {
  using Int = typename larger_type<long, int>::type;
}
```

This approach breaks down when anything you want to do in your conditional operation is not supported by both types.
For example, using `larger_type` on `void` (can't use `sizeof` on `void`).
The other more subtle failure is when your true or false type is invalid for some reason, regardless of whether it is selected by `std::conditional`.

## ... operate conditionally on types but `std::conditional` doesn't work

You have to use [SFINAE](https://en.cppreference.com/w/cpp/language/sfinae).



