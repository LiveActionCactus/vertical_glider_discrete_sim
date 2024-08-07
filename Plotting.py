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
		fig_.subplots_adjust(left=0.125, bottom=0.07, right=0.9, top=0.927, wspace=0.198, hspace=0.251)
		
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
		multiplier_ = 300

		nodes_ = np.arange(0, on_surface_log_.shape[1], 1)  		# generate array of nodes/agents, {0, ... N}
		masked_ = np.multiply(nodes_+1, on_surface_log_[0,:]) 		# init graph state; +1 captures node 0
		masked_ = masked_[masked_ != 0]
		masked_ = masked_ - 1
		edges_ = itertools.combinations(masked_,2) 					# generate edges at init graph state

		G = nx.Graph() 												# initialize the graph and build
		G.add_nodes_from(nodes_)
		G.add_edges_from(edges_)

		fig_, ax_ = plt.subplots(figsize=(6,4))

		layout = nx.circular_layout(G) 								# init graph layout; faster to pass the pre-built layout

		# animate; update animation w/ callback fcn; and save to file
		ani = animation.FuncAnimation(fig_, self.anim_update, frames=math.floor(on_surface_log_.shape[0]/multiplier_), fargs=(multiplier_, layout, G, on_surface_log_, nodes_, ax_))
		ani.save(self._animation_path, writer='pillow', fps=30)


	def plot_graph_edges_as_random(self, print_on_surface_results=False, display_ave_comms_graph=False, graph_layout="spring"):
		on_surface_log_ = self._sim_env.comms._on_surface_log
		nodes_ = np.arange(0, on_surface_log_.shape[1], 1)  		# generate array of nodes/agents, {0, ... N}

		#
		# FIND AVERAGES OF ON-SURFACE FREQUENCY (non-unique)
		#

		max_on_surface_ = np.zeros(len(nodes_)) 					# 1 - agent on surface at any time in sim; 0 - agent never on surface
		ave_on_surface_ = np.zeros(len(nodes_))
		ave_on_surface_transient_ = np.zeros((on_surface_log_.shape[0], on_surface_log_.shape[1]))

		for i in range(0, on_surface_log_.shape[0]):
			max_on_surface_ = [max(l1, l2) for l1, l2 in zip(max_on_surface_, on_surface_log_[i,:])]
			ave_on_surface_ = ave_on_surface_ + on_surface_log_[i,:]

			if i == 0:
				ave_on_surface_transient_[i,:] = ave_on_surface_transient_[i,:]
			else:
				ave_on_surface_transient_[i,:] = (on_surface_log_[i,:] + i*ave_on_surface_transient_[i-1,:]) / (i+1)

		ave_on_surface_ = ave_on_surface_ / on_surface_log_.shape[0]

		if print_on_surface_results == True:
			print("max on surface: {0}".format(max_on_surface_))
			print("ave_on_surface_: {0}".format(ave_on_surface_))
			print("ave transient end: {0}".format(ave_on_surface_transient_[-1,:]))
			print("ave transient rand: {0}".format(ave_on_surface_transient_[20000,:]))

		#
		# FIND AVERAGES OF COMMS GRAPH EDGES FREQUENCY (non-unique)
		#

		# build out edge combinations for a complete graph
		complete_edges_ = list(itertools.combinations(nodes_,2))

		# turn edges into keys of a dictionary
		complete_edges_dict_ = {}
		for edge in list(complete_edges_):
			complete_edges_dict_[edge] = 0

		# count occurances of edges
		for i in range(0, on_surface_log_.shape[0]):
			edges_ = self.recover_graph_edges(nodes_, on_surface_log_[i,:])

			for edge in edges_:
				if edge in complete_edges_dict_:
					complete_edges_dict_[edge] = complete_edges_dict_[edge] + 1 		# occurances

 		# compute average occurance of each edge
		complete_edges_dict_prob_ = {}
		for key,value in complete_edges_dict_.items():
			complete_edges_dict_prob_[key] = round(value / on_surface_log_.shape[0] , 3)


		final_edges_prob_ = []
		for key, value in complete_edges_dict_prob_.items():
			if value > 0.0:
				final_edges_prob_.append((key[0], key[1], value))

		# initialize graph
		G = nx.Graph()
		G.add_nodes_from(nodes_)
		G.add_weighted_edges_from(final_edges_prob_)
		
		if graph_layout == 'spring':
			pos = nx.spring_layout(G, seed=7)
		elif graph_layout == 'circular':
			pos = nx.circular_layout(G)
		else:
			raise Exception("No valid graph layout specified")

		# set nodes and labels
		nx.draw_networkx_nodes(G, pos, node_color="steelblue", node_size=700)
		nx.draw_networkx_labels(G, pos, font_size=20, font_color="whitesmoke", font_family="sans-serif")
		
		# set edges and labels
		nx.draw_networkx_edges(
		    G, pos, edgelist=final_edges_prob_, width=2, alpha=0.5, edge_color="k", style="dashed"
		)
		edge_labels = nx.get_edge_attributes(G, "weight")
		nx.draw_networkx_edge_labels(G, pos, edge_labels)

		ax = plt.gca()
		ax.margins(0.08)
		ax.set_title("Percentage of sim steps in communication")
		plt.axis("off")
		plt.tight_layout()
		plt.savefig("./figures/random_graph.png", format='png', bbox_inches='tight', dpi=60) 				# TODO: need to increase figure size

		if display_ave_comms_graph:
			plt.show()


		# NOTE: the edges calculations above only show the number of sim steps in communications; doesn't show # of unique conenctions
		# TODO: can we count occurances of subgraphs?
		# TODO: can we find periodicity in the occurances of subgraphs? 					ONCE ESTABLISHED WE CAN USE REN'S RESULTS
		# TODO: can we find when the union of the time-varying graphs becomes connected?


	#####
	# HELPER FUNCTIONS
	#####

	# TODO: THIS FCN IS PROBABLY NOT REQUIRED; DELETE
	def complete_graph_from_list(self, L, create_using=None):
	    G = nx.empty_graph(len(L),create_using)
	    if len(L)>1:
	        if G.is_directed():
	            edges = itertools.permutations(L,2)
	        else:
	            edges = itertools.combinations(L,2)
	        G.add_edges_from(edges)

	    return G

	# TODO: graph is jumping around; find a way to remove edges but not the nodes; need to delete edges but not nodes, start with fully connected graph to place nodes
	# TODO: why is agent0 never in comms? check the data vector
	def anim_update(self, num, multiplier, layout, G, on_surface_log_, nodes_, ax):
		itr = math.floor(num*multiplier)

		ax.clear()
		G.clear()   																			# TODO: need a better solution; don't delete the nodes

		G.add_nodes_from(nodes_)
	
		# accumulate all "on_surface" comms between graphical displays
		max_on_surface_ = np.zeros(len(nodes_))
		for i in range(itr-multiplier, itr):
			max_on_surface_ = [max(l1, l2) for l1, l2 in zip(max_on_surface_, on_surface_log_[i,:])]

		edges_ = self.recover_graph_edges(nodes_, max_on_surface_)		# determine new edges
		G.add_edges_from(edges_)
		# G.update(edges=edges_)

		nx.draw(G, pos=layout, ax=ax, with_labels=True) 						# draw the graph
		ax.set_title("Frame {}".format(itr)) 									# update the title


	def recover_graph_edges(self, nodes, itr_edges):
		masked_ = np.multiply(nodes+1, itr_edges)
		masked_ = masked_[masked_ != 0]
		masked_ = masked_ - 1
		edges_ = list(itertools.combinations(masked_,2)) 				# TODO: make sure list() still works for animation gen

		return edges_