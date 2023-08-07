#!python
# convert vulcan data (block model, triangulations) to VTK format
# block models and triangulations
# v1.1 12/2021 paulo.ernesto
# v1.0 09/2020 paulo.ernesto
# Copyright 2020 Vale
# License: Apache 2.0
"""
usage: $0 input_data*bmf,00t,vtk,vti,csv condition variables#variable:input_data output*obj,vtk,vti,csv display@
"""

import sys, os.path

# import modules from a pyz (zip) file with same name as scripts
sys.path.append(os.path.splitext(sys.argv[0])[0] + '.pyz')

from _gui import pyd_zip_extract, usage_gui, bm_sanitize_condition, commalist, wavefront_save_obj, table_name_selector, pd_load_dataframe, pd_detect_xyz

import numpy as np
import pandas as pd

pyd_zip_extract()
import pyvista as pv
from vulcan_save_tri import vulcan_load_tri
from pd_vtk import vtk_Voxel, vtk_meshes_to_obj, vtk_plot_meshes, pv_save, pv_read, vtk_mesh_info

# convert a vulcan surface to a vulcan solid
def bm_to_vtk(input_data, condition, variables, output, display):
  mesh = None
  color = None
  variables = commalist().parse(variables)

  if variables:
    variables = variables.split()
  else:
    variables = None

  file_path, table_name = table_name_selector(input_data)

  if file_path.lower().endswith('bmf'):
    import vulcan
    bm = vulcan.block_model(file_path)
    grid = vtk_Voxel.from_bmf(bm, table_name)
    mesh = grid.add_arrays_from_bmf(bm, condition, variables)
    mesh.cells_volume('volume')
  elif file_path.lower().endswith('csv'):
    df = pd_load_dataframe(file_path)
    mesh = vtk_Voxel.from_df(df, None, pd_detect_xyz(df), variables)
  else:
    mesh = pv_read(file_path)

  vtk_mesh_info(mesh)
  if output.lower().endswith('obj'):
    od = vtk_meshes_to_obj([mesh])
    wavefront_save_obj(output, od)
  elif output:
    pv_save([mesh], output)
  else:
    mesh.save(input_data + '.vtk')


  if int(display):
    vtk_plot_meshes([mesh])

  print("finished")

main = bm_to_vtk

if __name__=="__main__":
  usage_gui(__doc__)
