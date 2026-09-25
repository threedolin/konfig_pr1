#!/bin/sh
# задан только путь к VFS
cd "$(dirname "$0")/../.."
echo "=== только --vfs ==="
./run.sh --vfs /home/user/my_vfs < /dev/null
