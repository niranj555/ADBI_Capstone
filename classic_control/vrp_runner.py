import gym
from actor_critic_discrete import NewAgent
import pandas
#from utils import plotLearning

import logging
LOG_FILENAME = 'example.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)

logging.info('This message should go to the log file')

def reshape_observation(observation) :
    return observation.T.values.flatten()

if __name__=="__main__":
    agent = NewAgent(alpha=0.00001, input_dims=[36], gamma=0.99,n_actions=3, layer1_size=50, layer2_size=15)
    env=gym.make('vrp-v0')
    score_history=[]
    num_episodes=200

    for i in range(num_episodes):
        done = False
        observation = env.reset()
        score=0
        while not done:
            flat_obs = reshape_observation(observation)
            action = agent.choose_action( flat_obs  )
            next_observation, reward, done, info = env.step(action)
            flat_next_obs = reshape_observation(next_observation)
            agent.learn ( flat_obs, reward, flat_next_obs, done)
            score += reward
        
        score_history.append(score)
        logging.info("EPISODE "+ str(i)+ "score " + str(score))
        print("episode ",i,"score %.2f",score)
        
    filename='vrp-discrete.png'
    #plotLearning(score_history, file, windows=58)