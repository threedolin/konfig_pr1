#!/bin/sh
# задан только путь к VFS
cd "$(dirname "$0")/../.."
echo "=== только --vfs ==="
./run.sh --vfs tests/vfs/several < /dev/null
