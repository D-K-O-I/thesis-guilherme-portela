import sys
from datetime import datetime
import time
import global_vars
import numpy
import matplotlib.pyplot as plt
import os
import re
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

if False:
	dt = datetime.now()
	start_time = dt.strftime("%Y%m%d_%H%M")

	#start_time = str(datetime.now())

	#file_name = sys.argv[1]

	f = open(global_vars.filename_test, "r")
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

if True:
	out = open("20200622_1710.txt", 'r')
	x1_axis = []
	y1_axis = []
	x2_axis = []
	y2_axis = []
	x3_axis = []
	y3_axis = []

	out.seek(0, os.SEEK_SET)
	line = out.readline()
	while line:
		if "id: " in line:
			x_point = int(re.sub('\D', '', line))
			line = out.readline()
			if "battery?" in line:
				x1_axis.append(x_point)
				battery_value_str = out.readline()
				battery_value_int = re.sub('\D', '', battery_value_str)
				y1_axis.append(battery_value_int)
			if "wifi?" in line:
				x2_axis.append(x_point)
				snr_value_str = out.readline()
				snr_value_int = re.sub('\D', '', snr_value_str)
				y2_axis.append(snr_value_int)
			if "temp?" in line:
				x3_axis.append(x_point)
				tmp_value_str = out.readline()
				tmp_value_int = re.sub('\D', '', tmp_value_str)
				tmp_value_int_low = int(str(tmp_value_int)[0]+str(tmp_value_int[1]))
				tmp_value_int_high = int(str(tmp_value_int)[2]+str(tmp_value_int[3]))
				tmp_avg = (tmp_value_int_low + tmp_value_int_high)/2
				y3_axis.append(tmp_avg)
		line = out.readline()

	plt.title("Battery spenditure during flight")
	plt.xlabel("Command ID")
	plt.ylabel("Battery (Percentage)")
	x1_plot = numpy.array(x1_axis)
	y1_plot = numpy.array(y1_axis)
	plt.plot(x1_plot, y1_plot,'go')
	plt.gca().invert_yaxis()
	plt.draw()

	plt.figure()
	plt.title("Wi-Fi SNR during flight")
	plt.xlabel("Command ID")
	plt.ylabel("SNR (dB)")
	x2_plot = numpy.array(x2_axis)
	y2_plot = numpy.array(y2_axis)
	plt.plot(x2_plot, y2_plot,'bo')
	plt.gca().invert_yaxis()
	plt.draw()

	plt.figure()
	plt.title("Drone Temperature during flight")
	plt.xlabel("Command ID")
	plt.ylabel("Temp (Celsius)")
	x3_plot = numpy.array(x3_axis)
	y3_plot = numpy.array(y3_axis)
	plt.plot(x3_plot, y3_plot,'ro')
	plt.draw()

	plt.show()
