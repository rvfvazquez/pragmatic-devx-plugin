import unittest
from src.counter import increment


class CounterTests(unittest.TestCase):
    def test_ac_1_increments(self):
        self.assertEqual(increment(1), 2)
