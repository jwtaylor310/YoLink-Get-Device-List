#!/usr/bin/python3
Filename= "yolink_get_devices.py"
Version = "1.00"

# Version 1.00: Adapted from version 1.68 of yolink_health.py
import json
import time
import datetime
import smtplib
from pprint import pprint
import paho.mqtt.client as mqtt
import requests
from requests.structures import CaseInsensitiveDict
import os
import os.path

# Name of file containing configuration information
config_file='yolink_get_devices.cfg'

# Name of activity log file
log_file="yolink_get_devices.log"

# Yolink MQTT Broker variables:
YL_mqttBroker = 'api.yosmart.com'
YL_port = 8003

# Access Token time variables
# The access_token_timestamp value is set to a default value in the past here.  It will be 
# updated with the current value each time a new access token is obtained.
# The YL_token_valid_minutes is the number of minutes that a newly issued access token is valid.
# It is set to 120 minutes here but will be updated each time an access token is obtained.
access_token_timestamp=datetime.datetime.now()-datetime.timedelta(days=7)
YL_token_valid_minutes = 120 

# Flags to determine whether information from MQTT broker is current
YL_token_valid = False

# Build Yolink unix style date/time string from current date/time
def unix_timestamp():
   now = int(time.time()*1000)
   return str(now)

# Convert Yolink version of Unix time to Python datetime format
def unpack_unix_time(time):
   dt=datetime.datetime.fromtimestamp(int(time/1000))
   return(dt.strftime('%Y-%m-%d %I:%M:%S %p'))

# Build formatted date/time string from current date/time.
def timestamp():
   now=datetime.datetime.now()
   return(now.strftime('%Y-%m-%d %I:%M:%S %p'))

# Function to get program configuration information from external file
def read_config_variables():
    global UAID
    global SECRET_KEY
    global verbose
    global poll_interval
    global valid_config_file

    # Flag for valid config file contents.  Gets turned off if any entry from this
    # point forward is invalid in which case the rest of the lookups are abandoned
    valid_config_file = True

    if valid_config_file: UAID=get_config_string('UAID')
    if valid_config_file: SECRET_KEY=get_config_string('SECRET_KEY')
    if valid_config_file: verbose=get_config_truefalse('verbose')
    if valid_config_file: poll_interval=get_config_integer('poll_interval')

    return valid_config_file


# Function to search configuration file for a specific variable entry
def get_config_string(vname):
    global valid_config_file

    found = False
    vname_value = ''
 
    try:
        file = open(config_file,'r')

        for line in file:
            ptr=line.find('=')
            if ptr >= 0:
                tag = line[:ptr]
                tag=tag.rstrip(' ')
                if tag == vname:
                    vname_value = line[ptr+1:]
                    vname_value = vname_value.rstrip('\n')
                    vname_value = vname_value.lstrip(' ').rstrip(' ')
                    found = True

        file.close()
    except:
       valid_config_file = False

    if found == False:
       print('Unable to locate entry for key "%s" in "%s" configuration file.\n' % (vname,config_file))

    return vname_value

# Function to search configuration/state file for a specific variable which must have True or False value
def get_config_truefalse(vname):
    global valid_config_file
    
    vname_value = get_config_string(vname)
    result=''
    if valid_config_file:
        if vname_value=='True':
            result = True
        elif vname_value=='False':
            result = False
        else:
            valid_config_file = False
            print('Invalid True/False setting for key "%s" in "%s" configuration file.\n' % (vname,config_file))

    return result

# Function to search configuration file for a specific variable which must convert to an integer
def get_config_integer(vname):
    global valid_config_file
    
    vname_value = get_config_string(vname)
    result=''
    if valid_config_file:
       try:
          result = int(vname_value)
       except:
          result = ''
          valid_config_file = False
          print('Invalid integer value for key "%s" in "%s" configuration file.\n' % (vname,config_file))

    return result

# Function to search configuration file for a specific variable which must convert to a list
def get_config_list(vname):
    global valid_config_file
    
    vname_value = get_config_string(vname)
    result=''
    if valid_config_file:
       try:
          result = vname_value.split(',')
       except:
          result = []
          valid_config_file = False
          print('Invalid list entry for key "%s" in "%s" configuration file.\n' % (vname,config_file))

    return result


