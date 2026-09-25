"""Тесты эмулятора.

Запуск из корня репозитория: PYTHONPATH=src python3 -m unittest discover tests
"""

import unittest

from shell import Emulator, ParseError, parse_line


class TestParser(unittest.TestCase):
    """Тесты парсера."""

    def test_simple(self):
        """Обычные аргументы через пробел."""
        self.assertEqual(parse_line("ls -l  /tmp"), ["ls", "-l", "/tmp"])

    def test_empty(self):
        """Пустая строка."""
        self.assertEqual(parse_line("   "), [])

    def test_quotes(self):
        """Аргументы в кавычках."""
        self.assertEqual(parse_line('cd "my dir"'), ["cd", "my dir"])
        self.assertEqual(parse_line("ls 'a b' c"), ["ls", "a b", "c"])

    def test_empty_quotes(self):
        """Пустые кавычки дают пустой аргумент."""
        self.assertEqual(parse_line('ls ""'), ["ls", ""])

    def test_unclosed_quote(self):
        """Незакрытая кавычка - ошибка."""
        with self.assertRaises(ParseError):
            parse_line('ls "abc')


class TestEmulator(unittest.TestCase):
    """Тесты команд."""

    def setUp(self):
        """Создаем эмулятор перед каждым тестом."""
        self.emu = Emulator()

    def test_prompt(self):
        """Приглашение содержит пользователя и хост."""
        prompt = self.emu.get_prompt()
        self.assertTrue(prompt.startswith(self.emu.user + "@"))
        self.assertTrue(prompt.endswith(":~$ "))

    def test_stubs(self):
        """Заглушки выводят имя и аргументы."""
        self.assertIn("ls", self.emu.execute("ls -a"))
        self.assertIn("'my dir'", self.emu.execute('cd "my dir"'))

    def test_errors(self):
        """Неизвестная команда и неверные аргументы."""
        self.assertIn("неизвестная команда", self.emu.execute("abc"))
        self.assertIn("слишком много", self.emu.execute("cd a b"))
        self.assertIn("не закрыта", self.emu.execute('ls "x'))

    def test_exit(self):
        """exit останавливает цикл."""
        self.emu.execute("exit")
        self.assertFalse(self.emu.running)


if __name__ == "__main__":
    unittest.main()
