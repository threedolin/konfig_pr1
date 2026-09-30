"""Тесты загрузки VFS (этап 3).

Запуск из корня репозитория: PYTHONPATH=src python3 -m unittest discover tests
"""

import io
import os
import unittest
from contextlib import redirect_stdout

from shell import Emulator
from vfs import VFSError, count_items, load_vfs

VFS_DIR = os.path.join(os.path.dirname(__file__), "vfs")


def vfs_path(name):
    """Возвращает путь к тестовой VFS."""
    return os.path.join(VFS_DIR, name)


class TestLoadVfs(unittest.TestCase):
    """Тесты функции load_vfs."""

    def test_minimal(self):
        """Минимальная VFS: один файл."""
        vfs = load_vfs(vfs_path("minimal"))
        self.assertEqual(count_items(vfs), (0, 1))
        hello = vfs["children"]["hello.txt"]
        self.assertEqual(hello["type"], "file")
        self.assertIn(b"minimal", hello["content"])

    def test_several(self):
        """Несколько файлов в корне."""
        vfs = load_vfs(vfs_path("several"))
        self.assertEqual(count_items(vfs), (0, 4))

    def test_deep(self):
        """Не меньше трех уровней вложенности."""
        vfs = load_vfs(vfs_path("deep"))
        home = vfs["children"]["home"]
        drafts = home["children"]["user"]["children"]["docs"]
        drafts = drafts["children"]["drafts"]
        self.assertEqual(drafts["type"], "dir")
        self.assertIn("draft1.txt", drafts["children"])

    def test_not_found(self):
        """Несуществующий путь - ошибка."""
        with self.assertRaises(VFSError):
            load_vfs(vfs_path("no_such_dir"))

    def test_not_a_directory(self):
        """Файл вместо директории - ошибка формата."""
        with self.assertRaises(VFSError):
            load_vfs(os.path.join(vfs_path("minimal"), "hello.txt"))

    def test_disk_not_changed(self):
        """Изменения VFS в памяти не трогают файлы на диске."""
        vfs = load_vfs(vfs_path("several"))
        del vfs["children"]["todo.txt"]
        self.assertTrue(os.path.exists(vfs_path("several/todo.txt")))


class TestEmulatorVfs(unittest.TestCase):
    """Загрузка VFS через эмулятор."""

    def load(self, path):
        """Загружает VFS в эмулятор, возвращает эмулятор, результат, вывод."""
        emu = Emulator(vfs_path=path)
        out = io.StringIO()
        with redirect_stdout(out):
            ok = emu.load_vfs()
        return emu, ok, out.getvalue()

    def test_load_ok(self):
        """Успешная загрузка, имя VFS берется из имени папки."""
        emu, ok, out = self.load(vfs_path("deep"))
        self.assertTrue(ok)
        self.assertEqual(emu.vfs_name, "deep")
        self.assertIn("папок - 9, файлов - 7", out)

    def test_load_error(self):
        """Ошибка загрузки выводится пользователю."""
        _, ok, out = self.load(vfs_path("no_such_dir"))
        self.assertFalse(ok)
        self.assertIn("не удалось загрузить VFS", out)

    def test_default_vfs(self):
        """Без пути остается пустая VFS по умолчанию."""
        emu, ok, _ = self.load(None)
        self.assertTrue(ok)
        self.assertEqual(count_items(emu.vfs), (0, 0))


if __name__ == "__main__":
    unittest.main()
