+++
title = "Single-header C++ Matrix Market Reader"
date = 2021-07-30T00:00:00
lastmod = 2021-07-30T00:00:00
draft = false

# Authors. Comma separated list, e.g. `["Bob Smith", "David Jones"]`.
authors = ["Carl Pearson"]

tags = ["sparse"]

summary = "GPLv3 single-header C++11 Matrix Market Reader"

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
  preview_only = true


categories = []

# Set captions for image gallery.


+++

I'm continually re-writing some C++ code to read [Matrix Market files](https://math.nist.gov/MatrixMarket/formats.html), a common format for distributing matrices.
I finally got around to writing something that I should be able to reuse.

The code is [available on github](github.com/cwpearson/matrix-market).

An example follows:

```c++
#include "mm/mm.hpp"

int main(int argc, char **argv)
{
    if (argc < 2)
    {
        std::cerr << "Usage: " << argv[0] << " <file.mtx>\n";
        exit(EXIT_FAILURE);
    }
    const std::string path = argv[1];

    {
        std::cout << "with Ordinal=int, Scalar=float, Offset=size_t" << std::endl;
        typedef int Ordinal;
        typedef float Scalar;
        typedef MtxReader<Ordinal, Scalar> reader_t;
        typedef typename reader_t::coo_type coo_t;
        typedef typename coo_t::entry_type entry_t;

        // read matrix as coo
        reader_t reader(path);
        coo_t coo = reader.read_coo();

        // non-zeros, rows, cols
        std::cout << coo.nnz() << std::endl;                               // size_t
        std::cout << coo.num_rows() << "," << coo.num_cols() << std::endl; // int

        // first entry
        entry_t e = coo.entries[0];
        std::cout << e.i << "," << e.j << std::endl; // int, int
        std::cout << e.e << std::endl;               // float
    }

    {
        std::cout << "with Ordinal=int64_t, Scalar=std::complex<float>, Offset=int" << std::endl;
        typedef MtxReader<int64_t, std::complex<float>, int> reader_t;
        typedef typename reader_t::coo_type coo_t;
        typedef typename coo_t::entry_type entry_t;

        // read matrix as coo
        reader_t reader(path);
        coo_t coo = reader.read_coo();

        // non-zeros, rows, cols
        std::cout << coo.nnz() << std::endl;                               // int
        std::cout << coo.num_rows() << "," << coo.num_cols() << std::endl; // complex<double>

        // first entry
        entry_t e = coo.entries[0];
        std::cout << e.i << "," << e.j << std::endl; // int64_t
        std::cout << e.e << std::endl;               // complex<double>
    }
    return 0;
}
```