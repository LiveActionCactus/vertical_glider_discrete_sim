import numpy as np
import math
from Agent import Agent
from Comms import Comms

class SimEnv:

	def __init__(self):
		# define simulation parameters
		self._tmax = 100*60								# minutes*(seconds) to run simulation
		self._dt = 0.2									# sampling / discretization rate of simulation
		self._t = math.floor(self._tmax / self._dt)		# total indices required to run simulation
		self._num_agents = 2

		# define agents and comms
		self._sync_dyn = True							# enable/disable syncronizing dynamics
		self.comms = Comms()							# empty comms class to be passed to agents
		self.agents = self.initialize_agents()			# build array of agent objects

		# define agent logging
		(shapex, shapey) = self.agents[0]._state.shape
		self._state_log = np.zeros((shapex, self._t, self._num_agents))		# 3-D tensor w/ struct: state dim, sim length, number of agents 

		# initialize comms object
		self.comms.delayed_init(sim_length=self._t, agents=self.agents, log_comms=True)


	def initialize_agents(self):
		agents = [];

		for i in range(0, self._num_agents):
			agents.append(Agent(i, comms=self.comms, sync_dyn=self._sync_dyn))				# gives agent unique id

		return agents


	# runs the entire simulation
	def run_sim(self):
		for k in range(0, self._t):
			self.comms.log_comms_values(k)
			self.comms.update_comms(k)									# update communications; needs to come before dynamics update so dynamics step is well informed

			for i in range(self._num_agents):	
				self.log_state_values(k, i)											# store state information
				self.agents[i].update_state_via_comms_and_dynamics(k, self._dt) 	# update agent dynamics


	def log_state_values(self, k, i):
		self._state_log[:, k:k+1, i] = self.agents[i]._state 	# k-th sim step; i-th agent


	# TODO: NEED TO DO SYNCHRONIZATION FROM THIS LEVEL AND PASS UPDATED PHASES TO EACH GLIDER FOR TRACKING 