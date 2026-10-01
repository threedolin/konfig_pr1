"""Команды эмулятора: ls, cd, uname, who, wc.

Каждая команда - функция cmd_имя(emu, args), где emu - эмулятор,
args - список аргументов. Функция возвращает текст для вывода.
Если произошла ошибка, текст начинается с "Ошибка".
"""

import os
import platform
import sys
import time

from vfs import find_node, resolve_path

ERROR_PREFIX = "Ошибка"
MAX_CD_ARGS = 1
ONE_ITEM = 1
DIR_SIZE = 4096
LS_FLAGS = "l"
UNAME_FLAGS = "asnrm"
UNAME_ORDER = "snrm"
WHO_FLAGS = "H"
WC_FLAGS = "lwc"
DEFAULT_TERMINAL = "pts/0"


def split_flags(args):
    """Делит аргументы на флаги (-l, -la) и остальные аргументы.

    Возвращает строку со всеми буквами флагов и список остальных
    аргументов. Например: ["-la", "docs"] -> ("la", ["docs"]).
    """
    flags = ""
    other = []
    for arg in args:
        if arg.startswith("-") and arg != "-":
            flags += arg[1:]
        else:
            other.append(arg)
    return flags, other


def check_flags(name, flags, allowed):
    """Проверяет флаги команды. Возвращает текст ошибки или пустую строку."""
    for letter in flags:
        if letter not in allowed:
            return f"{ERROR_PREFIX}: {name}: неверный флаг -{letter}"
    return ""


def get_node(emu, path):
    """Ищет элемент VFS по пути относительно текущей папки."""
    return find_node(emu.vfs, resolve_path(emu.cwd, path))


def node_size(node):
    """Размер элемента: для файла - в байтах, для папки - 4096."""
    if node["type"] == "dir":
        return DIR_SIZE
    return len(node["content"])


def format_item(name, node, long_format):
    """Одна строка вывода ls. В формате -l: тип, размер и имя."""
    if not long_format:
        return name
    kind = "d" if node["type"] == "dir" else "-"
    return f"{kind} {node_size(node):>6} {name}"


def list_dir(node, long_format):
    """Возвращает содержимое папки для ls."""
    names = sorted(node["children"])
    items = [format_item(n, node["children"][n], long_format) for n in names]
    if long_format:
        return "\n".join(items)
    return "  ".join(items)


def cmd_ls(emu, args):
    """ls [-l] [путь ...] - выводит содержимое папки.

    Без пути выводится текущая папка. Флаг -l - подробный вывод
    (тип: d - папка, - - файл; размер; имя).
    """
    flags, paths = split_flags(args)
    error = check_flags("ls", flags, LS_FLAGS)
    if error:
        return error
    long_format = "l" in flags
    if not paths:
        paths = ["."]
    blocks = []
    for path in paths:
        node = get_node(emu, path)
        if node is None:
            return f"{ERROR_PREFIX}: ls: нет такого файла или папки: {path}"
        if node["type"] == "file":
            blocks.append(format_item(path, node, long_format))
            continue
        text = list_dir(node, long_format)
        if len(paths) > ONE_ITEM:
            text = f"{path}:\n{text}"
        blocks.append(text)
    return "\n\n".join(blocks)


def cmd_cd(emu, args):
    """cd [путь] - переход в другую папку.

    Без аргументов или с ~ - переход в корень VFS (домашняя папка).
    """
    if len(args) > MAX_CD_ARGS:
        return f"{ERROR_PREFIX}: cd: слишком много аргументов"
    path = args[0] if args else "~"
    parts = resolve_path(emu.cwd, path)
    node = find_node(emu.vfs, parts)
    if node is None:
        return f"{ERROR_PREFIX}: cd: нет такой папки: {path}"
    if node["type"] != "dir":
        return f"{ERROR_PREFIX}: cd: это не папка: {path}"
    emu.cwd = parts
    return ""


def uname_info():
    """Сведения о реальной ОС, в которой работает эмулятор."""
    info = platform.uname()
    return {
        "s": info.system,
        "n": info.node,
        "r": info.release,
        "m": info.machine,
    }


def cmd_uname(emu, args):
    """uname [-a] [-s] [-n] [-r] [-m] - сведения о системе.

    -s имя ядра (по умолчанию), -n имя компьютера, -r версия ядра,
    -m архитектура, -a все сразу.
    """
    flags, other = split_flags(args)
    if other:
        return f"{ERROR_PREFIX}: uname: лишний аргумент {other[0]}"
    error = check_flags("uname", flags, UNAME_FLAGS)
    if error:
        return error
    if "a" in flags:
        flags = UNAME_ORDER
    if not flags:
        flags = "s"
    info = uname_info()
    return " ".join(info[key] for key in UNAME_ORDER if key in flags)


def get_terminal():
    """Имя терминала, например pts/0 (если его нельзя узнать - pts/0)."""
    try:
        return os.ttyname(sys.stdin.fileno()).replace("/dev/", "")
    except (OSError, ValueError):
        return DEFAULT_TERMINAL


def cmd_who(emu, args):
    """who [-H] - кто работает в системе.

    Выводит имя пользователя, терминал и время входа (время запуска
    эмулятора). -H - вывести заголовок.
    """
    flags, other = split_flags(args)
    if other:
        return f"{ERROR_PREFIX}: who: лишний аргумент {other[0]}"
    error = check_flags("who", flags, WHO_FLAGS)
    if error:
        return error
    login = time.strftime("%Y-%m-%d %H:%M", time.localtime(emu.start_time))
    line = f"{emu.user:<10}{get_terminal():<12}{login}"
    if "H" in flags:
        return f"{'NAME':<10}{'LINE':<12}TIME\n{line}"
    return line


def count_text(content):
    """Считает строки, слова и байты в содержимом файла."""
    return {
        "l": content.count(b"\n"),
        "w": len(content.split()),
        "c": len(content),
    }


def format_counts(counts, flags, name):
    """Строка вывода wc для одного файла."""
    numbers = [str(counts[key]) for key in WC_FLAGS if key in flags]
    return " ".join(numbers) + " " + name


def cmd_wc(emu, args):
    """wc [-l] [-w] [-c] файл ... - количество строк, слов и байтов.

    Без флагов выводятся все три числа. Если файлов несколько,
    в конце выводится строка total.
    """
    flags, files = split_flags(args)
    error = check_flags("wc", flags, WC_FLAGS)
    if error:
        return error
    if not files:
        return f"{ERROR_PREFIX}: wc: не указан файл"
    if not flags:
        flags = WC_FLAGS
    lines = []
    total = {"l": 0, "w": 0, "c": 0}
    for path in files:
        node = get_node(emu, path)
        if node is None:
            return f"{ERROR_PREFIX}: wc: нет такого файла: {path}"
        if node["type"] == "dir":
            return f"{ERROR_PREFIX}: wc: {path} - это папка"
        counts = count_text(node["content"])
        for key in total:
            total[key] += counts[key]
        lines.append(format_counts(counts, flags, path))
    if len(files) > ONE_ITEM:
        lines.append(format_counts(total, flags, "total"))
    return "\n".join(lines)
