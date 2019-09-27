from __future__ import print_function
import argparse
import os
import pandas as pd
import httplib2
import time

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
from googleAnalyticUtility._helpers import managementService, iterResponsePages, formatDates


class Management(object):
    """
    Management class has a set of static methods aims at completing administrative operations, examples:
        - connect to GA service
        - get GA account information
        - format ga returned data to a dataframe
    """

    @staticmethod
    def initService():
        """
        The value used for this method need to be created through an environment variable

            Return:
                service: googleapiclient.discovery.Resource object, a Google API service object
        """
        scopes = os.environ.get('GA_API_SCOPES').split(',')
        name = os.environ.get('GA_API_NAME')
        version = os.environ.get('GA_API_VERSION')
        file_path = os.environ.get('GA_API_CREDS')

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            file_path, 
            scopes=scopes
        )

        service = build(name, version, credentials=credentials)

        return service

    
    @staticmethod
    def getAccountDetails():
        """
        Fetch all the viewId linked to an account. This function uses a v3 service created for the
        helper.py file.

            Return:
                accounts_data: dict, represents the account, property, and view data (id and name)
        """
        management_service = managementService()

        accounts_data = {'accounts': list()}
        
        accounts = management_service.management().accounts().list().execute().get('items')
        for accounti in accounts:
            account_id = accounti.get('id')
            account_name = accounti.get('name')
            account_properties = list()

            properties = management_service.management().webproperties().list(accountId=account_id).execute().get('items')
            for propertyi in properties:
                property_id = propertyi.get('id')
                property_name = propertyi.get('name')
                property_views = list()

                views = management_service.management().profiles().list(accountId=account_id, 
                                                                        webPropertyId=property_id).execute().get('items')
                for viewi in views:
                    view_id = viewi.get('id')
                    view_name = viewi.get('name')
                    property_views.append({'view_name': view_name,
                                            'view_id': view_id})
                
                account_properties.append({'property_name': property_name,
                                            'property_id': property_id,
                                            'property_views': property_views})
            
            accounts_data.get('accounts').append({'account_name': account_name,
                                        'account_id': account_id,
                                        'account_properties': account_properties}
                                        )
        
        return accounts_data


    @staticmethod
    def dataToFrame(data):
        """
        format the raw data from the API response into a pandas dataframe

            Args:
                data: list, list of dictionnary containing the reporting data
            Return:
                df: pandas.DataFrame, a dataframe object contaning the formated reporting data
        """
        dfs = list()

        for datum in data:
            for report in datum.get('reports'):
                columnHeader = report.get('columnHeader')
                dimensionHeader = columnHeader.get('dimensions')
                metricHeaders = columnHeader.get('metricHeader')
                metricHeaderEntries = metricHeaders.get('metricHeaderEntries')
                metricHeader = list()

                for mHeader in metricHeaderEntries:
                    metricHeader.append(mHeader.get('name'))

                headers = dimensionHeader + metricHeader

                dims = [[] for _ in range(len(dimensionHeader))]
                mets= [[] for _ in range(len(metricHeaderEntries))]
                rows = report.get('data').get('rows')

                for row in rows:
                    dimensions = row.get('dimensions')
                    metrics = row.get('metrics')

                    for i, dimension in enumerate(dimensions):
                        dims[i].append(dimension)

                    for metric in metrics:
                        values = metric.get('values')
                        for i, value in enumerate(values):
                            mets[i].append(value)

                dims_mets = dims + mets
                
                df_tmp = dict()
                for i, header in enumerate(headers):
                    df_tmp[header] = dims_mets[i]

                dfs.append(pd.DataFrame(df_tmp))

        df = pd.concat(dfs)
        return df


