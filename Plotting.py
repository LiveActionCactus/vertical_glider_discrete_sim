import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import itertools
from matplotlib import animation
import math

class Plotting():

	def __init__(self, sim_env):
		self._sim_env = sim_env
		self._animation_path = './animations/10agents_200min_waituntil.gif'


	def plot_state(self):
		k_ = np.linspace(0, self._sim_env._tmax/60, self._sim_env._t)		# defines the simulation length and step size

		fig_, axs_ = plt.subplots(2,2)
		
		for i in range(0, self._sim_env._num_agents):
			agent_ = self._sim_env._state_log[:,:,i]

			# plot positions
			axs_[0,0].plot(k_, agent_[0,:], label='Agent {0}'.format(i))
			axs_[0,0].set(xlabel='Time (min)', ylabel='Depth (m)')
			axs_[0,0].set_title('Position vs. Time')
			if self._sim_env._num_agents < 5:
				axs_[0,0].legend()

			# plot velocities
			axs_[0,1].plot(k_, agent_[1,:], label='Agent {0}'.format(i))
			axs_[0,1].set(xlabel='Time (min)', ylabel='Velocity (m/s)')
			axs_[0,1].set_title('Velocity vs. Time')
			if self._sim_env._num_agents < 5:
				axs_[0,1].legend()

			# plot ballast
			axs_[1,0].plot(k_, agent_[2,:], label='Agent {0}'.format(i))
			axs_[1,0].set(xlabel='Time (min)', ylabel='Ballast (kg)')
			axs_[1,0].set_title('Ballast vs. Time')
			# if self._sim_env._num_agents < 5:
			axs_[1,0].legend()

			# plot phase
			axs_[1,1].plot(k_, agent_[3,:], label='Agent {0}'.format(i))
			axs_[1,1].set(xlabel='Time (min)', ylabel='Phase (rad)')
			axs_[1,1].set_title('Phase vs. Time')
			if self._sim_env._num_agents < 5:
				axs_[1,0].legend()

		plt.show(block="False")


	def plot_time_varying_graph(self):
		# https://stackoverflow.com/questions/31815454/animate-graph-diffusion-with-networkx

		on_surface_log_ = self._sim_env.comms._on_surface_log
		multiplier_ = 23

		nodes_ = np.arange(0, on_surface_log_.shape[1], 1)  		# generate array of nodes/agents, {0, ... N}
		masked_ = np.multiply(nodes_, on_surface_log_[0,:]) 			# init graph state
		masked_ = masked_[masked_ != 0]
		edges_ = itertools.combinations(masked_,2) 					# generate edges at init graph state

		G = nx.Graph() 												# initialize the graph
		G.add_nodes_from(nodes_)
		G.add_edges_from(edges_)

		fig_, ax_ = plt.subplots(figsize=(6,4))

		layout = nx.circular_layout(G) 								# init graph layout; faster to pass the pre-built layout

		ani = animation.FuncAnimation(fig_, self.simple_update, frames=math.floor(on_surface_log_.shape[0]/multiplier_), fargs=(multiplier_, layout, G, on_surface_log_, nodes_, ax_))
		ani.save(self._animation_path, writer='pillow', fps=30)


	# def plot_graph_edges_as_random(self):


	#####
	# HELPER FUNCTIONS
	#####

	def complete_graph_from_list(self, L, create_using=None):
	    G = nx.empty_graph(len(L),create_using)
	    if len(L)>1:
	        if G.is_directed():
	            edges = itertools.permutations(L,2)
	        else:
	            edges = itertools.combinations(L,2)
	        G.add_edges_from(edges)

	    return G

	# TODO: graph is jumping around; find a way to remove edges but not the nodes
	# TODO: why is agent3 never in comms? check the data vector
	def simple_update(self, num, multiplier, layout, G, on_surface_log_, nodes_, ax):
		itr = math.floor(num*multiplier)

		ax.clear()

		# G.clear()   																			# TODO: need a better solution; don't delete the nodes
		# G.add_nodes_from(nodes_)
		edges_ = self.recover_graph_edges(nodes_, on_surface_log_[itr,:])		# determine new edges
		# G.add_edges_from(edges_)
		G.update(edges=edges_)

		nx.draw(G, pos=layout, ax=ax, with_labels=True) 						# draw the graph
		ax.set_title("Frame {}".format(itr)) 	# update the title


	def recover_graph_edges(self, nodes, itr_edges):
		masked_ = np.multiply(nodes, itr_edges)
		masked_ = masked_[masked_ != 0]
		edges_ = itertools.combinations(masked_,2)

		return edges_