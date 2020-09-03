import bpy
import numpy as np
import random
from math import sqrt, floor, ceil

# Additional script to print lists in console in a better format
def print_list(list):
    string = ""
    for i in list:
        string += str(i) + """, 
"""
    print (string)

# Degree conversion
def deg_to_rad(deg):
    rads = deg * np.pi / 180
    return rads

# Draw a straight line
def angled_sides(xco, btm_width, top_width, z_parts):
    yco = [btm_width + i * (top_width-btm_width)/z_parts for i in range(len(xco))]
    return yco

# Draw a sin curve    
def sin_sides(xco, min_width, max_width, s_radians, f_radians, z_parts):
    yco = [min_width + ((max_width-min_width)/2 + ((max_width-min_width) * np.sin(s_radians + i*f_radians/z_parts))/2) for i in range(len(xco))]
    return yco

# Draw a cos curve
def cos_sides(xco, min_width, max_width, s_radians, f_radians, z_parts):
    yco = [min_width + ((max_width-min_width)/2 + ((max_width-min_width) * np.cos(s_radians + i*f_radians/z_parts))/2) for i in range(len(xco))]
    return yco

# Draw a tan curve (technically a arctan)
def tan_sides(xco, min_width, max_width, lim, z_parts):
    yco = [min_width + (max_width-min_width) * (np.arctan(lim*i/z_parts)/np.arctan(lim)) for i in range(len(xco))]
    return yco

# Random pot sides
def find_lines(zco, pot, dim_library, x_or_y, in_or_ex):
    if in_or_ex == 'ex':
        x_min = dim_library[pot][6]
        x_max = dim_library[pot][7]
        y_min = dim_library[pot][8]
        y_max = dim_library[pot][9]
    elif in_or_ex == 'in':
        x_min = dim_library[pot][6] - dim_library[pot][5]
        x_max = dim_library[pot][7] - dim_library[pot][5]
        y_min = dim_library[pot][8] - dim_library[pot][5]
        y_max = dim_library[pot][9] - dim_library[pot][5]
            
    if dim_library[pot][0][0] == 'Line':
        x_curve = angled_sides(zco, x_min/2, x_max/2, dim_library[pot][1])
    elif dim_library[pot][0][0] == 'Sin':
        x_curve = sin_sides(zco, x_min/2, x_max/2, dim_library[pot][10], dim_library[pot][11], dim_library[pot][1])
    elif dim_library[pot][0][0] == 'Cos':
        x_curve = cos_sides(zco, x_min/2, x_max/2, dim_library[pot][10], dim_library[pot][11], dim_library[pot][1])
    elif dim_library[pot][0][0] == 'Tan':
        x_curve = tan_sides(zco, x_min/2, x_max/2, 5, dim_library[pot][1])
        
    if dim_library[pot][0][1] == 'Line':
        y_curve = angled_sides(zco, y_min/2, y_max/2, dim_library[pot][1])
    elif dim_library[pot][0][1] == 'Sin':
        y_curve = sin_sides(zco, y_min/2, y_max/2, dim_library[pot][10], dim_library[pot][11], dim_library[pot][1])
    elif dim_library[pot][0][1] == 'Cos':
        y_curve = cos_sides(zco, y_min/2, y_max/2, dim_library[pot][10], dim_library[pot][11], dim_library[pot][1])
    elif dim_library[pot][0][1] == 'Tan':
        y_curve = tan_sides(zco, y_min/2, y_max/2, 5, dim_library[pot][1])
    
    if x_or_y == 'x':
        curve = x_curve
    elif x_or_y == 'y':
        curve = y_curve

    return curve

#0    'pot_types'
#1    'parts'
#2    'z_parts'
#3    'height'
#4    'thickness'
#5    'base_thickness'
#6    'x_min'
#7    'x_max'
#8    'y_min'
#9    'y_max'
#10   's_radians'
#11   'f_radians'

# Rotate curve around a central point
def find_circle_co_sin (curve, parts):
    temp_co = []
    for l in curve:
        templist = [np.sin(deg_to_rad(i*360/parts)) for i in range(parts)]
        temp_co.append([l * p for p in templist])
    return temp_co

def find_circle_co_cos (curve, parts):
    temp_co = []
    for l in curve:
        templist = [np.cos(deg_to_rad(i*360/parts)) for i in range(parts)]
        temp_co.append([l * p for p in templist])
    return temp_co

# Point creation
def create_points(xco, yco, zco, parts):
    z_limit = len(zco)
    i = 0
    j = 0
    tempco = []
    while i < z_limit:
        while j < parts:
            tempco.append((round(xco[i][j], 2), round(yco[i][j],2), round(zco[i],0)))
            j += 1
        i += 1
        j = 0
    return tempco

# Define the faces from the nodes
def faces(nodes, parts, z_parts):
    faces = []
    for j in range(z_parts):
        for i in range(parts-1):
            faces.append((j*parts + i, j*parts + parts+i+1, j*parts + parts+i))
            faces.append((j*parts + i, j*parts + i+1, j*parts + parts+i+1))
        faces.append((j*parts+(parts-1), j*parts+parts, (j+1)*parts+(parts-1)))
        faces.append((j*parts+(parts-1), j*parts, j*parts+parts))
    return faces

# Create mesh layer
def mesh(name = 'Base Mesh', verts = [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 0)], faces = [(0, 1, 3, 2)]):
    
    # Create Mesh Datablock
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    
    # Create Object and link to scene
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)

# Find top rims
def find_rim(ex_nodes, in_nodes, parts):
    rim_nodes = ex_nodes[-parts:]
    rim_nodes2 = in_nodes[-parts:]
    
    for i in range(len(rim_nodes)):
        rim_nodes.append(rim_nodes2[i])
    
    rim_faces = faces(rim_nodes, parts, 1)
    
    return [rim_nodes, rim_faces]

