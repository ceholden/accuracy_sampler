#!/usr/bin/env python
"""
Adds color table and category names for our map
"""

from osgeo import gdal

out_ct = [(0,0,0,255), # Masked
          (0,91,234,255), # Water
          (254,0,0,255), # Developed/Urban
          (255,1,196,255), # Mech. Disturbed
          (204,204,204,255), # Barren
          (0,0,0,255), # Mining
          (39,115,6,255), # Forest
          (255,255,0,255), # Grass/Shrub
          (255,170,1,255), # Agriculture
          (0,254,197,255), # Wetland
          (195,0,252,255), # Nonmech. Disturbed
          (255,255,255,255) # Ice/Snow
         ]
out_class = ['Masked',
             'Water', 'Developed/Urban', 'Mech. Disturbed',
             'Barren', 'Mining', 'Forest', 'Grass/Shrub',
             'Agriculture', 'Wetland', 'Nonmech. Disturbed',
             'Ice/Snow']

ds = gdal.Open('LC_20050101_subset.gtif', gdal.GA_Update)
b = ds.GetRasterBand(1)

ct = gdal.ColorTable()
for i, _ct in enumerate(out_ct):
    ct.SetColorEntry(i, _ct)
b.SetColorTable(ct)
b.SetCategoryNames(out_class)

ds = None
