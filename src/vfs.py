"""Виртуальная файловая система (VFS), которая хранится в памяти.

Источник VFS - директория на диске. При загрузке вся директория
(папки и содержимое файлов) читается в словари Python. Дальше эмулятор
работает только с этими словарями, файлы на диске не изменяются.

Как устроены элементы VFS:
    папка - {"type": "dir", "children": {имя: элемент, ...}}
    файл  - {"type": "file", "content": b"содержимое файла"}
"""

import os


class VFSError(Exception):
    """Ошибка загрузки VFS."""


def make_dir():
    """Создает пустую папку VFS."""
    return {"type": "dir", "children": {}}


def make_file(content):
    """Создает файл VFS с указанным содержимым (bytes)."""
    return {"type": "file", "content": content}


def read_file(path):
    """Читает содержимое файла с диска в память."""
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError as e:
        raise VFSError(f"не удалось прочитать файл {path}: {e.strerror}")


def load_dir(path):
    """Рекурсивно читает папку с диска и возвращает папку VFS."""
    node = make_dir()
    try:
        names = sorted(os.listdir(path))
    except OSError as e:
        raise VFSError(f"не удалось прочитать папку {path}: {e.strerror}")
    for name in names:
        full_path = os.path.join(path, name)
        if os.path.islink(full_path):
            continue
        if os.path.isdir(full_path):
            node["children"][name] = load_dir(full_path)
        elif os.path.isfile(full_path):
            node["children"][name] = make_file(read_file(full_path))
    return node


def load_vfs(path):
    """Загружает VFS из директории на диске.

    Если путь не существует или это не директория, выбрасывается VFSError.
    """
    if not os.path.exists(path):
        raise VFSError(f"путь к VFS не найден: {path}")
    if not os.path.isdir(path):
        raise VFSError(f"неверный формат VFS, нужна директория: {path}")
    return load_dir(path)


def count_items(node):
    """Считает количество папок и файлов внутри папки (рекурсивно)."""
    dirs = 0
    files = 0
    for child in node["children"].values():
        if child["type"] == "dir":
            sub_dirs, sub_files = count_items(child)
            dirs += 1 + sub_dirs
            files += sub_files
        else:
            files += 1
    return dirs, files


def resolve_path(cwd, path):
    """Переводит путь в список имен от корня VFS.

    cwd - текущая папка (список имен), path - путь, который ввел
    пользователь. Корень VFS - это домашняя папка "~". Поддерживаются
    абсолютные пути (/a/b), пути от ~ (~/a), относительные пути, "." и "..".
    """
    if path == "~" or path.startswith("~/"):
        parts = []
        path = path[1:]
    elif path.startswith("/"):
        parts = []
    else:
        parts = list(cwd)
    for name in path.split("/"):
        if name in ("", "."):
            continue
        if name == "..":
            if parts:
                parts.pop()
        else:
            parts.append(name)
    return parts


def find_node(root, parts):
    """Ищет элемент VFS по списку имен. Если не найден, возвращает None."""
    node = root
    for name in parts:
        if node["type"] != "dir" or name not in node["children"]:
            return None
        node = node["children"][name]
    return node


def path_to_str(parts):
    """Превращает список имен в строку для приглашения: ~, ~/home/user."""
    if not parts:
        return "~"
    return "~/" + "/".join(parts)
