import numpy as np
import copy
import random

class Sync():
	def __init__(self, comms):
		self.comms = comms   			# gives access to agents, on_surface, on_surface_log 				# TODO: can probably get rid of this with a refactor

		# wait_until_ring_topology variables
		self._prev_on_surface = []
		self._order_in_dive_queue = 0 	# waiting in line to dive; used to modify the surface time threshold
		self._dive_interval = None
		self._overlap_tuning = 50.0		# increase to increase the amount of time gliders spend on the surface communicating with one another; larger values increase number of gliders on surface

		# wait_until_M_outliers variable
		self._init_idx = 0  				# allows for setting omegas for M agents
		self._NM_prev_on_surface = []
		self._NM_comms_list = []

	def max_surface_hold(self, comms_list, curr_surface_time):
		new_surface_time_elapsed = curr_surface_time

		for comm in comms_list:
			if comm[1] < new_surface_time_elapsed:
				new_surface_time_elapsed = comm[1]

		return new_surface_time_elapsed


	# TODO: still getting clumping issues if too many agents are initialized too close together
	# TODO: need closed-form expression for dive_interval as a fcn of max depth and number of agents (and/or outputs desired overlap?)
	def wait_until_ring_topology(self, state_machine, comms_list):
		if state_machine._on_surface_params["surface_time_ctr"] == 0:
			self._prev_on_surface = copy.copy(self.comms._on_surface) 				# have to copy because we need to see time differences in this information
			self._order_in_dive_queue = len(comms_list)
			self._dive_interval = (2*np.pi / self.comms._num_agents) / self.comms.agents[-1]._omega					# ideal phase spacing
			self._dive_interval = self._dive_interval + (self._dive_interval/self.comms._num_agents) + 1			# this accounts for the overall surface delay which distorts the periodic behavior of the agents
			self._dive_interval = self._dive_interval + self._overlap_tuning  										# tune surface hold to increase time and # agents in-comms

			state_machine._on_surface_params["surface_time_threshold"] =  self._order_in_dive_queue*self._dive_interval

		if ( (self.comms._on_surface - self._prev_on_surface).any() ):

			# operations relating to (just) dived agents
			dived_idx_ = ( np.asarray(self._prev_on_surface) - np.asarray(self.comms._on_surface) ) > 0 			# find out if any agents dived
			
			if dived_idx_.sum() > 0:  																							# if agent(s) dived
				self._order_in_dive_queue = self._order_in_dive_queue - 1  														# decrement queue
				state_machine._on_surface_params["surface_time_ctr"] = 0  														# account for mismatch in dive counter
				state_machine._on_surface_params["surface_time_threshold"] =  self._order_in_dive_queue*self._dive_interval 	# update surface hold time

			self._prev_on_surface = copy.copy(self.comms._on_surface)


	# works okay for fixed 10-agent case
	# Need to troubleshoot clumping issues... becomes more pronounce here
	def wait_until_M_outliers(self, M, agent_id, state_machine, comms_list):
		if agent_id < M:
			if self._init_idx == 0:
				self._init_idx = self._init_idx + 1
				self.comms.agents[agent_id]._omega = 2*self.comms.agents[agent_id]._omega 						# TODO: this is just a test

		else:
			# TODO: wait_until (or not, eg: fixed surface hold ?)
			# self._NM_prev_on_surface = copy.copy(self.comms._on_surface[M:])
			self._NM_comms_list = [] 		# TODO: should always have self in list...

			# TODO: do i really need this conditional? run everytime?
			# if len(comms_list) > 1:
			for agent in comms_list:
				if agent[0] >= M:
					self._NM_comms_list.append(agent)

			# print("agent id: {0}".format(agent_id))
			# print("comms list: {0}".format(comms_list))
			# print("new comms list: {0}".format(self._NM_comms_list))
			# input()

			# almost exact re-implementation of wait_until_ring_topology
			if state_machine._on_surface_params["surface_time_ctr"] == 0:
				self._NM_prev_on_surface = copy.copy(self.comms._on_surface[M:]) 				# have to copy because we need to see time differences in this information
				self._order_in_dive_queue = len(self._NM_comms_list)
				self._dive_interval = ( 2*np.pi / (self.comms._num_agents-M) ) / self.comms.agents[-1]._omega			# ideal phase spacing
				self._dive_interval = self._dive_interval + (self._dive_interval / (self.comms._num_agents-M) ) + 1		# this accounts for the overall surface delay which distorts the periodic behavior of the agents
				self._dive_interval = self._dive_interval + self._overlap_tuning  										# tune surface hold to increase time and # agents in-comms

				state_machine._on_surface_params["surface_time_threshold"] =  self._order_in_dive_queue*self._dive_interval

			if ( (self.comms._on_surface[M:] - self._NM_prev_on_surface).any() ):

				# operations relating to (just) dived agents
				dived_idx_ = ( np.asarray(self._NM_prev_on_surface) - np.asarray(self.comms._on_surface[M:]) ) > 0 			# find out if any agents dived
				
				if dived_idx_.sum() > 0:  																							# if agent(s) dived
					self._order_in_dive_queue = self._order_in_dive_queue - 1  														# decrement queue
					state_machine._on_surface_params["surface_time_ctr"] = 0  														# account for mismatch in dive counter
					state_machine._on_surface_params["surface_time_threshold"] =  self._order_in_dive_queue*self._dive_interval 	# update surface hold time

				self._NM_prev_on_surface = copy.copy(self.comms._on_surface[M:])


		# peel off first M agents; assign different ang vel (omega) -- how to choose these omegas?
			# need separate on surface identification for N-M agents and M agents; N-M agents do the surface cover and M agents improve the est convergence rate
			# could just zero those agents out when doing the N-M update / or array slicing [M:]
		# N-M agents perform wait_until; OR have N-M agents w/ surface hold and NO wait_until (might be easier to implement initially; won't correct init cond??)




	###
	# Helper Functions
	### 