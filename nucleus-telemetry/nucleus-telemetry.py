import requests
#
from models.data import Models
from models.data import ModelType

def iterate():
    """try:
        conn = mysql.connector.connect(host='localhost', database='appDbSandbox', user='user', password='password')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchall()
            print("You're connected to - ", record)

        r=requests.get('http://192.168.1.83/get/sysstat')
        print(r.status_code)
        print(r.text)
    except Error as e:
        print ("Print your error msg", e)
    finally:
        if(conn.is_connected()):
            cursor.close()
            conn.close()"""

    response = Models().fetch(ModelType.NODE_TO_QUERY)
    id = response[0][0]
    nodeIp = response[0][1]
    print ("REsponse type: ", type(response))
    print ("Response: ", response)
    print ("nodeIp: ", nodeIp)

    api = Models().fetch(ModelType.SYSTEM_STAT_ENDPOINT)
    api_id = api[0][0]
    ep = api[0][1]
    print("sysstat ep: ", ep)

    #request 
    url = 'http://'+nodeIp+ep
    print (url)
    td = requests.get(url)
    print(td.status_code)
    print(td.text)

    status_str = "FAIL"
    if(td.status_code == 200):
        status_str = "SUCCESS"
    
    jsonResponse = td.json()
    print(jsonResponse['ip'])
    print(jsonResponse['node'])

    Models().push(ModelType.TELEMETRY_DATA, 
                    jsonResponse['node'],
                    api_id,
                    td.status_code,
                    td.text,
                    status_str)

    #Update node_list with ts
    Models().push(ModelType.UPDATE_TIMESTAMP_FOR_ID, id)

if __name__ == "__main__":
    iterate()
