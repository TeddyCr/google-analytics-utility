import unittest
import sys
import os
import apiclient
import Analytics


class testAnalyticsAPI(unittest.TestCase):
    """
    Main class to test the Analytics API of the google-utility modeul
    """

    def setUp(self):
        """
        Creates a service. This will be call each time a TestCase will be called
        """
        analytics = Analytics.GetGAData('2019-09-20', '2019-09-24')
        self.service = analytics.initService()

    def testServiceObject(self):
        self.assertTrue(isinstance(self.service, apiclient.discovery.Resource))


if __name__ == '__main__':
    unittest.main(verbosity=2)
