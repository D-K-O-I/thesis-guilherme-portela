from vcm import VCM
from tello import Tello
from datetime import datetime
import global_vars
import time
import multiprocessing
import subprocess
import os
import sys


#drone_position = None #metric::= [0.0, 0.0, 0.0]
rcv = None

def query_rfid():
	#hardware instruction: query nearby path markers
	#retrieve nearest RFID by RSSI and virtual coordinates
	pass

def check_rssi(node):
	#t: tag-found query
	t = None
	rcv = None
	while t is None:
		print("Sending RFID signal to nearby nodes...")
		#rcv::= (EPC, RSSI)
		rcv = query_rfid()
		time.sleep(1)
		if rcv[0] == node:
			t = 0
			print("Found node " + str(rcv[0]) + "; RSSI = " + str(rcv[1]))
	return rcv


def movement_controller(traverse_order, shelf_level, node):
	#for each node to be traversed
	#wait for immediate node tag (path marker) to be checked
	p = multiprocessing.Process(target=check_rssi, args=(node,))
	p.start()
	#timeout
	p.join(3)
	if rcv is None:
		#re-route: create new route with remaining levels, cross out current node from temp nodemap
		vcm.route3d()
		#spanning_tree_reached will include current level progress
		#spanning_tree_unreached will contain the remaining nodes
		#since drone is taking the shortest path already, carry on with regular movement
		pass
	else:
		#send command: compute required movement
		#movement_vector = 
		#identify if movement is diagonal, if so, bend nearest corner and move to an position orthogonal to it, then meet it
		pass
	return movement

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

	out = open(start_time + '.txt', 'w')
	for stat in log:
		stat.print_stats()
		str = stat.return_stats()
		out.write(str)

def main():
	vcm = VCM()
	tello = Tello()
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
	vcm.set_perimeter((-1,-2),(2,2))
	
	f = open(global_vars.filename, 'w')
	f.write("command\n")
	f.write("liftoff\n")
	f.close()	

	vcm.route_3d()
	print(vcm.traverse_order)

	drone_position = [vcm.traverse_order[0][0], 0]
	#print(drone_position)
	#print(vcm.nodemap[drone_position])
	tello.on_close()
	#for shelf_level in vcm.traverse_order:
	#	for node in shelf_level:
	#		dir, dst = movement_controller(traverse_order, shelf_level, node)
	#		#connection broker attempts to resend commands!
	#		connection_broker()


if __name__ == '__main__':
	main()