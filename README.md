# Marc Mentat Scripting
A how-to guide for scripting marc mentat using python API.

This README will contain an overview of the provided example. Each script is relatively well documented and commented.

### File definitions
| Extension  | File function |
| ------------- | ------------- |
| .proc | This is the Mentat input file. We create this file and then run it to build the model. |
| .dat  | This is the input file to the solver (Marc).  |
| .t16  | Results file - can be processed in mentat or using `py_post`.  |
| .sts  | Status file - file is updated whilst being solved. After completion, the exit code is found at the bottom of this file.  |
| .x_t  | Not sure, have never used it. |
| .mud  | Marc Binary Model File - I do not use this file in my scripting pipeline. |

## Example - Create unit with a rectangular void and generate a .dat file.

### Generating the rectangle.
Mentat can create a polygon by placing node points in a winding order. Therefore the `create_rectangle` function takes in the desired parameters and returns the necessary node points which can be passed to mentat through the Python API.

### Creating the model in Mentat using .proc files.
We cannot directly alter the `.dat` files if we need to do meshing. Therefore we will create a `.dat` file and let mentat set up the model for us in the background using `mentat -bg <file_name>.proc`.
