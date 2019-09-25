from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

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
        name = os.environ.get('GA_API_NAME')
        version = 'v3'
        file_path = os.environ.get('GA_API_CREDS')

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            file_path, 
            scopes=scopes
        )

        management_service = build(api_name, api_version, credentials=credentials)

        return management_service

def iterResponsePages(service, payload, verbose):
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
        data_tmp = service.reports().batchGet(body=payload).execute()
        token = data.get('reports')[0].get('nextPageToken')

        if token != "None":
            payload.get('reportRequests')[0].update({'pageToken': token})
        else:
            next_page = False
            payload.get('reportRequests')[0].update({'pageToken': 0})

        for report in data_tmp.get('reports'):
            data.get('reports').append(report)

    return data
        



