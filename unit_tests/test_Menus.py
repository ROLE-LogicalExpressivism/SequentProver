import io
import contextlib
import os
import unittest
from unittest.mock import patch

from Controllers.Menus.Base import Menu, Option


current_dir = os.path.dirname(__file__)


class TestMenus(unittest.TestCase):
    def setUp(self):
        self.menu = Menu()

    def capture_menu_output(self, inputs):
        with patch("builtins.input", side_effect=inputs):
            with patch("Controllers.Menus.Base.Menu._show_options",
                       new=lambda *args: print("")):
                with patch("sys.stdout", new_callable=io.StringIO) as captured_out:
                    self.menu._separator = ""
                    self.menu.open()
                    return captured_out.getvalue().strip()

    def test_menu_starts_with_quit_item(self):
        self.assertEqual("Exit", self.menu.options[0].label)

    def test_menu_options(self):
        test_options = [
            Option("wow", lambda *args: print("much wow")),
        ]
        self.menu.extend(test_options)
        output = self.capture_menu_output(inputs=[1, 0])
        self.assertEqual("much wow", output)

    def test_basic_lambda_from_file(self):
        mock_file = os.path.join(current_dir, "mocks", "Menus", "TestMenu.json")
        self.menu.load(mock_file)
        output = self.capture_menu_output(inputs=[1, 0])
        self.assertEqual("Lady", output)


if __name__ == '__main__':
    unittest.main()