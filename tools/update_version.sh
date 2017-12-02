#!/usr/bin/env bash

current_version=`grep -oiP "(?<=VERSION \= \')([0-9.]+)(?=\')" setup.py`
current_version_re=${current_version//./\\.}

function last_changelog
{
  pcregrep -M --match-limit=0 "1\.7\.0 / \d{4}-\d\d-\d\d\n==================\n\n[^=]+\d+\.\d+\.\d+ / \d{4}-\d\d-\d\d\n==================" CHANGELOG.md | tail -n +4| head -n -3
}
function usage
{
      echo "Usage: $0 [parameters]"
      echo "      -v | --version <version>"
      echo "      -d | --dry-run"
      echo
      echo "For example: $0 -v 1.9.2"

}

dry=

while [ "$1" != "" ]; do
    case $1 in
        -v | --version )        shift
                                new_version=$1
                                ;;
        -d | --dry-run )        dry=1
                                ;;
        -h | --help )           usage
                                exit
                                ;;
        * )                     usage
                                exit 1
    esac
    shift
done

if [ -n "$dry" ]; then
  echo_cmd=echo
  echo "Dry run"
else
  echo_cmd= 
fi

echo "Current version is $current_version"
if [ -n "$new_version" ]; then
    echo "New version $new_version"
    $echo_cmd sed -e "s/${current_version_re}/${new_version}/g" -i "" cloudinary/__init__.py
    $echo_cmd sed -e "s/${current_version_re}/${new_version}/g" -i "" setup.py
    $echo_cmd git changelog -t $new_version
else
    usage
    exit
fi

