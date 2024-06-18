import numpy as np
import math
from Agent import Agent

class SimEnv:

	def __init__(self):
		self._tmax = 30*60;								# minutes to run simulation
		self._dt = 0.1;									# sampling / discretization rate of simulation
		self._t = math.floor(self._tmax / self._dt)		# total indices required to run simulation
		self._num_agents = 2;

		self.agents = self.initialize_agents();
		self._state_log = np.zeros((3, self._t, self._num_agents))	# 3-D tensor w/ struct: state dim, sim length, number of agents 


	def initialize_agents(self):
		agents = [];

		for i in range(self._num_agents):
			agents.append(Agent(i))					# gives agent unique id

		return agents


	def run_sim(self):
		for k in range(0, self._t):
			for i in range(self._num_agents):	
				self.log_state_values(k, i)
				self.agents[i].update_state_via_dynamics(k, self._dt)

		#print(self._state_log[:, 100:105, 0])


	def log_state_values(self, k, i):
		self._state_log[:, k:k+1, i] = self.agents[i]._state 	# k-th sim step; i-th agent


