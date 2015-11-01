#!/usr/bin/env bash
GIT_ROOT=$(git rev-parse --show-toplevel)
CURRENT_DIR=$PWD
cd $GIT_ROOT
echo Updating version to $1
sed -E -i.bak "s/version = \'[0-9]\.[0-9]\.[0-9]+\'/\version = \'$1\'/" setup.py
grep -HEo "version = '[0-9]\.[0-9]\.[0-9]+'" setup.py
sed -E -i.bak "s/VERSION = \"[0-9]\.[0-9]\.[0-9]+\"/\VERSION = \"$1\"/" cloudinary/__init__.py
grep -HEo "VERSION = \"[0-9]\.[0-9]\.[0-9]+\"" cloudinary/__init__.py
#git add setup.py cloudinary/__init__.py CHANGELOG.md
#git commit -m "Version $1"
#git tag -a $1 -m "Version $1"
cd $CURRENT_DIR