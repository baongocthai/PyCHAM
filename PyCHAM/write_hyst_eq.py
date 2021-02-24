'''module to write the equations for hysteresis behaviour of particle-phase water with respect to temperature'''
# writes the hyst_eq module based on the user inputs

import datetime

# define function
def write_hyst_eq(drh_str, erh_str):

	# inputs: ----------------------------------------------
	# drh_str - string from user inputs describing 
	#	deliquescence RH (fraction 0-1) as function of temperature (K)
	# erh_str - string from user inputs describing 
	#	efflorescence RH (fraction 0-1) as function of temperature (K)
	# --------------------------------------------------------
	
	# create new  file - will contain module for both deliquescence and efflorescence
	f = open('PyCHAM/hyst_eq.py', mode='w')
	
	f.write('\'\'\'solution of deliquescence and efflorescence RH, generated by eqn_pars.py in fully functioning mode, or by ui_check.py in testing mode\'\'\'\n')
	f.write('# module to estimate deliquescence and efflorescence relative humidity as a function of temperature\n')
	f.write('# File Created at %s\n' %(datetime.datetime.now()))	
	f.write('\n')
	f.write('# function for deliquescence\n')
	f.write('def drh(TEMP):\n')
	f.write('	\n')
	f.write('	# inputs: -----------------\n')
	f.write('	# TEMP - temperature in chamber (K)\n')
	f.write('	# ---------------------------\n')
	f.write('	\n')
	f.write('	# deliquescence relative humidity (fraction 0-1)\n')
	f.write('	DRH = %s\n' %drh_str)
	f.write('	return(DRH)\n')
	f.write('\n')
	f.write('# function for efflorescence\n')
	f.write('def erh(TEMP):\n')
	f.write('	\n')
	f.write('	# inputs: -----------------\n')
	f.write('	# TEMP - temperature in chamber (K)\n')
	f.write('	# ---------------------------\n')
	f.write('	\n')
	f.write('	# efflorescence relative humidity (fraction 0-1)\n')
	f.write('	ERH = %s\n' %erh_str)
	f.write('	return(ERH)\n')
	f.close() # close file
	
	return()