#!/bin/bash

set -euo pipefail

cd /Users/jasper/git/bobot/tinyusb/examples/device/cdc_msc

cmake -DBOARD=pico_sdk -B build
cmake --build build

echo "now connect the board and copy the uf2 file in build/ to it"