# Move nodes
def move_nodes(x_tran, y_tran, nodes):
    moved_nodes = []
    for node in nodes:
        node = list(node)
        node[0] += x_tran
        node[1] += y_tran
        node = tuple(node)
        moved_nodes.append(node)
    return moved_nodes

def create_pot(pot, dim_library):
    # Variables    
    pot_types = dim_library[pot][0]
    parts = dim_library[pot][1]
    z_parts = dim_library[pot][2]
    height = dim_library[pot][3]
    thickness = dim_library[pot][4]
    base_thickness = dim_library[pot][5]
    x_min = dim_library[pot][6]
    x_max = dim_library[pot][7]
    y_min = dim_library[pot][8]
    y_max = dim_library[pot][9]
    s_radians = dim_library[pot][10]
    f_radians = dim_library[pot][11]
    x_tran = dim_library[pot][12]
    y_tran = dim_library[pot][13]

    # Calculations
    # External nodes
    zco = [base_thickness + i*((height-base_thickness)/z_parts) for i in range(z_parts+1)]
    xcurve = find_lines(zco, pot, dim_library, 'x', 'ex')
    ycurve = find_lines(zco, pot, dim_library, 'y', 'ex')
    xco = find_circle_co_sin(xcurve, parts)
    yco = find_circle_co_cos(ycurve, parts)
    ex_nodes = create_points(xco, yco, zco, parts)
    ex_nodes = move_nodes(x_tran, y_tran, ex_nodes)
    btm_base_nodes = create_points(xco, yco, [0], parts)
    btm_base_nodes = move_nodes(x_tran, y_tran, btm_base_nodes)
    side_nodes = btm_base_nodes + ex_nodes[0:parts]
    side_faces = faces(side_nodes, parts, 1)

    # Internal nodes
    zco = [base_thickness + i*((height-base_thickness)/z_parts) for i in range(z_parts+1)]
    xcurve = find_lines(zco, pot, dim_library, 'x', 'in')
    ycurve = find_lines(zco, pot, dim_library, 'y', 'in')
    xco = find_circle_co_sin(xcurve, parts)
    yco = find_circle_co_cos(ycurve, parts)
    in_nodes = create_points(xco, yco, zco, parts)
    in_nodes = move_nodes(x_tran, y_tran, in_nodes)
    top_base_nodes = in_nodes[0:parts]

    # Base Faces
    base_faces = lambda nodes: [tuple([i for i in range(len(nodes))])]
    top_base_faces = base_faces(top_base_nodes)
    btm_base_faces = base_faces(btm_base_nodes)

    # External face of the pot
    ex_faces = faces(ex_nodes, parts, z_parts)
    mesh1 = mesh("Pot%d - External Mesh" % pot, ex_nodes, ex_faces)

    # Internal face of the pot
    in_faces = faces(in_nodes, parts, z_parts)
    mesh2 = mesh("Pot%d - Internal Mesh" % pot, in_nodes, in_faces)

    # Base plate meshing
    mesh3 = mesh("Pot%d - Top Plate" % pot, top_base_nodes, top_base_faces)
    mesh4 = mesh("Pot%d - Bottom Plate" % pot, btm_base_nodes, btm_base_faces)
    mesh5 = mesh("Pot%d - Base Sides" % pot, side_nodes, side_faces)

    # Rim of the pot
    rim = find_rim(ex_nodes, in_nodes, parts)
    mesh6 = mesh("Pot%d - Top Rim" % pot, rim[0], rim[1])

# To create multiple pots
def create_pots(pot_nums, dim_library):
    for pot in pot_nums:
        create_pot(pot, dim_library)

def create_pot_dims(pot_nums):
    # Create library
    dim_library = {'pot':['pot_types'
    'parts',
    'z_parts',
    'height',
    'thickness',
    'base_thickness',
    'x_min',
    'x_max',
    'y_min',
    'y_max',
    's_radians',
    'f_radians',
    'x_tran',
    'y_tran'
    ]}
    
    # Pot positions
    root = sqrt(len(pot_nums))
    upper = ceil(root)
    lower = floor(root)
    l_upper = []
    l_lower = []
    for i in range(upper):
        for j in range(upper):
            l_upper.append(j)
            l_lower.append(i)
    pot_sep = 175
    
    # Create random pots
    for pot in pot_nums:
        options = ['Line', 'Sin', 'Cos', 'Tan']
        pot_types = [options[random.randrange(0, 4)], options[random.randrange(0, 4)]]
        parts = random.randrange(6, 21)
        z_parts = random.randrange(6, 21)
        height = random.randrange(80, 150)
        thickness = 2
        base_thickness = 5
        x_min = random.randrange(60, 100)
        x_max = x_min + random.randrange(20, 60)
        y_min = random.randrange(60, 100)
        y_max = y_min + random.randrange(20, 60)
        s_radians = random.randrange(1, 5) * np.pi / 8
        f_radians = np.pi + random.randrange(1, 5) * np.pi / 8
        x_tran = pot_sep * l_upper[pot]
        y_tran = pot_sep * l_lower[pot]
        dim_library[pot] = [pot_types,
            parts,
            z_parts,
            height,
            thickness,
            base_thickness,
            x_min,
            x_max,
            y_min,
            y_max,
            s_radians,
            f_radians,
            x_tran,
            y_tran
            ]
        
    return dim_library


# Create random ppots
pot_nums = [i for i in range(36)]
dim_library = create_pot_dims(pot_nums)

# Print out pot dimensions
print(pot_nums)
print('-----------------------------------')
print(dim_library['pot'])
for pot in pot_nums:
    print(dim_library[pot])

create_pots(pot_nums, dim_library)