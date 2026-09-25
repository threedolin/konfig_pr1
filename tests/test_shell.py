"""Тесты эмулятора.

Запуск из корня репозитория: PYTHONPATH=src python3 -m unittest discover tests
"""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

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


class TestScript(unittest.TestCase):
    """Тесты стартового скрипта."""

    def run_script(self, text):
        """Записывает скрипт во временный файл, запускает, возвращает вывод."""
        with tempfile.NamedTemporaryFile("w", suffix=".txt",
                                         delete=False) as f:
            f.write(text)
        self.addCleanup(os.remove, f.name)
        emu = Emulator(script_path=f.name)
        out = io.StringIO()
        with redirect_stdout(out):
            emu.run_script(f.name)
        return emu, out.getvalue()

    def test_input_and_output(self):
        """На экран выводится и команда, и результат."""
        emu, out = self.run_script("# комментарий\nls a\n")
        self.assertIn(emu.get_prompt() + "ls a", out)
        self.assertIn("ls, аргументы: ['a']", out)
        self.assertNotIn("комментарий", out)

    def test_skip_errors(self):
        """Строка с ошибкой пропускается, дальше выполнение идет."""
        _, out = self.run_script("abc\nls after\n")
        self.assertIn("строка 1 с ошибкой пропущена", out)
        self.assertIn("['after']", out)

    def test_exit_in_script(self):
        """exit в скрипте останавливает выполнение."""
        emu, out = self.run_script("exit\nls never\n")
        self.assertFalse(emu.running)
        self.assertNotIn("never", out)

    def test_missing_file(self):
        """Несуществующий скрипт - сообщение об ошибке."""
        out = io.StringIO()
        with redirect_stdout(out):
            Emulator().run_script("/no/such/file.txt")
        self.assertIn("не удалось открыть скрипт", out.getvalue())

    def test_params(self):
        """Параметры сохраняются и выводятся."""
        emu = Emulator(vfs_path="my_vfs", script_path="s.txt")
        out = io.StringIO()
        with redirect_stdout(out):
            emu.print_params()
        self.assertIn("vfs    = my_vfs", out.getvalue())
        self.assertIn("script = s.txt", out.getvalue())


if __name__ == "__main__":
    unittest.main()
