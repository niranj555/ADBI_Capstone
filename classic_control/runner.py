import gym
from random import randint
env = gym.make('vrp-v0')

observation = env.reset()
print("INITIAL OBSERVATION")
print( observation )
for t in range(30):
	#print("Observation before action: ",observation)
	action = env.action_space.sample()
	print("RANDOM ACTION:",action)
	next_observation, reward, done, info = env.step(action)
	print("Obs:", next_observation)
	print("Reward:",reward)
	if done:
		print("Episode finished after {} timesteps".format(t+1))
		break
env.close()