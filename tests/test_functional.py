from pathlib import Path

import unittest

from datadirtest import DataDirTester
from freezegun import freeze_time


class TestComponent(unittest.TestCase):
    @freeze_time("2010-10-10")
    def test_functional(self):
        functional_tests = DataDirTester(Path(__file__).parent.joinpath('functional'),
                                         Path(__file__).parent.parent.joinpath('src/component.py'))
        functional_tests.run()


if __name__ == "__main__":
    unittest.main()