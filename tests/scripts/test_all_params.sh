#!/bin/sh
# все параметры сразу, справка и неверный параметр
cd "$(dirname "$0")/../.."
echo "=== --vfs и --script ==="
./run.sh --vfs /home/user/my_vfs --script tests/scripts/start_ok.txt < /dev/null
echo "=== --help ==="
./run.sh --help
echo "=== неверный параметр ==="
./run.sh --abc
