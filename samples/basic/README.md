Cloudinary Python sample project
================================

This sample is a synchronous script that shows the upload process from local file, remote URL, with different transformations and options.

## Installing and running in 5 simple steps

1. Install [Python](http://www.python.org/getit/)
1. Install [Cloudinary python egg](https://github.com/cloudinary/pycloudinary#setup)
1. Get [a cloudinary account](https://cloudinary.com/users/register/free)
1. Setup the `CLOUDINARY_URL` environment variable by copying it from the [Management Console](https://cloudinary.com/console):

    Using zsh/bash/sh

        $ export CLOUDINARY_URL=cloudinary://API-Key:API-Secret@Cloud-name

    Using tcsh/csh

        $ setenv CLOUDINARY_URL cloudinary://API-Key:API-Secret@Cloud-name

    Using Windows command prompt/PowerShell

        > set CLOUDINARY_URL=cloudinary://API-Key:API-Secret@Cloud-name

1. Run the script:

        $ python basic.py

In order to delete the uploaded images using Cloudinary's Admin API, run the script:

        $ python basic.py cleanup


Good luck!
