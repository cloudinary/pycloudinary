#!/usr/bin/env bash

# Update version number and prepare for publishing the new version

set -o errexit

# Extract the last entry or entry for a given version
# The function is not currently used in this file.
# Examples:
#   changelog_last_entry
#   changelog_last_entry 1.10.0
#

function changelog_last_entry
{
  sed -e "1,/^${1}/d" -e '/^=/d' -e '/^$/d' -e '/^[0-9]/,$d' CHANGELOG.md
}

function verify_dependencies
{
    # Test if the gnu grep is installed
    if ! grep --version | grep -q GNU
    then
        echo "GNU grep is required for this script"
        echo "You can install it using the following command:"
        echo ""
        echo "brew install grep --with-default-names"
        exit
    fi

    if [[ -z "$(type -t git-changelog)" ]]
    then
        echo "git-extras packages is not installed."
        echo "You can install it using the following command:"
        echo ""
        echo "brew install git-extras"
        exit
    fi
}

function usage
{
      echo "Usage: $0 [parameters]"
      echo "      -v | --version <version>"
      echo "      -d | --dry-run print the commands without executing them"
      echo "      -h | --help print this information and exit"
      echo
      echo "For example: $0 -v 1.9.2"
}

function process_arguments
{
    # Empty to run the rest of the line and "echo" for a dry run
    cmd_prefix=

    while [ "$1" != "" ]; do
        case $1 in
            -v | --version )
                shift
                new_version=${1:-}
                if ! [[ "$new_version" =~ [0-9]+\.[0-9]+\.[0-9]+(\-.+)? ]]; then
                  echo "You must supply a new version after -v or --version"
                  echo "For example:"
                  echo "  1.11.0"
                  echo "  1.11.0-rc1"
                  echo ""
                  usage
                  exit 1
                fi
                ;;
            -d | --dry-run )
                cmd_prefix=echo
                echo "Dry Run"
                echo ""
                ;;
            -h | --help )
                usage
                exit
                ;;
            * )
              usage
              exit 1
        esac
        shift || true
    done
}

function update_version
{

    local current_version=`grep -oiP "(?<=VERSION \= \")([0-9.]+)(?=\")" cloudinary/__init__.py`
    # Use literal dot character in regular expression
    local current_version_re=${current_version//./\\.}

    echo "# Current version is $current_version"
    echo "# New version is ${new_version}"
    if [ -n "$new_version" ]; then
        local __GIT_ROOT=$(git rev-parse --show-toplevel)
        local __ORIGINAL_DIR=$PWD
        cd $__GIT_ROOT

        # add a quote if this is a dry run
        __q=${cmd_prefix:+"'"}

        $cmd_prefix sed -E -i '.bak' \
            "${__q}s/version = \"${current_version_re}\"/version = \"${new_version}\"/${__q}"       \
            setup.py

        $cmd_prefix sed -E -i '.bak' \
            "${__q}s/VERSION = \"${current_version_re}\"/VERSION = \"${new_version}\"/${__q}" \
            cloudinary/__init__.py

        $cmd_prefix git changelog -t $new_version || true

        echo ""
        echo "# After editing CHANGELOG.md, issue these commands:"
        echo git add setup.py cloudinary/__init__.py CHANGELOG.md
        echo git commit -m "\"Version ${new_version}\""
        echo sed \
          -e "'1,/^${new_version//./\\.}/d'" \
          -e "'/^=/d'" -e "'/^$/d'" \
          -e "'/^[0-9]/,\$d'" CHANGELOG.md \| git tag -a "'${new_version}'" --file=-
        cd $__ORIGINAL_DIR
    else
        usage
        exit
    fi

}

verify_dependencies
process_arguments $*
update_version
