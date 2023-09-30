+++
title = "Setting up Python with Pyenv and Poetry on Debian"
date = 2021-08-22T00:00:00
lastmod = 2022-06-23T00:00:00
draft = false

# Authors. Comma separated list, e.g. `["Bob Smith", "David Jones"]`.
authors = ["Carl Pearson"]

tags = []

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
  preview_only = true


categories = []

# Set captions for image gallery.


+++

Setting up a python development environment is annoying.
We'd especially like to avoid:

* Using the system python: it may be way out of date, have special modifications, or be required for the system to function (and therefore we should avoid messing with it).
* Installing packages globally: different projects may require different versions, and the system may have its own package requirements that conflict with ours.

The solution has two components:
1. install and use whatever version of python you like
2. create isolated environments using your preferred version of python for each project

## Pyenv

[pyenv](https://github.com/pyenv/pyenv) is a version manger for python.
It streamlines the installation and use of multiple python version on a single system.

On Debian, you can visit [pyenv-installer](https://github.com/pyenv/pyenv-installer) to install pyenv.

Then, I had to add to my `.zshrc`:
```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
```

To install new python versions using pyenv, you may need to install the python build dependencies:
```bash
sudo apt-get update; sudo apt-get install make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

Basically, `pyenv` allows you to associate different python versions with different directories.

* `pyenv install -l`: list pythons available to install
* `pyenv install ...`: install a python
* `pyenv versions`: list installed pythons
* `pyenv shell ...`: use a python version in the current shell
* `pyenv local ...`: set the python to use in this directory

## Poetry

Poetry is a package manager for python.
It needs python to install, but once it is installed it will use whatever python is in your path (i.e., whatever you set with `pyenv`).
If the system python is new enough, it is fine to use the system python to install poetry.

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
```

This added `export PATH="$HOME/.poetry/bin:$PATH"` to my `.zshrc`.
You may need to follow the instructions to do something similar.

It's also nice to

```bash
poetry config virtualenvs.in-project true
```

This puts the virtualenv configuration files in the directory you use poetry in, as opposed to a centralized location.
The downside is you won't want to commit these files to your version control.


## Putting it together
An example of use

Outside of any particular project, you'll need some versions of python for whatever work you need.
```bash
pyenv install 3.9.6
```

Then, to create a new project
```bash
mkdir test && cd test
pyenv local 3.9.6 # when you cd into test, `python` will be python 3.9.6
poetry init 
poetry add numpy
echo "import numpy\nimport sys\nprint(sys.version)\nprint(numpy.version.version)" > test.py
poetry run python test.py
```