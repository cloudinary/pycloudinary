#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

PY_VER=$(python -V 2>&1 | head -n 1 | cut -d ' ' -f 2);
SDK_VER=$(grep -oiP '(?<=version \= \")([a-zA-Z0-9\-.]+)(?=")' setup.py)


bash ${DIR}/allocate_test_cloud.sh "Python ${PY_VER} SDK ${SDK_VER}"
