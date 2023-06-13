def create_rectangle_proc_dat(
    x_vals,
    y_vals,
    element_size,
    pressure_val,
    min_fraction,
    area,
    proc_file_name,
    dat_file_name,
):
    """
    Create a proc file using parameters passed to the function.

    Args:
        x_vals: (list) The four cavity corner node x values.
        y_vals: (list) The four cavity corner node y values.
        element_size: (float) The mesh size.
        pressure_val: (float) The pressure to be applied to the cavity (MPa)
        min_fraction: (float) The minimum allowed fraction of load case time.
        proc_file_name: (str) The name of the proc file to be created.
        dat_file_name: (str) The name of the dat file that the .proc file will 
            generate when run using the command `mentat -bg proc_file_name.proc`

    Returns:
        None: It just produces a .proc file.
    """

    commands = [
        "*new_model yes",
        "*set_model_analysis_dimension planar",
        "*set_solid_type sheet_rect",
        "*add_solids 0 0 0 25 25",
        "*set_solid_type sheet_arb_poly",
        "*add_solids {x1} {y1} 0 {x2} {y2} 0 {x3} {y3} 0 {x4} {y4} 0",
        "#",
        "*solids_subtract 1 ",
        "2",
        "#",
        "*add_nodes 0 0 0 25 0 0 25 25 0 0 25 0",
        "*add_nodes {x1} {y1} 0",
        "*add_nodes {x2} {y2} 0",
        "*add_nodes {x3} {y3} 0",
        "*add_nodes {x4} {y4} 0",
        "@set($automesh_surface_desc,sheet)",
        "@set($automesh_surface_family,quad)",
        "@set($automesh_surface_order,linear)",
        "*pt_set_target_element_size_method manual",
        "*pt_set_global_element_size_sheet {element_size}",
        "*pt_mesh_sheet linear quad",
        "solid1 #",
        "*sweep_nodes all_existing #",
        "*new_apply *apply_type fixed_displacement",
        "*apply_dof x *apply_dof_value x 0.0",
        "*apply_dof y *apply_dof_value y 0.0",
        "*add_apply_nodes 1 #",
        "*new_apply *apply_type fixed_displacement",
        "*apply_dof x *apply_dof_value x 0.0",
        "*add_apply_nodes 4 #",
        "*new_mater standard *mater_option general:state:solid",
        "*mater_option general:skip_structural:off",
        "*mater_option structural:type:ogden",
        "*mater_param structural:ogden_nterm 3",
        "*mater_param structural:ogden_modulus_1 0.024361",
        "*mater_param structural:ogden_modulus_2 6.6703e-5",
        "*mater_param structural:ogden_modulus_3 4.5381e-4",
        "*mater_param structural:ogden_exp_1 1.7138",
        "*mater_param structural:ogden_exp_2 7.0697",
        "*mater_param structural:ogden_exp_3 -3.3659",
        "*mater_option structural:volum_behav:series",
        "*mater_param structural:vol_strn_nrg_coef_d_1 3.2587",
        "*add_mater_elements all_existing",
        "*new_geometry *geometry_type mech_planar_pstrain ",
        "*geometry_param norm_to_plane_thick 0.002",
        "*add_geometry_elements all_existing",
        "*new_pre_defined_table linear_ramp_time",
        "*select_method_path",
        "*select_clear_nodes",
        "*select_clear_edges",
        "*select_edges 5 6 #",
        "*select_edges 6 7 #",
        "*select_edges 7 8 #",
        "*select_edges 8 5 #",
        "*new_apply *apply_type edge_load",
        "*apply_option edge_load_mode:area",
        "*apply_dof p *apply_dof_value p",
        "*apply_dof_value p {pressure_val}",
        "*apply_dof_table p linear_ramp_time1",
        "*add_apply_edges all_selected #",
        "*new_cbody mesh *contact_option state:solid",
        "*contact_option skip_structural:off",
        "*add_contact_body_elements all_existing",
        "*new_contact_table",
        "*ctable_set_default_touch",
        "*new_loadcase *loadcase_type struc:static",
        "*loadcase_value time 1",
        "*loadcase_option stepping:multicriteria",
        "*loadcase_value desired 30",
        "*loadcase_value maxrec 100",
        "*loadcase_value minfraction {min_fraction}",
        "*loadcase_option procedure:modifiednr",
        "*loadcase_option converge:resid_and_disp",
        "*loadcase_value force 0.001",
        "*loadcase_value displacement 0.001",
        "*loadcase_ctable ctable1",
        "*new_job structural",
        "*add_job_loadcases lcase1",
        "*job_option nod_quantities:manual",
        "*job_option follow:on",
        "*add_post_nodal_quantity Displacement",
        "*add_post_tensor log_strain",
        "*job_option strain:large",
        "*job_contact_table ctable1",
        "*element_type 118 all_existing",
        "*write_marc '{dat_file_name}.dat' yes",
    ]

    # Open the file in write mode
    with open(f"{proc_file_name}.proc", "a") as file:
        # Write each command to a new line, replacing the placeholders with the actual values
        for command in commands:
            file.write(
                command.format(
                    x1=x_vals[0],
                    x2=x_vals[1],
                    x3=x_vals[2],
                    x4=x_vals[3],
                    y1=y_vals[0],
                    y2=y_vals[1],
                    y3=y_vals[2],
                    y4=y_vals[3],
                    element_size=element_size,
                    pressure_val=pressure_val,
                    min_fraction=min_fraction,
                    area=area,
                    dat_file_name=dat_file_name,
                )
                + "\n"
            )

    return None
