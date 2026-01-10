import unittest

class AITest(unittest.TestCase):
    def test_response(self):
        self.assertEqual(get_response({}, "test"), "Default")

if __name__ == "__main__":
    unittest.main()