import gym
env = gym.make('vrp-v0')

observation = env.reset()
for t in range(3):
	print(observation)
	action = env.action_space.sample()
	print("ACTION:",action)
	observation, reward, done, info = env.step(action)
	print("Observation:",observation)
	print("Reward:",reward)
	if done:
		print("Episode finished after {} timesteps".format(t+1))
		break
env.close()