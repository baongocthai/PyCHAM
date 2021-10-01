'''solution of ODEs, generated by eqn_pars.py'''
# module to solve system of ordinary differential equations (ODEs) using solve_ivp of Scipy 
# File Created at 2021-10-01 13:05:54.917289

import numpy as np
import scipy.sparse as SP
from scipy.integrate import solve_ivp

# define function
def ode_solv(y, integ_step, rindx, pindx, rstoi, pstoi, 
	nreac, nprod, rrc, jac_stoi, njac, jac_den_indx, 
	jac_indx, Cinfl_now, y_arr, y_rind, uni_y_rind, 
	y_pind, uni_y_pind, reac_col, prod_col, 
	rstoi_flat, pstoi_flat, rr_arr, rr_arr_p,
	rowvals, colptrs, num_comp, num_sb,
	wall_on, Psat, Cw, act_coeff, kw, jac_wall_indx,
	seedi, core_diss, kelv_fac, kimt, num_asb,
	jac_part_indx, jac_extr_indx,
	rindx_aq, pindx_aq, rstoi_aq, pstoi_aq,
	nreac_aq, nprod_aq, jac_stoi_aq, njac_aq, jac_den_indx_aq, jac_indx_aq,
	y_arr_aq, y_rind_aq, uni_y_rind_aq, y_pind_aq, uni_y_pind_aq,
	reac_col_aq, prod_col_aq, rstoi_flat_aq,
	pstoi_flat_aq, rr_arr_aq, rr_arr_p_aq, eqn_num, jac_mod_len,
	jac_part_hmf_indx, rw_indx, N_perbin, jac_part_H2O_indx,
	H2Oi, dil_fac, RO2_indx, comp_namelist, Psat_Pa, Cinfl_nowp_indx,
	Cinfl_nowp):

	# inputs: -------------------------------------
	# y - initial concentrations (# molecules/cm3)
	# integ_step - the maximum integration time step (s)
	# rindx - index of reactants per equation
	# pindx - index of products per equation
	# rstoi - stoichiometry of reactants
	# pstoi - stoichiometry of products
	# nreac - number of reactants per equation
	# nprod - number of products per equation
	# rrc - reaction rate coefficient
	# jac_stoi - stoichiometries relevant to Jacobian
	# njac - number of Jacobian elements affected per equation
	# jac_den_indx - index of component denominators for Jacobian
	# jac_indx - index of Jacobian to place elements per equation (rows)
	# Cinfl_now - influx of components with continuous influx 
	#		(# molecules/cm3/s)
	# y_arr - index for matrix used to arrange concentrations of gas-phase reactants, 
	#	enabling calculation of reaction rate coefficients 
	# y_rind - index of y relating to reactants for reaction rate 
	# 	coefficient equation
	# uni_y_rind - unique index of reactants 
	# y_pind - index of y relating to products
	# uni_y_pind - unique index of products 
	# reac_col - column indices for sparse matrix of reaction losses
	# prod_col - column indices for sparse matrix of production gains
	# rstoi_flat - 1D array of reactant stoichiometries per equation
	# pstoi_flat - 1D array of product stoichiometries per equation
	# rr_arr - index for reaction rates to allow reactant loss
	# 	calculation
	# rr_arr_p - index for reaction rates to allow reactant loss
	# 	calculation
	# rowvals - row indices of Jacobian elements
	# colptrs - indices of  rowvals corresponding to each column of the
	# 	Jacobian
	# num_comp - number of components
	# num_sb - number of size bins
	# wall_on - flag saying whether to include wall partitioning
	# Psat - pure component saturation vapour pressures (molecules/cc)
	# Cw - effective absorbing mass concentration of wall (molecules/cc) 
	# act_coeff - activity coefficient of components
	# kw - mass transfer coefficient to wall (/s)
	# jac_wall_indx - index of inputs to Jacobian by wall partitioning
	# seedi - index of seed material
	# core_diss - dissociation constant of seed material
	# kelv_fac - kelvin factor for particles
	# kimt - mass transfer coefficient for gas-particle partitioning (s)
	# num_asb - number of actual size bins (excluding wall)
	# jac_part_indx - index for sparse Jacobian for particle influence 
	# jac_extr_indx - index for sparse Jacobian for air extraction influence 
	# rindx_aq - index of aqueous-phase reactants 
	# eqn_num - number of gas- and aqueous-phase reactions 
	# jac_mod_len - modification length due to high fraction of component(s)
	# 	in particle phase
	# jac_part_hmf_indx - index of Jacobian affected by water
	#	 in the particle phase
	# rw_indx - indices of rows affected by water in particle phase
	# N_perbin - number concentration of particles per size bin (#/cc)
	# jac_part_H2O_indx - sparse Jacobian indices for the effect of
	#	particle-phase water on all other components
	# H2Oi - index for water
	# dil_fac - dilution factor for chamber (fraction of chamber air removed/s)
	# RO2_indx - index of organic peroxy radicals
	# comp_namelist - chemical scheme names of components
	# Psat_Pa - saturation vapour pressure of components (Pa) at starting
	#	temperature of chamber
	# Cinfl_nowp_indx - index of particle-phase components with continuous influx 
	# Cinfl_nowp - concentration (# molecules/cm3/s) of particle-phase components with
	#	continuous influx
	# ---------------------------------------------

	def dydt(t, y): # define the ODE(s)
		
		# inputs: ----------------
		# y - concentrations (# molecules/cm3), note when using
		#	scipy integrator solve_ivp, this should have shape
		#	(number of elements, 1)
		# t - time interval to integrate over (s)
		# ---------------------------------------------
		
		# ensure y is correct shape
		if (y.shape[1] > 1):
			y = y[:, 0].reshape(-1, 1)
		# empty array to hold rate of change per component
		dd = np.zeros((y.shape[0], 1))
		
		# gas-phase reactions -------------------------
		# empty array to hold relevant concentrations for
		# reaction rate coefficient calculation
		rrc_y = np.ones((rindx.shape[0]*rindx.shape[1]))
		rrc_y[y_arr] = y[y_rind, 0]
		rrc_y = rrc_y.reshape(rindx.shape[0], rindx.shape[1], order = 'C')
		# reaction rate (molecules/cc/s) 
		rr = rrc[0:rindx.shape[0]]*((rrc_y**rstoi).prod(axis=1))
		# loss of reactants
		data = rr[rr_arr]*rstoi_flat # prepare loss values
		# convert to sparse matrix
		loss = SP.csc_matrix((data, y_rind, reac_col))
		# register loss of reactants
		dd[uni_y_rind, 0] -= np.array((loss.sum(axis = 1))[uni_y_rind])[:, 0]
		# gain of products
		data = rr[rr_arr_p]*pstoi_flat # prepare loss values
		# convert to sparse matrix
		loss = SP.csc_matrix((data, y_pind, prod_col))
		# register gain of products
		dd[uni_y_pind, 0] += np.array((loss.sum(axis = 1))[uni_y_pind])[:, 0]
		
		# gas-particle partitioning-----------------
		# transform particle phase concentrations into
		# size bins in rows, components in columns
		ymat = (y[num_comp:num_comp*(num_asb+1), 0]).reshape(num_asb, num_comp)
		# force all components in size bins with no particle to zero
		ymat[N_perbin[:, 0] == 0, :] = 0
		# total particle-phase concentration per size bin (molecules/cc (air))
		csum = ((ymat.sum(axis=1)-ymat[:, seedi].sum(axis=1))+((ymat[:, seedi]*core_diss).sum(axis=1)).reshape(-1)).reshape(-1, 1)
		# tile over components
		csum = np.tile(csum, [1, num_comp])
		# size bins with contents
		isb = (csum[:, 0] > 0.)
		
		if (any(isb)): # if particle-phase components present
			# container for gas-phase concentrations at particle surface
			Csit = np.zeros((num_asb, num_comp))
			# mole fraction of components at particle surface
			Csit[isb, :] = (ymat[isb, :]/csum[isb, :])
			# gas-phase concentration of components at
			# particle surface (molecules/cc (air))
			Csit[isb, :] = Csit[isb, :]*Psat[isb, :]*kelv_fac[isb]*act_coeff[isb, :]
			# partitioning rate (molecules/cc/s)
			dd_all = kimt*(y[0:num_comp, 0].reshape(1, -1)-Csit)
			# gas-phase change
			dd[0:num_comp, 0] -= dd_all.sum(axis=0)
			# particle change
			dd[num_comp:num_comp*(num_asb+1), 0] += (dd_all.flatten())
		
		# gas-wall partitioning ----------------
		# concentration on wall (molecules/cc (air))
		Csit = y[num_comp*(num_asb+1):num_comp*(num_asb+2), 0]
		# saturation vapour pressure on wall (molecules/cc (air))
		# note, just using the top rows of Psat and act_coeff
		# as do not need the repetitions over size bins
		if (Cw > 0.):
			Csit = Psat[0, :]*(Csit/Cw)*act_coeff[0, :]
			# rate of transfer (molecules/cm3/s)
			dd_all = kw*(y[0:num_comp, 0]-Csit)
			dd[0:num_comp, 0] -= dd_all # gas-phase change
			dd[num_comp*num_sb:num_comp*(num_sb+1), 0] += dd_all # wall change
		
		
		dd = (dd[:, 0]).reshape(num_sb+1, num_comp)
		# force all components in size bins with no particle to zero
		if (num_asb > 0):
			dd[1:num_asb+1, :][N_perbin[:, 0] == 0, :] = 0
		# return to array, note that consistent with the solve_ivp manual, this ensures dd is
		# a vector rather than matrix, since y0 is a vector
		dd = dd.flatten()
		return (dd)

	def jac(t, y): # define the Jacobian
		
		# inputs: ----------------
		# y - concentrations (molecules/cc), note when using scipy integrator solve_ivp, this should have shape (number of elements, 1)
		# t - time interval to integrate over (s)
		# ---------------------------------------------
		
		# ensure y is correct shape
		if (y.ndim == 2):
			if (y.shape[1] > 1):
				y = y[:, 0].reshape(-1, 1)
		if (y.ndim <= 1):
			y = y.reshape(-1, 1)
		
		# elements of sparse Jacobian matrix
		data = np.zeros((22389+jac_mod_len))
		
		for i in range(rindx.shape[0]): # gas-phase reaction loop
			# reaction rate (molecules/cc/s)
			rr = rrc[i]*(y[rindx[i, 0:nreac[i]], 0].prod())
			# prepare Jacobian inputs
			jac_coeff = np.zeros((njac[i, 0]))
			# only fill Jacobian if reaction rate sufficient
			if (rr != 0.):
				jac_coeff = (rr*(jac_stoi[i, 0:njac[i, 0]])/
				(y[jac_den_indx[i, 0:njac[i, 0]], 0]))
			data[jac_indx[i, 0:njac[i, 0]]] += jac_coeff
		
		
		# gas-particle partitioning
		part_eff = np.zeros((12623))
		if (sum(N_perbin[:, 0]) > 0.): # if any particles present 
			part_eff[0:4855:5] = -kimt.sum(axis=0) # effect of gas on gas
		
		# empty array for any particle-on-gas and particle-on-particle effects on water in the particle-phase for rows of Jacobian
		part_eff_rw = np.zeros((len(jac_part_hmf_indx)))
		# empty array for any particle-on-gas and particle-on-particle effects of water in the particle-phase on non-water components in the particle-phase for columns of Jacobian
		part_eff_cl = np.zeros((len(jac_part_H2O_indx)))
		# starting index for jacobian row inputs for effect on water
		sti_rw = 0 
		
		# transform particle phase concentrations into
		# size bins in rows, components in columns
		ymat = (y[num_comp:num_comp*(num_asb+1), 0]).reshape(num_asb, num_comp)
		ymat[N_perbin[:, 0] == 0, :] = 0 # ensure zero components where zero particles
		# total particle-phase concentration per size bin (molecules/cc (air))
		csum = ymat.sum(axis=1)-ymat[:, seedi].sum(axis=1)+(ymat[:, seedi]*core_diss).sum(axis=1)
		
		# effect of particle on gas
		for isb in range(int(num_asb)): # size bin loop
			if (csum[isb] > 0): # if components present in this size bin
				# effect of gas on particle
				part_eff[1+isb:num_comp*(num_asb+1):num_asb+1] = +kimt[isb, :]
				# start index
				sti = int((num_asb+1)*num_comp+isb*(num_comp*2))
				# diagonal index
				diag_indxg = sti+np.arange(0, num_comp*2, 2).astype('int')
				diag_indxp = sti+np.arange(1, num_comp*2, 2).astype('int')
				# prepare for diagonal (component effect on itself)
				diag = kimt[isb, :]*Psat[0, :]*act_coeff[0, :]*kelv_fac[isb, 0]*(-(csum[isb]-ymat[isb, :])/(csum[isb]**2.)) 
				# implement to part_eff
				part_eff[diag_indxg] -= diag
				part_eff[diag_indxp] += diag
				
				if (rw_indx[isb] > -1): # if water in this size bin 
					# prepare for row(s) (particle-phase non-water component effects on water in particle phase)
					rw = kimt[isb, rw_indx[isb]]*Psat[0, rw_indx[isb]]*act_coeff[0, rw_indx[isb]]*kelv_fac[isb, 0]*(-(-ymat[isb, rw_indx[isb]])/(csum[isb]**2.)) 
					# indices
					indxg = sti_rw+np.arange(0, ((num_comp-1)*2), 2).astype('int')
					indxp = sti_rw+np.arange(1, ((num_comp-1)*2), 2).astype('int')
					# implement to part_eff_rw
					part_eff_rw[indxg] -= rw
					part_eff_rw[indxp] += rw
					
					# prepare for column(s) (particle-phase water effect on non-water in particle phase)
					#cl = kimt[isb, :]*Psat[0, :]*act_coeff[0, :]*kelv_fac[isb, 0]*(-(-ymat[isb, :])/(csum[isb]**2.))
					#cl = np.zeros((num_comp))
					# remove water
					#cl = np.concatenate((cl[0:H2Oi], cl[H2Oi+1::]))
					#indxg = sti_rw+np.arange(0, (num_comp-1)).astype('int')
					#indxp = sti_rw+np.arange((num_comp-1), (num_comp-1)*2).astype('int')
					# implement to part_eff_cl
					#part_eff_cl[indxg] -= cl
					#part_eff_cl[indxp] += cl
					
					# starting index update
					sti_rw += (num_comp-1)*2
		
		data[jac_part_indx] += part_eff # diagonal
		data[jac_part_hmf_indx] += part_eff_rw # rows
		#data[jac_part_H2O_indx] += part_eff_cl # columns
		
		if (Cw > 0.):
			wall_eff = np.zeros((3884))
			wall_eff[0:1942:2] = -kw # effect of gas on gas 
			wall_eff[1:1942:2] = +kw # effect of gas on wall 
			# effect of wall on gas
			wall_eff[1942:3884:2] = +kw*(Psat[0,:]*act_coeff[0, :]/Cw) 
			# effect of wall on wall
			wall_eff[1942+1:3884:2] = -kw*(Psat[0,:]*act_coeff[0, :]/Cw) 
			data[jac_wall_indx] += wall_eff
		
		# create Jacobian
		j = SP.csc_matrix((data, rowvals, colptrs))
		
		return(j)
	
	# set ODE solver tolerances
	atol = 0.001
	rtol = 0.0001
	
	# check for underflow issues
	# reaction rate coefficient calculation
	#rrc_y = np.ones((rindx.shape[0]*rindx.shape[1]))
	#rrc_y[y_arr] = y[y_rind]
	#rrc_y = rrc_y.reshape(rindx.shape[0], rindx.shape[1], order = 'C')
	# reaction rate coefficient zeroed wherever product of reactant concentrations is zero (including where underflow causes zero, thereby preventing underflows breaking the solver which appears to be an issue on less powerful machines such as HP Spectre Folio) (/s) 
	#rrc[((rrc_y**rstoi).prod(axis=1)) == 0.0] = 0.
	
	# call on the ODE solver, note y contains the initial condition(s) (molecules/cc (air)) and must be 1D even though y in dydt and jac has shape (number of elements, 1)
	sol = solve_ivp(dydt, [0, integ_step], y, atol = atol, rtol = rtol, method = 'BDF', t_eval = [integ_step], vectorized = True, jac = jac)
	
	# force all components in size bins with no particle to zero
	y = np.squeeze(sol.y)
	y = y.reshape(num_sb+1, num_comp)
	if (num_asb > 0):
		y[1:num_asb+1, :][N_perbin[:, 0] == 0, :] = 0
	# return to array
	y = y.flatten()
	
	# return concentration(s) and time(s) following integration
	return(y, sol.t)
