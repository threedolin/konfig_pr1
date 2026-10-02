#!/bin/sh
# этап 5: команды rm и chown на VFS "deep"
# после работы проверяем, что файлы на диске не изменились
cd "$(dirname "$0")/../.."
before=$(ls -lR tests/vfs/deep)
echo "=== этап 5: VFS deep ==="
./run.sh --vfs tests/vfs/deep --script tests/scripts/start_stage5.txt
after=$(ls -lR tests/vfs/deep)
if [ "$before" = "$after" ]; then
    echo "файлы VFS на диске не изменились"
else
    echo "ОШИБКА: файлы VFS на диске изменились"
fi
