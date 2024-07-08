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
			print("on the surface agent: {0}".format(agent_id))
			# print(self.comms._on_surface)
			# print(self._prev_on_surface)
			# print(self._diving_queue)
			# input()
			self._prev_on_surface = copy.copy(self.comms._on_surface) 				# have to copy because we need to see time differences in this information
			self._last_dive_time = None
			state_machine._on_surface_params["surface_time_threshold"] = 100000 	# set surface hold threshold impossibly high; stay on surface
			self._diving_queue = []

			if len(comms_list) == 1:
				self._diving_queue = comms_list
				self._first_on_surface = True
				print("first on the surface: {0}".format(agent_id))
			elif len(comms_list) > 1:
				self._diving_queue = comms_list
				self.sort_diving_queue()
			else:
				raise Exception(f'Entered invalid state for _diving_queue')		


		if ( (self.comms._on_surface - self._prev_on_surface).any() ):
			print("i'm in the update loop, agent: {0}".format(agent_id))
			# print("diving queue: {0}".format(self._diving_queue))

			# operations relating to (just) dived agents
			dived_idx_ = ( np.asarray(self._prev_on_surface) - np.asarray(self.comms._on_surface) ) > 0 			# find who dived
			# print("dived_idx_ {0}".format(dived_idx_))
			
			if dived_idx_.sum() > 0:  									# if agent(s) dived
				for idx in np.where(dived_idx_ == 1)[0]:  				# should only be length 1 most times; maybe 2
					for j, agent in enumerate(self._diving_queue):		# O(n)
						if agent[0] == idx:
							self._diving_queue.pop(j) 					# remove dived agents

				if self._last_dive_time == None:
					self._last_dive_time = k*dt
					self._dive_interval = (2*np.pi / self.comms._num_agents) / self.comms.agents[0]._omega 			# seconds; TODO: may get tripped up in constructor init; TODO: why does 4*pi look so good?
					print("agent: {0}, dive interval: {1}, surface interval: {2}".format(agent_id, self._dive_interval, state_machine._on_surface_params["surface_time_ctr"]))
					
					state_machine._on_surface_params["surface_time_threshold"] =  state_machine._on_surface_params["surface_time_ctr"] + self._dive_interval
					print("updated surface time threshold")

					# # why is this necessary?
					# for agent in self._diving_queue:
					# 	if agent[0] == agent_id:
					# 		state_machine._on_surface_params["surface_time_threshold"] =  state_machine._on_surface_params["surface_time_ctr"] + self._dive_interval
					# 		print("updated surface time threshold")

			# operations related to (just) surfaced agents
			surfaced_idx_ = ( np.asarray(self.comms._on_surface) - np.asarray(self._prev_on_surface) ) > 0 			# find who surfaced
			print("surfaced_idx_ {0}".format(surfaced_idx_))
			if surfaced_idx_.sum() > 0:
				for idx in np.where(surfaced_idx_ == 1)[0]: 				# should only be length 1 most times; maybe 2
					for j, agent in enumerate(comms_list):					# O(n)
						if agent[0] == idx:
							self._diving_queue.append(comms_list[j]) 		# add newly surfaced agents to end of diving queue; TODO: diving queue doesn't look right... times?

				if self._first_on_surface == True and self.comms._on_surface.sum() == 2:
					# state_machine._diving = True
					state_machine._on_surface_params["surface_time_threshold"] = 0
					print("counter {0} and threshold {1}".format(state_machine._on_surface_params["surface_time_ctr"], state_machine._on_surface_params["surface_time_threshold"]))

			# TODO: how to handle the first agent on the surface
			# TODO: need to make sure surface hold is also adjusting appropriately long

			self._prev_on_surface = copy.copy(self.comms._on_surface)

		else:
			# print("agent: {0}, diving queue: {1}".format(agent_id, self._diving_queue))
			# input()

			if self._sync_update_timer >= self._sync_update_rate:
				self._sync_update_timer = 0.0
				self._prev_on_surface = copy.copy(self.comms._on_surface)

			self._sync_update_timer = self._sync_update_timer + dt

			# if agent_id == 0:
				# print("diving queue: {0}".format(self._diving_queue))
				# input()

		# check if queue changed; set dive time off that; OR maybe just 2*pi/N 

			# find agents that dived; create list of idxs
			# if agents dived
				# remove dived agents from diving queue

				# if last dive time is none
					# set last dive time
					# set dive time 				# TODO: do this by fiddling with surface hold time relative to surface time

			# find new agent(s) in comms
			# append to diving queue
	



		# if self surface time is 0 
			# reset diving queue

		# if comms list empty
			# create diving queue with self as only element
		
		# if comms list not empty (not the first to surface)
			# if diving queue empty
				# sort comms list and append self to end
			# if diving queue not empty
				# append self to end



	###
	# Helper Functions
	### 

	def sort_diving_queue(self):
		self._diving_queue = sorted(self._diving_queue, key = lambda x:x[1])
