from test import test_image_path_parser
import unittest

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromModule(test_image_path_parser)
    unittest.TextTestRunner(verbosity=2).run(suite)
