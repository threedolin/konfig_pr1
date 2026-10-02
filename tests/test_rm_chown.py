"""Тесты команд этапа 5: rm и chown.

Запуск из корня репозитория: PYTHONPATH=src python3 -m unittest discover tests
"""

import os
import unittest

from shell import Emulator
from vfs import find_node, load_vfs

VFS_DIR = os.path.join(os.path.dirname(__file__), "vfs")


def make_emulator():
    """Создает эмулятор с глубокой тестовой VFS."""
    emu = Emulator()
    emu.vfs = load_vfs(os.path.join(VFS_DIR, "deep"))
    return emu


class TestRm(unittest.TestCase):
    """Тесты rm."""

    def setUp(self):
        """Эмулятор с VFS deep."""
        self.emu = make_emulator()

    def test_remove_file(self):
        """Файл удаляется из памяти, но не с диска."""
        self.assertEqual(self.emu.execute("rm etc/passwd"), "")
        self.assertEqual(self.emu.execute("ls etc"), "hostname")
        disk_file = os.path.join(VFS_DIR, "deep", "etc", "passwd")
        self.assertTrue(os.path.exists(disk_file))

    def test_remove_dir(self):
        """Папка удаляется только с -r."""
        self.assertIn("нужен флаг -r", self.emu.execute("rm var"))
        self.emu.execute("rm -r var")
        self.assertEqual(self.emu.execute("ls"), "etc  home")

    def test_force(self):
        """-f не ругается на несуществующий файл."""
        self.assertIn("нет такого файла", self.emu.execute("rm nope"))
        self.assertEqual(self.emu.execute("rm -f nope"), "")
        self.assertEqual(self.emu.execute("rm -f"), "")

    def test_forbidden(self):
        """Нельзя удалить корень, . и ..; нужен аргумент."""
        self.assertIn("корень", self.emu.execute("rm -r ~"))
        self.assertIn("'.' или '..'", self.emu.execute("rm -r ."))
        self.assertIn("не указан файл", self.emu.execute("rm"))

    def test_remove_current_dir(self):
        """Если удалена текущая папка, переходим выше."""
        self.emu.execute("cd home/user/docs")
        self.emu.execute("rm -r /home/user")
        self.assertEqual(self.emu.cwd, ["home"])


class TestChown(unittest.TestCase):
    """Тесты chown (пользователи root и daemon есть в любом Linux)."""

    def setUp(self):
        """Эмулятор с VFS deep."""
        self.emu = make_emulator()

    def node(self, *parts):
        """Элемент VFS по списку имен."""
        return find_node(self.emu.vfs, list(parts))

    def test_owner_and_group(self):
        """Смена владельца и группы."""
        self.emu.execute("chown root:daemon etc/passwd")
        node = self.node("etc", "passwd")
        self.assertEqual((node["owner"], node["group"]), ("root", "daemon"))
        self.assertIn("root     daemon", self.emu.execute("ls -l etc"))

    def test_group_only(self):
        """chown :группа меняет только группу."""
        owner = self.node("etc")["owner"]
        self.emu.execute("chown :root etc")
        self.assertEqual(self.node("etc")["owner"], owner)
        self.assertEqual(self.node("etc")["group"], "root")

    def test_recursive(self):
        """-R меняет владельца у всего содержимого папки."""
        self.emu.execute("chown -R root home")
        report = self.node("home", "user", "docs", "report.txt")
        self.assertEqual(report["owner"], "root")
        self.assertNotEqual(self.node("etc")["owner"], "root")

    def test_errors(self):
        """Ошибки chown."""
        self.assertIn("нужно указать", self.emu.execute("chown root"))
        self.assertIn("неизвестный пользователь",
                      self.emu.execute("chown no_user_xyz etc"))
        self.assertIn("неизвестная группа",
                      self.emu.execute("chown :no_group_xyz etc"))
        self.assertIn("нет такого файла", self.emu.execute("chown root x"))
        self.assertIn("неверный флаг", self.emu.execute("chown -x root etc"))


if __name__ == "__main__":
    unittest.main()
