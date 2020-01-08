import os
import io
import sys  
import json
import time
import pycurl
import logging
import certifi
import smtplib
import traceback
import xlsxwriter
import requests
import datetime
from constant import *
sys.path.append("")

class tenantInfo:
   def __init__(self):
     self.tenant_url = ""
     self.tenant_get_token = ""
     self.tenant_post_token = ""
     self.name = ""

json_data = {}
json_data["series"] = []
json_data["type"]="USQL data"
#property_var = {}
#property_var['Property']="USQL data sent back through API"
#json_data["properties"]=property_var
#------------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to make API call using the token defined in constant.py
# Returns the json object returned using the API call 
#------------------------------------------------------------------------------
def dtApiQuery(logger, endpoint, tenant_info, URL=""):
  try: 
    logger.info("In dtApiQuery")
    logger.debug ("dtApiQuery: endpoint = %s", endpoint)
    buffer = io.BytesIO()

    if URL == "":
      URL = tenant_info.tenant_url + USQL_QUERY
   
    #print "\n\n\n" + URL 
    endpoint = endpoint.replace(" ", "%20")
    endpoint = endpoint.replace("=", "%3D")
    endpoint = endpoint.replace("\"", "%22")

    endpoint = URL + "query=" + endpoint + "&explain=false" 
    #print "\n\n\n NEXT"
    #print endpoint
    get_param = {'Accept':'application/json; charset=utf-8', 'Authorization':'Api-Token {}'.format(tenant_info.tenant_get_token)}
    config_post = requests.get(endpoint, headers = get_param, verify = False)
    #print "\n\n\n VALUE"
    print config_post.text
    #c = pycurl.Curl()
    ##print str(URL) + "query=" + str(endpoint) + "&explain=false"
    #c.setopt(c.URL, URL + "query=" + str(endpoint) + "&explain=false")
    #c.setopt(pycurl.CAINFO, certifi.where())
    #c.setopt(c.HTTPHEADER, ['Authorization: Api-Token ' + tenant_info.tenant_get_token] )
    #c.setopt(pycurl.WRITEFUNCTION, buffer.write)
    #c.perform()
    #c.close()
    logger.info("Execution sucessfull: dtApiQuery")

  except Exception,e:
    traceback.print_exc()
    logger.error("Received exception while running dtApiQuery", str(e), exc_info = True) 

  finally:
    #return(buffer.getvalue().decode('UTF-8'))
    return(config_post.text)
#------------------------------------------------------------------------
# Author: Nikhil Goenka
# filename: the config file which the user would configure
#------------------------------------------------------------------------
def parse_config(filename):
  try:
    stream = open(filename)
    data = json.load(stream)
  except Exception:
    traceback.print_exc()
    print "Exception encountered in parse_config function : %s ", str(e)
  finally:
    return data

#------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to call API and populate the excel file
#------------------------------------------------------------------------
def populate_tenant_details(logger, tenant, tenant_info):
  try:
    logger.info("In populate_tenant_details")
    logger.info("In populate_tenant_details %s ", tenant)

    tenant_info.tenant_url = tenant['tenant-URL'] 
    tenant_info.tenant_get_token = tenant['API-GET-token']
    tenant_info.tenant_post_token = tenant['API-POST-token']
    tenant_info.name = tenant['tenant-name']
  except Exception, e:
    traceback_print.exc()
    print "Exception encountered while executing populate_tenant_details %s ", str(e)
  finally:
    return tenant_info 

#------------------------------------------------------------------------
# Author: Nikhil Goenka
#------------------------------------------------------------------------
def call_api(logger, tenant_info, use_case):
  try:
    
    logger.info("In call_api")
    query = use_case['api']
    logger.debug("call_api = %s", query)
    applicationIO = dtApiQuery(logger, query, tenant_info)
    applications = json.loads(applicationIO)

    epoch_time = time.mktime(datetime.datetime.now().timetuple()) * 1000
    #epoch_time= int(time.time())
    #epoch_time = int(round(time.time() * 1000))
    if applications != "":
     value = str(applications["values"])
     value = value.replace("]","")
     value = value.replace("[","")

     data_obj  = {}
     data_obj ['dataPoints'] = [[epoch_time,int(value)]]
     data_obj ["timeseriesId"] = use_case['timeseriesId']

     json_data["series"].append(data_obj)
     
     #data_obj = {"timeseriesId : {}, dataPoints : [ [ {},{}]]".format(use_case['timeseriesId'],str(epoch_time),str(value))}
     #data_obj = data_obj.replace("TIMESERIES_ID",use_case['timeseriesId'])
     #data_obj = data_obj.replace("TIMESTAMP", str(epoch_time))
     #data_obj = data_obj.replace("VALUE", str(value))

    logger.info("Successful execution: fetch_sync_application")
    
  except Exception,e:
    traceback.print_exc()
    logger.fatal("Received exception while running call_api", str(e), exc_info=True)

  finally:
    return json_data 

