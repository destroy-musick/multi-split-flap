# multi-split-flap
Branch from Split Flap project, including original arduino code and modified wrapper script. This is designed to help facilitate the use of multiple arduino mc's to act as one large unit

<h1>Usage</h1>

Before running the main.py script to initialise the split-flap application, all Arduino/Arduino-like modules need to be registered using the arduinoregistration.py script. This requires **python3** to run

**PREPARING ARDUINO**

First, apply the splitflap.ino file found in arduino\splitflap\ to your arduino via the Arduino IDE. This INO file is set to look at 10 motors and sensors by default

**REGISTER ARDUINO**

This script assists in registering and modifying the crucial Printflapconfig.json configuration file. This file defines the size of the split-flap installation, and will require each arduino to be register in its own individual index.

For example:

557353231363512011C1 is registered to index position 1

In a 2 x 7 grind, you will have space for 14 indexes, with index 1 being the top left, reading left to right. The script can also swap out indexes and can display the grid as defined in the config: 

                ________________________________________________________________________________
                |                                        |                                        |
                |        1 - 5573631313835180B1B2        |        2 - 557353231363512011C1        |
                |________________________________________|________________________________________|
                |                                        |                                        |
                |                                        |                                        |
                |________________________________________|________________________________________|
                |                                        |                                        |
                |                                        |                                        |
                |________________________________________|________________________________________|
                |                                        |                                        |
                |                                        |                                        |
                |________________________________________|________________________________________|
                |                                        |                                        |
                |                                        |                                        |
                |________________________________________|________________________________________|
                |                                        |                                        |
                |                                        |                                        |
                |________________________________________|________________________________________|
                |                                        |                                        |
                |                                        |                                        |
                |________________________________________|________________________________________|
				

To register an arduino, ensure that the device is plugged into the controller (as Raspberry PI or PC) and then choose a free index slot on the grid. This will allow the main.py script to know where to send each piece of text

<h1>MAIN SCRIPT</h1>

The main script usage is defined as follows:

	    '-m --manualinput : Manual Input Mode\n' \
            '-s --script : Script mode, supply full path name of text file as script file\n' \
            '-t --time : In seconds. If not using manual input, the minimum time delay between text changes\n' \
            '-i --iterations : If using script mode, number of iterations to run the script. 0 or leave to set as indefinite\n' \
            '-l --listener : The full directory path of the folder to listen to.  Must be supplied if running in no other mode\n' \
            '\n' \
            'Default mode is to run as a \'listener\' that will check every 2 seconds for the existence of a script file.\n' \
            'This script file will be consumed by the python script'
		

There are 3 modes of operation:

**Listener (default)**

The script cannot run without at least a listener folder being chosen. This folder is used to listen for any files and read its text contents. This text will then be consumed by the application, removed and each line processed across the split-flap installation. This is the default option if no other argument is set.

Example: python3 main.py -l C:\Users\Admin\Documents\GitHub\multi-split-flap\software\listener_input --- This script will look in the listener_input folder indefinitely for text files to consume, and iterate every 5 seconds

**Script**

This mode is defined when the full path name of a single file is chosen. This script will be read line by line, with an interval (-t) between each line in seconds. If no interval is chosen, it will default to 5 seconds.

Example: python3 main.py -s C:\Users\Admin\Documents\GitHub\multi-split-flap\software\example_script.txt -t 2 --- This will run the script in script mode interval through each line in the file every 2 seconds indefinitely

**Manual Input**

This mode will initialise the modules and then wait for user input before running

Example: python3 main.py -m

**Troubleshooting**

Hardware sensor output is displayed with each word iteration, including the index number of the arduino returning the fault, and the sensor number (1 - 10) returning the error:

Sensor Error - Arduno no.1 - Sensor no.2 - missed_home 1 - unexpected_home 0 --- This means arduino at index 1 has a fault reported on sensor number 2

At the beginning of each initialisation, all sensors will report back to the script if there is any error status:

Arduino Index - 2 - sensor_error
Sensor Number - 3

This means Arduino at index 2, sensor number 3, is having a fault initialising. This would almost always be a hardware error, so hardware troubleshooting would be required until the sensor is working optimaly.

If the script is throwing unhandled or unexpected errors, please check you are running and executing the latest version of python. This requires python 3 to run
