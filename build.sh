#!/bin/bash
# Wrapper script for build_tools/build.sh
cd "$(dirname "$0")" || exit 1
./build_tools/build.sh "$@"

