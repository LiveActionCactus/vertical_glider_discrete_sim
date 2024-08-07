import numpy as np
import math
import random

from Agent import Agent
from Comms import Comms

class SimEnv:

	def __init__(self):
		# define simulation parameters
		self._tmax = 200*60								# minutes*(seconds) to run simulation
		self._dt = 0.2									# sampling / discretization rate of simulation
		self._t = math.floor(self._tmax / self._dt)		# total indices required to run simulation
		self._num_agents = 10

		# agents' physical parameters
		# TODO: pass in struct with parameters to parse out on agent init
		self._max_depth = 100 							# meters

		# define agents and comms
		self._ideal_phase_on_init = True				
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
			state_ = self.random_depth_init_state() 					# arbitary number of agents; TODO: implement a "save init conditions" parameter w/ pickle
			# state_ = self.fixed_4agent_init_state(agent_id=i) 		# 4 or fewer agents
			# state_ = self.fixed_10agent_init_state(agent_id=i) 		# 10 or fewer agents

			if self._ideal_phase_on_init:
				state_ = self.align_phase(state_)

			agents.append(Agent(i, init_state=state_, comms=self.comms, sync_dyn=self._sync_dyn, max_depth=self._max_depth))				# gives agent unique id

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


	#####
	# HELPER FUNCTIONS
	#####

	# TODO: need to specify max depth
	def align_phase(self, state):
		arg_ = (2.0*state[0] / self._max_depth) + 1.0 		# recovers ideal phase delay from initial depth (NOTE: depth must be negative)
		ang_ = math.acos(arg_)								# produces angle in [0, pi], need other half of the unit circle
		ang_ = ( (-1)**(random.randint(0,1)) )*ang_

		state[3] = ang_

		return state


	def random_depth_init_state(self):
		state_ = np.zeros((4,1))  										# pos, vel, ballast, phase delay

		depth = -random.randint(0, math.floor(self._max_depth))
		state_[0] = float(depth);

		return state_


	def fixed_4agent_init_state(self, agent_id):
		state_ = np.zeros((4,1))  		# pos, vel, ballast, phase delay

		if agent_id == 0:
			state_[0] = -74.0
			state_[1] = 0.0
			state_[2] = 0.0
			state_[3] = 2.07145104
		elif agent_id == 1:
			state_[0] = -8.0
			state_[1] = 0.0
			state_[2] = 0.0
			state_[3] = 0.5735131
		elif agent_id == 2:
			state_[0] = -69.0
			state_[1] = 0.0
			state_[2] = 0.0
			state_[3] = -1.96059262
		elif agent_id == 3:
			state_[0] = -100.0
			state_[1] = 0.0
			state_[2] = 0.0
			state_[3] = -3.14159265

		return state_


	def fixed_10agent_init_state(self, agent_id):
		state_ = np.zeros((4,1))  		# pos, vel, ballast, phase delay

		if agent_id == 0:
			state_[0] = -53.0
			state_[1] = 0.0
			state_[2] = 0.0
			state_[3] = 1.63083239
		elif agent_id == 1:
			state_[0] = -76.0
			state_[1] = 0.0
			state_[2] = 0.0
			state_[3] = -2.11764728
		elif agent_id == 2:
			state_[0] = -73.0
			state_[1] = 0.0
			state_[2] = 0.0
			state_[3] = 2.04879153
		elif agent_id == 3:
			state_[0] = -48.0
			state_[1] = 0.0
			state_[2] = 0.0
			state_[3] = 1.53078565
		elif agent_id == 4:
			state_[0] = -18.0
			state_[1] = 0.0
			state_[2] = 0.0
			state_[3] = -0.87629806
		elif agent_id == 5:
			state_[0] = -46.0
			state_[1] = 0.0
			state_[2] = 0.0
			state_[3] = -1.49071075
		elif agent_id == 6:
			state_[0] = -84.0
			state_[1] = 0.0
			state_[2] = 0.0
			state_[3] = 2.31855896
		elif agent_id == 7:
			state_[0] = -44.0
			state_[1] = 0.0
			state_[2] = 0.0
			state_[3] = 1.45050644
		elif agent_id == 8:
			state_[0] = -4.0
			state_[1] = 0.0
			state_[2] = 0.0
			state_[3] = -0.40271584
		elif agent_id == 9:
			state_[0] = -69.0
			state_[1] = 0.0
			state_[2] = 0.0
			state_[3] = 1.96059262

		return state_
