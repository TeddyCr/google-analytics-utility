from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
from datetime import datetime, timedelta
import time

import os

def managementService():
        """
        v4 API currently does not support the `management()` method, hence, we need to define
        an new service object with the API version set to v3.
        The value used for this method need to be created through an environment variable
        
            Return:
                service: googleapiclient.discovery.Resource object, a Google API service object v3
        """
        scopes = os.environ.get('GA_API_SCOPES').split(',')
        name = 'analytics'
        version = 'v3'
        file_path = os.environ.get('GA_API_CREDS')

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            file_path, 
            scopes=scopes
        )

        management_service = build(name, version, credentials=credentials)

        return management_service


def reportService():
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


def iterResponsePages(service, payload, verbose, slow_down):
    """
    iter through the response pages and concat the data from different pages under one 
    'reports' key dictionnary.

        Args:
            service: googleapiclient.discovery.Resource, a Google API service object v4
            payload: dict, a dictionnary representation of a the payload to be passed with the request
            verbose: bool, True will display the starting row being fetch, while False will mute this behavior 
    """
    token = 0
    next_page = True
    data = {'reports': []}


    while next_page:
        if verbose:
            print(f'Fetching rows starting at position: {token}')
        if slow_down > 0:
            time.sleep(slow_down)
            
        data_tmp = service.reports().batchGet(body=payload).execute()
        token = data_tmp.get('reports')[0].get('nextPageToken')

        if token != None:
            payload.get('reportRequests')[0].update({'pageToken': token})
        else:
            next_page = False
            payload.get('reportRequests')[0].update({'pageToken': '0'})

        for report in data_tmp.get('reports'):
            data.get('reports').append(report)

    return data
        

def formatDates(start_date, end_date):
    """
    Iterate over the date range provided to create a list of single days

        Args:
            start_date: str, a string representation of the start date for the desired date range
            end_date: str, a string representation of the end date for the desired date range
        Return:
            dates: list, strings representing each single days for the date range chosen
    """
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    dates = [(end_date - timedelta(days=d)).strftime('%Y-%m-%d') for d in range((end_date - start_date).days + 1)]

    return dates


