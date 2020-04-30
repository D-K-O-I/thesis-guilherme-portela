#Virtual Coordinates Map Management
#nodemap: dict(EPC: tag)
import operator
import math

DIMX = 9999.99
DIMY = 9999.99

class VCM:
	def __init__(self):
		self.nodemap = {}

	def add_node(self, epc, x, y):
		if epc in self.nodemap:
			while True:
				user_input = input("EPC already registered to node at " + str(self.nodemap[epc]) + ". Update this node's coordinates?\n [Y]es [N]o\n")
				if user_input == "Y":
					self.nodemap[epc] = (x,y)
					break
				elif user_input == "N":
					break
		else:
			if (x,y) in self.nodemap.values():
				print("Coordinates already assigned to an EPC. Update that Coordinate or choose a different Coordinate to add.")
			else:
				self.nodemap[epc] = (x,y)

	def del_node(self, epc):
		del self.nodemap[epc]

	def get_nodemap(self):
		return self.nodemap


	def find_neighbours(self, cpos):
		#Finds neighbouring nodes orthogonally
		nm = {}

		#Positive X
		temp = tuple(map(operator.add, cpos, (1,0)))
		if  temp in self.nodemap.values():
			temp_n = [k for k,v in self.nodemap.items() if v == temp]
			#print(temp_n)
			for neighbour in temp_n:
				nm[neighbour] = self.nodemap[neighbour]
		#Positive Y
		temp = tuple(map(operator.add, cpos, (0,1)))
		if  temp in self.nodemap.values():
			temp_n = [k for k,v in self.nodemap.items() if v == temp]
			#print(temp_n)
			for neighbour in temp_n:
				nm[neighbour] = self.nodemap[neighbour]
		#Negative X
		temp = tuple(map(operator.add, cpos, (-1,0)))
		if  temp in self.nodemap.values():
			temp_n = [k for k,v in self.nodemap.items() if v == temp]
			#print(temp_n)
			for neighbour in temp_n:
				nm[neighbour] = self.nodemap[neighbour]
		#Negative Y
		temp = tuple(map(operator.add, cpos, (0,-1)))
		if  temp in self.nodemap.values():
			temp_n = [k for k,v in self.nodemap.items() if v == temp]
			#print(temp_n)
			for neighbour in temp_n:
				nm[neighbour] = self.nodemap[neighbour]

		return nm

	def route(self):
		#Current Goal: Form a Minimum spanning tree by for the shortest LONGEST PATH
		#The drone must cross ALL minweight edges and the minimum number of maxweight edges
		#Then, it must return to its starting position according to Djikstra's Shortest Path Theorem
		#Orientation: Orthogonal, with X being maxweight and Y being minweight
		self.current_pos = (0,0) #arbitrary
		self.start_pos = self.current_pos
		self.spanning_tree_reached = []
		self.spanning_tree_unreached = list(self.nodemap)
		#add start_pos vector to reached, del for unreached
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

			print("Reached VS Unreached")
			print(self.spanning_tree_reached)
			print(self.spanning_tree_unreached)
			
			
			record = 9999.99
			
			for candidate in candidatelist:
				
				#calculate vector to candidate
				effort = (abs(self.current_pos[0] - self.nodemap[candidate][0]), abs(self.current_pos[1] - self.nodemap[candidate][1]))
				# calculate hypotenuse to candidate
				effort_h_sq = ((effort[0]*self.maxweight)**2) + ((effort[1]*self.minweight)**2)
				effort_final = math.sqrt(effort_h_sq)
				#print(candidate + " -> " + str(effort_final))
				
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
					if self.nodemap[candidate][0] == self.nodemap[answer][0] and self.current_pos[0] == self.nodemap[candidate][0]:
						#pick shortest extremity to minimize aisle-travel time
						for unreached in self.spanning_tree_unreached:
							if self.nodemap[unreached][0] == self.current_pos[0]:
								count += 1
								if self.nodemap[unreached][1] > self.nodemap[candidate][1] and self.nodemap[unreached][1] > max:
									max = self.nodemap[unreached][1]
								elif self.nodemap[unreached][1] < self.nodemap[candidate][1] and self.nodemap[unreached][1] < min:
									min = self.nodemap[unreached][1]
						
						#by default or if shortest, head North (positive Y)
						if abs(max) <= abs(min):
							answer_coord = tuple(map(operator.add, self.current_pos, (0,int(self.minweight))))
							answerp = [k for k,v in self.nodemap.items() if v == answer_coord]
							#print(answerp)
							answer = answerp.pop(0)
						#if shortest, head South (negative Y)
						elif abs(max) > abs(min):
							answer_coord = tuple(map(operator.add, self.current_pos, (0,-int(self.minweight))))
							answerp = [k for k,v in self.nodemap.items() if v == answer_coord]
							#print(answerp)
							answer = answerp.pop(0)
						
					else:	
						#compare candidate with answer for row, always pick West (negative X) if possible
						if self.nodemap[answer][0] > self.nodemap[candidate][0]:
							answer = candidate

			self.spanning_tree_reached.append(answer)
			del self.spanning_tree_unreached[self.spanning_tree_unreached.index(answer)]

			self.current_pos = self.nodemap[self.spanning_tree_reached[-1]]
			currentpos_node = [k for k,v in self.nodemap.items() if v == self.current_pos]
			print("Moved to: " + str(currentpos_node) + str(self.current_pos))

		#return sequence
		#self.spanning_tree_reached.append(self.spanning_tree_reached[0])

		print("Done! Route: " + str(self.spanning_tree_reached))

			
			