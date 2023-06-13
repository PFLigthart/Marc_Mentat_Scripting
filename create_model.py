"""
Author: Philip Ligthart
Date: April 2022

Create the dat files for a Monte-Carlo simulation
"""

import math
import pandas as pd
import configparser
from create_rectangle_proc_dat import create_rectangle_proc_dat


def create_rectangle(center_x: float , center_y: float, aspect_ratio: float, rotation_angle: float, area: float) -> list:
    """
    Create a rectangle with a specified area, rotation_angle and aspect_ratio.

    Args:
        center_x: (float) The x-coordinate of the center of the rectangle.
        center_y: (float) The y-coordinate of the center of the rectangle.
        aspect_ratio: (float) The ratio of length to width
        rotation_angle: (float) The angle (in degrees) by which to rotate the
            rectangle. A positive angle rotates the rectangle clockwise.
        area: (float) The area of the rectangle.

    Returns:
        corners (tuple): The four corners of the void.
            (x1, y1, z1, x2, y2, z2, x3, y3, z3)
    """

    # Calculate the side length of the rectangle
    length = math.sqrt(area * aspect_ratio)
    width = length / aspect_ratio

    # Calculate the half-length of the rectangle
    half_length = length / 2.0
    half_width = width / 2.0

    # Calculate the rotation angle in radians
    alpha_rad = math.radians(rotation_angle)

    center = [center_x, center_y]

    # Calculate the vertices of the rectangle
    vertices = [
        [center[0] + half_length, center[1] + half_width],
        [center[0] - half_length, center[1] + half_width],
        [center[0] - half_length, center[1] - half_width],
        [center[0] + half_length, center[1] - half_width],
    ]

    # Apply the rotation alpha to each vertex
    for i in range(len(vertices)):
        x = vertices[i][0] - center[0]
        y = vertices[i][1] - center[1]
        vertices[i][0] = (
            center[0] + x * math.cos(alpha_rad) - y * math.sin(alpha_rad)
        )
        vertices[i][1] = (
            center[1] + x * math.sin(alpha_rad) + y * math.cos(alpha_rad)
        )

    # Adding the z displacements of zero which are required by mentat.
    vertices = (
        vertices[0][0],
        vertices[0][1],
        0,
        vertices[1][0],
        vertices[1][1],
        0,
        vertices[2][0],
        vertices[2][1],
        0,
        vertices[3][0],
        vertices[3][1],
        0,
    )

    return vertices


def setup_proc_file_main():
    """
    Setup the proc file from the input .csv file.
        The loadcase parameters are read from the config.ini file.
        The rectangle designs are read from the Rectangle_inputs.csv file.
 
    Args:
        None

    Returns:
        None
    """
    # read the parameters from the config file
    config_obj = configparser.ConfigParser()
    config_obj.read("config.ini")
    Params = config_obj["Parameters"]

    pressure = float(Params["pressure"]) 
    element_size = float(Params["element_size"])
    min_fraction = float(Params["min_fraction"]) 
    
    # read the csv file with the rectangle designs into a pandas dataframe
    df = pd.read_csv(f"Rectangle_inputs.csv", header=None)
    col_headings = ["center_x", "center_y", "aspect_ratio", "rotation", "area"]
    df.columns = col_headings

    # loop over every sample in the the df
    for index, row in df.iterrows():
        proc_file_name = f".\marcmentat_files\example_model_{index}"
        dat_file_name = f"example_model_{index}"
        
        # get the values from the dataframe row
        center_x = row["center_x"]
        center_y = row["center_y"]
        angle = row["rotation"]
        aspect_ratio = row["aspect_ratio"]
        area = row["area"]

        # create the rectangle
        nodes = create_rectangle(center_x, center_y, aspect_ratio, angle, area)
        x_vals = [nodes[0], nodes[3], nodes[6], nodes[9]]
        y_vals = [nodes[1], nodes[4], nodes[7], nodes[10]]
        
        # create the proc file
        create_rectangle_proc_dat(
                x_vals,
                y_vals,
                element_size,
                pressure,
                min_fraction,
                area,
                proc_file_name,
                dat_file_name,
            )


if __name__ == "__main__":
    setup_proc_file_main()
    print("create_model - completed")