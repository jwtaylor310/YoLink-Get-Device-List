# Yolink-Get-Devices
Python program to periodically poll the YoLink MQTT broker to obtain and display the list of all devices bound to an account.

Developed on a Raspberry Pi.  May run in other environments that support Python, but only tested on Pi's.


###Setup:
   1. Copy yolink_get_devices.py and yolink_get_devices_template.cfg to a folder on your Raspberry Pi.
  
   2. Obtain User Access Credentials for your YoLink account.  This is done by opening the YoLink app on a cell phone, then selecting the 
      'hamburger' icon at the top-left corner and navigating to Settings...Account...Advanced Settings...User Access Credentials.  Record
      the UAID and Secret Key.  These values are unique to your account and should not be shared.
    
   3. Copy the yolink_get_devices_template.cfg file to yolink_get_devices.cfg.  Then edit yolink_get_devices.cfg to replace the dummy values of UAID and SECRET_KEY
      with the values obtained in the previous step.     
     
     
###Running the program:
   Open a terminal session on the Raspberry Pi.  Navigate to the folder where you have installed the "yolink_get_devices.py" and "yolink_get_devices.cfg" files.
   Start the program with the command: "python yolink_get_devices.py".  (Some Pi's may require specifying "python3" instead of just "python").  The program
   will start and it will request the current list of devices from the YoLink MQTT broker.  The results will be displayed in the terminal session.  The program
   will then sleep for 5 minutes before repeating the process.  You can adjust the sleep time by editing the entry for 'poll_interval' in the configuration
   file.  The value is the number of seconds between poll.

   The program may be run continuously.  It keeps track of the expiration time of the access token.  Five minutes before the token is due to expire the program
   requests a new token.  This allows the program to maintain valid authentication indefinitely.
