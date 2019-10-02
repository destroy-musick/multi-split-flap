# Used to place the arduino devices into a specific order for dynamic COM registration

import os
import json
import sys
import serial
import serial.tools.list_ports

data = {}
config = 'Printflapconfig.json'


def run():
    get_config()
    menu()


def get_config():

    if os.path.exists(config):
        s = open(config, 'r').read()
        global data
        data = json.loads(s)
        print('Config file loaded')
    else:
        print('Config file not found')
        create_config()


def create_config():
    print('Creating new config file. Please ensure at least 1 arduino device is plugged in before continuing')
    input('Press any key to continue...')
    data['rows'] = input('How many rows of arduinos?')
    data['columns'] = input('How many columns of arduinos?')
    data['arduinos'] = []
    arduino_registration()


def menu():

    ext = True
    while ext:
        print('')
        print('====== MAIN MENU ======')
        print('Please choose an option...')
        print('1. Register new Arduino Device')
        print('2. Set up Print Flap Orientation')
        print('3. Save and exit')
        print('4. Exit')
        print('')
        opt = int(input())
        if opt == 3:
            with open(config, 'w') as output:
                json.dump(data, output)
                print('Goodbye')
                ext = False

        elif opt == 1:
            arduino_registration()

        elif opt == 2:
            printflap_orientation()

        elif opt == 4:
            print('Goodbye')
            ext = False

        else:
            print('Please choose a valid option!')


def arduino_registration():

    arduinos = serial.tools.list_ports.comports()

    for i, port in enumerate(arduinos):
        if any(d['serial_number'] == port.serial_number for d in data['arduinos']):
            print('[{: 2}] {} - {} - {} - ALREADY REGISTERED'.format(i, port.device, port.description, port.serial_number))
        else:
            print('[{: 2}] {} - {} - {}'.format(i, port.device, port.description, port.serial_number))

    choice = input('Please choose Arduino device to add or q to quit')
    if choice != 'q' and choice != 'Q':
        index_of = int(choice)
        print('{} - {} - {}'.format(arduinos[index_of].device, arduinos[index_of].description, arduinos[index_of].serial_number))
        if any(d['serial_number'] == arduinos[index_of].serial_number for d in data['arduinos']):
            print('Arduino already registered!')
            arduino_registration()
        else:
            print('Please choose a position index')
            positionindex = int(input())
            if any(d['position_index'] == position_index for d in data['arduinos']):
                print('Index already taken')
                arduino_registration()
            else:
                data['arduinos'].append({"position_index": positionindex,
                                         "serial_number": arduinos[index_of].serial_number})
                choice = input("Do you wish to add another device? Y or any key to continue")

            if choice == 'Y' or choice == 'y':
                arduino_registration()


def printflap_orientation():

    grid = get_grid()
    print(grid)
    choice = input("Do you wish to move or swap an arduino? Y or any key to return to menu")
    if choice == 'y' or choice == 'Y':
        start_index = int(input('Please choose a number index to move:'))
        end_index = int(input('Please choose destination index'))
        arduino = next(d for d in data['arduinos'] if d['position_index'] == start_index)
        arduino['position_index'] = end_index
        printflap_orientation()


def get_grid():
    columns = int(data['columns'])
    box_width = 40
    ws = box_width * " "
    lm = box_width * "_"
    ds = " " * int((box_width / 4) - 2) + "%s" + (" " * int((box_width / 4) -2))
    cl_line = 2 * "\t" + " " + (box_width * columns) * "_" + "\n"
    ws_line = 2 * "\t" + (("|" + ws) * columns) + "|" + "\n"
    lm_line = 2 * "\t" + (("|" + lm) * columns) + "|" + "\n"
    ds_line = 2 * "\t" + (("|" + ds) * columns) + "|" + "\n"
    row = ws_line + ds_line + lm_line
    block = cl_line + (row * int(data['rows']))

    # Draw grind representing position of each arduino along with their serial number
    arduino_info = []
    total_indexes = int(data['columns']) * int(data['rows'])
    x = 1
    while x <= total_indexes:
        found = False
        for i in data['arduinos']:
            if i['position_index'] == x:
                arduino_info.append('{} - {}'.format(i['position_index'], i['serial_number']))
                found = True
                break

        if not found:
            arduino_info.append('                        ')

        x += 1

    return block % tuple(arduino_info)


if __name__ == '__main__':
    run()
