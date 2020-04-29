from tello import Tello
import sys
from datetime import datetime
import time

from vcm import VCM
#READ COMMANDS: ADD ?
#speed: cm/s
#battery: %
#time: s
#height: cm
#temp:ºC
#attitude: IMU
#baro: m
#acceleration: IMU
#tof: cm
#wifi: SNR

#WRITE COMMANDS:
#command - switches drone to SDK
#takeoff
#land
#emergency
#up, down, left, right, forward, back: x (cm)
#cw, ccw: 1-3600º
#go: x, y, z, speed
#speed: x
vcm = VCM()

start_time = str(datetime.now())
tello = Tello()

while True:
    command = input("INPUT COMMAND: ")

    if command != '' and command != '\n':
        command = command.rstrip()

        if command.find('delay') != -1:
            sec = float(command.partition('delay')[2])
            print ('delay %s' % sec)
            time.sleep(sec)
            pass

        elif command.find('land') != -1 or command.find('emergency') != -1:
            tello.send_command(command)
            break
        else:
            tello.send_command(command)

log = tello.get_log()

out = open(start_time[:10] + '.txt', 'w')
for stat in log:
    stat.print_stats()
    statstr = stat.return_stats()
    out.write(statstr)