import torch as T
T.set_default_tensor_type('torch.cuda.FloatTensor')
import torch.nn as nn
import torch.nn.functional as F 
import torch.optim as optim
import numpy as np 

class ActorCriticNetwork(nn.Module):
	def __init__(self, alpha, input_dims, fc1_dims, fc2_dims, n_actions):
		super(ActorCriticNetwork, self).__init__()
		self.input_dims = input_dims
		self.fc1_dims = fc1_dims
		self.fc2_dims = fc2_dims

		self.n_actions = n_actions
		# 2 layers common to both networks
		self.fc1 = nn.Linear(*self.input_dims, self.fc1_dims) # use * to be able to unpack dimensions for 2D images as well: expects list or tuple
		self.fc2 = nn.Linear(self.fc1_dims, self.fc2_dims)

		# actor: probability of choosing action given in some state
		self.pi = nn.Linear(self.fc2_dims, n_actions) # policy layer: fc2_dims input and outputs n_actions
		self.v = nn.Linear(self.fc2_dims, 1) # outputs critic values

		self.optimizer = optim.Adam(self.parameters(), lr = alpha) # get parameters from module
		self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')
		self.to(self.device)

	def forward(self, observation):
		state = T.Tensor(observation).to(self.device)
		x = F.relu(self.fc1(state))
		x = F.relu(self.fc2(x))
		pi = self.pi(x)
		v = self.v(x)

		return pi, v

	
class NewAgent(object):
	def __init__(self, alpha, input_dims, gamma = 0.99, layer1_size = 256, layer2_size = 256, n_actions = 2) : 
		# gamme = discount rate
		self.gamma = gamma
		self.actor_critic = ActorCriticNetwork(alpha, input_dims, layer1_size, layer2_size, n_actions = n_actions)
		self.actor_critic.cuda()
		self.log_probs = None # value used ot update weights for NN (get gradient of log of prob dist for actor critic)


	def choose_action(self, observation):
		policy, _ = self.actor_critic.forward(observation)
		# use softamx layer cuz prob
		policy = F.softmax(policy)
		# for discrete actions:
		action_probs = T.distributions.Categorical(policy)

		action = action_probs.sample()
		self.log_probs = action_probs.log_prob(action)

		return action.item() # to get integer of tensor

	def learn(self, state, reward, state_,  done):
		self.actor_critic.optimizer.zero_grad() # zero these top gradients to ignore intermediary steps now

		_, critic_value = self.actor_critic.forward(state)
		_, critic_value_ = self.actor_critic.forward(state_)

		# to keep tensors in line:
		reward = T.tensor(reward, dtype = T.float).to(self.actor_critic.device)

		#temporal distance loss quantity: take diff between reward - gamma and next state
		# how far you are from optimal
		delta = reward + self.gamma * critic_value_*(1- int(done)) - critic_value

		actor_loss = -self.log_probs * delta # evolves agent's prolicy over time to minimize negative quantity
		critic_loss = delta**2

		(actor_loss + critic_loss).backward()
		self.actor_critic.optimizer.step()


