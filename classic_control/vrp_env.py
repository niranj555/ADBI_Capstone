import gym
from gym import spaces
import router
import pandas as pd
import numpy as np
import random

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
		self.student_near_stops = self.router.generate_student_near_stops()
		self.stop_near_students=None
		self.stop_near_stops=self.router.generate_stop_near_stops()
		# Define action and observation space
		# They must be gym.spaces objects
		# Example when using discrete actions:
		self.action_space = spaces.Discrete(3)  
		# N to D
		# D to N
		# N to N
		# Example for using image as input:
		print("SELF.STOPS", self.stops)
		self.no_of_stops=len(self.stops)
		
		self.demand= self.get_demand() 
		self.reward = -np.inf
	
		self.local_stops = self.stops
		self.gloabl_stops = self.stops
		self.local_path_list = []
		self.global_path_list = []
	
		# initiliazing the observation dataframe
		self.column_names = ["stop_id", "stop_x", "stop_y","demand","maxwalk","capacity", "visited"]
		self.observation = pd.DataFrame(columns = self.column_names)
		self.observation['stop_id']=list(self.stops.keys())
		self.observation['stop_x']=[self.stops.get(x)[0] for x in self.stops]
		self.observation['stop_y']=[self.stops.get(x)[1] for x in self.stops] 
		self.observation['maxwalk']=[self.maxwalk] *self.no_of_stops  
		self.observation['demand']=self.demand                                        
		self.observation['capacity']=[self.capacity] *self.no_of_stops 
		self.observation['visited'] = [0]* self.no_of_stops
		# 0: not visited, 1: visited; if the capacity < demand at that node, then keep as not visited
	
		# choosing a random node to start with
		self.start_point= random.randint(1,self.no_of_stops)
		#self.start_point = random.choice(for i in range(self.no_of_stops))
	
		#random.randint(0, len(self.df.loc[:, 'Open'].valu#) ########
		#next_stop = random.choice(local_stops)
	
		self.current_point = self.start_point
		# depot. coordinates = (0,0)
		self.done = False
		self.observation_space = spaces.Box(low=-500, high=500, shape=(self.no_of_stops,7), dtype=np.uint8)
		# stock market: self.observation_space = spaces.Box(low=0, high=1, shape=(6, 6), dtype=np.float16)
	
		self.action_space = spaces.Discrete(3)
		# stock market: spaces.Box(low=np.array([0, 0]), high=np.array([3, 1]), dtype=np.float16)

	def get_demand(self):
		self.global_path_list,self.global_students_dict=self.router.route_local_search()
		self.demand = [0] * self.no_of_stops  
		for i in self.global_students_dict:
			self.demand[self.global_students_dict[i]]+=1
		return self.demand

	def step(self, action):
		self._take_action(action)
		total_dist = 0
	
		# negative of the local path distance
		if self.global_path_list[0]:
			for g in range(len(self.global_path_list)):
				node_dict = self.global_path_list[g]
		for n in range(len(node_dict)-1):
			total_dist += float(self.get_distance(node_dict[n], node_dict[n+1]))
		self.reward = float(-1*total_dist)
		self.done = self.check_done()
	
		return self.observation, self.reward, self.done, {}
	
	def check_done(self):
		if list(self.observation['demand']) == [0]*self.no_of_stops:
			return True
	
	def _take_action(self, action):
		# policy = greedy local search 
	
		# Action 1: (node to depot):
		if action == 1 :
			self.global_path_list.extend(self.local_path_list)
			self.local_path_list = []
			self.observation['capacity']=[self.capacity] *self.no_of_stops 
			self.current_point = 0     
	
		# Action 2: (depot to node)
		if action == 2:
			curr = 0
			minm = np.inf
			for i in range(len(self.stop_near_stops[curr])):
				next_stop = self.stop_near_stops[curr][i][0]
				next_stop_distance = self.stop_near_stops[curr][i][1]
				if next_stop_distance < minm and self.observation['visited'][next_stop] == 0:
					# checking if the node is visited
					closest_next_stop = next_stop
					minm = next_stop_distance
			self.update_obvs(closest_next_stop)

			self.local_path_list.extend(closest_next_stop)
			self.current_point = closest_next_stop
			self.local_path_list.extend(closest_next_stop)
	  
		# Action 0 (node to node): checking all neighboring nodes, calculating euclidean distance and choosing nearest node
		if action == 0:
			#curr = self.stops[self.current_point] # coordinates of current point
			curr = self.current_point
			minm = np.inf
			print("Stops near stops", self.stop_near_stops)
			for i in range(len(self.stop_near_stops[curr])):
				next_stop = self.stop_near_stops[curr][i][0]
				next_stop_distance = self.stop_near_stops[curr][i][1]
				if next_stop_distance < minm and self.observation['visited'][next_stop] == 0:
					# checking if the node is visited
					closest_next_stop = next_stop
					minm = next_stop_distance
			self.update_obvs(closest_next_stop)

			self.local_path_list.extend(closest_next_stop)
			self.current_point = closest_next_stop

	def update_obvs(self, next_node):
		if self.capacity < self.observation['demand'][next_node]:
			self.observation['demand'][next_node] -= self.observation['demand'][next_node] - self.capacity
			self.observation['capacity']=[0] *self.no_of_stops 
			self.observation['visited'][next_node] = 0 # no change in the visited since have to go back here again
		else:
			self.observation['demand'][next_node] = 0
			self.observation['visited'][next_node] = 1
			self.observation['capacity']=[self.capacity - self.observation['demand'][next_node]] *self.no_of_stops 
	  
  
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
		self.student_near_stops = self.router.get_student_near_stops()

		self.demand= self.get_demand() 
		self.observation = pd.DataFrame(columns = self.column_names)
		self.observation['stop_id']=list(self.stops.keys())
		self.observation['stop_x']=[self.stops.get(x)[0] for x in self.stops]
		self.observation['stop_y']=[self.stops.get(x)[1] for x in self.stops] 
		self.observation['demand']=self.demand                               
		self.observation['maxwalk']=[self.maxwalk] *self.no_of_stops           
		self.observation['capacity']=[self.capacity] *self.no_of_stops 
		self.observation['visited'] = [0]* self.no_of_stops

		

if __name__ == '__main__':
	blah=VrpEnv()
	print(blah.observation)