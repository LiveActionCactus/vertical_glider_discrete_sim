

class Sync():
	def __init__(self):
		pass


	def max_surface_hold(self, comms_list, curr_surface_time):
		new_surface_time_elapsed = curr_surface_time

		for comm in comms_list:
			if comm[1] < new_surface_time_elapsed:
				new_surface_time_elapsed = comm[1]

		return new_surface_time_elapsed