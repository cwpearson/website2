+++
title = "Implementation of a Integer Linear Programming Solver in Python"
date = 2022-04-05T00:00:00
lastmod = 2022-04-05T00:00:00
draft = false

# Authors. Comma separated list, e.g. `["Bob Smith", "David Jones"]`.
authors = ["Carl Pearson"]

tags = ["python"]

summary = "Roll your own integer linear programming (ILP) solver using Scipy."

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

<!-- style math  -->
<script>
    document.addEventListener("DOMContentLoaded", function() {
        renderMathInElement(document.body, {
          // customised options
          // • auto-render specific keys, e.g.:
          delimiters: [
              {left: '$$', right: '$$', display: true},
              {left: '$', right: '$', display: false},
              {left: '\\(', right: '\\)', display: false},
              {left: '\\[', right: '\\]', display: true}
          ],
          // • rendering keys, e.g.:
          throwOnError : false
        });
    });
</script>

## Introduction

Integer linear programming problems are common in many domains.
I recently found myself experimenting with formulating a probem as an integer programming problem, and I realized that I didn't really understand how the various solvers worked, so I set out to implement my own.
This post is about the three pieces that need to be assembled to create one:

1. Expression trees and rewrite rules to provide a convenient interface.
2. Linear programming relaxation to get a non-integer solution (using `scipy.optimize.linprog`).
3. Branch-and-bound to refine the relaxed soltion to an integer solution.

