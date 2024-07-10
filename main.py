from SimEnv import SimEnv
from Plotting import Plotting
import pickle


data_path = './data/GOOD_10agents_200min_waituntil.pkl'

def pickle_results(sim):
	sim_ = sim
	state_log_ = sim._state_log
	on_surface_log_ = sim.comms._on_surface_log
	data = [sim_, state_log_, on_surface_log_]

	with open(data_path, 'wb') as f:
		pickle.dump(data, f)
	f.close

def load_pickle_results():
	with open(data_path, 'rb') as f:
		data = pickle.load(f)
	f.close()

	return data

if __name__ == "__main__":
	# sim = SimEnv();

	# sim.run_sim()
	# pickle_results(sim)

	data = load_pickle_results()
	sim = data[0]

	plt = Plotting(sim)
	plt.plot_time_varying_graph()
	# plt.plot_state()