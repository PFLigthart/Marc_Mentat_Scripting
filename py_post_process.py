"""
Program to post process marc .t16 files. 

Author: Philip Ligthart
Date: May 2023
"""

import py_post
import numpy as np
from py_post import post_open
import matplotlib.pyplot as plt
import numpy as np
import os  # for file handling


def find_closest_node(t_16_file, node_targets):
    """Find the node in the model that is closest to the target node.
    
    Args:
        t_16_file: The mentat post file object class.
        node_targets: tuple with all the node targets, takes form:
            ((x1, y1, z1), (x2, y2, z2), ..., (xn, yn, zn)).
        
    Returns:
        actual_node_pos_and_num: np array of the node numbers for the node
    """
    increment = 0
    t_16_file.moveto(increment)

    n_nodes = t_16_file.nodes()
    nodes = np.arange(n_nodes)

    # precompute node positions
    x = np.array([t_16_file.node(int(j)).x for j in nodes])
    y = np.array([t_16_file.node(int(j)).y for j in nodes])
    z = np.array([t_16_file.node(int(j)).z for j in nodes])
    node_coor = np.column_stack((x, y, z))

    actual_node_pos_and_id = []

    for target in node_targets:
        # calculate euclidean distances for all nodes simultaneously
        distances = np.sqrt(np.sum((node_coor - np.array(target)) ** 2, axis=1))

        # find the closest node
        closest_node_id = np.argmin(distances)
        closest_node_pos = (*node_coor[closest_node_id], closest_node_id)

        actual_node_pos_and_id.append(closest_node_pos)

    return np.array(actual_node_pos_and_id)


def find_closest_node_old(t_16_file, node_targets):
    """Find the closest node in the t.16 file to each of the targets in the
    node_targets tuple.

    Args:
        t_16_file: The mentat post file object class.
        node_targets: tuple with all the node targets, takes form:
            ((x1, y1, z1), (x2, y2, z2), ..., (xn, yn, zn)).

    Returns:
        actual_node_pos_and_num: np array of the node numbers for the node
        targets as well as the actual position of that node. Takes the form
        (x, y, z, node_num)
    """

    # Extract all the nodes and their positions from the class into an np array
    increment = 0  # This is the time before the simulation starts.
    t_16_file.moveto(increment)  # This moves to the increment of interest.

    n_nodes = t_16_file.nodes()  # Get the number of nodes
    nodes = [i for i in range(n_nodes)]

    # Get original node position
    x = np.array([t_16_file.node(int(j)).x for j in nodes])
    y = np.array([t_16_file.node(int(j)).y for j in nodes])
    z = np.array([t_16_file.node(int(j)).z for j in nodes])
    node_coor = np.vstack([x, y, z]).transpose()

    # Loop over all targets and find the closest node to that target in an
    # Euclidean distance sense
    actual_node_pos_and_id = []
    for target in node_targets:
        min_dist = float("inf")
        closest_node = None
        for i, node_pos in enumerate(node_coor):
            dist = np.sqrt(
                (node_pos[0] - target[0]) ** 2 + (node_pos[1] - target[1]) ** 2
            )
            if dist < min_dist:
                min_dist = dist
                closest_node = (node_pos[0], node_pos[1], node_pos[2], i)
        actual_node_pos_and_id.append(closest_node)

    # Return the np array of the node numbers for the node target as well as the
    # actual position of that node. Takes the form (x, y, z, node_id)
    return np.array(actual_node_pos_and_id)


def _write_positions_to_file(displacements: np.array, file_name):
    """
    Write the contents of an array to a text file.

    Args:
        displacements: The displacements to be written to file.
        file_name: The name of the file to be written to. Must include file
            extension.

    Returns:
        None: Just writes the file.
    """

    # Extract the x and y values from each array
    x = displacements[:, 0]
    y = displacements[:, 1]

    combined_array = np.concatenate((x, y), axis=0).transpose()
    # Save the x and y values to a CSV file
    with open(file_name, "a") as file:
        file.write("\n")
        for k in combined_array:
            file.write(f"{k}, ")
        file.write("0")  # append a zero to the end of each line.
    return None


