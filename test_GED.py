import unittest
import Read_Process_GED as GEDcode


class TestGED (unittest.TestCase):

    def test_uniqueIds(self):
        self.assertTrue(GEDcode.isIDUnique(5, [1, 2]))
        self.assertFalse(GEDcode.isIDUnique(5, [5, 2]))
        self.assertTrue(GEDcode.isIDUnique(5, ["@I1", 2]))
        self.assertTrue(GEDcode.isIDUnique(5, [1, "-5"]))
        self.assertFalse(GEDcode.isIDUnique("@I7@", ["@I11", "@I7@"]))


if __name__ == "__main__":
    unittest.main()
