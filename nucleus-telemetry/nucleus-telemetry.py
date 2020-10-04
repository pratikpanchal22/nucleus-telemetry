import requests
import threading
from datetime import datetime
#
from models.data import Models
from models.data import ModelType

def iterate():    
    print ("\nNew Iteration:", datetime.now())

    response = Models().fetch(ModelType.NODE_TO_QUERY)
    id = response[0][0]
    nodeIp = response[0][1]
    nodeId = response[0][2]

    lastRecord = Models().fetch(ModelType.LAST_NODE_TELEMETRY_RECORD, nodeId)

    apiIdToFetch = "Identity"
    if(lastRecord[0][3] == 'System statistics'):
        apiIdToFetch = "Identity"
    elif(lastRecord[0][3] == 'Identity'):
        apiIdToFetch = "System statistics"
    else:
        apiIdToFetch = "Identity"

    api = Models().fetch(ModelType.FETCH_ENDPOINT_FOR_API_ID, apiIdToFetch)
    api_id = api[0][0]
    ep = api[0][1]

    #request 
    url = 'http://'+nodeIp+ep
    print ("-> URL to GET: ", url)

    jsonResponse = '{}'
    http_status_code = -1
    status_str = "SUCCESS"

    try:
        td = requests.get(url, timeout=10)
        jsonResponse = td.text
        http_status_code = td.status_code

        print("-> Response HTTP status code:", http_status_code)

        if(http_status_code != 200):
            status_str = "FAIL"
            print("-> Response: ", jsonResponse)

        if(nodeId != td.json()['node']):
            status_str = "Mismatched NodeId"

    except requests.exceptions.Timeout as e:
        print("-> Exception: Timeout: ",e)
        status_str = str(e)
    except requests.exceptions.RequestsWarning as e:
        print("-> Exception: RequestsWarning: ",e)
        status_str = str(e)
    except requests.exceptions.RetryError as e:
        print("-> Exception: RetryError: ",e)
        status_str = str(e)
    except requests.exceptions.RequestException as e:
        print("-> Exception: RequestException: ",e)
        status_str = str(e)

    #Add telemetry data
    rowsAdded = Models().push(ModelType.TELEMETRY_DATA, 
                    nodeId,
                    api_id,
                    http_status_code,
                    jsonResponse,
                    status_str)
    print("-> Number of telemetry data-rows added successfully:", rowsAdded)

    if(rowsAdded != 1):
        print (" ERROR! Expected 1. Received:", rowsAdded)

    #Update node_list with ts
    rowsAdded = Models().push(ModelType.UPDATE_TIMESTAMP_FOR_ID, id)
    print("-> Timestamp updated for node", nodeId,"| Rows updated:",rowsAdded)

    if(rowsAdded != 1):
        print (" ERROR! Expected 1. Received:", rowsAdded)

    numberOfNodesToQuery = Models().fetch(ModelType.NUMBER_OF_ACTIVE_QUERIES)[0][0]
    nodeQueryPeriodicity = 120 #seconds - TODO: fetch from database
    secondsToPause = nodeQueryPeriodicity / numberOfNodesToQuery

    print("-> Next thread will run in ",secondsToPause, " seconds")

    nextThread = threading.Timer(secondsToPause, iterate)
    nextThread.start()

if __name__ == "__main__":
    iterate()
