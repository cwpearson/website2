+++
title = "Reverse HTTPS Proxy with Nginx"
date = 2021-08-23T00:00:00
lastmod = 2021-08-23T00:00:00
draft = true

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

Objective:

A single computer, hosting things like
* `app1.example.com`
* `app2.example.com`

Each app is represented by a different subdomain of a domain we've registered.

## Subdomain CNAME records

First, add some CNAME records to point those subdomains to your root domain
* `app1.example.com CNAME 1 hour  example.com.`
* `app2.example.com CNAME 1 hour  example.com.`

That should take a couple seconds / a couple minutes to propogate.
Check with 

```
nslookup app1.example.com
```

## nginx proxy

We'll use nginx proxy to aim incoming requests to `app1.example.com` to a particular port.

Start up a test service at the desired port:

```
python3 -m http.server 4567
python3 -m http.server 4568
```

Edit `/etc/nginx/nginx.conf` to do the forwarding.
In the `http` section, add something like

```nginx
server {
    listen 80;
    server_name app1.example.com;

    location / {
        proxy_pass http://localhost:4567;
    }   
}

server {
    listen 80;
    server_name app2.example.com;

    location / {
        proxy_pass http://localhost:4568;
    }   
}
```

Restart nginx

```
systemctl restart nginx`
```

Then navigate to `app1.example.com` and see your stuff!

## nginx proxy with https

