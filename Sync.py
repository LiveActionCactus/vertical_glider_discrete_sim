import numpy as np
import copy
import random

class Sync():
	def __init__(self, comms):
		self.comms = comms   			# gives access to agents, on_surface, on_surface_log

		# wait_until_ring_topology variables
		self._last_dive_time = None
		self._prev_on_surface = []
		self._dive_interval = None
		self._sync_update_rate = 1.0 			# seconds; sync rate; amplifies difference in comms states
		self._sync_update_timer = 0.0
		self._first_on_surface = False



	def max_surface_hold(self, comms_list, curr_surface_time):
		new_surface_time_elapsed = curr_surface_time

		for comm in comms_list:
			if comm[1] < new_surface_time_elapsed:
				new_surface_time_elapsed = comm[1]

		return new_surface_time_elapsed



	# TODO: need to have check to not submerge unless another agent(s) are on the surface
	def wait_until_ring_topology(self, k, dt, agent_id, state_machine, comms_list):
		if state_machine._on_surface_params["surface_time_ctr"] == 0:
			self._prev_on_surface = copy.copy(self.comms._on_surface) 				# have to copy because we need to see time differences in this information
			# self._last_dive_time = None
			# state_machine._on_surface_params["surface_time_threshold"] = 1000000 	# set surface hold threshold impossibly high; stay on surface
			# self._first_on_surface = False
			
			self._dive_interval = (2*np.pi / self.comms._num_agents) / self.comms.agents[0]._omega 
			# state_machine._on_surface_params["surface_time_ctr"] = 0.0
			state_machine._on_surface_params["surface_time_threshold"] =  len(comms_list)*self._dive_interval

			# if len(comms_list) == 1:
			# 	self._first_on_surface = True
			# 	print("first on the surface: {0}".format(agent_id))

		# if ( (self.comms._on_surface - self._prev_on_surface).any() ):

		# 	# operations relating to (just) dived agents
		# 	dived_idx_ = ( np.asarray(self._prev_on_surface) - np.asarray(self.comms._on_surface) ) > 0 			# find who dived
			
		# 	# TODO: need to know how many agents "in front" for multiple of delay time; this will prevent "clumping/absorbtion" with higher # of agents
		# 	if dived_idx_.sum() > 0:  									# if agent(s) dived

		# 		if self._last_dive_time == None:
		# 			self._last_dive_time = k*dt
		# 			self._dive_interval = self._dive_interval #* 1.35 			# this accounts for the overall surface delay which distorts the periodic behavior of the agents; treat as tuning parameter to have more surface comms time
		# 			# state_machine._on_surface_params["surface_time_threshold"] =  state_machine._on_surface_params["surface_time_ctr"] + len(comms_list)*self._dive_interval
		# 			state_machine._on_surface_params["surface_time_ctr"] = 0.0
		# 			state_machine._on_surface_params["surface_time_threshold"] =  len(comms_list)*self._dive_interval

		# 			# print("agent: {0}, num agents on surface: {1}, dive interval")

		# 	# operations related to (just) surfaced agents
		# 	surfaced_idx_ = ( np.asarray(self.comms._on_surface) - np.asarray(self._prev_on_surface) ) > 0 			# find who surfaced

		# 	if surfaced_idx_.sum() > 0:

		# 		if self._first_on_surface == True and self.comms._on_surface.sum() > 1 and (state_machine._on_surface_params["surface_time_ctr"] >= self._dive_interval):
		# 			state_machine._on_surface_params["surface_time_threshold"] = 0 				# if first agent on surface, dive as soon a new agent surfaces

		# 	self._prev_on_surface = copy.copy(self.comms._on_surface)

		# else:
		# 	if self._sync_update_timer >= self._sync_update_rate: 					# TODO: pretty sure this is required to help mitigate failure mode where they all get trapped on the surface
		# 		self._sync_update_timer = 0.0
		# 		self._prev_on_surface = copy.copy(self.comms._on_surface)
			
		# 	self._sync_update_timer = self._sync_update_timer + dt

			# force agent to stay on surface if alone
			# if state_machine._on_surface_params["surface_time_ctr"] >= state_machine._on_surface_params["surface_time_threshold"]:
			# 	if len(comms_list) == 1:
			# 		self._first_on_surface = True
			# 		state_machine._on_surface_params["surface_time_threshold"] = 1000000

		# TODO: failure mode where they all get stuck on the surface
		# TODO: if two agents have the exact same initial conditions all agents can get stuck on the surface


	###
	# Helper Functions
	### 

	def sort_diving_queue(self):
		self._diving_queue = sorted(self._diving_queue, key = lambda x:x[1])
