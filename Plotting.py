import matplotlib.pyplot as plt
import numpy as np

class Plotting():

	def __init__(self, sim_env):
		self._sim_env = sim_env 

	def plot_state(self):
		k = np.linspace(0, self._sim_env._tmax/60, self._sim_env._t)		# defines the simulation length and step size

		fig, axs = plt.subplots(2,2)
		
		for i in range(0, self._sim_env._num_agents):
			agent = self._sim_env._state_log[:,:,i]

			# plot positions
			axs[0,0].plot(k, agent[0,:], label='Agent {0}'.format(i))
			axs[0,0].set(xlabel='Time (min)', ylabel='Depth (m)')
			axs[0,0].set_title('Position vs. Time')
			if self._sim_env._num_agents < 5:
				axs[0,0].legend()

			# plot velocities
			axs[0,1].plot(k, agent[1,:], label='Agent {0}'.format(i))
			axs[0,1].set(xlabel='Time (min)', ylabel='Velocity (m/s)')
			axs[0,1].set_title('Velocity vs. Time')
			if self._sim_env._num_agents < 5:
				axs[0,1].legend()

			# plot ballast
			axs[1,0].plot(k, agent[2,:], label='Agent {0}'.format(i))
			axs[1,0].set(xlabel='Time (min)', ylabel='Ballast (kg)')
			axs[1,0].set_title('Ballast vs. Time')
			if self._sim_env._num_agents < 5:
				axs[1,0].legend()


		plt.show(block="True")