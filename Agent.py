import numpy as np
import random
import math

class Agent:

	def __init__(self, agent_id=1, init_state="random_depth", ideal_phase=True, sync_dyn=False):
		# define logical parameters
		self._id = agent_id
		self._on_surface = False							# TODO: maybe better as a more general "comms_available" parameter
		#self._comms = comms  								# enable/disable inter-agent communications (TODO: add options for "continuous" vs. discrete/on-surface)
		self._sync_dyn = sync_dyn 							# enable/disable synchronizing dynamics

		# define physical parameters
		self._g = 9.81										# m/s^2; gravity
		self._m3 = 14.0 									# kg; vertical component of glider mass
		self._A = self._g / self._m3						# TODO
		self._B = 1.0										# TODO
		self._max_depth = 100.0								# meters; 

		# define trajectory parameters
		self._dive_time = 15.0									# minutes to reach max depth from surface
		self._omega = 2.0*math.pi / (60.0*2.0*self._dive_time)	# angular frequency of sinusoidal trajectory to track
		self._theta = 0.0										# rad; initial phase delay in periodic trajectory

		# initialize state
		self._state = self.set_init_state(init_state, sync_dyn)		# pos (m); vel (m/s); ballast mass (kg)
		self._theta = self.align_phase(ideal_phase)					# if set to true, sets ideal phase delay from inital depth 


	def update_state_via_dynamics(self, k, dt, K1=2, K2=1):
		# redefine important variables for readability
		z1_ = self._state[0]
		z2_ = self._state[1]
		u_ = self._state[2] 			# TODO: will need to add omega and theta to the state as these become variable

		# saturate position
		z1_ = min([0, z1_])

		A_ = self._A
		B_ = self._B
		D_ = self._max_depth
		omega_ = self._omega
		theta_ = self._theta

		# pre-compute terms in the state update
		err1_ = z1_ - (D_/2.0)*math.cos(omega_*k*dt + theta_) + (D_/2.0)
		err2_ = z2_ + (D_/2.0)*omega_*math.sin(omega_*k*dt + theta_)	
		rk2_ = -(D_/2.0)*(omega_**2)*math.cos(omega_*k*dt + theta_)
		uk_ = (1.0/A_)*( B_*abs(z2_)*z2_ + rk2_ - K1*err1_ -  K2*err2_ )

		# saturate ballast
		uk_ = max([-1.5, min([uk_, 1.5])])

		self._state[0] = z1_ + dt*z2_
		self._state[1] = z2_ + dt*(-B_*abs(z2_)*z2_  + A_*uk_)
		self._state[2] = uk_

		self.update_on_surface(self._state[0])

###
# HELPER FUNCTIONS
###
	
	def align_phase(self, ideal_phase):
		if ideal_phase:
			ang = (2.0*self._state[0] / self._max_depth) + 1.0 		# recovers ideal phase delay from initial depth (NOTE: depth must be negative)
			return math.acos(ang)

		else:
			return 0


	def set_init_state(self, init_state, sync_dyn=False):
		if sync_dyn == True:
			state_ = np.zeros((4,1))  		# pos, vel, ballast, phase delay
		else:
			state_ = np.zeros((3,1))		# pos, vel, ballast, phase delay

		if init_state == "random_depth":
			depth = -random.randint(0, math.floor(self._max_depth))
			state_[0] = float(depth);

		self.update_on_surface(state_[0])

		return state_


	def update_on_surface(self, depth):
		if depth > -2E-10:
			self._on_surface = True
		else:
			self._on_surface = False