import unittest
import analyze_logs


class AnalyzeLog(unittest.TestCase):

    def setUp(self):
        self.logcheck = analyze_logs.Logcheck("..\\..\\Logfiles\\access*.log*", "..\\..\\db.mmdb")

    def test_logs_to_array(self):
        test_obj = self.logcheck.logs_to_array()
        self.assertEqual(type(test_obj), list)
        self.assertEqual(type(test_obj[0]), str)
        self.assertTrue(len(test_obj) >= 1)

    def test_get_ip_date_n_location(self):
        self.logcheck.get_ip_date_n_location()
        self.assertEqual(type(self.logcheck.ips[0]), str)
        self.assertEqual(type(self.logcheck.countries[0]), str)
        self.assertEqual(type(self.logcheck.log_attributes), list)
        self.assertEqual(type(self.logcheck.log_attributes[1]), dict)


if __name__ == '__main__':
    unittest.main()
