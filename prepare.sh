#!/bin/bash

/bin/rm -rf cloudinary/static/cloudinary
mkdir -p cloudinary/static/cloudinary
cd cloudinary/static/cloudinary

OPTIONS=

# GNU tar does not support wildcards by default, it needs explicit --wildcards option,
# while BSD tar does not recognize this option
if tar --version | grep -q 'gnu'; then
    OPTIONS='--wildcards'
fi

curl -L https://github.com/cloudinary/cloudinary_js/tarball/master | tar zxvf - --strip=1 --exclude test $OPTIONS '*/html' '*/js'

