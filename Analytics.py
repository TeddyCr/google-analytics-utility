from __future__ import print_function

import argparse
import os

import httplib2

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
from _helpers import managementService, iterResponsePages


class GetGAData(object):

    def __init__(self, start_date, end_date):
        """
        Initialize the GetData() class

            Args:
                start_date: str, start date of the period the data are pulled for
                end_date: str, end date of the period the data are pulled for
        """
        self.start_date = start_date
        self.end_date = end_date


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

        service = build(api_name, api_version, credentials=credentials)

        return service


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
                                                                        ebPropertyId=property_id).execute().get('items')
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


    def getData(service, payload, batch=True, verbose=True,):
        """
        Fetch the data from the GA API

            Args:
                service: googleapiclient.discovery.Resource object, a service object returned by the initService() object
                payload: dict, payload to be passed with the service in the API call
                batch: bool, True if to fetch all the data within the data range at once or False to fetch
                       them day by day
                verbose: bool, display information regarding rows being fetched
        """
        if batch:
            if verbose:
                print(f'-----------\nfetching data between {self.start_date} and {self.end_date}')
            data = iterResponsePages()
            return data
        else:
            pass


    @classmethod
    def formatPayload(dimensions, metrics, view_id, operator=None, dimensions_filters=None, metrics_filters=None):
    """  
        Format the payload for the GA API
        Args:
            dimensions: list of GA dimension to be returned 
                        https://developers.google.com/analytics/devguides/reporting/core/dimsmets
            metrics: list of GA metrics to be returned https://developers.google.com/analytics/devguides/reporting/core/dimsmets
            view_id: the view id from which the data should be retrieve. Raise error if None
            operator: string the operator to be used to perform the filtering operation
                    'AND' or 'OR' default to None. If None, then perform an 'OR' operation
            dimensions_filter: list of tuple containing the logical operation to be performed for filtering. Each tuple
                                represents 1 logical operation and tuple value correspond to
                                    tuple[0] dimension name
                                    tuple[1] logical expression (True or False) to include or exclude
                                    tuple[2] dimension operator ('REGEXP' or 'EXACT')
                                    tuple[3] expression
            dmetrics_filter: list of tuple containing the logical operation to be performed for filtering. Each tuple
                             represents 1 logical operation and tuple value correspond to
                                    tuple[0] metric name
                                    tuple[1] metric operator ('REGEXP' or 'EXACT')
                                    tuple[2] expression
        Return:
            payload: dict, returns a dictionnary representation of the payload to be passed with the service object in the
                     API call            
    """
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
                'expressions': dim_filt[3]
            })
            
    if metrics_filters:
        for met_filt in metrics_filters:
            met_filters.append({
                "metricName": met_filt[0],
                "operator": met_filt[1],
                "comparisonValue": met_filt[2]
            })
            
            
    payload = {
        'reportRequests': [{
            'viewId': VIEW_ID,
            'dateRanges': [
                {
                    'startDate': f'{self.start_date}',
                    'endDate': f'{self.end_date}',
                }
            ],
            'dimensions': formated_dimensions,
            'metrics': formated_metrics,
            'pageToken': '0',
            'pageSize': 100000,
            "dimensionFilterClauses":  [{ 
                        "operator": operator,
                        "filters": dim_filters
            }],
            "metricFilterClauses":  [{ 
                        "operator": operator,
                        "filters": met_filters
            }],
        }]
    }
    
    return payload