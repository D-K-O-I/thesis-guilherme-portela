from tello import Tello

global tello
global filename
global flag_return
global logfile
global filename_test

tello = Tello()
filename = "command_entry.txt"
filename_test = "command_entry_graphs.txt"
flag_return = False
flag_reroute = False
logfile = ""