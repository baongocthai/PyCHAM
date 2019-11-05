# function to test the PyCHAM.py module
# set path to the PyCHAM folder
import os
import sys
dirpath = os.getcwd() # get current path
sys.path.append(os.path.split(dirpath)[0]) # add path to system path

if os.path.isfile(os.path.split(dirpath)[0]+'/PyCHAM.py') == 1:
	print('PyCHAM.py exists, now importing and calling as in __main__.py')
	print('to test the PyCHAM.py module, please follow the instructions below:')
	print('first, set the test variable in inputs/Example_Run_inputs.txt to = 1')
	print('if working, a graphical user interface (GUI) will show next, requesting user inputs')
	print('for the requested inputs, please select the following:')
	print('for "Chemical Scheme .txt File" select inputs/Example_Run.txt')
	print('for "Chemical Scheme .txt File" select inputs/Example_Run_xml.xml')
	print('for "Model Variables .txt File" select inputs/Example_Run_inputs.txt')
	print('please select the "Run Model" button')
	print('to finish the test select the "Plot Results" button')
	from PyCHAM import PyCHAM
	PyCHAM()
	

else:
	print('PyCHAM.py does not exist in the expected path, which is: ', (os.path.split(dirpath)[0]+'/PyCHAM.py'))
	exit()