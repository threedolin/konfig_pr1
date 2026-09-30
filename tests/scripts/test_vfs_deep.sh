#!/bin/sh
# загрузка VFS "deep" и выполнение стартового скрипта этапа 3
cd "$(dirname "$0")/../.."
echo "=== VFS: deep ==="
./run.sh --vfs tests/vfs/deep --script tests/scripts/start_stage3.txt
