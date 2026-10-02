"""Эмулятор командной строки UNIX."""

import getpass
import os
import socket
import time

from commands import (
    ERROR_PREFIX, cmd_cd, cmd_chown, cmd_ls, cmd_rm, cmd_uname, cmd_wc,
    cmd_who,
)
from vfs import VFSError, count_items, load_vfs, make_dir, path_to_str


class ParseError(Exception):
    """Ошибка при разборе введенной строки."""


def parse_line(line):
    """Разбивает строку на команду и аргументы.

    Слова разделяются пробелами. Текст в кавычках ("..." или '...')
    считается одним аргументом, например: cd "my folder".
    """
    words = []
    current = ""
    quote = None
    has_word = False
    for ch in line:
        if quote:
            if ch == quote:
                quote = None
            else:
                current += ch
        elif ch in "\"'":
            quote = ch
            has_word = True
        elif ch.isspace():
            if has_word:
                words.append(current)
            current = ""
            has_word = False
        else:
            current += ch
            has_word = True
    if quote:
        raise ParseError("не закрыта кавычка " + quote)
    if has_word:
        words.append(current)
    return words


def cmd_exit(emu, args):
    """exit - завершает работу эмулятора."""
    if args:
        return f"{ERROR_PREFIX}: exit: команда не принимает аргументы"
    emu.running = False
    return ""


class Emulator:
    """Эмулятор оболочки с приглашением user@host:~$."""

    def __init__(self, vfs_path=None, script_path=None):
        """Берет имя пользователя и хоста из реальной ОС.

        vfs_path - путь к VFS, script_path - путь к стартовому скрипту.
        """
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.vfs = make_dir()
        self.vfs_name = "default"
        self.user = getpass.getuser()
        self.host = socket.gethostname()
        self.cwd = []
        self.start_time = time.time()
        self.running = True
        self.commands = {
            "ls": cmd_ls,
            "cd": cmd_cd,
            "uname": cmd_uname,
            "who": cmd_who,
            "wc": cmd_wc,
            "rm": cmd_rm,
            "chown": cmd_chown,
            "exit": cmd_exit,
        }

    def get_prompt(self):
        """Возвращает строку приглашения к вводу.

        Текущая папка self.cwd хранится как список имен от корня VFS,
        корень показывается как ~.
        """
        return f"{self.user}@{self.host}:{path_to_str(self.cwd)}$ "

    def execute(self, line):
        """Выполняет одну строку и возвращает текст, который нужно вывести."""
        try:
            words = parse_line(line)
        except ParseError as e:
            return f"{ERROR_PREFIX}: {e}"
        if not words:
            return ""
        name = words[0]
        args = words[1:]
        if name not in self.commands:
            return f"{ERROR_PREFIX}: неизвестная команда '{name}'"
        return self.commands[name](self, args)

    def print_params(self):
        """Отладочный вывод параметров, с которыми запущен эмулятор."""
        print("[debug] Параметры запуска:")
        print(f"[debug]   vfs    = {self.vfs_path}")
        print(f"[debug]   script = {self.script_path}")

    def load_vfs(self):
        """Загружает VFS из директории vfs_path в память.

        Если путь не задан, остается пустая VFS по умолчанию.
        Возвращает False, если при загрузке произошла ошибка.
        """
        if self.vfs_path:
            try:
                self.vfs = load_vfs(self.vfs_path)
            except VFSError as e:
                print(f"{ERROR_PREFIX}: не удалось загрузить VFS: {e}")
                return False
            full_path = os.path.abspath(self.vfs_path)
            self.vfs_name = os.path.basename(full_path)
        dirs, files = count_items(self.vfs)
        print(f"[debug] VFS '{self.vfs_name}' загружена в память: "
              f"папок - {dirs}, файлов - {files}")
        return True

    def run_script(self, path):
        """Выполняет команды из стартового скрипта.

        Каждая команда выводится вместе с приглашением, как будто ее ввел
        пользователь. Строки с ошибками пропускаются, выполнение идет дальше.
        Пустые строки и строки с # не выполняются.
        """
        try:
            with open(path, encoding="utf-8") as f:
                lines = f.read().splitlines()
        except OSError as e:
            print(f"{ERROR_PREFIX}: не удалось открыть скрипт {path}: "
                  f"{e.strerror}")
            return
        for number, line in enumerate(lines, start=1):
            if not line.strip() or line.strip().startswith("#"):
                continue
            print(self.get_prompt() + line)
            result = self.execute(line)
            if result:
                print(result)
            if result.startswith(ERROR_PREFIX):
                print(f"[script] строка {number} с ошибкой пропущена")
            if not self.running:
                break

    def run(self):
        """Основной цикл REPL: читаем команду, выполняем, выводим."""
        while self.running:
            try:
                line = input(self.get_prompt())
            except (EOFError, KeyboardInterrupt):
                print()
                break
            result = self.execute(line)
            if result:
                print(result)
