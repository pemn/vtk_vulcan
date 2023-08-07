#!python
# convert vtk grid to vulcan vulcan block model
# v1.0 08/2023 paulo.ernesto
# Copyright 2023 Vale
# License: Apache 2.0
"""
usage: $0 input_path*vtk output*bmf
"""

import sys, os.path
import numpy as np
import pandas as pd

# import modules from a pyz (zip) file with same name as scripts
sys.path.append(os.path.splitext(sys.argv[0])[0] + '.pyz')

from _gui import usage_gui, pyd_zip_extract

pyd_zip_extract()

import pyvista as pv

def vtk_to_bmf(grid, output):

# convert a vulcan surface to a vulcan solid
  xyzn = grid.dimensions
  xyz0 = np.zeros(3)

  xyzo = np.take(grid.bounds, np.arange(0,5,2))
  xyz1 = np.subtract(np.take(grid.bounds, np.arange(1,6,2)), xyzo)

  names = grid.cell_arrays if sys.hexversion < 0x3080000 else grid.cell_data
  import vulcan
  bm = vulcan.block_model()
  bm.create_regular(output, *xyz0, *xyz1, *xyzn)
  bm.set_model_origin(*xyzo)
  #print(names)
  #names = list(filter(lambda _: not bm.field_predefined(_), names))
  #print(names)
  arr_name = {}
  for name in names:
    if bm.field_predefined(name): continue
    arr_name[name] = grid.get_array(name)
    if arr_name[name].dtype.num < 17:
      bm.add_variable(name, 'float', '-99', '')
    else:
      bm.add_variable(name, 'name', 'n', '')

  cells = grid.cell_centers().points
  for n in range(grid.n_cells):
    if bm.find_world_xyz(*cells[n]):
      continue
    for k,v in arr_name.items():
      if v.dtype.num < 17:
        if np.isnan(v[n]):
          bm.put(k, -99)
        else:
          bm.put(k, float(v[n]))
      else:
        bm.put_string(k, str(v[n]))


def bm_from_vtk(input_path, output = None):

  mesh = pv.read(input_path)
  print(mesh)
  if mesh.GetDataObjectType() in [2,6]:
    if not output:
      output = os.path.splitext(input_path)[0] + '.bmf'
    print(output)
    vtk_to_bmf(mesh, output)
  else:
    if not output:
      output = os.path.splitext(input_path)[0] + '.00t'
    print(output)
    from pd_vtk import pv_save
    pv_save(mesh, output)



main = bm_from_vtk

if __name__=="__main__":
  usage_gui(__doc__)
