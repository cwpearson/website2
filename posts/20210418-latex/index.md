+++
title = "Tips for Technical Writing in Latex"
date = 2021-04-18T00:00:00
lastmod = 2022-03-10T00:00:00
draft = false

# Authors. Comma separated list, e.g. `["Bob Smith", "David Jones"]`.
authors = ["Carl Pearson"]

tags = ["latex"]

summary = "Accumulated tips for formatting technical writing in Latex"

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

I recently finished my Ph.D thesis (yay!) and accumulated a few tips related to formatting technical writing in Latex.

## Hyphenation and Line Breaks

Many people are familiar with the `\hyphenation` command, which tells Latex where it may hyphenate words it does not already know about to prevent lines from being too long.
Latex will not know about many technical words, or function names that are not "plain english."
In English writing, line breaks should occur at syllable boundaries only.

```latex
\hyphenation{cuda-Memcpy-Peer-Async bi-di-rec-tion-al}
```

You can also allow breaks at underscores, which is convenient for certain programming languages or libraries.

```latex
\renewcommand\_{\textunderscore\allowbreak}
```

You may then want to *prevent* line breaks in some places.
Use `\mbox` for that.

```latex
\mbox{\_\_device\_\_}
```

Latex will only break already-hypenated words at the hyphen position.
You can add more optional breaks with `{\-}`

```latex
A super-hypenated-latex-confusing compound adjective.
A su{\-}per-hy{\-}phen{\-}at{\-}ed...
```

## lstlisting

The `lstlisting` environment is used to add and format code in Latex documents.
You can use `minipage` to prevent short `lstlistings` from being broken across pages.
You can also use the `\noindent` command to prevent the `minipage` from being indented if it starts a new paragraph
The 

```latex
\noindent
\begin{minipage}{\linewidth}
\begin{lstlisting}
\end{lstlisting}
```

## SI units

Use the `siunitx` package to automatically format numbers with SI units.
(`[binary-units]` may not be necessary depending on your version.)

```latex
\usepackage[binary-units]{siunitx}
\SI{512}{\byte}
```

In newer versions of the `siunitx` package, `\SI` may be replaced with `\qty`.

## Algorithm

Algorithm statements are often written in math mode, which treats consecutive letters as the product of variables and can lead to strange kerning.
You can fix with `\mathit{}`

```latex
\State $\mathit{word} \gets ...$
```

## Digit grouping and separators.

Latex can make it hard to manually format digit grouping and separators in numbers.
The `number` package makes this easy.

```latex
\usepackage[group-separator={,}]{siunitx}
\num{242000}
```

## CLI spell-checking

You can use `aspell` with the Latex filter (to reduce false positives).
The `-t` flag puts it in Latex mode.

```bash
aspell -t -c main.tex
```

## Latex and Version Control
Write one latex sentence on each line, so version control diffs are easier to follow.
It feels a little unnatural at first.

```latex
This is one sentence.
This is another sentence.
```

## Latex and arxiv

Arxiv does not want a raw PDF, annoyingly.
You can defined a makefile target that will create a zip for you to upload.
You'll need to tweak this to get all the files uploaded you need.
Arxiv usually wants the pre-processed `bib` file that ends in `bbl`, so you need to run `bibtex`.

```make
arxiv: main.tex main.bib ${FIGS}
  pdflatex ${PAPER}.tex
  bibtex ${PAPER}.aux
  rm -f upload.zip
  zip -r upload.zip main.tex main.bbl figures acmart.cls ACM-Reference*
```

## Tables that are too wide or too tall

Use `resizebox` for tables that are too wide or too tall (which is almost always the case, right???)

To match the text width:

```latex
\label{tab:related}
\resizebox{\textwidth}{!}{%
\begin{tabular}{...}
\end{tabular}
}%resizebox
\end{table*}
```

To match the text height:

```latex
\label{tab:related}
\resizebox{!}{\textheight}{%
\begin{tabular}{...}
\end{tabular}
}%resizebox
\end{table*}
```


## Reducing space between captions and figures

I think there is too much wasted space between figures and captions in some templates.
You may be able to tweak this yourself with the `caption` package.

```latex
\usepackage{caption}
\captionsetup{skip=1pt}
```

## Shortcuts for repeated formatting

You may wish to repeatedly apply formatting to a particular word.
You can define your own command for that.
The `xpsace` command will try to be smart about whether to put a space after the word.

```latex
\newcommand{\StreamData}{\textit{StreamData}\xspace}

Now \StreamData is in italics.

% notice the absence of \xspace
\newcommand{\DenseData}{\textit{DenseData}}

When I use \DenseData{} I may need to put the braces afterwords to get a space.
```

# Figures and text

Use the `pifont` package, and then the `\ding` command

```latex
\usepackage{pifont}

This: \ding{202} will make a black circle with a white "1" in it.
You can then draw a matching object in your figure.
\ding{203} will make a 2, \ding{204} will make a 3, etc.
```