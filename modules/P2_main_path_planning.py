import json
import P2_bandit as bd
import P2_agent as agent
import P2_Lowerlevel_network as LN
import P2_Upperlevel_network as UN
import P1_BIM as BIM

class NetworkPlanner:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.best_epsilon = None
        self.schedule = []
        self.coordinates = {}
        self.smoothed_paths = []  # Store all smoothed paths

    def define_epsilon(self):
        env = bd.CustomBanditzones()
        epsilon_values = [0.5, 0.4, 0.3, 0.2, 0.1]

        optimizer = agent.EpsilonGreedyBandit(env, epsilon_values, n_steps=1000)
        optimizer.run_simulation()
        self.best_epsilon = optimizer.get_best_epsilon()
        return self.best_epsilon

    def calc_schedule(self, epsilon):
        env = bd.CustomBanditzones()
        epsilon_values = [epsilon]
        calc_schedule_optimizer = agent.EpsilonGreedyBandit(env, epsilon_values, n_steps=3)
        schedule = calc_schedule_optimizer.run_simulation()

        def remove_exact_duplicates(lst):
            if not lst:
                return []
            result = [lst[0]]
            for i in range(1, len(lst)):
                if lst[i] != lst[i - 1]:
                    result.append(lst[i])
            return result

        self.schedule = remove_exact_duplicates(schedule)
        return self.schedule

    def load_coordinates(self):
        with open(self.json_file_path, 'r') as file:
            self.coordinates = json.load(file)
        return self.coordinates

    def run_upper_level_network(self, schedule):
        analyzer = UN.GraphAnalyzer(BIM.nodes, BIM.connections_list)
        nodes = BIM.nodes
        locator = UN.NodeLocator(nodes)

        source_zone = schedule[0]
        target_zone = schedule[1]
        source_location = tuple(self.coordinates.values())[source_zone]['location']
        target_location = tuple(self.coordinates.values())[target_zone]['location']

        closest_to_source = locator.find_closest_node(source_location)
        closest_to_target = locator.find_closest_node(target_location)

        shortest_path = analyzer.find_shortest_path(closest_to_source[0], closest_to_target[0])
        return shortest_path, source_location, target_location

    def run_lower_level_network(self, shortest_path, source_location, target_location):
        boundary = (0, 3000, 0, 2000)
        obstacle = BIM.plan
        all_paths = []

        rrt_star_planner = LN.RRTStar(source_location, BIM.nodes[shortest_path[0]], [], boundary)
        rrt_star_planner.set_obstacles(obstacle)
        path_to_closest_node = rrt_star_planner.rrt_star_with_smoothing(smooth=False)
        all_paths.extend(path_to_closest_node)

        for i in range(len(shortest_path) - 1):
            start = BIM.nodes[shortest_path[i]]
            goal = BIM.nodes[shortest_path[i + 1]]
            rrt_star_planner = LN.RRTStar(start, goal, [], boundary)
            rrt_star_planner.set_obstacles(obstacle)
            path_segment = rrt_star_planner.rrt_star_with_smoothing(smooth=False)
            if len(all_paths) > 0:
                all_paths.extend(path_segment[1:])
            else:
                all_paths.extend(path_segment)

        rrt_star_planner = LN.RRTStar(BIM.nodes[shortest_path[-1]], target_location, [], boundary)
        rrt_star_planner.set_obstacles(obstacle)
        path_to_target_node = rrt_star_planner.rrt_star_with_smoothing(smooth=False)
        all_paths.extend(path_to_target_node)

        rrt_star_planner = LN.RRTStar(all_paths[0], all_paths[-1], [], boundary)
        rrt_star_planner.set_obstacles(obstacle)
        smoothed_path = rrt_star_planner.smooth_path(all_paths)
        
        # Store the smoothed path
        self.smoothed_paths.append(smoothed_path)
        print()
        print("--------------------------------------------")
        print("Path section found, close window to continue")
        print("--------------------------------------------")
        print()

        # Plot the result
        rrt_star_planner.plot_result(smoothed_path)

        length_of_all_paths = rrt_star_planner.calculate_path_length(smoothed_path)
        print("Length of the smoothed path:", length_of_all_paths)
        return self.smoothed_paths

    def run(self):
        self.best_epsilon = self.define_epsilon()
        self.schedule = self.calc_schedule(self.best_epsilon)
        self.load_coordinates()

        for i in range(len(self.schedule) - 1):
            current_schedule = [self.schedule[i], self.schedule[i + 1]]
            shortest_path, source_location, target_location = self.run_upper_level_network(current_schedule)
            if shortest_path:
                self.run_lower_level_network(shortest_path, source_location, target_location)

# Create an instance of NetworkPlanner
planner = NetworkPlanner('assets/BIM.json')
    
# Run the planner
planner.run()
    
# Access the smoothed paths
smoothed_paths = planner.smoothed_paths
   
# Print or process the smoothed paths
print("Smoothed Paths:", smoothed_paths)
print()
print("----------------------------------------------------------")
print("Full path is planned, Press 'Start' to activate S.I.M.O.H.")
print("----------------------------------------------------------")

with open("assets/path.json", "w") as file:
    json.dump(smoothed_paths, file)