def get_node_position(t_16_file, node_nums="") -> tuple:
    """
    get_node_position(t_16_file,node_nums = '')
        Get the node coordinates and their displacements for all the time steps in all 3 dimensions without
        the need of a .dat file

        Parameters
        ----------
        t_16_file : must be a mentat post file class
        node_nums : if data from specific set of nodes is to be extracted, list object,
        otherwise leave this blank

        Returns
        -------
        node_position   : The final positions of the nodes.
        node_disp       : The displacements of the nodes.

        Written by John van Tonder 06/09/2021
        Edited by Philip Ligthart April 2023
    """
    check_flag = 0
    if type(t_16_file) == str:
        t_16_file = post_open(t_16_file)
        check_flag = 1

    t_16_file.moveto(1)
    n_incs = t_16_file.increments() - 1

    if type(node_nums) == str:
        n_nodes = t_16_file.nodes()
        node_seq = [t_16_file.node_sequence(i) for i in np.arange(1, n_nodes + 1)]
        node_seq = range(n_nodes)
    else:
        n_nodes = len(node_nums)
        node_seq = [i for i in node_nums]
        # filter for nodes that do not exist

    # get orginal node position
    x = np.array([t_16_file.node(int(j)).x for j in node_seq])
    y = np.array([t_16_file.node(int(j)).y for j in node_seq])
    z = np.array([t_16_file.node(int(j)).z for j in node_seq])

    node_coor = np.vstack([x, y, z]).transpose()

    # get node displacemnts
    dx = np.zeros([n_incs, n_nodes])
    dy = np.zeros([n_incs, n_nodes])
    dz = np.zeros([n_incs, n_nodes])

    for i in range(1, n_incs + 1):
        t_16_file.moveto(i)
        for j, e in enumerate(node_seq):
            dx[i - 1, j], dy[i - 1, j], dz[i - 1, j] = t_16_file.node_displacement(e)

    node_disp = np.vstack(
        [[dx.transpose()], [dy.transpose()], [dz.transpose()]]
    ).transpose()

    node_position = node_coor + node_disp

    if check_flag == 1:
        t_16_file.close()

    return node_position, node_disp


def set_up_node_targets(intervals: int=50, UNIT_DIM_BASE: float=25., UNIT_DIM_BASE_X: float=25., UNIT_DIM_BASE_Y:float=25.):
    """
    Create the target node positions.
        The node targets correspond to the positions of the nodes at the start
        of the simulation. They can then be tracked throughout the simulation.

    Args:
        intervals: (int) the number of discrete points per side of the unit
        UNIT_DIM_BASE: (float) How big is a unit.
        UNIT_DIM_BASE_X: (float) How big is a sub unit in the x direction.
        UNIT_DIM_BASE_Y: (float) How big is a sub unit in the y direction.

    Returns:
        node_targets: (list) A list of the node positions.
    """

    nodes = []

    # side 1
    for i in np.linspace(0, 25, intervals):
        nodes.append((i * int(UNIT_DIM_BASE / UNIT_DIM_BASE_X), 0, 0))
    # side 2
    for i in np.linspace(0, 25, intervals):
        nodes.append(
            (
                25 * int(UNIT_DIM_BASE / UNIT_DIM_BASE_X),
                i * int(UNIT_DIM_BASE / UNIT_DIM_BASE_Y),
                0,
            )
        )
    # side 3
    for i in np.linspace(25, 0, intervals):
        temp = (
            i * int(UNIT_DIM_BASE / UNIT_DIM_BASE_X),
            25 * int(UNIT_DIM_BASE / UNIT_DIM_BASE_Y),
            0,
        )
        nodes.append(temp)
    # side 4
    for i in np.linspace(25, 0, intervals):
        nodes.append((0, i * int(UNIT_DIM_BASE / UNIT_DIM_BASE_Y), 0))

    node_targets = tuple(nodes)

    return node_targets