You can follow along at [cwpearson/csips][https://github.com/cwpearson/csips]

## Problem Formulation

A [linear programming problem](https://en.wikipedia.org/wiki/Linear_programming) is an optimization problem with the following form:

find \\(\mathbf{x}\\) to maximize
$$
\mathbf{c}^T\mathbf{x}
$$

subject to 

$$\begin{aligned}
A\mathbf{x} &\leq \mathbf{b} \cr
0 &\leq \mathbf{x} \cr
\end{aligned}$$

For [integer linear programming (ILP)](https://en.wikipedia.org/wiki/Integer_programming), there is one additional constrait:

$$
\mathbf{x} \in \mathbb{Z}
$$

In plain english, \\(\mathbf{x}\\) is a vector, where each entry represents a variable we want to find the optimal value for.
\\(\mathbf{c}\\) is a vector with one weight for each entry of \\(\mathbf{x}\\).
We're trying to maximize the dot product  \\(\mathbf{c}^T\mathbf{x}\\); we're just summing up each  each entry of entry of \\(\mathbf{x}\\) weighted by the corresponding entry of \\(\mathbf{c}\\).
For example, if we seek to maximize the sum of the first two entries of \\(\mathbf{x}\\), the first two entries of \\(\mathbf{c}\\) will be \\(1\\) and the rest \\(0\\).

**What about Minimizing instead of Maximizing?** 
Just maximize \\(-\mathbf{c}^T\mathbf{x}\\) instead of maximizing \\(\mathbf{c}^T\mathbf{x}\\).

**What if one of my variables needs to be negative?** 
At first glance, it appears \\(0 \leq \mathbf{x}\\) will be a problem.
However, we'll just construct \\(A\\) and \\(\mathbf{b}\\) so that all constraints are relative to \\(-\mathbf{x}_i\\) instead of \\(\mathbf{x}_i\\) for variable \\(i\\).

## Example

To specify our problem, we must specify \\(A\\), \\(\mathbf{b}\\), and \\(\mathbf{c}^T\\).

For simple problems it might be convenient enough to do this unassisted, for [example (pdf)](https://faculty.math.illinois.edu/~mlavrov/docs/482-spring-2020/lecture33.pdf):

find \\(x,y\\) to maximize
$$
4x + 5y
$$

subject to 

$$\begin{aligned}
x + 4y &\leq 10 \cr
3x - 4y &\leq 6 \cr
0 &\leq x,y
\end{aligned}$$

We have two variables \\(x\\) and \\(y\\), so Our \\(\mathbf{x}\\) vector will be two entries, \\(\mathbf{x}_0\\) for \\(x\\) and \\(\mathbf{x}_1\\) for \\(y\\).
Correspondingly, \\(A\\) will have two columns, one for each variable, and our \\(\mathbf{c}\\) will have two entries, one for each variable.
We have two constraints, so our \\(A\\) will have two rows, one for each constraint.

```python
cT = [4, 5]    # maximize 4x + 5y
A_ub = [
    [1, 4],    # constraint 1:  x + 4y
    [3, -4],   # constraint 2: 3x - 4y
]
b_ub = [
  10,          # constraint 1 <= 10
   6,          # constraint 2 <= 6
] , 
```
How do we handle \\(0 \leq x,y\\)?
We'll cover that later when we talk about scipy's `linprog` function to actually solve this.

## User-friendly Interface

* Implemented in [expr.py](https://github.com/cwpearson/csips/blob/master/csips/expr.py)

If your problem is complicated it can get clumsy to specify every constraint and objective in this form, since you'llneed to massage all your constraints so that all the variables are on the left and are \\(\leq\\) a constant on the right.
It would be best to have the computer do this for you, and present a more natural interface akin to the following:

```python
m = Model()

x = m.int_1d(2) # 1 dimensional vector of two integer variables
m.constraint(    x[0] + 4 * x[1] <= 10) # x + 4y <= 10
m.constraint(3 * x[0] - 4 * x[1] <= 6)  # 3x - 4y <= 6
m.constraint(x[0] >= 0) # x >= 0
m.constraint(x[1] >= 0) # y >= 0

c, A_ub, b_ub = m.get_problem() # produce vectors and matrices
```

To do this, we'll introduce some python classes to represent nodes in an [expression tree](https://en.wikipedia.org/wiki/Binary_expression_tree) of our constraints.
Then we'll overload the `*`, `+`, `-`, `==`, `<=`, and `>=` operators on those classes to allow those nodes to be composed into a tree from a natural expression.

For example, an implementation of scaling a variable by an integer:

```python
class ScalExpr:
    def __init__(self, a, x):
        assert isinstance(a, int)
        assert isinstance(x, Var)
        self.a = a
        self.x = x

class Var:
    def __init__(self, ...):
        ...

    def __rmul__(self, lhs):
        assert isinstance(lhs, int)
        return ScalExpr(lhs, self)
```

Using part of the constraints above:
```python
3 * x[0]

# becomes
x[0].__rmul__(3)

# returns
ScalExpr(3, x[0])
```

which represents variable `x[0]` multiplied by integer `3`.
We can construct more complicated trees to support our expression grammar by extending these classes with additional operations (e.g. `__leq__`, `__sum__`, ...) and additional classes to represent summation expressions, less-or-equal equations, and so forth.

## Conversion to Standard Form

* Implemented at [csips.py](https://github.com/cwpearson/csips/blob/1f05f5377d0afa367e019a41ef1f11e4c54ad321/csips/csips.py#L109-L191)

Once each constraint (and the objective) are represented as expression trees, the challenge then becomes converting them into the standard form, e.g. all variables and scalar multiplications on the left-hand side (a row of \\(A\\)), and a single constant on the right-hand side (an entry of \\(\mathbf{b}\\)).
We can use a few [rewrite](https://en.wikipedia.org/wiki/Rewriting) rules to transform our expression trees into what we want.

Distribution:
$$
a \times (b + c) \rightarrow a \times b + a \times c
$$

```python
ScalExpr(a, SumExpr([b,c]))               # a * (b+c)
SumExpr([ScalExpr(a, b), ScalExpr(a, c)]) # a * b + a * c
```

Fold:
$$
a + b \rightarrow c
$$
```python
SumExpr([a, b]) # a + b  (sum of 2 ints)
SumExpr([a+b])  # c      (sum of a single int) where c = a + b
```

Move left
$$
a \leq b + c \rightarrow a - b \leq c
$$

Flip:
$$
a \geq b \rightarrow -a \leq -b
$$

By applying these rules, we can convert any of our expressions to one where a sum of scaled variables is on the left hand side of \\(\leq\\), and a single int is on the right hand side.
Then it's a simple matter of generating an \\(\mathbf{x}\\) with one entry per unique variable, \\(A\\) from the scaling on those variables, and \\(\mathbf{b}\\) from the right-hand side.

## Linear Program Relaxation

* Implemented at [csips.py](https://github.com/cwpearson/csips/blob/1f05f5377d0afa367e019a41ef1f11e4c54ad321/csips/csips.py#L304-L318)

The way this is usually done is actually by initially ignoring the integer constraint ( \\(\mathbf{x} \in \mathbb{Z}\\) ), then going back and "fixing" the non-integer parts of your solution.
When you ignore the integer constraint, you're doing what's called ["linear programming relaxation" (LP relaxation)](https://en.wikipedia.org/wiki/Linear_programming_relaxation).
Solving the LP relaxation will provide a (possibly non-integer) \\(\mathbf{x}\\).

We'll use [scipy's `linprog` function](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html) to solve the LP relaxation.

```python
from scipy import linprog
result = linprog(c, A_ub, b_ub, A_eq, b_eq, bounds)
```

Here's how `linprog`'s arguments map to our formulation

* `c`: this is \\(\mathbf{c}^T\\)
* `A_ub`: this is \\(A\\)
* `b_ub`: this is \\(\mathbf{b}\\)

`linprog` also allows us to specify bounds on \\(\mathbf{x}\\) in a convenient form.

* `bounds`: this allows us to provide bounds on \\(\mathbf{x}\\), e.g. providing the tuple `(0, None)` implements \\(0 \leq \mathbf{x}\\).
This is not strictly necessary since we can directly express this constraint using `A_ub` and `b_ub`.

`linprog` also allows us to specify additional constraints in the form \\(A\mathbf{x} = \mathbf{b}\\). 
This is not strictly necessary, since for a variable \\(i\\) we could just say \\(\mathbf{x}_i \leq c\\) and \\(-\mathbf{x}_i \leq -c\\) in our original formulation to achieve \\(\mathbf{x}_i = c\\).

* `A_eq`: \\(A\\) in optional \\(A\mathbf{x} = \mathbf{b}\\)
* `b_eq`: \\(\mathbf{b}\\) in optional \\(A\mathbf{x} = \mathbf{b}\\)

`linprog` will dutifully report the optimal solution as \\(x = 4\\), \\(y = 1.5\\), and \\(4x \times 5y = 23.5\\).
Of course, \\(y = 1.5\\) is not an integer, so we'll use "branch and bound" to refine towards an integer solution.

## Branch and Bound

* Implemented at [csips.py](https://github.com/cwpearson/csips/blob/1f05f5377d0afa367e019a41ef1f11e4c54ad321/csips/csips.py#L325-L389)

[Branch and bound](https://en.wikipedia.org/wiki/Branch_and_bound) is a whole family of algorithms for solving discrete and combinatorial optimization problems.
It represents the space of solutions in a tree, where the root node is all possible solutions.
Each node *branches* into two child nodes each which represents two non-overlapping smaller subsets of the full solution space.
As the tree is descended, the solution space will either shrink to 1 (a feasible solution) or 0 (no feasible solution).
As we discover feasible solutions, we will keep track of the best one.
At any point, we may be able to determine a *bound* on the best possible solution offered by a subset.
If that bound is worse than the best solution so far, we can skip that entire subtree.

For our ILP problem, the algorithm looks like this:

1. Initialize the best objective observed so far to \\(\inf\\)
2. Find the LP relaxation solution
3. If the LP relaxation objective is worse than the best solution so far, discard it. The integer solution will be no better than the relaxation solution, so if the relaxation solution is worse, then the integer solution will be too.
4. Else, push that solution onto a stack
5. Loop until the stack is empty
    1. Take solution off the stack
    2. If all \\(\mathbf{x}\\) entries are integers and the objective is the best so far, record it
    3. Else, branch to produce two child nodes. If \\(\mathbf{x}_i = c\\) is non-integer, two subproblems, each with one additional constraint \\(\mathbf{x}_i \leq \lfloor c \rfloor \\) and \\(\mathbf{x}_i \geq \lceil c \rceil \\)
6. Report the solution with the best result so far.

Doing so for our example will converge on a solution of \\(x = 2\\), \\(y = 2\\), and \\(4x \times 5y = 18\\).

In 5.3, there are [different ways](https://en.wikipedia.org/wiki/Branch_and_cut#Branching_strategies) to choose which non-integer variable to branch on.
CSIPS branches on the [first one](https://github.com/cwpearson/csips/blob/1f05f5377d0afa367e019a41ef1f11e4c54ad321/csips/branch.py#L13-L39) or the [most infeasible](https://github.com/cwpearson/csips/blob/1f05f5377d0afa367e019a41ef1f11e4c54ad321/csips/branch.py#L42-L72).

There are more sophisticated methods for solving the integer problem, such as branch-and-cut or branch-and-price.
Unfortunately, these are difficult to investigate using scipy's linprog, as none of its solver methods make the tableau form accessible.