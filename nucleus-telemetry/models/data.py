from enum import Enum
import mysql.connector
from mysql.connector import Error
#
from models import dbConfig as dbc
#from common.utility import logger

#################### App Models #######################
#MODEL TYPES
class ModelType(Enum):
    UNINITIALIZED_MODEL_TYPE = 0
    #Fetch
    SELECT_DATABASE = 1
    NODE_TO_QUERY = 2
    FETCH_ENDPOINT_FOR_API_ID = 3
    NUMBER_OF_ACTIVE_QUERIES = 4
    LAST_NODE_TELEMETRY_RECORD = 5
    #Push
    TELEMETRY_DATA = 101
    UPDATE_TIMESTAMP_FOR_ID = 102
    
class Models:
    def __init__(self):
        self.sqlParameterTuple = ()
        try:
            self.dbConnection = mysql.connector.connect(host=dbc.MYSQL_HOST, database=dbc.MYSQL_DB, user=dbc.MYSQL_USER, password=dbc.MYSQL_PASSWORD)
            if(self.dbConnection.is_connected()):
                self.modelType = ModelType.UNINITIALIZED_MODEL_TYPE
                self.query = ""
            else:
                print("Error: Unable to establish database connection")
        except Error as e:
            print ("Exception:", e)

    def wrapUp(self):
        if(self.dbConnection.is_connected()):
            self.dbConnection.close()
        
    def fetch(self, modelType, *argv):
        self.modelType = modelType
        
        if(self.modelType == ModelType.SELECT_DATABASE):
            self.query = ("select database();")

        elif(self.modelType == ModelType.NODE_TO_QUERY):
            self.query = ("SELECT "+dbc.KEY_ID+", inet_ntoa("+dbc.KEY_IP+"), "+dbc.KEY_NODE_ID+", "
                                +dbc.KEY_TS_LAST_UPDATED+", "+dbc.KEY_STATUS
                              +" FROM "+dbc.TABLE_NODE_LIST+ " WHERE "
                              +dbc.KEY_STATUS+" != 'INACTIVE' " 
                              +" ORDER BY " +dbc.KEY_TS_LAST_UPDATED+ " ASC LIMIT 1;")
        
        elif(self.modelType == ModelType.FETCH_ENDPOINT_FOR_API_ID):
            try: 
                apiId = argv[0]
            except:
                print("ERROR: Expected apiId")
                self.wrapUp()
                return

            self.query = ("SELECT "+dbc.KEY_API_ID+", "+dbc.KEY_ENDPOINT+" "
                              +" FROM "+dbc.TABLE_NODE_API_LIST
                              +" WHERE "+dbc.KEY_API_ID+" = '"+apiId+"';")

        elif(self.modelType == ModelType.NUMBER_OF_ACTIVE_QUERIES):
            self.query = ("select count(*) from node_list where status != 'INACTIVE';")

        elif(self.modelType == ModelType.LAST_NODE_TELEMETRY_RECORD):
            try: 
                nodeId = argv[0]
            except:
                print("ERROR: Expected nodeId")
                self.wrapUp()
                return

            self.query = ("select * from node_telemetry "
			            +" where nodeId = " + str(nodeId)
                        +" order by ts_created desc limit 1;")

        else:
            print("ERROR: Unsupported model type for method:fetch : ",str(self.modelType))
            return
        
        if(self.query == ""):
            print("Error! Empty query / unsupported ModelType")
            return
        
        #logger("_INFO_", "Query: ", self.query)
        
        r = []

        try:
            cursor = self.dbConnection.cursor()
            cursor.execute(self.query)
            r = list(cursor.fetchall())
        except mysql.connector.Error as e:
            print ("MySQL query failed. Exception: ",e)
            print ("Query: ", self.query)
        finally:
            cursor.close()
            self.wrapUp()
        
        return r

    def push(self, modelType, *argv):
        self.modelType = modelType

        if(self.modelType == ModelType.TELEMETRY_DATA):
            try:
                nodeId = argv[0]
            except:
                print("ERROR: Expected nodeId")
                self.wrapUp()
                return

            try:
                api_id = argv[1]
            except:
                print("ERROR: Expected api_id")
                self.wrapUp()
                return

            try:
                status_code = argv[2]
            except:
                print("ERROR: Expected status_code")
                self.wrapUp()
                return

            try:
                response = argv[3]
            except:
                print("ERROR: Expected response")
                self.wrapUp()
                return

            try:
                status = argv[4]
            except:
                print("ERROR: Expected status")
                self.wrapUp()
                return

            self.sqlParameterTuple = (str(nodeId), api_id, str(status_code), response, status)

            """
            self.query = ("INSERT INTO " + dbc.TABLE_NODE_TELEMETRY + " (" + dbc.KEY_NODE_ID+", "
                            + dbc.KEY_API_ID+", "
                            + dbc.KEY_STATUS_CODE+", "
                            + dbc.KEY_RESPONSE+", "
                            + dbc.KEY_STATUS
                            + ") VALUES (" 
                            + str(nodeId) + ", "
                            + "'" + api_id + "', "
                            + str(status_code) + ", "
                            + "'" + response + "', "
                            + "'" + status + "'"
                            + ");")
            """
            self.query = ("INSERT INTO " + dbc.TABLE_NODE_TELEMETRY + " (" + dbc.KEY_NODE_ID+", "
                            + dbc.KEY_API_ID+", "
                            + dbc.KEY_STATUS_CODE+", "
                            + dbc.KEY_RESPONSE+", "
                            + dbc.KEY_STATUS
                            + ") VALUES (%s, %s, %s, %s, %s);")

        elif(self.modelType == ModelType.UPDATE_TIMESTAMP_FOR_ID):
            try:
                id = argv[0]
            except:
                print("ERROR: Expected id")
                self.wrapUp()
                return

            self.sqlParameterTuple = (str(id),)                

            """
            self.query = ("UPDATE "+dbc.TABLE_NODE_LIST+" SET "+dbc.KEY_STATUS+" = 'ACTIVE', "+dbc.KEY_TS_LAST_UPDATED+"=NOW() WHERE "
                            +dbc.KEY_ID+" = "+str(id)+";")
            """
            self.query = ("UPDATE "+dbc.TABLE_NODE_LIST
                        +" SET "+dbc.KEY_STATUS+" = 'ACTIVE', "
                                +dbc.KEY_TS_LAST_UPDATED+"=NOW()"
                        +" WHERE "
                            +dbc.KEY_ID+" = %s;")
            #print(self.query)

        else:
            print("ERROR: Unsupported model type for method:push : ",str(self.modelType))
            return

        if(self.query == ""):
            print("Error! Empty query / unsupported ModelType")
            return

        rowsAffected = -1
        try:
            cursor = self.dbConnection.cursor()
            cursor.execute(self.query, self.sqlParameterTuple)
            self.dbConnection.commit()
            #print("Cursor.rowcount results: ", cursor.rowcount)
            rowsAffected = cursor.rowcount
        except mysql.connector.Error as e:
            print ("MySQL query failed. Exception: ",e)
            print ("Query: ", self.query)
        finally:
            cursor.close()
            self.wrapUp()
        
        return rowsAffected
