"""Точка входа в эмулятор."""

import argparse
import sys

from shell import Emulator


def parse_args():
    """Читает параметры командной строки."""
    parser = argparse.ArgumentParser(description="Эмулятор командной строки")
    parser.add_argument("--vfs", help="путь к физическому расположению VFS")
    parser.add_argument("--script", help="путь к стартовому скрипту")
    return parser.parse_args()


def main():
    """Запускает эмулятор: загрузка VFS, стартовый скрипт, потом REPL."""
    args = parse_args()
    emu = Emulator(vfs_path=args.vfs, script_path=args.script)
    emu.print_params()
    if not emu.load_vfs():
        sys.exit(1)
    if args.script:
        emu.run_script(args.script)
    emu.run()


if __name__ == "__main__":
    main()
