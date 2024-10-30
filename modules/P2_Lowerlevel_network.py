import numpy as np
import matplotlib.pyplot as plt
import random
import math
import P1_BIM as BIM
from matplotlib.patches import Polygon

class Node:
    def __init__(self, point):
        self.point = point
        self.parent = None
        self.cost = 0

class RRTStar:
    def __init__(self, start, goal, obstacle, boundary, max_iter=10000, goal_radius=20, step_size=10, search_radius=10):
        self.max_iter = max_iter
        self.goal_radius = goal_radius
        self.step_size = step_size
        self.search_radius = search_radius
        
        # Define the graph's boundary and obstacles
        self.boundary = boundary  # boundary = (x_min, x_max, y_min, y_max)
        self.obstacle = obstacle  # List of obstacle coordinates or areas
        
        # Initialize start and goal nodes
        self.start_node = Node(start)
        self.goal_node = Node(goal)
        self.tree = [self.start_node]

    @staticmethod
    def distance(p1, p2):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def random_point(self):
        x_min, x_max, y_min, y_max = self.boundary
        ptrand = (random.randint(x_min, x_max), random.randint(y_min, y_max))
        return ptrand

    def nearest(self, point):
        return min(self.tree, key=lambda node: self.distance(node.point, point))

    def set_obstacles(self, polygon_points):
        self.obstacle = []
        for points in polygon_points:
            polygon = Polygon(points, closed=True, fill=None, edgecolor='black')
            self.obstacle.append(polygon)

    def is_collision_free(self, p1, p2):
        num_points = int(self.distance(p1, p2) / 2)  # Increase for less detail
        for i in range(num_points):
            u = i / num_points
            x = int(p1[0] * (1 - u) + p2[0] * u)
            y = int(p1[1] * (1 - u) + p2[1] * u)
            if any(polygon.contains_point((x, y)) for polygon in self.obstacle):  # Check if (x, y) is in obstacles
                return False
        return True

    def nearby_nodes(self, point, radius):
        return [node for node in self.tree if self.distance(node.point, point) < radius]

    def rewire(self, new_node, nearby_nodes):
        for node in nearby_nodes:
            if node is not new_node.parent:
                new_cost = new_node.cost + self.distance(new_node.point, node.point)
                if new_cost < node.cost and self.is_collision_free(new_node.point, node.point):
                    node.parent = new_node
                    node.cost = new_cost

    def rrt_star(self):
        for i in range(self.max_iter):
            # Generate a random point
            rand_point = self.random_point()
            if random.random() < 0.15:  # Goal bias
                rand_point = self.goal_node.point

            # Find the nearest node to the random point
            nearest_node = self.nearest(rand_point)

            # Calculate direction to the random point
            direction = [rand_point[0] - nearest_node.point[0], rand_point[1] - nearest_node.point[1]]
            norm = (direction[0]**2 + direction[1]**2) ** 0.5
            
            if norm < 1e-6:
                continue

            # Normalize direction
            direction = [direction[0] / norm, direction[1] / norm]
            new_point = [int(round(nearest_node.point[0] + direction[0] * self.step_size)),
                        int(round(nearest_node.point[1] + direction[1] * self.step_size))]

            # Check bounds and collisions
            if (self.boundary[0] <= new_point[0] <= self.boundary[1] and
                self.boundary[2] <= new_point[1] <= self.boundary[3] and
                self.is_collision_free(nearest_node.point, new_point)):
                
                # Create a new node at new_point
                new_node = Node(new_point)
                new_node.parent = nearest_node
                new_node.cost = nearest_node.cost + self.distance(nearest_node.point, new_point)
                self.tree.append(new_node)

                # Rewire the tree
                near_nodes = self.nearby_nodes(new_point, self.search_radius)
                self.rewire(new_node, near_nodes)

                # Check if the goal is reached
                if self.distance(new_point, self.goal_node.point) < self.goal_radius:
                    self.goal_node.parent = new_node
                    self.goal_node.cost = new_node.cost + self.distance(new_point, self.goal_node.point)
                    self.tree.append(self.goal_node)
                    print(f"Goal reached at iteration {i}")
                    break

        return self.tree, self.goal_node

    def extract_path(self):
        path = []
        node = self.goal_node
        while node:
            path.append(node.point)
            node = node.parent
        return path[::-1]  # Reverse the path

    def smooth_path(self, path):
        smoothed_path = [path[0]]
        i = 0
        while i < len(path) - 1:
            for j in range(len(path) - 1, i, -1):
                if self.is_collision_free(path[i], path[j]):
                    smoothed_path.append(path[j])
                    i = j
                    break
        return smoothed_path

    def rrt_star_with_smoothing(self, smooth=True):
        # Run the RRT* algorithm
        self.tree, self.goal_node = self.rrt_star()
        
        # Extract the path from start to goal
        path = self.extract_path()
        
        # Apply smoothing if requested
        if smooth:
            path = self.smooth_path(path)
        
        return path

    def calculate_path_length(self, path):
        length = 0.0
        for i in range(1, len(path)):
            length += np.linalg.norm(np.array(path[i]) - np.array(path[i - 1]))
        return length

    def plot_result(self, smoothed_path):
        plt.figure(figsize=(8, 5))
        
        # Plot the smoothed path
        plt.plot([p[0] for p in smoothed_path], [p[1] for p in smoothed_path], 
                'b-', linewidth=2, label="Smoothed Path")
        
        start_point = smoothed_path[0]
        end_point = smoothed_path[-1]
        
        plt.scatter(start_point[0], start_point[1], color='black', label="Start", s=50)
        plt.scatter(end_point[0], end_point[1], color='red', label="Goal", s=50)
        
        # Plot obstacles
        for polygon in self.obstacle:
            # Extract the x and y coordinates of the polygon vertices
            x, y = polygon.get_xy().T  # get_xy returns the vertices as an array
            plt.fill(x, y, color='black', alpha=0.5)  # Fill the polygon to represent an obstacle
        
        plt.legend()
        plt.title("RRT* Path Planning with Smoothed Path")
        plt.xlim(self.boundary[0], self.boundary[1])
        plt.ylim(self.boundary[2], self.boundary[3])
        plt.axis('equal')
        plt.show()

# # For local usage
# if __name__ == "__main__":
#     # Define start and goal points
#     start = BIM.nodes[2]  # Replace with your start coordinates
#     goal = BIM.nodes[3]  # Replace with your goal coordinates
#     boundary = (0, 3000, 0, 2000)

#     obstacle = BIM.plan

#     rrt_star_planner = RRTStar(start, goal, [], boundary)
#     rrt_star_planner.set_obstacles(obstacle)
#     smoothed_path = rrt_star_planner.rrt_star_with_smoothing(smooth=True)
    
#     # Calculate the length of the smoothed path
#     length_of_smooth_path = rrt_star_planner.calculate_path_length(smoothed_path)
#     print("Length of the smoothed path:", length_of_smooth_path)

#     # Plot the result
#     rrt_star_planner.plot_result(smoothed_path)