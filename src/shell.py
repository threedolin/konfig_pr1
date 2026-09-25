"""Эмулятор командной строки UNIX."""

import getpass
import socket

MAX_CD_ARGS = 1
ERROR_PREFIX = "Ошибка"


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


class Emulator:
    """Эмулятор оболочки с приглашением user@host:~$."""

    def __init__(self, vfs_path=None, script_path=None):
        """Берет имя пользователя и хоста из реальной ОС.

        vfs_path - путь к VFS, script_path - путь к стартовому скрипту.
        """
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.user = getpass.getuser()
        self.host = socket.gethostname()
        self.cwd = "~"
        self.running = True
        self.commands = {
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "exit": self.cmd_exit,
        }

    def get_prompt(self):
        """Возвращает строку приглашения к вводу."""
        return f"{self.user}@{self.host}:{self.cwd}$ "

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
        return self.commands[name](args)

    def cmd_ls(self, args):
        """Заглушка ls: печатает имя команды и аргументы."""
        return f"ls, аргументы: {args}"

    def cmd_cd(self, args):
        """Заглушка cd: печатает имя команды и аргументы."""
        if len(args) > MAX_CD_ARGS:
            return f"{ERROR_PREFIX}: cd: слишком много аргументов"
        return f"cd, аргументы: {args}"

    def cmd_exit(self, args):
        """Завершает работу эмулятора."""
        if args:
            return f"{ERROR_PREFIX}: exit: команда не принимает аргументы"
        self.running = False
        return ""

    def print_params(self):
        """Отладочный вывод параметров, с которыми запущен эмулятор."""
        print("[debug] Параметры запуска:")
        print(f"[debug]   vfs    = {self.vfs_path}")
        print(f"[debug]   script = {self.script_path}")

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
