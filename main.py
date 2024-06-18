from SimEnv import SimEnv
from Plotting import Plotting


if __name__ == "__main__":
	sim = SimEnv();

	sim.run_sim()

	plt = Plotting(sim)
	plt.plot_state()