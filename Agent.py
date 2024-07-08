from AgentStateMachine import AgentStateMachine
from Sync import Sync
import numpy as np
import random
import math
import time

class Agent:

	def __init__(self, agent_id=1, comms=None, init_state="random_depth", ideal_phase=True, sync_dyn=False):
		# define functionality/logical parameters
		self._id = agent_id
		
		self.comms = comms  								# enable/disable inter-agent communications (TODO: add options for "continuous" vs. discrete/on-surface)
		self._comms_list = None								#
		
		self._sync_dyn = sync_dyn
		if sync_dyn:
			self.sync = Sync(comms)

		# define physical parameters
		self._g = 9.81										# m/s^2; gravity
		self._m3 = 14.0 									# kg; vertical component of glider mass
		self._A = self._g / self._m3						# TODO
		self._B = 1.0										# TODO
		self._max_depth = 100.0								# meters; 

		# define trajectory parameters
		self._dive_time = 15.0									# minutes to reach max depth from surface
		self._omega = 2.0*math.pi / (60.0*2.0*self._dive_time)	# angular frequency of sinusoidal trajectory to track

		# initialize state
		self._state = self.set_init_state(init_state, ideal_phase)		# pos (m); vel (m/s); ballast mass (kg); phase (rad)

		self.state_machine = AgentStateMachine(self._state)			# all agents initialized diving


	def update_state_via_comms_and_dynamics(self, k, dt):
		if self.state_machine._on_surface:

			# comms update
			if self.state_machine._ready_for_comms:
				self._comms_list = self.comms.get_in_comms_with_update(self._id)
			else:
				self._comms_list = [] 					# have to clear the comms list when diving

			# sync update
			if self.state_machine._ready_for_sync_update:
				# Max hold strategy
				#self.state_machine._on_surface_params["surface_time_ctr"] = self.sync.max_surface_hold(self._comms_list, self.state_machine._on_surface_params["surface_time_ctr"])

				# TODO: implement ring topology; then implement controller to evenly space phases; then implement estimators for cases 1) and 2)
				self.sync.wait_until_ring_topology(k, dt, self._id, self.state_machine, self._comms_list)


			# dynamics update
			self._state[0:3] = 0 											# glider is stationary
			self._state[3] = self._state[3] - self._omega*dt

			# state machine update
			self.state_machine.update_state_machine(k, dt)

		else: # diving

			# dynamics update
			self.update_dynamics_via_feedback_linearization(k, dt, K1=2, K2=1)									# glider is moving

			# state machine update
			self.state_machine.update_state_machine(k, dt)



	def update_dynamics_via_feedback_linearization(self, k, dt, K1=2, K2=1):
		# redefine important variables for readability
		z1_ = self._state[0] #+ np.random.normal(0,0.05,1)	# mean, std dev, # samples
		z2_ = self._state[1]
		u_ = self._state[2] 			# TODO: will need to add omega and theta to the state as these become variable
		theta_ = self._state[3]

		# saturate position
		z1_ = min([0, z1_])

		A_ = self._A
		B_ = self._B
		D_ = self._max_depth
		omega_ = self._omega

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
		self._state[3] = theta_ 			# TODO: should I be wrapping theta to [-pi, pi) ?

###
# HELPER FUNCTIONS
###
	
	def align_phase(self, state, ideal_phase):
		if ideal_phase:
			arg = (2.0*state[0] / self._max_depth) + 1.0 		# recovers ideal phase delay from initial depth (NOTE: depth must be negative)
			ang = math.acos(arg)								# produces angle in [0, pi], need other half of the unit circle
			ang = ( (-1)**(random.randint(0,1)) )*ang

			return ang
		else:
			return 0


	def set_init_state(self, init_state, ideal_phase):
		state_ = np.zeros((4,1))  		# pos, vel, ballast, phase delay

		if init_state == "random_depth":
			depth = -random.randint(0, math.floor(self._max_depth))
			state_[0] = float(depth);

		state_[3] = self.align_phase(state_, ideal_phase)

		return state_


