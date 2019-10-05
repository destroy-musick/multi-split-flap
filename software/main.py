from __future__ import print_function
from splitflap import Splitflap
from multiprocessing.pool import ThreadPool

import json
import os
import serial
import serial.tools.list_ports
import sys
import getopt
import time


def run():

    script_arguments = get_arguments()
    run_mode = 'listen_mode'

    if script_arguments['manual_mode']:
        run_mode = 'manual_mode'
    elif script_arguments['script_mode']:
        run_mode = 'script_mode'

    print('Script is running in {} '.format(run_mode))

    ports = get_ports()

    print('Starting...')

    # Mark all arduino ports which cannot be read or initialised.
    for port in ports:
        err_count = 0
        try:
            sensors = port['Splitflap'].loop_for_status()
            print(sensors)
            for x, sensor in enumerate(sensors):
                if sensor['state'] != 'normal':
                    print('=======================================')
                    print('Arduino Index - {} - {}'.format(port['Index'], sensor['state']))
                    print('Sensor Number - {}'.format(x + 1))
                    print('=======================================')
            port['Initialised'] = True
        except Exception as e:
            print('Arduino - {} at index {} is not initialised'.format(port['Serial Number'], port['Index']))
            print('{}'.format(e))
            port['Initialised'] = False
            err_count += 1

    if err_count == len(ports):
        print('All units have failed to initialise!')
        sys.exit(1)
    elif err_count > 0:
        print('{} have failed to initialise!'.format(err_count))

    # Now run with the specified mode

    interval = script_arguments['time']

    if run_mode == 'manual_mode':
        run_manual_mode(ports)
    elif run_mode == 'script_mode':
        iterations = script_arguments['iterations']
        script_file = script_arguments['script']
        run_script_mode(ports, interval, script_file, iterations)
    else:
        folder = script_arguments['listener']
        run_listen_mode(ports, interval, folder)


def get_text(port):
    try:
        flap_text = ''
        text = port['Text']
        result = port['Splitflap'].set_text(text)
        for x, sensor in enumerate(result):
            letter = '*'
            missed_home = sensor['count_missed_home']
            unexpected_home = sensor['count_unexpected_home']
            if sensor['state'] == 'normal':
                letter = sensor['flap']

            if missed_home > 0 or unexpected_home > 0:
                print('Sensor Error - Arduno no.{} - Sensor no.{} - missed_home {} - unexpected_home {}'.format(port['Index'], x + 1, missed_home, unexpected_home))

            flap_text += letter

        print('{} - {} - {}'.format(port['Serial Number'], port['Index'], flap_text))

    except Exception as e:
        print('Error: {}'.format(e))


def get_arguments():

    # get command line options to determine operating mode
    usage = '-m --manualinput : Manual Input Mode\n' \
            '-s --script : Script mode, supply full path name of text file as script file\n' \
            '-t --time : In seconds. If not using manual input, the minimum time delay between text changes\n' \
            '-i --iterations : If using script mode, number of iterations to run the script. 0 or leave to set as indefinite\n' \
            '-l --listener : The full directory path of the folder to listen to.  Must be supplied if running in no other mode\n' \
            '\n' \
            'Default mode is to run as a \'listener\' that will check every 2 seconds for the existence of a script file.\n' \
            'This script will be consumed by the python script'

    opts, args = getopt.getopt(sys.argv[1:], 'ms:t:i:l:', ['manualinput', 'script=', 'time=', 'iterations=', 'listener='])

    command_arguments = {'time': 5,  # default time between queued up lines of text
                         'iterations': 0,
                         'script': None,
                         'manual_mode': False,
                         'script_mode': False,
                         'listen_mode': True,
                         'listener': None}

    for opt, arg in opts:
        if opt in ('-m', '--manualinput'):
            command_arguments['manual_mode'] = True
        elif opt in ('-s', '--script'):
            command_arguments['script_mode'] = True
            command_arguments['script'] = arg
        elif opt in ('-i', '--iterations'):
            command_arguments['iterations'] = int(arg)
        elif opt in ('-t', '--time'):
            command_arguments['time'] = int(arg)
        elif opt in ('-l', '--listener'):
            command_arguments['listener'] = arg
            command_arguments['listen_mode'] = True

    if len(opts) == 0:
        print('No arguments supplied')
        print(usage)
        sys.exit(2)

    if command_arguments['manual_mode'] and command_arguments['script_mode']:
        print('Only one mode can be selected')
        print(usage)
        sys.exit(2)
    else:
        return command_arguments


def run_script_mode(ports, interval, file, iterations):
    print('Run script mode')
    print('Time between text: {}'.format(interval))

    try:
        with open(file) as fp:
            line_list = [line.rstrip('\n') for line in fp]  # Get file contents as list
    except Exception as ex:
        print('Cannot open or read file: {}'.format(file))
        print(ex)
        return

    if iterations > 0:
        x = 0
        while x < iterations:
            print('Iteration {} of {}'.format(x + 1, iterations))
            for line in line_list:
                set_text(ports, line)
                time.sleep(interval)
            x += 1
    else:
        while True:
            for line in line_list:
                set_text(ports, line)
                time.sleep(interval)


def run_listen_mode(ports, interval, folder):
    print('Run listen mode')
    print('Time between text: {}'.format(interval))
    print('Listening for file in {} folder'.format(folder))

    while True:
        for file in os.listdir(folder):
            print('Processing {}'.format(file))
            try:
                with open(os.path.join(folder, file)) as fp:
                    line_list = [line.rstrip('\n') for line in fp]
                    for line in line_list:
                        set_text(ports, line)
                        time.sleep(interval)
            except Exception as ex:
                print('Cannot read text in file')
                print('{}'.format(ex))
            finally:
                print('Removing {}'.format(file))
                os.remove(os.path.join(folder, file))

        time.sleep(interval)


def run_manual_mode(ports):

    while True:

        text = input("Type in a word: ")
        set_text(ports, text)


def set_text(ports, text):

    text_arr = split_text('{:140}'.format(text))  # Pad text to 140 blank characters if needed
    split_flaps_update = []

    for index in range(len(text_arr)):
        x = index + 1  # increment index to account for zero based indexing
        port = next((y for y in ports if y['Index'] == x), None)
        if port is not None and port['Initialised']:
            pos_index = port['Index']
            text = text_arr[pos_index - 1].lower()  # minus 1 to account for zero based indexing
            port['Text'] = text
            split_flaps_update.append(port)

    pool = ThreadPool()
    pool.map(get_text, split_flaps_update)


def split_text(x):
    chunks = len(x)
    text_arr = [x[i:i+10] for i in range(0, chunks, 10)]
    return text_arr


def get_ports():
    arduinos = []
    data = {}
    config = 'Printflapconfig.json'

    if os.path.exists(config):
        s = open(config, 'r').read()
        data = json.loads(s)
        print('Config file loaded')

    ports = serial.tools.list_ports.comports()

    for i, port in enumerate(ports):
        if any(d['serial_number'] == port.serial_number for d in data['arduinos']):
            arduinos_config = next(d for d in data['arduinos'] if d['serial_number'] == port.serial_number)
            arduinos.append({'Splitflap': Splitflap(serial.Serial(port.device, '38400', timeout=20)),
                             'Index': arduinos_config['position_index'],
                             'Serial Number': port.serial_number,
                             'Initialised': False,
                             'Text': None})
            print('{} {} has been initialized'.format(port.device, port.serial_number))

    return arduinos


if __name__ == '__main__':
    run()
