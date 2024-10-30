import numpy as np
import json

def simulate_robot_path(step=5):
    """Simulate a robot moving through zones, yielding [x, y, z] coordinates.
    Input: step (int): Step size for interpolation.
    Output: list: The next point on the path [x, y, z]"""
    
    # Open the json where the calculated path is stored and extract the dataset_points
    with open("S.I.M.O.H./assets/path.json", "r") as file:
        dataset_points = json.load(file)

    # Loop over each path in dataset_points
    for path in dataset_points:
        # Loop over each segment within the current path
        for i in range(len(path) - 1):
            # Define start and end points
            start = np.array(path[i])
            end = np.array(path[i + 1])

            # Calculate direction and distance
            direction = end - start
            distance = np.linalg.norm(direction)
            num_steps = int(distance // step)

            # Yield interpolated points
            if num_steps == 0:
                yield list(map(int, start))
            else:
                unit_direction = direction / distance
                for j in range(num_steps):
                    yield list(map(int, start + unit_direction * step * j))
            
            # Yield the end point to ensure complete coverage
            yield list(map(int, end))