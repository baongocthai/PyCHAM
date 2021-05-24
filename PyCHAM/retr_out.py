'''code to open saved PyCHAM files and return useful variables'''
# called by PyCHAM plotting codes to obtain the required model outputs for evaluation

import numpy as np
import os

def retr_out(output_by_sim):
	
	# inputs: -------------------------------
	# output_by_sim - name of folder requested by the calling code to be looked at
	# ---------------------------------------
	
	# name of file where experiment constants saved
	fname = str(output_by_sim + '/model_and_component_constants')
	const_in = open(fname)

	const = {} # prepare to create dictionary
	for line in const_in.readlines():
		
		dlist = [] # prepare to convert to python list
		for i in line.split(',')[1::]:
			
			if str(line.split(',')[0]) == 'number_of_size_bins':
				dlist.append(int(i))
			if str(line.split(',')[0]) == 'number_of_components' or str(line.split(',')[0]) == 'wall_on_flag_0forNO_1forYES':
				dlist.append(int(i))
			if str(line.split(',')[0]) == 'molecular_weights_g/mol_corresponding_to_component_names' or  str(line.split(',')[0]) == 'molecular_volumes_cm3/mol' or  str(line.split(',')[0]) == 'molar_volumes_cm3/mol':
				i = i.strip('\n')
				i = i.strip('[')
				i = i.strip(']')
				i = i.strip(' ')
				dlist.append(float(i))
			if (str(line.split(',')[0]) == 'pure_component_saturation_vapour_pressures_at_298.15K'):
				i = i.strip('\n')
				i = i.strip('[[')
				i = i.strip(']]')
				i = i.strip('[')
				i = i.strip(']')
				i = i.strip(' ')
				dlist.append(float(i))
			if (str(line.split(',')[0]) == 'organic_peroxy_radical_index'):
				i = i.strip('\n')
				i = i.strip(' ')
				i = i.strip('[[')
				i = i.strip(']]')
				i = i.strip('[')
				i = i.strip(']')
				i = i.strip(' ')
				dlist.append(int(i))
			if (str(line.split(',')[0]) == 'oxygen_to_carbon_ratios_of_components'):
				i = i.strip('\n')
				i = i.strip('[[')
				i = i.strip(']]')
				i = i.strip('[')
				i = i.strip(']')
				i = i.strip(' ')
				dlist.append(float(i))
			if (str(line.split(',')[0]) == 'index_of_water'):
				i = i.strip('\n')
				i = i.strip('[[')
				i = i.strip(']]')
				i = i.strip('[')
				i = i.strip(']')
				i = i.strip(' ')
				dlist.append(int(i))
			if (str(line.split(',')[0]) == 'index_of_seed_components'):
				i = i.strip('\n')
				i = i.strip('[[')
				i = i.strip(']]')
				i = i.strip('[')
				i = i.strip(']')
				i = i.strip(' ')
				dlist.append(int(i))
			if (str(line.split(',')[0]) == 'chem_scheme_names') or (str(line.split(',')[0]) == 'SMILES') or (str(line.split(',')[0]) == 'space_mode'):
				i = i.strip('\n')
				i = i.strip('[')
				i = i.strip(']')
				i = i.strip(' ')
				i = i.strip('\'')
				dlist.append(str(i))
			if str(line.split(',')[0]) == 'factor_for_multiplying_ppb_to_get_molec/cm3_with_time':
				i = i.strip('\n')
				i = i.strip(' ')				
				i = i.strip('[[')
				i = i.strip('[')
				i = i.strip(']')
				dlist.append(float(i))
			if str(line.split(',')[0]) == 'simulation_computer_time(s)':
				i = i.strip('\n')
				i = i.strip('[')
				i = i.strip(']')
				i = i.strip(' ')
				dlist.append(float(i))
			if (str(line.split(',')[0]) == 'size_structure_0_for_moving_centre_1_for_full_moving'):
				i = i.strip('\n')
				i = i.strip('[[')
				i = i.strip(']]')
				i = i.strip('[')
				i = i.strip(']')
				i = i.strip(' ')
				dlist.append(int(i))
			
			
		const[str(line.split(',')[0])] = dlist
	const_in.close()
	
	# extract required data from dictionary, note this prepared above
	num_sb = int((const['number_of_size_bins'])[0]) # number of size bins
	num_comp = int((const['number_of_components'])[0]) # number of components
	# conversion factor to change gas-phase concentrations from molecules/cc 
	# (air) into ppb 
	Cfactor = const['factor_for_multiplying_ppb_to_get_molec/cm3_with_time']
	rel_SMILES = const['SMILES']
	y_MW = const['molecular_weights_g/mol_corresponding_to_component_names']
	comp_names = const['chem_scheme_names']
	wall_on = const['wall_on_flag_0forNO_1forYES'][0]
	space_mode = const['space_mode'][0]
	# pure component saturation vapour pressures at 298.15 K (log10(atm))
	PsatPa = const['pure_component_saturation_vapour_pressures_at_298.15K']
	# pure component saturation vapour pressures at 298.15 K (log10(atm))
	OC = const['oxygen_to_carbon_ratios_of_components']
	H2Oi = int((const['index_of_water'])[0]) # index of water
	
	seedi = const['index_of_seed_components'] # index of seed components
	siz_str = const['size_structure_0_for_moving_centre_1_for_full_moving']
	
	try:
		MV = const["molecular_volumes_cm3/mol"]
	except:
		MV = const["molar_volumes_cm3/mol"]

	try:
		speed = (const["simulation_computer_time(s)"])[0]
	except:
		speed = 0.
	
	try: # indices of organic peroxy radical components
		RO2i = const['organic_peroxy_radical_index']
	except:
		RO2i = []
	
	# withdraw index and names of components to plot the gas-phase concentration temporal profile of
	fname = str(output_by_sim+'/components_with_initial_gas_phase_concentrations_specified')
	if (os.stat(fname).st_size > 120): # if file contains more than just the header
		indx_plot = np.loadtxt(fname, delimiter=',', skiprows=1, dtype='str')
		# chemical scheme names of components
		comp0 = indx_plot[1].tolist()
		# indices of components
		indx_plot = indx_plot[0].tolist()
		indx_plot = [int(i) for i in indx_plot]
	else:
		comp0 = []
		indx_plot = []

	# withdraw times (s)
	fname = str(output_by_sim+'/time')
	t_array = np.loadtxt(fname, delimiter=',', skiprows=1)
	timehr = t_array/3600.0 # convert from s to hr
	
	try: # this output added on 23/02/2021
		# withdraw chamber environmental conditions (s)
		fname = str(output_by_sim+'/chamber_environmental_conditions')
		cham_env = np.loadtxt(fname, delimiter=',', skiprows=1)
	except:
		cham_env = []
	
	# withdraw concentrations
	fname = str(output_by_sim+'/concentrations_all_components_all_times_gas_particle_wall')
	y = np.loadtxt(fname, delimiter=',', skiprows=1)
	
	# following will only load for certain simulation setups (mostly whether particles included)
	
	try:
		# withdraw the wall concentration of components due to particle deposition to wall
		fname = str(output_by_sim+'/concentrations_all_components_all_times_on_wall_due_to_particle_deposition_to_wall')
		yrec_p2w = np.loadtxt(fname, delimiter = ',', skiprows = 2)
	except:
		yrec_p2w = []
	
	try:
		# withdraw number-size distributions (# particles/cc (air))
		fname = str(output_by_sim+'/particle_number_concentration_dry')
		N = np.loadtxt(fname, delimiter=',', skiprows=1)
		if ((num_sb-wall_on) == 1): # if just one size bin, ensure two dimensions
			N = N.reshape(-1, 1)
	except:
		N = []
	
	try:
		# withdraw number-size distributions (# particles/cc (air))
		fname = str(output_by_sim+'/particle_number_concentration_wet')
		Nwet = np.loadtxt(fname, delimiter=',', skiprows=1)
		if ((num_sb-wall_on) == 1): # if just one size bin, ensure two dimensions
			Nwet = Nwet.reshape(-1, 1)
	except:
		Nwet = []
	
	try:
		# particle sizes (um)
		fname = str(output_by_sim+'/size_bin_radius')
		x = np.loadtxt(fname, delimiter=',', skiprows=1) # skiprows=1 omits header
	except:
		x = []

	try:
		# particle size bin bounds (radii) (um3)
		fname = str(output_by_sim+'/size_bin_bounds')
		rbou_rec = np.loadtxt(fname, delimiter=',', skiprows=1) # skiprows=1 omits header
	except:
		rbou_rec = []
	
	return(num_sb, num_comp, Cfactor, y, N, rbou_rec, x, timehr, rel_SMILES, y_MW, 
		Nwet, comp_names, MV, speed, wall_on, space_mode, indx_plot, comp0, 
		yrec_p2w, PsatPa, OC, H2Oi, seedi, siz_str, cham_env, RO2i)

