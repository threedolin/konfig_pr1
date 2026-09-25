#!/bin/sh
# запуск эмулятора
cd "$(dirname "$0")"
python3 src/main.py "$@"
