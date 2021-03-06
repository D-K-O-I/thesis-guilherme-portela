#Virtual Coordinates Map Management
#nodemap: dict(EPC: tag)
import operator
import math
import global_vars

DIMX = 9999.99
DIMY = 9999.99
DIMH = 10

class VCM:
	def __init__(self):
		self.nodemap = {}
		self.nodemap_per = {}
		self.nodemap_hld = {}
		self.shelf_height = 2
		self.current_pos = (0,0) #arbitrary, definable
		self.traverse_order = [] #final routing path
		self.i = 0

	def upd_node(self):
		self.nodemap_hld = self.nodemap

	def add_node(self, epc, x, y):
		if epc in self.nodemap:
			while True:
				user_input = input("EPC already registered to node at " + str(self.nodemap[epc]) + ". Update this node's coordinates?\n [Y]es [N]o\n")
				if user_input == "Y":
					self.nodemap[epc] = (x,y)
					self.upd_node()
					break
				elif user_input == "N":
					break
		else:
			if (x,y) in self.nodemap.values():
				print("Coordinates already assigned to an EPC. Update that Coordinate or choose a different Coordinate to add.")
			else:
				self.nodemap[epc] = (x,y)
				self.upd_node()

	def del_node(self, epc):
		del self.nodemap[epc]
		self.upd_node()

	def get_nodemap(self):
		print(self.nodemap)
		return self.nodemap

	def set_perimeter(self, lower_bound, upper_bound):
	#receives 2 tuples (coordinates) to define its boundaries
	#defines boundaries (coordinate-wise) for the drone to stay in, affects _record_ variable
		if len(self.nodemap_per) != 0:
			self.rem_perimeter()

		for node in self.nodemap:
			if (self.nodemap.get(node)[0] >= lower_bound[0] and self.nodemap.get(node)[1] >= lower_bound[1]) and (self.nodemap.get(node)[0] <= upper_bound[0] and self.nodemap.get(node)[1] <= upper_bound[1]):
				self.nodemap_per[node] = self.nodemap.get(node)

		#print(self.nodemap_per)
		self.nodemap = self.nodemap_per
		#print(self.nodemap)
		print("New perimeter set.")
		return self.nodemap

	def rem_perimeter(self):
		print("Erased existing perimeter.")
		self.nodemap_per.clear()
		self.nodemap = self.nodemap_hld

	def coordinate_check(self,cpos,x,y):
		temp_nm = {}
		temp = tuple(map(operator.add, cpos, (x,y)))
		if  temp in self.nodemap.values():
			temp_n = [k for k,v in self.nodemap.items() if v == temp]
			#print(temp_n)
			for neighbour in temp_n:
				temp_nm[neighbour] = self.nodemap[neighbour]

		#Failsafe: if there is no immediate Y axis node, check its "next to kin" to determine if there is a shelf to be traversed
		else:
			temp = tuple(map(operator.add, cpos, (x,2*y)))
			if  temp in self.nodemap.values():
				temp_n = [k for k,v in self.nodemap.items() if v == temp]
				#print(temp_n)
				for neighbour in temp_n:
					temp_nm[neighbour] = self.nodemap[neighbour]
		return temp_nm

	def find_neighbours(self, cpos):
		#Finds neighbouring nodes orthogonally
		nm = {}
		for d in (self.coordinate_check(cpos,0,1), self.coordinate_check(cpos,0,-1), self.coordinate_check(cpos,1,0), self.coordinate_check(cpos,-1,0)):
			nm.update(d)

		return nm

	def route_3d(self):
		#TODO (main.py): add failsafe on timeout or re-route to get list of reached nodes for current shelf level;
		#use route_per_level and self.spanning_tree_reached as base
		while self.i <= self.shelf_height:
			route_per_level = self.route()
			self.traverse_order.append(route_per_level)
			print("END OF LEVEL")
			self.i+=1
		self.traverse_order[self.shelf_height].append(self.traverse_order[0][0])


	def route(self):
		#Current Goal: Form a Minimum spanning tree by for the shortest LONGEST PATH
		#The drone must cross ALL minweight edges and the minimum number of maxweight edges
		#Then, it must return to its starting position according to Djikstra's Shortest Path Theorem
		#Orientation: Orthogonal, with X being maxweight and Y being minweight

		#IMPORTANT: THIS ROUTE IS STRICTLY HORIZONTAL: to check several shelf levels, increase self.shelf_height
		#vertical movement is expensive, so the drone should only move upwards when necessary
		#The drone should perform one route() per level, after having reached all nodes

		
		if not global_vars.flag_reroute:
			self.start_pos = self.current_pos
			self.spanning_tree_reached = []
			self.spanning_tree_unreached = list(self.nodemap)
		else:
			self.start_pos = self.nodemap[spanning_tree_reached[-1]]
			global_vars.flag_reroute = False

		#add start_pos vector to reached, f for unreached
		temp = [k for k,v in self.nodemap.items() if v == self.start_pos]
		self.spanning_tree_reached = self.spanning_tree_reached + temp
		self.spanning_tree_unreached.remove(self.spanning_tree_reached[-1])

		self.maxweight = 3.0
		self.minweight = 1.0
		while len(self.spanning_tree_unreached) > 0:
			#Prim's approach
			#place edges into heap
			#pick lightest Y movement?
			#move key of node moved to into spanning tree reached, del from unreached

			#prepare candidate list from all reached nodes' neighbours
			candidatelist = []
			for reached in self.spanning_tree_reached:
				neighbourmap = self.find_neighbours(self.nodemap[reached])
				candidatelist += neighbourmap
			#print("Reached node neighbours:")
			#print(candidatelist)

			#remove duplicate candidate neighbours
			candidatelist = list(dict.fromkeys(candidatelist))
			#print("Removed duplicates:")
			#print(candidatelist)

			#remove already reached neighbours
			for reached_neighbour in sorted(self.spanning_tree_reached, reverse=True):
				if reached_neighbour in candidatelist:
					del candidatelist[candidatelist.index(reached_neighbour)]

			#print("Removed already reached nodes:")
			#print(candidatelist)

			#print("Reached VS Unreached")
			#print(self.spanning_tree_reached)
			#print(self.spanning_tree_unreached)
			
			
			record = 9999.99
			
			for candidate in candidatelist:
				#verification: if vector of (current_pos -> candidate) centered on current_pos exceeds DIMX or DIMY, it is discarded (candidate is poorly configured)
				misconfig_test = tuple(map(operator.add, self.current_pos, (self.nodemap[candidate][0],self.nodemap[candidate][1])))
				if misconfig_test[0] > DIMX or misconfig_test[1] > DIMY:
					#ignore this connection
					continue

				#calculate vector to candidate
				effort = (abs(self.current_pos[0] - self.nodemap[candidate][0]), abs(self.current_pos[1] - self.nodemap[candidate][1]))
				# calculate hypotenuse to candidate
				effort_h_sq = ((effort[0]*self.maxweight)**2) + ((effort[1]*self.minweight)**2)
				effort_final = math.sqrt(effort_h_sq)
				print(candidate + " -> " + str(effort_final))
				
				#select shortest path, single answer
				if effort_final < record:
					record = effort_final
					answer = candidate
				
				#select shortest path, two answers
				elif effort_final == record:
					max = 0
					min = 0
					count = 0
					
					#check if equality is aisle-related or due to different rows

					#aisle-related
					if self.nodemap[candidate][0] == self.nodemap[answer][0] and self.current_pos[0] == self.nodemap[candidate][0]:
						#pick shortest extremity to minimize aisle-travel time
						for unreached in self.spanning_tree_unreached:
							if self.nodemap[unreached][0] == self.current_pos[0]:
								count += 1
								if self.nodemap[unreached][1] >= self.nodemap[candidate][1] and self.nodemap[unreached][1] > max:
									max = self.nodemap[unreached][1]
								elif self.nodemap[unreached][1] <= self.nodemap[candidate][1] and self.nodemap[unreached][1] < min:
									min = self.nodemap[unreached][1]
						print(max,min)
						
						#by default or if shortest, head North (positive Y)
						if abs(max) <= abs(min):
							answer_coord = tuple(map(operator.add, self.current_pos, (0,int(self.minweight))))
							answerp = [k for k,v in self.nodemap.items() if v == answer_coord]
							#print(answerp)
							try:
								answer = answerp.pop(0)
							except:
								continue
						#if shortest, head South (negative Y)
						elif abs(max) > abs(min):
							answer_coord = tuple(map(operator.add, self.current_pos, (0,-int(self.minweight))))
							answerp = [k for k,v in self.nodemap.items() if v == answer_coord]
							#print(answerp)
							try:
								answer = answerp.pop(0)
							except:
								continue
					
					#different rows		
					else:	
						#pick shortest extremity to minimize aisle-travel time
						for unreached in self.spanning_tree_unreached:
							if self.nodemap[unreached][0] == self.current_pos[0]:
								count += 1
								if self.nodemap[unreached][0] >= self.nodemap[candidate][0] and self.nodemap[unreached][0] > max:
									max = self.nodemap[unreached][0]
								elif self.nodemap[unreached][0] <= self.nodemap[candidate][0] and self.nodemap[unreached][0] < min:
									min = self.nodemap[unreached][0]
						
						#if shortest, head East (positive X)
						if abs(max) < abs(min):
							answer_coord = tuple(map(operator.add, self.current_pos, (int(self.minweight),0)))
							answerp = [k for k,v in self.nodemap.items() if v == answer_coord]
							#print(answerp)
							try:
								answer = answerp.pop(0)
							except:
								continue
						#by default or if shortest, head West (negative X)
						elif abs(max) >= abs(min):
							answer_coord = tuple(map(operator.add, self.current_pos, (-int(self.minweight),0)))
							answerp = [k for k,v in self.nodemap.items() if v == answer_coord]
							#print(answerp)
							try:
								answer = answerp.pop(0)
							except:
								continue

			self.spanning_tree_reached.append(answer)
			del self.spanning_tree_unreached[self.spanning_tree_unreached.index(answer)]

			self.current_pos = self.nodemap[self.spanning_tree_reached[-1]]
			currentpos_node = [k for k,v in self.nodemap.items() if v == self.current_pos]
			print("Moved to: " + str(currentpos_node) + str(self.current_pos))

		#return sequence
		#self.spanning_tree_reached.append(self.spanning_tree_reached[0])

		print("Done! Route: " + str(self.spanning_tree_reached))
		return(self.spanning_tree_reached)
			
			