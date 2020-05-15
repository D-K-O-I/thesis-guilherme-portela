import sys
from datetime import datetime
import time
import global_vars
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

dt = datetime.now()
start_time = dt.strftime("%Y%m%d_%H%M")

#start_time = str(datetime.now())

#file_name = sys.argv[1]

f = open(global_vars.filename, "r")
commands = f.readlines()
f.close()

#tello = Tello()
for command in commands:
    if command != '' and command != '\n':
        command = command.rstrip()

        if command.find('delay') != -1:
            sec = float(command.partition('delay')[2])
            print ('delay %s' % sec)
            time.sleep(sec)
            pass
        else:
            global_vars.tello.send_command(command)

log = global_vars.tello.get_log()

out = open(start_time + '.txt', 'w')
for stat in log:
    stat.print_stats()
    str = stat.return_stats()
    out.write(str)