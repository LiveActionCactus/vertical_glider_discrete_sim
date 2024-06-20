import numpy as np

class Comms:

	def __init__(self, sim_length, agents, log_comms=True):
		self._sim_length = sim_length
		self.agents = agents
		self._num_agents = len(self.agents)
		#self.inst_adj_mat = np.zeros((self._num_agents, self._num_agents))				# TODO: probably only necessary for networkx plotting
		self._on_surface = np.zeros(self._num_agents)
		
		# define logging
		self._log_comms = log_comms
		if self._log_comms == True:
			self._on_surface_log = self.initialize_comms_logging()	# for on-surface communications only; change to triu for more comprehensive logging


	# TODO: I'm not sure what a "comms update" should entail. Minimum logging for complete reconstruction is "_on_surface". Must be called from sim_env
	def update_comms(self, k):
		self.update_on_surface_list()
		#triu = self.surface_list_to_triu()

		if self._log_comms == True:
			self._on_surface_log[k,:] = self._on_surface


	# # TODO: force information state by only sharing information if glider on surface, and only with other gliders on surface. Zero/None out everything else.
	# def get_in_comms_with_update(self):
	# 	in_comms_state_ = []
	# 	for i in range(0,self._num_agents):
	# 		in_comms_state_.append((self._on_surface[i], self.agents[i]._state))

	# 	return in_comms_state_


	#####
	### HELPER FUNCTIONS
	#####

	def update_on_surface_list(self):
		for i in range(0, self._num_agents):
			if self.agents[i]._on_surface == True:
				self._on_surface[i] = 1
			else:
				self._on_surface[i] = 0


	# converts list of surfaced vehicles to array representation of an upper triangular (symmetric) matrix  
	def surface_list_to_triu(self):
		M = int(self._num_agents*(self._num_agents+1)/2)			# length of triu and runtime complexity
		triu = np.zeros(M)

		offset_ = 0
		idx_ = self._num_agents										# index for decreasing window  

		for i in range(0, self._num_agents):
			if self._on_surface[i] == 0:
				triu[offset_:(offset_+idx_)] = np.zeros((1,idx_))
			else:
				triu[offset_:(offset_+idx_)] = self._on_surface[i:None]		# map on-surface list to triu

			triu[offset_] = 1 												# always a self-loop
			offset_ = offset_ + idx_
			idx_ = idx_ - 1													# decrease idx to half runtime

		return triu


	def triu_to_adj_matrix(self, triu_array):
		dim = self._num_agents
		adj_mat = np.zeros((dim, dim))
		adj_mat[np.triu_indices(adj_mat.shape[0], k=0)] = triu_array
		adj_mat = adj_mat + adj_mat.T - np.diag(np.diag(adj_mat))

		return adj_mat


	def initialize_comms_logging(self):
		return np.zeros((self._sim_length, self._num_agents))