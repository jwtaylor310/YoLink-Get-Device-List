# Yolink Get Devices
This is a Python program that periodically polls the YoLink MQTT broker to obtain and display the list of all devices bound to an account.

This program was developed and tested on a Raspberry Pi.  It has also been teseted and runs successfully on a Windows 11 PC.


### Setup:
   1. Copy "yolink_get_devices.py" and "yolink_get_devices_template.cfg" to the folder on the computer Pi that you will be using for the program (e.g, "YL_get_devices").  The files are available for download at https://github.com/jwtaylor310/YoLink_Get_Device_List.  Click on the green 'Code" button and select "Download ZIP" to download the files.
  
   2. Obtain User Access Credentials for your YoLink account.  This is done by opening the YoLink app on a cell phone, then selecting the 
      'hamburger' icon at the top-left corner and navigating to Settings...Account...Advanced Settings...User Access Credentials.  Record
      the UAID and Secret Key.  These values are unique to your account and should not be shared.
    
   3. On the computer, copy the "yolink_get_devices_template.cfg" file to "yolink_get_devices.cfg".  Then edit "yolink_get_devices.cfg" to replace the dummy values of UAID and SECRET_KEY with the values obtained in the previous step.

4. If you will be running the program under Windows, you will need to install Python on the PC if that hasn't been done previously. It can be downloaded from the Microsoft store. (Python is installed by default in the distribution version of the Raspberry Pi operating system).

5. This program uses the "paho-MQTT" library. If you have not done so previously, you will need to install that library on the computer. To do so, open a terminal window and enter the command "pip install paho-mqttt".

6. This program uses the "request" library.  That library is normally included in the distribution version of the Raspberry Pi
   operating system.  It is not normally included in Windows.  To install in either environment, use the command
   "python -m pip install requests".

     
### Running the program:
   Open a terminal session on the Raspberry Pi or a Command Prompt window if you are using Windows.  Navigate to the folder where you have installed the "yolink_get_devices.py" and the "yolink_get_devices.cfg" files.
   Start the program by entering the command  "python yolink_get_devices.py". (Some Pi's may require specifying "python3" instead of just "python").  The program
   will start and it will request the current list of devices from the YoLink MQTT broker.  The results will be displayed in the terminal session.  The program
   will then sleep for five minutes before repeating the process.  You can adjust the sleep time by editing the entry for 'poll_interval' in the configuration
   file.  The value is the number of seconds between polls.  Press "Ctrl-c" to exit the program.

   The program may be run continuously.  The access token for the YoLink MQTT broker expires periodically, typically after two hours.  The program keeps track of the expiration time and five minutes before the token is due to expire it will automtically request a new token.  This allows the program to maintain valid authentication indefinitely.
