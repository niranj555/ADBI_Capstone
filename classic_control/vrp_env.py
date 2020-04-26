import gym
from gym import spaces
import router
import pandas as pd
import numpy as np
import random
import collections
import logging
LOG_FILENAME = 'distance.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)
pd.set_option('mode.chained_assignment', None)

class VrpEnv(gym.Env):
	"""Custom Environment that follows gym interface to solve VRP Graph Combinatorics Problem"""

	def __init__(self):
		super(VrpEnv, self).__init__()
		self.minvalue = float('+Inf')
		self.min_path_list = None
		self.min_students_dict = None
		self.instance_file = 'instances/my2.txt'
		self.router = router.Router(self.instance_file)
		self.stops = self.router.get_stops()
		self.students = self.router.get_students()
		self.maxwalk = self.router.get_maxwalk()
		self.capacity = self.router.get_capacity()
		self.router.generate_student_near_stops()
		self.student_near_stops = self.router.student_near_stops
		self.router.generate_stop_near_students()
		self.stop_near_students=self.router.stop_near_students
		#print(self.router.stop_near_students)
		self.router.generate_stop_near_stops()
		self.stop_near_stops=self.router.stop_near_stops
		# Define action and observation space
		# They must be gym.spaces objects
		# Example when using discrete actions:
		self.action_space = spaces.Discrete(3)  
		# N to D
		# D to N
		# N to N
		# Example for using image as input:
		#print("SELF.STOPS", self.stops)
		self.no_of_stops=len(self.stops)
		
		self.demand= self.router.get_demand() 
		self.reward = -1000
	
		self.local_stops = self.stops
		self.gloabl_stops = self.stops
		
		self.global_path_list = []
        #self.total_local_distance = 0
	
		# choosing a random node to start with
		self.current_point = random.randint(1,self.no_of_stops-1)
		self.local_path_list = [ self.current_point ]
		# initiliazing the observation dataframe
		self.column_names = ["stop_id", "stop_x", "stop_y","maxwalk","demand","capacity", "visited", "current_point"]
		self.obs_columns = ["demand","capacity", "visited", "current_point"]
		self.info_columns = ["stop_id", "stop_x", "stop_y","maxwalk"]
		self.observation = pd.DataFrame(columns = self.column_names)
		self.observation['stop_id']=list(self.stops.keys())
		self.observation['stop_x']=[self.stops.get(x)[0] for x in self.stops]
		self.observation['stop_y']=[self.stops.get(x)[1] for x in self.stops] 
		self.observation['maxwalk']=[self.maxwalk] *self.no_of_stops  
		self.observation['demand'] = self.demand                                        
		self.observation['capacity']=[self.capacity] *self.no_of_stops 
		self.observation['visited'] = [0]* self.no_of_stops
		self.observation['current_point'] = [self.current_point] * self.no_of_stops 
		# 0: not visited, 1: visited; if the capacity < demand at that node, then keep as not visited
			
		# depot. coordinates = (0,0)
		self.done = False

		self.observation_space = spaces.Box(low=-100, high=100, shape=(self.no_of_stops,4), dtype=np.uint8)
		# stock market: self.observation_space = spaces.Box(low=0, high=1, shape=(6, 6), dtype=np.float16)
	    
		self.action_space = spaces.Discrete(3)
		# stock market: spaces.Box(low=np.array([0, 0]), high=np.array([3, 1]), dtype=np.float16)

	def get_total_distance(self):
		total_path_yet = self.global_path_list + self.local_path_list
		total_dist = 0
		# negative of the local path distance
		flatten_stops = self.router.flatten(total_path_yet)
		if flatten_stops is not None:
			for n in range(len(flatten_stops) - 1):
				total_dist += float(self.get_distance(flatten_stops[n], flatten_stops[n+1]))
		# if self.global_path_list is not None:
		# 	for g in range(len(self.global_path_list)):
		# 		node_dict = self.global_path_list[g]
		# 		for n in range(len(node_dict)-1):
		# 			total_dist += float(self.get_distance(node_dict[n], node_dict[n+1]))
		print("Route till now: ", flatten_stops)
		print("Distance covered: ", total_dist)
		return total_dist
                    
	def getState(self) :
		return self.obs_columns

	def print_total_distance_(self):
		if self.done:
			f = open('distance.txt', 'a+')
			f.write(str(self.get_total_distance())+ "\n")
			f.close()
			logging.info("Distance covered after episode ", self.get_total_distance())

	def step(self, action):
		self.weight = self._take_action(action)
		self.reward = -1 * self.weight * self.get_total_distance()
		self.done = self.check_done()
		return self.observation[self.obs_columns], self.reward, self.done, self.observation[self.info_columns]
	
	def check_done(self):
		if(self.weight == 1):
			print("Demand check", self.observation['demand'])
		if list(self.observation['demand']) == [0]*self.no_of_stops:
			return True
		return False
	
	def _take_action(self, action):
		# Action 1: (node to depot):
		if action == 1  : 
			if self.current_point == 0 :
				print("[PENALTY] Trying Action: 1 (node to depot) with current point 0 is penalised", " Current point ", self.current_point)
				weight = 10000
			else :
				print("[TAKING  ACTION 1] : (node to depot) with current point: " ,self.current_point)
				# Observation change based on Current point, current capacity and demand
				
				# if self.observation['capacity'][self.current_point] != 0:
				# 	# Bad action when capacity is non-zero but bus goes to depot
				# 	weight = self.observation['capacity'][self.current_point]*10
				# else :
				# 	# Good action when capacity is zero 	
				weight = 1 + 100 * (self.observation['capacity'][self.current_point]/self.capacity)

				self.update_obvs(self.current_point)
				# Add depot to route and finish the local path list
				self.local_path_list.append(0)
				self.global_path_list.extend(self.local_path_list)
				# Add depot to route and start a new local path list
				self.local_path_list = [0]
				self.observation['capacity']= [self.capacity] *self.no_of_stops 
				self.current_point = 0
				self.observation['current_point'] = [self.current_point] * self.no_of_stops 
				
	
		# Action 2: (depot to node)
		if action == 2 :
			if self.current_point == 0:
				print("[TAKING  ACTION 2]: (depot to node) with current point: " , self.current_point)
				curr = 0
				minm = np.inf
				closest_next_stop = -1
				for i in range(len(self.stop_near_stops[curr])):
					next_stop = self.stop_near_stops[curr][i][0]
					next_stop_distance = self.stop_near_stops[curr][i][1]
					#print("CHECKING possible closest_next_stop from ", self.current_point, " with stop: ", next_stop , " whose distance is ", next_stop_distance, "Status", self.observation['visited'][next_stop] )
					#print("Minimum till now " , minm, "  Closest near stop till now ", closest_next_stop)
					if next_stop_distance < minm and self.observation['visited'][next_stop] == 0:
						# checking if the node is visited
						closest_next_stop = next_stop
						minm = next_stop_distance
						#print(" Assigned new stop ", closest_next_stop)
				print("Closest next stop from ",self.current_point, " is ", closest_next_stop)	
				if ( closest_next_stop > -1 and self.observation['visited'][closest_next_stop] == 0) :
					print(" Going to next stop ", closest_next_stop)
					self.local_path_list.append(closest_next_stop)
					self.current_point = closest_next_stop
					self.observation['current_point'] = [self.current_point] * self.no_of_stops 
				weight = 1
			else:
				print("[PENALTY] : Trying Action: 2 (depot to node) with current point non-zero is penalised", " Current point ", self.current_point)
				weight = 10000
          
	  
		# Action 0 (node to node): checking all neighboring nodes, calculating euclidean distance and choosing nearest node
		if action == 0 :
			if self.current_point == 0 :
				print("[PENALTY] : Trying ACTION: 0 (node to node) with current point 0 is penalised", " Current point ", self.current_point)	
				weight = 100
			elif (list(self.observation["capacity"]) == [0]*self.no_of_stops ):	
				print("[PENALTY] : Trying ACTION: 0 (node to node) with no capacity is penalised", " Current point ", self.current_point)
				weight = 10000
			else : 
				print("[TAKING  ACTION 0] : (node to node) with current point: " , self.current_point )
				#curr = self.stops[self.current_point] # coordinates of current point
				curr = self.current_point
				# Observation change based on Current point, current capacity and demand
				self.update_obvs(curr)
				minm = np.inf
				#print("Stops near stops", self.stop_near_stops)
				closest_next_stop = -1 
				for i in range(len(self.stop_near_stops[curr])):
					next_stop = self.stop_near_stops[curr][i][0]
					#closest_next_stop = next_stop
					next_stop_distance = self.stop_near_stops[curr][i][1]
					#print("CHECKING possible closest_next_stop from ", self.current_point, " with stop: ", next_stop , " whose distance is ", next_stop_distance, "Status", self.observation['visited'][next_stop] )
					#print("Minimum till now " , minm, "  Closest near stop till now ", closest_next_stop)
					if next_stop_distance < minm and self.observation['visited'][next_stop] == 0 and next_stop!= 0 :
						# checking if the node is visited
						closest_next_stop = next_stop
						minm = next_stop_distance
						#print(" Assigned new stop ", closest_next_stop)
				print("Closest next stop from ",self.current_point, " is ", closest_next_stop)	
				if ( closest_next_stop > -1 and self.observation['visited'][closest_next_stop] == 0) :
					print(" Going to next stop ", closest_next_stop)
					self.local_path_list.append(closest_next_stop)
					self.current_point = closest_next_stop
					self.observation['current_point'] = [self.current_point] * self.no_of_stops 
				weight = 1  # * ( 1 + self.observation['capacity'][self.current_point])
		
		return weight

	def update_obvs(self, node_to_update):
		#print("Updating Observation for current point " + str(node_to_update) + " with demand " + str(self.observation['demand'][node_to_update]))
		if self.observation['capacity'][node_to_update] < self.observation['demand'][node_to_update]:
			self.observation['demand'][node_to_update] = (self.observation['demand'][node_to_update] - self.observation['capacity'][node_to_update] )
			self.observation['capacity'] = [0] * self.no_of_stops 
			self.observation['visited'][node_to_update] = 0 # no change in the visited since have to go back here again
		else:
			self.observation['capacity']=[self.observation['capacity'][node_to_update] - self.observation['demand'][node_to_update]] *self.no_of_stops 
			self.observation['demand'][node_to_update] = 0
			self.observation['visited'][node_to_update] = 1
		#print("Updating Observation After for current point " + str(node_to_update) + " with demand " + str(self.observation['demand'][node_to_update]))

  
	def get_distance(self, a, b):
		coor_a = self.stops[a]
		coor_b = self.stops[b]

		return np.linalg.norm(coor_b-coor_a)
	
	def reset(self):
		# when all stops are covered: can start with the next random point
		self.minvalue = float('+Inf')
		self.min_path_list = None
		self.min_students_dict = None
		self.instance_file = 'instances/my2.txt'
		self.router = router.Router(self.instance_file)
		self.stops = self.router.get_stops()
		self.students = self.router.get_students()
		self.maxwalk = self.router.get_maxwalk()
		self.capacity = self.router.get_capacity()
		self.router.generate_student_near_stops()
		self.student_near_stops = self.router.student_near_stops
		self.router.generate_stop_near_students()
		self.stop_near_students=self.router.stop_near_students
		self.router.generate_stop_near_stops()
		self.stop_near_stops=self.router.stop_near_stops
		# choosing a random node to start with
		self.current_point = random.randint(1,self.no_of_stops-1)
		#Resetting the routes
		self.local_path_list = [ self.current_point ]
		self.global_path_list = []
		self.demand= self.router.get_demand() 
		self.observation = pd.DataFrame(columns = self.column_names)
		self.observation['stop_id']=list(self.stops.keys())
		self.observation['stop_x']=[self.stops.get(x)[0] for x in self.stops]
		self.observation['stop_y']=[self.stops.get(x)[1] for x in self.stops] 
		self.observation['demand']=self.demand                               
		self.observation['maxwalk']=[self.maxwalk] *self.no_of_stops           
		self.observation['capacity']=[self.capacity] *self.no_of_stops 
		self.observation['visited'] = [0]* self.no_of_stops
		self.observation['current_point'] = [self.current_point] * self.no_of_stops 
		return self.observation[self.obs_columns]

		

if __name__ == '__main__':
	blah=VrpEnv()
	print(blah.observation)