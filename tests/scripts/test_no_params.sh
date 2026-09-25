#!/bin/sh
# запуск без параметров
cd "$(dirname "$0")/../.."
echo "=== без параметров ==="
./run.sh < /dev/null
