#!/bin/sh
# загрузка VFS "minimal" и выполнение стартового скрипта этапа 3
cd "$(dirname "$0")/../.."
echo "=== VFS: minimal ==="
./run.sh --vfs tests/vfs/minimal --script tests/scripts/start_stage3.txt
