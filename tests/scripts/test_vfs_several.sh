#!/bin/sh
# загрузка VFS "several" и выполнение стартового скрипта этапа 3
cd "$(dirname "$0")/../.."
echo "=== VFS: several ==="
./run.sh --vfs tests/vfs/several --script tests/scripts/start_stage3.txt