def get_positions(file_name: str, node_targets: tuple):
    """
    Get the final positions of a .t16 file.

    Args:
        file_name: (string) The .t16 file name with extension.
        node_targets: (tuple) The positions of the nodes of interest in rest
            state, i.e., at the start of the simulation.

    Returns:
        final_positions: (array) The final positions of the node targets in form
            [[[x1], [y1], [z1]], [[x2], [y2], [z2]], ...]"""

    # Create the post objectj
    p_obj = py_post.post_open(file_name)
    nodes_pos_and_id = find_closest_node(p_obj, node_targets)
    node_numbers = [int(i[-1]) for i in nodes_pos_and_id]
    positions, disps = get_node_position(p_obj, node_numbers)

    return positions[-1, :, :]


def check_if_file_exists(file_name: str, directory: str):
    """
    Check if a file exists. If not, write the file name to a file
        called "missing_files.txt".

    Args:
        file_name: (string) The file name with extension.
        directory: (string) The directory where the file is located.

    Returns:
        True if file exists, False if not.
    """

    if os.path.isfile(file_name):
        return True
    else:
        print(file_name)
        with open(f"{directory}\missing_files.txt", "a") as f:
            f.write(f"{file_name}\n")
        return False


def _check_if_successful(file_name: str, directory: str):
    """
    Open the .sts file and check if the exit code is 3004. if not write the
        file name to a file called "failed_sims.txt".
    
    Args:
        file_name: The file name, without extension.
        directory: The directory where the file is located.
        
    Returns:
        successfull: (bool) True if successfull.
    """
    # change the file name extension from .t16 to .sts
    base_name, _ = os.path.splitext(file_name)
    file_name = base_name + ".sts"
    with open(file_name, "r") as file:
        # read all content of a file
        content = file.read()
        # check if string present in a file
        word = "Job ends with exit number :    3004"
        successful_run = False
        if word in content:
            successful_run = True
        else:
            with open(f"{directory}\\failed_sims.txt", "a") as f:
                f.write(f"{file_name}\n") 
    return successful_run


def do_the_post_processing(iteration: int, directory_loc: str, file_name: str):
    """
    Do the post processing for the given simulation.

    Args:
        iteration: (int) The iteration number.
        directory_loc: (string) The directory where the .dat files are located.
        file_name: (string) The file name of the .dat file with extension.

    Returns:
        None
    """

    # Setup the node targets to be used for all simulations
    intervals = 50
    unit_size = 25
    size_x = 25
    size_y = 25
    node_targets = set_up_node_targets(intervals, unit_size, size_x, size_y)

    out_put_file = f"{directory_loc}\Example_ouput_file.txt"

    file_name = f"{directory_loc}\\{file_name}" 
    if check_if_file_exists(file_name, directory_loc):
        if _check_if_successful(file_name, directory_loc):
            positions = get_positions(
                file_name=file_name, node_targets=node_targets
            )
            _write_positions_to_file(positions, out_put_file)
        else:
            print(f"Simulation {iteration} failed.")
    else:
        print(f"Simulation {iteration} does not exist.")


if __name__ == "__main__":


    # Note: A Zero is appended to the end of each line. This is to correct for
    # the final comma as a result of my bad file writing. This just means that
    # the last value is a zero and can be ignored when working with the results.

    num_sims = 2 
    for iteration in range(num_sims):
        file_name=f"example_model_{iteration}.t16"
        directory_loc=".\marcmentat_files"
        do_the_post_processing(iteration, directory_loc, file_name)
    
    # plotting the data for some visual feedback
    data = np.loadtxt(".\marcmentat_files\Example_ouput_file.txt", delimiter=",")
    x0 = data[0, 0:int(data.shape[1]/2)]
    y0 = data[0, int(data.shape[1]/2):-1] # ignore the last value
    plt.plot(x0, y0, "o", label="Simulation 0")
    x1 = data[1, 0:int(data.shape[1]/2)]
    y1 = data[1, int(data.shape[1]/2):-1] # ignore the last value
    plt.plot(x1, y1, "o", label="Simulation 1")
    plt.plot([0, 25, 25, 0, 0], [0, 0, 25, 25, 0], "k--", label="Undeformed")
    plt.axis("equal")
    plt.legend()
    plt.show()
