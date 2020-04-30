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
	vcm.route()

if __name__ == '__main__':
	main()