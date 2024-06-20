import numpy as np

class Comms:

	def __init__(self, num_agents, on_surface):
		self._num_agents = num_agents
		self.inst_adj_mat = np.zeros((self._num_agents, self._num_agents))
		self.on_surface_ = on_surface


	def surface_list_to_triu(self):
		M = int(self._num_agents*(self._num_agents+1)/2)			# length of triu and runtime complexity
		triu_array = np.zeros(M)

		offset_ = 0
		idx_ = self._num_agents								# 

		for i in range(0, self._num_agents):
			if self.on_surface_[i] == 0:
				triu_array[offset_:(offset_+idx_)] = np.zeros((1,idx_))
			else:
				triu_array[offset_:(offset_+idx_)] = self.on_surface_[i:None]		# map on-surface list to triu

			triu_array[offset_] = 1 												# for self-loop; NOTE: adjacency matrix always has 0s on diagonal; change to 0 if we need that
			offset_ = offset_ + idx_
			idx_ = idx_ - 1													# decrease idx to half runtime

		return triu_array


	def triu_to_adj_matrix(self, triu_array):
		dim = self._num_agents
		adj_mat = np.zeros((dim, dim))
		adj_mat[np.triu_indices(adj_mat.shape[0], k=0)] = triu_array
		adj_mat = adj_mat + adj_mat.T - np.diag(np.diag(adj_mat))

		return adj_mat

if __name__ == "__main__":
	on_surface = np.array([1,0,1,1]) # also works for: [1,0,1,1], [1,0,1,0], [0, 0, 1, 1]
	#on_surface = np.array([0,1,1,0,1])

	comms = Comms(num_agents=len(on_surface), on_surface=on_surface)

	test = comms.surface_list_to_triu()

	print(test)

	test2 = comms.triu_to_adj_matrix(test)

	print(test2)


# NOTE: DOES NOT WORK FOR WEIGHTED EDGES / NODES