#=============================================================================================
# Get YoLink Access Token
#=============================================================================================
def YL_get_access_token():
   global YL_access_token_timestamp
   global YL_access_token, YL_token_valid, YL_token_valid_minutes

   print("Getting Access Token")

   url = "http://api.yosmart.com/open/yolink/token"

   headers = CaseInsensitiveDict()
   headers["Content-Type"] = "application/x-www-form-urlencoded"

   data = "grant_type=client_credentials&client_id="+UAID+"&client_secret="+SECRET_KEY

   resp = requests.post(url, headers=headers, data=data)
   
   if resp.status_code == 200:

      # Response of 200 means valid POST
      # Proceed to request the record
      try:
         result = resp.json()

         YL_access_token = result['access_token']
         YL_token_type = result['token_type']
         YL_expires_in = result['expires_in']
         YL_refresh_token = result['refresh_token']
         YL_scope = result['scope']

         YL_access_token_timestamp = datetime.datetime.now()
         YL_token_valid_minutes = int(YL_expires_in/60)
         YL_token_valid = True

         if verbose:
            print("\nAccess Token Fields:")
            print("token: %s" % YL_access_token)
            print("type: %s" % YL_token_type)
            print("expires_in: %s - %s" % (YL_expires_in,YL_token_valid_minutes))
            print("refresh_token: %s" % YL_refresh_token)
            print("scope: %s" % YL_scope)
      except:
         YL_token_valid = False

   else:
      YL_token_valid = False

   if YL_token_valid == False:
      ###!!!
      fid=open("dump.txt","a")
      fid.write("%s Exit!" % timestamp())
      fid.close()
      print('Home.getDeviceList\n*** Unable to obtain Access Token.  Check the credentials in the configuration file "%s".' % config_file)
      print("\nProgram stopped.\n")
      os._exit(5)
   return()


#=============================================================================================
# Get Device List
#=============================================================================================
def YL_get_device_list():

   url = "https://api.yosmart.com/open/yolink/v2/api"

   headers = CaseInsensitiveDict()
   headers["Content-Type"] = "application/json"
   headers["Authorization"] = "Bearer "+ YL_access_token

   data = '{"method":"Home.getDeviceList","time":"' + unix_timestamp() + '"}'

   resp = requests.post(url, headers=headers, data=data)

   if resp.status_code == 200:

      # Response of 200 means valid POST
      # Proceed to request the record
      result = resp.json()

      YL_code = result['code']
      YL_time = result['time']
      YL_msgid = result['msgid']
      YL_method = result['method']
      YL_desc = result['desc']

      if verbose:
         print("\nDevice List Fields")
         print("code: %s" % YL_code)
         print("time: %s = %s" % (YL_time,unpack_unix_time(YL_time)))
         print("msgid: %s" % YL_msgid)
         print("method: %s" % YL_method)
         print("desc: %s" % YL_desc)


      # Extract sub-dictionary containing the device information
      YL_device_dictionary = result["data"]["devices"]

      # Display the device ID's and name for each entry
      for entry in YL_device_dictionary:
         YL_device_Id = entry["deviceId"]
         YL_device_UDID = entry["deviceUDID"]
         YL_device_name = entry['name']
         print("ID: %s    UDID: %s    %s" % (YL_device_Id, YL_device_UDID, YL_device_name))

   return()

# ==========================================================================
#
# Main Program
#
# ==========================================================================

print("\n%s\nProgram %s Version %s startup\n%s" % ('='*50, Filename, Version, '='*50))

if os.path.exists(config_file):
   read_config_variables()
   if valid_config_file == False:
      print('Invalid configuration file "%s".  Program unable to continue.\n' % config_file)

else:
   valid_config_file = False
   print('Missing configuration file "%s".\n' % config_file)
   print('Obtain a copy of "yolink_get_devices_template.cfg", edit it for your environment,')
   print('then save it as "%s" in the same folder as the main "yolink_get_devices.py" program.' % config_file)
   print('\nExiting program\n')

while valid_config_file:

   YL_get_access_token()

   # Calculate time 5 minutes before access token is set to expire
   YL_refresh_time = YL_access_token_timestamp+datetime.timedelta(minutes=(YL_token_valid_minutes-5))
   print("New refresh time: %s" % YL_refresh_time)

   # Poll broker and display device list until it is time to get new token
   while datetime.datetime.now() < YL_refresh_time:
      print("\n%s Polling" % timestamp())

      # Get list of devices
      YL_get_device_list()

      # Sleep for "poll_interval" seconds before returning to top of loop and starting a new poll
      time.sleep(poll_interval)
      print("\033c")

   # Time for refresh.  Go to top of loop and get new access token


# ==========================================================================
# End of Program
