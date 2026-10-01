"""Тесты команд этапа 4: ls, cd, uname, who, wc.

Запуск из корня репозитория: PYTHONPATH=src python3 -m unittest discover tests
"""

import os
import platform
import unittest

from shell import Emulator
from vfs import load_vfs, resolve_path

VFS_DIR = os.path.join(os.path.dirname(__file__), "vfs")


def make_emulator(name):
    """Создает эмулятор с тестовой VFS."""
    emu = Emulator()
    emu.vfs = load_vfs(os.path.join(VFS_DIR, name))
    return emu


class TestPaths(unittest.TestCase):
    """Тесты разбора путей."""

    def test_relative(self):
        """Относительный путь от текущей папки."""
        self.assertEqual(resolve_path(["home"], "user/docs"),
                         ["home", "user", "docs"])

    def test_absolute_and_home(self):
        """Абсолютный путь и путь от ~."""
        self.assertEqual(resolve_path(["home"], "/etc"), ["etc"])
        self.assertEqual(resolve_path(["home"], "~/var"), ["var"])
        self.assertEqual(resolve_path(["home"], "~"), [])

    def test_dots(self):
        """Точка и две точки."""
        self.assertEqual(resolve_path(["a", "b"], "../c/./d"), ["a", "c", "d"])
        self.assertEqual(resolve_path([], "../.."), [])


class TestLs(unittest.TestCase):
    """Тесты ls."""

    def setUp(self):
        """Эмулятор с глубокой VFS."""
        self.emu = make_emulator("deep")

    def test_root(self):
        """ls без аргументов - текущая папка."""
        self.assertEqual(self.emu.execute("ls"), "etc  home  var")

    def test_path(self):
        """ls с путем."""
        self.assertEqual(self.emu.execute("ls home/user/docs"),
                         "drafts  report.txt")

    def test_long(self):
        """ls -l показывает тип и размер."""
        out = self.emu.execute("ls -l etc")
        self.assertIn("-      9 hostname", out)

    def test_several(self):
        """Несколько папок - с заголовками."""
        out = self.emu.execute("ls etc var")
        self.assertIn("etc:\nhostname  passwd", out)
        self.assertIn("var:\nlog", out)

    def test_errors(self):
        """Несуществующий путь и неверный флаг."""
        self.assertIn("нет такого файла", self.emu.execute("ls nope"))
        self.assertIn("неверный флаг", self.emu.execute("ls -z"))


class TestCd(unittest.TestCase):
    """Тесты cd."""

    def setUp(self):
        """Эмулятор с глубокой VFS."""
        self.emu = make_emulator("deep")

    def test_cd(self):
        """Переход в папку, назад и домой."""
        self.emu.execute("cd home/user")
        self.assertEqual(self.emu.cwd, ["home", "user"])
        self.assertEqual(self.emu.execute("ls"), "docs  music")
        self.emu.execute("cd ..")
        self.assertEqual(self.emu.cwd, ["home"])
        self.emu.execute("cd")
        self.assertEqual(self.emu.cwd, [])

    def test_errors(self):
        """Нет папки, файл вместо папки, много аргументов."""
        self.assertIn("нет такой папки", self.emu.execute("cd nope"))
        self.assertIn("это не папка", self.emu.execute("cd etc/passwd"))
        self.assertIn("слишком много", self.emu.execute("cd a b"))
        self.assertEqual(self.emu.cwd, [])


class TestUnameWho(unittest.TestCase):
    """Тесты uname и who."""

    def setUp(self):
        """Эмулятор с пустой VFS."""
        self.emu = Emulator()

    def test_uname(self):
        """uname берет данные из реальной ОС."""
        self.assertEqual(self.emu.execute("uname"), platform.system())
        self.assertEqual(self.emu.execute("uname -m"), platform.machine())
        self.assertIn(platform.release(), self.emu.execute("uname -a"))

    def test_uname_errors(self):
        """Лишний аргумент и неверный флаг."""
        self.assertIn("лишний аргумент", self.emu.execute("uname x"))
        self.assertIn("неверный флаг", self.emu.execute("uname -x"))

    def test_who(self):
        """who показывает пользователя, -H - заголовок."""
        self.assertTrue(self.emu.execute("who").startswith(self.emu.user))
        self.assertTrue(self.emu.execute("who -H").startswith("NAME"))
        self.assertIn("лишний аргумент", self.emu.execute("who x"))


class TestWc(unittest.TestCase):
    """Тесты wc."""

    def setUp(self):
        """Эмулятор с VFS из нескольких файлов."""
        self.emu = make_emulator("several")

    def test_wc(self):
        """Строки, слова и байты."""
        self.assertEqual(self.emu.execute("wc data.csv"), "3 3 34 data.csv")
        self.assertEqual(self.emu.execute("wc -l data.csv"), "3 data.csv")

    def test_total(self):
        """Для нескольких файлов выводится total."""
        out = self.emu.execute("wc -l data.csv hello.sh")
        self.assertEqual(out.splitlines()[-1], "5 total")

    def test_errors(self):
        """Нет файла, папка, нет аргументов."""
        self.assertIn("не указан файл", self.emu.execute("wc"))
        self.assertIn("нет такого файла", self.emu.execute("wc nope"))
        self.assertIn("это папка", self.emu.execute("wc ."))


if __name__ == "__main__":
    unittest.main()
