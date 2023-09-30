+++
title = "PUMPS+AI 2019 Summer School"
subtitle = ""
date = 2019-06-26T00:00:00
lastmod = 2019-06-26T00:00:00
draft = false

# Authors. Comma separated list, e.g. `["Bob Smith", "David Jones"]`.
authors = ["Carl Pearson"]

tags = ["GPU", "BSC"]

summary = "TA at PUMPS+AI 2019"

# Projects (optional).
#   Associate this post with one or more of your projects.
#   Simply enter your project's folder or file name without extension.
#   E.g. `projects = ["deep-learning"]` references 
#   `content/project/deep-learning/index.md`.
#   Otherwise, set `projects = []`.
# projects = ["internal-project"]

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


#FIXME gallery
[[gallery_item]]
album = "gallery"
image = "carl_mentor.jpg"
caption = "Me mentoring Jakub (left) and Pavel (right) on their LBM code"
[[gallery_item]]
album = "gallery"
image = "tas.jpg"
caption = "Mert, Simon and me in front of Vertex on UPC campus"
[[gallery_item]]
album = "gallery"
image = "collaboration.jpg"
caption = "PUMPS students collaborating on Tuesday"

+++

It's my privilege to attend [PUMPS+AI 2019](https://pumps.bsc.es/2019/front-page-content) summer school in Barcelona!
The summer school was stared by my advisor, Professor Wen-mei Hwu and David Kirk (formerly of Nvidia).


## Monday

The first day of PUMPS, we mentored Pavel Eichler and Jakub Klinkovsky on GPU acceleration for a lattice-boltzmann-method-based computational fluid dynamics solver.
Mert Hidayetoglu, Simon Garcia de Gonzalo, and I helped them apply some binning and scatter-to-gather transformations for a key coordinate-transformation step of their code.

## Tuesday - Friday

The next three days consisted of morning lectures and afternoon hands-on labs for the students.
I was mostly responsible for maing the sure the students could use [rai](github.com/rai-project/rai) to do their [labs](github.com/illinois-impact/gpu-algorithms-labs), and I also TAed the labs:

* Scatter/Gather
* Binning
* Basic Convolution
* Tiled Convolution

## Saturday

The final day has the Barcelona Supercomputing Center teaching the students about OmpSs, a pragma-based parallel runtime.

