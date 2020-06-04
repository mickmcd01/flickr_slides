Purpose: take an album of photos from flickr, add the title
and the date taken, and put them in a directory where they
can be used as a rotating background on your screen (at least
they can on Linux Mint).

Step 1: On flickr, request a zip of an album
Step 2: Download the zip
Step 3: Prepare a settings.py file based on example_settings.py
Step 3: Run this script

usage: flickr_slides.py [-h] [--zip ZIP] [--slides SLIDES] [--name NAME]
                        [--photoset PHOTOSET]

optional arguments:
  -h, --help           show this help message and exit
  --zip ZIP            full path to the zip file
  --slides SLIDES      full path to the slides directory
  --name NAME          name of the slides sub-directory
  --photoset PHOTOSET  ID of the flickr photoset

Note: photoset ID is the numeric portion of the URL for the album
In this URL: https://www.flickr.com/photos/mickmcd/albums/72157711362446296,
72157711362446296 is the photoset ID.