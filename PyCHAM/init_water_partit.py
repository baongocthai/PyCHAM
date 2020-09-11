'''function to estimate the initial concentration of water on particles and walls'''

import numpy as np
from partit_var import kimt_calc
import ipdb
from mov_cen_water_eq import mov_cen_main as movcen # moving centre method for rebinning
import sys
import matplotlib.pyplot as plt
import scipy.constants as si

def init_water_partit(x, y, H2Oi, Psat, mfp, num_sb, num_speci, 
			accom_coeff, y_mw, surfT, R_gas, TEMP, NA, y_dens, 
			N_perbin, DStar_org, RH, core_diss, Varr, Vbou, Vol0, MV,
			therm_sp, Cw, kgwt, corei, act_coeff, wall_on):

	# inputs: ------------------------------------------------------
	# x - radius of particles per size bin (um)
	# Psat - saturation vapour pressure of components (molecules/cc (air))
	# N_perbin - initial particle concentration (#/cc (air))
	# therm_sp - thermal speed of components (m/s) (num_speci)
	# Cw - concentration of wall (molecules/cc (air))
	# kgwt - mass transfer coefficient for vapour-wall partitioning (/s)
	# corei - index of core component
	# act_coeff - activity coefficients of components (dimensionless)
	# wall_on - marker for whether to consider wall
	# --------------------------------------------------------------
	

	if sum(N_perbin)>0.0: # if seed particles present
		# new array of size bin radii (um)
		print('Equilibrating water in vapour with water in seed particles')

		for sbstep in range(len(x)): # loop through size bins
			if N_perbin[sbstep]<1.0e-10: # no need to partition if no particle present
				continue
			
			# partitioning coefficient and kelvin factor
			[kimt, kelv_fac] = kimt_calc(y, mfp, num_sb, num_speci, accom_coeff, y_mw,   
								surfT, R_gas, TEMP, NA, y_dens, N_perbin, DStar_org, 
								x.reshape(1, -1)*1.0e-6, Psat, therm_sp, 
								H2Oi, act_coeff, wall_on, 0)

			# get core properties
			# concentration (molecules/cc (air))
			ycore = y[num_speci*(sbstep+1)+corei]*core_diss
			
			# first guess of particle-phase water concentration based on RH = mole 
			# fraction (molecules/cc (air))
			y[num_speci*(sbstep+1)+H2Oi] = (ycore/kelv_fac[sbstep])*RH
			
			# gas phase concentration of water (molecules/cc (air)), will stay constant
			# because RH is constant
			Cgit = y[H2Oi]
			
			# concentration of water at particle surface in gas phase (molecules/cc (air))
			Wc_surf = y[num_speci*(sbstep+1)+H2Oi]
			
			# total particle surface gas-phase concentration of all species 
			# (molecules/cc (air)):
			conc_sum = (np.sum(y[num_speci*(sbstep+1):num_speci*(sbstep+2)]))
			# account for core dissociation constant
			conc_sum = (conc_sum-y[num_speci*(sbstep+1)+corei]+
							(y[num_speci*(sbstep+1)+corei]*core_diss))
			
			# partitioning coefficient and kelvin factor
			[kimt, kelv_fac] = kimt_calc(y, mfp, num_sb, num_speci, accom_coeff, y_mw,   
								surfT, R_gas, TEMP, NA, y_dens, N_perbin, DStar_org, 
								x.reshape(1, -1)*1.0e-6, Psat, therm_sp, 
								H2Oi, act_coeff, wall_on, 0)

			Csit = (Wc_surf/conc_sum)*Psat[0, H2Oi]*kelv_fac[sbstep, 0]
			
			y0 = np.zeros(len(y))
			y0[:] = y[:] # initial concentration before moving centre (molecules/cc (air))
			y00 = np.zeros(len(y))
			y00[:] = y[:] # initial concentration before iteration (molecules/cc (air))
			dydtfac = 1.0e-1
			dydt0 = 0 # change in water concentration (molecules/cc) on previous iteration
			
			while np.abs(Cgit-Csit)>Cgit/1.0e6:
				
				y0[:] = y[:] # update initial concentrations (molecules/cc (air))
				
				# new particle size, required to update kelvin factor and partitioning
				# coefficient in kimt_calc below 
				# number of moles of each component in a single particle (mol/cc (air))
				nmolC= ((y[num_speci*(sbstep+1):num_speci*(sbstep+2)]/(si.Avogadro*N_perbin[sbstep])))
				# new radius of single particle per size bin (um) including volume of 
				# water
				Vnew = np.sum(nmolC*MV*1.0e12)
				x[sbstep] = ((3.0/(4.0*np.pi))*Vnew)**(1.0/3.0)
				
				# update partitioning coefficients
				[kimt, kelv_fac] = kimt_calc(y, mfp, num_sb, num_speci, accom_coeff, y_mw,   
								surfT, R_gas, TEMP, NA, y_dens, N_perbin, DStar_org, 
								x.reshape(1, -1)*1.0e-6, Psat, therm_sp, 
								H2Oi, act_coeff, wall_on, 0)
				
				# concentration of water at particle surface in gas phase 
				# (molecules/cc (air))
				Wc_surf = y[num_speci*(sbstep+1)+H2Oi]
				
				# total particle surface gas-phase concentration of all species 
				# (molecules/cc (air)):
				conc_sum = (np.sum(y[num_speci*(sbstep+1):num_speci*(sbstep+2)]))
				
				# account for core dissociation constant
				conc_sum = (conc_sum-y[num_speci*(sbstep+1)+corei]+
								(y[num_speci*(sbstep+1)+corei]*core_diss))
				
				Csit = (Wc_surf/conc_sum)*Psat[0, H2Oi]*kelv_fac[sbstep, 0]*act_coeff[0, H2Oi]
		
				
				dydt = kimt[sbstep, H2Oi]*(Cgit-Csit) # partitioning rate (molecules/cc.s)
				dydtn = dydt*(dydtfac*RH*x[sbstep]**3.0)
				dydtn = dydt*(dydtfac*RH*x[sbstep]**3.0)/kelv_fac[sbstep, 0]
				
				# new estimate of concentration of condensed water (molecules/cc (air))
				y[num_speci*(sbstep+1)+H2Oi] += dydtn
				# if iteration becomes unstable, reset and reduce change per step
				if ((np.sum(y[num_speci*(sbstep+1):num_speci*(sbstep+2)]))<0.0):
					# return to first guess before iteration on this size bin began
					y[:] = y00[:]
					dydtfac = dydtfac/2.0
				# if iteration oscillates, reduce change per step
				if dydt0<0 and dydtn>0:
					dydtfac = dydtfac/2.0
				
				# remember change in this step
				dydt0 = dydtn
				
			
			sbstep += 1

		# call on the moving centre method for redistributing particles that have grown 
		# beyond their upper size bin boundary due to water condensation, note, only do this
		# after the iteration per size bin when we know the new particle-phase concentration 
		# of water
	
		(N_perbin, Varr, y[num_speci:-num_speci], x, redt, blank, tnew) = movcen(N_perbin, Vbou, 
		np.transpose(y[num_speci:-num_speci].reshape(num_sb-1, num_speci)), 
		(np.squeeze(y_dens*1.0e-3)), num_sb-1, num_speci, y_mw, Vol0, 0.0,
		0, MV)
	
		if redt == 1: # check on whether exception raised by moving centre
			print('Error whilst equilibrating seed particles with water vapour (inside init_water_partit module).  Please investigate, perhaps by checking rh and pconc inputs in model variables input file.  See README for guidance and how to report bugs.')
			sys.exit()
	

	if kgwt>1.0e-10 and Cw>0.0:
		print('Equilibrating water in vapour with water on wall')
	
		# first guess of wall-phase water concentration based on RH = mole 
		# fraction (molecules/cc (air))
		y[num_speci*num_sb+H2Oi] = Cw*RH
		

		# allow gas-phase water to equilibrate with walls
		while np.abs(y[H2Oi]-Psat[0, H2Oi]*((y[num_speci*(num_sb)+H2Oi]/Cw))*act_coeff[0, H2Oi])>1.0e2:
			
			# concentration of water at wall surface in gas phase (molecules/cc (air))
			Csit = y[num_speci*num_sb:num_speci*(num_sb+1)]
			Csit = (Psat[0, :]*(Csit/Cw)*act_coeff[0, H2Oi]) # with Raoult term
			
			
			dydt = y[H2Oi]-Csit[H2Oi] # distance from equilibrium (molecules/cc)

			dydt = ((dydt/Psat[0, H2Oi])*Cw)/2.0

			# new estimate of concentration of condensed water (molecules/cc (air))
			y[num_speci*(num_sb)+H2Oi] += dydt
			
	print('Finished initiating water condensation')
	
	return(y, Varr, x, N_perbin)