class GetGAData(object):
    """
    The GetGAData class has a suite of methods that handles operations around fetching GA data
    for a specified date range
    """

    def __init__(self, start_date=None, end_date=None):
        """
        Initialize the GetData() class

            Args:
                start_date: str, start date of the period the data are pulled for
                end_date: str, end date of the period the data are pulled for
        """
        self.start_date = start_date
        self.end_date = end_date


    def getData(self, service, payload, batch=True, verbose=True,):
        """
        Fetch the data from the GA API

            Args:
                service: googleapiclient.discovery.Resource object, a service object returned by the initService() object
                payload: dict, payload to be passed with the service in the API call
                batch: bool, True if to fetch all the data within the data range at once or False to fetch
                       them day by day
                verbose: bool, display information regarding rows being fetched
            Return:
                data: list, contains the report data for the specified request. If batch=False, len(data) = 1 otherwise
                      len(data) = n when n is the number of days in the date range.

        """
        data = list()
        if batch:
            if verbose:
                print(f'-----------\nfetching data between {self.start_date} and {self.end_date}')
            data.append(iterResponsePages(service, payload, verbose))
            return data
        else:
            dates = formatDates(self.start_date, self.end_date)
            self.days_ = len(dates)
            for date in dates:
                if verbose:
                    print(f'-----------\nfetching data between {date} and {date}')
                payload.get('reportRequests')[0].get('dateRanges')[0].update({'startDate': date})
                payload.get('reportRequests')[0].get('dateRanges')[0].update({'endDate': date})
                data.append(iterResponsePages(service, payload, verbose))
            return data        


    def formatPayload(self, dimensions, metrics, view_id=None, dimension_operator=None, dimensions_filters=None, 
                        metric_operator=None, metrics_filters=None):
        """  
            Format the payload for the GA API
            Args:
                dimensions: list of GA dimension to be returned 
                            https://developers.google.com/analytics/devguides/reporting/core/dimsmets
                metrics: list of GA metrics to be returned https://developers.google.com/analytics/devguides/reporting/core/dimsmets
                view_id: the view id from which the data should be retrieve. Raise error if None
                dimension_operator: string the dimension operator to be used to perform the filtering operation
                        'AND' or 'OR' default to None. If None, then perform an 'OR' operation
                dimensions_filter: list of tuple containing the logical operation to be performed for filtering. Each tuple
                                    represents 1 logical operation and tuple values correspond to
                                        tuple[0] dimension name
                                        tuple[1] logical expression (True or False) to include or exclude
                                        tuple[2] dimension operator ('REGEXP' or 'EXACT')
                                        tuple[3] expression
                                        tuple[4] case sensitive, specify if the matchs should be case sensitive
                metric_operator: string the metric operator to be used to perform the filtering operation
                        'AND' or 'OR' default to None. If None, then perform an 'OR' operation
                metrics_filter: list of tuple containing the logical operation to be performed for filtering. Each tuple
                                represents 1 logical operation and tuple values correspond to
                                        tuple[0] metric name
                                        tuple[1] logical expression (True or False) to include or exclude
                                        tuple[2] metric operator ('EQUAL', 'LESS_THAN', 'GREATER_THAN', 'IS_MISSING')
                                        tuple[3] expression
            Return:
                payload: dict, returns a dictionnary representation of the payload to be passed with the service object in the
                        API call            
        """
        if not view_id:
            raise ValueError("view_id cannot be None. You must pass a GA View ID")

        formated_dimensions = list()
        formated_metrics = list()
        
        for dimension in dimensions:
            formated_dimensions.append({'name':dimension})
            
        for metric in metrics:
            formated_metrics.append({'expression': metric})
        
        dim_filters = list()
        met_filters = list()
        
        if dimensions_filters:
            for dim_filt in dimensions_filters:
                dim_filters.append({
                    'dimensionName': dim_filt[0],
                    'not': dim_filt[1],
                    'operator': dim_filt[2],
                    'expressions': dim_filt[3],
                    'caseSensitive': dim_filt[4]
                })
                
        if metrics_filters:
            for met_filt in metrics_filters:
                met_filters.append({
                    "metricName": met_filt[0],
                    "not": met_filt[1],
                    "operator": met_filt[2],
                    "comparisonValue": met_filt[3]
                })
                
                
        payload = {
            'reportRequests': [{
                'viewId': view_id,
                'dateRanges': [
                    {
                        'startDate': self.start_date,
                        'endDate': self.end_date,
                    }
                ],
                'dimensions': formated_dimensions,
                'metrics': formated_metrics,
                'pageToken': '0',
                'pageSize': 100000,
                "dimensionFilterClauses":  [{ 
                            "operator": dimension_operator,
                            "filters": dim_filters
                }],
                "metricFilterClauses":  [{ 
                            "operator": metric_operator,
                            "filters": met_filters
                }],
            }]
        }
        
        return payload