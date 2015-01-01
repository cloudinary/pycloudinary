#!/bin/bash

/bin/rm -rf cloudinary/static
mkdir -p cloudinary/static
cd cloudinary/static
curl -L https://github.com/cloudinary/cloudinary_js/tarball/master | tar zxvf - --strip=1 --exclude README.md --exclude test --exclude samples

