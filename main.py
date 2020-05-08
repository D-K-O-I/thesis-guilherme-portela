from vcm import VCM

def main():
	vcm = VCM()
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
	vcm.route_3d()

	#vcm.set_perimeter((0,0),(2,1))
	#vcm.get_nodemap()
	#vcm.rem_perimeter()
	#vcm.get_nodemap()

if __name__ == '__main__':
	main()