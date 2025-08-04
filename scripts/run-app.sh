#!/bin/sh
set -e
set -x

scripts/prestart.sh
echo "Running start command: $@"
exec "$@"
