from SimEnv import SimEnv
from Plotting import Plotting
import pickle


data_path = './data/GOOD_10agents_200min_waituntil.pkl'

def pickle_results(sim):
	data = sim

	with open(data_path, 'wb') as f:
		pickle.dump(data, f)
	f.close()

def load_pickle_results():
	with open(data_path, 'rb') as f:
		data = pickle.load(f)
	f.close()

	return data

gen_new_data = True

if __name__ == "__main__":
	# generate new data, or use old
	if gen_new_data:
		sim = SimEnv();
		sim.run_sim()
		pickle_results(sim)
	else:
		data = load_pickle_results()
		sim = data

	plt = Plotting(sim)
	plt.plot_state()
	# plt.plot_time_varying_graph()
	# plt.plot_graph_edges_as_random()