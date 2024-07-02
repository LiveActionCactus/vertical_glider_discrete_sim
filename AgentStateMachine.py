

class AgentStateMachine:

	def __init__(self, state=None):
		self._state = state

		self. _diving = True														# State 1.0
		self._diving_params = {"dive_time_ctr" : 0, "dive_time_threshold" : 60}							# TODO: set via parameter

		# self._ready_to_surface = False 
		self._on_surface = False 													# State 2.0
		self._on_surface_params = {"surface_time_ctr" : 0, "surface_time_threshold" : 120}				# TODO: set via parameter
		self._ready_for_comms = False  												# State 2.1
		self._ready_for_sync_update = False  										# State 2.2


	def update_state_machine(self, k, dt):
		if self._diving and not self._on_surface:

			if self._diving_params["dive_time_ctr"] >= self._diving_params["dive_time_threshold"]:
				self.check_on_surface() 								# diving; assumes threshold enough time to clear surface noise 

				if self._on_surface:  									# _on_surface = True
					self._diving = False								# stop diving

					self._ready_for_comms = True
					self._ready_for_sync_update = True
					self._on_surface_params["surface_time_ctr"] = 0 	# resets surface counter

			else:
				self._on_surface = False 						# keep diving; forces to False until glider clears surface noise
				self._diving_params["dive_time_ctr"] = self._diving_params["dive_time_ctr"] + dt

		elif not self._diving and self._on_surface:
			
			if self._on_surface_params["surface_time_ctr"] >= self._on_surface_params["surface_time_threshold"]:
				self._diving = True
				self._diving_params["dive_time_ctr"] = 0 	# resets diving counter

				self._on_surface = False
				self._ready_for_comms = False
				self._ready_for_sync_update = False

			else:
				self._on_surface_params["surface_time_ctr"] = self._on_surface_params["surface_time_ctr"] + dt			

		else:
			raise Exception(f"Entered invalid state from state machine!")


	def check_on_surface(self):
		if self._state[0] > -2E-10:
			self._on_surface = True
		else:
			self._on_surface = False
