from __future__ import print_function
from splitflap import Splitflap
from multiprocessing.pool import ThreadPool

import json
import os
import serial
import serial.tools.list_ports
import sys


def get_text(port):
    try:
        flaptext = ''
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

            flaptext += letter

        print('{} - {} - {}'.format(port['Serial Number'], port['Index'], flaptext))

    except Exception as e:
        print('Error: {}'.format(e))


def run():

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

    # Loop through entering text until closure. Split each string into equal pieces and send to the correct positional
    # index.

    while True:

        text = input("Type in a word: ")
        text_arr = split_text(text)
        splitflaps_update = []

        for index in range(len(text_arr)):
            x = index + 1  # increment index to account for zero based indexing
            port = next((y for y in ports if y['Index'] == x), None)
            if port is not None and port['Initialised']:
                pos_index = port['Index']
                text = text_arr[pos_index - 1].lower()  # minus 1 to account for zero based indexing
                port['Text'] = text
                splitflaps_update.append(port)
                #try:
                    #result = a_send_text(port, text)  # port['Splitflap'].set_text(text)
                    #print(text)
                    #print(result)
                #except Exception as e:
                #    print("Error {}".format(e))

        pool = ThreadPool()
        pool.map(get_text, splitflaps_update)


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
