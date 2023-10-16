+++
title = "Nsight Systems and Nsight Compute Teaching Resources"
subtitle = ""
date = 2020-04-16T00:00:00
lastmod = 2020-04-16T00:00:00
draft = false

# Authors. Comma separated list, e.g. `["Bob Smith", "David Jones"]`.
authors = ["Carl Pearson"]

tags = ["GPU", "Nsight Compute", "Nsight Systems"]

summary = ""

# Projects (optional).
#   Associate this post with one or more of your projects.
#   Simply enter your project's folder or file name without extension.
#   E.g. `projects = ["deep-learning"]` references 
#   `content/project/deep-learning/index.md`.
#   Otherwise, set `projects = []`.
projects = ["nsight"]

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

I was invited to give a guest lecture for the Spring 2020 ECE 408 GPU programming course at the University of Illinois.
This lecture covers some performance measurement techniques available in CUDA.
The 75 minute lecture, available on Youtube in four parts:
* [Slides (pdf)](/pdf/20200416_nsight.pdf)
* [Part 1: Intro](https://youtu.be/uN2qju175aE)
* [Part 2: CUDA Events](https://youtu.be/yI137sSOlkU)
* [Part 3: Nsight Compute](https://youtu.be/UNX0KNMQlW8)
* [Part 4: Nsight Systems](https://youtu.be/YHrmnaPgFfY)

There is also a repository [cwpearson/nvidia-performance-tools](https://github.com/cwpearson/nvidia-performance-tools) which contains all the code examples used in the lecture.
It also contains Docker images for amd64 and ppc64le with Nsight Compute and Nsight Systems.

