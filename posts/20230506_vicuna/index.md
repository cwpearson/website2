+++
title = "Running Vicuna-13B in Google Cloud"
date = 2023-05-06T00:00:00
lastmod = 2023-05-06T00:00:00
draft = false

# Authors. Comma separated list, e.g. `["Bob Smith", "David Jones"]`.
authors = ["Carl Pearson"]

tags = []

summary = "How to experiment with hosting Vicuna-13B on a cloud VM"

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

[Vicuna-13B](https://lmsys.org/blog/2023-03-30-vicuna/) is an LLM chatbot based off of the LLaMa model.
It's authors claim it achieves 90% of the quality of ChatGPT in a "fun and non-scientific" evaluation.

You can rent some cloud hardware and experiment with Vicuna 13B yourself!
Using CPU-only is slow (couple tokens per second), but fast enough for yout to get an idea of what to expect.

## Set up your Cloud Instance

Create a cloud VM with
* 150 GB of disk space
* 64 GB of CPU memory

I used a Google Compute Engine `e2-standard-16`, which costs around $0.70/hour, so it may not be something you want to leave running. You can stop the instance when you're not using it.

When everything was done, my VM had 132GB of disk space used.

Ordinarily I wouldn't recommend setting up python like this, but since we're just experimenting:

```
apt-get install python3-pip
```

## Acquire the LLaMa-13B model

For licensing reasons, Vicuna-13B is distributed as a delta of the LLaMa model, so the first step is to acquire the LLaMa model.
The official way is to request the weights from Meta, by filling this [Google Docs form](https://docs.google.com/forms/d/e/1FAIpQLSfqNECQnMkycAp2jP4Z9TFX0cGR4uf7b_fBxjY_OjhJILlKGA/viewform?usp=send_form).

You can also use leaked weights from a torrent with the following magnet link:

`magnet:?xt=urn:btih:b8287ebfa04f<HASH>cf3e8014352&dn=LLaMA`

> NOTE
> replace `<HASH>` above with this: `879b048d4d4404108`

Or, someone has made the leaked weights available on IPFS, which you can access through a helpful mirror:

https://ipfs.io/ipfs/Qmb9y5GCkTG7ZzbBWMu2BXwMkzyCKcUjtEKPpgdZ7GEFKm/

I couldn't figure out how to get a torrent client working on Google's VMs (perhaps a firewall issue), so I ended up using [aria2c]() to download the LLaMa weights from the IPFS mirror above.

```
apt-get install aria2

mkdir -p $HOME/llama/13B
cd $HOME/llama/13B
aria2c https://ipfs.io/ipfs/QmPCfCEERStStjg4kfj3cmCUu1TP7pVQbxdFMwnhpuJtxk/consolidated.00.pth
aria2c https://ipfs.io/ipfs/QmPCfCEERStStjg4kfj3cmCUu1TP7pVQbxdFMwnhpuJtxk/consolidated.01.pth
aria2c https://ipfs.io/ipfs/QmPCfCEERStStjg4kfj3cmCUu1TP7pVQbxdFMwnhpuJtxk/checklist.chk
aria2c https://ipfs.io/ipfs/QmPCfCEERStStjg4kfj3cmCUu1TP7pVQbxdFMwnhpuJtxk/params.json
aria2c https://ipfs.io/ipfs/Qmb9y5GCkTG7ZzbBWMu2BXwMkzyCKcUjtEKPpgdZ7GEFKm/tokenizer.model
```

The `consolidated` files are the weights.
`checklist.chk` has the md5 sums for the files, which you should check after they're downloaded.
`params.json` seems to have some metadata.
Finally, `tokenizer.model` is needed to convert the weights to HuggingFace format.

## Convert weights to HuggingFace Format

```
pip install torch transformers accelerate sentencepiece protobuf==3.20
python3 convert_llama_weights_to_hf.py --input_dir ~ --output_dir ~/llama-hf --model_size 13B
```

I used [rev d2ffc3fc4 of the script](https://github.com/huggingface/transformers/blob/d2ffc3fc48430f629c38c36fa8f308b045d1f715/src/transformers/models/llama/convert_llama_weights_to_hf.py).

```
apt-get install wget

wget https://github.com/huggingface/transformers/blob/d2ffc3fc48430f629c38c36fa8f308b045d1f715/src/transformers/models/llama/convert_llama_weights_to_hf.py

pip install torch transformers accelerate sentencepiece protobuf==3.20

python3 convert_llama_weights_to_hf.py --input_dir $HOME/llama --output_dir $HOME/llama-hf --model_size 13B
```

These are the package versions that worked for me (note `protobuf=3.20` in the pip install command).

| package        | version |
|----------------|---------|
|`torch`         | 2.0.0   |
|`transformers`  | 4.28.1  |
|`accelerate`    | 0.18.0  |
|`sentencepiece` | 0.1.99  |
|`protobuf`      | 3.20.0  |

I got an error about regenerating protobuf functions if I used protobuf > 3.20.

## Apply the vicuna deltas

[FastChat](https://github.com/lm-sys/FastChat) has done the work of getting a little chat interface set up.
We'll use their package to download the deltas and apply them as well.

```
pip install fschat
python3 -m fastchat.model.apply_delta \
  --base-model-path $HOME/llama_hf \
  --target-model-path $HOME/vicuna-13b \
  --delta-path lmsys/vicuna-13b-delta-v1.1
```

I had `fschat 0.2.5`.

## Start Chatting

This will open up a little Chat-GPT-style interface in your terminal.

```
python3 -m fastchat.serve.cli --device cpu --model-path vicuna-13b/
```