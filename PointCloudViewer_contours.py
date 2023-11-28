
import pyvista as pv
import numpy as np
import math
import csv


ply_file_path = './pointcloud_reduced2.ply'
ply_grid_file_path = './pointcloud_grid.ply'
csv_file_path = './outputtest.csv'
read_or_write_csv = 1

# Covnerts float input into inches/fractions
def float_to_inches(value):
    inches = int(value)  # Get the whole number part
    fraction = int((value % 1) * 4)  # Get the fractional part in 4ths of an inch
    if fraction == 0:
        return f"{inches}"
    elif fraction == 2:
        return f"{inches}-1/2\""
    return f"{inches}-{fraction}/4\""



# Finds the closest point in a list to the given point
def find_closest_point(point, point_list):
    # Use only the first two elements (x, y) of the point
    point_array = np.array(point)[:2]
    
    # Use only the first two elements (x, y) of each point in the list
    point_list_array = np.array(point_list)[:, :2]

    # Calculate Euclidean distances using vectorized operations
    distances = np.linalg.norm(point_list_array - point_array, axis=1)

    # Find the index of the minimum distance
    min_distance_index = np.argmin(distances)

    return point_list[min_distance_index], distances[min_distance_index]



# Returns polydata of grid given grid cloud and the point cloud
def grid_list_heights(grid_cloud, point_cloud):
    # Convert the PyVista array to a regular Python list
    grid_coordinates = grid_cloud.points
    point_coordinates = point_cloud.points
    
    grid_list = grid_coordinates.tolist()
    point_list = point_coordinates.tolist()
    result_list = []
    list_length = len(grid_list)
    i = 0
    for point in grid_list:
        i += 1
        print(str(i) + '/' + str(list_length))
        closest_point, distance = find_closest_point(point, point_list)
        if distance <= 5:
            result_list.append(closest_point)

    write_to_csv(result_list, csv_file_path)
    
    # Convert the list to polydata format for pyvista
    points_array = np.array(result_list)
    polydata = pv.PolyData(points_array)
    
    print('before dela')
    # Create a surface from the point cloud using delaunay_2d
    surface = polydata.delaunay_2d()
    
    print('after dela')
    
    # Create contours between points with the same z-value
    contour_lines = surface.contour()
    
    return contour_lines


# Creates the grid (miX, maX, miY,maY, interval to space out points for grid, z axis to input into points list, point cloud, 0: write csv 1: read csv)
def create_grid_list(min_x, max_x, min_y, max_y, interval, z, cloud, write):
    finished = False
    current_x = min_x
    current_y = min_y
    grid_list = []
    
    # Create grid list
    grid_list.append([current_x, current_y, z])
    while finished == False:
        
        if current_x <= max_x:
            current_x += interval
            grid_list.append([current_x, current_y, z])
        elif current_x >= max_x:
            current_x = min_x
            current_y += interval
            if current_y >= max_y:
                finished = True
                
    # Convert grid_list to polydata format for pyvista
    points_array = np.array(grid_list)
    polydata = pv.PolyData(points_array)
    
    if write == 0:
        print('starting finish cloud')
        finished_cloud = grid_list_heights(polydata, cloud)
        print('ending finished cloud')
    elif write == 1:
        finished_list = open_and_read_csv(csv_file_path)
        
        # Convert the list to polydata format for pyvista
        finished_array = np.array(finished_list)
        finished_polydata = pv.PolyData(finished_array)
        
        return finished_polydata
             
    return finished_cloud



# Write csv file and return list
def write_to_csv(my_list, csv_file_path):
    # Writing to CSV
    with open(csv_file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write the data
        csv_writer.writerows(my_list)

    return print(f'The list has been saved to {csv_file_path}')



# Read csv file and return list
def open_and_read_csv(csv_file_path):
    new_list = []
    with open(csv_file_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            row = tuple(map(float, row))
            new_list.append(row)
            
    print(f'The data has been loaded into the new list:')
    return new_list



###
#
# End of methods/functions
#
###




# Load the PLY file
point_cloud = pv.read(ply_file_path)
grid_cloud = pv.read(ply_grid_file_path)


# Access the XYZ coordinates (points) of the mesh
xyz_coordinates = point_cloud.points
xyz_grid_coordinates = grid_cloud.points


# Get the minimum and maximum X, Y values
min_x = np.min(xyz_grid_coordinates[:, 0])
max_x = np.max(xyz_grid_coordinates[:, 0])
min_y = np.min(xyz_grid_coordinates[:, 1])
max_y = np.max(xyz_grid_coordinates[:, 1])


# Create point cloud for displaying markers at 24 inches over center. 
test_cloud = create_grid_list(min_x, max_x, min_y, max_y, 24, 1, point_cloud, read_or_write_csv)

# Move the mesh up in the z-direction
translation_vector = [0, 0, 15]  # Move up by 2 units in the z-direction
translation_vector2 = [0, 0, 12]  # Move up by 2 units in the z-direction
point_cloud.points += np.array(translation_vector2)
test_cloud.points += np.array(translation_vector)

test_cloud["Elevation"] = test_cloud.points[:, 2]

contour_lines = test_cloud.contour(scalars="Elevation")

mesh = test_cloud.delaunay_2d()
mesh.translate([0,0,15])

contours = mesh.contour(np.linspace(-12, 20, 32))

# Visualization of the original and decimated point clouds
p = pv.Plotter()


# generate z_values for labels and convert z_values to inches
z_values = test_cloud.points[:, 2]
z_values_inches = []
for i in z_values:
    i1 = i + 15
    i2 = float_to_inches(i1)
    z_values_inches.append(i2)
    
sargs = dict(fmt="%.0f in", color='white')

# Add meshes/labels to plotter
p.add_mesh(point_cloud, point_size=6, rgb=True)
p.add_mesh(test_cloud, color='r', point_size=5)
p.add_mesh(contours,scalars='Elevation', line_width=5, scalar_bar_args=sargs)
# p.add_mesh(contours, scalars='Elevation', color="b", line_width=5, scalar_bar_args=sargs)
# p.add_scalar_bar(title="Scalar Bar", n_labels=5, **sargs)


# p.add_mesh(test_cloud.extract_cells(np.arange(test_cloud.n_cells)), color='b', line_width=2)  # Add white contour lines
# p.add_point_labels(
#     test_cloud, 
#     z_values_inches,    
#     italic=True,
#     font_size=5,
#     point_color='red',
#     point_size=1,
#     render_points_as_spheres=False,
#     always_visible=True,
#     shadow=True,
# )


# view plotter
p.show()











# sargs = dict(fmt="%.0f in", color='black', title_font_size=4)

# # Add meshes/labels to plotter
# p.add_mesh(point_cloud, point_size=4, rgb=True)
# p.add_mesh(test_cloud, color='r', point_size=5)
# p.add_mesh(contours, line_width=5)
# # p.add_mesh(contours, scalars='Elevation', color="b", line_width=5, scalar_bar_args=sargs)
# p.add_scalar_bar(title="Scalar Bar", n_labels=5, **sargs)