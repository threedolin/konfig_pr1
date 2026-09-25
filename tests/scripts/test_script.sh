#!/bin/sh
# задан только стартовый скрипт: без ошибок, с ошибками, несуществующий
cd "$(dirname "$0")/../.."
echo "=== --script без ошибок ==="
./run.sh --script tests/scripts/start_ok.txt < /dev/null
echo "=== --script с ошибками ==="
./run.sh --script tests/scripts/start_errors.txt < /dev/null
echo "=== --script несуществующий файл ==="
./run.sh --script tests/scripts/no_file.txt < /dev/null
