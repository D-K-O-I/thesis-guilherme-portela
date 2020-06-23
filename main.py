from vcm import VCM
from tello import Tello
from datetime import datetime
import global_vars
import time
import multiprocessing
import subprocess
import os
import sys
import math
import matplotlib.pyplot as plt
import numpy
import re

DRONE_DISTANCE = 20 #arbitrary
DRONE_MAXHEIGHT = 200
drone_position = None #metric::= [0.0, 0.0, 0.0]
rcv = 0


def query_rfid():
	#hardware instruction: query nearby path markers
	#retrieve nearest RFID by RSSI and virtual coordinates
	pass

def check_rssi(node):
	#t: tag-found query
	#t = None
	#rcv = None
	#while t is None:
	#	print("Sending RFID signal to nearby nodes...")
	#	#rcv::= (EPC, RSSI)
	#	rcv = query_rfid()
	#	time.sleep(1)
	#	if rcv[0] == node:
	#		t = 0
	#		print("Found node " + str(rcv[0]) + "; RSSI = " + str(rcv[1]))
	#return rcv
	pass

def movement_controller(traverse_order, shelf_level, node, next_node, nodemap, dhc):
	string_builder_temp = ""
	#for each node to be traversed
	#wait for immediate node tag (path marker) to be checked
	#p = multiprocessing.Process(target=check_rssi, args=(node,))
	#p.start()
	#timeout
	#p.join(3)
	if rcv is None:
		#re-route: create new route with remaining levels, cross out current node from temp nodemap
		global_vars.flag_reroute = True
		vcm.route3d()
		#spanning_tree_reached will include current level progress
		#spanning_tree_unreached will contain the remaining nodes
		#since drone is taking the shortest path already, carry on with regular movement
	else:
		movement_vector = (nodemap[next_node][0] - nodemap[node][0], nodemap[next_node][1] - nodemap[node][1])
		print(movement_vector)
		if (movement_vector[0] != movement_vector[1] and (movement_vector[0] == 0 or movement_vector[1] == 0)):
			#ORTHOGONAL CASE
			#vertical movement
			if movement_vector[0] == 0:
				if movement_vector[1] < 0:
					#string_builder_temp += "back "
					if dhc == 180:
						string_builder_temp += "forward "
					else:
						rotation = (180 - dhc) % 360
						if rotation <= 180:
							string_builder_temp += "cw " + str(rotation) + "\n"
						else:
							string_builder_temp += "ccw" + str(rotation%180) + "\n"
						string_builder_temp += "forward "
						dhc = 180

				else:
					#string_builder_temp += "forward "
					if dhc == 0:
						string_builder_temp += "forward "
					else:
						rotation = (0 - dhc) % 360
						if rotation <= 180:
							string_builder_temp += "cw " + str(rotation) + "\n"
						else:
							string_builder_temp += "ccw" + str(rotation%180) + "\n"
						string_builder_temp += "forward "
						dhc = 0

				string_builder_temp += str(abs(movement_vector[1])*DRONE_DISTANCE)
				
			#horizontal movement
			elif movement_vector[1] == 0:
				if movement_vector[0] < 0:
					#string_builder_temp += "left "
					if dhc == 270:
						string_builder_temp += "forward "
					else:
						rotation = (270 - dhc) % 360
						if rotation <= 180:
							string_builder_temp += "cw " + str(rotation) + "\n"
						else:
							string_builder_temp += "ccw" + str(rotation%180) + "\n"
						string_builder_temp += "forward "
						dhc = 270

				else:
					#string_builder_temp += "right "
					if dhc == 90:
						string_builder_temp += "forward "
					else:
						rotation = (90 - dhc) % 360
						if rotation <= 180:
							string_builder_temp += "cw " + str(rotation) + "\n"
						else:
							string_builder_temp += "ccw" + str(rotation%180) + "\n"
						string_builder_temp += "forward "
						dhc = 90

				string_builder_temp += str(abs(movement_vector[0])*DRONE_DISTANCE)
			
			string_builder_temp += "\n"
		else:
			#DIAGONAL CASE
			if dhc != 0:
				rotation = (0 - dhc) % 360
				string_builder_temp += "cw " + str(rotation) + "\n"
				dhc = 0
			#string_builder_temp += "up " + str(abs(100)) + "\n" #UNQUOTE AFTER DRONE_POSITION IS DEFINED
			#move diagonally to point
			angle_degrees = math.degrees(math.atan2(movement_vector[0], movement_vector[1]))
			hypotenuse = math.hypot(movement_vector[0], movement_vector[1])

			angle_degrees = angle_degrees % 360

			if angle_degrees <= 180:
				#cw angle
				string_builder_temp += "cw " + str(angle_degrees) + "\n"
				#forward hypotenuse
				string_builder_temp += "forward " + str(hypotenuse*DRONE_DISTANCE) + "\n"
				#ccw angle
				string_builder_temp += "ccw " + str(angle_degrees) + "\n"

			else:
				#ccw 360 - angle
				string_builder_temp += "ccw " + str(360 - angle_degrees) + "\n"
				#forward hypotenuse
				string_builder_temp += "forward " + str(hypotenuse*DRONE_DISTANCE) + "\n"
				#cw 360 - angle
				string_builder_temp += "cw " + str(360 - angle_degrees) + "\n"
			
			#string_builder_temp += "down " + str(abs(100)) + "\n" #UNQUOTE AFTER DRONE_POSITION IS DEFINED
	movement = string_builder_temp
	return movement, dhc