def createCustomDevice(logger, application, tenant_info, application_no):
  try:
    config_url = tenant_info.tenant_url + CREATE_CUSTOM_DEVICE + str(application_no)
    #config_url="https://stg99002.live.dynatrace.com/api/v1/entity/infrastructure/custom/idOfmyCustomDevice" + str(application_no) 
    post_param = {'Content-Type':'application/json; charset=utf-8', 'Authorization':'Api-Token {}'.format(tenant_info.tenant_post_token)}

    #print config_url
    #print post_param
    #create_custom_device_file = open("create_custom_device.json")
    #custom_device_details = json.load(create_custom_device_file)
   
    application_name = application["app-name"] 
    custom_device_details = {}
    custom_device_details['type'] = "USQL data"
    custom_device_details['properties'] = {}
    custom_device_details['displayName'] = application_name
    custom_device_details['properties']['Property']="USQL data sent back through API"

    config_post = requests.post(config_url, data = json.dumps(custom_device_details), headers = post_param)
    if config_post.status_code != 200:
      logging.error('postConfigs: failed to create customDevice for %s ', application_name)
    else:
       logging.info('SUCCESS postConfigs status code for {0} '.format(application_name))
    #logger.info("")
    #print config_post.text

  except Exception, e:
    traceback.print_exc()
    logger.fatal("Received exception while running createCustomDevice", str(e), exc_info=True)

  finally:
    return config_url

def send_data_custom_device(logger, restpoint, json_data):
  try:
    logger.debug("In send_data_custom_device")
    post_param = {'Content-Type':'application/json; charset=utf-8', 'Authorization':'Api-Token {}'.format(tenant_info.tenant_post_token)}

    config_post = requests.post(restpoint, data = json.dumps(json_data), headers = post_param)
    if config_post.status_code != 200:
      logging.error('postConfigs: failed to send data %s %s', config_post.text, json.dumps(json_data))
     
  except Exception, e:
    traceback.print_exc()
    logger.fatal("Received exception while running send_data_custom_device ", str(e), exc_info=True)
     
  finally:
    return 
#------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to call API and populate the excel file
#------------------------------------------------------------------------

if __name__ == "__main__":
  try:
    while (1):
      flag = 0 #Flag to initialize the timeseries id
      filename = "config.json"
      data = parse_config(filename)
      
      logging.basicConfig(filename=data['log_file'],
                              filemode='a',
                              format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                              datefmt='%H:%M:%S',
                              level=logging.DEBUG)
      logger = logging.getLogger()
      tenants = data['tenant-details']

      applications = data['application-name']
      for i in range(len(applications)):
        #create the custom device - can check in DB if the device is already present 
        use_cases = applications[i]['use-case']

        tenant_info = tenantInfo()
        tenant_info = populate_tenant_details(logger, data['tenant-details'], tenant_info)

        restpoint = createCustomDevice(logger, applications[i], tenant_info, i + 12)
        if flag == 0:
          for k in range(len(use_cases)):
            #timeSeriesURL = "https://stg99002.live.dynatrace.com/api/v1" + TIMESERIES_DEF
            timeSeriesURL = tenant_info.tenant_url + TIMESERIES_DEF
            metrics_name = use_cases[k]["timeseriesId"]
            metrics_name = metrics_name.replace(":","%3A")
            timeSeriesURL = timeSeriesURL + metrics_name
          
            timeseries_def = {}
            timeseries_def["displayName"] = use_cases[k]["displayname"]
            timeseries_def["types"]=[]
            timeseries_def["types"].append("USQL data")
            post_param = {'Content-Type':'application/json; charset=utf-8', 'Authorization':'Api-Token {}'.format(tenant_info.tenant_post_token)}
            config_post = requests.put(timeSeriesURL, data = json.dumps(timeseries_def), headers = post_param, verify = False)
            if config_post.status_code != 200:
              logging.error('postConfigs: failed to create timeseries for %s ', metrics_name)
            else:
               logging.info('SUCCESS postConfigs status code for {0} '.format(metrics_name))
            #print config_post.text + " " + use_cases[k]["timeseriesId"]
            flag = 1
      
        for j in range(len(use_cases)):
        #for j in range(1):
          json_data = call_api(logger, tenant_info, use_cases[j]) 
        
        config_post = send_data_custom_device(logger, restpoint, json_data)
        json_data["series"] = []
        time.sleep(20)
        #count = count + 1

  except Exception, e:
    traceback.print_exc()

