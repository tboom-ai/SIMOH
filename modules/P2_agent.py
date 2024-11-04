import numpy as np
import P2_bandit as bd
import matplotlib.pyplot as plt

class EpsilonGreedyBandit:
    def __init__(self, env, epsilon_values, n_steps):
        self.env = env
        self.epsilon_values = epsilon_values
        self.n_steps = n_steps
        self.step_rewards = {epsilon: np.zeros(n_steps) for epsilon in epsilon_values}
        self.final_total_rewards = {}

    def run_simulation(self):
        for epsilon in self.epsilon_values:
            observation = self.env.reset()
            total_reward = 0
            mean_reward = np.zeros(len(self.env.p_dist))
            action_counts = np.zeros(len(self.env.p_dist))
            action_list = []
            
            print(f"\nRunning simulation with epsilon = {epsilon}")

            for step in range(self.n_steps):
                if np.random.rand() < epsilon:
                    action = np.random.randint(len(mean_reward))  # Explore
                    #print(f"Step {step + 1}: Epsilon {epsilon} - Exploring: Chose ({self.env.zone_names[action]})")       
                    action_list.append(action)       
                else:
                    max_reward_estimate = np.max(mean_reward)
                    best_actions = np.where(mean_reward == max_reward_estimate)[0]
                    action = np.random.choice(best_actions)  # Exploit
                    #print(f"Step {step + 1}: Epsilon {epsilon} - Exploiting: Chose ({self.env.zone_names[action]})")
                    action_list.append(action)                    
                
                # Take a step in the environment
                observation, reward, done, info = self.env.step(action)
                
                # Update counts and mean reward estimate for chosen action
                action_counts[action] += 1
                mean_reward[action] += (reward - mean_reward[action]) / action_counts[action]
                
                # Accumulate total reward
                total_reward += reward
                
                # Store the cumulative reward at this step
                self.step_rewards[epsilon][step] = total_reward

            self.final_total_rewards[epsilon] = total_reward
        return action_list

    def get_best_epsilon(self):
        # Calculate the average rewards for each epsilon
        final_avg_rewards = {epsilon: self.final_total_rewards[epsilon] / self.n_steps for epsilon in self.epsilon_values}
        
        # Find the epsilon with the highest average reward
        best_epsilon = max(final_avg_rewards, key=final_avg_rewards.get)
        return best_epsilon
        

    def plot_results(self):
        plt.figure(figsize=(10, 8))

        # Calculate the final average reward for each epsilon
        final_avg_rewards = {epsilon: self.step_rewards[epsilon][-1] / self.n_steps for epsilon in self.epsilon_values}
        
        # Find the epsilon with the highest final average reward
        best_epsilon = max(final_avg_rewards, key=final_avg_rewards.get)
        print(f"\nBest epsilon value: {best_epsilon}")

        for epsilon in self.epsilon_values:
            # Compute average reward per step at each step
            average_rewards = self.step_rewards[epsilon] / (np.arange(self.n_steps) + 1)
            plt.plot(np.arange(self.n_steps), average_rewards, label=f"Epsilon = {epsilon}")

        # Display the final total rewards per epsilon
        print("\nFinal Total Rewards per Epsilon:")
        for epsilon, reward in self.final_total_rewards.items():
            print(f"Epsilon {epsilon}: Total Reward = {reward}")

        plt.title('Average Reward vs Steps for different Epsilon values')
        plt.xlabel('Steps')
        plt.ylabel('Average Reward')
        plt.legend()
        plt.grid(True)
        plt.show()


# #For local use
# if __name__ == "__main__":
#     # Set up the environment and parameters
#     env = bd.CustomBanditzones()
#     epsilon_values = [0.3, 0.2, 0.1, 0.05]
#     n_steps = 100000

#     # Create an instance of the EpsilonGreedyBandit class
#     bandit = EpsilonGreedyBandit(env, epsilon_values, n_steps)
    
#     # Run the simulation
#     bandit.run_simulation()
    
#     # Plot the results
#     bandit.plot_results()