def retr_out_noncsv(output_by_sim, comp_of_int): # similar to above function but for when non-csv files need interrogating
	
	import netCDF4 as nc # for EASY outputs
	
	# inputs: -------------------------------
	# output_by_sim - name of folders requested by the calling code to be looked at
	# comp_of_int - components of interest
	# ---------------------------------------
	
	# if a .dat file used (e.g. FACSIMILE output)
	if (output_by_sim[-4::] == '.dat'):
	
		datafile = open(output_by_sim)
	
		# flag stating whether column titles yet reached
		col_title = 0
		data_cnt = -1 # count on lines of data
		
		# prepare to create dictionary containing component names, times and concentrations
		data_dic = {}
		for line in datafile.readlines():
		
			dlist = [] # prepare to convert to python list
		
			if (col_title == 2): # ready to read in concentrations and times
				data_cnt += 1 # count on lines of data
		
			# loop through sections of line separated by a space
			for i in line.split(' '):
				
				if (i == ''): # ignore spaces
					continue
				if (i == 'PRINT'): # identifier for header
					break # skip header
				if (i == 'TIME'): # column titles
					col_title = 1 # flag that column titles being read
				if (col_title == 1):
					if str(i)[-1::] == '\n': # in case new line symbol included
						i = str(i)[0:-1]
					dlist.append(str(i)) # list column headers
				if (col_title == 2): # ready to read in concentrations and times
					dlist.append(float(i))
			
			if (col_title == 2):
				data_dic[str('data'+str(data_cnt))] = dlist
			if (col_title == 1):
				data_dic['col_title'] = dlist
				col_title = 2 # ready to read in concentrations and times
			
	
		# extract times (s), component names and concentrations with time (molecules/cm3)
		# from dictionary
		comp_names = [i for i in data_dic['col_title'][1::]]
	
		Crec = np.zeros((data_cnt+1, len(comp_names))) # empty array for concentrations with time (molecules/cm3)
		time_s = np.zeros((data_cnt+1, 1)) # empty array for times (s)
	
		for key in data_dic: # loop through dictionary keys
			if (key[0:4] == 'data'): # if this a useful entry
				rn = int(key[4::])# get row number
				time_s[rn] = data_dic[key][0] # times (s)
				Crec[rn, :] = data_dic[key][1::] # concentrations with time (molecules/cm3)
	
		
		return(time_s, comp_names, Crec)
	
	# if a .nc file used (e.g. EASY output)
	if (output_by_sim[-3::] == '.nc'):
		
		ds = nc.Dataset(output_by_sim) # open file
		
		time_s = ds['time'][:] # get time (seconds)
		
		# empty array ready for component concentrations (molecules/cm3)
		Crec = np.zeros((len(time_s), len(comp_of_int)))
		
		# retrieve concentrations (molecules/cm3) of components of interest
		c_cnt = 0 # count on components
		for comp_name in comp_of_int:
			Crec[:, c_cnt] = ds[str(comp_name+'_0')][:]
			c_cnt += 1 # count on components
			
		return(time_s, comp_of_int, Crec)
		
	else: # if file type unrecognised return fillers
		return([], [], [])