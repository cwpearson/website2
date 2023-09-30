+++
title = "Setting up Photoprism with HTTPS on Google Compute Engine"
date = 2021-01-03T00:00:00
lastmod = 2021-01-03T00:00:00
draft = false

# Authors. Comma separated list, e.g. `["Bob Smith", "David Jones"]`.
authors = ["Carl Pearson"]

tags = ["photoprism"]

summary = "Set up PhotoPrism on Google Cloud with docker-compose and a LetsEncrypt HTTPS certificate"

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

[PhotoPrism](https://photoprism.app/) is a server-based application for browsing, organizing, and sharing your photo collection.
Here, I describe how I set it up on a Google Compute Engine virtual machine using docker-compose, an nginx https proxy, and LetsEncrypt.

*Disclaimer: I know next to nothing about securing applications exposed to the internet. Use at your own risk.*

In this entire post, I assume your domain will be `photoprism.example.com`.
You'll need to change all instances of that throughout.

## The Google Cloud Instance

First, I created a new project in Google Compute just for this.
It simplifies the firewall rules.

Depending on whether you want automatic Tensorflow image labeling:

* *no*: e2-micro (2 vCPU, 1GB RAM). Needs swap during indexing.
* *yes*: e2-medium (2 vCPU, 4GB RAM). You can get away with e2-small (2 GB RAM) if you're willing to enable swap.

As for the other VM settings:

* Debian 10 image and 50 GB disk. The OS and photoprism docker images use quite a few GBs, and you need some space left for your pictures.
* Allow HTTP and HTTPS traffic.
  * LetsEncrypt `certbot` will try to connect to this machine over HTTP to validate you own the domain.
  * you can disable HTTP later.
* Create/attach a static IPv4 address to your instance.
* Add the corresponding custom resource record to your DNS (this allows `photoprism.example.com`. Change `photoprism` to a different subdomain if you like)
  * `photoprism A 1h <static IPv4 address>`

## docker, docker-compose, certbot, nginx, swapfile, pull photoprism images

This snippet will do it all in one shot.
If you don't need the swapfile, you can skip that part at the end.
The first part cribs the [current docker-ce install instructions for x86_64 debian](https://docs.docker.com/engine/install/debian/).
Check to make sure they are still current.

```bash
(
sudo apt-get update
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
sudo apt-key fingerprint 0EBFCD88
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/debian \
   $(lsb_release -cs) \
   stable"
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose wget htop nginx apache2-utils certbot python3-certbot-nginx
wget https://dl.photoprism.org/docker/docker-compose.yml
sudo docker-compose pull
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo "/swapfile none swap sw 0 0" | sudo tee -a /etc/fstab > /dev/null
)
```

## Get your HTTPS certificate with LetsEncrypt

*remember to change `photoprism.example.com`*

Run `sudo certbot certonly -d photoprism.example.com`

Since we installed nginx in the previous step, select the "nginx plugin" option (this is where you need HTTP allowed through the firewall).

After answering the prompts, the successful result was:

```txt
Plugins selected: Authenticator nginx, Installer None
Obtaining a new certificate
Performing the following challenges:http-01 challenge for photoprism.example.com
Waiting for verification...
Cleaning up challenges
IMPORTANT NOTES: - Congratulations! Your certificate and chain have been saved at:
/etc/letsencrypt/live/photoprism.example.com/fullchain.pem Your key file has been
saved at: /etc/letsencrypt/live/photoprism.example.com/privkey.pem Your cert will
expire on 2021-04-03. To obtain a new or tweaked version of this certificate in
the future, simply run certbot again. To non-interactively renew *all* of your
certificates, run "certbot renew" - If you like Certbot, please consider supporting
our work by:
Donating to ISRG / Let's Encrypt: https://letsencrypt.org/donate
Donating to EFF: https://eff.org/donate-le
```

## Configure and Start Photoprism

I used the photoprism commit `af71e5f704461012be028834ab499f9c2b8e0a7e` from Jan 2, 2021.

Photoprism is configured with `docker-compose.yml`.

You will need to choose and enter three seprate passwords.
I recommend not using special characters, as the wrong combo can cause things to try to look up environment variables with unpredicable results.
* `PHOTOPRISM_DATABASE_PASSWORD`/`MYSQL_PASSWORD`
* `PHOTOPRISM_ADMIN_PASSWORD`
* `MYSQL_ROOT_PASSWORD`

*Note that `PHOTOPRISM_DATABASE_PASSWORD` and `MYSQL_PASSWORD` must be the same.*


If you are using a smaller instance, also set
```yaml
PHOTOPRISM_WORKERS: 1
PHOTOPRISM_DISABLE_TENSORFLOW: "true"
```

To start photoprism, run `sudo docker-compose up -d`

You can look at logs with `sudo docker-compose logs`. you should not see anything like "failed to connect to database"

If you goof this up, you need to do something like (this will delete everything)

``` bash
sudo docker-compose down
sudo docker volume prune
sudo rm -r storage database
```

## Configure and Start NGINX

*remember to change `photoprism.example.com`*

I had to follow alternate instructions [here](https://docs.photoprism.org/getting-started/advanced/nginx-proxy-setup/) *(the current instructions [here](https://docs.photoprism.org/getting-started/proxies/nginx/) did not work for me)*.

First, create `/etc/nginx/sites-enabled/photoprism.example.com`

Put the following content in it.
This is taken from the PhotoPrism instructions, except `proxy_pass http://localhost:2342;` instead of `proxy_pass http://docker.homenet:2342;`

```txt
# PhotoPrism Nginx config with SSL HTTP/2 and reverse proxy
# This file gives you an example on how to secure you PP instance with SSL
server {
    # listen 80; # If you really need HTTP (unsecure) remove the "#" on the beginning. Not recommended!
    # listen [::]:80; # HTTP IPv6

    listen 443 ssl http2; # Listen on port 443 and enable ssl and HTTP/2
    listen [::]:443 ssl http2; # Same for IPv6

    # Put your domain name in here.
    server_name  photoprism.example.com;

    # - - - - - - - - - -
    # SSL security
    # - - - - - - - - - -
    ssl_certificate          /etc/letsencrypt/live/photoprism.example.com/fullchain.pem;
    ssl_certificate_key      /etc/letsencrypt/live/photoprism.example.com/privkey.pem;

    # Since the PP API is also used on Android, we have to keep TLS1.2 in here for a while.
    # A lot of the older Android devices do not support TLS1.3 yet :/
    ssl_protocols            TLSv1.2 TLSv1.3;

    # Use good and strong ciphers, disable weak and old ciphers
    ssl_ciphers              HIGH:!RC4:!aNULL:!eNULL:!LOW:!3DES:!MD5:!EXP:!PSK:!SRP:!DSS;

    # Enable HSTS (https://developer.mozilla.org/en-US/docs/Security/HTTP_Strict_Transport_Security)
    add_header Strict-Transport-Security "max-age=172800; includeSubdomains";

    # This checks if the certificate has been invalidated by the certificate authority
    # You can remove this section if you use self-singed certificates...
    # Enable OCSP stapling (http://blog.mozilla.org/security/2013/07/29/ocsp-stapling-in-firefox)
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/photoprism.example.com/fullchain.pem;

    # DNS Servers to use for OCSP lookups
    resolver 8.8.8.8 1.1.1.1 9.9.9.9 valid=300s;
    resolver_timeout 5s;

    # - - - - - - - - -
    # Reverse Proxy
    # - - - - - - - - -
    proxy_redirect           off;
    proxy_set_header         X-Real-IP $remote_addr;                        # Let PP know the clients real IP
    proxy_set_header         X-Forwarded-For $proxy_add_x_forwarded_for;    # Let PP know that a proxy did forward this request
    proxy_set_header         Host $http_host;                               # Set Proxy host info

    proxy_http_version 1.1;                                                 # Required for WebSocket connection
    proxy_set_header Upgrade $http_upgrade;                                 # Allow protocol switch to websocket
    proxy_set_header Connection "upgrade";                                  # Do protocol switch
    proxy_set_header X-Forwarded-Proto $scheme;                             # Let PP know that this connection used HTTP or HTTPS

    client_max_body_size 500M;                                              # Bump the max body size, you may want to upload huge stuff via the upload GUI
    proxy_buffering off;                                                    # Do not hold back the request while the client sends data, give the stream directly to PP

    location / {
            # Optional; additional protection with Basic Auth.
            # Note: This breaks WebDAV without additional configuration
            #       You also have to create a .htpasswd file using the command:
            #       "htpasswd -c /etc/nginx/.pp_htpasswd my_secret_user"
            # - - -
            # auth_basic           "PhotoPrism Pre Auth";
            # auth_basic_user_file /etc/nginx/.pp_htpasswd;

            # pipes the traffic to PhotoPrism
            # Change this to your PhotoPrisms IP / DNS
            proxy_pass http://localhost:2342;
    }
}

```

Then run `sudo systemctl restart nginx`.
You should see no errors

## Try it Out

Navigate to [https://photoprism.example.com](https://photoprism.example.com) and log in with the `PHOTOPRISM_ADMIN_PASSWORD` you chose previously.

## Automatic Restart

Once everything is working, set up automatic image restart.
I guess this causes the photoprism image to be restarted unless you explicitly shut it down.

* `docker-compose stop`
* uncomment out the restart portion of `docker-compose.yml`
* `docker-compose up -d`


## To renew the LetsEncrypt Certificate

1. Shut down photoprism `docker-compose stop`
2. Stop nginx proxy: `systemctl stop nginx`
3. Edit the VM to allow HTTP traffic
4. Renew the cert `sudo certbot certonly -d photoprism.example.com`
5. Start nginx `systemctl start nginx`
6. Start photoprism `docker-compose up -d`

## Get updates

```bash
docker-compose pull photoprism
docker-compose stop photoprism
docker-compose up -d photoprism
```



## All Finished!

Congrats!

`unattended-upgrades` seems to be configured by default on the Google Compute debian image.
You almost certainly want this.

I set up a weekly automated snapshot under `Compute Engine` > `Snapshots` > `Snapshot Schedules`.
Attach it to the machine on the `Disks` page with `Edit`.
