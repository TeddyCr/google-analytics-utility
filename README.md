# Foreword
## google-analytic-utility in a Nutshell
google-analytic-utility is an abstraction module allowing you to interact with the Google Analytics API with a few line of codes. 

## Set Up
Before interacting with the package, you will have to set up some [environment variables](https://en.wikipedia.org/wiki/Environment_variable) as well as setting up your Google account to accept requests from the API.  
### Step 1 - Create a client ID
google-analytic-utility leverage Google Service API. You will have to create a service account and get the credentials linked to this account.
1) Open the [Service accounts page](https://console.developers.google.com/iam-admin/serviceaccounts). If prompted, select a project.  
2) Click add Create Service Account, enter a name and description for the service account. You can use the default service account ID, or choose a different, unique one. When done click Creaunique one. When done click Create.  
3) The Service account permissions (optional) section that follows is not required. Click Continue.  
4) On the Grant users access to this service account screen, scroll down to the Create key section. Click add Create key.  
5) In the side panel that appears, select the format for your key: JSON is recommended.  
6) Click Create. Your new public/private key pair is generated and downloaded to your machine; it serves as the only copy of this key. For information on how to store it securely, see [Managing service account keys](https://cloud.google.com/iam/docs/understanding-service-accounts#managing_service_account_keys).  
7) Click Close on the Private key saved to your computer dialog, then click Done to return to the table of your service accounts.  

### Step 2 - Add Service Account to Google Analytics Acccount
The newly created service account will have an email address, `<projectId>-<uniqueId>@developer.gserviceaccount.com`; Use this email address to add a user to the Google analytics account you want to access via the API. 

### Step 3 - Create environment variables
Depending on the OS you are using the method to create environment variables will change. 
* For Mac user follow [these instructions](https://stackoverflow.com/questions/7501678/set-environment-variables-on-mac-os-x-lion)  
* For Windows user follow [these instructions](https://superuser.com/questions/949560/how-do-i-set-system-environment-variables-in-windows-10)

You will need to create 4 environment variables (5 if you wish to run the tests):
1) GA_API_CREDS: this is the full path to your `.json` credentials file  
2) GA_API_NAME: this should be set to `analyticsreporting`  
3) GA_API_SCOPES: this is the scope of the API. Only `https://www.googleapis.com/auth/analytics.readonly` is currently supported  
4) GA_API_VERSION: this should be set to `v4`  
5) GA_TEST_VIEWID (Optional): if you wish to run the test suit you will have to explicitly pass a GA view ID to run the test  

### Step 4 - Install dependencies
google-analytic-utility leverage a few python packages. To ensure you are able to fully run this package you should run `pip install -r requirements.txt`


# Getting Started
## Quick Start
### Initiating a service object
The first thing you will need to do before making a call to the API is initiating a service object by running.  
```
from Analytics import GetGAData, Management
service = Management().initService()
```

### Instanciate a GetGAData Class
Once you have your service created, you will need to instanciate a `GetGAData` object. This object will be use to 1) structure your payload, more information below, and make your request. 
You will need to pass the start date and the end date of the range you are trying to get data for.  
```
from Analytics import GetGAData, Management
....
analytics = GetGAData('2019-09-01', '2019-09-02')
```

### Structure the payload to be passed with the request
With your `GetGAData()` class object instanciated you can now structure the payload by using `formatPayload()` method. At minimum, you will need to pass 1) a list of GA API dimensions, 2) a list of GA API metrics, and 3) a view ID of tyope string.  
```
from Analytics import GetGAData, Management
....
payload = analytics.formatPayload(['ga:deviceCategory', 'ga:browser'],
                                ['ga:sessions', 'ga:pageviews'],
                                view_id='111111111')
```

### Get the reporting data
Once you have your service object and your payload you can use the `getData()` method to get the reporting data. Note that at this point the returned data will be raw. You will need to use the `dataToFrame()` method of the `Management()` class to get your data into a `pd.DataFrame`.  
You can pass `bash=False` (default to `True`) to send one request per day in your date range. This can be useful if you query a large date range as your data may be sample if you leave the default `bash` option.  
```
from Analytics import GetGAData, Management
....
data = analytics.getData(service, payload)
```

### Format the Data to a DataFrame
With your raw data you can use the `dataToFrame()` method of the `Management()` class to aggregate and structure your data into a usable format. From there, all `pandas` methods will be available for your GA data.  
```
from Analytics import GetGAData, Management
....
df = Management.dataToFrame(data)
```
