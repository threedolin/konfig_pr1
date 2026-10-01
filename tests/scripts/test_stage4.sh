#!/bin/sh
# этап 4: команды ls, cd, uname, who, wc на VFS "deep"
cd "$(dirname "$0")/../.."
echo "=== этап 4: VFS deep ==="
./run.sh --vfs tests/vfs/deep --script tests/scripts/start_stage4.txt
