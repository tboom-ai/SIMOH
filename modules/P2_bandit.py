import numpy as np
import gym
from gym import spaces
from gym.utils import seeding
import json


class BanditEnv(gym.Env):
    """
    Bandit environment base to allow agents to interact with the class n-armed bandit
    in different variations

    p_dist:
        A list of probabilities of the likelihood that a particular bandit will pay out
    r_dist:
        A list of either rewards (if number) or means and standard deviations (if list)
        of the payout that bandit has
    """
    def __init__(self, p_dist, r_dist):
        if len(p_dist) != len(r_dist):
            raise ValueError("Probability and Reward distribution must be the same length")

        if min(p_dist) < 0 or max(p_dist) > 1:
            raise ValueError("All probabilities must be between 0 and 1")

        for reward in r_dist:
            if isinstance(reward, list) and reward[1] <= 0:
                raise ValueError("Standard deviation in rewards must all be greater than 0")

        self.p_dist = p_dist
        self.r_dist = r_dist

        self.n_bandits = len(p_dist)
        self.action_space = spaces.Discrete(self.n_bandits)
        self.observation_space = spaces.Discrete(1)

        self._seed()

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):
        assert self.action_space.contains(action)

        reward = 0
        done = True

        if np.random.uniform() < self.p_dist[action]:
            if not isinstance(self.r_dist[action], list):
                reward = self.r_dist[action]
            else:
                reward = np.random.normal(self.r_dist[action][0], self.r_dist[action][1])

        return 0, reward, done, {}

    def reset(self):
        return 0

    def render(self, mode='human', close=False):
        pass

class CustomBanditzones(BanditEnv):
    def __init__(self):
        # Load the zone_id data and store it as an instance variable
        with open("assets/BIM.json", "r") as file:
            self.zone_id = json.load(file)  # Instance variable
                
        self.zone_names = list(self.zone_id.keys())  # Store zone names

        # Extract risk_factor values from each zone in the instance variable
        p_dist = [zone["risk_factor"] for zone in self.zone_id.values()]
        
        # Create r_dist as a list of ones, with length equal to the number of zones
        r_dist = [1] * len(self.zone_id)

        # Initialize the parent class (BanditEnv) with p_dist and r_dist
        BanditEnv.__init__(self, p_dist=p_dist, r_dist=r_dist)

        # Print the distributions for verification
        print("p_dist:", p_dist)
        print("r_dist:", r_dist)