def connection_broker():
	dt = datetime.now()
	start_time = dt.strftime("%Y%m%d_%H%M")

	f = open(global_vars.filename, "r")
	commands = f.readlines()
	f.close()

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

	logname = start_time + '.txt'
	global_vars.logfile = logname
	out = open(start_time + '.txt', 'w')
	for stat in log:
		stat.print_stats()
		str = stat.return_stats()
		out.write(str)

def main():
	vcm = VCM()
	#tello = Tello()
	vcm.add_node("A",0,0)
	vcm.add_node("B",1,0)
	vcm.add_node("C",0,-1)
	vcm.add_node("D",1,-1)
	vcm.add_node("E",0,-2)
	vcm.add_node("F",1,-2)
	vcm.add_node("G",-1,0)
	vcm.add_node("H",-1,1)
	vcm.add_node("I",0,1)
	vcm.add_node("J",1,1)
	vcm.add_node("K",0,2)
	vcm.add_node("L",-1,-2)
	
	vcm.add_node("M",2,0)
	vcm.add_node("N",2,-1)
	vcm.add_node("O",2,-2)

	vcm.add_node("P",-2,0)
	vcm.add_node("Q",-3,0)
	vcm.add_node("R",-2,1)
	vcm.add_node("S",-3,1)

	vcm.add_node("T",2,1)
	vcm.set_perimeter((-1,-1),(1,1))
	
	f = open(global_vars.filename, 'w')
	f.write("command\n")
	#f.write("speed 10\n")
	f.write("battery?\n")
	f.write("wifi?\n")
	f.write("takeoff\n")
	f.write("down 20\n")
	
	string_builder = ""

	nodemap = vcm.get_nodemap()
	vcm.route_3d()
	print(vcm.traverse_order)

	drone_position = [vcm.traverse_order[0][0], 0]
	#drone heading current
	dhc = 0
	#print(drone_position)
	#print(vcm.nodemap[drone_position])
	#tello.on_close()
	for shelf_level in vcm.traverse_order:
		pair_stop = shelf_level[0]
		for node, next_node in zip(shelf_level, shelf_level[1:] + [shelf_level[0]]):
			if next_node != pair_stop:
				print(node, next_node)
				#make MOVEMENT command
				sbt, dhc = movement_controller(vcm.traverse_order, shelf_level, node, next_node, nodemap, dhc)
				string_builder += sbt
				string_builder += "delay 1\n"
				string_builder += "battery?\n"
				#string_builder += "wifi?\n"
				string_builder += "temp?\n"

				#print(dhc)
		#-> make UP command
		string_builder += "up " + str(abs(DRONE_DISTANCE)) + "\n"

	f.write(string_builder)
	f.write("land\n")
	f.close()
	#finally, connection broker relays all commands to drone
	#connection broker attempts to resend commands!
	connection_broker()
	global_vars.tello.on_close()
	

	#COMMAND-BASED BATTERY LEVEL GRAPH PER COMMAND IDs [MOVED TO tello_test.py]
	#x1_axis = []
	#y1_axis = []
	#x2_axis = []
	#y2_axis = []
	#logreader = open(global_vars.logfile, 'r')
	#line = logreader.readline()
	#while line:
	#	if "id: " in line:
	#		x_point = int(re.sub('\D', '', line))
	#		line = logreader.readline()
	#		if "battery?" in line:
	#			x1_axis.append(x_point)
	#			battery_value_str = logreader.readline()
	#			battery_value_int = re.sub('\D', '', battery_value_str)
	#			y1_axis.append(battery_value_int)
	#		#if "wifi?" in line:
	#		#	x2_axis.append(x_point)
	#		#	snr_value_str = logreader.readline()
	#		#	snr_value_int = re.sub('\D', '', snr_value_str)
	#		#	y2_axis.append(snr_value_int)
	#		if "temp?" in line:
	#			x2_axis.append(x_point)
	#			tmp_value_str = logreader.readline()
	#			tmp_value_int = re.sub('\D', '', tmp_value_str)
	#			y2_axis.append(tmp_value_int)
	#	line = logreader.readline()

	#plt.title("Battery spenditure during flight")
	#plt.xlabel("Command ID")
	#plt.ylabel("Battery")
	#x1_plot = numpy.array(x1_axis)
	#y1_plot = numpy.array(y1_axis)
	#plt.plot(x1_plot, y1_plot)
	#plt.gca().invert_yaxis()
	#plt.draw()

	#plt.figure()
	#plt.title("Wi-Fi SNR during flight")
	#plt.xlabel("Command ID")
	#plt.ylabel("SNR")
	#x2_plot = numpy.array(x2_axis)
	#y2_plot = numpy.array(y2_axis)
	#plt.plot(x2_plot, y2_plot)
	#plt.gca().invert_yaxis()
	#plt.draw()

	#plt.show()
if __name__ == '__main__':
	main()