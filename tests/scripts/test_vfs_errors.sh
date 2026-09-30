#!/bin/sh
# ошибки загрузки VFS и VFS по умолчанию
cd "$(dirname "$0")/../.."
echo "=== VFS: путь не существует ==="
./run.sh --vfs tests/vfs/no_such_dir < /dev/null
echo "код возврата: $?"
echo "=== VFS: файл вместо директории ==="
./run.sh --vfs tests/vfs/minimal/hello.txt < /dev/null
echo "код возврата: $?"
echo "=== VFS не задана (пустая VFS по умолчанию) ==="
./run.sh < /dev/null
echo "код возврата: $?"
