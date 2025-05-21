#!/bin/sh

set -e

make -C /app migrate
make -C /app populate

exec "$@"
