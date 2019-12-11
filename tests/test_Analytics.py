import unittest
import sys
import os
import apiclient
import pandas as pd

from googleAnalyticUtility.Analytics import GetGAData, Management


class testAnalyticsAPI(unittest.TestCase):
    """
    Main class to test the Analytics API of the google-utility modeul
    """

    def setUp(self):
        """
            self.analytics: googleAnalyticUtility.Analytics.GetGAData object representing the insitiation of the class
            self.account_details: dict, a dictionnary representing accounts details
        """
        self.analytics = GetGAData('2019-09-20', '2019-09-24')
        self.account_details = Management().getAccountDetails()


    def testServiceObject(self):
        """
        """
        self.assertIsInstance(self.analytics.report_service, apiclient.discovery.Resource)


    def testAccountDetailsResponse(self):
        """
        """
        l = len(self.account_details.get('accounts'))
        self.assertGreater(l, 0)
    

    def testAccountDetailsType(self):
        """
        """
        self.assertIsInstance(self.account_details, dict)


    def testAccountDetailsStructure(self):
        """
        """
        t0 = self.account_details.get('accounts')
        t1 = self.account_details.get('accounts')[0].get('account_properties')
        t2 = self.account_details.get('accounts')[0].get('account_properties')[0].get('property_views')

        for t in [t0, t1, t2]:
            with self.subTest():
                self.assertIsNotNone(t)   


    def testPayloadClauseOperators(self):
        """
        """
        clause_operators = ['OR', 'AND']

        for op in clause_operators:
            payload = self.analytics.formatPayload(['ga:deviceCategory', 'ga:browser'],
                                ['ga:sessions', 'ga:pageviews'],
                                view_id=os.environ.get('GA_API_TEST_VIEWID'),
                                dimension_operator=op,
                                dimensions_filters=[('ga:deviceCategory', False, 'EXACT', 'mobile', False),
                                                    ('ga:browser', False, 'EXACT', 'Safari', True)],
                                metric_operator=op,
                                metrics_filters=[('ga:sessions', False, 'GREATER_THAN', '1')])
            
            l = len(self.analytics.getData(payload)[0].get('reports'))
            self.assertGreater(l, 0)

    
    def testPayloadDimensionOperators(self):
        """
        """
        dimension_operators = ['EXACT', 'REGEXP']

        for op in dimension_operators:
            payload = self.analytics.formatPayload(['ga:deviceCategory', 'ga:browser'],
                                ['ga:sessions', 'ga:pageviews'],
                                view_id=os.environ.get('GA_API_TEST_VIEWID'),
                                dimensions_filters=[('ga:deviceCategory', False, op, 'mobile', False),
                                                    ('ga:browser', False, 'EXACT', 'Safari', True)],
                                metrics_filters=[('ga:sessions', False, 'GREATER_THAN', '1')])
            
            l = len(self.analytics.getData(payload)[0].get('reports'))
            self.assertGreater(l, 0)


    def testPayloadMetricOperators(self):
        """
        """
        metric_operators = ['GREATER_THAN', 'LESS_THAN', 'EQUAL', 'IS_MISSING']

        for op in metric_operators:
            payload = self.analytics.formatPayload(['ga:deviceCategory', 'ga:browser'],
                                ['ga:sessions', 'ga:pageviews'],
                                view_id=os.environ.get('GA_API_TEST_VIEWID'),
                                dimensions_filters=[('ga:deviceCategory', False, 'EXACT', 'mobile', False),
                                                    ('ga:browser', False, 'EXACT', 'Safari', True)],
                                metrics_filters=[('ga:sessions', False, op, '1')])
            
            l = len(self.analytics.getData(payload)[0].get('reports'))
            self.assertGreater(l, 0)


    def testPayloadNots(self):
        """
        """
        nots = [True, False]

        for n in nots:
            payload = self.analytics.formatPayload(['ga:deviceCategory', 'ga:browser'],
                                ['ga:sessions', 'ga:pageviews'],
                                view_id=os.environ.get('GA_API_TEST_VIEWID'),
                                dimensions_filters=[('ga:deviceCategory', n, 'EXACT', 'mobile', False),
                                                    ('ga:browser', n, 'EXACT', 'Safari', True)],
                                metrics_filters=[('ga:sessions', n, 'LESS_THAN', '1')])
            
            l = len(self.analytics.getData(payload)[0].get('reports'))
            self.assertGreater(l, 0)


    def testDataFormatting(self):
        payload = self.analytics.formatPayload(['ga:date','ga:deviceCategory', 'ga:browser'],
                                          ['ga:sessions', 'ga:pageviews'], view_id=os.environ.get('GA_API_TEST_VIEWID'),
                                          dimensions_filters=[('ga:deviceCategory', False, 'EXACT', 'mobile', False)],
                                          metrics_filters=[('ga:sessions', False, 'GREATER_THAN', '1')])
        data = self.analytics.getData(payload, batch=True)
        df = Management.dataToFrame(data)
        self.assertIsInstance(df, pd.DataFrame)


if __name__ == '__main__':
    unittest.main()
