import unittest
from pathlib import Path

from freezegun import freeze_time
from keboola.datadirtest import DataDirTester


class TestComponent(unittest.TestCase):
    @freeze_time("2010-10-10")
    def test_functional(self):
        functional_tests = DataDirTester(
            Path(__file__).parent.joinpath("functional"), Path(__file__).parent.parent.joinpath("src/component.py")
        )
        functional_tests.run()


if __name__ == "__main__":
    unittest.main()
