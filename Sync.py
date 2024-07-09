import numpy as np
import copy
import random

class Sync():
	def __init__(self, comms):
		self.comms = comms   			# gives access to agents, on_surface, on_surface_log

		# wait_until_ring_topology variables
		self._prev_on_surface = []
		self._order_in_dive_queue = 0 	# waiting in line to dive; used to modify the surface time threshold
		self._dive_interval = None
		self._overlap_tuning = 50.0		# increase to increase the amount of time gliders spend on the surface communicating with one another; larger values increase number of gliders on surface


	def max_surface_hold(self, comms_list, curr_surface_time):
		new_surface_time_elapsed = curr_surface_time

		for comm in comms_list:
			if comm[1] < new_surface_time_elapsed:
				new_surface_time_elapsed = comm[1]

		return new_surface_time_elapsed


	def wait_until_ring_topology(self, state_machine, comms_list):
		if state_machine._on_surface_params["surface_time_ctr"] == 0:
			self._prev_on_surface = copy.copy(self.comms._on_surface) 				# have to copy because we need to see time differences in this information
			self._order_in_dive_queue = len(comms_list)
			self._dive_interval = (2*np.pi / self.comms._num_agents) / self.comms.agents[0]._omega					# ideal phase spacing
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


	###
	# Helper Functions
	### 

	def sort_diving_queue(self):
		self._diving_queue = sorted(self._diving_queue, key = lambda x:x[1])
