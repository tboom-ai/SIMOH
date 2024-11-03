import ifcopenshell
import ifcopenshell.geom
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
from shapely.geometry.polygon import orient
import json

settings = ifcopenshell.geom.settings()

# Load the IFC file
model = ifcopenshell.open('assets/v1.ifc') #####################

# Calculate the global transformation for a placement
def get_global_transform(placement):
    location = [0, 0, 0]
    while placement:
        if hasattr(placement, 'RelativePlacement'):
            relative_placement = placement.RelativePlacement
            local_location = relative_placement.Location.Coordinates
            location = [
                location[0] + local_location[0],
                location[1] + local_location[1],
                location[2] + local_location[2] if len(local_location) > 2 else location[2]
            ]
        placement = getattr(placement, 'PlacementRelTo', None)
    return location

# Filter ground floor rooms
ground_floor_storeys = [storey for storey in model.by_type("IfcBuildingStorey") if "bg" in storey.Name.lower() or "begane" in storey.Name.lower() or "bg." in storey.Name.lower()]

if not ground_floor_storeys:
    print("No ground floor rooms found")
else:
    ground_floor_storey = ground_floor_storeys[0]  # Assume the first is the ground floor
    print(f"Ground floor found: {ground_floor_storey.Name}")

    ground_floor_spaces = [
        space for space in model.by_type("IfcSpace")
        if space.Decomposes and space.Decomposes[0].RelatingObject == ground_floor_storey
    ]

    # Find doors related to the ground floor using IfcRelContainedInSpatialStructure
    contained_in_storey = [
        rel for rel in model.by_type("IfcRelContainedInSpatialStructure") 
        if rel.RelatingStructure == ground_floor_storey
    ]

    ground_floor_doors = [
        door for rel in contained_in_storey for door in rel.RelatedElements if door.is_a("IfcDoor")
    ]

    # Get the name of a space
    def get_space_name(space):
        return space.LongName or space.Name

    # Get the vertices of a space
    def get_space_vertices(space):
        try:
            if not space.Representation or not space.Representation.Representations:
                print(f"Space {space.Name} has no valid geometry.")
                return []
            
            shape = ifcopenshell.geom.create_shape(settings, space)
            geometry = shape.geometry
            vertices = geometry.verts

            # Extract only x and y values
            points = [(vertices[i], vertices[i+1]) for i in range(0, len(vertices), 3)]

            # Remove duplicate points
            return list(dict.fromkeys(points))
        except Exception as e:
            print(f"Error retrieving vertices for space {space.Name}: {e}")
            return []

    # Get the location of a door
    def get_door_location(door):
        try:
            if not door.ObjectPlacement:
                print(f"Door {door.Name} has no valid placement.")
                return None

            # Get global location from ObjectPlacement
            global_location = get_global_transform(door.ObjectPlacement)

            # Return (x, y) coordinates
            return global_location[0], global_location[1]
        except Exception as e:
            print(f"Error retrieving location for door {door.Name}: {e}")
            return None

    # Start visualization
    fig, ax = plt.subplots()

    # Store data for rooms and doors
    spaces_data = []
    doors_data = []

    # Process ground floor rooms
    for space in ground_floor_spaces:
        room_name = get_space_name(space)
        print(f"Space: {room_name}")

        # Get vertices of the space
        vertices = get_space_vertices(space)

        if vertices:
            try:
                if len(vertices) < 3:
                    print(f"Not enough points for space {room_name}, cannot create polygon.")
                    continue

                # Create initial polygon
                polygon = Polygon(vertices)

                # Remove any holes in the polygon
                if polygon.interiors:
                    polygon = Polygon(polygon.exterior)

                # Simplify polygon if invalid
                if not polygon.is_valid:
                    polygon = polygon.simplify(0.1, preserve_topology=True)
                
                # Use convex hull if still invalid
                if not polygon.is_valid:
                    polygon = Polygon(vertices).convex_hull

                # Ensure polygon is oriented clockwise
                polygon = orient(polygon, sign=1.0)

                # Plot valid polygon
                if polygon.is_valid:
                    x, y = polygon.exterior.xy
                    ax.plot(x, y, color='black', linewidth=2)
                    min_x, min_y, max_x, max_y = polygon.bounds
                    spaces_data.append({
                        "name": room_name,
                        "vertices": vertices,
                        "min_x": min_x,
                        "min_y": min_y,
                        "max_x": max_x,
                        "max_y": max_y,
                        "linked_spaces": []
                    })
                else:
                    # Plot original points if polygon could not be fixed
                    x, y = zip(*vertices)
                    ax.plot(x, y, color='red', linestyle='--', linewidth=1)
                    min_x = min(x)
                    max_x = max(x)
                    min_y = min(y)
                    max_y = max(y)
                    spaces_data.append({
                        "name": room_name,
                        "vertices": vertices,
                        "min_x": min_x,
                        "min_y": min_y,
                        "max_x": max_x,
                        "max_y": max_y,
                        "linked_spaces": []
                    })

                # Add room name at centroid
                centroid_x = sum(x for x, y in vertices) / len(vertices)
                centroid_y = sum(y for x, y in vertices) / len(vertices)
                ax.text(centroid_x, centroid_y, room_name, fontsize=8, ha='center')

            except Exception as e:
                print(f"Error creating polygon for space {room_name}: {e}")

    # Process ground floor doors
    for door in ground_floor_doors:
        print(f"Processing door: {door.Name}")
        door_location = get_door_location(door)
        if door_location:
            door_name = door.Name
            print(f"Door: {door_name} at {door_location}")
            doors_data.append({"name": door_name, "location": door_location})
            ax.plot(door_location[0], door_location[1], marker='o', color='purple', markersize=7)

    # Set plot settings
    ax.set_aspect('equal')
    plt.grid(True)
    plt.title("Visualization of rooms and doors on the ground floor")
    plt.xlabel("X-coordinates")
    plt.ylabel("Y-coordinates")
    
    plt.autoscale()
    plt.show()

    # Export data to JSON
    with open('ground_floor_spaces_and_doors.json', 'w') as json_file:
        json.dump({"spaces": spaces_data, "doors": doors_data}, json_file, indent=4)
