import numpy as np
import copy

class Sync():
	def __init__(self, comms):
		self.comms = comms   			# gives access to agents, on_surface, on_surface_log

		# wait_until_ring_topology variables
		self._diving_queue = []  				# will be filled in descending order (FIFO) via the second parameter of (agent_idx, surface time)
		self._last_dive_time = None
		self._prev_on_surface = []
		self._dive_interval = None
		self._sync_update_rate = 1.0 			# seconds; amplifies difference in comms states
		self._sync_update_timer = 0.0
		self._first_on_surface = False



	def max_surface_hold(self, comms_list, curr_surface_time):
		new_surface_time_elapsed = curr_surface_time

		for comm in comms_list:
			if comm[1] < new_surface_time_elapsed:
				new_surface_time_elapsed = comm[1]

		return new_surface_time_elapsed


	def wait_until_ring_topology(self, k, dt, agent_id, state_machine, comms_list):
		if state_machine._on_surface_params["surface_time_ctr"] == 0:
			self._prev_on_surface = copy.copy(self.comms._on_surface) 				# have to copy because we need to see time differences in this information
			self._last_dive_time = None
			state_machine._on_surface_params["surface_time_threshold"] = 100000 	# set surface hold threshold impossibly high; stay on surface
			self._first_on_surface = False

			if len(comms_list) == 1:
				self._first_on_surface = True
				print("first on the surface: {0}".format(agent_id))

		if ( (self.comms._on_surface - self._prev_on_surface).any() ):
			print("i'm in the update loop, agent: {0}".format(agent_id))

			# operations relating to (just) dived agents
			dived_idx_ = ( np.asarray(self._prev_on_surface) - np.asarray(self.comms._on_surface) ) > 0 			# find who dived
			
			if dived_idx_.sum() > 0:  									# if agent(s) dived

				if self._last_dive_time == None:
					self._last_dive_time = k*dt
					self._dive_interval = (2*np.pi / self.comms._num_agents) / self.comms.agents[0]._omega 
					self._dive_interval = self._dive_interval * 1.35 			# this accounts for the overall surface delay which distorts the periodic behavior of the agents; treat as tuning parameter to have more surface comms time
					state_machine._on_surface_params["surface_time_threshold"] =  state_machine._on_surface_params["surface_time_ctr"] + self._dive_interval

			# operations related to (just) surfaced agents
			surfaced_idx_ = ( np.asarray(self.comms._on_surface) - np.asarray(self._prev_on_surface) ) > 0 			# find who surfaced

			if surfaced_idx_.sum() > 0:

				if self._first_on_surface == True and self.comms._on_surface.sum() > 1:
					state_machine._on_surface_params["surface_time_threshold"] = 0

			self._prev_on_surface = copy.copy(self.comms._on_surface)

		else:
			if self._sync_update_timer >= self._sync_update_rate:
				self._sync_update_timer = 0.0
				self._prev_on_surface = copy.copy(self.comms._on_surface)

			self._sync_update_timer = self._sync_update_timer + dt


	###
	# Helper Functions
	### 

	def sort_diving_queue(self):
		self._diving_queue = sorted(self._diving_queue, key = lambda x:x[1])
